# type: ignore
from pymongo import MongoClient

def find_record_by_mac_address(uri, db_name, collection_name, mac_address):
    try:
        client = MongoClient(uri)
        db = client[db_name]
        collection = db[collection_name]
        
        query = {"Unique Info.MAC Address": mac_address}
        record = collection.find_one(query)

        return record
    
    except Exception as e:
        print(f"An exception has occurred: {e}")
        return None
    finally:
        client.close()

if __name__ == "__main__":
    MONGO_URI = "" 
    DB_NAME = ""
    COLLECTION_NAME = ""

    mac_address_to_find = "00:40:AE:14:02:68"

    record = find_record_by_mac_address(MONGO_URI, DB_NAME, COLLECTION_NAME, mac_address_to_find)

    if record:
        print(record['SerialNumber'])
    else:
        print("No matching record found")