from sh import kubectl #pylint: disable=E0611
import argparse
import yaml
import sys
import time

def getDeploymentLabels(deployments):
    deployment_dictionary = {}
    for deployment in deployments:
        deployment_dictionary[deployment['metadata']['name']] = deployment['spec']['template']['metadata']['labels']
    return deployment_dictionary

def getPods(namespace, deployment_name, deployment_labels):
    print("getting pods for deployment {}".format(deployment_name), file=sys.stderr) 
    selectors = []
    for deployment_label in deployment_labels:
        selectors.append('{}={}'.format(deployment_label, deployment_labels[deployment_label]))
    label_string=','.join(selectors)
    pods_as_yaml = {}
    try:
        pods_as_yaml=yaml.load(kubectl("get", "pods", "--namespace", namespace, "-l", label_string, "-o", "yaml").stdout)['items']
    except:
        print("Couldn't retrieve pods for the deployment {}".format(deployment_name))
    return pods_as_yaml

def deletePod(namespace, pods, sleep_timer):
    for pod in pods:
        try:
            kube_delete_op_result = kubectl('delete', 'pod', '--namespace', namespace, pod)
            print(kube_delete_op_result.stdout)
            time.sleep(sleep_timer)
        except:
            print("Failed to delete {}".format(pod))

    
if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--namespace', dest='namespace', action='store', help='Namespace to work in (use all to signal all namespaces)', default="default")
    parser.add_argument('--deployments', dest='deployments', action='store', nargs='+', required=True, help='Use all to signal all deployments for the namespace')
    parser.add_argument('--sleep', dest='sleep_timer', action='store', type=int, default=5, help='Time in seconds to keep between deleting each pod. Defaults to 5')
    args = parser.parse_args()
    if args.deployments != ["all"]:
        try:
            deployments_as_yaml = yaml.load(kubectl("get", "deployments", "--namespace", args.namespace, args.deployments, "-o", "yaml").stdout)
            if 'items' not in deployments_as_yaml:
                deployments = [deployments_as_yaml]
            else:
                deployments = deployments_as_yaml['items']
        except:
            print("oops did not work")
            sys.exit(1)
    else:
        try:
            deployments_as_yaml = yaml.load(kubectl("get", "deployments", "--namespace", args.namespace, "-o", "yaml").stdout)
            deployments = deployments_as_yaml['items']
        except:
            print("oh nop. all didnt work")
            sys.exit(1)

    deployments_with_labels = getDeploymentLabels(deployments)
    pods_to_delete = {}
    for deployment_name in deployments_with_labels:
        pods=getPods(args.namespace, deployment_name, deployments_with_labels[deployment_name])
        pods_to_delete[deployment_name] = [pod['metadata']['name'] for pod in pods]
    for deployment_name in pods_to_delete:
        pod_list = pods_to_delete[deployment_name]
        deletePod(args.namespace, pod_list, args.sleep_timer)
            