# type: ignore
from datetime import datetime
import requests
import msgpack


DATETIME_TYPE = 1

def custom_ext_decoder(code, data):
    if code == DATETIME_TYPE:
        # Decode 8-byte binary data to integer timestamp and convert to datetime
        timestamp = int.from_bytes(data, "big")
        return datetime.fromtimestamp(timestamp)
    else:
        # Return unrecognized types as raw ExtType for further handling if needed
        return msgpack.ExtType(code, data)
    
def fetch_data():
    try:
        response = requests.get("http://127.0.0.1:5000/data")

        if response.status_code == 200:
            data = msgpack.unpackb(response.content, ext_hook=custom_ext_decoder, raw=False)
            print("Decoded data:", data)
            print("Decode 'created_at' as Date:", data['created_at'])
        else:
            print("Failed to fetch data:", response.status_code)
    except requests.RequestException as e:
        print("Error fetching data:", e)
        

fetch_data()