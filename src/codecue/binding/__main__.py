from __future__ import annotations
import argparse
import json
from pathlib import Path
from .datasets import generate, validate, write_json


def main():
    parser = argparse.ArgumentParser(description="CodeCue versioned-binding study")
    parser.add_argument("command", choices=["generate", "validate", "run-behavior", "extract", "fit-probes", "intervene", "evaluate-heldout", "report", "freeze-source", "verify-source", "profile-model", "fit-forecasters", "write-forecasts", "diagnose-interface", "calibrate-protocol", "build-calibration-bank", "diagnose-errors", "compare-backends", "check-generation", "build-difficulty-ladder", "analyze-difficulty-ladder"])
    parser.add_argument("--config")
    parser.add_argument("--dataset")
    parser.add_argument("--run")
    parser.add_argument("--output")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text()) if args.config else None
    if args.command == 'freeze-source':
        from .snapshots import freeze
        result = freeze(args.output)
    elif args.command == 'verify-source':
        from .snapshots import verify
        result = verify(args.run)
    elif args.command == 'profile-model':
        from .profiling import profile
        result = profile(config)
    elif args.command == "generate":
        result = generate(config["generation"], config["dataset"])
    elif args.command == "validate":
        path = args.dataset or config["dataset"]
        result = validate(path)
        write_json(Path(path).with_suffix(".validation.json"), result)
    elif args.command == "run-behavior":
        from .behavior import run
        result = run(config)
    elif args.command == "extract":
        from .activations import extract
        result = extract(config)
    elif args.command == "fit-probes":
        from .probes import fit
        result = fit(config)
    elif args.command == "intervene":
        from .interventions import run
        result = run(config)
    elif args.command == "evaluate-heldout":
        from .heldout import evaluate
        result = evaluate(config)
    elif args.command == 'fit-forecasters':
        from .forecasting import fit
        result = fit(config)
    elif args.command == 'write-forecasts':
        from .forecasting import write_forecasts
        result = write_forecasts(config)
    elif args.command == 'diagnose-interface':
        from .diagnostics import run
        result = run(config)
    elif args.command=='calibrate-protocol':
        from .calibration import run
        result=run(config)
    elif args.command=='build-calibration-bank':
        from .calibration import build_bank
        result=build_bank(args.output)
    elif args.command=='diagnose-errors':
        from .diagnostic_null import run
        result=run(config)
    elif args.command=='compare-backends':
        from .backend_comparison import run
        result=run(config)
    elif args.command=='check-generation':
        from .generation_reference import run
        result=run(config)
    elif args.command=='build-difficulty-ladder':
        from .ladder import build
        result=build(config)
    elif args.command=='analyze-difficulty-ladder':
        from .ladder import analyze
        result=analyze(config)
    else:
        from .analysis import report
        result = report(Path(args.run or config["run_dir"]))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
