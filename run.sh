#!/bin/bash

PROJECT_NAME="trusted-crawler"
URL="https://drive.usercontent.google.com/download?id=13xo-4qqUsQfr3F33A4VpSz6S2k-Hmr0J&export=download&authuser=0&confirm=t&uuid=8611f394-74e3-4627-a38a-97243f909554&at=AENtkXbi_DUr8t4VbB_We6G-S0Hk%3A1731234574948"
DEST_DIR="app/raw/model"
DEST_FILE="$DEST_DIR/ml_classifier.zip"
EXTRACTED_DIR="$DEST_DIR/saved_model"
ENV_FILE=".env"

get_local_ip() { hostname -I | awk '{print $1}'; }

check_or_set_s_server() {
    [ ! -f "$ENV_FILE" ] && echo ".env file does not exist." && exit 1
    source "$ENV_FILE"
    S_SERVER=$(echo "$S_SERVER" | tr -d '\r' | xargs)
    if [ -z "$S_SERVER" ]; then
        echo "Error: S_SERVER is not set or empty in the .env file." >&2
        exit 1
    fi
    if curl --silent --head --fail --max-time 5 "$S_SERVER" > /dev/null; then
        echo "SUCCESS: $S_SERVER is accessible." >&2
    else
        echo "Error: $S_SERVER is not accessible." >&2
        exit 1
    fi
}

mkdir -p $DEST_DIR

download_and_extract_model() {
    [ -d "$EXTRACTED_DIR" ] && echo "Extracted folder already exists." && return
    [ ! -f "$DEST_FILE" ] && curl -# -L "$URL" -o "$DEST_FILE"
    [ -f "$DEST_FILE" ] && unzip -o "$DEST_FILE" -d "$DEST_DIR" && rm "$DEST_FILE"
}

clean_docker() {
    docker compose -p $PROJECT_NAME down --volumes --remove-orphans
    docker container prune -f --filter "label=com.docker.compose.project=$PROJECT_NAME"
    docker volume prune -f --filter "label=com.docker.compose.project=$PROJECT_NAME"
    docker network prune -f --filter "label=com.docker.compose.project=$PROJECT_NAME"
    docker image prune -f --filter "label=com.docker.compose.project=$PROJECT_NAME"
}

disconnect_and_remove_networks() {
    docker network ls --filter "name=${PROJECT_NAME}_" --format '{{.Name}}' | while read -r net_name; do
        containers=$(docker network inspect -f '{{range .Containers}}{{.Name}} {{end}}' "$net_name")
        for container in $containers; do
            docker network disconnect "$net_name" "$container"
        done
        docker network rm "$net_name"
    done
    docker network ls --format '{{.Name}}' | grep -q "toxic_model_project_backend" && docker network rm toxic_model_project_backend
}

rebuild_api_container() {
    echo "Stopping and removing any existing trusted-crawler-api container..."
    docker stop trusted-crawler-api || true
    docker rm trusted-crawler-api || true

    echo "Rebuilding the trusted-crawler-api container..."
    docker compose -p $PROJECT_NAME build trusted-crawler-api
    docker compose -p $PROJECT_NAME up -d trusted-crawler-api

    echo "trusted-crawler-api container rebuilt and started."
}

reset_celery() {
    while true; do
      docker stop trusted-crawler-celery
      docker start trusted-crawler-celery
      sleep 86400
    done
}

if [ "$1" == "build" ]; then
    docker compose down
    check_or_set_s_server
    echo "Are you sure you want to remove all services and build the project? (y/n)"
    read -r confirm
    [ "$confirm" != "y" ] && exit 0
    clean_docker
    disconnect_and_remove_networks
    download_and_extract_model
    rebuild_api_container
    docker compose -p $PROJECT_NAME build
    docker compose -p $PROJECT_NAME up -d
    echo "crawler service started"
elif [ "$1" == "invoke_unique_crawler" ]; then
    echo "operation in development phase"
elif [ "$1" == "stop" ]; then
    clean_docker
    disconnect_and_remove_networks
    docker compose down
    echo "Services stopped successfully."
else
    docker compose down
    check_or_set_s_server
    clean_docker
    disconnect_and_remove_networks
    download_and_extract_model
    rebuild_api_container
    docker compose down
    docker compose -p $PROJECT_NAME up -d
    echo "crawler service started"
fi
