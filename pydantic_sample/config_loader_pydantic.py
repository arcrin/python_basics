from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# --- Define the Nested Settings Model ---
class LogSettings(BaseSettings):
    # Configure Pydantic to look for environment variables prefixed with "LOG_"
    # for this specific nested model.
    model_config = SettingsConfigDict(
        env_file='my_app.env',  # Name of your .env file
        env_prefix='LOG_',  
        case_sensitive=False,
        extra='ignore'  
    )
    
    level: str
    file_path: Optional[str] = None
    formatter: str = "Simple"


class SimpleAppSettings(BaseSettings):
    # Configure Pydantic to load from .env file and environment variables
    model_config = SettingsConfigDict(
        env_file='my_app.env', # Name of your .env file
        env_file_encoding='utf-8',
        case_sensitive=False,       # Environment variable matching is case-insensitive
        extra='ignore'              # Ignore extra environment variables not defined in the model
    )

    # Define your settings fields
    app_title: str    # This will be loaded from APP_TITLE in .env or environment
    api_key: str      # Loaded from API_KEY
    port: int = 8000  # Default value if PORT is not found
    debug_enabled: bool = False # Default value
    
    # Nested the Logsettings model.
    # Pydantic will automatically instantiate and populate this.
    log: LogSettings = LogSettings()

# --- Load and print settings ---
try:
    settings = SimpleAppSettings()

    print("--- Settings Loaded Successfully ---")
    print(f"Application Title: {settings.app_title}")
    print(f"API Key: {'*' * len(settings.api_key) if settings.api_key else 'Not Set'}")
    print(f"Port: {settings.port}")
    print(f"Debug Mode: {settings.debug_enabled}")

    print("\n--- Nested Log Settings ---")
    print(f"Log Level: {settings.log.level}")
    print(f"Log File Path: {settings.log.file_path}")
    print(f"Log Formatter: {settings.log.formatter}")
    print(f"Type of settings.log: {type(settings.log)}")


except Exception as e:
    print(f"\n*** ERROR: Failed to load settings. ***")
    print(f"Error details: {e}")
    if hasattr(e, 'errors'):
        print("Pydantic errors:", e.errors())