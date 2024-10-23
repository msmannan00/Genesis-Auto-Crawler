#!/bin/bash

PROJECT_NAME="toxic_model_project"
URL="https://drive.usercontent.google.com/download?id=1LTI94WsJbf8PheaMb7269Vxm5ZKtbHwb&export=download&authuser=0&confirm=t&uuid=1163171e-ce7c-4a98-9a46-2a3ce2a91f48&at=AO7h07dQiPcuFN56QrmDruowdk0P%3A1727101003781"
DEST_DIR="app/raw/toxic_model"
DEST_FILE="$DEST_DIR/toxic-model.zip"
EXTRACTED_DIR="$DEST_DIR/saved_model"
ENV_FILE=".env"

get_local_ip() { hostname -I | awk '{print $1}'; }

check_or_set_s_server() {
    [ ! -f "$ENV_FILE" ] && echo ".env file does not exist." && exit 1
    source "$ENV_FILE"

    if ! curl --silent --head --fail --max-time 5 "$S_SERVER"; then
        echo "Error: S_SERVER ($S_SERVER) is not accessible. Exiting."
        exit 1
    fi

    echo "S_SERVER is accessible: $S_SERVER"
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

reset_celery() {
    echo "Stopping 'trusted-crawler-celery' every 10 seconds..."
    while true; do
        docker restart trusted-crawler-celery
        sleep 43200
    done
}

if [ "$1" == "build" ]; then
    #check_or_set_s_server
    echo "Are you sure you want to remove all services and build the project? (y/n)"
    read -r confirm
    [ "$confirm" != "y" ] && exit 0
    clean_docker
    disconnect_and_remove_networks
    download_and_extract_model
    docker compose -p $PROJECT_NAME build
    docker compose -p $PROJECT_NAME up -d
    reset_celery
    echo "crawler service started"
elif [ "$1" == "invoke_unique_crawler" ]; then
    echo "operation in development phase"
elif [ "$1" == "stop" ]; then
    clean_docker
    disconnect_and_remove_networks
    docker compose down
    echo "Services stopped successfully."
else
    #check_or_set_s_server
    clean_docker
    disconnect_and_remove_networks
    download_and_extract_model
    docker compose -p $PROJECT_NAME up -d
    reset_celery
    echo "crawler service started"
fi
