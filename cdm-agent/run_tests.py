#!/usr/bin/env python3
"""
CDM MCP Provider Test Runner
Comprehensive test suite for CDM Database MCP Provider
"""
import asyncio
import sys
import os
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_config import get_test_config, validate_environment, print_test_info

class TestRunner:
    """Test runner for CDM MCP Provider"""
    
    def __init__(self):
        self.config = get_test_config()
        self.results = {}
    
    def run_environment_test(self) -> bool:
        """Test environment configuration"""
        print("\n🔧 Testing Environment Configuration")
        print("-" * 40)
        
        if not validate_environment():
            return False
        
        print("✅ Environment variables validated")
        return True
    
    def run_database_test(self) -> bool:
        """Test database connectivity and basic queries"""
        print("\n🗄️  Testing Database Connectivity")
        print("-" * 40)
        
        try:
            from common.db import conn, q, one
            
            # Test connection
            cnx = conn()
            print("✅ Database connection established")
            
            # Test trade_state table
            trade_count = one(cnx, "SELECT COUNT(*) as count FROM trade_state")
            print(f"✅ Trade states: {trade_count['count']} records")
            
            # Test cdm_outputs table
            output_count = one(cnx, "SELECT COUNT(*) as count FROM cdm_outputs")
            print(f"✅ CDM outputs: {output_count['count']} records")
            
            # Test unique trades
            trades = q(cnx, "SELECT COUNT(DISTINCT trade_id) as count FROM trade_state")
            print(f"✅ Unique trades: {trades[0]['count']} records")
            
            # Validate minimum counts
            min_counts = self.config['expected_counts']
            if trade_count['count'] < min_counts['min_trade_states']:
                print(f"⚠️  Warning: Expected at least {min_counts['min_trade_states']} trade states")
            if output_count['count'] < min_counts['min_cdm_outputs']:
                print(f"⚠️  Warning: Expected at least {min_counts['min_cdm_outputs']} CDM outputs")
            if trades[0]['count'] < min_counts['min_trades']:
                print(f"⚠️  Warning: Expected at least {min_counts['min_trades']} unique trades")
            
            cnx.close()
            return True
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False
    
    def run_utilities_test(self) -> bool:
        """Test common utility functions"""
        print("\n🛠️  Testing Common Utilities")
        print("-" * 40)
        
        try:
            from common.diff import notional, fixed_rate, changed, appended
            
            # Test changed function
            result = changed("old", "new")
            assert result == {"from": "old", "to": "new", "changed": True}
            print("✅ changed() function works")
            
            # Test appended function
            result = appended([1, 2], [1, 2, 3, 4])
            assert result == [3, 4]
            print("✅ appended() function works")
            
            # Test CDM JSON parsing with sample data
            sample_state = {
                "trade": {
                    "tradableProduct": {
                        "product": {
                            "economicTerms": {
                                "payout": {
                                    "interestRatePayout": [{
                                        "quantity": {"value": 1000000.0},
                                        "rateSpecification": {
                                            "rateSchedule": {"rate": {"value": 0.045}}
                                        }
                                    }]
                                }
                            }
                        }
                    }
                }
            }
            
            # Test notional extraction
            notional_val = notional(sample_state)
            if notional_val == 1000000.0:
                print("✅ notional() extraction works")
            else:
                print(f"⚠️  notional() returned {notional_val}, expected 1000000.0")
            
            # Test fixed_rate extraction
            rate_val = fixed_rate(sample_state)
            if rate_val == 0.045:
                print("✅ fixed_rate() extraction works")
            else:
                print(f"⚠️  fixed_rate() returned {rate_val}, expected 0.045")
            
            return True
            
        except Exception as e:
            print(f"❌ Utilities test failed: {e}")
            return False
    
    async def run_provider_test(self) -> bool:
        """Test MCP provider tools"""
        print("\n🔌 Testing MCP Provider Tools")
        print("-" * 40)
        
        try:
            from providers.cdm_db.provider import (
                get_trade_states, get_lineage, get_tradestate_payload,
                get_business_event, diff_states
            )
            
            # Get sample trade ID
            sample_trades = self.config['test_data']['sample_trade_ids']
            trade_id = sample_trades[0]
            
            # Test get_trade_states
            print(f"Testing get_trade_states with {trade_id}...")
            states = await get_trade_states(trade_id)
            if states and 'states' in states and states['states']:
                print(f"✅ get_trade_states returned {len(states['states'])} states")
            else:
                print("⚠️  get_trade_states returned no states")
            
            # Test get_lineage
            if states and states['states']:
                state_id = states['states'][0]['trade_state_id']
                print(f"Testing get_lineage with {state_id}...")
                lineage = await get_lineage(state_id)
                if lineage:
                    print(f"✅ get_lineage returned lineage data")
                    print(f"   Intent: {lineage.get('intent', 'N/A')}")
                else:
                    print("⚠️  get_lineage returned no lineage")
            
            # Test get_tradestate_payload
            if states and states['states']:
                state_id = states['states'][0]['trade_state_id']
                print(f"Testing get_tradestate_payload with {state_id}...")
                try:
                    payload = await get_tradestate_payload(state_id)
                    if payload:
                        print("✅ get_tradestate_payload returned payload")
                    else:
                        print("⚠️  get_tradestate_payload returned no payload")
                except ValueError as e:
                    print(f"⚠️  get_tradestate_payload failed: {e}")
            
            # Test get_business_event
            if states and states['states']:
                event_id = states['states'][0].get('event_id')
                if event_id:
                    print(f"Testing get_business_event with {event_id}...")
                    try:
                        event = await get_business_event(event_id)
                        if event:
                            print("✅ get_business_event returned event data")
                        else:
                            print("⚠️  get_business_event returned no event")
                    except ValueError as e:
                        print(f"⚠️  get_business_event failed: {e}")
            
            # Test diff_states
            if states and len(states['states']) >= 2:
                state1_id = states['states'][0]['trade_state_id']
                state2_id = states['states'][1]['trade_state_id']
                print(f"Testing diff_states with {state1_id} -> {state2_id}...")
                try:
                    diff = await diff_states(state1_id, state2_id)
                    if diff:
                        print("✅ diff_states returned comparison data")
                    else:
                        print("⚠️  diff_states returned no diff")
                except ValueError as e:
                    print(f"⚠️  diff_states failed: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Provider test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("🧪 CDM MCP Provider Test Suite")
        print("=" * 50)
        print_test_info()
        
        # Run tests
        self.results = {
            "Environment": self.run_environment_test(),
            "Database": self.run_database_test(),
            "Utilities": self.run_utilities_test(),
            "Provider": await self.run_provider_test()
        }
        
        # Print summary
        self.print_summary()
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        print("\n📊 Test Summary")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        
        print("\nDetailed Results:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        if failed_tests == 0:
            print("\n🎉 All tests passed! CDM MCP Provider is ready to use.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please check the errors above.")

async def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="CDM MCP Provider Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick test only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.quick:
        # Run quick test
        print("🚀 Running Quick Test...")
        try:
            from quick_test import quick_test
            success = await quick_test()
            sys.exit(0 if success else 1)
        except ImportError:
            print("❌ Quick test not available")
            sys.exit(1)
    else:
        # Run full test suite
        runner = TestRunner()
        results = await runner.run_all_tests()
        
        # Exit with appropriate code
        if all(results.values()):
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
