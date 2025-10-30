# CDM Reference MCP Provider

A Model Context Protocol (MCP) provider for CDM type definitions, enums, and validation. This provider exposes tools that agents and UIs can use to:

- Look up CDM type definitions and field information
- Retrieve enum values and descriptions
- Validate CDM JSON payloads against object types
- Navigate the CDM type system

## Purpose

This provider provides read-only access to CDM reference data including:

- Type definitions and field metadata
- Enum values and their display names
- Validation of CDM JSON structures
- Schema introspection for CDM objects

## Available Tools

### `cdm_reference(pathOrType: str)`

Get CDM type definition, fields, and enums for a given path or type.

**Parameters:**

- `pathOrType`: CDM path or object type (e.g., "BusinessEvent", "cdm.product.template.EconomicTerms")

**Returns:**

```json
{
  "name": "BusinessEvent",
  "description": "CDM reference for BusinessEvent (stub mode)",
  "fields": [],
  "enums": []
}
```

### `validate_payload(object_type: str, json_payload: dict)`

Validate CDM JSON payload against object type.

**Parameters:**

- `object_type`: CDM object type (e.g., "BusinessEvent", "TradeState")
- `json_payload`: CDM JSON payload to validate

**Returns:**

```json
{
  "valid": true,
  "issues": []
}
```

## Current Implementation Status

**⚠️ STUB MODE**: This provider currently runs in stub mode with placeholder implementations. The following features are planned for future implementation:

### Planned Features

1. **Py4J Bridge Integration**

   - Connect to CDM Java JAR via Py4J gateway
   - Access CDM type system and validation classes
   - Real-time type introspection and validation

2. **Environment Configuration**

   - `CDM_JAR_PATH`: Path to cdm-java JAR (from Maven build or local repo)
   - `JAVA_HOME`: Java installation path for Py4J gateway
   - `CDM_VERSION`: CDM version to use for validation

3. **Enhanced Type Information**
   - Field types, constraints, and relationships
   - Enum values with display names and descriptions
   - Inheritance hierarchies and type relationships
   - Validation rules and business logic constraints

## Future Integration

### CDM Java JAR Setup

The provider will eventually integrate with the CDM Java distribution:

```xml
<dependency>
    <groupId>org.finos.cdm</groupId>
    <artifactId>cdm-java</artifactId>
    <version>LATEST</version>
</dependency>
```

### Py4J Configuration

```python
# Future implementation will include:
from py4j.java_gateway import JavaGateway

gateway = JavaGateway()
cdm_validator = gateway.entry_point.getValidator()
cdm_types = gateway.entry_point.getTypeSystem()
```

### Example Usage

```python
# Future usage examples:
# Get type definition
result = await cdm_reference("BusinessEvent")
# Returns: {"name": "BusinessEvent", "fields": [...], "enums": [...]}

# Validate payload
result = await validate_payload("BusinessEvent", {"businessEvent": {...}})
# Returns: {"valid": true, "issues": []}
```

## Development Notes

- Provider follows MCP 1.18.0 API pattern
- Stub functions marked with TODO comments for Py4J integration
- Test suite validates stub functionality
- Ready for future JAR integration without API changes

## Testing

Run the test suite to verify stub functionality:

```bash
cd cdm-agent
python test_cdm_ref.py
```

The tests will confirm:

- Provider starts successfully
- Tools are registered and callable
- Stub responses return valid JSON structures
- Clear indication of stub mode operation
