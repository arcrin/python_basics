from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    BeforeValidator,
    AfterValidator,
    RootModel, # Not strictly needed for this example, but good to know
    model_validator, # Replaces root_validator in Pydantic V2 for model-level checks
)
from typing import Optional, List, Any
from typing_extensions import Annotated
from  decimal import Decimal, InvalidOperation

# --- 1. Define Reusable Validator Functions ---
def strip_whitespace(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value 

def ensure_not_empty_str(value:str) -> str:
    if not value:
        raise ValueError('String must not be empty')
    return value

def convert_to_decimal_if_str(value: Any) -> Decimal:
    """Convert string or float to Decimal, ensuring precision."""
    if isinstance(value, str):
        try:
            return Decimal(value)
        except InvalidOperation:
            raise ValueError("Invalid decimal string")
    elif isinstance(value, (int, float)):
        return Decimal(str(value))
    elif isinstance(value, Decimal):
        return value
    raise TypeError("Price must be a string, number, or Decimal")

def ensure_positive_decimal(value: Decimal) -> Decimal:
    if value <= Decimal('0'):
        raise ValueError("Value must be positive")
    return value

# --- 2. Annotated Types for Reusable Field Validation ---

StrippedNotEmptyString = Annotated[
    str,
    BeforeValidator(strip_whitespace),  
    AfterValidator(ensure_not_empty_str)
]

PositiveDecimal = Annotated[
    Decimal,
    BeforeValidator(convert_to_decimal_if_str),
    AfterValidator(ensure_positive_decimal)
]

PositiveInt = Annotated[
    int,
    Field(gt=0)  # Greater than zero
]

# --- 3. Define the Nested Model (OrderItem) ---
class OrderItem(BaseModel):
    item_sku: StrippedNotEmptyString = Field(max_length=20)
    item_name: StrippedNotEmptyString = Field(max_length=100)
    quantity: PositiveInt
    unit_price: PositiveDecimal

    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.unit_price 
    

# --- 4. Define the Parent Model (Order) ---
class Order(BaseModel):
    order_id: StrippedNotEmptyString
    customer_name: StrippedNotEmptyString
    items: List[OrderItem] = Field(min_length=1)  
    shipping_cost: PositiveDecimal = Field(default=Decimal('0.00'))
    
    # Pydantic V2 model_validator (replaces root_validator)
    # 'before' mode runs before individual field/item validation
    # 'after' mode runs after individual field/item validation
    @model_validator(mode='after') 
    def check_minimum_order_value_and_item_count(self) -> 'Order':
        # 'self' here is the model instance *after* its fields and nested models
        # (like items) have been validated and constructed.
        if not self.items: # Should be caught by Field(min_length=1) on items, but good for illustration
            raise ValueError("Order must contain at least one item.")
        
        total_order_value = sum(item.total_price for item in self.items)

        min_value_for_free_shipping = Decimal('50.00')

        if total_order_value < Decimal('10.00'):
            raise ValueError(f"Order total value must be at least $10.00. Current: ${total_order_value:.2f}")

        # Example of modifying a field based on other validated fields
        if total_order_value >= min_value_for_free_shipping and self.shipping_cost > Decimal('0.00'):
           print(f"Order qualifies for free shipping (total: ${total_order_value:.2f}), setting shipping cost to $0.00")
           self.shipping_cost = Decimal('0.00')
        return self 

   # --- Test Cases ---
   
print("--- VALID ORDER ---")
valid_order_data = {
    "order_id": "ORD12345",
    "customer_name": "Alice Wonderland",
    "items": [
        {
            "item_sku": "BOOK-001",
            "item_name": "  Advanced Pydantic V2  ", # Will be stripped
            "quantity": 2,
            "unit_price": "29.99" # String will be converted to Decimal
        },
        {
            "item_sku": "GADGET-007",
            "item_name": "Universal Translator",
            "quantity": 1,
            "unit_price": 199.50 # Float will be converted to Decimal
        }
    ],
    "shipping_cost": "5.00" # Will become $0.00 due to total order value
}

try:
    order1 = Order(**valid_order_data)
    print("Order 1 (Valid):")
    print(order1.model_dump_json(indent=2))
    print(f"Order 1 Item 0 Name: '{order1.items[0].item_name}'") # Check normalization
    print(f"Order 1 Item 0 Total Price: {order1.items[0].total_price}")
    print(f"Order 1 Shipping Cost (after root validation): {order1.shipping_cost}")
except ValidationError as e:
    print("Error creating Order 1:")
    print(e.json(indent=2))