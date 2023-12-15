# school-event-management-system

### Example of `.env` file:

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
CELERY_BROKER_URL=<redis://redis:6379>

# SMTP
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

```

### Start project:

Local:
```shell
docker-compose -f docker-compose-local.yml build
docker-compose -f docker-compose-local.yml up
```

Production:
```shell
docker-compose -f docker-compose-master.yml build
docker-compose -f docker-compose-master.yml up
```

## License

This project is licensed under the terms of the Apache-2.0 license.
