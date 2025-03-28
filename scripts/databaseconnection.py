from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://rucorbach:PIL1G4@piproyect.anlag1u.mongodb.net/?retryWrites=true&w=majority&appName=PIProyect"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    print (client.get_database("UnderSoundsData").list_collection_names())
except Exception as e:
    print(e)