#!/usr/bin/env python3
"""
CDM Reference MCP Provider Test Script
Tests all provider tools and stub functionality
"""
import asyncio
import sys
import os
from typing import Dict, Any

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from providers.cdm_ref.provider import (
    cdm_reference, 
    validate_payload
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

def test_imports():
    """Test that all imports work correctly"""
    print_header("Testing Imports")
    
    try:
        from providers.cdm_ref.provider import cdm_reference, validate_payload
        print_success("All imports successful")
        return True
    except Exception as e:
        print_error(f"Import failed: {e}")
        return False

async def test_cdm_reference():
    """Test cdm_reference tool"""
    print_header("Testing CDM Reference Tool")
    
    try:
        # Test with BusinessEvent
        result = await cdm_reference("BusinessEvent")
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "name" in result, "Result should contain 'name' field"
        assert "description" in result, "Result should contain 'description' field"
        assert "fields" in result, "Result should contain 'fields' field"
        assert "enums" in result, "Result should contain 'enums' field"
        assert result["name"] == "BusinessEvent", "Name should match input"
        print_success("cdm_reference returned valid structure for BusinessEvent")
        
        # Test with complex type path
        result = await cdm_reference("cdm.product.template.EconomicTerms")
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result["name"] == "cdm.product.template.EconomicTerms", "Name should match input"
        print_success("cdm_reference returned valid structure for complex type")
        
        # Test with enum type
        result = await cdm_reference("DayCountFractionEnum")
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result["name"] == "DayCountFractionEnum", "Name should match input"
        print_success("cdm_reference returned valid structure for enum type")
        
        return True
        
    except Exception as e:
        print_error(f"cdm_reference test failed: {e}")
        return False

async def test_validate_payload():
    """Test validate_payload tool"""
    print_header("Testing Validate Payload Tool")
    
    try:
        # Test with valid BusinessEvent payload
        payload = {
            "businessEvent": {
                "eventDate": "2025-01-02",
                "intent": "Execution"
            }
        }
        result = await validate_payload("BusinessEvent", payload)
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "valid" in result, "Result should contain 'valid' field"
        assert "issues" in result, "Result should contain 'issues' field"
        assert result["valid"] == True, "Stub should return valid=True"
        assert isinstance(result["issues"], list), "Issues should be a list"
        print_success("validate_payload returned valid structure for BusinessEvent")
        
        # Test with TradeState payload
        payload = {
            "tradeState": {
                "trade": {
                    "tradeIdentifier": [{"assignedIdentifier": [{"identifier": "IRS-2025-001"}]}]
                },
                "state": {
                    "positionState": "EXECUTED"
                }
            }
        }
        result = await validate_payload("TradeState", payload)
        assert result["valid"] == True, "Stub should return valid=True"
        print_success("validate_payload returned valid structure for TradeState")
        
        # Test with invalid object type
        result = await validate_payload("NonExistentType", {"data": "test"})
        assert result["valid"] == True, "Stub should accept everything"
        print_success("validate_payload handled non-existent type gracefully")
        
        return True
        
    except Exception as e:
        print_error(f"validate_payload test failed: {e}")
        return False

def test_stub_mode_indicators():
    """Test that stub mode is clearly indicated"""
    print_header("Testing Stub Mode Indicators")
    
    try:
        # Check that descriptions indicate stub mode
        from providers.cdm_ref.provider import jar_describe, jar_validate
        
        result = jar_describe("TestType")
        assert "stub" in result["description"].lower(), "Description should indicate stub mode"
        print_success("jar_describe indicates stub mode in description")
        
        result = jar_validate("TestType", {"data": "test"})
        assert result["valid"] == True, "Stub validator should accept everything"
        assert len(result["issues"]) == 0, "Stub validator should have no issues"
        print_success("jar_validate accepts all payloads in stub mode")
        
        return True
        
    except Exception as e:
        print_error(f"Stub mode indicator test failed: {e}")
        return False

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
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! CDM Reference MCP Provider is working correctly in stub mode.{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Note: This provider is running in stub mode. Real CDM integration requires Py4J bridge setup.{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Please check the errors above.{Colors.END}")

async def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}CDM Reference MCP Provider Test Suite{Colors.END}")
    print("Testing stub functionality and MCP provider tools...")
    print(f"{Colors.YELLOW}⚠️  Running in STUB MODE - Real CDM integration not yet implemented{Colors.END}")
    
    # Run all tests
    results = {
        "Imports": test_imports(),
        "CDM Reference Tool": await test_cdm_reference(),
        "Validate Payload Tool": await test_validate_payload(),
        "Stub Mode Indicators": test_stub_mode_indicators()
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
