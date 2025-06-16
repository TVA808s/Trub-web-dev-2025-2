import datetime
class UserRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector
        
    def get_all_meetings(self, page=1, per_page=10):
        offset = (page - 1) * per_page
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT 
                    m.id,
                    m.title,
                    m.description,
                    m.date,
                    m.place,
                    m.volunteers_amount,
                    m.image,
                    m.organizer,
                    CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) AS organizer_name,
                    (SELECT COUNT(*) 
                    FROM registration_table r 
                    WHERE r.meeting = m.id) AS volunteers_count
                FROM meetings m
                LEFT JOIN users u ON m.organizer = u.id
                WHERE m.date >= CURDATE()
                ORDER BY m.date DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            meetings = cursor.fetchall()

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM meetings
                WHERE date >= CURDATE()
            """)
            total = cursor.fetchone().total
        
        return meetings, total

    def get_meeting_by_id(self, meeting_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT meetings.*, 
                       CONCAT_WS(' ', users.last_name, users.first_name, users.middle_name) AS organizer_name,
                       COUNT(registration_table.id) AS volunteers_count
                FROM meetings
                LEFT JOIN users ON meetings.organizer = users.id
                LEFT JOIN registration_table ON meetings.id = registration_table.meeting
                WHERE meetings.date >= CURDATE() AND meetings.id = %s
                GROUP BY meetings.id
            """, (meeting_id,))
            meeting = cursor.fetchone()
        return meeting
    
    def get_accepted_volunteers(self, meeting_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) as full_name,
                    r.contacts,
                    r.date        
                FROM registration_table r
                JOIN users u ON r.volunteer = u.id
                WHERE r.meeting = %s
                AND r.status = 'accepted'
                ORDER BY r.date DESC
            """, (meeting_id,))
            av = cursor.fetchall()
        return av
    
    def get_pending_volunteers(self, meeting_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT 
                    CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) as full_name,
                    r.contacts,
                    r.date,
                    r.id AS registration_id  # Важно: используем id регистрации
                FROM registration_table r
                JOIN users u ON r.volunteer = u.id
                WHERE r.meeting = %s
                AND r.status = 'pending'  # Предполагаем, что статус ожидания - 'pending'
                ORDER BY r.date DESC
            """, (meeting_id,))
            pv = cursor.fetchall()
        return pv
    
    def set_status(self, registration_id, status):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            cursor.execute(
                "UPDATE registration_table SET status = %s WHERE id = %s", 
                (status, registration_id)
            )
            connection.commit()

    def get_by_id(self, user_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
            user = cursor.fetchone()
        return user
    
    def get_by_login_and_password(self, login, password):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE login = %s AND password = SHA2(%s, 256);", (login, password))
            user = cursor.fetchone()
        return user
    
    def all(self):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT users.*, roles.name AS role FROM users LEFT JOIN roles ON users.role_id = roles.id")
            users = cursor.fetchall()
        return users
    
    def create(self, username, password, first_name, middle_name, last_name, role_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            if last_name == None:
                query = (
                "INSERT INTO users (username, password, first_name, middle_name, role_id) VALUES"
                "(%s, SHA2(%s,256), %s, %s, %s)"
                )
            else:
                query = (
                    "INSERT INTO users (username, password, first_name, middle_name, last_name, role_id) VALUES"
                    "(%s, SHA2(%s,256), %s, %s, %s, %s)"
                )
            user_data = (username, password, first_name, middle_name, last_name, role_id)
            cursor.execute(query, user_data)
            connection.commit()
            
    def update(self, user_id, first_name, middle_name, last_name, role_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            query = (
                "UPDATE users SET first_name = %s, "
                "middle_name = %s, last_name = %s, role_id = %s WHERE id = %s"
            )
            user_data = (first_name, middle_name, last_name, role_id, user_id)
            cursor.execute(query, user_data)
            connection.commit()   
            
    def change_password(self, user_id, new_password):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            query = (
                "UPDATE users SET password = SHA2(%s, 256) WHERE id = %s"
            )
            user_data = (new_password, user_id)
            cursor.execute(query, user_data)
            connection.commit()    
            
    def delete(self, meeting_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            cursor.execute("DELETE FROM meetings WHERE id = %s", (meeting_id,))
            connection.commit()

    def validate_password(self, user_id, password_to_validate):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s AND password = SHA2(%s, 256);", (user_id, password_to_validate))
            user = cursor.fetchone()
        return user