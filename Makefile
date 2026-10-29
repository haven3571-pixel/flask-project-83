install:
	uv sync
	npm ci
dev:
	uv run flask --debug --app page_analyzer:app run
setup: install build-css
PORT ?= 8080
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
build:
	./build.sh
render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
build-css:
	npm run build:css