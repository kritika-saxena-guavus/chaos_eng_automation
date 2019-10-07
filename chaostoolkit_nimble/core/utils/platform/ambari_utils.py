from logzero import logger

from nimble.core.utils.components.ambari_utils import AmbariUtils, ServiceStatus


def are_services_running():
    ambari_utils = AmbariUtils()
    service_status_mapping = {}
    services = ambari_utils.get_all_services()
    for service in services:
        service_name = service["ServiceInfo"]["service_name"]
        service_state = ambari_utils.get_service_state(service_name)
        service_status_mapping.update({service_name: service_state == ServiceStatus.STARTED.value})
    logger.debug("Service status mapping: %s" % service_status_mapping)
    return all(service_status_mapping.values())
