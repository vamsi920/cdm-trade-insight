"""
Database connection utilities for CDM MCP Provider
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def conn():
    """Create PostgreSQL connection using environment variables"""
    return psycopg2.connect(
        host=os.getenv('PGHOST', 'localhost'),
        port=os.getenv('PGPORT', '5432'),
        database=os.getenv('PGDATABASE', 'cdm_demo'),
        user=os.getenv('PGUSER', 'cdm'),
        password=os.getenv('PGPASSWORD', 'cdm'),
        cursor_factory=RealDictCursor
    )

def q(cnx, sql, params=None):
    """Execute query returning list of dicts"""
    with cnx.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()

def one(cnx, sql, params=None):
    """Execute query returning single dict or None"""
    with cnx.cursor() as cursor:
        cursor.execute(sql, params)
        result = cursor.fetchone()
        return result