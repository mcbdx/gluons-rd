# Contracts
This directory contains the contract definitions and related services for the application.

# Models
The models are defined in `pydantic/contract/models/Contract.py` and represent the structure of the contracts.

Sample contract: 
```json
{
  "version": "1.0",
  "source": {
    "table_name": "source_table",
    "database": "source_db",
    "incremental": true,
    "incremental_column": "updated_at"
  },
  "target": {
    "target_table_name": "target_table",
    "target_database": "target_db"
  },
  "connection": {
    "connection_string": "mysql://user:pass@localhost/db",
    "connection_type": "mysql"
  },
  "data_patterns": {
    "pattern": "merge",
    "schemaEnforcement": true
  },
  "trigger": "daily"
}
```

The idea of this contract is to define how data should be moved from a source to a target, including connection details and data patterns. However, this is just a sample and can be extended or modified as needed. The idea was to explore how to use Pydantic for contract management and versioning as well as to provide a clear structure for data movement operations.

# Services
The `ContractManager` service in `pydantic/contract/services/contract_manager.py` is responsible for managing contract versions and migrations. It provides methods to create, load, validate, and migrate contracts. 

