import logging
from contextlib import asynccontextmanager
from fastapi import (
    FastAPI, Body, Depends, status, HTTPException
)
from fastapi.encoders import ENCODERS_BY_TYPE
from bson import ObjectId

from app.db import ping_mongo_db_server
from app.models import mongo_database
from app.schemas import PlayList

logger = logging.getLogger("uvicorn.error")
# This will ensure objectIds are encoded & returned as strings
ENCODERS_BY_TYPE[ObjectId] = str

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ping_mongo_db_server()
    db = mongo_database()
    logger.info("Creating songs index. -1 means descending order")
    await db.songs.create_index({"album.release_year": -1})
    await db.songs.create_index({"artist": "text"})
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
    inserted_song = await db.songs.insert_one(song.model_dump())
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

@app.post("/playlist")
async def create_playlist(
        playlist: PlayList = Body(
            example={
                "name": "Favorite Songs",
                "songs": ["Song 1", "Song 2"]
            }
        ),
        db=Depends(mongo_database),
    ):
    result = await db.playlists.insert_one(playlist.model_dump())
    return {
        'id': str(result.inserted_id),
        'message': 'Playlist created successfully'
    }

@app.get("/playlist/{playlist_id}")
async def get_playlist(
        playlist_id: str,
        db=Depends(mongo_database),
    ):
    playlist = await db.playlists.find_one(
        {
            "_id": ObjectId(playlist_id)
            if ObjectId.is_valid(playlist_id) else None
        }
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    songs = await db.songs.find(
        {
            "_id": {
                "$in": [
                    ObjectId(song_id)
                    if ObjectId.is_valid(song_id) else None
                    for song_id in playlist["songs"]
                ]
            }
        }
    ).to_list(None)
    
    return {
        "name": playlist["name"],
        "songs": songs
    }

@app.put("/playlist/{playlist_id}")
async def update_playlist(
        playlist_id: str,
        updated_playlist: PlayList,
        db=Depends(mongo_database),
    ):
    result = await db.playlists.update_one(
        {
            "_id": ObjectId(playlist_id)
            if ObjectId.is_valid(playlist_id) else None
        },
        {"$set": updated_playlist.dict()}
    )
    if not result.modified_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    return {
        'message': 'Playlist updated successfully'
    }

@app.delete("/playlist/{playlist_id}")
async def delete_playlist(
        playlist_id: str,
        db=Depends(mongo_database),
    ):
    result = await db.playlists.delete_one(
        {
            "_id": ObjectId(playlist_id)
            if ObjectId.is_valid(playlist_id) else None
        }
    )
    if not result.deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    return {
        'message': 'Playlist deleted successfully'
    }

# get songs by year
@app.get("/songs/year")
async def get_songs_by_released_year(
        year: int,
        db=Depends(mongo_database),
    ):
    query = db.songs.find({"album.release_year": year})
    explained_query = await query.explain()
    logger.info(
        "Index used: %s",
        explained_query.get("queryPlanner", {})
        .get("winningPlan", {})
        .get("inputStage", {})
        .get("indexName", "No index was used")
    )

    songs = await query.to_list(None)
    return songs

# get songs by artist
@app.get("/songs/artist")
async def get_songs_by_artist(
        artist: str,
        db=Depends(mongo_database),
    ):
    query = db.songs.find({"$text": {"$search": artist}})
    explained_query = await query.explain()
    logger.info(
        "Index used: %s",
        explained_query.get("queryPlanner", {})
        .get("winningPlan", {})        
        .get("indexName", "No index was used")
    )

    songs = await query.to_list(None)
    return songs
