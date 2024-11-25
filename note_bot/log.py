import logging
import logging.config

_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'logfile_formatter': {
            'format': '%(asctime)s %(levelname)s [%(name)s] %(message)s'
        }
    },
    'handlers': {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "logfile_formatter",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        'logfile_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'logfile_formatter',
            'level': 'INFO',
            'filename': 'server.log',
            'maxBytes': 50 * 1024 * 1024,
            'backupCount': 10
        }
    },
    'root': {
        'handlers': ['logfile_handler', 'console'],
        'level': 'INFO'
    },
    'loggers': {
        'azure.core.pipeline.policies.http_logging_policy': {
            'level': 'WARNING'
        }
    }
}


def setup_logger():
    logging.config.dictConfig(_LOGGING_CONFIG)