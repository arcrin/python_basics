from pydantic import BaseModel, Field, ValidationError, BeforeValidator, AfterValidator
from typing import Optional, List, Any
from typing_extensions import Annotated

# --- 1. Define Reusable Validator Functions ---

# For 'name' validation and normalization
def strip_whitespace_modifier(value: Any) -> Any:
    """If the value is a string, strip leading/trailin whitespace."""
    if isinstance(value, str):
        return value.strip()
    return value # Pass through other types for Pydantic's core validation

def ensure_name_is_not_empty_after_strip(value: str) -> str:
    """Ensures a string (assumed to be already stripped) is not empty."""
    print(f"Validating name: '{value}'")  # Debug print to see the value being validated
    if not value: # Check for empty string after stripping
        raise ValueError('Name must not be empty or just whitespace')
    return value

def title_case_modifier(value: str) -> str:
    """Converts a string to title case."""
    print(f"Converting name to title case: '{value}'")  # Debug print to see the value being modified
    return value.title()

# For 'sku' validation and normalization
def uppercase_modifier(value: Any) -> Any:
    """If the value is a string, convert to uppercase."""
    if isinstance(value, str):
        return value.upper()
    return value  

def validate_sku_format_after_uppercase(value: str) -> str:
    """Validates the format of an uppercased SKU string."""
    parts = value.split('-')
    if not (2 <= len(parts) <= 3):
        raise ValueError("SKU must have 2 or 3 parts separated by hyphens")
    if not parts[0].isalpha() or not len(parts[0]) == 3: 
        raise ValueError("First part of SKU must be 3 alphabetic characters")
    if not parts[1].isdigit() or not (1 <= len(parts[1]) <= 5):
        raise ValueError("Second part of SKU must be 1 to 5 digits")
    if len(parts) == 3 and (not parts[2].isdigit() or not len(parts[2]) ==2):
        raise ValueError('This part of SKU (if present) must be 2 digits')
    return value


# --- 2. Create Annotated Types for Reusability ---

# For 'name':
# 1. Strip whitespace (Before Pydantic's main 'str' validation)
# 2. Ensure it's not empty (After Pydantic's 'str' validation and stripping)
# 3. Convert to title case (After all other checks)
# Length constraint will be applied via Field on the model.
ValidatedProductName = Annotated[
    str,
    BeforeValidator(strip_whitespace_modifier),
    AfterValidator(ensure_name_is_not_empty_after_strip),
    AfterValidator(title_case_modifier)
]

# For 'sku':
# 1. Conver to uppercase (Before Pydantic's main 'str' validation)
# 2. Validate the specific SKU format (After Pydantic's 'str' validation and uppercasing)
ValidatedSKU = Annotated[
    str,
    BeforeValidator(uppercase_modifier),
    AfterValidator(validate_sku_format_after_uppercase)
]

# --- 3. Define the Pydantic V2 Product Model ---
class Product(BaseModel):
    model_config = {
        'strict': True,  # Enable strict mode for stricter type checking
    }
    product_id: int
    name: ValidatedProductName = Field(max_length=50)
    sku: ValidatedSKU
    price: float = Field(gt=0)  # Price must be greater than 0
    tags: Optional[List[str]] = Field(default_factory=list) # Correct way for mutable defaults in V2

# --- Test Cases (similar to the V1 example) ---

# --- Valid data Examples ---
print("--- VALID DATA ---")
valid_product_data = {
    "product_id": 101,
    "name": "   ultra soft widget   ", # Will be stripped, checked for emptiness, title-cased, then length checked
    "sku": "wid-00123",          # Will be uppercased, then format checked
    "price": 19.99,
}

try:
    product_instance = Product(**valid_product_data)
    print("\nProduct (Valid):")
    # model_dump_json is the Pydantic V2 equivalent of .json()
    print(product_instance.model_dump_json(indent=2))
    assert product_instance.name == "Ultra Soft Widget" # Check normalization
    assert product_instance.sku == "WID-00123"      # Check normalization
except ValidationError as e:
    print("Error creating Product (Valid):")
    # e.json() is available, e.errors() gives a list of dicts
    print(e.json(indent=2))

 # --- Invalid data Examples ---
print("\n--- INVALID DATA ---")

# print("\nInvalid Name (empty after strip):")
# invalid_name_data = {
#     "product_id": 201, "name": " ", "sku": "TST-00001", "price": 10.00
# }
# try:
#     Product(**invalid_name_data)
# except ValidationError as e:
#     print(e.errors(include_url=False)) # include_url=False for cleaner output

# print("\nInvalid Name (too long):")
# invalid_name_data_long = {
#     "product_id": 202, "name": "This is an extremely long product name that hopefully exceeds the fifty character limit",
#     "sku": "LNG-00002", "price": 20.00
# }
# try:
#     Product(**invalid_name_data_long)
# except ValidationError as e:
#     print(e.errors(include_url=False))

# print("\nInvalid SKU format (wrong parts):")
# invalid_sku_data = {
#     "product_id": 203, "name": "Test Product", "sku": "AB-123456", "price": 30.00
# }
# try:
#     Product(**invalid_sku_data)
# except ValidationError as e:
#     print(e.errors(include_url=False))

# print("\nInvalid SKU format (non-alpha first part):")
# invalid_sku_data_2 = {
#     "product_id": 204, "name": "Test Product 2", "sku": "123-12345", "price": 40.00
# }
# try:
#     Product(**invalid_sku_data_2)
# except ValidationError as e:
#     print(e.errors(include_url=False))

print("\nInvalid Price (zero):")
invalid_price_data = {
    "product_id": 205, "name": "Freebie", "sku": "FRE-00000", "price": 0
}
try:
    Product(**invalid_price_data)
except ValidationError as e:
    print(e.errors(include_url=False))   