#!/usr/bin/env python
"""Re-score every stored generation with the current parsers (no GPU). Prints groups that moved."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import OUT_DIR
from codecue.prompts import parse_answer, parse_answer_free, parse_regime, value_written

def main() -> int:
    for bf in sorted(OUT_DIR.glob("runs/*/*/*/*/behavior.jsonl")):
        regime = parse_regime(bf.parents[1].name)[0]; few = regime in ("direct", "trace")
        rows = [json.loads(l) for l in bf.open()]; out = []; moved = 0
        for r in rows:
            pred = parse_answer(r["generation"]) if few else parse_answer_free(r["generation"])
            role = r["target"] or r["query"]
            vw = ({rr: value_written(r["generation"], nm) for rr, nm in r["names"].items()} if regime != "direct"
                  else {rr: None for rr in r["names"]})
            wrote = vw[role]
            new = {**r, "pred": pred, "correct": pred == r["answer"], "pred_is_lure": r["lure"] is not None and pred == r["lure"],
                   "value_written": wrote, "wrote_true_value": wrote is not None and wrote == r["values"][role], "values_written": vw}
            moved += (new["pred"], new["correct"], new["value_written"], r.get("values_written")) != (r["pred"], r["correct"], r.get("value_written"), vw); out.append(new)
        if moved:
            acc0 = sum(r["correct"] for r in rows) / len(rows); acc1 = sum(r["correct"] for r in out) / len(out)
            print(f"{str(bf.parent.relative_to(OUT_DIR / 'runs')):58s} acc {100*acc0:5.1f} -> {100*acc1:5.1f} ({moved} rows)")
            bf.write_text("".join(json.dumps(r) + "\n" for r in out))
            sf = bf.parent / "summary.json"
            if sf.exists():
                s = json.loads(sf.read_text()); s["accuracy"] = acc1
                s["lure_rate"] = sum(r["pred_is_lure"] for r in out) / len(out); s["reparsed"] = True
                sf.write_text(json.dumps(s, indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main())
