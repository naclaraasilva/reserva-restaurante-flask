import pymysql
import pymysql.cursors
from config import Config


def get_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def execute_sql(sql: str, params: tuple = (), fetchone: bool = False,
                fetchall: bool = False, commit: bool = False):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            if commit:
                conn.commit()
                return cursor.lastrowid
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
