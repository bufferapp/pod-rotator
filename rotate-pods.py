import argparse
import subprocess
import rotater

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="A Tool to Rotate Pods")
    parser.add_argument("job", choices=['rotate', 'find-secrets'])
    parser.add_argument("remaining", nargs=argparse.REMAINDER)
    args=parser.parse_args()
    #print(' '.join(args.remaining))
    #c = python('rotater.py {}'.format(' '.join(args.remaining)))
    #print(c)
    if args.job == "rotate":
        rotater.delete_pods_for_given_deployment(args.remaining)
    elif args.job == "find-secrets":
        print("not yet implemented. Coming soon")