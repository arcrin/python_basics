# backend.py
# type: ignore
from flask import Flask, Response
import msgpack
from datetime import datetime

app = Flask(__name__)

# Define a custom type code for datetime
DATETIME_TYPE = 1

def custom_ext_decoder(code, data):
    if code == DATETIME_TYPE:
        timestamp = int.from_bytes(data, "big")
        return datetime.fromtimestamp(timestamp) 
    else:
        return msgpack.ExtType(code, data)

def custom_ext_encoder(obj):
    if isinstance(obj, datetime):
        timestamp = int(obj.timestamp())
        return msgpack.ExtType(DATETIME_TYPE, timestamp.to_bytes(8, 'big'))
    else:  
        raise TypeError(f"Unsupported type: {type(obj)}")

@app.route('/data')
def get_data():
    # Example data with datetime
    data = {
        "name": "Alice",
        "age": 30,
        "active": True,
        "created_at": datetime.now()
    }
    
    # Serialize data with datetime to MessagePack format
    packed_data = msgpack.packb(data, default=custom_ext_encoder)
    print("Serialized packed_data: ", packed_data)
    
    # Return the MessagePack data as a binary response
    return Response(packed_data, content_type='application/x-msgpack')


if __name__ == '__main__':
    print("test")
    app.run(port=5000)
