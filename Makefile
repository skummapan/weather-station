REGESTRY:=docker.skumble.net
IMAGE_NAME?=weather-station
TAG?=0.1

IMAGE_TAG:=$(REGESTRY)/$(IMAGE_NAME):$(TAG)

image:
	docker build -t $(IMAGE_TAG) .

push: image
	docker push $(IMAGE_TAG)

start: image
	docker compose up -d

stop:
	docker compose down
