import psycopg2
import web.models.settings as settings

def connect():
    """
    Connects to the database and returns a cursor.
    Default values are read from the settings file.
    """
    try:
        conn = psycopg2.connect(database=settings.DB)
    except psycopg2.OperationalError:   # pragma: no cover
        try:
            conn = psycopg2.connect(host=settings.HOST,
                                    port=settings.DEFAULTPORT,
                                    user=settings.USER,
                                    password=settings.PASS,
                                    database=settings.DB)
        except psycopg2.OperationalError:
            conn = psycopg2.connect(host=settings.HOSTIP,
                                    port=settings.PORT,
                                    user=settings.USER,
                                    database=settings.DB)
    return conn.cursor()
