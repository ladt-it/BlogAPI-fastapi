import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_article(client: AsyncClient):
    # Регистрируем пользователя
    await client.post("/auth/register", json={
        "email": "article_test@mail.com",
        "username": "articletest",
        "password": "secret123",
    })
    # Логинимся, чтобы получить токен
    login_resp = await client.post("/auth/login", json={
        "email": "article_test@mail.com",
        "password": "secret123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём статью
    response = await client.post("/articles/", json={
        "title": "Test Article",
        "content": "Content of the article",
    }, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Article"
    assert data["content"] == "Content of the article"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_article(client: AsyncClient):
    # Регистрируем пользователя
    await client.post("/auth/register", json={
        "email": "get_article@mail.com",
        "username": "getarticle",
        "password": "secret123",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "get_article@mail.com",
        "password": "secret123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём статью
    create_resp = await client.post("/articles/", json={
        "title": "One more article",
        "content": "Body",
    }, headers=headers)
    article_id = create_resp.json()["id"]

    # Получаем статью по ID
    response = await client.get(f"/articles/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == "One more article"


@pytest.mark.asyncio
async def test_list_articles(client: AsyncClient):
    # Регистрируем пользователя
    await client.post("/auth/register", json={
        "email": "list_articles@mail.com",
        "username": "listarticles",
        "password": "secret123",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "list_articles@mail.com",
        "password": "secret123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём пару статей
    await client.post("/articles/", json={
        "title": "Article 1",
        "content": "Content 1",
    }, headers=headers)
    await client.post("/articles/", json={
        "title": "Article 2",
        "content": "Content 2",
    }, headers=headers)

    # Получаем список
    response = await client.get("/articles/?size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_update_article(client: AsyncClient):
    # Регистрируем пользователя
    await client.post("/auth/register", json={
        "email": "update_article@mail.com",
        "username": "updatearticle",
        "password": "secret123",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "update_article@mail.com",
        "password": "secret123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём статью
    create_resp = await client.post("/articles/", json={
        "title": "Old Title",
        "content": "Old Content",
    }, headers=headers)
    article_id = create_resp.json()["id"]

    # Обновляем
    response = await client.put(f"/articles/{article_id}", json={
        "title": "New Title",
        "content": "New Content",
    }, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["content"] == "New Content"


@pytest.mark.asyncio
async def test_update_article_forbidden(client: AsyncClient):
    # Первый пользователь
    await client.post("/auth/register", json={
        "email": "owner@mail.com",
        "username": "owner",
        "password": "secret123",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "owner@mail.com",
        "password": "secret123",
    })
    token_owner = login_resp.json()["access_token"]
    headers_owner = {"Authorization": f"Bearer {token_owner}"}

    # Создаём статью от первого пользователя
    create_resp = await client.post("/articles/", json={
        "title": "Owner's article",
        "content": "Secret",
    }, headers=headers_owner)
    article_id = create_resp.json()["id"]

    # Второй пользователь
    await client.post("/auth/register", json={
        "email": "intruder@mail.com",
        "username": "intruder",
        "password": "secret123",
    })
    login_resp2 = await client.post("/auth/login", json={
        "email": "intruder@mail.com",
        "password": "secret123",
    })
    token_intruder = login_resp2.json()["access_token"]
    headers_intruder = {"Authorization": f"Bearer {token_intruder}"}

    # Пытаемся обновить чужую статью
    response = await client.put(f"/articles/{article_id}", json={
        "title": "Hacked",
        "content": "Hacked",
    }, headers=headers_intruder)

    assert response.status_code == 403
    assert "Not your article" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_article(client: AsyncClient):
    # Регистрируем пользователя
    await client.post("/auth/register", json={
        "email": "delete_article@mail.com",
        "username": "deletearticle",
        "password": "secret123",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "delete_article@mail.com",
        "password": "secret123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём статью
    create_resp = await client.post("/articles/", json={
        "title": "To be deleted",
        "content": "Content",
    }, headers=headers)
    article_id = create_resp.json()["id"]

    # Удаляем
    response = await client.delete(f"/articles/{article_id}", headers=headers)
    assert response.status_code == 204

    # Проверяем, что удалилась
    get_resp = await client.get(f"/articles/{article_id}")
    assert get_resp.status_code == 404