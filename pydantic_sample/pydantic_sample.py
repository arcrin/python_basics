# type: ignore
from pydantic import BaseModel, ValidationError
from  typing import List, Optional

class Item(BaseModel):
    model_config = {
        "strict": True,  # Enable strict mode to enforce type checking
    }
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tags: List[str] = []


# Example of valid data
data_valid = {
    "id": 123,
    "name": "Example Item",
    "price": 19.99,
    "tags": ["electronics", "gadget"]
}

item_valid = Item(**data_valid)
print(item_valid.model_dump_json(indent=2))
# {
#   "id": 123,
#   "name": "Example Item",
#   "description": null,
#   "price": 19.99,
#   "tags": [
#     "electronics",
#     "gadget"
#   ]
# }

# Example of invalid data
data_invalid = {
    "id": "123",
    "name": "Another Item",
    "price": "19.99",
}

try:
    item_invalid = Item(**data_invalid)
    print(item_invalid.model_dump_json(indent=2))
except ValidationError as e:
    print(e)