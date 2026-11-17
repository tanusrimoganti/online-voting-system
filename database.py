import sqlite3
import os

# Get the project folder location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create database folder if it does not exist
DATABASE_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DATABASE_DIR, exist_ok=True)

# Database file location
DATABASE_NAME = os.path.join(DATABASE_DIR, "voting.db")


def get_db_connection():
    """Connect to the SQLite database."""
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    """Create all required database tables."""

    connection = get_db_connection()
    cursor = connection.cursor()

    # Student table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            registration_number TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        )
    """)

    # Election table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS elections (
            election_id INTEGER PRIMARY KEY AUTOINCREMENT,
            election_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'upcoming'
        )
    """)

    # Candidate table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            election_id INTEGER NOT NULL,
            manifesto TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (election_id) REFERENCES elections(election_id),
            UNIQUE(student_id, election_id),
            UNIQUE(candidate_id, election_id)
        )
    """)

    # Records whether a student has already voted
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voter_participation (
            participation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            election_id INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (election_id) REFERENCES elections(election_id),
            UNIQUE(student_id, election_id)
        )
    """)

    # Stores ballots separately from student identities
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            election_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            FOREIGN KEY (election_id) REFERENCES elections(election_id),
            FOREIGN KEY (candidate_id, election_id)
                REFERENCES candidates(candidate_id, election_id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables() 

