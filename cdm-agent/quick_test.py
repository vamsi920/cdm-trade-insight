#!/usr/bin/env python3
"""
Quick CDM MCP Provider Test
Simple validation script for basic functionality
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def quick_test():
    """Quick test of CDM MCP Provider"""
    print("🚀 CDM MCP Provider Quick Test")
    print("=" * 40)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from common.db import conn, q, one
        from common.diff import notional, fixed_rate, changed, appended
        from providers.cdm_db.provider import get_trade_states, get_lineage
        print("   ✅ All imports successful")
        
        # Test database connection
        print("2. Testing database connection...")
        cnx = conn()
        result = one(cnx, "SELECT COUNT(*) as count FROM trade_state")
        print(f"   ✅ Connected to database, found {result['count']} trade states")
        cnx.close()
        
        # Test basic query
        print("3. Testing basic query...")
        cnx = conn()
        trades = q(cnx, "SELECT DISTINCT trade_id FROM trade_state LIMIT 3")
        print(f"   ✅ Found trades: {[t['trade_id'] for t in trades]}")
        cnx.close()
        
        # Test MCP tools
        print("4. Testing MCP tools...")
        if trades:
            trade_id = trades[0]['trade_id']
            states = await get_trade_states(trade_id)
            print(f"   ✅ get_trade_states returned {len(states['states'])} states for {trade_id}")
            
            if states['states']:
                state_id = states['states'][0]['trade_state_id']
                lineage = await get_lineage(state_id)
                print(f"   ✅ get_lineage returned lineage for {state_id}")
        
        print("\n🎉 All tests passed! CDM MCP Provider is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
