"""Score Kavach's detector on ICFD-31k, an independent dataset of synthetic
Indian fraud-call transcripts (Ahuja, Prateek and Singh, IJCAI 2026).

    python scripts/eval_icfd.py                 # validation, test and cross-domain
    python scripts/eval_icfd.py --split test
    python scripts/eval_icfd.py --misses validation --n 20   # print missed calls

Text only: no Prisma, no Timbre, no credits, about 10 seconds. Every turn
(both speakers, as a speakerphone would hear them) goes to a fresh
ScamDetector in order, with its timestamp.

How the splits are used, so the numbers stay honest:
- validation: allowed for development. Misses may be read and used to widen
  the rules.
- test and cross_domain: measured only. Never read individual misses.

Get the data (about 5 MB; defensive-use licence, cite the paper):
    mkdir -p cache/icfd && cd cache/icfd
    for f in validation-00000-of-00002 validation-00001-of-00002 test-00000-of-00002 \\
             test-00001-of-00002 cross_domain-00000-of-00001; do
      curl -sLO https://huggingface.co/datasets/rishia2220/icfd-31k/resolve/main/source_conversations/$f.jsonl.zst
      zstd -dq $f.jsonl.zst
    done

The dataset is about 99% fraud calls, so it measures how many scams are
caught. False alarms are measured on Kavach's own genuine calls instead.
"""
import argparse
import collections
import glob
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402
from app.detector import ScamDetector  # noqa: E402

DATA = config.ROOT / "cache" / "icfd"
SPLITS = ("validation", "test", "cross_domain")


def load(split: str) -> list[dict]:
    files = sorted(glob.glob(str(DATA / f"{split}-*.jsonl")))
    if not files:
        sys.exit(f"No {split} files in {DATA}; see this script's docstring to download them.")
    return [json.loads(line) for f in files for line in open(f)]


def seconds(value, default: float) -> float:
    """Timestamps are usually numbers, but a few are written like "1.2*60"."""
    try:
        return float(value)
    except (TypeError, ValueError):
        m = re.fullmatch(r"\s*([\d.]+)\s*\*\s*([\d.]+)\s*", str(value))
        return float(m[1]) * float(m[2]) if m else default


def score(call: dict) -> dict:
    """Run one transcript through a fresh detector."""
    det = ScamDetector()
    t = 0.0
    for turn in call["transcript"]:
        t = seconds(turn.get("timestamp_end"), t)
        det.update(turn.get("text", ""), t)
    s = det.summary(t)
    first_flag = next((seconds(c.get("timestamp"), 0.0) for c in call.get("chunk_level_analysis", [])
                       if c.get("verdict_at_chunk") == "YES"), None)
    return {
        "id": call["release_metadata"]["conversation_uid"],
        "domain": call["release_metadata"]["domain"],
        "fraud": call["final_verdict"] == "YES",
        "warned": det.level >= 2,
        "max_risk": s["max_risk"],
        "warn_t": s["warn_t"],
        "first_flag_t": first_flag,
        "scam_type": s["scam_type"],
    }


def report(split: str, rs: list[dict]) -> dict:
    fraud = [r for r in rs if r["fraud"]]
    normal = [r for r in rs if not r["fraud"]]
    caught = [r for r in fraud if r["warned"]]
    early = [r for r in caught if r["first_flag_t"] is not None and r["warn_t"] <= r["first_flag_t"] + 10]
    by_domain = {}
    for r in fraud:
        d = by_domain.setdefault(r["domain"], [0, 0])
        d[0] += r["warned"]
        d[1] += 1
    out = {
        "split": split,
        "fraud_calls": len(fraud),
        "caught": len(caught),
        "catch_rate": round(100 * len(caught) / max(len(fraud), 1), 1),
        "normal_calls": len(normal),
        "warned_on_normal": sum(r["warned"] for r in normal),
        "median_warn_s": round(statistics.median([r["warn_t"] for r in caught]), 1) if caught else None,
        "within_10s_of_annotator": round(100 * len(early) / max(len(caught), 1), 1),
        "by_domain": {k: f"{v[0]}/{v[1]} ({100 * v[0] / v[1]:.0f}%)" for k, v in sorted(by_domain.items())},
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=SPLITS)
    ap.add_argument("--misses", choices=["validation"],
                    help="print missed fraud calls from the development split (never test)")
    ap.add_argument("--n", type=int, default=15)
    ap.add_argument("--save", help="write the summaries to this JSON file")
    args = ap.parse_args()

    if args.misses:
        calls = load(args.misses)
        missed = [(c, score(c)) for c in calls if c["final_verdict"] == "YES"]
        missed = [(c, r) for c, r in missed if not r["warned"]]
        print(f"{len(missed)} missed fraud calls in {args.misses}; showing {min(args.n, len(missed))}\n")
        for c, r in missed[:args.n]:
            print(f"== {r['domain']}  peak {r['max_risk']}  {c['scenario']['description'][:110]}")
            for turn in c["transcript"]:
                if turn.get("speaker") == "Agent":
                    print("   ", turn["text"][:160])
            print()
        return

    results = []
    for split in ([args.split] if args.split else SPLITS):
        rs = [score(c) for c in load(split)]
        s = report(split, rs)
        results.append(s)
        print(f"{split:13s} caught {s['caught']}/{s['fraud_calls']} fraud calls ({s['catch_rate']}%), "
              f"warned on {s['warned_on_normal']}/{s['normal_calls']} calls labelled normal, "
              f"median warning at {s['median_warn_s']} s, "
              f"{s['within_10s_of_annotator']}% within 10 s of the annotator's first flag")
        for d, v in s["by_domain"].items():
            print(f"    {d:30s} {v}")
    if args.save:
        Path(args.save).write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
