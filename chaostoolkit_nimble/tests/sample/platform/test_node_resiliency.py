import logging

import pytest

from chaostoolkit_nimble.actions.base.flows import chaos_user_actions
from chaostoolkit_nimble.tests.conftest import OPTIONS_DICT
from nimble.actions.sample.sample_actions import SampleActions
from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.components.hadoop_utils import HadoopCliUtils
from nimble.core.utils.components.hive_utils import HiveBeelineUtils, HivePythonClientUtils
from nimble.core.utils.dynamic_substitution_utils import DynamicSubstitutionUtils

_LOGGER = logging.getLogger(__name__)


@pytest.mark.incremental
class TestNodeResiliency():
    job_alias = "hive_to_hive"
    input_db = "aut_squad_hive_db"
    input_table = "aut_squad_hive_table"

    @pytest.fixture(scope="session")
    def sample_actions(self):
        return SampleActions(self.job_alias)

    # def test_2(self):
    #     res = ambari_utils.all_services_running()
    #     pass
    #
    # def test_1(self):
    #     url = "http://192.168.134.140:8080/api/v1/clusters/testautomation-reflex-platform/request_schedules"
    #     ambari_header = {"X-Requested-By": "ambari"}
    #     auth = ("admin", "Sbe7UGkRBMF8")
    #     payload = '[{"RequestSchedule":{"batch":[{"requests":[{"order_id":1,"type":"POST","uri":"\/api\/v1\/clusters\/testautomation-reflex-platform\/requests","RequestBodyInfo":{"RequestInfo":{"context":"HDFS Service Check (batch 1 of 3)","command":"HDFS_SERVICE_CHECK"},"Requests\/resource_filters":[{"service_name":"HDFS"}]}},{"order_id":2,"type":"POST","uri":"\/api\/v1\/clusters\/testautomation-reflex-platform\/requests","RequestBodyInfo":{"RequestInfo":{"context":"YARN Service Check (batch 2 of 3)","command":"YARN_SERVICE_CHECK"},"Requests\/resource_filters":[{"service_name":"YARN"}]}},{"order_id":3,"type":"POST","uri":"\/api\/v1\/clusters\/testautomation-reflex-platform\/requests","RequestBodyInfo":{"RequestInfo":{"context":"MapReduce Service Check (batch 3 of 3)","command":"MAPREDUCE2_SERVICE_CHECK"},"Requests\/resource_filters":[{"service_name":"MAPREDUCE2"}]}}]},{"batch_settings":{"batch_separation_in_seconds":1,"task_failure_tolerance":1}}]}}]'
    #     payload = json.dumps(payload)
    #     api_request_specification = ApiRequestSpecification(request_type=RequestType.POST, url=url, auth=auth,
    #                                                         json=payload, headers=ambari_header, verify=False)
    #     # api_request_specification.set_content_type(ContentType.FORM_URLENCODED)
    #     api_request = ApiRequest()
    #     request_schedule_response = api_request.execute_request(api_request_specification)
    #     reponse = "bsajdjs"
    #     try:
    #         request_schedule_id = request_schedule_response.json()["resources"][0]["RequestSchedule"]["id"]
    #         url = "http://192.168.134.140:8080/api/v1/clusters/testautomation-reflex-platform/request_schedules/%s" % request_schedule_id
    #         api_request_specification = ApiRequestSpecification(request_type=RequestType.GET, url=url, auth=auth,
    #                                                             headers=ambari_header, verify=False)
    #         batch_request_response = api_request.execute_request(api_request_specification)
    #         running_service_check_status = batch_request_response.json()["RequestSchedule"]["status"]
    #     except KeyError:
    #         pass
    #     pass

    @pytest.fixture(scope="session")
    def hive_utils(self):
        if NodeManager.node_obj.kerberized is True:
            return HiveBeelineUtils()
        return HivePythonClientUtils()

    @pytest.fixture(scope="session")
    def hadoop_cli_utils(self):
        return HadoopCliUtils()

    @pytest.fixture(scope="session")
    def send_data_to_hive(self, user_actions, hive_utils, hadoop_cli_utils):
        hdfs_path = "/tmp/aut_squad_hive_table/"
        hadoop_cli_utils.remove(hdfs_path, recursive=True)
        hive_utils.drop_database(self.input_db)
        user_actions.send_data_to_hdfs(
            "modules/platform/validation/aut_squad_test_data/input_output_sources/hive/aut_squad_hive_db/aut_squad_hive_table/",
            hdfs_path)
        hive_utils.restore_table(self.input_db, self.input_table, hdfs_path)
        yield
        hadoop_cli_utils.remove(hdfs_path, recursive=True)
        hive_utils.drop_database(self.input_db)

    def test_node_failover(self, send_data_to_hive):
        # pylint: disable=unused-argument
        exp_template_file = OPTIONS_DICT["experimentsPath"]
        # exp_template_file = "target/artifacts/tmp/exp_templates/node_failover_exp.json"
        node_alias = NodeManager.node_obj.get_node_aliases_by_component(Components.DATANODE.name)[0]
        context = {"node_alias": node_alias}
        # chaos_user_actions.run_experiment(exp_template_file=exp_template_file, context=context)
        chaos_user_actions.run_experiment(custom_exp_template_file=OPTIONS_DICT["experimentsPath"], context=context)

    def test_validate(self, user_actions, sample_actions, send_data_to_hive):
        # pylint: disable=unused-argument
        DynamicSubstitutionUtils.add({"randynamic_db_name": self.input_db})
        DynamicSubstitutionUtils.add({"randynamic_table_name": self.input_table})
        user_actions.validate(sample_actions.validate_hive_to_hive, self.job_alias)
