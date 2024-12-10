[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a1f302d35c0f4f8c9293acabc5086512)](https://app.codacy.com/gh/msmannan00/Orion-Search/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
![CodeQL Analysis](https://github.com/msmannan00/Orion-Crawler/actions/workflows/github-code-scanning/codeql/badge.svg)

![homepage](https://github.com/user-attachments/assets/37fcf444-40be-46c9-8bd8-45a22d824141)

# Orion Crawler
<table>
<tr>
<td>
<br>
This repository hosts a powerful web crawler specifically designed for monitoring activities on the hidden web. It leverages Docker Compose to seamlessly orchestrate multiple services, including MongoDB for data storage, Redis for caching and task management, and multiple Tor containers to ensure robust anonymity and secure communication. This setup provides a scalable and efficient framework for collecting and analyzing hidden web data while prioritizing privacy and security.<br>
<br>
</td>
</tr>
<br>
<tr>
<td>
<br>

**1. Docker-Based Deployment**: Quick setup and deployment using Docker.

**2. Advanced Search Functionality**: Provides comprehensive search capabilities with various filters and options to refine search results.

**3. Data Visualization**: Generates visual representations of the data, making it easier to analyze search results.

**4. Customizable Search Parsers**: Allows for integrating custom parsers to refine data extraction from specific websites.

**5. Integrated Machine Learning Models**: Incorporates NLP and machine learning models to provide search relevance, content categorization, and detection of specific data patterns.
<br><br>
</td>
</tr>
</table>

## Prerequisites

Ensure you have the following installed on your system:
- [Python]([https://www.rust-lang.org/tools/install](https://github.com/python))
- [Docker]([https://nodejs.org/](https://github.com/docker))
- [Docker Compose]([https://github.com/docker/compose])

## Installation

### Step 1: Clone Repository

```
git clone https://github.com/yourusername/hidden-web-monitoring-webcrawler.git
cd hidden-web-monitoring-webcrawler
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
- Navigate to the Orion-Crawler/app/ directory.
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
