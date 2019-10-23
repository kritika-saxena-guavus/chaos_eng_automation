from logzero import logger
from retrying import retry

from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils

NODE_PING_TIMEOUT = 90000


def _query_node_status(result):
    return not result


def is_node_up_and_running(node_alias):
    node_hostname_domain = NodeManager.node_obj.get_node_hostname_domain_by_alias(node_alias)
    command = ShellUtils.ping(node_hostname_domain, count=5)
    logger.info("Executing command: %s" % command)
    response = ShellUtils.execute_shell_command(command).stdout
    logger.debug(response)
    return not "Request timeout" in response


@retry(stop_max_delay=NODE_PING_TIMEOUT, wait_fixed=5000, retry_on_result=_query_node_status)
def wait_for_node_to_be_pingable(node_alias):
    return is_node_up_and_running(node_alias)


def reboot_node(node_alias):
    node_ip = NodeManager.node_obj.get_node_ip_by_alias(node_alias)
    username = NodeManager.node_obj.nodes[node_alias].username
    password = NodeManager.node_obj.nodes[node_alias].password
    command = 'nohup sshpass -p "%s" ssh %s@%s %s' % (password, username, node_ip, ShellUtils.reboot(force=True))
    mgmt_node = NodeManager.node_obj.get_node_aliases_by_component(Components.MANAGEMENT.name)[0]
    logger.info("Executing command on node %s: %s" % (mgmt_node, command))
    return NodeManager.node_obj.execute_remote_command_in_bg(mgmt_node, command)
