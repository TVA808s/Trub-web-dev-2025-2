class MeetingRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector
            
    def create(self, title, description, date, place, volunteers_amount, image, organizer):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            query = (
            "INSERT INTO meetings (title, description, date, place, volunteers_amount, image, organizer) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            )
            meeting = (title, description, date, place, volunteers_amount, image, organizer)
            cursor.execute(query, meeting)
            connection.commit()
            
    def edit(self, meeting_id, title, description, date, place, volunteers_amount):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            query = (
                "UPDATE meetings SET title = %s, "
                "description = %s, date = %s, place = %s, volunteers_amount = %s WHERE id = %s"
            )
            user_data = (title, description, date, place, volunteers_amount, meeting_id)
            cursor.execute(query, user_data)
            connection.commit()   
             
    def delete(self, meeting_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            cursor.execute("DELETE FROM meetings WHERE id = %s", (meeting_id,))
            connection.commit()
    
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
                    WHERE r.meeting = m.id AND r.status = 'accepted') AS volunteers_count
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
                SELECT 
                    meetings.*,
                    CONCAT_WS(' ', users.last_name, users.first_name, users.middle_name) AS organizer_name,
                    (SELECT COUNT(*) 
                    FROM registration_table 
                    WHERE meeting = meetings.id 
                    AND status = 'accepted'
                    ) AS volunteers_count
                FROM meetings
                LEFT JOIN users ON meetings.organizer = users.id
                WHERE meetings.id = %s          
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
                    r.id AS registration_id 
                FROM registration_table r
                JOIN users u ON r.volunteer = u.id
                WHERE r.meeting = %s
                AND r.status = 'pending'  
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

    def reject_all_pending(self, meeting_id):
        connection = self.db_connector.connect()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE registration_table SET status = 'rejected' WHERE meeting = %s AND status = 'pending'",(meeting_id,)
            )
            connection.commit()

    def registrate(self, meeting_id, user_id, contacts):
        connection = self.db_connector.connect()
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO registration_table (meeting, volunteer, contacts) values (%s,%s,%s);", (meeting_id, user_id, contacts))
            connection.commit()

