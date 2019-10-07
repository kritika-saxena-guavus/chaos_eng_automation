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

    def test_validate_pre_chaos(self, user_actions, sample_actions, send_data_to_hive):
        # pylint: disable=unused-argument
        DynamicSubstitutionUtils.add({"randynamic_db_name": self.input_db})
        DynamicSubstitutionUtils.add({"randynamic_table_name": self.input_table})
        user_actions.validate(sample_actions.validate_hive_to_hive, self.job_alias)

    def test_node_failover(self, send_data_to_hive):
        # pylint: disable=unused-argument
        exp_template_file = OPTIONS_DICT["experimentsPath"]
        # exp_template_file = "target/artifacts/tmp/exp_templates/node_failover_exp.json"
        node_alias = NodeManager.node_obj.get_node_aliases_by_component(Components.DATANODE.name)[0]
        context = {"node_alias": node_alias}
        # chaos_user_actions.run_experiment(exp_template_file=exp_template_file, context=context)
        chaos_user_actions.run_experiment(custom_exp_template_file=OPTIONS_DICT["experimentsPath"], context=context)

    def test_validate_post_chaos(self, user_actions, sample_actions, send_data_to_hive):
        # pylint: disable=unused-argument
        DynamicSubstitutionUtils.add({"randynamic_db_name": self.input_db})
        DynamicSubstitutionUtils.add({"randynamic_table_name": self.input_table})
        user_actions.validate(sample_actions.validate_hive_to_hive, self.job_alias, dataset_alias="dataset2")
