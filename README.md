# Foodgram - продуктовый помощник
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