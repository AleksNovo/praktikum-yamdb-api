# YaMDb REST API
![Workflow status badge](https://github.com/AleksNovo/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

Учебный командный проект Яндекс Практикум (курс Python-разработчик).

## Описание
Сервис YaMDb собирает отзывы пользователей на произведения (фильмы, книги и музыка). Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

В проекте реализована контейнеризация с помощью Docker и Docker Compose, а также CI/CD через GitHub Actions.

## Технологии
[![Python](https://img.shields.io/badge/Python-3.7-3776AB?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-2.2-092E20?&logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-grey?logo=postgresql)](https://www.postgresql.org/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-grey?logo=django)](https://www.django-rest-framework.org/)
[![JSON Web Tokens](https://img.shields.io/badge/JSON_Web_Tokens-grey?logo=jsonwebtokens)](https://jwt.io/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-grey?logo=gunicorn)](https://gunicorn.org/)
[![nginx](https://img.shields.io/badge/nginx-grey?logo=nginx)](https://nginx.org/)
[![Docker](https://img.shields.io/badge/Docker-grey?logo=docker)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker_Compose-grey?logo=docker)](https://docs.docker.com/compose/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-grey?logo=githubactions)](https://github.com/features/actions)

## Авторы
- @epanchincev - регистрация и аутентификация, подтверждение через email, права доступа;
- @AuXoNej - произведения, категории, жанры;
- @AleksNovo - отзывы, комментарии, рейтинг произведений, контейнеризация и инфраструктура.

## Доступные эндпоинты
- `api/v1/auth/signup/` (POST): регистрация нового пользователя;
- `api/v1/auth/token/` (POST): получение JWT-токена;
- `api/v1/users/` (GET, POST): получение списка всех пользователей или добавление нового;
- `api/v1/users/me/` (GET, PATCH): получение или редактирование данных своей учетной записи;
- `api/v1/users/{username}/` (GET, PATCH, DELETE): получение, редактирование или удаление пользователя по `username`;
- `api/v1/categories/` (GET, POST): получение списка всех категорий или добавление новой;
- `api/v1/categories/{slug}` (DELETE): удаление категории по `slug`;
- `api/v1/genres/` (GET, POST): получение списка всех жанров или добавление нового;
- `api/v1/genres/{slug}` (DELETE): удаление жанра по `slug`;
- `api/v1/titles/` (GET, POST): получение списка всех произведений или добавление нового;
- `api/v1/titles/{title_id}/` (GET, PATCH, DELETE): получение, редактирование или удаление произведения по `id`;
- `api/v1/titles/{title_id}/reviews/` (GET, POST): получение списка всех отзывов или добавление нового на произведение с  `id=title_id`;
- `api/v1/titles/{title_id}/reviews/{review_id}/` (GET, PATCH, DELETE): получение, редактирование или удаление отзыва по `id` на произведение с `id=title_id`;
- `api/v1/titles/{title_id}/reviews/{review_id}/comments/` (GET, POST): получение списка всех комментариев или добавление нового к отзыву с `id=review_id`;
- `api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` (GET, PATCH, DELETE): получение, редактирование или удаление комментария по `id` к отзыву с `id=review_id`.

## Документация к API
Подробная документация к API будет доступна после запуска проекта по эндпоинту:
```
redoc/
```

## Запуск проекта в Docker-контейнерах
Клонировать репозиторий и перейти в директорию `infra/`:
```bash
git clone https://github.com/bvsvrvb/praktikum-yamdb-api.git
```
```bash
cd praktikum-yamdb-api/infra
```

Создать `.env` файл с переменными окружения:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=db
DB_PORT=5432
```

Собрать и запустить контейнеры:
```bash
docker-compose up
```

Создать миграции внутри контейнера `web`:
 ```bash
 sudo docker-compose exec web python manage.py makemigrations
 ```

Выполнить миграции внутри контейнера `web`:
 ```bash
 sudo docker-compose exec web python manage.py migrate
 ```

Собрать статику проекта внутри контейнера `web`:
 ```bash
 sudo docker-compose exec web python manage.py collectstatic --no-input
 ```  

Создать суперпользователя для админ-панели внутри контейнера `web`:
 ```bash
 sudo docker-compose exec web python manage.py createsuperuser
 ```

## CI/CD GitHub Actions

### Workflow состоит из четырёх шагов:

   1. Проверка кода тестами.
   2. Сборка и публикация образа на DockerHub.
   3. Автоматический деплой и запуск контейнеров на удаленном сервере.
   4. Отправка уведомления в телеграм-чат.

### Для работы с Workflow GitHub Actions необходимо добавить в GitHub Secrets переменные окружения:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=db
DB_PORT=5432

DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
```

### И подготовить удаленный сервер:
Выполнить вход на удаленный сервер:
```bash
ssh <username>@<host>
```

Установить Docker на сервере:
```bash
sudo apt install docker.io 
```

Установить Docker Compose на сервере:
```bash
sudo apt install docker-compose
```

Скопировать файлы `docker-compose.yaml` и `default.conf` на сервер:
```bash
scp docker-compose.yaml <username>@<host>:/home/<username>/
scp default.conf <username>@<host>:/home/<username>/nginx/
```
