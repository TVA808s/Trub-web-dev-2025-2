class UserRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector
     
    def get_by_id(self, user_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT u.*, CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) as full_name FROM users u WHERE u.id = %s;", (user_id,))
            user = cursor.fetchone()
        return user
    
    def get_by_login_and_password(self, login, password):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT u.*, CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) as full_name FROM users u WHERE u.login = %s AND u.password = SHA2(%s, 256);", (login, password))
            user = cursor.fetchone()
        return user
    
    def get_reg_user_or_not(self, meeting_id, user_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM registration_table WHERE meeting = %s AND volunteer = %s", (meeting_id, user_id))
            reg = cursor.fetchone()
        return reg
   
