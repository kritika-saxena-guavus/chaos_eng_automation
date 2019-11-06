from time import sleep

from chaoslib.types import Configuration, \
    Secrets, Activity
from logzero import logger

from chaostoolkit_nimble.controllers.base import control

control.configure_control()


def before_activity_control(context: Activity,
                            configuration: Configuration = None,
                            secrets: Secrets = None, **kwargs):
    """
    before-control of the activity's execution

    Called by the Chaos Toolkit before the activity is applied.
    """
    logger.debug("----------------CONTEXT BEFORE ACTIVITY %s:" % context)
    if "Reboot" in context["name"]:
        logger.debug("Sleeping for 10s before node reboot happens")
        sleep(10)
        logger.debug("Sleep finished")
