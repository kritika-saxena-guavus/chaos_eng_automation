from retrying import RetryError

from nimble.core.utils.components.ambari_utils import AmbariUtils


def are_all_services_running():
    ambari_utils = AmbariUtils()
    try:
        return ambari_utils.wait_for_services_to_come_up()
    except RetryError:
        return False
