# type: ignore
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import logging
import time

# Import generated Protobuf classes
import item_pb2

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

@app.websocket("/ws/items/{item_id}")
async def websocket_get_item_protobuf(websocket: WebSocket, item_id: int):
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for item_id: {item_id} from {websocket.client.host}:{websocket.client.port}")
    try:
        # 1. Construct the Protobuf message
        # In a real app, you'd fetch data from a DB or other source
        item_data = item_pb2.Item()
        item_data.item_id = item_id
        item_data.item_name = f"Protobuf Item {item_id}"
        item_data.description = f"This is a description for item {item_id} using Protobuf."
        item_data.price = 49.99 + item_id  # Example price calculation
        item_data.submission_timestamp_utc = int(time.time()) # Current Unix timestamp

        # 2. Serialize the Protobuf message to a byte string
        serialized_item = item_data.SerializeToString()

        # 3. Send the binary date over WebSocket
        await websocket.send_bytes(serialized_item)
        logger.info(f"Sent Protobuf item data (size: {len(serialized_item)}) for item_id: {item_id} to client.")
        
        # Keep the connection open (optional, based on your app's needs)
        while True:
            try:
                # You could handle incoming messages here if needed (e.g., client requests refresh)
                # For this example, we'll just wait for disconnect
                data = await websocket.receive_text()
                logger.info(f"Received text from client for item_id {item_id}: {data}")
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                logger.info(f"Client disconnected for item_id: {item_id}")
                break
            except Exception as e:
                logger.error(f"Error during WebSocket communication for item_id {item_id}: {e}")
            
    except Exception as e:
        logger.error(f"Error processing WebSocket request for item_id {item_id}: {e}")
    finally:
        logger.info(f"WebSocket connection closed for item_id: {item_id}")
        

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")