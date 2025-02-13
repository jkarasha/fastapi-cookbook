from motor.motor_asyncio import AsyncIOMotorClient

import logging

logger = logging.getLogger("uvicorn.error")

mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")

async def ping_mongo_db_server():
    try:
        await mongo_client.admin.command("ping")
        logger.info("MongoDB server pinged successfully")
    except Exception as e:
        logger.error(f"Error pinging MongoDB server: {str(e)}")
        raise e

