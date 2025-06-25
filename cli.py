import click, os
from pathlib import Path
from db_handlers.init import *
from enum import Enum
from validation import Validation
from urllib.parse import urlparse


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
    pass

@cli.command()
@click.option('--database-url', help='Complete database connection URL (e.g., postgresql://user:pass@host:port/dbname)')
@click.option('--db-type', required=True, type=click.Choice(['mysql', 'postgres', 'mongodb', 'sqlite']), help='Type of the database')
@click.option('--host', default='localhost', help='Database host', show_default=True)
@click.option('--port', type=int, help='Database port', default=5432, show_default=True)
@click.option('--user', help='Database username', default="postgres", show_default=True)
@click.option('--password', hide_input=True, confirmation_prompt=False, help='Database password')
@click.option('--db-name', required=True, help='Database name', default="test_database")
@click.option('--output', default=OUTPUT_DIR, help='Output directory for backup files')
def backup(database_url, db_type, host, port, user, password, db_name, output):
    """Backup the specified database in a backup file"""
    click.echo(f"Testing connection on {db_type} database '{db_name}' at {host}:{port}.")

    try:
        if db_type == DB_TYPE.POSTGRES.value:
            if database_url:
                parsed = urlparse(database_url)
                db_type = parsed.scheme.split('+')[0]
                user = parsed.username
                password = parsed.password
                host = parsed.hostname
                port = parsed.port or 5432
                db_name = parsed.path.lstrip('/')
                click.echo(f"Parsed database URL: db_type={db_type}, host={host}, db={db_name}")

            if not all([db_type, host, port, user, password, db_name]):
                raise click.UsageError("Missing required database parameters. Use either --database-url or provide individual options.")

            # validate user params
            validator = Validation(host=host, port=port, user=user, password=password, db_name=db_name, output_dir=output)
            validator.validate_user_params()

            pg =  PostgresHandler(host=host, port=port, user=user, password=password, db_name=db_name, output_dir=output)
            try:
                if pg.test_connection():
                    click.echo(f"Connected to {db_type} database successfully.")
                    click.echo(f"Started taking backup......")
                    try:
                        backup_file_path = pg.backup()
                        click.echo(f"Backup file saved at: {backup_file_path}")
                    except Exception as e:
                        click.secho(str(e), fg='red')
                else:
                    click.secho("Failed to connect to the database.", fg='red')
            except Exception as e:
                raise click.ClickException(str(e))

    except (FileExistsError, FileNotFoundError) as fe:
        raise click.ClickException(str(fe))

    except (KeyError, ValueError) as kv:
        raise click.ClickException(str(kv))

    except TypeError as t:
        raise click.ClickException(str(t))

    except Exception as e:
        raise click.ClickException(str(e))




@cli.command()
@click.option('--db-type', prompt=True, type=click.Choice(['mysql', 'postgres', 'mongodb', 'sqlite']), help='Type of the database')
@click.option('--host', prompt=True, default='localhost', help='Database host', show_default=True)
@click.option('--port', prompt=True, type=int, help='Database port', default=5432, show_default=True)
@click.option('--user', prompt=True, help='Database username', default="postgres", show_default=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=False, help='Database password')
@click.option('--db-name', prompt=True, required=True, help='Database name')
@click.option('--file-path', prompt=True, default=OUTPUT_DIR, help='File path location where the file is located.')
def restore(file_path, db_type, host, port, user, password, db_name):
    """Restore the specified database from a backup file"""
    click.echo(f"Testing connection on {db_type} database '{db_name}' at {host}:{port}.")
    if db_type == DB_TYPE.POSTGRES.value:
        pg =  PostgresHandler(host=host, port=port, user=user, password=password, db_name=db_name)
        if pg.test_connection():
            click.echo(f"Connected to {db_type} database successfully.")

@cli.command()
@click.option('--db-type', required=True, type=click.Choice(['mysql', 'postgres', 'mongodb', 'sqlite']), help='Type of the database')
@click.option('--cron', required=True, help='Cron expression for scheduling the backup')
def schedule(db_type, cron):
    """Schedule automatic backups using cron syntax"""
    click.echo(f"Scheduled {db_type} backups with cron: {cron}")
    # Placeholder for actual scheduling logic

if __name__ == '__main__':
    cli()
