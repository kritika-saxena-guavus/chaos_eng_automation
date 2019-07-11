# Chaos Toolkit Kubernetes Support

[![Build Status](https://travis-ci.org/chaostoolkit/chaostoolkit-kubernetes.svg?branch=master)](https://travis-ci.org/chaostoolkit/chaostoolkit-kubernetes)
[![codecov](https://codecov.io/gh/chaostoolkit/chaostoolkit-kubernetes/branch/master/graph/badge.svg)](https://codecov.io/gh/chaostoolkit/chaostoolkit-kubernetes)
[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-kubernetes.svg)](https://www.python.org/)
[![Downloads](https://pepy.tech/badge/chaostoolkit-kubernetes)](https://pepy.tech/project/chaostoolkit-kubernetes)

This project contains activities, such as probes and actions, you can call from
your experiment through the Chaos Toolkit.

## Install

To be used from your experiment, this package must be installed in the Python
environment where [chaostoolkit][] already lives.

[chaostoolkit]: https://github.com/chaostoolkit/chaostoolkit

```
$ pip install chaostoolkit-kubernetes
```

## Usage

To use the probes and actions from this package, add the following to your
experiment file:

```json
{
    "name": "all-our-microservices-should-be-healthy",
    "type": "probe",
    "tolerance": "true",
    "provider": {
        "type": "python",
        "module": "chaosk8s.probes",
        "func": "microservice_available_and_healthy",
        "arguments": {
            "name": "myapp",
            "ns": "myns"
        }
    }
},
{
    "type": "action",
    "name": "terminate-db-pod",
    "provider": {
        "type": "python",
        "module": "chaosk8s.pod.actions",
        "func": "terminate_pods",
        "arguments": {
            "label_selector": "app=my-app",
            "name_pattern": "my-app-[0-9]$",
            "rand": true,
            "ns": "default"
        }
    },
    "pauses": {
        "after": 5
    }
}
```

That's it! Notice how the action gives you the way to kill one pod randomly.

Please explore the code to see existing probes and actions.

### Discovery

You may use the Chaos Toolkit to discover the capabilities of this extension:

```
$ chaos discover chaostoolkit-kubernetes --no-install
```

## Configuration

This extension to the Chaos Toolkit can use the Kubernetes configuration 
found at the usual place in your HOME directory under `~/.kube/`, or, when
run from a Pod in a Kubernetes cluster, it will use the local service account.
In that case, make sure to set the `CHAOSTOOLKIT_IN_POD` environment variable
to `"true"`.

You can also pass the credentials via secrets as follows:

```json
{
    "secrets": {
        "kubernetes": {
            "KUBERNETES_HOST": "http://somehost",
            "KUBERNETES_API_KEY": {
                "type": "env",
                "key": "SOME_ENV_VAR"
            }
        }
    }
}
```

Then in your probe or action:

```json
{
    "name": "all-our-microservices-should-be-healthy",
    "provider": {
        "type": "python",
        "module": "chaosk8s.probes",
        "func": "microservice_available_and_healthy",
        "secrets": ["kubernetes"],
        "arguments": {
            "name": "myapp",
            "ns": "myns"
        }
    }
}
```

You may specify the Kubernetes context you want to use as follows:

```json
{
    "secrets": {
        "kubernetes": {
            "KUBERNETES_CONTEXT": "minikube"
        }
    }
}
```

Or via the environment:

```
$ export KUBERNETES_CONTEXT=minikube
```

In the same spirit, you can specify where to find your Kubernetes configuration
with:

```
$ export KUBECONFIG=some/path/config
```

## Contribute

If you wish to contribute more functions to this package, you are more than
welcome to do so. Please fork this project, make your changes following the
usual [PEP 8][pep8] code style, add appropriate tests and submit a PR for
review.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/

The Chaos Toolkit projects require all contributors must sign a
[Developer Certificate of Origin][dco] on each commit they would like to merge
into the master branch of the repository. Please, make sure you can abide by
the rules of the DCO before submitting a PR.

[dco]: https://github.com/probot/dco#how-it-works

## Execution steps

root@testautomation-mgt-01 ~]# mkdir chaos_automation_folder
[root@testautomation-mgt-01 ~]# cd chaos_automation_folder
[root@testautomation-mgt-01 chaos_automation_folder]# git clone https://github.com/kritika-saxena-guavus/chaos_engineering_automation.git
[root@testautomation-mgt-01 chaos_automation_folder]# cd chaos_engineering_automation/
[root@testautomation-mgt-01 chaos_engineering_automation]# git branch
* master

[root@testautomation-mgt-01 chaos_engineering_automation]# git checkout AUT-542
Branch AUT-542 set up to track remote branch AUT-542 from origin.
Switched to a new branch 'AUT-542'


[root@testautomation-mgt-01 chaos_engineering_automation]# cd ../

[root@testautomation-mgt-01 chaos_automation_folder]# virtualenv --python=python3 venv

(venv) [root@testautomation-mgt-01 chaos_engineering_automation]# pip install -r requirements.txt

(venv) [root@testautomation-mgt-01 chaos_engineering_automation]# python setup.py develop

(venv) [root@testautomation-mgt-01 chaos_engineering_automation]# pip install nimble  --extra-index-url http://192.168.192.201:5050/simple/ --trusted-host 192.168.192.201

(venv) [root@testautomation-mgt-01 chaos_engineering_automation]# pip uninstall fabric

(venv) [root@testautomation-mgt-01 chaos_engineering_automation]# pip install fabric3

(venv) [root@testautomation-mgt-01 chaos_engineering_automation]# python mypackage/runner_process.py 

(venv) [root@testautomation-mgt-01 chaos_engineering_automation]# python mypackage/kubernetes_process.py 

(venv) [root@testautomation-mgt-01 chaos_engineering_automation]# ls -ltr target/artifacts/
total 132
-rw-r--r--. 1 root root  1249 Jul 11 07:05 process_experiment.json
-rw-r--r--. 1 root root  6967 Jul 11 07:05 process_chaostoolkit.log
-rw-r--r--. 1 root root  4622 Jul 11 07:05 process_journal.json
-rw-r--r--. 1 root root  3592 Jul 11 07:05 process_output.txt
-rw-r--r--. 1 root root  2426 Jul 11 07:06 kubernetes_experiment.json
-rw-r--r--. 1 root root 29482 Jul 11 07:07 kubernetes_chaostoolkit.log
-rw-r--r--. 1 root root 26460 Jul 11 07:07 kubernetes_journal.json
-rw-r--r--. 1 root root 42779 Jul 11 07:07 kubernetes_output.txt
