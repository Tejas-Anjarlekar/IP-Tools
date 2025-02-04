# Define the image name for the test container
IMAGE_NAME = ip-tool-test-image
# Define the image name for the script container
SCRIPT_IMAGE_NAME = ip-tool-image


run-test: clean build test clean
run-iptool-script: build-script run-script clean

.PHONY: build test clean

build:
	docker build -t ${IMAGE_NAME} -f Dockerfile.test .

test:
	docker run --rm ${IMAGE_NAME}

clean:
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build-script:
	docker build -t ${SCRIPT_IMAGE_NAME} .

# Run the container for the ip-tool script, passing the file for collision check
run-script:
	@if [ -n "${FILE}" ]; then \
		echo "Running with --check-collision ${FILE}..."; \
		docker run --rm ${SCRIPT_IMAGE_NAME} python3 /app/ip_tools.py --check-collision ${FILE}; \
	else \
		echo "Running without --check-collision..."; \
		docker run --rm ${SCRIPT_IMAGE_NAME}; \
	fi
