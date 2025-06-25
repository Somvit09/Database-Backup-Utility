import click, os
from pathlib import Path
from db_handlers.init import *
from enum import Enum
from validation import Validation


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
@click.option('--db-type', prompt=True, type=click.Choice(['mysql', 'postgres', 'mongodb', 'sqlite']), help='Type of the database')
@click.option('--host', prompt=True, default='localhost', help='Database host', show_default=True)
@click.option('--port', prompt=True, type=int, help='Database port', default=5432, show_default=True)
@click.option('--user', prompt=True, help='Database username', default="postgres", show_default=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=False, help='Database password')
@click.option('--db-name', prompt=True, required=True, help='Database name')
@click.option('--output', prompt=True, default=OUTPUT_DIR, help='Output directory for backup files')
def backup(db_type, host, port, user, password, db_name, output):
    """Backup the specified database in a backup file"""
    click.echo(f"Testing connection on {db_type} database '{db_name}' at {host}:{port}.")
    validator = Validation(host=host, port=port, user=user, password=password, db_name=db_name, output_dir=output)
    validator.validate_user_params()

    if db_type == DB_TYPE.POSTGRES.value:
        pg =  PostgresHandler(host=host, port=port, user=user, password=password, db_name=db_name, output_dir=output)
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
