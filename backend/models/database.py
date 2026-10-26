import pymysql
import pymysql.cursors
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception class for database operations that masks passwords"""
    pass

def get_db_connection(include_db_name=True):
    """
    Establishes and returns a PyMySQL connection using parameters from Config.
    Never exposes passwords in error handling.
    """
    try:
        db_config = Config.get_db_config(include_db_name=include_db_name)
        db_config['cursorclass'] = pymysql.cursors.DictCursor
        connection = pymysql.connect(**db_config)
        return connection
    except pymysql.err.OperationalError as e:
        err_code, err_msg = e.args[0], e.args[1] if len(e.args) > 1 else str(e)
        logger.error(f"MySQL OperationalError [{err_code}]: {err_msg}")
        if err_code == 1045:
            raise DatabaseError("Database authentication failed. Please verify DB_USER and DB_PASSWORD in .env.")
        elif err_code == 1049:
            raise DatabaseError(f"Database '{Config.DB_NAME}' does not exist. Run init_db.py to create it.")
        elif err_code == 2003:
            raise DatabaseError("Unable to connect to MySQL database server. Check MySQL service and DB_HOST settings.")
        else:
            raise DatabaseError("Unable to connect to MySQL database. Check MySQL service and database credentials.")
    except Exception as e:
        logger.error(f"Database Connection Error: {str(e)}")
        raise DatabaseError("An unexpected error occurred while connecting to the database.")

def check_db_health():
    """
    Performs a lightweight query to verify MySQL database health.
    Returns (bool, str) tuple.
    """
    try:
        conn = get_db_connection(include_db_name=False)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
        conn.close()
        return True, "Database server connection successful"
    except DatabaseError as e:
        return False, str(e)
    except Exception:
        return False, "Database server health check failed"
