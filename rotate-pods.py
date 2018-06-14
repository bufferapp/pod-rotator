import argparse
import subprocess

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="A Tool to Rotate Pods")
    parser.add_argument("job", choices=['rotate', 'find-secrets'])
    parser.add_argument("remaining", nargs=argparse.REMAINDER)
    args=parser.parse_args()
    #print(' '.join(args.remaining))
    #c = python('rotater.py {}'.format(' '.join(args.remaining)))
    #print(c)
    if args.job == "rotate":
        subprocess.call(['python', 'rotater.py']+args.remaining)
    elif args.job == "find-secrets":
        print("not yet implemented. Coming soon")