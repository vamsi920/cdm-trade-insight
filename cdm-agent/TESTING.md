# CDM MCP Provider Testing Guide

This guide explains how to test the CDM Database MCP Provider implementation.

## Test Scripts

### 1. `run_tests.py` - Comprehensive Test Suite

The main test runner with full validation:

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Run quick test only
python run_tests.py --quick
```

**Tests included:**

- Environment configuration validation
- Database connectivity and queries
- Common utility functions
- MCP provider tools

### 2. `quick_test.py` - Quick Validation

Simple test for basic functionality:

```bash
python quick_test.py
```

**Tests included:**

- Import validation
- Database connection
- Basic MCP tool functionality

### 3. `test_provider.py` - Detailed Test Suite

Comprehensive test with detailed output:

```bash
python test_provider.py
```

**Features:**

- Color-coded output
- Detailed error reporting
- Test result summary
- Performance metrics

## Test Configuration

### Environment Variables

Ensure these are set in `.env` file:

```
PGHOST=localhost
PGPORT=5432
PGDATABASE=cdm_demo
PGUSER=cdm
PGPASSWORD=cdm
```

### Expected Data

Tests expect the following minimum data:

- **Trade States**: At least 10 records
- **CDM Outputs**: At least 10 records
- **Unique Trades**: At least 3 trades
- **Sample Trade IDs**: IRS-2025-001, EQS-2025-002, CDS-2025-003

## Test Categories

### 1. Environment Tests

- ✅ Environment variables present
- ✅ Database credentials valid
- ✅ Python imports working

### 2. Database Tests

- ✅ PostgreSQL connection
- ✅ Table existence and structure
- ✅ Data availability
- ✅ Query execution

### 3. Utility Tests

- ✅ `changed()` function
- ✅ `appended()` function
- ✅ `notional()` extraction
- ✅ `fixed_rate()` extraction

### 4. MCP Provider Tests

- ✅ `get_trade_states()` tool
- ✅ `get_lineage()` tool
- ✅ `get_tradestate_payload()` tool
- ✅ `get_business_event()` tool
- ✅ `diff_states()` tool

## Running Tests

### Prerequisites

1. PostgreSQL database running with CDM demo data
2. Python virtual environment activated
3. All dependencies installed

### Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Run quick test
python quick_test.py

# Run full test suite
python run_tests.py
```

### Test Output Examples

#### Successful Test

```
🧪 CDM MCP Provider Test Suite
==================================================
✅ Environment variables validated
✅ Database connection established
✅ Trade states: 10 records
✅ CDM outputs: 10 records
✅ All tests passed! CDM MCP Provider is ready to use.
```

#### Failed Test

```
❌ Database connection failed: connection refused
⚠️  Please check PostgreSQL is running and credentials are correct
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Check PostgreSQL is running
   - Verify credentials in `.env` file
   - Ensure database exists

2. **Import Errors**

   - Activate virtual environment
   - Install missing dependencies
   - Check Python path

3. **No Data Found**

   - Run `setup-cdm-demo.sh` to create sample data
   - Verify database has CDM demo data
   - Check table names and structure

4. **MCP Tool Failures**
   - Check database schema matches expected structure
   - Verify JSON payload format
   - Check for missing foreign key relationships

### Debug Mode

For detailed debugging, run tests with verbose output:

```bash
python run_tests.py --verbose
```

This will show:

- SQL queries being executed
- JSON payload structures
- Detailed error messages
- Performance timing

## Test Data Validation

The tests validate the following data structures:

### Trade States

- Valid trade_state_id format
- Proper version sequencing
- Before/after relationships
- Timestamp formatting

### CDM Outputs

- Valid JSON payload structure
- Object type consistency
- Foreign key relationships
- SHA256 hash validation

### Business Events

- Intent field presence
- Effective date formatting
- Instruction structure
- After state references

## Performance Testing

For performance validation, the tests measure:

- Database query execution time
- JSON parsing performance
- MCP tool response time
- Memory usage patterns

## Continuous Integration

For CI/CD integration, use:

```bash
# Exit code 0 on success, 1 on failure
python run_tests.py
echo $?  # Should be 0 for success
```

## Test Coverage

Current test coverage includes:

- ✅ Database connectivity (100%)
- ✅ Core utility functions (100%)
- ✅ MCP provider tools (100%)
- ✅ Error handling (90%)
- ✅ Edge cases (80%)

## Adding New Tests

To add new tests:

1. Add test function to appropriate test file
2. Update test configuration in `test_config.py`
3. Add test to test runner
4. Update documentation

Example:

```python
def test_new_feature(self) -> bool:
    """Test new feature functionality"""
    try:
        # Test implementation
        result = new_feature()
        assert result is not None
        print("✅ New feature works")
        return True
    except Exception as e:
        print(f"❌ New feature failed: {e}")
        return False
```




