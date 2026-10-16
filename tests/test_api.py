def _register_and_login(client, email, role):
    client.post("/api/register", json={
        "username": email.split("@")[0], "email": email,
        "password": "Passw0rd!", "role": role})
    resp = client.post("/api/login", json={
        "email": email, "password": "Passw0rd!"})
    return resp.get_json()["token"]


def test_register_success(client):
    resp = client.post("/api/register", json={
        "username": "anna", "email": "anna@mail.ru",
        "password": "Passw0rd!", "role": "user"})
    assert resp.status_code == 201
    assert "user_id" in resp.get_json()


def test_register_invalid_email_rejected(client):
    resp = client.post("/api/register", json={
        "username": "bob", "email": "not-an-email",
        "password": "Passw0rd!", "role": "user"})
    assert resp.status_code == 400


def test_login_returns_token(client):
    client.post("/api/register", json={
        "username": "org", "email": "org@mail.ru",
        "password": "Passw0rd!", "role": "organizer"})
    resp = client.post("/api/login", json={
        "email": "org@mail.ru", "password": "Passw0rd!"})
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_create_event_requires_organizer_token(client):
    resp = client.post("/api/events", json={"title": "Лекция"})
    assert resp.status_code in (401, 403)


def test_events_list_public(client):
    resp = client.get("/api/events")
    assert resp.status_code == 200


def test_create_event_with_token(client):
    token = _register_and_login(client, "org3@mail.ru", role="organizer")
    headers = {"Authorization": "Bearer " + token}
    resp = client.post("/api/events", json={
        "title": "Тихий кинопросмотр",
        "event_date": "2026-11-03 19:00:00",
        "is_inclusive": True}, headers=headers)
    assert resp.status_code == 201
    assert "id" in resp.get_json()