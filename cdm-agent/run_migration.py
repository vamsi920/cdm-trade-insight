#!/usr/bin/env python3
"""
Run database migration to create narrative_cache table
"""
import os
from common.db import conn, execute_migration

def run_migrations():
    """Execute all migrations"""
    cnx = conn()
    
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
    
    print("Running migrations...")
    for migration_file in migration_files:
        print(f"  Applying {migration_file}...")
        migration_path = os.path.join(migrations_dir, migration_file)
        
        with open(migration_path, 'r') as f:
            sql = f.read()
        
        try:
            execute_migration(cnx, sql)
            print(f"  ✓ {migration_file} applied successfully")
        except Exception as e:
            print(f"  ✗ Error applying {migration_file}: {e}")
            raise
    
    cnx.close()
    print("\nAll migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()

