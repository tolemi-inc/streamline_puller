all:build-image

build-image:
	podman manifest rm streamline-puller:latest
	podman build --jobs=2 --platform=linux/amd64,linux/arm64 --manifest streamline-puller:latest .