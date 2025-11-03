# ⚠️ IMPORTANT: Run Database Migration First!

## Error You're Seeing

```
psycopg2.errors.UndefinedTable: relation "narrative_cache" does not exist
```

This means the database table hasn't been created yet.

## Quick Fix (Run This Now)

```bash
cd /Users/vamsi/Desktop/cdm-trade-insight/cdm-agent
python run_migration.py
```

## Expected Output

You should see:
```
Running migrations...
  Applying 001_narrative_cache.sql...
  ✓ 001_narrative_cache.sql applied successfully

All migrations completed successfully!
```

## Verify Table Was Created

```bash
psql -h localhost -U cdm -d cdm_demo -c "\d narrative_cache"
```

Should show table structure with columns:
- id, cache_key, narrative_type, trade_id, event_id, perspective
- narrative_text, generation_metadata, created_at, updated_at, version_hash

## Then Restart Your Backend

```bash
cd /Users/vamsi/Desktop/cdm-trade-insight/cdm-agent
python api/main.py
```

## Now Test

1. Refresh your frontend
2. Select a trade
3. You should now see a "Generate Summary" button
4. Click it to generate the narrative

---

**After running the migration, the 500 errors will be fixed!**

