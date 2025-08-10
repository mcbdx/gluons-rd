## Models 
## a pydantic model is a python class that inherits from pydantic.BaseModel and defines schema for data validation

from pydantic import BaseModel, Field

class Dog(BaseModel):
    name: str
    age: int = Field(..., ge=0) # ... means this field is required, ge=0 means age must be greater than or equal to 0
    breed: str
    ## Fields are used to add default values, descriptions, and other metadata
    color: str = Field(default="golden", description="The color of the dog", example="brown")

## sample dog instance
kala = Dog(name="Kala", age=3, breed="Golden Retriever")
print(kala)

## JSON and Json Schema
## pydantic models can export data as JSON and generate JSON schema for API docs
print(kala.model_dump_json())  # Convert to JSON string # .json() is deprecated
print(kala.model_json_schema())  # Generate JSON schema # .schema() is deprecated


# Serialization
# pydantic models can be serialized to and from dictionaries
kala_dict = kala.model_dump(exclude="color")  # Convert to dict, excluding the color field
print(kala_dict)

# Deserialization
# You can create a model instance from a dictionary
sample_dict = {
    "name": "Buddy",
    "age": 5,
    "breed": "Labrador",
    "color": "black"
}

new_dog = Dog(**sample_dict)
print(new_dog)

## Types, Union and Aliases 
# pydantic supports standrd and complex types, union for multiple types and alias for field names
from typing import Union, List

class Cat(BaseModel):
    category: Union[str, int]  # category can be either str or int
    age: int
    friends: list[str] = Field(default_factory=list)  # friends is a list of strings
    nickname: str = Field(alias="nick")  # alias for the field name

jacko = Cat(category="siamese", age = 2, friends=["Mittens", "Whiskers"], nick="Jackoroo")
print(jacko)

# Validation
from pydantic import field_validator, ValidationError, AfterValidator
from typing import Annotated

## there are 2 ways to validate fields in pydantic models: Annotated Validations or field_validators

## Annotated Validations

def is_even(value: int) -> int: 
    if value % 2 != 0:
        raise ValueError("Value must be even")
    return value

# there's also before and after validators, but they are not used as often
class Car(BaseModel):
    make: str
    model: str
    year: Annotated[int, AfterValidator(is_even)] # year must be even

try:
    car = Car(make="Toyota", model="Camry", year=2023)  # This will raise a validation error
except ValidationError as e:
    print(e)

# Field Validators - decorator pattern 

class Person(BaseModel):
    name: str
    age: int

    @field_validator("age", mode="after")  # mode can be "before", "after", or "wrap"
    @classmethod
    def validate_age(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Age must be a positive integer")
        return value

try: 
    person = Person(name="Alice", age=-5)  # This will raise a validation error
except ValidationError as e:
    print(e)

# model validators - validate the entire model
from typing_extensions import Self
from pydantic import model_validator

class User(BaseModel):
    username: str
    password: str
    password_confirm: str

    @model_validator(mode="after")
    def check_passwords_match(self: Self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

try:
    user = User(username="john_doe", password="secret123", password_confirm="secret1231")
except ValidationError as e:
    print(e)