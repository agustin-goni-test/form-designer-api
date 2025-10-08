# db.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

'''
Singleton implementation for database connection.
Ensures that only one connection to the database is created and reused.

Uses environment variables for configuration:
- DBNAME: Name of the database
- USER: Database user
- PASSWORD: Database user's password
- HOST: Database host
- PORT: Database port

If some variable is not present, raises an EnvironmentError.
'''

load_dotenv()

class DatabaseConnection:
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def _validate_environment_variables(self):
        """Validate that all required environment variables exist"""
        required_vars = ["DBNAME", "DBUSER", "PASSWORD", "HOST", "PORT"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
    
    def get_connection(self):
        """Get database connection (singleton)"""
        if self._connection is None or self._connection.closed:
            self._validate_environment_variables()
            
            self._connection = psycopg2.connect(
                dbname=os.getenv("DBNAME"),
                user=os.getenv("DBUSER"),
                password=os.getenv("PASSWORD"),
                host=os.getenv("HOST"),
                port=os.getenv("PORT"),
                cursor_factory=RealDictCursor
            )
        
        return self._connection
    
    def close_connection(self):
        """Close the database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

# For backward compatibility, you can keep the original function names
_db_connection = DatabaseConnection()

def get_connection():
    """Get database connection (singleton)"""
    return _db_connection.get_connection()

def close_connection():
    """Close the database connection"""
    _db_connection.close_connection()