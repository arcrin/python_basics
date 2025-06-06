from pydantic import BaseModel, ValidationError
from typing import List, Optional


class Address(BaseModel):
    street: str
    city: str
    postal_code: str
    country: str
    

class MenuItem(BaseModel):
    name: str
    price: float
    description: Optional[str] = ""
    is_vegetarian: bool
    

class Restaurant(BaseModel):
    name: str
    cuisine_type: str
    address: Address
    menu: List[MenuItem]
    phone_number: Optional[str] = ""
    rating: Optional[float] = 0.0 
    

# --- Valid Data with Nested Strutures ---
print("--- VALID NESTED DATA ---")
restaurant_data_valid = {
    "name": "The Gourmet Place",
    "cuisine_type": "Modern European",
    "address": { # This dictionary will be parsed into an Address model
        "street": "123 Main St",
        "city": "Vancouver",
        "postal_code": "V6A 1B3",
        "country": "Canada"  
        # 'country' will use its default "Canada" from the Address model
    },
    "menu": [
        {
            "name": "Truffle Pasta",
            "price": 25.99,
            "description": "Creamy pasta with black truffles",
            "is_vegetarian": False  
        },
        {
            "name": "Garden Salad",
            "price": 12.50,
            "is_vegetarian": True 
        }
    ],
    "rating": 4.5
}

try:
    restaurant1 = Restaurant(**restaurant_data_valid)
    print("Restaurant 1:")
    print(restaurant1.model_dump_json(indent=2))
    print(f"\nRestaurant 1 Address City: {restaurant1.address.city}")
    print(f"\nRestaurant 1 Address Country: {restaurant1.address.country}")
    print(f"Restaurant 1 First Menu Item Name: {restaurant1.menu[0]}")
    print(f"Type of restaurant1.address: {type(restaurant1.address)}")
    print(f"Type of restaurant1.menu[0]: {type(restaurant1.menu[0])}")
except ValidationError as e:
    print("Error creating Restaurant 1")
    print(e.json(indent=2)) 

# --- Invalid Data in a Nested Model ---
print("\n--- INVALID NESTED DATA ---")
restaurant_data_invalid_nested = {
    "name": "The Shaky Joint",
    "cuisine_type": "Fast Food",
    "address": {
        "street_address": "456 Side Rd",
        "city": "Burnaby",
        "postal_code": 12345 # Invalid: postal_code expects a string
    },
    "menu": [
        {
            "name": "Mystery Burger",
            "price": "cheap" # Invalid: price expects a float
        }
    ]
}


try:
    restaurant2 = Restaurant(**restaurant_data_invalid_nested)
    print("\nRestaurant 2 (should not print):")
    print(restaurant2.model_dump_json(indent=2))
except ValidationError as e:
    print("\nValidation Errors for Restaurant 2 (invalid nested data):")
    print(e.json(indent=2)) # .json(indent=2) provides a nicely formatted error output
    # You can also access e.errors() for a list of error dictionaries
    # print("\nError details as list:")
    # print(e.errors())