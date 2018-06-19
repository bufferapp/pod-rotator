# Kubernetes Pod Rotater

A tiny utility to help do a rolling refresh of pods across select deployments.

## How to use

`python3 rotate_pods.py rotate --namespace <namespace of choice> --deployments list of space separated deployments --sleep <number of seconds to sleep after each pod is deleted>`

Compatibility has been tested only with `python3`

## Installation

* Clone the repo: `git clone git@github.com:bufferapp/pod-rotator.git`
* Install requirements: `pip3 install -r requirements.txt`
* Run command :) 

## Description of commands

`python3 rotate_pods.py rotate` takes the following params:

* `--namespace`: Defaults to `default`. Can only input 1 namespace
* `--deployments`: **Required** (if not running `--restart`) input. Space separated list of deployments to delete pods from. If you wish to rotate pods for all deployments in the namespace, use **`all`** as the value.
* `--restart`: Used if the previous attempt to rotate pods fails in between. Usually because the net drops. This restarts from the point where it stopped so that you don't rotate already rotated pods again.
* `--sleep`: **Optional**. Number of seconds to sleep after each pod deletion request completes. _Defaults to 5_
* `--threaded`: **Experimental**. Leverages threads to delete pods of deployments in parallel
  * Note that this does NOT delete pods of the same deployment in parallel. If there are 2 or more deployments specified, it deletes pods from each deployment in parallel.
  * Eg - Deployment A and Deployment B have 3, and 5 pods respectively. Deployment A's pods are `pod-A-1` to `pod-A-3`. Deployment B's pods are `pod-B-1` to `pod-B-5`. Pods `pod-A-1`, and `pod-B-1` will be deleted in parallel but `pod-A-1` and `pod-A-2` will never be deleted at the same time.
  * This is to prevent causing a scenario where a deployment has all its pods in terminating state.

---

`python3 rotate_pods.py find-secrets` takes the following params:

* `--namespace`: Defaults to `default`. Can only input 1 namespace
* `--secrets`: Space separated list of secrets to filter deployment list by
* `--single-line`: Formats the final result as a list of space separated deployments. Useful to get a string to use with rotating pods.

## Todo

* Allow reading a deployment list from a file
* ~Have a failure resistance mechanism built in -- use a log to track progress~ - DONE
* Make this `pip` installable
* ~Make `rotater.py` be runnable via a function call instead of `subprocess`~ - DONE
* ~Add threading support for large deployments~ - DONE
