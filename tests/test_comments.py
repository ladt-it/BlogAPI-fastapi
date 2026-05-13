import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_comment(client: AsyncClient):
    # Регистрируем пользователя
    await client.post("/auth/register", json={
        "email": "commenter@mail.com",
        "username": "commenter",
        "password": "secret123",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "commenter@mail.com",
        "password": "secret123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём статью
    create_article_resp = await client.post("/articles/", json={
        "title": "Article for comments",
        "content": "Some content",
    }, headers=headers)
    article_id = create_article_resp.json()["id"]

    # Добавляем комментарий (добавлен / в конце)
    response = await client.post(f"/articles/{article_id}/comments/", json={
        "text": "Nice article!",
    }, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Nice article!"
    assert data["article_id"] == article_id
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_comments(client: AsyncClient):
    # Регистрируем пользователя
    await client.post("/auth/register", json={
        "email": "lister@mail.com",
        "username": "lister",
        "password": "secret123",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "lister@mail.com",
        "password": "secret123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём статью
    create_article_resp = await client.post("/articles/", json={
        "title": "Article for comment list",
        "content": "Content",
    }, headers=headers)
    article_id = create_article_resp.json()["id"]

    # Добавляем два комментария (исправлены слеши)
    await client.post(f"/articles/{article_id}/comments/", json={
        "text": "First comment",
    }, headers=headers)
    await client.post(f"/articles/{article_id}/comments/", json={
        "text": "Second comment",
    }, headers=headers)

    # Получаем список комментариев (добавлен /)
    response = await client.get(f"/articles/{article_id}/comments/?size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_update_comment_forbidden(client: AsyncClient):
    # Первый пользователь
    await client.post("/auth/register", json={
        "email": "owner_comment@mail.com",
        "username": "ownercomment",
        "password": "secret123",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "owner_comment@mail.com",
        "password": "secret123",
    })
    token_owner = login_resp.json()["access_token"]
    headers_owner = {"Authorization": f"Bearer {token_owner}"}

    # Создаём статью и комментарий от первого пользователя
    create_article_resp = await client.post("/articles/", json={
        "title": "Owner's article for comments",
        "content": "Secret",
    }, headers=headers_owner)
    article_id = create_article_resp.json()["id"]
    create_comment_resp = await client.post(f"/articles/{article_id}/comments/", json={
        "text": "Owner's comment",
    }, headers=headers_owner)
    comment_id = create_comment_resp.json()["id"]

    # Второй пользователь
    await client.post("/auth/register", json={
        "email": "intruder_comment@mail.com",
        "username": "intrudercomment",
        "password": "secret123",
    })
    login_resp2 = await client.post("/auth/login", json={
        "email": "intruder_comment@mail.com",
        "password": "secret123",
    })
    token_intruder = login_resp2.json()["access_token"]
    headers_intruder = {"Authorization": f"Bearer {token_intruder}"}

    # Пытаемся обновить чужой комментарий (исправлен URL с /)
    response = await client.put(
        f"/articles/{article_id}/comments/{comment_id}",
        json={"text": "Hacked comment"},
        headers=headers_intruder,
    )

    assert response.status_code == 403
    assert "Not your comment" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_comment(client: AsyncClient):
    # Регистрируем пользователя
    await client.post("/auth/register", json={
        "email": "deleter_comment@mail.com",
        "username": "deletercomment",
        "password": "secret123",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "deleter_comment@mail.com",
        "password": "secret123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём статью и комментарий
    create_article_resp = await client.post("/articles/", json={
        "title": "Article for comment deletion",
        "content": "Content",
    }, headers=headers)
    article_id = create_article_resp.json()["id"]
    create_comment_resp = await client.post(f"/articles/{article_id}/comments/", json={
        "text": "Comment to delete",
    }, headers=headers)
    comment_id = create_comment_resp.json()["id"]

    # Удаляем комментарий (URL с /, статус 204 без тела)
    response = await client.delete(f"/articles/{article_id}/comments/{comment_id}", headers=headers)
    assert response.status_code == 204

    # Проверяем, что комментарий действительно удалён (добавлен /)
    get_resp = await client.get(f"/articles/{article_id}/comments/?size=10")
    data = get_resp.json()
    assert len(data["items"]) == 0