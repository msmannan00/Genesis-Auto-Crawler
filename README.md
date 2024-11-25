# Trustly-Crawler

This repository contains a webcrawler designed for monitoring the dark web. It uses Docker Compose to manage services, including MongoDB, Redis, and multiple Tor containers for enhanced anonymity.

## Prerequisites

Ensure you have the following installed on your system:
- [Python]([https://www.rust-lang.org/tools/install](https://github.com/python))
- [Docker]([https://nodejs.org/](https://github.com/docker))
- [Docker Compose]([https://github.com/docker/compose])

## Installation

### Step 1: Clone Repository

```
git clone https://github.com/yourusername/dark-web-monitoring-webcrawler.git
cd dark-web-monitoring-webcrawler
```

### Step 2: Build and Start the Docker
```
docker-compose up --build
```
This command will build and start the following services:

    API Service (api): The main webcrawler service that runs according to the predefined settings.
    MongoDB (mongo): Database for storing crawled data.
    Redis (redis_server): In-memory data store for caching and task queuing.
    Tor Containers (tor-extend-*): Multiple Tor instances to route crawler traffic through different Tor exit nodes.

### Step 3: Build and Start the Services

You can run the webcrawler in two ways:

#### Direct Execution:
    
- Copy app/libs/nltk_data folder to appdata in windows or home directory in linux.
- Navigate to the Genesis-Crawler/app/ directory.
- Run the webcrawler directly using:
    
```
python main_direct.py
```
#### Using Docker:

- The webcrawler can also be started using Docker, which utilizes the start_app.sh script:

```
docker-compose up --build
```
        
## Project Structure

api/: Contains the webcrawler source code.
data/db/: Directory where MongoDB stores data.
dockerFiles/: Dockerfiles for building custom images.
    
## Usage

Follow the installation steps to set up and run the webcrawler. After starting the services, the crawler will automatically begin monitoring specified dark web URLs through the Tor network, storing data in MongoDB. Redis is used for caching and managing tasks.

## Configuring Tor Instances

Each Tor container is configured to run as a separate instance, routing traffic through different Tor exit nodes. This increases anonymity and reduces the chances of IP bans.

## Scaling

You can scale the number of Tor instances by modifying the docker-compose.yml file and adding more tor-extend-* services as needed.
