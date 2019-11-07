from time import sleep

from chaoslib.types import Configuration, \
    Experiment, Secrets
from logzero import logger

from chaostoolkit_nimble.controllers.base import control

control.configure_control()


def before_method_control(context: Experiment,
                          configuration: Configuration = None,
                          secrets: Secrets = None, **kwargs):
    """
    before-control of the method's execution

    Called by the Chaos Toolkit before the activities of the method are
    applied.
    """
    logger.debug("----------------CONFIGURATION BEFORE METHOD:  %s" % configuration)
    sleep(3)


def after_method_control(context: Experiment,
                         configuration: Configuration = None,
                         secrets: Secrets = None, **kwargs):
    """
    before-control of the method's execution

    Called by the Chaos Toolkit before the activities of the method are
    applied.
    """
    logger.debug("----------------CONFIGURATION AFTER METHOD:  %s" % configuration)
    sleep(120)
