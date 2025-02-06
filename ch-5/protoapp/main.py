from fastapi import FastAPI

app = FastAPI()

@app.get("/home")
async def read_main():
    return {"message": "Hello from ch-5!"}