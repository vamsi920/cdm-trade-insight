"""
Script to clear all narrative data from database for testing
Deletes all rows from narrative_cache and narrative_logs tables
"""
import sys
from common.db import conn, execute, q

def table_exists(cnx, table_name: str) -> bool:
    """Check if a table exists"""
    try:
        result = q(
            cnx,
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
            """,
            (table_name,)
        )
        return result[0]['exists'] if result else False
    except:
        return False

def clear_narratives():
    """Delete all narratives and logs from the database"""
    cnx = conn()
    try:
        print("🗑️  Clearing narrative data...")
        
        total_deleted = 0
        
        # Delete logs first (if table exists)
        if table_exists(cnx, 'narrative_logs'):
            logs_count = execute(cnx, "DELETE FROM narrative_logs")
            print(f"   ✅ Deleted {logs_count} log entries from narrative_logs")
            total_deleted += logs_count
        else:
            print("   ℹ️  narrative_logs table does not exist (skip)")
        
        # Delete narratives (if table exists)
        if table_exists(cnx, 'narrative_cache'):
            narratives_count = execute(cnx, "DELETE FROM narrative_cache")
            print(f"   ✅ Deleted {narratives_count} narratives from narrative_cache")
            total_deleted += narratives_count
        else:
            print("   ℹ️  narrative_cache table does not exist (skip)")
        
        if total_deleted == 0:
            print("\n⚠️  No data was deleted. Tables may not exist yet.")
            print("   Run 'python run_migration.py' first to create the tables.")
        else:
            print("\n✨ Database cleared successfully!")
            print("   You can now regenerate narratives and logs to test the system.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error clearing narratives: {str(e)}", file=sys.stderr)
        return False
    finally:
        cnx.close()

def clear_specific_trade(trade_id: str):
    """Delete narratives and logs for a specific trade"""
    cnx = conn()
    try:
        print(f"🗑️  Clearing narrative data for trade: {trade_id}...")
        
        total_deleted = 0
        
        # Delete logs for this trade (if table exists)
        if table_exists(cnx, 'narrative_logs'):
            logs_count = execute(
                cnx,
                "DELETE FROM narrative_logs WHERE trade_id = %s",
                (trade_id,)
            )
            print(f"   ✅ Deleted {logs_count} log entries")
            total_deleted += logs_count
        else:
            print("   ℹ️  narrative_logs table does not exist (skip)")
        
        # Delete narratives for this trade (if table exists)
        if table_exists(cnx, 'narrative_cache'):
            narratives_count = execute(
                cnx,
                "DELETE FROM narrative_cache WHERE trade_id = %s",
                (trade_id,)
            )
            print(f"   ✅ Deleted {narratives_count} narratives")
            total_deleted += narratives_count
        else:
            print("   ℹ️  narrative_cache table does not exist (skip)")
        
        if total_deleted == 0:
            print(f"\n⚠️  No data found for trade {trade_id}.")
            print("   Tables may not exist yet - run 'python run_migration.py' first.")
        else:
            print(f"\n✨ Cleared all data for trade {trade_id}!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error clearing narratives: {str(e)}", file=sys.stderr)
        return False
    finally:
        cnx.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Clear specific trade
        trade_id = sys.argv[1]
        success = clear_specific_trade(trade_id)
    else:
        # Clear all narratives
        print("⚠️  WARNING: This will delete ALL narratives and logs from the database!")
        print("   Press Ctrl+C to cancel, or Enter to continue...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n❌ Cancelled.")
            sys.exit(0)
        
        success = clear_narratives()
    
    sys.exit(0 if success else 1)

