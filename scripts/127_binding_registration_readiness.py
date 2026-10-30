#!/usr/bin/env python
"""Lint forecast-registration metadata and emit an inert prerequisite DAG."""
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config')
    args = parser.parse_args()
    from codecue.binding.registration_readiness import build, load_config
    print(json.dumps(build(load_config(args.config)), sort_keys=True, indent=2))


if __name__ == '__main__': main()
