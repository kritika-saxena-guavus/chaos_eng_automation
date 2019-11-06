from chaostoolkit_nimble.actions.base.flows import chaos_user_actions
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.components.hadoop_utils import HadoopCliUtils
from nimble.core.utils.components.hive_utils import HiveBeelineUtils, HivePythonClientUtils
from nimble.core.utils.multiprocessing_utils import MultiprocessingUtils


def import_data_to_hive(db_name, table_name, fileserver_path):
    hive_utils = HiveBeelineUtils() if NodeManager.node_obj.kerberized is True else HivePythonClientUtils()
    hadoop_cli_utils = HadoopCliUtils()
    hdfs_path = "/tmp/aut_squad/automation/"
    hadoop_cli_utils.remove(hdfs_path, recursive=True)
    hive_utils.drop_database(db_name)
    chaos_user_actions.send_data_to_hdfs(fileserver_path, hdfs_path)

    multiprocessing_utils = MultiprocessingUtils(1)
    multiprocessing_utils.run_method_in_parallel_async(hive_utils.restore_table,
                                                       args_list=[(db_name, table_name, hdfs_path)])
