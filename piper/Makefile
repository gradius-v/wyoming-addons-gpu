.PHONY: local run update gpu local-gpu run-gpu update-gpu

VERSION := 1.4.0
TAG := rhasspy/wyoming-piper
PLATFORMS := linux/amd64,linux/arm64,linux/arm/v7
DATA_DIR := ${HOME}/.local/share/wyoming/piper
VOICE := en_US-lessac-medium
HOST := 0.0.0.0
PORT := 10200

all:
	docker buildx build . --platform "$(PLATFORMS)" --tag "$(TAG):$(VERSION)" --push -f .NONGPU.Dockerfile
gpu:
	docker buildx build . --platform "$(PLATFORMS)" --tag "$(TAG):$(VERSION)-gpu" --push -f .GPU.Dockerfile

update:
	docker buildx build . --platform "$(PLATFORMS)" --tag "$(TAG):latest" --push -f .NONGPU.Dockerfile
update-gpu:
	docker buildx build . --platform "$(PLATFORMS)" --tag "$(TAG):latest-gpu" --push -f .GPU.Dockerfile

local:
	docker build . -t "$(TAG):$(VERSION)" -f .NONGPU.Dockerfile --build-arg TARGETARCH=amd64
local-gpu:
	docker build . -t "$(TAG):$(VERSION)" -f .GPU.Dockerfile --build-arg TARGETARCH=amd64

run:
	mkdir -p "$(DATA_DIR)"
	docker run -it -p '$(PORT):$(PORT)' -v "$(DATA_DIR):/data"  "$(TAG):$(VERSION)" --voice "$(VOICE)" --uri 'tcp://$(HOST):$(PORT)' --debug
run-gpu:
	mkdir -p "$(DATA_DIR)"
	docker run -it --gpus all -p '$(PORT):$(PORT)' -v "$(DATA_DIR):/data"  "$(TAG):$(VERSION)" --voice "$(VOICE)" --uri 'tcp://$(HOST):$(PORT)' --cuda --debug