from conftest import TEST_USER_1, TEST_USER_2


def test_upload_media(client):
    """Тест загрузки медиа файла"""

    # Успешная загрузка картинки
    test_file = {"file": ("test_image.jpg", b"fake_image_content", "image/jpeg")}

    response = client.post(
        "/api/medias", files=test_file, headers={"api-key": TEST_USER_1["api_key"]}
    )

    assert response.status_code == 200
    assert response.json()["result"]
    media_id = response.json()["media_id"]
    assert isinstance(media_id, int)

    # Успешная загрузка PNG
    test_file_png = {"file": ("test_logo.png", b"fake_png_content", "image/png")}

    response = client.post(
        "/api/medias", files=test_file_png, headers={"api-key": TEST_USER_1["api_key"]}
    )

    assert response.status_code == 200
    assert response.json()["result"]

    # Неверный API ключ
    response = client.post(
        "/api/medias", files=test_file, headers={"api-key": "BAD_API_KEY_123"}
    )

    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    # Отсутствует файл
    response = client.post("/api/medias", headers={"api-key": TEST_USER_1["api_key"]})

    assert response.status_code == 422

    # Загрузка от другого пользователя
    response = client.post(
        "/api/medias", files=test_file, headers={"api-key": TEST_USER_2["api_key"]}
    )

    assert response.status_code == 200
    assert response.json()["result"]
