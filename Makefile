all:build-image

build-image:
	podman build --jobs=2 --platform=linux/amd64,linux/arm64 --manifest streamline:latest .