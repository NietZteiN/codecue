#!/usr/bin/env python
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--layout-only', action='store_true')
    parser.add_argument('config')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    from codecue.binding.hook_preflight import run, layout_check
    print(json.dumps((layout_check if args.layout_only else run)(config), indent=2))


if __name__ == '__main__':
    main()
