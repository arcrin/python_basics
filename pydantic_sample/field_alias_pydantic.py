from pydantic import BaseModel, Field, ValidationError


class UserProfile(BaseModel):
    user_id: int = Field(alias="userID") # Maps "userID" from  input to user_id
    full_name: str = Field(alias="fullName")    
    email_address: str = Field(alias="emailAddress")    
    date_of_birth: str = Field(alias="dateOfBirth") # Assuming string for simplicity here
    company_name: str = Field(alias="company-name") # Alias with a hyphen

    # For Pydantic V2, to allow initialization by either alias or field name:
    model_config = {
        "populate_by_name": True
    }
    # In Pydantic V1, this behavior (population by field name even if alias exists)
    # was more the default, ror you could use Config.allow_population_by_field_name = True

    # --- Valid Data with Aliased keys ---
print("--- VALID DATA (using aliases) ---")
user_data_aliased = {
    "userID": 1001,
    "fullName": "Alice Wonderland",
    "emailAddress": "alice@example.com",
    "dateOfBirth": "1995-07-15",
    "company-name": "Mad Hatter Inc."         
}

try:
    profile1 = UserProfile(**user_data_aliased)
    print("Profile 1 (parsed from aliased data):")    
    print(f"    User ID: {profile1.user_id}")
    print(f"    Full Name: {profile1.full_name}")
    print(f"    Company: {profile1.company_name}")

    print("\nSerialized Profile 1 (using field names by default):")
    print(profile1.model_dump_json(indent=2))

    print("\nSerialized Profile 1 (using aliases for output):")
    print(profile1.model_dump_json(indent=2, by_alias=True))

except ValidationError as e:
    print("Error creating Profile 1")
    print(e.json(indent=2))
    

 # --- Valid Data with Python Attribute Names (if populate_by_name=True) ---
print("\n--- VALID DATA (using Python attribute names, populate_by_name=True) ---")
user_data_python_names = {
    "user_id": 1002,
    "full_name": "Bob The Builder",
    "email_address": "bob@example.com",
    "date_of_birth": "1980-01-01",
    "company_name": "FixIt Felix Jr. LLC" # Python attribute name
}

try:
    profile2 = UserProfile(**user_data_python_names)
    print("Profile 2 (parsed from Python attribute names):")
    print(f"  User ID: {profile2.user_id}")
    print(f"  Full Name: {profile2.full_name}")
    print(f"  Company: {profile2.company_name}") # Still accesses via python name
    
    print("\nSerialized Profile 2 (using aliases for output):")
    print(profile2.model_dump_json(indent=2, by_alias=True))
except ValidationError as e:
    print("Error creating Profile 2:")
    print(e.json(indent=2))   


# --- Invalid Data (missing a required aliased field) ---
print("\n--- INVALID DATA (missing required aliased field) ---")
user_data_missing = {
    "userID": 1003,
    # "fullName" is missing
    "emailAddress": "charlie@example.com",
    "dateOfBirth": "2000-12-25"
}

try:
    profile3 = UserProfile(**user_data_missing)
    print("\nProfile 3 (should not print):")
except ValidationError as e:
    print("\nValidation Errors for Profile 3 (missing fullName):")
    # Error messages will refer to the Python attribute name ('full_name')
    # but Pydantic looks for 'fullName' in the input if populate_by_name is not strictly enforced for input.
    print(e.json(indent=2))