# type: ignore
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Initialize a FastAPI app
app = FastAPI()

# --- Pydantic Model Definition (same as before) ---
class Item(BaseModel):
    item_id: int = Field(alias="itemId")
    item_name: str = Field(alias="itemName")
    description: Optional[str] =Field(default=None)
    price: float
    submission_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": [
                {
                    "itemId": 1, 
                    "itemName": "Awesome Gadget via WebSocket",
                    "description": "The best gadget you've ever seen, now over WebSocket!",
                    "price": 99.99,
                    "submission_date": "2023-05-30T12:00:00Z"
                }
            ]
        }
    } 
    
# -- (Optional) CORS Middleware for HTTP if you still have HTTP endpoints ---
# from fastapi.middleware.cors import CORSMiddleware
# origins = [
#     "http://localhost:3000",
#     "http://localhost:5173", # Vite default
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# --- WebSocket Endpoint ---
@app.websocket("/ws/items/{item_id}")
async def websocket_get_item(websocket: WebSocket, item_id: int):
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for item_id: {item_id} from {websocket.client.host}:{websocket.client.port}")
    try:
        # Construct the item data (similar to the HTTP GET endpoint)
        item_data = Item(
            itemId=item_id,
            itemName=f"WS Item {item_id}",
            description="This item was delivered over a WebSocket connection",
            price=29.99 + item_id,
        )
        
        # Serialize the Pydantic model to JSON string
        # Pydantic V2: model_dum_json, PYdantic V1: .json()
        json_data = item_data.model_dump_json(by_alias=True)
        
        # Send the JSOn data to the client
        await websocket.send_text(json_data)
        logger.info(f"Sent item data for item_id: {item_id} to client.")
        
        # Keep the connection open to potentially listen for client messages or send updates
        # For this example, we'll just wait for the client to close or send a message
        while True:
            try:
                # You could add logic here to handle incoming messages if needed
                data = await websocket.receive_text()
                logger.info(f"Received from client for item_id {item_id}: {data}")
                if data == "ping":
                    await websocket.send_text("pong")
                # Add more sophisticated message handling if your app needs it
            except WebSocketDisconnect:
                logger.info(f"Client disconnected for item_id: {item_id}")
                break
            except Exception as e:
                logger.error(f"Error during WebSocket communication for item_id {item_id}: {e}")

    except Exception as e:
        logger.error(f"Error in preparing or sending item data for item_id {item_id}: {e}")
        # Attempt to send an error message before closing if connection is still active
        try:
            await websocket.send_text(f'{{"error": "Failed to process item {item_id}", "details": "{str(e)}"}}')
        except Exception:
            pass # Ignore if sending error fails
        await websocket.close(code=1011) # Internal error
    finally:
        logger.info(f"WebSocket connection closed for item_id: {item_id}")
        
@app.get("/api/items/{item_id}", response_model=Item)
async def get_item_http(item_id: int):
    return Item(
        itemId=item_id,
        itemName=f"HTTP Item {item_id}",
        description="This item was delivered over an HTTP GET request",
        price=19.99 + item_id,
    )
        