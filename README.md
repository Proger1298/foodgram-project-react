Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

**Шаблон наполнения env-файла**

DB_ENGINE=.. # указываем, что работаем с postgresql ( или не с ней :) )

DB_NAME=... # имя базы данных

POSTGRES_USER=... # логин для подключения к базе данных

POSTGRES_PASSWORD=...

DB_HOST=... # название сервиса (контейнера)

DB_PORT=... # порт для подключения к БД

## Установка проекта локально в контейнерах:

Для сборки и запуска контейнеров
```docker-compose up -d --build ```

При необходимости создайте суперпользователя
```docker-compose exec web python manage.py createsuperuser```

При желании можете заполнить базу данных готовыми данными
```docker-compose exec backend python manage.py loaddata dump.json```

## Установка проекта локально:

**Cоздать и активировать виртуальное окружение:**

```python -m venv venv ```

```source venv/bin/activate ```

**Установить зависимости из файла requirements.txt:**

```python3 -m pip install --upgrade pip ```

```pip install -r requirements.txt ```

**Выполнить миграции:**

```python manage.py migrate ```

**Запуск проекта:**

```python manage.py runserver```

### Примеры запросов:

**`POST` | Создание рецепта: `http://localhost/api/recipes/`**

Request:
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoA ... g==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
Response:
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

# В проекте применены технологии:

Python 3.8.10

Django 4.1.7

Django REST Framework 3.14.0

# Авторы:
**Антон Кучеренко** https://github.com/Proger1298
