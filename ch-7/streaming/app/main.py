from contextlib import asynccontextmanager
from fastapi import (
    FastAPI, Body, Depends, status, HTTPException
)
from fastapi.encoders import ENCODERS_BY_TYPE
from bson import ObjectId

from app.db import ping_mongo_db_server
from app.models import mongo_database

# This will ensure objectIds are encoded & returned as strings
ENCODERS_BY_TYPE[ObjectId] = str

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ping_mongo_db_server()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/song")
async def add_song(song: dict = Body(
        example={
            "title": "Song 1",
            "artist": "Artist 1",
            "genre": "Genre 1"
        }
    ),
    db=Depends(mongo_database),
):
    inserted_song = await db.songs.insert_one(song)
    return {
        'id': str(inserted_song.inserted_id),
        'message': 'Song added successfully'
    }

@app.get("/song/{song_id}")
async def get_song(
        song_id: str,
        db=Depends(mongo_database),
    ):
    song = await db.songs.find_one(
        {
            "_id": ObjectId(song_id)
            if ObjectId.is_valid(song_id) else None
        }
    )
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    return song

@app.put("/song/{song_id}")
async def update_song(
        song_id: str,
        updated_song: dict,
        db=Depends(mongo_database),
    ):
    result = await db.songs.update_one(
        {
            "_id": ObjectId(song_id)
            if ObjectId.is_valid(song_id) else None
        },
        {"$set": updated_song}
    )
    if not result.modified_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    return {
        'message': 'Song updated successfully'
    }



@app.delete("/song/{song_id}")
async def delete_song(
        song_id: str,
        db=Depends(mongo_database),
    ):
    result = await db.songs.delete_one(
        {
            "_id": ObjectId(song_id)
            if ObjectId.is_valid(song_id) else None
        }
    )
    if not result.deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    return {
        'message': 'Song deleted successfully'
    }