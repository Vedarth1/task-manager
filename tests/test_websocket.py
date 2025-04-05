import pytest
import websockets
import httpx,uuid
from auth import get_db, get_current_user
from sqlalchemy.orm import Session
from jose import jwt
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def extract_user_id_from_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("sub")

@pytest.mark.asyncio
async def test_websocket_connection():
    base_url = "http://localhost:8000"

    # Step 1: Register user
    async with httpx.AsyncClient() as client:
        await client.post(f"{base_url}/auth/signup", json={
            "email": f"test{uuid.uuid4()}@example.com",
            "password": "test123"
        })

        # Step 2: Log in
        response = await client.post(f"{base_url}/auth/login", data={
            "username": "websockettest@example.com",
            "password": "test123"
        })
        token_data = response.json()
        access_token = token_data["access_token"]

        # Step 3: Decode the user_id from token
        user_id = extract_user_id_from_token(access_token)

    # Step 4: Connect via WebSocket
    ws_url = f"ws://localhost:8000/ws/{user_id}"
    async with websockets.connect(ws_url) as websocket:
        await websocket.send("hello websocket")
        message = await websocket.recv()
        assert "hello websocket" in message
