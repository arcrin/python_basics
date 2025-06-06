from pydantic import BaseModel, ValidationError
from typing import List, Optional
from datetime import datetime, date

class User(BaseModel):
    model_config = {
        "strict": True,  # Enable strict mode to enforce type checking
    }
    id: int
    username: str
    signup_ts: Optional[datetime] = None
    join_date: Optional[date] = None
    friends: List[int]  # Do not provide a default value if the field is required 
    is_active: bool = True
    

# --- Valid Data Examples ---
print("--- VALID DATA ---")
data1 = {
    "id": 123,
    "username": "john_doe",
    "join_date": date(2023, 10, 1),  
    "friends": [1, 2, 3],     
    "is_active": False
}

try:
    user1 = User(**data1)
    print("User 1 (coerced data):")
    print(user1.model_dump_json(indent=2))
    print(f"Type of user1.join_date: {type(user1.join_date)}")
    print(f"Type of user1.friends[2]: {type(user1.friends[2])}")
    print(f"Type of user1.is_active: {type(user1.is_active)}")
except ValidationError as e:
    print("Error creating User 1")
    print(e)

print("\nUser 2 (minimal data, using defaults):")
data2 = {"id": 456, "username": "jane_doe"}
try:
    user2 = User(**data2)
    print(user2.model_dump_json(indent=2))
except ValidationError as e:
    print("Error creating User 2")
    print(e)
    
# --- Invalid Data Examples ---
print("\n--- INVALID DATA ---")
invalid_data = {
    "id": "not_an_int",  # Invalid type
    "username": "invalid_user",
    "friends": [1, 2, "three"],  # "three" cannot be coerced to int
}

try:
    user_invalid = User(**invalid_data)
    print("\nInvalid User (should raise error):")
    print(user_invalid.model_dump_json(indent=2))
except ValidationError as e:
    print("Error creating Invalid User")
    print(e)