"""Module to contain actual logic of rotating pods."""

from sh import kubectl  # pylint: disable=E0611
import json
import argparse
import yaml
import sys
import time
from multiprocessing import Pool


def get_deployment_labels(deployments):
    """
    Get labels for a given list of deployments.

    Returns a dictionary in the below format:

    { deployment_name: {dictionary of deployment labels}, ...}
    """
    deployment_dictionary = {}
    for deployment in deployments:
        deployment_dictionary[deployment['metadata']['name']] = deployment['spec']['template']['metadata']['labels']
    return deployment_dictionary


def get_pods(namespace, deployment_name, deployment_labels):
    """Get a list of pods for a given deployment label set."""
    print("getting pods for deployment {}".format(deployment_name), file=sys.stderr)
    selectors = []
    for deployment_label in deployment_labels:
        selectors.append('{}={}'.format(deployment_label, deployment_labels[deployment_label]))
    label_string = ','.join(selectors)
    pods_as_yaml = {}
    try:
        pods_as_yaml = yaml.load(kubectl("get", "pods", "--namespace", namespace, "-l", label_string, "-o", "yaml").stdout)['items']
    except Exception:
        print("Couldn't retrieve pods for the deployment {}".format(deployment_name))
    return pods_as_yaml


def delete_pod(namespace, pods, deployment_name, sleep_timer):
    """
    Delete a list of given pods.

    Follows a sleep timer to insert a  sleep time between each deletion.
    """
    for pod in pods:
        try:
            # print("kubectl delete pod --namespace {} {}".format(namespace, pod))
            kube_delete_op_result = kubectl('delete', 'pod', '--namespace', namespace, pod)
            print(kube_delete_op_result.stdout.decode('utf-8'))
            f = open('/tmp/podrotaterstatus-{}'.format(deployment_name), 'r')
            rotation_information = json.loads(f.read())
            if pod in rotation_information['unrotated_pod_list']:
                rotation_information['unrotated_pod_list'].remove(pod)
            f = open('/tmp/podrotaterstatus-{}'.format(deployment_name), 'w')
            f.write(json.dumps(rotation_information))
            f.close()
            time.sleep(sleep_timer)
        except Exception:
            print("Failed to delete {}".format(pod))


def delete_pods_for_given_deployment(args_to_parse):
    """Entry function for the module."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--namespace', dest='namespace', action='store', help='Namespace to work in (use all to signal all namespaces)', default="default")
    parser.add_argument('--deployments', dest='deployments', action='store', nargs='+', help='Use all to signal all deployments for the namespace')
    parser.add_argument('--sleep', dest='sleep_timer', action='store', type=int, default=5, help='Time in seconds to keep between deleting each pod. Defaults to 5')
    parser.add_argument('--threaded', dest='threaded', action='store_true', help='Experimental: Leverages threads to delete pods across deployments in parallel')
    parser.add_argument('--restart', dest='restart', action='store_true')
    args = parser.parse_args(args_to_parse)
    if args.restart:
        restart_deletion(args.threaded, args.sleep_timer)
    else:
        if not args.deployments:
            print("error: the following arguments are required: --deployments")
            sys.exit(-1)
        f = open('/tmp/podrotaterlast', 'w')
        current_command_info = {"namespace": args.namespace,
                                "deployments": args.deployments}
        f.write(json.dumps(current_command_info))
        f.close()
        if args.deployments != ["all"]:
            print("Attempting to grab deployment details")
            try:
                deployments_as_yaml = yaml.load(kubectl("get", "deployments", "--namespace", args.namespace, args.deployments, "-o", "yaml").stdout)
                if 'items' not in deployments_as_yaml:
                    deployments = [deployments_as_yaml]
                else:
                    deployments = deployments_as_yaml['items']
            except Exception:
                print("oops did not work")
                sys.exit(1)
        else:
            try:
                deployments_as_yaml = yaml.load(kubectl("get", "deployments", "--namespace", args.namespace, "-o", "yaml").stdout)
                deployments = deployments_as_yaml['items']
            except Exception:
                print("oh nop. all didnt work")
                sys.exit(1)
        print("Downloaded deployment information")
        deployments_with_labels = get_deployment_labels(deployments)
        pods_to_delete = {}
        for deployment_name in deployments_with_labels:
            pods = get_pods(args.namespace, deployment_name, deployments_with_labels[deployment_name])
            pods_to_delete[deployment_name] = [pod['metadata']['name'] for pod in pods]
            f = open('/tmp/podrotaterstatus-{}'.format(deployment_name), 'w')
            info_to_write = {"deployment_name": deployment_name,
                             "namespace": args.namespace,
                             "unrotated_pod_list": pods_to_delete[deployment_name]}
            f.write(json.dumps(info_to_write))
            f.close()
        if not args.threaded:
            for deployment_name in pods_to_delete:
                pod_list = pods_to_delete[deployment_name]
                delete_pod(args.namespace, pod_list, deployment_name, args.sleep_timer)
        else:
            delete_pods_in_threads(pods_to_delete, args.namespace, args.sleep_timer)


def delete_pods_in_threads(pods_to_delete, namespace, sleep_timer):
    """Delete a list of pods using threads."""
    delete_pool = Pool()
    for deployment_name in pods_to_delete:
        pod_list = pods_to_delete[deployment_name]
        delete_pool.apply_async(delete_pod, [namespace, pod_list, deployment_name, sleep_timer])
    delete_pool.close()
    delete_pool.join()


def restart_deletion(threaded, sleep_timer):
    """Start deleting of pods from last stopped spot."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--threaded', dest='threaded', action='store_true', help='Experimental: Leverages threads to delete pods across deployments in parallel')
    f = open('/tmp/podrotaterlast', 'r')
    last_command_info = json.loads(f.read())
    pods_to_delete = {}
    for deployment_name in last_command_info['deployments']:
        f = open('/tmp/podrotaterstatus-{}'.format(deployment_name), 'r')
        pod_rotation_status = json.loads(f.read())
        if threaded:
            pods_to_delete[deployment_name] = pod_rotation_status['unrotated_pod_list']
        else:
            delete_pod(last_command_info['namespace'], pod_rotation_status['unrotated_pod_list'], deployment_name, sleep_timer)
    if threaded:
        delete_pods_in_threads(pods_to_delete, last_command_info['namespace'], sleep_timer)
