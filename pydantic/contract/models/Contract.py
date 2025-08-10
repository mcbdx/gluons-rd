from typing import Literal, Optional, Union, Annotated, overload
from pydantic import BaseModel, Field, field_validator, ValidationInfo, TypeAdapter, ConfigDict

# Contract Model 

## shared sub-models

### Source Sub-model
class Source(BaseModel):
    table_name: str = Field(..., description="Name of the source table")
    database: str
    incremental: bool = Field(default=False, description="Is the source incremental?")
    incremental_column: Optional[str]

    @field_validator("incremental_column")
    def check_incremental_column(cls, v, info: ValidationInfo):
        incremental = info.data.get("incremental")
        if incremental and not v:
            raise ValueError("incremental_column must be provided if incremental is True")
        if not incremental and v:
            raise ValueError("incremental_column must be None if incremental is False")
        return v
        
### Target Sub-model
class Target(BaseModel):
    target_table_name: str = Field(..., description="Name of the target table")
    target_database: str
    
###  Connection Sub-model
class Connection(BaseModel):
    connection_string: str = Field(..., description="Connection string for the database")
    connection_type: Literal["mysql", "postgresql", "sqlite", "oracle"] = "mysql" # Default to MySQL

### Data Patterns 
class DataPatterns(BaseModel):
    pattern: Literal["append", "overwrite", "merge"] = "overwrite"  # Default to overwrite
    schemaEnforcement: bool

### Contract Model
class SQLContractV1(BaseModel):
    version: Literal["1.0"] = "1.0"
    source: Source
    target: Target
    connection: Connection
    data_patterns: DataPatterns
    trigger: str
    model_config = ConfigDict(extra="forbid") # Prevents extra fields not defined in the model
    
### Contract Model 2 
class SQLContractV2(BaseModel):
    version: Literal["2.0"] = "2.0"
    source: Source
    target: Target
    connection: Connection
    data_patterns: DataPatterns
    trigger: str
    description: Optional[str] = Field(None, description="Optional description of the contract")


# Union of both contract versions
SQLContractType = Annotated[Union[SQLContractV1, SQLContractV2], Field(discriminator="version")]

## factory function to create a contract instance
## the factory method can be used to descriminate between different versions of the contract and create the appropriate model instance

## good option but when versions grow or hand written errors become a problem, and no single place to emit json, better to use a type discriminator with type adapter
# def SQLContract(**data) -> SQLContractType: 
#     """ Factory function to create a SQL contract instance."""
#     version = data.get("version", "1.0")
#     if version == "1.0":
#         return SQLContractV1(**data)
#     elif version == "2.0":
#         return SQLContractV2(**data)
#     else:
#         raise ValueError(f"Unsupported contract version: {version}")

## the type adapter approach is more robust 
## allows for one source of truth, better structured for errors and easy to extend with new versions
## can parse json strings directly into the appropriate model

## type adapter allows us to create a single function that can handle both versions of the contract
## it helps us descriminate between different versions of the contract based on the `version` field
_SQL_ADAPTER = TypeAdapter(SQLContractType)

## overloading allows us to use the same function name with different signatures or types
@overload
def SQLContract(*, version: Literal["1.0"], **data) -> SQLContractV1: ...
## the * means, keyword arguments only after *, this is useful for versioning
@overload
def SQLContract(*, version: Literal["2.0"], **data) -> SQLContractV2: ...


def SQLContract(**data) -> SQLContractType:
    """ Factory function to create a SQL contract instance based on version."""
    if "version" not in data:
        data["version"] = "2.0" # in theory default should be latest version

    # Use the type adapter to validate and parse the data into the appropriate model
    return _SQL_ADAPTER.validate_python(data)

# End of Contract Model


## Example Usage
if __name__ == "__main__":
    # Example of creating a contract instance
    contract = SQLContract(
        version="2.0",
        source=Source(table_name="source_table", database="source_db", incremental=True, incremental_column="updated_at"),
        target=Target(target_table_name="target_table", target_database="target_db"),
        connection=Connection(connection_string="mysql://user:pass@localhost/db", connection_type="mysql"),
        data_patterns=DataPatterns(pattern="merge", schemaEnforcement=True),
        trigger="daily",
        description="This is a sample contract for data processing."  # Optional field for v2
    )

    print(contract.model_dump_json(indent=2))  # Print the contract in JSON format