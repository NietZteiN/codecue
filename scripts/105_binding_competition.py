#!/usr/bin/env python
"""Build or review the arithmetic-free discovery competition bank."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('build', 'audit-names', 'review-competition', 'review-serialization'))
    parser.add_argument('config')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    if args.command.startswith('review-'):
        from codecue.binding import continuation_review
        result = getattr(continuation_review, args.command.removeprefix('review-'))(config)
    elif args.command == 'build':
        from codecue.binding.competition import build
        result = build(config)
    else:
        from transformers import AutoTokenizer
        from codecue.binding.model_adapter import configure_tokenizer
        from codecue.binding.datasets import write_json
        result = {}
        for model in config['models']:
            tok = AutoTokenizer.from_pretrained(model['model'], revision=model['tokenizer_revision'], local_files_only=True)
            configure_tokenizer(tok, model)
            checks = []
            for a, b in config['pairs']:
                lengths = []
                for prefix in ('train_', 'dev_'):
                    for context in ('{} = 3', 'print({})', '\n{} = 3'):
                        left = tok(context.format(prefix + a), add_special_tokens=False)['input_ids']
                        right = tok(context.format(prefix + b), add_special_tokens=False)['input_ids']
                        lengths.append((len(left), len(right)))
                checks.append(dict(names=[a, b], lengths=lengths, matched=all(a == b for a, b in lengths)))
            result[model['model']] = checks
        write_json(config['output'], result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
