#!/usr/bin/env python
import newrelic.agent
import sys  # noqa

if "prompt_steam_guard" in sys.argv:
    from gevent import monkey

    monkey.patch_all()

import os  # noqa

from pathlib import Path  # noqa


def configure_logging():
    import logging.config

    from django.conf import settings

    logging.config.dictConfig(settings.LOGGING)


if __name__ == "__main__":
    if "NEW_RELIC_CONFIG_FILE" in os.environ:
        print("Enabling New Relic integration...")
        print(
            f"Config: {os.environ['NEW_RELIC_CONFIG_FILE']}, Env: {os.environ['NEW_RELIC_ENVIRONMENT']}"
        )
        newrelic.agent.initialize()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

    try:
        from django.core.management import execute_from_command_line
        from django.conf import settings
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django  # noqa
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )

        raise

    # This allows easy placement of apps within the interior
    # boundlexx directory.
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path / "boundlexx"))

    configure_logging()

    if settings.DEBUG:
        import environ

        env = environ.Env()

        if env.bool("REMOTE_DEBUGGING") and (
            os.environ.get("RUN_MAIN") or os.environ.get("WERKZEUG_RUN_MAIN")
        ):
            import ptvsd
            import logging

            logger = logging.getLogger("django")

            ptvsd.enable_attach(address=("127.0.0.1", 3000))
            logger.info("VS Code Remote debugger running on 127.0.0.1:3000")

    execute_from_command_line(sys.argv)
