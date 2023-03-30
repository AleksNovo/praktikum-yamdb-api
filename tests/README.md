# yamdb_final
yamdb_final
 
# YaMDb
 
YaMDb - база данных, которая собирает отзывы о различных произведениях. Произведения делятся на категории: «Книги», «Фильмы», «Музыка». При необходимости, список категорий может быть расширен администратором. Пользователи могут оставлять рецензии на произведения и ставить оценки.
 
Проект реализован на `Django` и `DjangoRestFramework`. Доступ к данным реализован через API-интерфейс. Документация к API написана с использованием `Redoc`.
 
## Особенности реализации
 
- Проект завернут в Docker-контейнеры;
- Реализован workflow через GitHubActions: тестирование, обновление образа на DockerHub, автоматический деплой на сервер, отправление сообщения в Telegram об успешном выполнении всех шагов workflow;
- Проект развернут на сервере <http://51.250.79.197/redoc/>
 
## Развертывание проекта
 
### Развертывание на локальном сервере
 
1. Установите на сервере `docker` и `docker-dompose`.
2. Создайте файл `/infra/.env`. Шаблон для заполнения файла нахоится в `/infra/.env.example`.
3. Выполните команду `docker-compose up -d --buld`.
4. Выполните миграции `docker-compose exec web python manage.py migrate`.
5. Создайте суперюзера `docker-compose exec web python manage.py createsuperuser`.
6. Соберите статику `docker-compose exec web python manage.py collectstatic --no-input`.
7. При необходимости заполните базу `docker-compose exec web python manage.py loaddata fixtures.json`.
8. Документация к API находится по адресу: <http://localhost/redoc/>.
 
### Настройка проекта для развертывания на удаленном сервере
 
1. Установите на сервере `docker` и `docker-dompose`.
2. Локально отредактируйте файл `infra/nginx.conf`, в строке `server_name` впишите IP-адрес сервера.
3. Скопируйте файлы `docker-compose.yaml` и `nginx/defult.conf` из директории `infra` на сервер:
 
```bash
    scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yaml
    scp default.conf <username>@<host>:/home/<username>/nginx/default.conf
```
 
4. Добавьте в Secrets GitHub следующие переменные:
 
```bash
    DB_ENGINE=django.db.backends.postgresql указываем, что работаем с postgresql
    DB_NAME=имя базы данных
    POSTGRES_USER=логин для подключения к базе данных
    POSTGRES_PASSWORD=# пароль для подключения к БД 
    DB_HOST=db
    DB_PORT=5432
 
    DOCKER_PASSWORD=пароль от DockerHub
    DOCKER_USERNAME=имя пользователя
 
    USER=username для подключения к серверу
    HOST=IP сервера
    PASSPHRASE=пароль для сервера, если он установлен
    SSH_KEY=ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)
 
    TELEGRAM_TO=ID чата, в который придет сообщение
    TELEGRAM_TOKEN=токен вашего бота
```
 
5. Выполните команды:
 
```bash
    git add .
    git commit -m 'ваш комментарий'
    git push
```
 
6. После выполнения команды `git push` и выполнения всех шагов `workflow`, проект будет развернут на удаленном сервере.
7. Для окончательной настройки, зайдите на уделенный сервер и выполните миграции, создайте суперюзера, соберите статику и заполните базу (см. шаги 4-7 из описания развертывания проекта на локальном сервере).
 
## Автор
 
 Александр Новожилов
 
[![Django-app workflow](https://github.com/alexnovo/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/alexnovo/yamdb_final/actions/workflows/yamdb_workflow.yml)