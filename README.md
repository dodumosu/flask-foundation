# flask-foundation
This is meant to be a base for building applications.

The Python environment is managed by Poetry, and there's a makefile for some common tasks.

Gunicorn is included.

Included Flask extensions:
- flask-caching, configured to use Redis
- flask-cors
- flask-db (includes flask-sqlalchemy)
- flask-security-too (includes flask-login, flask-mailman, flask-wtf)
- flask-session, configured to use Redis
- flask-talisman

Configuration is managed using Dynaconf, but specifically uses the TOML format in this case.

The project has some existing pre-commit hooks set up.
