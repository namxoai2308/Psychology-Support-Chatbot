"""Legacy helper script to run the unified migrations for the `ratings` table.

Migration chuẩn cho bảng `ratings` đã được gom vào `app.core.migrations`.
File này giữ lại để bạn có thể chạy thủ công:

    python backend/migrate_add_ratings.py
"""

from app.core.migrations import check_and_add_ratings_table


def migrate() -> None:
    """Run only the `ratings` table migration using the shared logic."""
    print("🔧 Running unified migration: create 'ratings' table if missing...")
    check_and_add_ratings_table()
    print("✅ Done.")


if __name__ == "__main__":
    migrate()
