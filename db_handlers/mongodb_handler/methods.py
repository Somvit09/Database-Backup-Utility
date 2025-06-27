import time
from logger import setup_logger
from urllib.parse import urlparse
from pathlib import Path
from .mongodb import MongoDBHandler
from validation import Validation

logger = setup_logger("mongodb_tasks")

def fetch_mongo_params_and_validate(database_url: str, collection_name: str, output: str = None, backup_file: str = None, backup_dir: str = None):
    if database_url:
        parsed = urlparse(database_url)
        user = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 27017
        db_name = parsed.path.lstrip('/')

        logger.info(f"Testing MongoDB connection to '{db_name}' at {host}:{port}.")

        validator = Validation(
            host=host,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
            format="bson",
            backup_file=backup_file,
            backup_dir=backup_dir,
            output_dir=output,
            collection_name=collection_name
        )
        validator.validate_user_params()
        return db_name
    return None


def backup_mongo_database(database_url: str, collection_name: str = None, output: str = None):
    db_name = fetch_mongo_params_and_validate(database_url=database_url, output=output, collection_name=collection_name)
    mg = MongoDBHandler(db_name=db_name, output_dir=output, collection_name=collection_name, database_url=database_url)

    if mg.test_connection():
        logger.info(f"Started taking backup......")
        start_time = time.time()
        backup_dir = mg.backup()
        end_time = time.time()
        output_dirname = Path(output).name
        dirname = Path(backup_dir).name
        relative_path_str = f"{output_dirname}\\{dirname}"
        logger.info(f"Backup completed. Saved to {relative_path_str}. Time: {round((end_time-start_time)/60, 3)} minutes.")
    else:
        raise Exception(f"Failed to connect to {db_name}.")


def restore_mongo_database(database_url: str, collection_name: str = None, backup_dir: str = None):
    db_name = fetch_mongo_params_and_validate(database_url=database_url, backup_dir=backup_dir, collection_name=collection_name)
    mg = MongoDBHandler(db_name=db_name, output_dir=None, database_url=database_url)

    if mg.test_connection():
        logger.info("Connected to MongoDB successfully. Starting restore...")
        start_time = time.time()
        mg.restore(backup_dir)
        end_time = time.time()
        logger.info(f"Restore completed successfully in {round((end_time-end_time)/60, 3)} minutes.")
    else:
        raise Exception(f"Failed to connect to MongoDB at {db_name}.")
