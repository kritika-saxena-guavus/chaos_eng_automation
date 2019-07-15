from jinja2 import Environment, PackageLoader
from nimble.core import global_constants
from nimble.core.utils.file_utils import FileUtils

################### Templating
from mypackage.custom.shell_utils import ShellUtils

env = Environment(loader=PackageLoader("mypackage", "templates"))
# template = env.get_template('experiment_template.json')
template = env.get_template('process_experiment_template.json')
variables = {"remote_command_var": "echo Hi",
                "remote_ip_var": "192.168.135.36",
                "remote_username_var": "root",
                "remote_password_var": "guavus@123",
                "remote_command_timeout_var": 120,
                "remote_connection_timeout_var": 120,
                "expected_remote_command_output" : "Hi",
                "local_command_var": "ls",
                "local_command_arguments": "/tmp"
                }
# print(template.render(variables))
json_string = template.render(variables)
experiment_file_path = "%s/process_experiment.json" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
FileUtils.write_string_to_file(experiment_file_path, json_string)

################### Run experiment
experiment_output_file_path = "%s/process_output.txt" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
response_obj = ShellUtils.execute_shell_command("chaos run %s" %(experiment_file_path))
print(response_obj)
FileUtils.write_string_to_file(experiment_output_file_path, response_obj[0])
FileUtils.write_string_to_file(experiment_output_file_path, response_obj[1], write_mode="a+")



