# History local datbase (SQLite)

import sqlite3


class MessageDB:
    def __init__(self, db_path='./database/chat_history.db'):
        # Connection to DB and adding a table if not exist
        self.db_path = db_path
        self._connect()
        self._create_table()
        

    def _connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    

    def _create_table(self):
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS sessions (
                                session_id TEXT PRIMARY KEY,
                                title TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')

        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS messages (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                session_id TEXT,
                                role TEXT CHECK(role IN ('user', 'assistant', 'system')),
                                content TEXT,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                            )''')
        self.conn.commit()


    def add_session(self, session_id, title):
        self.cursor.execute('''
                            INSERT OR REPLACE INTO sessions (session_id, title) VALUES (?, ?)
                        ''', (session_id, title))
        self.conn.commit()


    def add_message(self, session_id, role, content):
        # Add message to history
        self.cursor.execute(''' 
                            INSERT INTO messages (session_id, role, content)
                            VALUES (?, ?, ?)
                            ''', (session_id, role, content))
        self.conn.commit()
    

    def get_messages(self, session_id):
        # Get all messages via session_id
        self.cursor.execute(''' 
                            SELECT role, content, timestamp FROM messages
                            WHERE session_id = ?
                            ORDER BY timestamp
                            ''', (session_id,))
        return self.cursor.fetchall()
    

    def get_sessions(self):
        # Get list of all uniq sessions
        self.cursor.execute('''
        SELECT session_id, title FROM sessions
        ORDER BY created_at DESC
    ''')
        return self.cursor.fetchall()  # [(session_id, title), ...]
    

    def delete_messages_for_session(self, session_id):
        self.cursor.execute(''' DELETE FROM messages WHERE session_id = ?''', (session_id,))
        self.conn.commit()


    def close(self):
        # Close connection
        self.conn.close()
