import pytest
from httpx import ASGITransport, AsyncClient

from protoapp.main import app

@pytest.mark.asyncio
async def test_read_main():
    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )
    response = await client.get("/home")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from ch-5!"}