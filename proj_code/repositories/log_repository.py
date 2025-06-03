class LogRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector
    
    def create_log(self, path, user_id=None):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            query = "INSERT INTO visit_logs (path, user_id) VALUES (%s, %s)"
            cursor.execute(query, (path, user_id))
            connection.commit()

    def get_all_logs(self, page=1, per_page=10):
        offset = (page - 1) * per_page
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            # Основной запрос с пагинацией
            query = """
            SELECT 
                vl.id, 
                vl.path, 
                vl.created_at,
                CONCAT(u.last_name, ' ', u.first_name, ' ', u.middle_name) AS user_full_name
            FROM visit_logs vl
            LEFT JOIN users u ON vl.user_id = u.id
            ORDER BY vl.created_at DESC
            LIMIT %s OFFSET %s
            """
            cursor.execute(query, (per_page, offset))
            logs = cursor.fetchall()
            
            # Получение общего количества записей для пагинации
            cursor.execute("SELECT COUNT(*) AS total FROM visit_logs")
            total = cursor.fetchone().total
            
        return logs, total
    
    def get_user_logs(self, user_id, page=1, per_page=10):
        offset = (page - 1) * per_page
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            query = """
            SELECT 
                vl.id, 
                vl.path, 
                vl.created_at,
                CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) AS user_full_name
            FROM visit_logs vl
            LEFT JOIN users u ON vl.user_id = u.id
            WHERE vl.user_id = %s
            ORDER BY vl.created_at DESC
            LIMIT %s OFFSET %s
            """
            cursor.execute(query, (user_id, per_page, offset))
            logs = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) AS total FROM visit_logs WHERE user_id = %s", (user_id,))
            total = cursor.fetchone().total
            
        return logs, total

    def get_pages_stat(self):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            query = """
            SELECT path, COUNT(*) as count 
            FROM visit_logs 
            GROUP BY path 
            ORDER BY count DESC
            """
            cursor.execute(query)
            page_stats = cursor.fetchall()
        return page_stats

    def get_users_stat(self):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            query = """
            SELECT 
                user_id,
                CASE
                    WHEN user_id IS NULL THEN 'Неаутентифицированный пользователь'
                    ELSE CONCAT_WS(' ', users.last_name, users.first_name, COALESCE(users.middle_name, ''))
                END as full_name,
                COUNT(*) as count
            FROM visit_logs
            LEFT JOIN users ON visit_logs.user_id = users.id
            GROUP BY user_id
            ORDER BY count DESC
            """
            cursor.execute(query)
            user_stats = cursor.fetchall()
        return user_stats