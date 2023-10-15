# -*- coding: utf-8 -*-
import logging
import logging.config

import structlog
from bitmapist import SYSTEMS
from flask import Flask, Response, request
from flask_request_id import RequestID
from flask_security.datastore import SQLAlchemyUserDatastore
from redis import StrictRedis

from flask_foundation import config, extensions, loggers, utils
from flask_foundation.db.sessions import db_session


def create_app(custom_settings: dict = None) -> Flask:
    setup_logging()
    setup_bitmapist()

    app = Flask(__name__, instance_relative_config=True)
    RequestID(app=app, generator_func=utils.generate_uuid_string)

    # other settings
    cache_redis_url = (
        config.settings.default.get("CACHE_REDIS_URL")
        or config.settings.default.REDIS_URL
    )
    session_redis_url = (
        config.settings.default.get("SESSION_REDIS_URL")
        or config.settings.default.REDIS_URL
    )
    additional_settings = {
        "CACHE_REDIS_URL": cache_redis_url,
        "CACHE_TYPE": "RedisCache",
        "SESSION_TYPE": "redis",
        "SESSION_REDIS": StrictRedis.from_url(session_redis_url),
        "SESSION_USE_SIGNER": True,
    }
    # NOTE: hack. for some reason, some values don't make it into
    # the FlaskDynaconf instance, for example, SQLALCHEMY_DATABASE_URI
    additional_settings.update(config.settings.default.to_dict())

    # override settings
    override_settings = custom_settings.copy() if custom_settings else {}
    override_settings.update(additional_settings)
    app.config.from_mapping(override_settings)

    # set up extensions
    setup_extensions(app)

    logger = structlog.get_logger()

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_error_logger.handlers[:]

    @app.after_request
    def log_after_request(response: Response) -> Response:
        request_id = request.environ.get("FLASK_REQUEST_ID")
        logger.info(
            message="request complete",
            request_id=request_id,
            url=request.url,
            response={
                "status": response.status,
                "status_code": response.status_code,
            },
        )

        return response

    @app.teardown_request
    def teardown_session(exception: Exception = None):
        db_session.remove()

    return app


def setup_bitmapist(system_name: str = None) -> None:
    system_name = system_name or config.settings.default.BITMAPIST_SYSTEM_NAME
    bitmapist_redis_url = config.settings.default.BITMAPIST_REDIS_URL
    system_redis_url = config.settings.default.REDIS_URL
    SYSTEMS[system_name] = StrictRedis.from_url(
        bitmapist_redis_url or system_redis_url
    )


def setup_logging() -> None:
    timestamper = structlog.processors.TimeStamper(
        fmt=config.settings.default.LOG_TIMESTAMP_FORMAT
    )
    pre_chain = [
        loggers.add_app_name,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(colors=False),
                    "foreign_pre_chain": pre_chain,
                },
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "development": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "console",
                },
                "production": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                },
            },
            "loggers": {"": {"level": "DEBUG", "propagate": True}},
        }
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            loggers.add_app_name,
            loggers.combined_logformat,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(
                fmt=config.settings.default.LOG_TIMESTAMP_FORMAT
            ),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def setup_extensions(app: Flask) -> None:
    from flask_foundation.auth.models import Role, User

    extensions.cors.init_app(app)
    extensions.cache.init_app(app)
    extensions.csrf.init_app(app)
    extensions.db.init_app(app)
    if app.debug and extensions.debug_toolbar:
        extensions.debug_toolbar.init_app(app)
    extensions.mail.init_app(app)

    datastore = SQLAlchemyUserDatastore(extensions.db, User, Role)
    # register the security blueprint if you need it
    extensions.security.init_app(app, datastore, False)
    extensions.talisman.init_app(app)
