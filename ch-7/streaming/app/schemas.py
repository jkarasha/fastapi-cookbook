from pydantic import BaseModel

class PlayList(BaseModel):
    name: str
    songs: list[str] = []