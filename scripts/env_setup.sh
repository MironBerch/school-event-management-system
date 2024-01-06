#!/bin/sh

ORIGINAL_DIR=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ENV_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"

cd "$DIR"

if [ -f "../.env" ]; then
    echo "Загрузка переменных среды из $(realpath "$ENV_FILE")"
    while IFS= read -r line; do
        if [[ ! "$line" =~ ^[[:space:]]*# && ! -z "$line" ]]; then
        key=$(echo "$line" | awk -F '=' '{print $1}')
        value=$(echo "$line" | awk -F '=' '{print $2}')
        export "$key"="$value"
        echo "Set $key"
        fi
    done < "$ENV_FILE"
    echo "Переменные среды, заданны из $(realpath "$ENV_FILE")."
else
    echo "Файл .env не найден в директории - $ENV_DIR/"
    echo "Создайте файл по пути - $ENV_DIR/.env"
fi

cd "$ORIGINAL_DIR"
