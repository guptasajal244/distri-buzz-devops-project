# Distri-Buzz: A Distributed Event Notification System

This project demonstrates a robust, multi-service application architecture orchestrated entirely using Docker and Docker Compose. It showcases a modern DevOps approach to deploying and managing complex systems.

## Overview

Distri-Buzz simulates a simplified event management and notification system built with Python Flask microservices, PostgreSQL for data storage, RabbitMQ for asynchronous messaging, and Nginx as an API Gateway.

**Key Architectural Features:**

* **Frontend (Nginx + Static HTML/JS):** A simple web interface for interacting with the backend APIs.
* **API Gateway (Nginx):** Single entry point routing requests to different microservices.
* **Event Service (Python/Flask):** Manages event creation and listing, publishes new event notifications to RabbitMQ.
* **User Service (Python/Flask):** Manages user registration and listing, interacts with PostgreSQL.
* **Notifier Service (Python/Flask):** Consumes event notifications from RabbitMQ and simulates sending them.
* **PostgreSQL:** Relational database for persistent storage of users and events.
* **RabbitMQ:** Message broker enabling asynchronous, decoupled communication between services.
* **Redis:** A high-performance in-memory data store, included for future caching or session management (currently integrated but not fully utilized by app logic, demonstrating readiness).

## Why This Project Demonstrates Strong DevOps Skills

My focus in building Distri-Buzz was exclusively on the **DevOps aspects** of containerization, orchestration, and infrastructure management. This project highlights my ability to:

* **Design and implement a multi-microservice architecture:** Orchestrating 6+ interconnected containers.
* **Master Docker Compose:** Defining custom networks, persistent volumes, environment variables, health checks, and service dependencies for complex applications.
* **Implement asynchronous communication patterns:** Integrating RabbitMQ demonstrates proficiency with message brokers for scalable, fault-tolerant systems.
* **Manage diverse data stores:** Working with both PostgreSQL (relational) and Redis (key-value/cache).
* **Utilize an API Gateway (Nginx):** For efficient request routing and frontend serving.
* **Build optimized Docker Images:** Employing multi-stage builds for lean and efficient service images.
* **Troubleshoot and ensure service health:** Configuring robust health checks and understanding container logs for debugging.

While the application logic in each microservice is intentionally minimal—serving primarily to enable the infrastructure and demonstrate communication flows—this project showcases my practical skills in building, deploying, and managing a truly distributed, containerized environment from scratch.

## Getting Started

Follow these steps to set up and run Distri-Buzz locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/guptasajal244/distri-buzz-devops-project.git
    cd distri-buzz
    ```
2.  **Create your `.env` file:**
    Copy the `.env` content provided in this README to your project's `.env` file.
    ```bash
    cp .env.example .env 
    ```
3.  **Build and Run with Docker Compose:**
    ```bash
    docker compose up --build -d
    ```
    * `--build`: Ensures your service images are rebuilt with any code changes.
    * `-d`: Runs the containers in detached mode (in the background).

4.  **Access the Application:**
    Open your web browser and navigate to:
    * **Frontend Dashboard:** `http://localhost/`
    * **RabbitMQ Management UI:** `http://localhost:15672/` (Login with `guest`/`guest` from `.env`)

5.  **Test Functionality:**
    * On the frontend, try **registering users** and **creating events**.
    * Observe your terminal where `docker compose logs -f notifier_service` is running – you should see the notifier service picking up messages for new events.
    * Check the "Fetch All Users" and "Fetch All Events" buttons.
    * Explore the RabbitMQ Management UI to see queues and messages.

## Stopping the Application

To stop and remove all containers, networks, and volumes (useful for a clean restart):
```bash
docker compose down -v
