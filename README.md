# 🛡️ Database Backup Utility

A modular Python-based utility to **backup** and **restore** databases via CLI. Designed to support multiple DBMS types (PostgreSQL, MySQL, MongoDB, SQLite).

---

## 🔗 Project URL

Project on Roadmap.sh: [https://roadmap.sh/projects/database-backup-utility](https://roadmap.sh/projects/database-backup-utility)

---

## 🧰 Supported Database Types

| Database   | Backup | Restore |
|------------|--------|---------|
| PostgreSQL | ✅     | ✅     |
| MySQL      | ✅     | ✅     |
| MongoDB    | ✅     | ✅     |
| SQLite     | ✅     | ✅     |


## 📦 Features

- 🔄 Backup for (PostgreSQL, MySQL, MongoDB, SQLite)
- ♻️ Restore using backup files
- 💾 Backup in different formats
- 🧩 Database URL parsing or manual connection parameters
- 📁 Configurable output path and file format
- 📦 Compressed backups (planned)
- 🧪 Connection testing & logging
- 🖥️ Cross-platform support: **Windows**, **Linux**, **MacOS**

---

## ⚙️ Setup

### 🔹 Clone the Repository

```bash
git clone git@github.com:Somvit09/Database-Backup-Utility.git
cd Database-Backup-Utility
```

### 🔹 Create and Activate Virtual Environment

#### Windows

```powershell
python -m venv venv
.venv\Scripts\activate
```

#### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

### 🔹 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 PostgreSQL Usage

### ✅ Backup

```bash
python cli.py backup --db-type postgres --database-url postgresql://<user>:<password>@<host>:<port>/<db_name> --format sql
```

Example:

```bash
python cli.py backup --db-type postgres --database-url postgresql://postgres:password@localhost:5432/test_db --format sql
```

📝 You can also pass values manually instead of a URL:

```bash
python cli.py backup --db-type postgres --host localhost --port 5432 --user postgres --password --db-name test_db --format sql
```

### ♻️ Restore

```bash
python cli.py restore --db-type postgres --database-url postgresql://<user>:<password>@<host>:<port>/<db_name> --format sql --file-path <path-to-backup-file>
```

Example:

```bash
python cli.py restore --db-type postgres --database-url postgresql://postgres:password@localhost:5432/test_db --format sql --file-path OUTPUT/test_db_backup_20250625_212130.sql
```

---

## 🪵 Logging

Logs are written to `logs/backup.log` with the following format:

```
2025-06-25 21:21:29,789 - INFO - Testing connection on postgresql database named 'postgres' at localhost:5432.
2025-06-25 21:21:30,136 - INFO - Connected to postgres database successfully.
2025-06-25 21:21:48,962 - INFO - Backup file saved at: ... Total time taken: X minutes.
```

---

## 📂 Project Structure

```
DATABASE-BACKUP-UTILITY/
│
├── cli.py
├── logger.py
├── db_handlers/
│   └── postgres_handlers/
│       ├── methods.py
│       └── postgres.py
├── logs/
│   └── backup.log
├── OUTPUT/
├── validation.py
├── requirements.txt
└── README.md
```

---

## 📜 License

MIT License © 2025
