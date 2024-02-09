# school-event-management-system

### Пример файла `.env`:

```dotenv
ENV=.env

# Project
SCHOOL_NAME=
SECRET_KEY=
DEBUG=

# Database
DB_NAME=
DB_USER=
DB_PASSWORD=

# Celery
CELERY_BROKER_URL=redis://redis:6379

# SMTP
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

```

### Запустить проект:

В локальной среде:
```shell
docker-compose -f docker-compose-local.yml build
docker-compose -f docker-compose-local.yml up
```

В производственной среде:
```shell
docker-compose -f docker-compose-master.yml build
docker-compose -f docker-compose-master.yml up
```

## Документация

- [Документация](./docs/README.md)


## License

This project is licensed under the terms of the Apache-2.0 license.
