from pydantic import RootModel, Field, ValidationError, validator, model_validator
from typing import List, Set, Any, Annotated


# Using RootModel to validate a list of unique positive integers
class ListOfUniquePositiveInts(RootModel[List[int]]):
    # The type hint List[int] is applied  to the root of the data

    # You can add validators to the RootModel that operate on the root value
    # For example, using Field for constraints on the items (if Pydantic supports it directly on root items)
    # Or more commonly, you'd use a custom validator for the root if needed.
    # For simple item constraints, Pydantic often handles it if the type hint is specific.
    # Let's make this more explicit with a vavlidator for uniqueness and positivity.

    @validator('root', pre=True, each_item=False) # 'root' refers to the entire list
    def validate_list_contents(cls, v: List[Any]) -> List[int]:
        if not isinstance(v, list):
            raise TypeError("Input must be a list")

        validated_numbers: List[int] = []
        seen_numbers: Set[int] = set()

        for i, item in enumerate(v):
            try:
                num = int(item) # Coerce to int
            except (ValueError, TypeError):
                raise ValueError(f"Item at index {i} ('{item}') is not a valid integer")
            
            if num <= 0:
                raise ValueError(f"Item at index {i} ('{item}') must be a positive integer")
            
            if num in seen_numbers:
                raise ValueError(f"Item at index {i} ('{item}') is not unique")
            validated_numbers.append(num)
            seen_numbers.add(num)
        return validated_numbers
    
 # --- Valid Data ---
# print("--- VALID LIST DATA ---")
# data1 = [1, 2, "3", 4, 5] # "3" will be coerced
# try:
#     valid_list = ListOfUniquePositiveInts(data1)
#     print(f"Validated list 1: {valid_list.root}") # Access data via .root
#     print(f"Type of valid_list.root[2]: {type(valid_list.root[2])}")
#     print(valid_list.model_dump_json(indent=2)) # Serialization
# except ValidationError as e:
#     print("Error validating list 1:")
#     print(e.json(indent=2))


 # --- Invalid Data (non-positive) ---
# print("\n--- INVALID LIST DATA (non-positive) ---")
# data2 = [1, 2, 0, 4]
# try:
#     invalid_list1 = ListOfUniquePositiveInts(data2)
#     print(invalid_list1.root)
# except ValidationError as e:
#     print("Error validating list 2:")
#     print(e.json(indent=2))   

# --- Invalid Data (not unique) ---
# print("\n--- INVALID LIST DATA (not unique) ---")
# data3 = [1, 2, 3, 2, 4]
# try:
#     invalid_list2 = ListOfUniquePositiveInts(data3)
#     print(invalid_list2.root)
# except ValidationError as e:
#     print("Error validating list 3:")
#     print(e.json(indent=2))

# --- Invalid Data (not a list) ---
# print("\n--- INVALID LIST DATA (not a list) ---")
# data4 = {"numbers": [1,2,3]} # This is a dict, not a list at the root
# try:
#     invalid_list3 = ListOfUniquePositiveInts(data4)
#     print(invalid_list3.root)
# except ValidationError as e:
#     print("Error validating list 4:")
#     print(e.json(indent=2))

# --- Using Field for item constraints (simpler for some cases) ---
# This example shows an alternative if you just want to constrain items in a list.
# However, uniqueness would still need a root validator.
class ListOfPositiveIntsSimple(RootModel[List[Annotated[int, Field(gt=0)]]]):
    model_config = {
        'strict': True,  # Enable strict mode for stricter type checking
    }
    pass

print("\n--- SIMPLE POSITIVE INT LIST ---")
data5 = [1, 10, 5] # "5" coerced, all positive
try:
    valid_list_simple = ListOfPositiveIntsSimple(data5)
    print(f"Simple validated list: {valid_list_simple.root}")
except ValidationError as e:
    print(e.json(indent=2))

data6 = [1, 2, 3]
try:
    ListOfPositiveIntsSimple(data6)
    print(f"\nSimple validated list with positive integers: {data6}")
except ValidationError as e:
    print(f"\nError for simple list with negative: \n{e.json(indent=2)}")