import logging

import pytest

from chaostoolkit_nimble.actions.base.flows import chaos_user_actions
from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager

_LOGGER = logging.getLogger(__name__)


@pytest.mark.incremental
class TestNodeResiliency():

    def test_node_failover(self):
        exp_template_file = "target/artifacts/tmp/exp_templates/node_failover_exp.json"
        node_alias = NodeManager.node_obj.get_node_aliases_by_component(Components.DATANODE.name)[0]
        context = {"node_alias": node_alias}
        chaos_user_actions.run_experiment(exp_template_file=exp_template_file, context=context)
