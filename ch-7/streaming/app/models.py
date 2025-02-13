from app.db import mongo_client

#define a database called beat_streaming
database = mongo_client.beat_streaming

def mongo_database():
    return database


