pytest:
	poetry run pytest

format:
	poetry run black -l 79 --target-version py310 .

sort-imports:
	poetry run isort --profile black --multi-line 3 .

lint: sort-imports format

pre-commit:
	poetry run pre-commit run --all-files

devserver:
	FLASK_DEBUG=1 poetry run flask --app flask_foundation.webapp --debug run

prodserver:
	poetry run gunicorn -c gunicorn.conf.py --log-config gunicorn_logging.conf flask_foundation.webapp:app

shell:
	poetry run flask --app flask_foundation.webapp shell
