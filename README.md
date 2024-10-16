### Проект Foodgram – Продуктовый помощник
Foodgram — это веб-приложение, которое помогает пользователям сохранять и управлять рецептами, 
подписываться на других пользователей, добавлять любимые рецепты в избранное и генерировать списки покупок для приготовления блюд. 
Сервис создан для того, чтобы сделать процесс планирования готовки еды по рецептам и покупки ингредиентов более удобным и организованным.
На сервисе фудграм пользователи могут публиковать рецепты, подписываться на публикации других пользователей, 
добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

## Используемые технологии
- **Django** — основной фреймворк для разработки веб-приложения.
- **Django REST Framework** — для создания RESTful API.
- **PostgreSQL** — основная база данных (в Docker-контейнерах).
- **Docker** — для контейнеризации приложения и его зависимостей.
- **Nginx** — для развертывания и проксирования запросов.
- **Git** — для управления версиями кода.

#### Доступ для неавторизованных пользователей
- Доступна главная страница.
- Доступна страница отдельного рецепта.
- Доступна страница любого пользователя.
- Доступна и работает форма входа.
- Доступна и работает форма регистрации.
#### Доступ для авторизованных пользователей
- Доступен в систему под своим логином и паролем.
- Доступен выход из системы (логаут).
- Доступна возможность изменения своего пароля.
- Доступна возможность создавать/редактировать/удалять собственные рецепты.
- Доступна главная страница.
- Доступна страница любого пользователя.
- Доступна страница отдельного рецепта.
- Доступна фильтрация рецептов по тегам.
- Доступна страница «Избранное»: добавлять рецепты в «Избранное» или удалять их, просматривать свою страницу избранных рецептов.
- Доступна страница «Список покупок»: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
- Доступна страница «Мои подписки»: возможность подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.
#### Доступ для администратора
Администратор обладает всеми правами авторизованного пользователя.
Дополнительные привилегии через админ-зону:
- Возможность изменять пароль любого пользователя.
- Возможность создавать/блокировать/удалять аккаунты пользователей.
- Возможноть редактировать/удалять любые рецепты.
- Возможноть добавлять/удалять/редактировать ингредиенты.
- Возможность добавлять/удалять/редактировать теги.

#### Запуск проекта в контейнерах

- Клонирование удаленного репозитория
```bash
git clone git@github.com:ForTheDarknessCome/foodgram.git
```
- В главной директории проекта необходимо создать файл .env с переменными окружения(в пример предоставлен файл .env.example в корне проекта).
- Сборка и развертывание контейнеров
```bash
cd infra
docker compose -f docker-compose.production.yml up -d --build
```
- Выполнение миграций, сбор статики, наполнение бд и создание суперпользователя автоматизированы и выполняются в файле entrypoint.sh
- Стандартная админ-панель Django доступна по адресу [`https://localhost/admin/`](https://localhost/admin/)

#### Запуск API проекта в dev-режиме

- Клонирование удаленного репозитория (см. выше)
- Создание виртуального окружения и установка зависимостей
```bash
cd backend
python -m venv .venv (можно просто venv)
. Source/.venv/Scripts/activate (windows)
. Source/.venv/bin/activate (linux)
pip install --upgade pip
pip install -r -requirements
```
- Примените миграции и соберите статику
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```
- Наполнение базы данных ингредиентами и тегами
```bash
python manage.py import_data
```
- в файле foodgram/setting.py замените БД на встроенную SQLite
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

- Запуск сервера
```bash
python manage.py runserver 
```
#### Данные сервера в глобальной сети

- В глобальной среде сервер доступен по следующему адресу: `https://f00dgram.ddns.net`
- IP адрес сервера: 89.169.165.185

- Данные для входа в админ-панель:
- Email - 'Antharas@example.com'
- Password - '456852123789Ee' p.s(Ee в латинской раскладке)
