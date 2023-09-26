import sqlite3

class Database(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def _create(self):
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS visitor
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date INTEGER default (strftime('%s', 'now')),
            name TEXT,
            company TEXT,
            host TEXT,
            email TEXT,
            days INTEGER
        )
        ''')
    
    def __enter__(self):
        self.con = sqlite3.connect(self.file_name)
        self.con.row_factory = sqlite3.Row
        self._create()
        return self

    def __exit__(self, _, __, ___):
        self.con.commit()
        self.con.close()

    def insert(self, name, company, host, email, days):
        self.con.execute('''
            INSERT INTO visitor(name, company, host, email, days)
            VALUES (?, ?, ?, ?, ?)''', (name, company, host, email, days)
        )

    def visitors(self, days=90):
        query = self.con.execute('''
            SELECT date, name, company, host, email, days
            FROM visitor
            WHERE date >= strftime('%s', date('now', ?))
        ''', (f"-{days} day",))
        return query.fetchall()

if __name__ == "__main__":
    with Database("visitors.db") as db:
        db.insert('foo bar', 'bin inc.', 'barbinz qux', 'mail@addr.com', 1)
