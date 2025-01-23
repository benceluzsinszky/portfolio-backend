from fastapi.security import APIKeyHeader
from fastapi import HTTPException, Security
import dotenv
import os

dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")

api_key_header = APIKeyHeader(name="api-key")


async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return api_key
