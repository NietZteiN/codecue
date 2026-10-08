#!/usr/bin/env python
"""Audit every disjoint rerun, select a validated release and rebuild the code paper."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codecue.config import OUT_DIR, RESULTS_DIR  # noqa: E402
from codecue.probe_validation import validate_file  # noqa: E402

MODELS = ("olmo2-7b-it", "llama32-3b-it", "llama31-8b-it")
REGIMES = ("trace", "trace_s11", "trace_s13")


def update_manuscript():
    path = ROOT / "paper/main.tex"
    text = path.read_text()
    text = text.replace("Probe results remain provisional because training\nand evaluation reuse programs.", "")
    text = text.replace("Our probe analysis requires replication on disjoint programs.",
                        "Probes compare the computed digit with the value the trace writes.")
    text = text.replace("The saved probe runs reused evaluation programs in\ntraining; their readouts are provisional.",
                        "Probe training and evaluation use disjoint program computations.")
    title = r"\subsection{Patches reduce lure writes; probes need replication}"
    if title in text:
        start = text.index(title)
        end = text.index("Patching independently tests", start)
        text = text[:start] + r"""\subsection{Readouts and patches at the writing position}

At the decision token, neutral-trained probes recover the computed digit with accuracy of
\NUM{probe-olmo7-code}\%, \NUM{probe-llama3-code}\% and \NUM{probe-llama8-code}\% in the
three affected models. Each layer is selected by neutral accuracy, averaging three probe seeds.
Training uses separate programs; renamed test computations are excluded. The name-identity
controls score \NUM{probe-olmo7-ctl}, \NUM{probe-llama3-ctl} and \NUM{probe-llama8-ctl} on
neutral programs. These readouts measure decodable information, not whether the model uses
the digit to generate its trace. Appendix~\ref{app:probes} gives the demonstration-set repeats.

""" + text[end:]
    text = text.replace("Dashed green: provisional true-value probe accuracy; evaluation programs overlap training.",
                        "Dashed green: true-value probe accuracy on programs excluded from training.")
    text = text.replace("Here misleading names change trace writes; the probe analysis requires disjoint\nreplication before a comparison of internal readouts is warranted.",
                        "Here misleading names change trace writes. The two studies do not establish a shared\nmechanism.")
    text = text.replace("The probe runs reuse evaluation programs in training and have strong name-identity controls.\nThey do not establish held-out decodability or whether a decoded value drives generation.\nThe corrected pipeline selects independent neutral programs; fresh runs remain necessary.",
                        "Name-identity controls measure identifier information in the readout. A readable digit\ndoes not establish that the model uses it during generation. Layers are selected on neutral\nevaluation accuracy, so those neutral scores are descriptive.")
    text = text.replace("However, the saved runs trained on neutral twins of the evaluation\nprograms. This invalidates a held-out interpretation of their accuracy. We corrected the\ntraining selector and added overlap guards; disjoint replication is pending. The strong\nname-control scores further limit selectivity.",
                        "The original implementation reused test programs in training. The reported reruns\nreplace those scores: they train on \\NUM{probe-n-train} independent neutral programs and\nevaluate \\NUM{probe-n-test} misleading-name programs, with overlap guards that ignore name\nspelling. Table~\\ref{tab:probe-repeats} reports the name controls alongside digit accuracy.")
    marker = "% Disjoint-probe demonstration repeats"
    if marker not in text:
        text = text.replace("The probes use a force-decoded gold trace.",
                            "We supply the correct trace token by token when caching probe inputs.")
        insertion = marker + r"""
The main scores use demonstration set 7. Repeating training and evaluation with sets 11 and 13
gives true-digit accuracies of \NUM{probe-olmo7-demo-lo}--\NUM{probe-olmo7-demo-hi}\%,
\NUM{probe-llama3-demo-lo}--\NUM{probe-llama3-demo-hi}\% and
\NUM{probe-llama8-demo-lo}--\NUM{probe-llama8-demo-hi}\% across the three sets. Each repeat
uses the same independent training programs and three probe seeds; its layer is selected by
that set's neutral accuracy. These repeats assess prompt sensitivity, not a causal role for
the decoded digit. Table~\ref{tab:probe-repeats} gives both conditions' readouts and controls.

\begin{table*}[t]
\centering\small
\tabinput{probe_repeats}
\caption{Disjoint code probes, three demonstration sets. Neutral and misleading are
true-digit accuracy; each control column gives name-identity accuracy for that condition.
Majority predicts the most frequent digit in training on the misleading test programs.
Rates are percentages, averaged over three probe seeds. Layers are selected by neutral accuracy.}
\label{tab:probe-repeats}
\end{table*}

"""
        anchor = "We supply the correct trace token by token when caching probe inputs."
        if anchor not in text:
            raise ValueError("probe appendix anchor changed; manuscript needs review")
        text = text.replace(anchor, insertion + anchor)
    path.write_text(text)
    path = ROOT / "paper/ARGUMENT.md"
    text = path.read_text().replace("The saved probes reuse evaluation programs in training,\nso their apparent recovery of the length requires disjoint replication.",
                                   "The revised probes train on disjoint programs and report readouts\nand name controls under all three demonstration sets; decodability does not establish use.")
    text = text.replace("Label probe readouts provisional: every misleading-name evaluation program has a neutral\n   twin in training. Require fresh disjoint runs before claiming held-out decodability.",
                        "Report the validated disjoint probe readouts and their controls, with demonstration-set\n   repeats. Decodability does not establish that the model uses the decoded digit.")
    text = text.replace("- The saved probes have train/test program overlap. Fresh disjoint runs are required.",
                        "- The original probes reused test programs in training. Reported replacement runs pass\n  the split audit; retain the original caches as an audit trail.")
    path.write_text(text)
    path = ROOT / "README.md"
    text = path.read_text().replace("The verification pass found train/test\nprogram overlap in the saved probes; their readouts remain provisional pending disjoint reruns.",
                                   "The verification pass found train/test\nprogram overlap in the original probes. Validated disjoint reruns now supply the paper's\nreadouts; the original caches remain available for auditing.")
    path.write_text(text)


def main():
    report = {"collected_utc": datetime.now(timezone.utc).isoformat(), "models": {}, "errors": []}
    for model in MODELS:
        report["models"][model] = {}
        for regime in REGIMES:
            path = OUT_DIR / "probes_disjoint" / model / "L5" / regime / "v1.json"
            try:
                report["models"][model][regime] = {**validate_file(path), "source": str(path)}
            except Exception as error:
                report["errors"].append({"model": model, "regime": regime, "error": str(error)})
    report["validated"] = not report["errors"]
    summary = RESULTS_DIR / "summary"
    (summary / "disjoint_probes.json").write_text(json.dumps(report, indent=2) + "\n")
    if report["errors"]:
        print(json.dumps(report["errors"], indent=2))
        return 1
    (summary / "probe_release.json").write_text(json.dumps({"validated": True,
        "root": "probes_disjoint", "audit": "disjoint_probes.json",
        "collected_utc": report["collected_utc"]}, indent=2) + "\n")
    update_manuscript()
    commands = [[sys.executable, "scripts/51_numbers.py"],
                [sys.executable, "scripts/71_mechanism_figure.py"],
                [sys.executable, "scripts/99_selfcheck.py"], ["make", "paper-submission"]]
    report["stages"] = []
    for i, command in enumerate(commands):
        log = ROOT / "log/round4_2026-10-02" / f"collect_stage{i+1}.out"
        with log.open("w") as output:
            run = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        report["stages"].append({"argv": command, "exit_code": run.returncode, "log": str(log)})
        if run.returncode:
            report["validated"] = False
            report["errors"].append({"stage": i+1, "error": f"exit {run.returncode}; see {log}"})
            break
    (summary / "disjoint_probes.json").write_text(json.dumps(report, indent=2) + "\n")
    with (RESULTS_DIR / "NOTES.md").open("a") as stream:
        stream.write("\n### Disjoint probe collection\n\n" +
                     f"Split validation passed for all nine reruns. Build status: {report['validated']}. " +
                     "Current scores and demonstration-set repeats are in `summary/disjoint_probes.json`. " +
                     "The original overlapping caches are historical and no longer supply paper numbers.\n")
    print(json.dumps({"validated": report["validated"], "errors": report["errors"]}, indent=2))
    return 0 if report["validated"] else 1


if __name__ == "__main__":
    sys.exit(main())
