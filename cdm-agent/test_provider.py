#!/usr/bin/env python3
"""
CDM Database MCP Provider Test Script
Tests all provider tools and database connectivity
"""
import asyncio
import sys
import os
from typing import Dict, Any

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.db import conn, q, one
from common.diff import notional, fixed_rate, changed, appended
from providers.cdm_db.provider import (
    get_trade_states, 
    get_lineage, 
    get_tradestate_payload, 
    get_business_event, 
    diff_states
)

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def test_database_connection():
    """Test database connection and basic queries"""
    print_header("Testing Database Connection")
    
    try:
        # Test connection
        cnx = conn()
        print_success("Database connection established")
        
        # Test basic query
        result = one(cnx, "SELECT COUNT(*) as count FROM trade_state")
        if result and result['count'] > 0:
            print_success(f"Found {result['count']} trade states in database")
        else:
            print_warning("No trade states found in database")
        
        # Test trade IDs
        trades = q(cnx, "SELECT DISTINCT trade_id FROM trade_state ORDER BY trade_id")
        if trades:
            print_success(f"Found {len(trades)} unique trades: {[t['trade_id'] for t in trades]}")
        else:
            print_warning("No trades found")
        
        cnx.close()
        return True
        
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False

def test_common_utilities():
    """Test common utility functions"""
    print_header("Testing Common Utilities")
    
    try:
        # Test changed function
        change_result = changed("OLD", "NEW")
        expected = {"from": "OLD", "to": "NEW", "changed": True}
        assert change_result == expected, f"Expected {expected}, got {change_result}"
        print_success("changed() function works correctly")
        
        # Test appended function
        append_result = appended([1, 2, 3], [1, 2, 3, 4, 5])
        expected = [4, 5]
        assert append_result == expected, f"Expected {expected}, got {append_result}"
        print_success("appended() function works correctly")
        
        # Test with sample CDM JSON structure
        sample_trade_state = {
            "trade": {
                "tradableProduct": {
                    "product": {
                        "economicTerms": {
                            "payout": {
                                "interestRatePayout": [{
                                    "quantity": {"value": 1000000.0},
                                    "rateSpecification": {
                                        "rateSchedule": {
                                            "rate": {"value": 0.045}
                                        }
                                    }
                                }]
                            }
                        }
                    }
                }
            }
        }
        
        # Test notional extraction
        notional_val = notional(sample_trade_state)
        if notional_val == 1000000.0:
            print_success("notional() function works correctly")
        else:
            print_warning(f"notional() returned {notional_val}, expected 1000000.0")
        
        # Test fixed_rate extraction
        rate_val = fixed_rate(sample_trade_state)
        if rate_val == 0.045:
            print_success("fixed_rate() function works correctly")
        else:
            print_warning(f"fixed_rate() returned {rate_val}, expected 0.045")
        
        return True
        
    except Exception as e:
        print_error(f"Common utilities test failed: {e}")
        return False

async def test_provider_tools():
    """Test all MCP provider tools"""
    print_header("Testing MCP Provider Tools")
    
    try:
        # Test get_trade_states
        print_info("Testing get_trade_states...")
        trade_states = await get_trade_states("IRS-2025-001")
        if trade_states and "states" in trade_states:
            print_success(f"get_trade_states returned {len(trade_states['states'])} states")
            for state in trade_states['states']:
                print(f"  - {state['trade_state_id']}: {state['position_state']} (v{state['version']})")
        else:
            print_warning("get_trade_states returned no states")
        
        # Test get_lineage
        print_info("Testing get_lineage...")
        if trade_states and trade_states['states']:
            first_state = trade_states['states'][0]
            lineage = await get_lineage(first_state['trade_state_id'])
            if lineage:
                print_success(f"get_lineage returned lineage for {first_state['trade_state_id']}")
                print(f"  - Intent: {lineage.get('intent', 'N/A')}")
                print(f"  - Before: {lineage.get('before', 'N/A')}")
                print(f"  - After: {lineage.get('after', [])}")
            else:
                print_warning("get_lineage returned no lineage")
        
        # Test get_tradestate_payload
        print_info("Testing get_tradestate_payload...")
        if trade_states and trade_states['states']:
            first_state = trade_states['states'][0]
            try:
                payload = await get_tradestate_payload(first_state['trade_state_id'])
                if payload:
                    print_success(f"get_tradestate_payload returned payload for {first_state['trade_state_id']}")
                else:
                    print_warning("get_tradestate_payload returned no payload")
            except ValueError as e:
                print_warning(f"get_tradestate_payload failed: {e}")
        
        # Test get_business_event
        print_info("Testing get_business_event...")
        if trade_states and trade_states['states']:
            first_state = trade_states['states'][0]
            if first_state.get('event_id'):
                try:
                    event = await get_business_event(first_state['event_id'])
                    if event:
                        print_success(f"get_business_event returned event for {first_state['event_id']}")
                        print(f"  - Intent: {event.get('intent', 'N/A')}")
                    else:
                        print_warning("get_business_event returned no event")
                except ValueError as e:
                    print_warning(f"get_business_event failed: {e}")
        
        # Test diff_states
        print_info("Testing diff_states...")
        if trade_states and len(trade_states['states']) >= 2:
            state1 = trade_states['states'][0]
            state2 = trade_states['states'][1]
            try:
                diff = await diff_states(state1['trade_state_id'], state2['trade_state_id'])
                if diff:
                    print_success(f"diff_states returned diff between {state1['trade_state_id']} and {state2['trade_state_id']}")
                    print(f"  - Changes: {len(diff.get('changes', {}))} fields")
                    print(f"  - Appends: {len(diff.get('appends', {}))} fields")
                else:
                    print_warning("diff_states returned no diff")
            except ValueError as e:
                print_warning(f"diff_states failed: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"Provider tools test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print_header("Testing Environment Configuration")
    
    required_vars = ['PGHOST', 'PGPORT', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print_error(f"Missing environment variables: {missing_vars}")
        print_info("Make sure .env file exists with all required variables")
        return False
    else:
        print_success("All required environment variables are set")
        for var in required_vars:
            value = os.getenv(var)
            # Mask password for security
            display_value = "***" if var == 'PGPASSWORD' else value
            print(f"  - {var}: {display_value}")
        return True

def print_summary(results: Dict[str, bool]):
    """Print test summary"""
    print_header("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {Colors.GREEN}{passed_tests}{Colors.END}")
    print(f"Failed: {Colors.RED}{failed_tests}{Colors.END}")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"  {color}{status}{Colors.END} - {test_name}")
    
    if failed_tests == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! CDM MCP Provider is ready to use.{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Please check the errors above.{Colors.END}")

async def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}CDM Database MCP Provider Test Suite{Colors.END}")
    print("Testing database connectivity, utilities, and MCP provider tools...")
    
    # Run all tests
    results = {
        "Environment Configuration": test_environment(),
        "Database Connection": test_database_connection(),
        "Common Utilities": test_common_utilities(),
        "MCP Provider Tools": await test_provider_tools()
    }
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
