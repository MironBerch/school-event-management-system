# Руководство по развёртыванию проекта на VPS сервере

Руководство по развёртыванию проекта на производственный VPS сервере.

## Конфигурация VPS сервера

#### Минимальная конфигурация VPS сервера:
| Комплектующие | Характеристика |
| ------ | ------ |
| CPU | 1 × 2000 МГц |
| RAM | 1 Гб |
| Диск | 10 Гб |

#### Рекомендуемая конфигурация VPS сервера:
| Комплектующие | Характеристика |
| ------ | ------ |
| CPU | 1 × 2000 МГц |
| RAM | 2 Гб |
| Диск | 15 Гб |

## Развёртывание проекта

- Запустите эту команду - она установит все зависимости необходимые для развёртывания проекта
```sh
sudo apt install git docker docker-compose vim
```

- Запустите эту команду - она скачает проект с GitHub
```sh
git clone https://github.com/MironBerch/school-event-management-system.git
```

- Запустите эту команду - она перенаправляет в каталог с кодом
```sh
cd school-event-management-system
```

- Запустите эту команду - она создаст `.env` файл с помощью vim 
```sh
vim .env
```

- Пример `.env` файла
```dotenv
ENV=.env

# Project
SECRET_KEY=
DEBUG=
SCHOOL_NAME=

# Postgres
DB_NAME=
DB_USER=
DB_PASSWORD=

# SMTP
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_HOST=
DEFAULT_FROM_EMAIL=

# Celery
CELERY_BROKER_URL=redis://redis:6379
```

- Запустите эту команду - она обновит миграции бд
```sh
. scripts/env_setup.sh && . scripts/setup_school_name.sh
```

- Запустите эту команду - она запустит проект
```sh
docker-compose -f docker-compose.yml -f docker-compose-master.yml up --build -d
```
