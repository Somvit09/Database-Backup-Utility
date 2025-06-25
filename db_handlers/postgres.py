import os, subprocess, shutil, platform
import psycopg2
from datetime import datetime
from pathlib import Path

class PostgresHandler:
    def __init__(self, host: str, port: int, user: str, password: str, db_name: str, output_dir: str, format: str):
        self.host = host.strip()
        self.port = port or 5432
        self.user = user
        self.password = password
        self.db_name = db_name
        self.format = format
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _find_pg_dump(self):
        pg_dump_path = shutil.which("pg_dump")
        if pg_dump_path:
            return pg_dump_path

        system = platform.system()

        if system == "Windows":
            possible_paths = [
                Path("C:/Program Files/PostgreSQL"),
                Path("C:/Program Files (x86)/PostgreSQL"),
            ]
            for base in possible_paths:
                if base.exists():
                    for version_dir in base.iterdir():
                        bin_path = version_dir / "bin" / "pg_dump.exe"
                        if bin_path.exists():
                            return str(bin_path)

        elif system == "Linux" or system == "Darwin":
            possible_paths = [
                "/usr/bin/pg_dump",
                "/usr/local/bin/pg_dump",
                "/opt/homebrew/bin/pg_dump",
            ]
            for path in possible_paths:
                if Path(path).exists():
                    return path

        raise FileNotFoundError("pg_dump not found. Make sure PostgreSQL is installed and pg_dump is in your PATH.")

    def test_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.db_name
            )
            if conn:
                conn.close()
                return True
            return False
        except psycopg2.OperationalError as e:
            error_msg = str(e).lower()
            if "does not exist" in error_msg:
                raise Exception(f"Database '{self.db_name}' does not exist.")
            elif "authentication failed" in error_msg:
                raise Exception("Authentication failed. Please check your username or password.")
            elif "could not connect to server" in error_msg or "connection refused" in error_msg:
                raise Exception(f"Could not connect to the server at {self.host}:{self.port}. Is PostgreSQL running?")
            else:
                raise Exception(f"OperationalError: {e}")
        except Exception as e:
            raise Exception(f"Unexpected connection error: {e}")

    def backup(self):
        pg_dump_path = self._find_pg_dump()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_db_name = self.db_name.replace(" ", "_")
        extension = ".sql" if self.format == "sql" else ".dump"
        pg_format = "p" if self.format == "sql" else "c"
        backup_file = self.output_dir / f"{safe_db_name}_backup_{timestamp}{extension}"

        env = os.environ.copy()
        env["PGPASSWORD"] = self.password

        # Sanitize host
        if self.host.strip().lower() == "localhost":
            self.host = "127.0.0.1"

        command = [
            pg_dump_path,
            "-h", self.host,
            "-p", str(self.port),
            "-U", self.user,
            "-F", pg_format,
            "-f", str(backup_file),
            self.db_name
        ]
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Backup failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        return backup_file


    def restore(self, backup_file):
        env = {"PGPASSWORD": self.password}
        command = [
            "pg_restore",
            "-h", self.host,
            "-p", str(self.port),
            "-U", self.user,
            "-d", self.db_name,
            "-c",
            str(backup_file)
        ]

        try:
            subprocess.run(command, env=env, check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Restore failed: {e}")