import logging

import pytest

from chaostoolkit_nimble.actions.base.flows import chaos_user_actions
from nimble.core.utils.components.kubernetes_utils import KubernetesRestClientUtils, KubernetesCliUtils

_LOGGER = logging.getLogger(__name__)


@pytest.mark.incremental
class TestSampleKubernetes():

    @pytest.fixture(scope="session")
    def kubernetes_rest_client_utils(self):
        return KubernetesRestClientUtils()

    @pytest.fixture(scope="session")
    def kubernetes_cli_utils(self):
        return KubernetesCliUtils()

    def test_pod_failover(self, kubernetes_rest_client_utils, kubernetes_cli_utils):
        exp_template_file = "target/artifacts/tmp/exp_templates/pod_failover_exp.json"
        namespace = "kube-system"
        context = {"kubernetes_host": kubernetes_rest_client_utils.base_url,
                   "kubernetes_api_key": kubernetes_cli_utils.get_secret_token(
                       secret_name_prefix="kubernetes-dashboard-token", namespace=namespace),
                   "namespace": namespace,
                   "pod_label_selector": "app=flannel,version=v0.1",
                   }
        chaos_user_actions.run_experiment(exp_template_file=exp_template_file, context=context)
