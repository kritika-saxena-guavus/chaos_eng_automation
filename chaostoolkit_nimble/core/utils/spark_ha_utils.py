import random

from logzero import logger
from retrying import RetryError

from chaostoolkit_nimble.controllers.application.spark import control
from chaostoolkit_nimble.core.exceptions.custom_exceptions import ChaosActionFailedError
from nimble.core.adapters.hadoop.base_hadoop_adapter import ApplicationState
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.components.hadoop_utils import HadoopRestClientUtils
from nimble.core.utils.components.spark_utils import SparkRestClientUtils
from nimble.core.utils.shell_utils import ShellUtils


def get_driver_and_executors(job_name):
    hadoop_rest_client_utils = HadoopRestClientUtils()
    spark_client_utils = SparkRestClientUtils()
    try:
        logger.info("Fetching yarn application id for the running job %s." % job_name)
        control.APPLICATION_ID = hadoop_rest_client_utils.get_yarn_most_recent_application_id_by_job_name(job_name,
                                                                                                          state=ApplicationState.RUNNING.value)
    except RetryError:
        raise ChaosActionFailedError(
            "Could not fetch yarn application id for job %s. Job not found in '%s' state" % (
                job_name, ApplicationState.RUNNING.value))
    try:
        logger.info("Fetching spark active executors for application id: %s" % control.APPLICATION_ID)
        return spark_client_utils.get_application_active_executors(control.APPLICATION_ID)
    except RetryError:
        raise ChaosActionFailedError(
            "Could not fetch spark executors for the application id: %s" % control.APPLICATION_ID)


def get_executors(job_name):
    executors = get_driver_and_executors(job_name)
    for i in range(len(executors)):
        if executors[i]["id"] == "driver":
            executors.pop(i)
            break
    return executors


def get_random_num_executors(job_name, num_of_exec=1):
    executors = get_executors(job_name)
    return random.sample(executors, int(num_of_exec))


def get_driver(job_name):
    driver = get_driver_and_executors(job_name)
    for i in range(len(driver)):
        if driver[i]["id"] != "driver":
            driver.pop(i)
            break
    return driver


def kill_active_executors(job_name, num_of_exec=1):
    executors = get_random_num_executors(job_name, num_of_exec=num_of_exec)
    response_list = []
    for executor in executors:
        executor_id = executor["id"]
        node_hostname_domain = executor["hostPort"].split(":")[0]
        logger.debug("Killing spark executor id %s on node %s" % (executor_id, node_hostname_domain))
        response = NodeManager.node_obj.execute_command_on_hostname_domain(node_hostname_domain,
                                                                           ShellUtils.kill_process_by_name("spark",
                                                                                                           pipe_command='grep -i "executor-id %s"' % executor_id))
        if "kill -9 " not in response.stdout:
            raise ChaosActionFailedError(
                "Could not kill process with spark executor id %s on node %s" % (executor_id, node_hostname_domain))
        response_list.append(response)
    return str(response_list)


def kill_driver(job_name):
    driver = get_driver(job_name)
    node_hostname_domain = driver["hostPort"].split(":")[0]
    logger.debug("Killing spark driver on node %s" % node_hostname_domain)
    response = NodeManager.node_obj.execute_command_on_hostname_domain(node_hostname_domain,
                                                                       ShellUtils.kill_process_by_name("spark",
                                                                                                       pipe_command='grep -i %s' % control.APPLICATION_ID))
    if "kill -9 " not in response.stdout:
        raise ChaosActionFailedError(
            "Could not kill spark driver process on node %s" % node_hostname_domain)
    return str(response)
