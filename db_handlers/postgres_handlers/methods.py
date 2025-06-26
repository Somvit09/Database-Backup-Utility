import time
from logger import setup_logger
from urllib.parse import urlparse
from .postgres import *
from validation import Validation
from pathlib import Path

logger = setup_logger("logs")


def fetch_database_params_and_validate(db_type: str, database_url: str, host: str, port: int, password: str, db_name: str, format: str, user: str, output: str = None, backup_file: str = None):
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
    validator = Validation(host=host, port=port, user=user, password=password, db_name=db_name, format=format, backup_file=backup_file, output_dir=output)
    validator.validate_user_params()

    return host, port, user, password, db_name, format, output, backup_file


def backup_postgres_database(db_type: str, database_url: str, host: str, port: int, password: str, db_name: str, format: str, user: str, output: str = None):
    try:
        host, port, user, password, db_name, format, output, _ = fetch_database_params_and_validate(
            db_name=db_name, db_type=db_type, database_url=database_url, host=host, port=port, password=password, format=format, user=user, output=output
        )
        pg =  PostgresHandler(host=host, port=port, user=user, password=password, db_name=db_name, output_dir=output, format=format)
        if pg.test_connection():
            logger.info(f"Connected to {db_type} database successfully.")
            logger.info(f"Started taking backup......")
            start_time = time.time()
            backup_file_path = pg.backup()
            end_time = time.time()
            output_dirname = Path(output).name
            filename = Path(backup_file_path).name
            relative_path_str = f"{output_dirname}\\{filename}"
            logger.info(f"Backup file saved at: {relative_path_str}. Total time taken: {round((end_time-start_time)/60, 6)} minutes.")
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


def restore_postgres_database(db_type: str, database_url: str, host: str, port: int, password: str, db_name: str, format: str, user: str, backup_file: str):
    try:
        host, port, user, password, db_name, format, _, backup_file = fetch_database_params_and_validate(
            db_name=db_name, db_type=db_type, database_url=database_url, host=host, port=port, password=password, format=format, user=user, backup_file=backup_file
        )

        # Instantiate handler
        pg = PostgresHandler(host=host, port=port, user=user, password=password, db_name=db_name, output_dir=None, format=format)

        # Check connection and restore
        if pg.test_connection():
            logger.info("Connected to the database. Starting restore...")
            start_time = time.time()
            pg.restore(backup_file)
            end_time = time.time()
            logger.info(f"Restore completed successfully in {round((end_time - start_time)/60, 6)} minutes.")
        else:
            logger.error("Failed to connect to the database.")
            raise Exception(f"Failed to connect to the database {db_name}.")

    except Exception as e:
        raise e
    except TypeError as t:
        raise t
    except (ValueError, KeyError) as kv:
        raise kv
    except (FileExistsError, FileNotFoundError) as fe:
        raise fe