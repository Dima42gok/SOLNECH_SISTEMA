# Описание API AccessEvent

| Метод | URL | Доступ | Вход (JSON) | Ответы |
|---|---|---|---|---|
| POST | /api/register | все | username, email, password, role | 201 user_id; 400 ошибки валидации |
| POST | /api/login | все | email, password | 200 token; 401 неверные данные |
| GET | /api/events | все | — | 200 список мероприятий |
| POST | /api/events | organizer | title, event_date, is_inclusive | 201 id; 401 без токена |
| GET | /api/events/<id> | все | — | 200 мероприятие; 404 не найдено |
| PUT | /api/events/<id> | organizer | title, event_date | 200 обновлено; 403 чужое |
| DELETE | /api/events/<id> | organizer | — | 200 удалено; 403 чужое |

## Примеры

### POST /api/register — запрос
{"username": "anna", "email": "anna@mail.ru", "password": "Passw0rd!", "role": "user"}

### Ответ 201
{"user_id": 1, "message": "Пользователь создан"}

### POST /api/login — запрос
{"email": "anna@mail.ru", "password": "Passw0rd!"}

### Ответ 200
{"token": "eyJhbGciOiJIUzI1NiIs...", "role": "user"}

### POST /api/events — запрос (с токеном организатора)
{"title": "Тихий кинопросмотр", "event_date": "2026-11-03 19:00:00", "is_inclusive": true}

### Ответ 201
{"id": 5, "message": "Мероприятие создано"}