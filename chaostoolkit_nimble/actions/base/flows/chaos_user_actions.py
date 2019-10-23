import re

import allure
import jinja2
from logzero import logger

from nimble.actions.base.regression.regression_actions import RegressionActions
from nimble.core import global_constants
from nimble.core.utils.file_server_utils import FileServerUtils
from nimble.core.utils.shell_utils import ShellUtils

EXPERIMENTS_BASE_PATH = "%s/tmp/experiments/" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
ShellUtils.execute_shell_command(ShellUtils.remove_and_create_directory(EXPERIMENTS_BASE_PATH))
regression_actions = RegressionActions()
USER_ACTIONS = None


def run_experiment(custom_exp_template_file=None, exp_template_file=None, context=None):
    status = None
    file_server_utils = FileServerUtils()
    journal_path = "%s/journal.json" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
    template_base_dir = "%s/tmp/exp_templates/" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
    ShellUtils.execute_shell_command(ShellUtils.remove_and_create_directory(template_base_dir))
    if custom_exp_template_file:
        ShellUtils.execute_shell_command(ShellUtils.copy(custom_exp_template_file, template_base_dir))
        template_file_name = custom_exp_template_file.rsplit("/", 1)[1]
    else:
        file_server_utils.download(exp_template_file, path_to_download=template_base_dir)
        template_file_name = exp_template_file.rsplit("/", 1)[1]
    render_template(template_base_dir, template_file_name, context=context)
    experiment_file = "%s/%s" % (EXPERIMENTS_BASE_PATH, template_file_name)
    response = ShellUtils.execute_shell_command("chaos run --journal-path %s %s" % (journal_path, experiment_file))
    status = re.search(r'.*Experiment\sended\swith\sstatus:\s(.*)', response.stderr).group(1)
    html_report_path = generate_html(journal_path)
    allure.attach.file(html_report_path, name='Chaos experiment html report',
                       attachment_type=allure.attachment_type.HTML)
    assert status == "completed"


def render_template(template_base_dir, template_file_name, context):
    templateLoader = jinja2.FileSystemLoader(searchpath=template_base_dir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file_name)
    logger.info('Rendering from template: %s' % template.name)
    template.stream(context).dump('%s/%s' % (EXPERIMENTS_BASE_PATH, template_file_name))


def generate_html(journal_path):
    html_report_path = "%s/chaos_report.html" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
    command = "export LC_ALL=en_US.UTF-8 && chaos report --export-format=html5 %s %s" % (
        journal_path, html_report_path)
    ShellUtils.execute_shell_command(command)
    return html_report_path


def regress(expected_file_server_path, entity_alias, output_alias,
            dataset_alias=global_constants.DEFAULT_DATASET_ALIAS, callable_=None, transfer_to_file_server=False,
            actual_file_server_path=None, sort=False, headers=False, actual_output=None, **kwargs):
    """Regress the expected golden output from the file server with the captured actual output.

    :param expected_file_server_path: The path on the file server where expected data is present.
    :type expected_file_server_path: str
    :param actual_output: Actual output that is captured to be written to the file. If not given then it is assumed
        that user has already dumped the actual output in this standard directory structure:
        `target/artifacts/actual/<entity_alias>/<output_alias>/<dataset_alias>/output.txt`
    :type actual_output: python object
    :param entity_alias: Entity alias for which the expected output is to be regressed with actual output.
    :type entity_alias: str
    :param output_alias: Output alias for which the expected output is to be regressed with actual output.
    :type output_alias: str
    :param dataset_alias: Dataset alias for which the expected output is to be regressed with actual output.
    :type dataset_alias: str
    :param callable_: Method to be executed to transform the actual output. This method should return the transformed
        actual output.
    :type callable_: :class:`typing.Callable`
    :param transfer_to_file_server: If `True`, the actual output will be transferred to the file server. Defaults to
        `False`.
    :type transfer_to_file_server: bool
    :param actual_file_server_path: The path on the file server where actual data is to be uploaded.
    :type actual_file_server_path: str
    :param sort: If `True`, the expected and actual output files will be sorted before the diff else `False`.
        Defaults to `False`.
    :type sort: bool
    :param headers: `True` if the expected and actual files contain headers. Defaults to `False`.
    :type headers: bool
    """
    regression_actions.dump_expected_output_from_fileserver(expected_file_server_path, entity_alias, output_alias,
                                                            dataset_alias=dataset_alias)
    if actual_output:
        if callable_:
            actual_output = callable_(actual_output, **kwargs)
        regression_actions.dump_actual_output(actual_output, entity_alias, output_alias, dataset_alias=dataset_alias)
    local_base_path = "%s/actual/%s/%s/%s/" % (
        global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH, entity_alias, output_alias, dataset_alias)
    regression_actions.actual_output_file_name = "%s/%s" % (local_base_path, regression_actions.output_file_name)

    try:
        regression_actions.compare_outputs(sort=sort, headers=headers)
        if transfer_to_file_server is True:
            regression_actions._logger.info("Deleting previous temp output from fileserver")
            regression_actions.file_server_utils.remove(actual_file_server_path, recursive=True)
            regression_actions._logger.info("Uploading actual output to fileserver")
            regression_actions.file_server_utils.upload(regression_actions.actual_output_file_name,
                                                        actual_file_server_path)
        return True
    except AssertionError:
        return False
