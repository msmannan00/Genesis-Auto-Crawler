#!/bin/bash

PROJECT_NAME="trusted-crawler"

download_and_extract_model() {
    MODEL_URL="https://drive.usercontent.google.com/download?id=1o53BOk7KRHEvW7enV5-xeUyL3Zc4JYEy&export=download&authuser=0&confirm=t&uuid=62cc3df2-0ece-45a3-9f5c-6debbfa5548b&at=AENtkXZJdjHrZGxVOedjx6oSE5tl%3A1732663653099"
    MODEL_DEST_DIR="app/raw/model"
    MODEL_DEST_FILE="$MODEL_DEST_DIR/ml_classifier.zip"
    MODEL_EXTRACTED_DIR="$MODEL_DEST_DIR/saved_model"

    mkdir -p "$MODEL_DEST_DIR"

    if [ -d "$MODEL_EXTRACTED_DIR" ]; then
        echo "Extracted folder already exists."
        return
    fi

    for attempt in 1 2; do
        [ "$attempt" -eq 2 ] && echo "Retrying download and extraction..." && rm -f "$MODEL_DEST_FILE"

        [ ! -f "$MODEL_DEST_FILE" ] && curl -# -L "$MODEL_URL" -o "$MODEL_DEST_FILE"
        if unzip -o "$MODEL_DEST_FILE" -d "$MODEL_DEST_DIR"; then
            echo "Model downloaded and extracted successfully."
            return
        fi

        [ "$attempt" -eq 2 ] && echo "Failed to extract model after retrying. Exiting." && exit 1
    done
}

clean_docker() {
    docker compose -p $PROJECT_NAME down --volumes --remove-orphans
    docker container prune -f --filter "label=com.docker.compose.project=$PROJECT_NAME"
    docker volume prune -f --filter "label=com.docker.compose.project=$PROJECT_NAME"
    docker network prune -f --filter "label=com.docker.compose.project=$PROJECT_NAME"
    docker image prune -f --filter "label=com.docker.compose.project=$PROJECT_NAME"
    docker compose -p $PROJECT_NAME exec -T worker celery -A crawler.crawler_services.celery_manager control purge || true
    docker compose -p $PROJECT_NAME exec -T worker celery -A crawler.crawler_services.celery_manager control revoke --terminate --all || true
    docker compose -p $PROJECT_NAME exec -T redis redis-cli FLUSHALL || true

    docker network ls --filter "name=${PROJECT_NAME}_" --format '{{.Name}}' | while read -r net_name; do
        containers=$(docker network inspect -f '{{range .Containers}}{{.Name}} {{end}}' "$net_name")
        for container in $containers; do
            docker network disconnect "$net_name" "$container" || true
        done
        docker network rm "$net_name" || true
    done
}

stop_docker() {
    docker compose stop
    clean_docker
}

stop_docker
if [ "$1" == "stop" ]; then
    echo "crawler service stopped"
else
    if [ "$1" == "build" ]; then
        download_and_extract_model
        docker compose -p $PROJECT_NAME build
    fi

    docker compose -p $PROJECT_NAME up -d
    echo "crawler service started"
fi

