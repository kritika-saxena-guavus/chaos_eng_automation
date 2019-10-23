from nimble.core.utils.components.ambari_utils import AmbariUtils


def are_all_services_running():
    ambari_utils = AmbariUtils()
    return ambari_utils.are_all_services_running()
