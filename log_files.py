# type: ignore
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
import msgpack
import zlib
import datetime

client = MongoClient("mongodb://qa-testmongo.network.com:27017/")
db = client["TestMFG_GridFS"]
fs = GridFS(db)

file_metadata = db.fs.files.find_one({"_id": ObjectId("673e424d36f6dae2381b113f")})

file_id = file_metadata["_id"]
grid_out = fs.get(file_id)

raw_data = grid_out.read()

print(raw_data)

try:
    decompressed_data = zlib.decompress(raw_data)
    decoded_data = msgpack.loads(decompressed_data)
    for entry in decoded_data['log_data']:
        print(entry)
except Exception as e:
    print(f"Error decoding log file: {e}")
