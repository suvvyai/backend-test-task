.PHONY: help run test format db-up

# Имя Docker контейнера для MongoDB
MONGO_CONTAINER_NAME := my-mongodb

# Основные команды

default: help

help:
	@echo "Makefile for the FastAPI Chatbot Application"
	@echo "-------------------------------------------"
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  run        Run the FastAPI application (using 'uv run app')."
	@echo "  test       Run all tests (using 'uv run pytest')."
	@echo "  format     Automatically format all code with ruff and black."
	@echo "  db-up      Start the MongoDB container using 'docker run'."
	@echo "  db-down    Stop and remove the MongoDB container."


run:
	@echo ">>> Starting FastAPI application with 'uv run app'..."
	uv run app

test:
	@echo ">>> Running tests with 'uv run pytest'..."
	uv run pytest

format:
	@echo ">>> Auto-fixing issues with Ruff..."
	uv run ruff check . --fix
	@echo "\n>>> Auto-formatting code with Black..."
	uv run black .

# Команды для управления MongoDB

db-up:
	@echo ">>> Starting MongoDB container '$(MONGO_CONTAINER_NAME)'..."
	@if [ $$(docker ps -q -f name=$(MONGO_CONTAINER_NAME)) ]; then \
		echo "Container '$(MONGO_CONTAINER_NAME)' is already running."; \
	elif [ $$(docker ps -aq -f status=exited -f name=$(MONGO_CONTAINER_NAME)) ]; then \
		echo "Restarting existing container '$(MONGO_CONTAINER_NAME)'..."; \
		docker start $(MONGO_CONTAINER_NAME); \
	else \
		echo "Creating and starting new container '$(MONGO_CONTAINER_NAME)'..."; \
		docker run -d --name $(MONGO_CONTAINER_NAME) -p 27017:27017 mongo; \
	fi

db-down:
	@echo ">>> Stopping and removing MongoDB container '$(MONGO_CONTAINER_NAME)'..."
	@if [ $$(docker ps -q -f name=$(MONGO_CONTAINER_NAME)) ]; then \
		docker stop $(MONGO_CONTAINER_NAME) && docker rm $(MONGO_CONTAINER_NAME); \
	elif [ $$(docker ps -aq -f name=$(MONGO_CONTAINER_NAME)) ]; then \
		docker rm $(MONGO_CONTAINER_NAME); \
	else \
		echo "Container '$(MONGO_CONTAINER_NAME)' not found."; \
	fi