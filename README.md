# Kubernetes Pod Rotater

A tiny utility to help do a rolling refresh of pods across select deployments.

## How to use

`python3 rotater.py rotate --namespace <namespace of choice> --deployments list of space separated deployments --sleep <number of seconds to sleep after each pod is deleted>`

Compatibility has been tested only with `python3`

## Installation

* Clone the repo: `git clone git@github.com:bufferapp/pod-rotator.git`
* Install requirements: `pip3 install -r requirements.txt`
* Run command :) 

## Description of commands

`python3 rotater.py rotate` takes the following params:

* `--namespace`: Defaults to `default`. Can only input 1 namespace
* `--deployments`: **Required** input. Space separated list of deployments to delete pods from. If you wish to rotate pods for all deployments in the namespace, use **`all`** as the value.
* `--sleep`: **Optional**. Number of seconds to sleep after each pod deletion request completes. _Defaults to 5_

## Todo

* Allow reading a deployment list from a file
* Have a failure resistance mechanism built in -- use a log to track progress 
* Make this `pip` installable
* Make `rotater.py` be runnable via a function call instead of `subprocess`
* Add threading support for large deployments