import enum

from crawler.crawler_services.redis_manager.redis_enums import REDIS_CONNECTIONS


class CELERY_CONNECTIONS:
  conn = f"redis://:{REDIS_CONNECTIONS.S_DATABASE_PASSWORD}@{REDIS_CONNECTIONS.S_DATABASE_IP}:{REDIS_CONNECTIONS.S_DATABASE_PORT}/0"


class CELERY_COMMANDS(enum.Enum):
  S_START_CRAWLER = 1
  S_INVOKE_UNIQUE_CRAWLER = 2


class ELASTIC_LOGGING:
  logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
      'default': {
        'format': '[%(asctime)s: %(levelname)s/%(name)s] %(message)s',
      },
    },
    'handlers': {
      'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'default',
      },
    },
    'loggers': {
      '': {  # root logger
        'level': 'DEBUG',
        'handlers': ['console'],
      },
      'celery': {
        'level': 'WARNING',  # Suppress Celery's internal INFO and DEBUG logs
        'handlers': ['console'],
        'propagate': False,
      },
      'celery.worker.strategy': {
        'level': 'WARNING',  # Suppress Celery worker strategy logs
        'handlers': ['console'],
        'propagate': False,
      },
      'kombu': {
        'level': 'WARNING',  # Suppress Kombu logs (Celery's messaging library)
        'handlers': ['console'],
        'propagate': False,
      },
      'pymongo': {
        'level': 'WARNING',  # Suppress pymongo logs
        'handlers': ['console'],
        'propagate': False,
      },
      'urllib3': {
        'level': 'WARNING',  # Suppress urllib3 logs
        'handlers': ['console'],
        'propagate': False,
      }
    },
  }
