"""
Module to route commands when being called.

Is used to call sub modules. This file should only be called
directly
"""
import argparse
import rotater

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A Tool to Rotate Pods")
    parser.add_argument("job", choices=['rotate', 'find-secrets', 'mptest'])
    parser.add_argument("remaining", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.job == "rotate":
        rotater.delete_pods_for_given_deployment(args.remaining)
    elif args.job == "find-secrets":
        print("not yet implemented. Coming soon")
