import logging
from glob import glob

import duckdb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.conn = duckdb.connect(db_path)
        self.make_migrations()

    def register_token(self, user_id: str, username: str, api_token: str) -> str:
        exists = self.conn.execute(
            "SELECT 1 FROM users WHERE discord_id = ?::BIGINT;",
            (user_id,),
        ).fetchone()

        if exists:
            self.conn.execute(
                "UPDATE users SET global_name = ?, api_token = ?, updated_at = CURRENT_TIMESTAMP WHERE discord_id = ?::BIGINT;",
                (username, api_token, user_id),
            )

            return 'Token updated successfully.'

        self.conn.execute(
            "INSERT INTO users (discord_id, global_name, api_token) VALUES (?::BIGINT, ?, ?);",
            (user_id, username, api_token),
        )

        return 'Token registered successfully.'

    def close(self):
        self.conn.close()

    def make_migrations(self):
        table_exists = bool(self.conn.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_name = 'migrations';"
        ).fetchone())
        applied_migrations = [item[0] for item in self.conn.execute("SELECT name FROM migrations;").fetchall()] if table_exists else []
        all_migrations = glob(r"migrations\*.sql")

        if len(applied_migrations) != len(all_migrations):
            logger.info("Applying migrations...")
            for migration in all_migrations:
                migration_name = migration.split("\\")[-1]
                if migration_name not in applied_migrations:
                    with open(migration, "r") as f:
                        sql = f.read()
                        self.conn.sql(sql)
                        self.conn.execute(
                            "INSERT INTO migrations (name) VALUES (?);",
                            (migration_name,),
                        )
                        logger.info(f"Applied migration: {migration_name}")
