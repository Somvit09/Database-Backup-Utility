import os
from pathlib import Path

class Validation:
    def __init__(self, host: str, port: int, user: str, password: str, db_name: str, format: str, collection_name: str = None, output_dir: str = None, backup_file: str = None, backup_dir: str = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.format = format
        self.output_dir = Path(output_dir) if output_dir else None
        self.backup_file = Path(backup_file) if backup_file else None
        self.backup_dir = Path(backup_dir) if backup_dir else None
        self.collection_name = collection_name if collection_name else None
        self.FORMATS = ['sql', 'dump', 'bson']

        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def validate_user_params(self):
        # Host validation
        if not isinstance(self.host, str) or not self.host.strip():
            raise ValueError("Host must be a non-empty string.")

        # Port validation
        if not isinstance(self.port, int) or self.port <= 0:
            raise ValueError("Port must be a positive integer.")

        # User validation
        if not isinstance(self.user, str) or not self.user.strip():
            raise ValueError("User must be a non-empty string.")

        # Password validation
        if not isinstance(self.password, str) or not self.password.strip():
            raise ValueError("Password must be a non-empty string.")

        # DB name validation
        if not isinstance(self.db_name, str) or not self.db_name.strip():
            raise ValueError("Database name must be a non-empty string.")

        # collection name validation
        if self.collection_name and not isinstance(self.collection_name, str):
            raise ValueError("Collection name must be a non-empty string.")

        if not isinstance(self.format, str) or not self.format.strip() or self.format not in self.FORMATS:
            raise ValueError(f"format must be a non empty string and should be either {', '.join(self.FORMATS)}")

        if self.output_dir:
            if not isinstance(self.output_dir, Path):
                raise TypeError("Output directory must be a Path object.")
            if not self.output_dir.exists():
                raise FileNotFoundError(f"Output directory '{self.output_dir}' does not exist.")

        if self.backup_file:
            if not isinstance(self.backup_file, Path):
                raise TypeError("backup_file must be a Path object.")
            if not self.backup_file.exists():
                raise FileNotFoundError(f"backup_file '{self.backup_file}' does not exist.")

        return True
