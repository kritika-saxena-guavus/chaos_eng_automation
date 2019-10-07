from logzero import logger
from retrying import retry, RetryError

from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils

NODE_PING_TIMEOUT = 90000


def _query_node_status(result):
    return not result


def is_node_up_and_running(node_alias):
    try:
        return ping_node(node_alias)
    except RetryError:
        return False


@retry(stop_max_delay=NODE_PING_TIMEOUT, wait_fixed=5000, retry_on_result=_query_node_status)
def ping_node(node_alias):
    node_hostname_domain = NodeManager.node_obj.get_node_hostname_domain_by_alias(node_alias)
    command = ShellUtils.ping(node_hostname_domain, count=5)
    logger.info("Executing command: %s" % command)
    response = ShellUtils.execute_shell_command(command).stdout
    logger.debug(response)
    return not "Request timeout" in response


def reboot_node(node_alias):
    return str(NodeManager.node_obj.execute_command_on_node(node_alias, "echo Hi"))
    # return str(NodeManager.node_obj.execute_command_on_node(node_alias, ShellUtils.reboot(force=True)))
