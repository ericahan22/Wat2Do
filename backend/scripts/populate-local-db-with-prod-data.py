#!/usr/bin/env python3
# TODO (tonyqiu): issues with this script where it fails when NOT PRODUCTION=1 in .env.
"""
Usage:
    python backend/scripts/populate-local-db-with-prod-data.py
"""

import os
import sys

import django
from django.apps import apps

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
# Ensure we're not in production mode
os.environ.pop("PRODUCTION", None)
django.setup()


def get_all_models():
    """Get all Django models automatically with proper dependency order"""
    from django.contrib.auth.models import Group, Permission, User
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.sessions.models import Session

    # Define import order to handle dependencies correctly
    system_models = [
        ContentType,  # Must come first - referenced by permissions
        Permission,  # Depends on ContentType
        Group,  # Can reference permissions
        User,  # Can reference groups and permissions
        Session,  # Independent
    ]

    # Get all other models (excluding system models)
    other_models = []
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            if model not in system_models:
                other_models.append(model)

    # Return in dependency order: system models first, then others
    return system_models + other_models


def get_production_connection():
    """Get a direct connection to the production database"""
    import psycopg2

    # Production database connection parameters
    prod_config = {
        "host": os.getenv("POSTGRES_HOST", "your-project.supabase.co"),
        "port": os.getenv("POSTGRES_PORT", "6543"),
        "database": os.getenv("POSTGRES_DB", "postgres"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "your-supabase-password"),
        "sslmode": "require",
    }

    try:
        return psycopg2.connect(**prod_config)
    except Exception as e:
        print(f"❌ Failed to connect to production database: {e}")
        print("💡 Make sure your production environment variables are set:")
        print("   - POSTGRES_HOST")
        print("   - POSTGRES_PORT")
        print("   - POSTGRES_DB")
        print("   - POSTGRES_USER")
        print("   - POSTGRES_PASSWORD")
        raise


def get_local_connection():
    """Get a direct connection to the local Docker database"""
    import psycopg2

    # Local database connection parameters
    local_config = {
        "host": "localhost",
        "port": "5432",
        "database": "postgres",
        "user": "postgres",
        "password": "postgres",
    }

    try:
        return psycopg2.connect(**local_config)
    except Exception as e:
        print(f"❌ Failed to connect to local database: {e}")
        print("💡 Make sure your local Docker database is running:")
        print("   docker-compose up -d postgres")
        raise


def sync_data():
    print("🔄 Syncing ALL data from production to local...")

    # Get all models automatically
    all_models = get_all_models()
    print(f"📋 Found {len(all_models)} models to sync")

    # Export from production database
    print("📤 Exporting from production...")
    production_data = {}

    # Get production connection
    prod_conn = get_production_connection()

    try:
        with prod_conn.cursor() as cursor:
            for model in all_models:
                model_name = model.__name__
                try:
                    # Use raw SQL to get data from production
                    table_name = model._meta.db_table
                    cursor.execute(f"SELECT * FROM {table_name}")
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()

                    # Convert to list of dicts
                    data = [dict(zip(columns, row, strict=False)) for row in rows]
                    production_data[model_name] = data
                    print(f"   - {len(data)} {model_name.lower()}")
                except Exception as e:
                    print(f"   ⚠️  Skipping {model_name}: {e}")
    finally:
        prod_conn.close()

    # Import to local database using direct connection
    print("📥 Importing to local database...")

    # Get local database connection
    local_conn = get_local_connection()

    try:
        # Clear local data (reverse order to handle foreign keys)
        print("🗑️  Clearing local data...")
        with local_conn.cursor() as cursor:
            for model in reversed(all_models):
                model_name = model.__name__
                try:
                    table_name = model._meta.db_table
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        cursor.execute(f"DELETE FROM {table_name}")
                        print(f"   🗑️  Cleared {count} {model_name.lower()}")
                except Exception as e:
                    print(f"   ⚠️  Could not clear {model_name}: {e}")

        # Import data to local database
        for model_name, data in production_data.items():
            try:
                model = next(m for m in all_models if m.__name__ == model_name)
                print(f"   Importing {len(data)} {model_name.lower()}...")

                if not data:
                    continue

                table_name = model._meta.db_table
                columns = list(data[0].keys())

                # Use a new cursor for each model to avoid transaction issues
                with local_conn.cursor() as cursor:
                    successful_inserts = 0
                    for record_data in data:
                        try:
                            # Build INSERT statement
                            placeholders = ", ".join(["%s"] * len(columns))
                            column_names = ", ".join(columns)

                            # Convert data types properly for PostgreSQL
                            values = []
                            for col in columns:
                                value = record_data[col]

                                # Handle different data types
                                if value is None:
                                    values.append(None)
                                elif isinstance(value, dict):
                                    # Convert dict to JSON string for JSONB columns
                                    import json

                                    values.append(json.dumps(value))
                                elif isinstance(value, list):
                                    # Convert list to JSON string for JSONB columns
                                    import json

                                    values.append(json.dumps(value))
                                else:
                                    values.append(value)

                            cursor.execute(
                                f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})",
                                values,
                            )
                            successful_inserts += 1
                        except Exception as e:
                            # Only show foreign key constraint errors for debugging
                            if "foreign key constraint" in str(e).lower():
                                print(f"   ⚠️  Skipping record: {e}")
                            else:
                                # For other errors, show more detail
                                print(f"   ⚠️  Skipping record: {e}")

                    # Commit after each model to prevent transaction abort cascades
                    local_conn.commit()
                    print(
                        f"   ✅ Successfully imported {successful_inserts}/{len(data)} {model_name.lower()}"
                    )

            except Exception as e:
                print(f"   ⚠️  Could not import {model_name}: {e}")
                # Rollback and continue with next model
                local_conn.rollback()

    finally:
        local_conn.close()

    print("✅ ALL data sync completed automatically!")


if __name__ == "__main__":
    sync_data()
