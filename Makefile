all:build-image

build-image:
	podman build  --jobs=2 --platform=linux/amd64 -t streamline-puller:latest-amd64 .
	podman build  --jobs=2 --platform=linux/arm64 -t streamline-puller:latest-arm64 .
	podman manifest rm streamline-puller:latest || true
	podman manifest create streamline-puller:latest
	podman manifest add --arch amd64 streamline-puller:latest streamline-puller:latest-amd64
	podman manifest add --arch arm64 streamline-puller:latest streamline-puller:latest-arm64

deploy:
	aws ecr get-login-password --region us-east-1 | podman login --username AWS --password-stdin 993874376304.dkr.ecr.us-east-1.amazonaws.com/pullers/streamline-puller
	podman manifest push --all streamline-puller:latest 993874376304.dkr.ecr.us-east-1.amazonaws.com/pullers/streamline-puller:latest
