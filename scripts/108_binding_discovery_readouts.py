#!/usr/bin/env python
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('config')
    config=json.loads(Path(parser.parse_args().config).read_text())
    from codecue.binding.discovery_readouts import run
    print(json.dumps(run(config),indent=2))


if __name__=='__main__':main()
