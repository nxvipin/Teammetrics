import psycopg2
import web.settings as settings

def connect(db=settings.DB):
    """
    Connects to the database and returns a cursor.
    Default values are read from the settings file.
    """
    try:
        conn = psycopg2.connect(database=db)
    except psycopg2.OperationalError:   # pragma: no cover
        try:
            conn = psycopg2.connect(host=settings.HOST,
                                    port=settings.DEFAULTPORT,
                                    user=settings.USER,
                                    password=settings.PASS,
                                    database=db)
        except psycopg2.OperationalError:
            conn = psycopg2.connect(host=settings.HOSTIP,
                                    port=settings.PORT,
                                    user=settings.USER,
                                    database=db)
    return conn.cursor()
