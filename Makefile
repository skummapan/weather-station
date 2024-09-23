IMAGE_NAME?=weather-station
TAG?=0.1

build-docker:
	docker build -t $(IMAGE_NAME):$(TAG) .

start: build-docker
	docker run $(IMAGE_NAME):$(TAG)