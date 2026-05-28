import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    MYSQL_HOST     = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT     = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER     = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB       = os.getenv("MYSQL_DB", "reserva_mesas")

    DEBUG      = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "reserva_mesas_secret")
