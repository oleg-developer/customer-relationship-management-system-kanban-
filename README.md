customer relationship management system (kanban)
============

## Back
1. Ставим зависмости 
2. Монтируем сабмодуль 
3. Запускаем uwsgi на 2021 порту и прокидываем его.
 
Миграции и статику собирать руками.

## Front
1. Копируем зависимости
2. Ставим зависимости
3. Копируем исходники
4. Собираем исходники в раздел static-front

## Web (nginx)
0. Закидывает конфиг nginx'а, удаляя дефолтный
1. Берет статику от
   * фронта (static-front)
   * джанги (примонтированный сабмодуль)
2. Прокидывает в uwsgi /admin/ & /api/

## Commands
```
submodules_setup.sh
submodules_dev_setup.sh

docker-compose up -d
docker-compose -f docker-compose-dev.yml up -d

docker exec -it rasa-back python manage.py collectstatic
docker exec -it rasa-back python manage.py migrate
docker exec -it rasa-back python manage.py createsuperuser
```
