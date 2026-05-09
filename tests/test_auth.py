import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "test@mail.com",
        "username": "testuser",
        "password": "secret123",
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "dup@mail.com", "username": "user1", "password": "pass1",
    })
    response = await client.post("/auth/register", json={
        "email": "dup@mail.com", "username": "user2", "password": "pass2",
    })

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "login@mail.com", "username": "login", "password": "pass",
    })
    response = await client.post("/auth/login", json={
        "email": "login@mail.com", "password": "pass",
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "wrong@mail.com", "username": "w", "password": "right",
    })
    response = await client.post("/auth/login", json={
        "email": "wrong@mail.com", "password": "wrong",
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "refresh@mail.com", "username": "r", "password": "p",
    })
    refresh_token = response.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data