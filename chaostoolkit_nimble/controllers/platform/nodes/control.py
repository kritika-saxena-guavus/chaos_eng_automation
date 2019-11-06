from typing import List

from chaoslib.types import Configuration, \
    Experiment, Run, Secrets
from logzero import logger
from retrying import RetryError

from chaostoolkit_nimble.controllers.base import control
from chaostoolkit_nimble.core.utils.node_ha_utils import wait_for_node_to_be_pingable
from nimble.core.utils.components.ambari_utils import AmbariUtils

control.configure_control()


def after_method_control(context: Experiment, state: List[Run],
                         configuration: Configuration = None,
                         secrets: Secrets = None, **kwargs):
    """
    after-control of the method's execution

    Called by the Chaos Toolkit after the activities of the method have been
    applied. The `state` is the list of activity results. See
    https://docs.chaostoolkit.org/reference/api/journal/#run for more
    information.
    """
    logger.debug("----------------STATE AFTER METHOD:  %s" % state)
    for run in state:
        activity_obj = run["activity"]
        activity_name = activity_obj["name"]
        run_status = run["status"]
        node_alias = activity_obj["provider"]["arguments"]["node_alias"]
        if "Reboot" in activity_name and run_status == "succeeded":
            ambari_utils = AmbariUtils()
            try:
                logger.info("Waiting for node to become pingable...")
                wait_for_node_to_be_pingable(node_alias)
                logger.info("Waiting for all ambari services to come up ...")
                ambari_utils.wait_for_services_to_come_up()
            except RetryError:
                pass
