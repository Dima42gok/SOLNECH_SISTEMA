# Анализ предметной области

Платформа AccessEvent помогает людям с особенностями слуха, зрения и мобильности находить мероприятия с доступной средой.

## Сущности системы

| Сущность | Описание | Ключевые поля |
|----------|----------|---------------|
| User | Пользователь платформы | id, email, password_hash, role |
| Event | Мероприятие | id, title, description, date, place |
| Registration | Запись на мероприятие | id, user_id, event_id, status |
| Organizer | Организатор мероприятия | id, name, contacts |
| Category | Категория мероприятия | id, name |
| AccessFeature | Особенность доступности | id, name, description |
| Review | Отзыв о мероприятии | id, user_id, event_id, text |
| Notification | Визуальное оповещение | id, user_id, message, sent_at |
