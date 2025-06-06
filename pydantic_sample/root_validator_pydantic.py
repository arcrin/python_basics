from __future__ import annotations  # For Python 3.7 compatibility
from pydantic import BaseModel, ValidationError, root_validator, field_validator
from  datetime import datetime
from typing import Optional, Any


class Event(BaseModel):
    event_name: str
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str] = ""
    max_attendees: Optional[int] = 0
    
    # A field validator for individual datetime fields (optional, but good practice)
    @field_validator('start_datetime', 'end_datetime')
    def ensure_datetime_is_not_naive(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            # For symplicity, let's assume UTC if not timezone
            # raise ValueError("Datetime must be timezone-aware")
            pass
        return value
    

    # Root validator to check consistency between start and end datetimes
    # By default (pre=False), this runs AFTER individual field validation
    @root_validator(skip_on_failure=True)
    def check_start_end_dates(cls, values: dict[Any, Any]) -> dict[Any, Any]:
        # 'values' is a dictionary of the field values after individual validation
        # e.g., {'event_name': 'Workshop', 'start_datetime': ..., 'end_datetime': ...}
        
        start_dt, end_dt = values.get('start_datetime'), values.get('end_datetime')
        
        # Ensure both fields are present (they should be, as they are not optional,
        # but good practice in root validators if dealing with optional fields involved in the check)
        if start_dt is None or end_dt is None:
            # This case might not be hit if fields are required and validated individually first,
            # unless skip_on_failure=False and they were initially None.
            return values
        if start_dt >= end_dt:
            raise ValueError("Start datetime must be before end datetime")
        
        # You can also modify values here if needed, e.g.,:
        # if 'location' not in values or values['locations'] is None:
        #     values['location'] = "TBD"

        return values
    

# --- Valid Data Example ---
print("--- VALID EVENT DATA ---")
valid_event_data = {
    "event_name": "Tech Conference 2025",
    "start_datetime": "2025-10-20T09:00:00", # Pydantic will parse to datetime
    "end_datetime": "2025-10-22T17:00:00",
    "location": "Convention Center"
}
try:
    event1 = Event(**valid_event_data)
    print("Event 1 (valid dates):")
    print(event1.model_dump_json(indent=2))
except ValidationError as e:
    print("Error creating Event 1:")
    print(e.json(indent=2))
    

# --- Invalid Data Example (end_datetime before start_datetime) ---
print("\n--- INVALID EVENT DATA (dates) ---")
invalid_event_data_dates = {
    "event_name": "Mismanaged Workshop",
    "start_datetime": "2025-11-05T14:00:00",
    "end_datetime": "2025-11-05T10:00:00", # End is before start
    "location": "Room 101"
}
try:
    event2 = Event(**invalid_event_data_dates)
    print("\nEvent 2 (should not print):")
    print(event2.model_dump_json(indent=2))
except ValidationError as e:
    print("\nValidation Errors for Event 2 (invalid dates):")
    # The error from the root validator will appear as a general model error ('__root__')
    # or associated with specific fields if you modify them and raise.
    # Pydantic v2 aims to improve how root validator errors are attributed.
    print(e.json(indent=2))
    # print(e.errors()) # For a list of dicts
    

# --- Invalid Data Example (individual field validation fails first) ---
print("\n--- INVALID EVENT DATA (field error) ---")
invalid_event_data_field = {
    "event_name": "Broken Event",
    "start_datetime": "This is not a date", # This will fail field validation
    "end_datetime": "2025-11-05T10:00:00"
}
try:
    event3 = Event(**invalid_event_data_field)
    print("\nEvent 3 (should not print):")
    print(event3.model_dump_json(indent=2))
except ValidationError as e:
    print("\nValidation Errors for Event 3 (field error):")
    # The root validator with skip_on_failure=True will not run
    print(e.json(indent=2))