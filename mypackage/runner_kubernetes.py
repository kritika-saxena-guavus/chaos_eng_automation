from jinja2 import Environment, PackageLoader
from nimble.core import global_constants
from nimble.core.utils.file_utils import FileUtils
from mypackage.custom.shell_utils import ShellUtils


################### Templating
env = Environment(loader=PackageLoader("mypackage", "templates"))
# template = env.get_template('experiment_template.json')
template = env.get_template('kubernetes_experiment_template.json')
variables = {"pod_name": "elasticsearch-pipeline-coordinator",
                    "pod_ns_var": "kube-system",
                    "pod_label_selector_var": "component=elasticsearch-pipeline,controller-revision-hash=739463158,pod-template-generation=1,role=coordinator-node",
                    "service_name": "elasticsearch-pipeline-rest",
                    "service_ns_var": "kube-system",
                    "service_label_selector_var": "component=elasticsearch-pipeline-rest,role=coordinator-node"
                    }
json_string = template.render(variables)
experiment_file_path = "%s/kubernetes_experiment.json" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
FileUtils.write_string_to_file(experiment_file_path, json_string)

################### Run experiment
experiment_output_file_path = "%s/kubernetes_output.txt" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
response_obj = ShellUtils.execute_shell_command("chaos run %s" %(experiment_file_path))
print(response_obj)
FileUtils.write_string_to_file(experiment_output_file_path, response_obj[0])
FileUtils.write_string_to_file(experiment_output_file_path, response_obj[1], write_mode="a+")



