import time
from logger import setup_logger
from urllib.parse import urlparse
from .postgres import *
from validation import Validation

logger = setup_logger("backup")

def backup_postgres_database(db_type: str, database_url: str, host: str, port: int, password: str, db_name: str, format: str, user: str, output: str = None):
    try:
        if database_url:
            parsed = urlparse(database_url)
            db_type = parsed.scheme.split('+')[0]
            user = parsed.username
            password = parsed.password
            host = parsed.hostname
            port = parsed.port or 5432
            db_name = parsed.path.lstrip('/')

        logger.info(f"Testing connection on {db_type} database named '{db_name}' at {host}:{port}.")
        if database_url:
            logger.info(f"Parsed database URL: db_type={db_type}, host={host}, db={db_name}, port={port}, user={user}")
        else:
            logger.info(f"Database information: db_type={db_type}, host={host}, db={db_name}, port={port}, user={user}")
        logger.info(f"Selected format: .{format}")

        if not all([db_type, host, port, user, password, db_name]):
            raise ValueError("Missing required database parameters. Use either --database-url or provide individual options.")

        # validate user params
        validator = Validation(host=host, port=port, user=user, password=password, db_name=db_name, output_dir=output, format=format)
        validator.validate_user_params()

        pg =  PostgresHandler(host=host, port=port, user=user, password=password, db_name=db_name, output_dir=output, format=format)
        if pg.test_connection():
            logger.info(f"Connected to {db_type} database successfully.")
            logger.info(f"Started taking backup......")
            start_time = time.time()
            backup_file_path = pg.backup()
            end_time = time.time()
            logger.info(f"Backup file saved at: {backup_file_path}. Total time taken: {round((end_time-start_time)/60, 6)} minutes.")
        else:
            logger.error(f"Failed to connect to the database {db_name}.")
            raise Exception(f"Failed to connect to the database {db_name}.")

    except Exception as e:
        raise e
    except TypeError as t:
        raise t
    except (ValueError, KeyError) as kv:
        raise kv
    except (FileExistsError, FileNotFoundError) as fe:
        raise fe