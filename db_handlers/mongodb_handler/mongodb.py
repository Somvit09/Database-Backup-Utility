import os
import subprocess
import shutil
import platform
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from logger import setup_logger

logger = setup_logger("logs")

class MongoDBHandler:
    def __init__(self, db_name: str, database_url: str, output_dir: str = None, collection_name: str = None):
        self.db_name = db_name
        self.database_url = database_url
        self.collection_name = collection_name if collection_name else None
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _find_tool(self, tool_name: str):
        """
        Locate mongodump or mongorestore binary.
        """
        tool_path = shutil.which(tool_name)
        if tool_path:
            return tool_path

        system = platform.system()
        possible_paths = []

        if system == "Windows":
            possible_paths = [
                Path("C:/Program Files/MongoDB"),
                Path("C:/Program Files/MongoDB/Server"),
                Path("C:/Program Files (x86)/MongoDB"),
            ]
            for base in possible_paths:
                if base.exists():
                    for version_dir in base.iterdir():
                        bin_path = version_dir / "bin" / f"{tool_name}.exe"
                        if bin_path.exists():
                            return str(bin_path)

        elif system in ("Linux", "Darwin"):
            possible_paths = [
                f"/usr/bin/{tool_name}",
                f"/usr/local/bin/{tool_name}",
                f"/opt/homebrew/bin/{tool_name}",
            ]
            for path in possible_paths:
                if Path(path).exists():
                    return path

        raise FileNotFoundError(f"{tool_name} not found. Make sure MongoDB Database Tools are installed and {tool_name} is in your PATH.")

    def test_connection(self):
        """
        Test connection to MongoDB.
        """
        try:
            client = MongoClient(self.database_url, serverSelectionTimeoutMS=5000)

            # Ping server
            client.admin.command("ping")
            logger.info(f"Successfully connected to MongoDB server.")

            # List databases
            db_list = client.list_database_names()
            if self.db_name not in db_list:
                raise Exception(f"Database '{self.db_name}' does not exist on the server.")

            logger.info(f"Database '{self.db_name}' exists.")

            if self.collection_name:
                collection_list = client[self.db_name].list_collection_names()
                if self.collection_name not in collection_list:
                    raise Exception(f"Collection '{self.collection_name}' does not exist in database '{self.db_name}'.")
                logger.info(f"Collection '{self.collection_name}' exists in database '{self.db_name}'.")

            client.close()
            return True
        except ConnectionFailure as e:
            raise Exception(f"Could not connect to MongoDB server at {self.host}:{self.port}: {e}")
        except OperationFailure as e:
            raise Exception(f"Authentication failed: {e}")
        except Exception as e:
            raise Exception(f"Unexpected connection error: {e}")

    def backup(self):
        """
        Backup the MongoDB database using mongodump.
        """
        mongodump_path = self._find_tool("mongodump")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_db_name = self.db_name.replace(" ", "_")

        if self.collection_name:
            backup_dir = self.output_dir / f"{safe_db_name}_{self.collection_name}_backup_{timestamp}"
        else:
            backup_dir = self.output_dir / f"{safe_db_name}_backup_{timestamp}"

        command = [
            mongodump_path,
            "--uri", self.database_url,
            "--out", str(backup_dir),
            "--authenticationDatabase", "admin",
        ]

        # If collection specified, add --collection
        if self.collection_name:
            command.extend(["--collection", self.collection_name])

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Backup failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

        return backup_dir

    def restore(self, backup_dir):
        """
        Restore the MongoDB database using mongorestore.
        """
        mongorestore_path = self._find_tool("mongorestore")

        # Base command with URI
        command = [
            mongorestore_path,
            "--uri", self.database_url,
            "--authenticationDatabase", "admin",
            "--drop"
        ]

        # If restoring a specific collection
        if self.collection_name:
            # Path to the .bson file of that collection
            collection_bson = Path(backup_dir) / self.db_name / f"{self.collection_name}.bson"
            if not collection_bson.exists():
                raise FileNotFoundError(
                    f"Collection BSON file not found: {collection_bson}"
                )
            command.extend([
                "--nsInclude", f"{self.db_name}.{self.collection_name}",
                "--collection", self.collection_name,
                "--db", self.db_name,
                "--file", str(collection_bson)
            ])
        else:
            # Full database restore from directory
            db_dir = Path(backup_dir) / self.db_name
            if not db_dir.exists():
                raise FileNotFoundError(
                    f"Backup directory for the database not found: {db_dir}"
                )

            command.extend([
                "--nsInclude", f"{self.db_name}.*",
                "--dir", str(db_dir)
            ])

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Restore failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Restore process error: {e}")
