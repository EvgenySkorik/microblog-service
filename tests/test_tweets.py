from conftest import TEST_USER_1, TEST_USER_2, TEST_USER_3

TWEET = "Тестовый твит без нагрузки №1"
TWEET_WITH_MEDIA = "Твит с нагрузкой №2"


def test_post_tweet(client):
    """Тест публикации твита без медиа"""
    user = TEST_USER_1

    test_tweet_data = {"tweet_data": TWEET, "tweet_media_ids": []}

    # Проверка публикации твита без нагрузки
    response = client.post(
        "/api/tweets", json=test_tweet_data, headers={"api-key": user["api_key"]}
    )

    assert response.status_code == 200
    assert response.json()["result"]
    assert isinstance(user.get("id"), int)
    assert response.json()["tweet_id"] == 1

    check_get_tweets_response = client.get(
        "/api/tweets", headers={"api-key": user["api_key"]}
    )
    assert check_get_tweets_response.status_code == 200
    assert TWEET in [tw["content"] for tw in check_get_tweets_response.json()["tweets"]]

    # Неправильный API
    apikey_bad = "very bad apy 55555"
    response = client.post(
        "/api/tweets", json=test_tweet_data, headers={"api-key": apikey_bad}
    )
    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    # Отсутствие API
    apikey_empty = ""
    response = client.post(
        "/api/tweets", json=test_tweet_data, headers={"api-key": apikey_empty}
    )
    assert response.status_code == 401
    assert "не существует" in response.json()["detail"]

    # Проверка публикации твита с нагрузкой

    test_file = {"file": ("test.txt", b"Some beautiful picture", "text/plain")}

    response_media = client.post(
        "/api/medias", files=test_file, headers={"api-key": user["api_key"]}
    )  # загрузка медиа перед созданием твита с нагрузкой
    assert response_media.status_code == 200
    media_id = response_media.json()["media_id"]

    test_tweet_data["tweet_data"] = TWEET_WITH_MEDIA
    test_tweet_data["tweet_media_ids"] = [media_id]

    response = client.post(
        "/api/tweets", json=test_tweet_data, headers={"api-key": user["api_key"]}
    )

    assert response.status_code == 200
    assert response.json()["result"]


def test_get_tweets(client):
    """Тест получения всех твитов"""
    user = TEST_USER_1

    response = client.get("/api/tweets", headers={"api-key": user["api_key"]})
    tweets_without_filtr_likes = response.json()["tweets"]

    assert response.status_code == 200
    assert response.json()["result"]
    assert len(response.json()["tweets"]) == 2
    assert all(
        f in response.json()["tweets"][0]
        for f in ("id", "content", "created_at", "author", "attachments", "likes")
    )
    assert any(tw["content"] == TWEET for tw in response.json()["tweets"])

    # Неправильный API
    apikey_bad = "very bad apy 55555"
    response = client.get("/api/tweets", headers={"api-key": apikey_bad})
    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    # Отсутствие API
    apikey_empty = ""
    response = client.get("/api/tweets", headers={"api-key": apikey_empty})
    assert response.status_code == 401
    assert "не существует" in response.json()["detail"]

    # Проверка фильтрации твитов по кол-ву лайков, залайкаем ТВИТ №1
    # (так как он сейчас второй в tweets, так как был опубликован раньше по created_at)
    id_tweet = 1
    cur_user_2 = TEST_USER_2
    cur_user_3 = TEST_USER_3

    response_like_from_user_2 = client.post(
        f"/api/tweets/{id_tweet}/likes", headers={"api-key": cur_user_2["api_key"]}
    )
    response_like_from_user_3 = client.post(
        f"/api/tweets/{id_tweet}/likes", headers={"api-key": cur_user_3["api_key"]}
    )
    assert response_like_from_user_2.status_code == 200
    assert response_like_from_user_3.status_code == 200

    response_with_likes = client.get(
        "/api/tweets", headers={"api-key": user["api_key"]}
    )

    assert response_with_likes.status_code == 200
    assert response_with_likes.json()["result"]
    assert len(response_with_likes.json()["tweets"]) == len(tweets_without_filtr_likes)
    assert response_with_likes.json()["tweets"][0]["id"] == id_tweet


def test_delete_tweet(client):
    """Тест удаления твита"""

    tweet_without_media_id = 1
    tweet_with_media_id = 2

    # Проверка удаления твита №1 от автора, который его не опубликовал
    response = client.delete(
        f"/api/tweets/{tweet_without_media_id}",
        headers={"api-key": TEST_USER_3["api_key"]},
    )

    assert "нет прав для удаления" in response.json()["detail"]

    # Отсутствие твита
    response = client.delete(
        f"/api/tweets/{tweet_with_media_id}",
        headers={"api-key": TEST_USER_3["api_key"]},
    )

    assert "Твит не найден" in response.json()["detail"]

    # Проверка авторизации
    response = client.delete(
        f"/api/tweets/{tweet_with_media_id}", headers={"api-key": "BAD API KEY55555"}
    )

    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    # Проверка удаления твита №1 без нагрузки от автора
    response = client.delete(
        f"/api/tweets/{tweet_without_media_id}",
        headers={"api-key": TEST_USER_1["api_key"]},
    )

    assert response.status_code == 200
    assert response.json()["result"]
    assert response.json()["message"] == "Ok delete"

    response_tweets = client.get(
        "/api/tweets", headers={"api-key": TEST_USER_1["api_key"]}
    )

    assert response_tweets.status_code == 200
    assert len(response_tweets.json()["tweets"]) != 2
    assert any(tw["id"] != 1 for tw in response_tweets.json()["tweets"])

    # Проверка удаления твита №2 с нагрузкой, от автора
    response = client.delete(
        f"/api/tweets/{tweet_with_media_id}",
        headers={"api-key": TEST_USER_1["api_key"]},
    )

    assert response.status_code == 200
    assert response.json()["result"]
    assert response.json()["message"] == "Ok delete"

    response_tweets = client.get(
        "/api/tweets", headers={"api-key": TEST_USER_1["api_key"]}
    )

    assert not response_tweets.json()["result"]
    assert response_tweets.json()["tweets"] is None


def test_like_tweet(client):
    """Тест для установки лайка"""
    users = [TEST_USER_1, TEST_USER_3]
    # Создаём твит и лайкаем его от двух пользователей
    test_tweet_data = {"tweet_data": TWEET, "tweet_media_ids": []}

    response = client.post(
        "/api/tweets", json=test_tweet_data, headers={"api-key": TEST_USER_2["api_key"]}
    )
    tweet_id = response.json()["tweet_id"]

    # Проверка авторизации
    response = client.post(
        f"/api/tweets/{tweet_id}/likes", headers={"api-key": "BAD API KEY55555"}
    )
    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    for u in users:
        response = client.post(
            f"/api/tweets/{tweet_id}/likes", headers={"api-key": u["api_key"]}
        )

    response = client.get("/api/tweets", headers={"api-key": TEST_USER_2["api_key"]})

    assert response.status_code == 200
    assert response.json()["result"]
    assert len(response.json()["tweets"][0]["likes"]) == 2


def test_unlike_tweet(client):
    """Тест для удаления лайка"""
    users = [TEST_USER_1, TEST_USER_3]
    tweet_id = 1

    # Проверка авторизации
    response = client.delete(
        f"/api/tweets/{tweet_id}/likes", headers={"api-key": "BAD API KEY55555"}
    )
    assert response.status_code == 401
    assert "Не верный ключ API-Key" in response.json()["detail"]

    # Убираем оба лайка от двух пользователей поставленных в test_like_tweet
    for u in users:
        response = client.delete(
            f"/api/tweets/{tweet_id}/likes", headers={"api-key": u["api_key"]}
        )

    response = client.get("/api/tweets", headers={"api-key": TEST_USER_2["api_key"]})

    assert response.status_code == 200
    assert response.json()["result"]
    assert len(response.json()["tweets"][0]["likes"]) == 0
