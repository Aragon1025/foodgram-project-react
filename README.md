# Foodgram - продуктовый помощник
![GitHub Workflow Status](https://github.com/Aragon1025/foodgram-project-react/actions/workflows/main.yml/badge.svg)
### Описание:
Foodgram это веб сервис, с помощью которого, пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список(в формате .txt) продуктов

### Используемые технологии:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

1. Склонируйте репозиторий по ссылке:
```
git clone git@github.com:Aragon1025/foodgram-project-react.git
```

2. В корневом каталоге создайте файл .env и добавьте необходимые данные:
* POSTGRES_DB=foodgram # Задаем имя для БД.
* POSTGRES_USER=foodgram_user # Задаем пользователя для БД.
* POSTGRES_PASSWORD=foodgram_password # Задаем пароль для БД.
* DB_HOST=db
* DB_PORT=5432
* DEBUG_MODE=False
* SECRET_KEY=django-insecure
* ALLOWED_HOSTS=127.0.0.1 localhost # Задаем свой IP сервера, DNS имя
* CSRF_TRUSTED_ORIGINS=http://127.0.0.1 http://localhost # Задаем свой IP сервера, DNS имя

# Для добавления логирования в телеграм так же в файле .env можно указать поля 
* TELEGRAM_TOKEN=Ваш токен телеграм бота 
* TELEGRAM_CHAT_ID=Ваш ChatID в телеге

3. Установите вирутальное окружение и зависимости:
```sh
python -m venv venv
pip install -r requirements.txt 

4. Выполните команду из корневой директории
docker-compose up --build

5. После запуска, откройте контейнер web и в нём выполните следующие команды
```sh
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py import_ingredients
```

## На сервер попасть можно по адресу https://aragon.servebeer.com/


## Автор проекта
- https://github.com/Aragon1025 "Трушков Павел"