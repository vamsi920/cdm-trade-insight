"""
Test Configuration for CDM MCP Provider
Configuration settings for running tests
"""
import os
from typing import Dict, Any

# Test database configuration
TEST_CONFIG = {
    "database": {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "database": os.getenv("PGDATABASE", "cdm_demo"),
        "user": os.getenv("PGUSER", "cdm"),
        "password": os.getenv("PGPASSWORD", "cdm")
    },
    "test_data": {
        "sample_trade_ids": ["IRS-2025-001", "EQS-2025-002", "CDS-2025-003"],
        "sample_state_ids": ["TS-IRS-001-EXEC", "TS-IRS-001-CONF", "TS-EQS-002-EXEC"],
        "sample_event_ids": ["EVT-IRS-001-EXEC", "EVT-IRS-001-CONF", "EVT-EQS-002-EXEC"]
    },
    "expected_counts": {
        "min_trade_states": 10,
        "min_cdm_outputs": 10,
        "min_trades": 3
    }
}

def get_test_config() -> Dict[str, Any]:
    """Get test configuration"""
    return TEST_CONFIG

def validate_environment() -> bool:
    """Validate that all required environment variables are set"""
    required_vars = ['PGHOST', 'PGPORT', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please ensure .env file exists with all required variables")
        return False
    
    return True

def print_test_info():
    """Print test configuration information"""
    config = get_test_config()
    print("🧪 CDM MCP Provider Test Configuration")
    print("=" * 50)
    print(f"Database: {config['database']['database']}@{config['database']['host']}:{config['database']['port']}")
    print(f"User: {config['database']['user']}")
    print(f"Sample Trade IDs: {config['test_data']['sample_trade_ids']}")
    print(f"Expected minimum records:")
    print(f"  - Trade States: {config['expected_counts']['min_trade_states']}")
    print(f"  - CDM Outputs: {config['expected_counts']['min_cdm_outputs']}")
    print(f"  - Unique Trades: {config['expected_counts']['min_trades']}")
    print("=" * 50)




