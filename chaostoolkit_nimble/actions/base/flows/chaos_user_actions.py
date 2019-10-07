import logging
import re

import allure
import jinja2

from nimble.core import global_constants
from nimble.core.utils.file_server_utils import FileServerUtils
from nimble.core.utils.shell_utils import ShellUtils

_LOGGER = logging.getLogger(__name__)

EXPERIMENTS_BASE_PATH = "%s/tmp/experiments/" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
ShellUtils.execute_shell_command(ShellUtils.remove_and_create_directory(EXPERIMENTS_BASE_PATH))


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
    _LOGGER.info('Rendering from template: %s' % template.name)
    template.stream(context).dump('%s/%s' % (EXPERIMENTS_BASE_PATH, template_file_name))


def generate_html(journal_path):
    html_report_path = "%s/chaos_report.html" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
    command = "export LC_ALL=en_US.UTF-8 && chaos report --export-format=html5 %s %s" % (
        journal_path, html_report_path)
    ShellUtils.execute_shell_command(command)
    return html_report_path
