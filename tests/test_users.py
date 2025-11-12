from conftest import TEST_USER_1, TEST_USER_2


def test_get_me(client):
    """Тест авторизации"""

    apikey_good, user_1_name = TEST_USER_1.get("api_key"), TEST_USER_1.get("name")
    response = client.get("/api/users/me", headers={"api-key": apikey_good})
    assert response.status_code == 200
    assert response.json()["result"]
    assert response.json()["user"]["name"] == user_1_name
    assert all(
        f in response.json()["user"] for f in ("id", "name", "followers", "following")
    )

    apikey_bad = "very bad apy 55555"
    response = client.get("/api/users/me", headers={"api-key": apikey_bad})
    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    apikey_empty = ""
    response = client.get("/api/users/me", headers={"api-key": apikey_empty})
    assert response.status_code == 401
    assert "не существует" in response.json()["detail"]

    response = client.get("/api/users/me")
    assert response.status_code == 422
    assert "missing" == response.json()["detail"][0]["type"]

    user_2_name, user_2_api_key = TEST_USER_2.get("name"), TEST_USER_2.get("api_key")
    response_user_2 = client.get("/api/users/me", headers={"api-key": user_2_api_key})
    assert response_user_2.status_code == 200
    assert response_user_2.json()["user"]["name"] == user_2_name

    assert user_1_name != user_2_name


def test_get_user_by_id(client):
    """Тест получения пользователя по ID"""
    user_api = TEST_USER_1.get("api_key")
    target_user_id = TEST_USER_2.get("id")

    response = client.get(f"/api/users/{target_user_id}")
    assert response.status_code == 422

    response = client.get(
        f"/api/users/{target_user_id}", headers={"api-key": "BAD API-KEY"}
    )
    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    response = client.get(f"/api/users/{target_user_id}", headers={"api-key": user_api})
    assert response.status_code == 200
    assert response.json()["result"]
    assert all(
        f in response.json()["user"] for f in ("id", "name", "followers", "following")
    )

    response = client.get(
        f"/api/users/{TEST_USER_1.get('id')}",
        headers={"api-key": TEST_USER_2.get("api_key")},
    )
    assert response.status_code == 200
    assert response.json()["result"]

    NOT_USER = "99999"
    response = client.get(f"/api/users/{NOT_USER}", headers={"api-key": user_api})
    assert not response.json()["result"]
    assert response.json()["user"] is None


def test_follow_user_by_id(client):
    """Тест подписи на пользователя по ID"""
    user_api = TEST_USER_1.get("api_key")
    target_user_id = TEST_USER_2.get("id")

    response = client.post(f"/api/users/{target_user_id}/follow")
    assert response.status_code == 422

    response = client.post(
        f"/api/users/{target_user_id}/follow", headers={"api-key": "BAD API-KEY"}
    )
    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    # Фолловим пользователя
    response = client.post(
        f"/api/users/{target_user_id}/follow", headers={"api-key": user_api}
    )
    assert response.status_code == 200
    assert response.json()["result"]
    assert response.json()["message"] == "Успешно оформлена"

    # Проверка связи у пользователя с теми на кого подписан
    response = client.get(
        f"/api/users/{TEST_USER_1['id']}", headers={"api-key": user_api}
    )
    current_user_data = response.json()["user"]
    following_names = [
        following["name"] for following in current_user_data["following"]
    ]
    assert TEST_USER_2.get("name") in following_names

    # Если подписываемся повторно, хотя фронт должен запускать delete
    response = client.post(
        f"/api/users/{target_user_id}/follow", headers={"api-key": user_api}
    )
    assert not response.json()["result"]
    assert response.json()["message"] == "Ошибка повторного подписания"

    # Проверка подписи на себя
    response = client.post(
        f"/api/users/{TEST_USER_1.get('id')}/follow",
        headers={"api-key": TEST_USER_1.get("api_key")},
    )
    assert not response.json()["result"]
    assert response.json()["message"] == "Ошибка повторного подписания"


def test_unfollow_user_by_id(client):
    """Тест подписи на пользователя по ID"""
    user_api = TEST_USER_1.get("api_key")
    target_user_id = TEST_USER_2.get("id")

    response = client.delete(f"/api/users/{target_user_id}/follow")
    assert response.status_code == 422

    response = client.delete(
        f"/api/users/{target_user_id}/follow", headers={"api-key": "BAD API-KEY"}
    )
    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    # Отписываемся от пользователя
    response = client.delete(
        f"/api/users/{target_user_id}/follow", headers={"api-key": user_api}
    )
    assert response.status_code == 200
    assert response.json()["result"]
    assert response.json()["message"] == "Успешно удалена"

    # Проверка отсутствия связи у пользователя с теми на кого подписан
    response = client.get(
        f"/api/users/{TEST_USER_1['id']}", headers={"api-key": user_api}
    )
    current_user_data = response.json()["user"]
    following_names = [
        following["name"] for following in current_user_data["following"]
    ]
    assert TEST_USER_2.get("name") not in following_names
