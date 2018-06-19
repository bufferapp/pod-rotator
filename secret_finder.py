"""Module to find which deployments use a given secret."""

from sh import kubectl  # pylint: disable=E0611
import yaml
import argparse
import sys


def get_all_deployments_for_namespace_as_yaml(namespace):
    """Return a list of deployments in yaml form for a given namespace."""
    print("Retrieving all deployments for the namespace {}".format(namespace))
    try:
        deployments_as_yaml = yaml.load(kubectl("get", "deployments", "--namespace", namespace, "--output", "yaml").stdout)['items']
        return deployments_as_yaml
    except Exception:
        print("Error happened while retrieving deployments")
        print(sys.exc_info())
        return {}


def filter_deployments_using_secret(secret_names, deployments_as_yaml):
    """Return a dictionary of deployments using the secret we are filtering on."""
    deployments_using_secrets = {}
    for deployment in deployments_as_yaml:
        found_secret = False
        containers = deployment['spec']['template']['spec']['containers']
        for container in containers:
            if found_secret:
                break
            if 'env' not in container:
                continue
            env_vars = container['env']
            for env_var in env_vars:
                if 'valueFrom' not in env_var or 'secretKeyRef' not in env_var['valueFrom']:
                    continue
                if env_var['valueFrom']['secretKeyRef']['name'] in secret_names:
                    deployments_using_secrets[deployment['metadata']['name']] = deployment
                    found_secret = True
                    break

    return deployments_using_secrets


def print_deployment_names(deployments, format_as_single_line):
    """Print a pretty print of just the deployment names."""
    if format_as_single_line:
        print(' '.join(deployments.keys()))
    else:
        print('\n'.join(deployments.keys()))


def find_deployments_using_secret(passed_arguments):
    """Entry method to start process of finding deployments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--namespace', dest='namespace', action='store', help='Namespace to work in (use all to signal all namespaces)', default="default")
    parser.add_argument('--secrets', dest='secrets', action='store', nargs='+', help='List of secrets to look for. Currently only supports one secret.')
    parser.add_argument('--single-line', dest='single_line', action='store_true', help='Prints all the deployments in a space separated single line. Useful for getting a list of deployments to delete')
    args = parser.parse_args(passed_arguments)
    namespace = args.namespace
    secret_names = args.secrets
    format_as_single_line = args.single_line
    deployments_as_yaml = get_all_deployments_for_namespace_as_yaml(namespace)
    deployments_using_secrets = filter_deployments_using_secret(secret_names, deployments_as_yaml)

    print_deployment_names(deployments_using_secrets, format_as_single_line)
    return 0
