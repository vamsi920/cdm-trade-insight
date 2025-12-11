# Database Setup Prompt for CDM Trade Insight

Use this document as a prompt for your IDE Copilot to recreate the database layer.

---

## TASK

Create a database schema and seed data for a CDM (Common Domain Model) trade insight application. The system tracks derivative trade lifecycles and stores AI-generated narratives about trades.

---

## DATABASE SCHEMA

### Table 1: `trade_state` - Trade Lifecycle States

Stores each version/state of a trade as it moves through its lifecycle.

```sql
CREATE TABLE trade_state (
    trade_state_id   VARCHAR(100)  PRIMARY KEY,
    trade_id         VARCHAR(100)  NOT NULL,
    version          INTEGER       NOT NULL,
    position_state   VARCHAR(50),
    closed_state     VARCHAR(50),
    event_id         VARCHAR(100),
    before_state_id  VARCHAR(100),
    as_of            TIMESTAMP,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_before_state FOREIGN KEY (before_state_id) 
        REFERENCES trade_state(trade_state_id)
);

CREATE INDEX idx_trade_state_trade_id ON trade_state(trade_id);
CREATE INDEX idx_trade_state_before ON trade_state(before_state_id);
CREATE INDEX idx_trade_state_event ON trade_state(event_id);
```

**Column definitions:**
- `trade_state_id`: Unique identifier for this state snapshot
- `trade_id`: Logical trade identifier (groups all versions)
- `version`: Sequential version number (1, 2, 3...)
- `position_state`: EXECUTED, CONFIRMED, CLEARED, AMENDED, TERMINATED
- `closed_state`: NULL or reason for closure (FULL_TERMINATION, PARTIAL_TERMINATION)
- `event_id`: Reference to the business event that created this state
- `before_state_id`: Self-reference to previous state (lineage chain)
- `as_of`: Business effective date/time

---

### Table 2: `cdm_outputs` - CDM JSON Payloads

Stores the full CDM JSON documents for BusinessEvents and TradeStates.

```sql
CREATE TABLE cdm_outputs (
    id               INTEGER       PRIMARY KEY AUTO_INCREMENT,
    object_type      VARCHAR(50)   NOT NULL,
    trade_id         VARCHAR(100),
    event_id         VARCHAR(100),
    trade_state_id   VARCHAR(100),
    schema_version   VARCHAR(20),
    payload_json     JSON          NOT NULL,
    payload_sha256   VARCHAR(64),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cdm_outputs_event ON cdm_outputs(object_type, event_id);
CREATE INDEX idx_cdm_outputs_state ON cdm_outputs(object_type, trade_state_id);
CREATE INDEX idx_cdm_outputs_trade ON cdm_outputs(trade_id);
```

**Column definitions:**
- `object_type`: "BusinessEvent" or "TradeState"
- `payload_json`: Full CDM-compliant JSON document
- `payload_sha256`: SHA256 hash for deduplication

---

### Table 3: `narrative_cache` - AI-Generated Narratives

Caches LLM-generated narratives to avoid regeneration.

```sql
CREATE TABLE narrative_cache (
    id                   INTEGER       PRIMARY KEY AUTO_INCREMENT,
    cache_key            VARCHAR(255)  UNIQUE NOT NULL,
    narrative_type       VARCHAR(20)   NOT NULL,
    trade_id             VARCHAR(100)  NOT NULL,
    event_id             VARCHAR(100),
    perspective          VARCHAR(50),
    narrative_text       TEXT          NOT NULL,
    generation_metadata  JSON,
    version_hash         VARCHAR(64),
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_narrative_type CHECK (narrative_type IN ('trade', 'event'))
);

CREATE INDEX idx_narrative_cache_key ON narrative_cache(cache_key);
CREATE INDEX idx_narrative_trade ON narrative_cache(trade_id);
CREATE INDEX idx_narrative_event ON narrative_cache(event_id);
```

**Column definitions:**
- `cache_key`: Format "trade:{trade_id}" or "event:{trade_id}:{event_id}"
- `narrative_type`: "trade" for full trade summary, "event" for single event
- `generation_metadata`: JSON with {model, tokens_used, tool_calls, generation_time_ms}

---

### Table 4: `narrative_logs` - Generation Process Logs

Stores step-by-step logs from narrative generation for UI replay.

```sql
CREATE TABLE narrative_logs (
    id               INTEGER       PRIMARY KEY AUTO_INCREMENT,
    cache_key        VARCHAR(255)  NOT NULL,
    narrative_type   VARCHAR(20)   NOT NULL,
    trade_id         VARCHAR(100)  NOT NULL,
    event_id         VARCHAR(100),
    log_index        INTEGER       NOT NULL,
    log_type         VARCHAR(50),
    message          TEXT          NOT NULL,
    metadata         JSON,
    timestamp        TIMESTAMP,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_log_narrative_type CHECK (narrative_type IN ('trade', 'event'))
);

CREATE INDEX idx_narrative_logs_cache_key ON narrative_logs(cache_key);
CREATE INDEX idx_narrative_logs_trade ON narrative_logs(trade_id);
CREATE INDEX idx_narrative_logs_order ON narrative_logs(cache_key, log_index);
```

**Column definitions:**
- `log_index`: Order in sequence (0, 1, 2...)
- `log_type`: "cache_check", "tool_call", "tool_response", "llm_generating", "complete"

---

## SAMPLE DATA

### Trade 1: Interest Rate Swap (IRS) - Full Lifecycle

```sql
-- Trade State 1: Execution
INSERT INTO trade_state (trade_state_id, trade_id, version, position_state, closed_state, event_id, before_state_id, as_of)
VALUES ('TS-IRS-001-V1', 'IRS-2025-001', 1, 'EXECUTED', NULL, 'EVT-EXEC-001', NULL, '2025-01-15 09:30:00');

-- Trade State 2: Confirmation
INSERT INTO trade_state (trade_state_id, trade_id, version, position_state, closed_state, event_id, before_state_id, as_of)
VALUES ('TS-IRS-001-V2', 'IRS-2025-001', 2, 'CONFIRMED', NULL, 'EVT-CONF-001', 'TS-IRS-001-V1', '2025-01-15 14:00:00');

-- Trade State 3: Amendment (notional increase)
INSERT INTO trade_state (trade_state_id, trade_id, version, position_state, closed_state, event_id, before_state_id, as_of)
VALUES ('TS-IRS-001-V3', 'IRS-2025-001', 3, 'AMENDED', NULL, 'EVT-AMEND-001', 'TS-IRS-001-V2', '2025-02-01 10:00:00');

-- Trade State 4: Partial Termination
INSERT INTO trade_state (trade_state_id, trade_id, version, position_state, closed_state, event_id, before_state_id, as_of)
VALUES ('TS-IRS-001-V4', 'IRS-2025-001', 4, 'TERMINATED', 'PARTIAL_TERMINATION', 'EVT-TERM-001', 'TS-IRS-001-V3', '2025-03-15 11:30:00');
```

### CDM Outputs for Trade 1

```sql
-- BusinessEvent: Execution
INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('BusinessEvent', 'IRS-2025-001', 'EVT-EXEC-001', 'TS-IRS-001-V1', '5.0.0', '{
  "businessEvent": {
    "intent": "Execution",
    "effectiveDate": "2025-01-15",
    "eventDate": "2025-01-15",
    "primitives": [{
      "execution": {
        "product": {
          "contractualProduct": {
            "economicTerms": {
              "payout": [{
                "interestRatePayout": {
                  "quantity": {
                    "notionalSchedule": {
                      "notionalStepSchedule": {
                        "initialValue": 10000000,
                        "currency": "USD"
                      }
                    }
                  },
                  "rateSpecification": {
                    "fixedRate": {
                      "rateSchedule": {
                        "initialValue": 0.0325
                      }
                    }
                  }
                }
              }]
            }
          }
        },
        "tradeIdentifier": [{
          "assignedIdentifier": [{
            "identifier": "IRS-2025-001"
          }]
        }],
        "party": [
          {"partyId": [{"identifier": "BANK-ABC"}], "name": "Bank ABC"},
          {"partyId": [{"identifier": "CORP-XYZ"}], "name": "Corporate XYZ"}
        ]
      }
    }]
  }
}');

-- TradeState: After Execution
INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('TradeState', 'IRS-2025-001', 'EVT-EXEC-001', 'TS-IRS-001-V1', '5.0.0', '{
  "tradeState": {
    "trade": {
      "tradeIdentifier": [{
        "assignedIdentifier": [{
          "identifier": "IRS-2025-001"
        }]
      }],
      "product": {
        "contractualProduct": {
          "economicTerms": {
            "payout": [{
              "interestRatePayout": {
                "quantity": {
                  "notionalSchedule": {
                    "notionalStepSchedule": {
                      "initialValue": 10000000,
                      "currency": "USD"
                    }
                  }
                },
                "rateSpecification": {
                  "fixedRate": {
                    "rateSchedule": {
                      "initialValue": 0.0325
                    }
                  }
                }
              }
            }]
          }
        }
      },
      "party": [
        {"partyId": [{"identifier": "BANK-ABC"}], "name": "Bank ABC"},
        {"partyId": [{"identifier": "CORP-XYZ"}], "name": "Corporate XYZ"}
      ]
    },
    "state": {
      "positionState": "EXECUTED"
    }
  }
}');

-- BusinessEvent: Confirmation
INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('BusinessEvent', 'IRS-2025-001', 'EVT-CONF-001', 'TS-IRS-001-V2', '5.0.0', '{
  "businessEvent": {
    "intent": "ContractFormation",
    "effectiveDate": "2025-01-15",
    "eventDate": "2025-01-15"
  }
}');

-- TradeState: After Confirmation
INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('TradeState', 'IRS-2025-001', 'EVT-CONF-001', 'TS-IRS-001-V2', '5.0.0', '{
  "tradeState": {
    "trade": {
      "tradeIdentifier": [{"assignedIdentifier": [{"identifier": "IRS-2025-001"}]}],
      "product": {
        "contractualProduct": {
          "economicTerms": {
            "payout": [{
              "interestRatePayout": {
                "quantity": {
                  "notionalSchedule": {
                    "notionalStepSchedule": {"initialValue": 10000000, "currency": "USD"}
                  }
                },
                "rateSpecification": {
                  "fixedRate": {"rateSchedule": {"initialValue": 0.0325}}
                }
              }
            }]
          }
        }
      }
    },
    "state": {"positionState": "CONFIRMED"}
  }
}');

-- BusinessEvent: Amendment
INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('BusinessEvent', 'IRS-2025-001', 'EVT-AMEND-001', 'TS-IRS-001-V3', '5.0.0', '{
  "businessEvent": {
    "intent": "ContractAmendment",
    "effectiveDate": "2025-02-01",
    "eventDate": "2025-02-01"
  }
}');

-- TradeState: After Amendment (notional increased to 15M)
INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('TradeState', 'IRS-2025-001', 'EVT-AMEND-001', 'TS-IRS-001-V3', '5.0.0', '{
  "tradeState": {
    "trade": {
      "tradeIdentifier": [{"assignedIdentifier": [{"identifier": "IRS-2025-001"}]}],
      "product": {
        "contractualProduct": {
          "economicTerms": {
            "payout": [{
              "interestRatePayout": {
                "quantity": {
                  "notionalSchedule": {
                    "notionalStepSchedule": {"initialValue": 15000000, "currency": "USD"}
                  }
                },
                "rateSpecification": {
                  "fixedRate": {"rateSchedule": {"initialValue": 0.0325}}
                }
              }
            }]
          }
        }
      }
    },
    "state": {"positionState": "AMENDED"}
  }
}');

-- BusinessEvent: Partial Termination
INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('BusinessEvent', 'IRS-2025-001', 'EVT-TERM-001', 'TS-IRS-001-V4', '5.0.0', '{
  "businessEvent": {
    "intent": "Termination",
    "effectiveDate": "2025-03-15",
    "eventDate": "2025-03-15"
  }
}');

-- TradeState: After Partial Termination (notional reduced to 10M)
INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('TradeState', 'IRS-2025-001', 'EVT-TERM-001', 'TS-IRS-001-V4', '5.0.0', '{
  "tradeState": {
    "trade": {
      "tradeIdentifier": [{"assignedIdentifier": [{"identifier": "IRS-2025-001"}]}],
      "product": {
        "contractualProduct": {
          "economicTerms": {
            "payout": [{
              "interestRatePayout": {
                "quantity": {
                  "notionalSchedule": {
                    "notionalStepSchedule": {"initialValue": 10000000, "currency": "USD"}
                  }
                },
                "rateSpecification": {
                  "fixedRate": {"rateSchedule": {"initialValue": 0.0325}}
                }
              }
            }]
          }
        }
      }
    },
    "state": {
      "positionState": "TERMINATED",
      "closedState": "PARTIAL_TERMINATION"
    }
  }
}');
```

### Trade 2: Credit Default Swap (CDS) - Simple Lifecycle

```sql
-- Trade State 1: Execution
INSERT INTO trade_state (trade_state_id, trade_id, version, position_state, closed_state, event_id, before_state_id, as_of)
VALUES ('TS-CDS-001-V1', 'CDS-2025-001', 1, 'EXECUTED', NULL, 'EVT-CDS-EXEC-001', NULL, '2025-01-20 10:00:00');

-- Trade State 2: Confirmation
INSERT INTO trade_state (trade_state_id, trade_id, version, position_state, closed_state, event_id, before_state_id, as_of)
VALUES ('TS-CDS-001-V2', 'CDS-2025-001', 2, 'CONFIRMED', NULL, 'EVT-CDS-CONF-001', 'TS-CDS-001-V1', '2025-01-20 15:30:00');

-- CDM Outputs for CDS
INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('BusinessEvent', 'CDS-2025-001', 'EVT-CDS-EXEC-001', 'TS-CDS-001-V1', '5.0.0', '{
  "businessEvent": {
    "intent": "Execution",
    "effectiveDate": "2025-01-20",
    "eventDate": "2025-01-20"
  }
}');

INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('TradeState', 'CDS-2025-001', 'EVT-CDS-EXEC-001', 'TS-CDS-001-V1', '5.0.0', '{
  "tradeState": {
    "trade": {
      "tradeIdentifier": [{"assignedIdentifier": [{"identifier": "CDS-2025-001"}]}],
      "product": {
        "contractualProduct": {
          "economicTerms": {
            "payout": [{
              "creditDefaultPayout": {
                "generalTerms": {
                  "referenceInformation": {
                    "referenceEntity": {"entityName": "Acme Corporation"}
                  }
                },
                "protectionTerms": [{
                  "notionalAmount": {"value": 5000000, "currency": "USD"}
                }]
              }
            }]
          }
        }
      },
      "party": [
        {"partyId": [{"identifier": "HEDGE-FUND-A"}], "name": "Hedge Fund Alpha"},
        {"partyId": [{"identifier": "BANK-DEF"}], "name": "Bank DEF"}
      ]
    },
    "state": {"positionState": "EXECUTED"}
  }
}');

INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('BusinessEvent', 'CDS-2025-001', 'EVT-CDS-CONF-001', 'TS-CDS-001-V2', '5.0.0', '{
  "businessEvent": {
    "intent": "ContractFormation",
    "effectiveDate": "2025-01-20",
    "eventDate": "2025-01-20"
  }
}');

INSERT INTO cdm_outputs (object_type, trade_id, event_id, trade_state_id, schema_version, payload_json)
VALUES ('TradeState', 'CDS-2025-001', 'EVT-CDS-CONF-001', 'TS-CDS-001-V2', '5.0.0', '{
  "tradeState": {
    "trade": {
      "tradeIdentifier": [{"assignedIdentifier": [{"identifier": "CDS-2025-001"}]}],
      "product": {
        "contractualProduct": {
          "economicTerms": {
            "payout": [{
              "creditDefaultPayout": {
                "generalTerms": {
                  "referenceInformation": {
                    "referenceEntity": {"entityName": "Acme Corporation"}
                  }
                },
                "protectionTerms": [{
                  "notionalAmount": {"value": 5000000, "currency": "USD"}
                }]
              }
            }]
          }
        }
      }
    },
    "state": {"positionState": "CONFIRMED"}
  }
}');
```

---

## DATABASE ACCESS LAYER

Create a Python module `common/db.py` with these functions:

```python
"""
Database connection utilities
Adapt this for your specific database (SQL Server, Oracle, MySQL, etc.)
"""
import os
from typing import List, Dict, Any, Optional

def conn():
    """
    Create database connection with dict-like row results.
    Returns a connection object.
    
    Environment variables:
    - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    """
    pass  # Implement for your database

def q(cnx, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
    """
    Execute query returning list of dicts.
    Example: q(cnx, "SELECT * FROM trade_state WHERE trade_id = %s", ("IRS-2025-001",))
    """
    pass  # Implement for your database

def one(cnx, sql: str, params: tuple = None) -> Optional[Dict[str, Any]]:
    """
    Execute query returning single dict or None.
    Example: one(cnx, "SELECT * FROM trade_state WHERE trade_state_id = %s", ("TS-IRS-001-V1",))
    """
    pass  # Implement for your database

def execute(cnx, sql: str, params: tuple = None) -> int:
    """
    Execute statement that does not return rows. Returns affected row count.
    Example: execute(cnx, "DELETE FROM narrative_cache WHERE trade_id = %s", ("IRS-2025-001",))
    """
    pass  # Implement for your database
```

---

## QUERY PATTERNS USED BY THE APPLICATION

```sql
-- Get all states for a trade (ordered by version)
SELECT trade_state_id, trade_id, version, position_state, closed_state, event_id, before_state_id, as_of
FROM trade_state 
WHERE trade_id = ? 
ORDER BY version ASC;

-- Get lineage (find states that come after this one)
SELECT trade_state_id 
FROM trade_state 
WHERE before_state_id = ?;

-- Get BusinessEvent payload
SELECT payload_json 
FROM cdm_outputs
WHERE object_type = 'BusinessEvent' AND event_id = ?
ORDER BY created_at DESC 
LIMIT 1;

-- Get TradeState payload
SELECT payload_json 
FROM cdm_outputs
WHERE object_type = 'TradeState' AND trade_state_id = ?
ORDER BY created_at DESC 
LIMIT 1;

-- Check narrative cache
SELECT narrative_text, generation_metadata 
FROM narrative_cache 
WHERE cache_key = ?;

-- Save narrative
INSERT INTO narrative_cache (cache_key, narrative_type, trade_id, event_id, narrative_text, generation_metadata, version_hash)
VALUES (?, ?, ?, ?, ?, ?, ?);

-- Get narrative logs for replay
SELECT log_type, message, metadata, timestamp 
FROM narrative_logs 
WHERE cache_key = ? 
ORDER BY log_index ASC;
```

---

## NOTES FOR YOUR DATABASE

1. **JSON Columns**: The `payload_json`, `generation_metadata`, and `metadata` columns store JSON. Use your database's JSON type (JSONB for PostgreSQL, JSON for MySQL, NVARCHAR(MAX) for SQL Server with JSON functions).

2. **Auto-increment**: Adapt `AUTO_INCREMENT` syntax for your database (IDENTITY for SQL Server, SEQUENCE for Oracle).

3. **Timestamps**: Use your database's timestamp/datetime type with appropriate defaults.

4. **Parameter Placeholders**: The application uses `%s` placeholders (psycopg2 style). Adapt to your database:
   - SQL Server: `?` or `@param`
   - Oracle: `:param`
   - MySQL: `%s`

5. **Indexes**: Create indexes on frequently queried columns (trade_id, event_id, cache_key).

---

## VERIFICATION QUERIES

After setup, verify with these queries:

```sql
-- Count trades
SELECT trade_id, COUNT(*) as state_count 
FROM trade_state 
GROUP BY trade_id;

-- Expected: IRS-2025-001 (4), CDS-2025-001 (2)

-- Verify lineage chain
SELECT ts.trade_state_id, ts.version, ts.before_state_id, ts.position_state
FROM trade_state ts
WHERE ts.trade_id = 'IRS-2025-001'
ORDER BY ts.version;

-- Verify CDM payloads exist
SELECT object_type, trade_id, COUNT(*) 
FROM cdm_outputs 
GROUP BY object_type, trade_id;

-- Expected: BusinessEvent/TradeState pairs for each state
```


