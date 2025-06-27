import click, os
from enum import Enum
from db_handlers.init import *


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "OUTPUT")

class DB_TYPE(Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"


@click.group()
def cli():
    """Database Backup CLI Utility"""



## BACKUP DATABASE
@cli.command()
@click.option('--database-url', help='Complete database connection URL.')
@click.option('--db-type', required=True, type=click.Choice(['mysql', 'postgres', 'mongodb', 'sqlite']), help='Type of the database')
@click.option('--host', default='localhost', help='Database host', show_default=True)
@click.option('--port', type=int, help='Database port', default=5432, show_default=True)
@click.option('--user', help='Database username', default="postgres", show_default=True)
@click.option('--password', hide_input=True, confirmation_prompt=False, help='Database password')
@click.option('--db-name', required=True, help='Database name', default="test_database")
@click.option('--output', default=OUTPUT_DIR, help='Output directory for backup files')
@click.option('--collection-name', help="Collection name of mongodb database if you need to take backup only from a specific collection.")
@click.option('--format', type=click.Choice(['sql', 'dump']), default='dump', help='Backup file format. sql for .sql & dump for .dump based files.')
def backup(database_url, db_type, host, port, user, password, db_name, output, format, collection_name):
    """Backup the specified database in a backup file"""
    try:
        if db_type == DB_TYPE.POSTGRES.value:
            backup_postgres_database(
                db_type=db_type, database_url=database_url, host=host, port=port, password=password, db_name=db_name, format=format, output=output, user=user
            )
        elif db_type == DB_TYPE.MONGODB.value:
            backup_mongo_database(
                database_url=database_url, output=output, collection_name=collection_name
            )
        else:
            pass
    except (FileExistsError, FileNotFoundError) as fe:
        raise click.ClickException(str(fe))
    except (KeyError, ValueError) as kv:
        raise click.ClickException(str(kv))
    except TypeError as t:
        raise click.ClickException(str(t))
    except Exception as e:
        raise click.ClickException(str(e))



## RESTORE DATABASE
@cli.command()
@click.option('--database-url', help='Complete database connection URL (e.g., postgresql://user:pass@host:port/dbname)')
@click.option('--db-type', required=True, type=click.Choice(['mysql', 'postgres', 'mongodb', 'sqlite']), help='Type of the database')
@click.option('--host', default='localhost', help='Database host', show_default=True)
@click.option('--port', type=int, help='Database port', default=5432, show_default=True)
@click.option('--user', help='Database username', default="postgres", show_default=True)
@click.option('--password', hide_input=True, confirmation_prompt=False, help='Database password')
@click.option('--db-name', required=True, help='Database name', default="test_database")
@click.option('--file-path', help='File path location where the file is located.')
@click.option('--dir-path', help='Dir path location where the folder is located.')
@click.option('--collection-name', help="Collection name of mongodb database if you need to take backup only from a specific collection.")
@click.option('--format', type=click.Choice(['sql', 'dump']), default='dump', help='Backup file format. sql for .sql & dump for .dump based files.')
def restore(database_url, file_path, dir_path, db_type, host, port, user, password, db_name, format, collection_name):
    """Restore the specified database from a backup file"""
    try:
        if db_type == DB_TYPE.POSTGRES.value:
            restore_postgres_database(
                db_type=db_type, database_url=database_url, host=host, port=port, password=password, db_name=db_name, format=format, user=user, backup_file=file_path
            )
        elif db_type == DB_TYPE.MONGODB.value:
            restore_mongo_database(
                database_url=database_url, backup_dir=dir_path, collection_name=collection_name
            )
        else:
            pass
    except (FileExistsError, FileNotFoundError) as fe:
        raise click.ClickException(str(fe))
    except (KeyError, ValueError) as kv:
        raise click.ClickException(str(kv))
    except TypeError as t:
        raise click.ClickException(str(t))
    except Exception as e:
        raise click.ClickException(str(e))

## SCHEDULE AUTOMATIC BACKUP
@cli.command()
@click.option('--db-type', required=True, type=click.Choice(['mysql', 'postgres', 'mongodb', 'sqlite']), help='Type of the database')
@click.option('--cron', required=True, help='Cron expression for scheduling the backup')
def schedule(db_type, cron):
    """Schedule automatic backups using cron syntax"""
    click.echo(f"Scheduled {db_type} backups with cron: {cron}")
    # Placeholder for actual scheduling logic

if __name__ == '__main__':
    cli()
