"""Legacy helper script (PostgreSQL/SQLite) for running unified migrations.

Trước đây file này tự kết nối DB bằng `psycopg2`/`sqlite3`.
Giờ toàn bộ logic đã dồn về `app.core.migrations`, dùng SQLAlchemy.

Giữ lại file này để bạn có thể chạy:

    python backend/migrate_add_sources_postgres.py

và nó sẽ dùng đúng logic chung thay vì code riêng lẻ.
"""

from app.core.migrations import check_and_add_sources_column


def migrate() -> None:
    """Run the `sources` column migration using the shared SQLAlchemy logic."""
    print("🔧 Running unified migration for 'sources' column (Postgres/SQLite)...")
    check_and_add_sources_column()
    print("✅ Done.")


if __name__ == "__main__":
    migrate()
