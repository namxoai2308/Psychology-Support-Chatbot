"""Legacy helper script to run the unified migrations for the `sources` column.

Hiện tại migration chính đã được gom vào `app.core.migrations`.
File này chỉ còn vai trò tiện chạy thủ công:

    python backend/migrate_add_sources.py
"""

from app.core.migrations import check_and_add_sources_column


def migrate() -> None:
    """Run only the `sources` column migration using the shared logic."""
    print("🔧 Running unified migration: add 'sources' column if missing...")
    check_and_add_sources_column()
    print("✅ Done.")


if __name__ == "__main__":
    migrate()
