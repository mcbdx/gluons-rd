from contract.models import SQLContract, SQLContractType
from typing import get_args
import json

# create contract
def create_contract(contract_data: str) -> SQLContract:
    """Create a SQL contract from JSON string."""
    try:
        data = json.loads(contract_data)
        contract = SQLContract(**data)
        return contract
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}")
    except Exception as e:
        raise ValueError(f"Error creating contract: {e}")

def save_contract(contract: SQLContract, file_path: str) -> None:
    """Save the SQL contract to a database."""
    ## simulating saving to a file for demonstration purposes but in practice this would be a database operation
    if not isinstance(contract, get_args(SQLContractType)):
        raise ValueError("Provided contract is not a valid SQLContract instance.")
    try:
        with open(file_path, 'w') as file:
            file.write(contract.model_dump_json(indent=2))
    except Exception as e:
        raise ValueError(f"Error saving contract to file: {e}")
    
def load_contract(file_path: str) -> SQLContract:
    """ Load contract from database"""
     ## this is simulating a loading from a file for demonstration purposes but in practice this would be a database operation
    try:
        with open(file_path, "r") as file: 
            data = json.load(file)
            contract = SQLContract(**data)
            return contract
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data in file: {e}")
    
def migrate_contract(old_contract: SQLContract) -> SQLContract:
    """ Migrate an old contract to the latest version."""
    model_classes = get_args(get_args(SQLContractType)[0])
    latest_version_class = model_classes[-1]  # Assuming the last class is the latest version
    if isinstance(old_contract, latest_version_class):
        return old_contract
    
    if isinstance(old_contract, model_classes[0]):
        old_data = old_contract.model_dump()  # dumps to dict
        new_data = old_data.copy()
        new_data["version"] = "2.0"
        new_data["description"] = "Migrated from V1"
        new_contract = model_classes[1](**new_data)
        print(f"Migrated contract to version {new_contract.version}")
        return new_contract
        

    # if isinstance(old_contract, SQLContractV1):
    #     # Example migration logic from V1 to V2
    #     new_data = old_contract.model_dump()
    #     new_data["version"] = "2.0"
    #     new_data["description"] = "Migrated from V1"
    #     new_contract = SQLContractV2(**new_data)
    #     return new_contract
    # else:
    #     raise ValueError("Unsupported contract version for migration.")
    
if __name__ == "__main__":
    contract_json = """
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
    """
    
    contract = create_contract(contract_json)
    print("Contract created successfully: \n", contract)
    save_contract(contract, 'contract.json')
    print("Contract saved to 'contract.json'.")
    loaded_contract = load_contract('contract.json')
    print("Contract loaded from 'contract.json': \n", loaded_contract)
    migrated_contract = migrate_contract(loaded_contract)
    print("Migrated Contract: \n", migrated_contract)
    
