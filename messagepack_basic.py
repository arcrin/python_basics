# type: ignore
from datetime import datetime
from decimal import Decimal
import msgpack


DATETIME_TYPE = 1
DECIMAL_TYPE = 2


def custom_ext_decoder(code, data):
    if code == DATETIME_TYPE:
        # Decode 8-byte binary data to integer timestamp and convert to datetime
        timestamp = int.from_bytes(data, "big")
        return datetime.fromtimestamp(timestamp)
    else:
        # Return unrecognized types as raw ExtType for further handling if needed
        return msgpack.ExtType(code, data)


def custom_ext_encoder(obj):
    if isinstance(obj, datetime):
        # Convert datetime to a Unix timestamp in seconds as 8-byte binary
        timestamp = int(obj.timestamp())
        return msgpack.ExtType(DATETIME_TYPE, timestamp.to_bytes(8, 'big'))
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")
    

data = {
    "name": "Alice",
    "created_at": datetime.now(),
}

# Serialize data with custom encoder
packed_data = msgpack.packb(data, default=custom_ext_encoder)

# Deserialize with custom decoder
data_back = msgpack.unpackb(packed_data, ext_hook=custom_ext_decoder, raw=False)

print("Origianl data", data)
print("Decoded data:", data_back)