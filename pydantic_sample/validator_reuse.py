from pydantic import BaseModel, Field, ValidationError, BeforeValidator, AfterValidator
from typing import Optional, List, Any
from typing_extensions import Annotated

# --- 1. Define reusable validator functions ---

def strip_whitespace(value: Any) -> Any:
    """
    If the value is a string, strip leading/trailing whitespace.
    Otherwise, return it as is (Pydantic's type validation will handle non-strings).


    Args:
        value (Any): The value to be validated. 

    Returns:
        Any: The stripped value if it is a string, otherwise the original value. 
    """
    if isinstance(value, str):
        return value.strip()
    return value

def ensure_not_empty(value: str) -> str:
    """
    Ensure a string is not empty after potential stripping.
    Assume 'value' is already a string.

    """
    if not value: # Check for empty string
        raise ValueError('must not be empty or just whitespace')
    return value

# ---  2. Create Annotated types using these validators ---

# This Annotated type will first strip whitespace, then ensure the string is not empty.
# Length constraints will be added via Field.
NotEmptyStrippedString = Annotated[
    str, 
    BeforeValidator(strip_whitespace),  # Run this before other Pydantic validation for 'str'
    AfterValidator(ensure_not_empty),   # Run this after Pydantic's str validation & strip_whitespace
]


class ProductReview(BaseModel):
    review_id: int
    product_sku: str
    reviewer_name: NotEmptyStrippedString = Field(min_length=2, max_length=50)
    comment_title: NotEmptyStrippedString = Field(min_length=5, max_length=100)
    comment_body: Optional[NotEmptyStrippedString] = Field(
        default=None, min_length=10, max_length=500
    )
    # Note: For Optional fields, the NotEmptyStrippedString validators and Field constraints 
    # will only apply if a non-None value is provided.

class UserFeedback(BaseModel):
    feedback_id: int
    username: NotEmptyStrippedString = Field(min_length=3, max_length=30)
    subject: NotEmptyStrippedString = Field(min_length=5, max_length=150)
    message: NotEmptyStrippedString = Field(min_length=1, max_length=1000)


# # --- Valid Data Examples ---
# print("--- VALID DATA---")
# review_data_valid = {
#     "review_id": 1,
#     "product_sku": "SKU123",
#     "reviewer_name": "  John Doe  ",  # Will be stripped and validated
#     "comment_title": "Excellent Product!",
#     "comment_body": "This product exceeded all my expectations. Highly recommended for everyone!"
# }
# try:
#     review1 = ProductReview(**review_data_valid)
#     print("Review 1 (Valid):")
#     print(review1.model_dump_json(indent=2))
#     assert review1.reviewer_name == "John Doe"  # Check stripping    
# except ValidationError as e:
#     print("Error creating Review 1:")
#     print(e.json(indent=2))

# feedback_data_valid = {
#     "feedback_id": 101,
#     "username": "feedback_user",
#     "subject": "Website Suggestion",
#     "message": "The website is great, but I have a suggestion."
# }
# try:
#     feedback1 = UserFeedback(**feedback_data_valid)
#     print("\nFeedback 1 (Valid):")
#     print(feedback1.model_dump_json(indent=2))
# except ValidationError as e:
#     print("Error creating Feedback 1:")
#     print(e.json(indent=2)) 

# --- Invalid Data Examples ---
# print("\n--- INVALID DATA ---")
# review_data_invalid_name = {
#     "review_id": 2, "product_sku": "SKU456", "reviewer_name": "J", "comment_title": "Okay"
# }
# try:
#     ProductReview(**review_data_invalid_name)
# except ValidationError as e:
#     print("\nInvalid Review (reviewer_name too short):")
#     # .errors() gives a list of error dictionaries
#     print(e.errors(include_url=False))

# feedback_data_invalid_subject = {
#     "feedback_id": 102, "username": "testuser", "subject": "Hi", "message": "..."
# }
# try:
#     UserFeedback(**feedback_data_invalid_subject)
# except ValidationError as e:
#     print("\nInvalid Feedback (subject too short):")
#     print(e.errors(include_url=False))

# review_data_empty_title = {
#     "review_id": 3, "product_sku": "SKU789", "reviewer_name": "Anonymous", "comment_title": "    "
# }
# try:
#     # This will first be stripped to "", then ensure_not_empty will raise ValueError
#     ProductReview(**review_data_empty_title)
# except ValidationError as e:
#     print("\nInvalid Review (comment_title is empty after stripping):")
#     print(e.errors(include_url=False))

# Example with an optional field being None (which is valid)
# review_data_no_body = {
#     "review_id": 4, 
#     "product_sku": "SKU000",
#     "reviewer_name": "Concise Critic",
#     "comment_title": "Good enough",
#     "comment_body": None # This is allowed
# }
# try:
#     review_no_body = ProductReview(**review_data_no_body)
#     print("\nReview with no comment_body (Valid):")
#     print(review_no_body.model_dump_json(indent=2))
# except ValidationError as e:
#     print("Error creating Review with no comment_body:")
#     print(e.json(indent=2))
    
# Example with an optional field having invalid content
review_data_invalid_body = {
    "review_id": 5, 
    "product_sku": "SKU001",
    "reviewer_name": "Brief Reviewer",
    "comment_title": "Needs Work",
    "comment_body": "Too short" # This will fail min_length for comment_body
}
try:
    ProductReview(**review_data_invalid_body)
except ValidationError as e:
    print("\nInvalid Review (comment_body too short):")
    print(e.errors(include_url=False))