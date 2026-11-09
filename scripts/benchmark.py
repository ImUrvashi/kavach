"""Benchmark Kavach end to end on every demo call.

Usage:
    python scripts/benchmark.py                    # all 27 calls, clean audio
    python scripts/benchmark.py --noise            # phone-line audio (narrow band + hiss)
    python scripts/benchmark.py --lang hi-IN       # one language
    python scripts/benchmark.py --lang hi-IN --script upi   # one call
    python scripts/benchmark.py --retry-errors     # re-run only the calls that failed last time
    python scripts/benchmark.py --rescore          # re-score saved transcripts with the current detector (free)
    python scripts/benchmark.py --unseen           # held-out set 1 (15 calls; development data since v2)
    python scripts/benchmark.py --blind            # blind held-out set 2 (30 calls written without seeing the rules)

Each call is spoken by Gnani Timbre and streamed through Gnani Prisma at
real-time speed, so a full run takes about 27 calls × ~25 s ÷ concurrency
(about 4 minutes at the default of 3 at once). Costs: Timbre once per line
(lines are saved after that), and Prisma for every second of every call.

Writes to cache/benchmark/ (cache/benchmark_noise/ with --noise,
cache/benchmark_unseen/ with --unseen, cache/benchmark_unseen_noise/ with both):
    results.json   everything, including each call's transcript
    results.md     summary tables, ready to paste into the README
    chart.svg      highest risk per call, for the README
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402
from app.benchmark import (LANG_NAMES, all_calls, chart_svg, headline, rescore,  # noqa: E402
                           run_all, short, summarize, to_markdown)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=list(LANG_NAMES))
    ap.add_argument("--script", help="one call, e.g. scam, family, upi, legit (or trai_sim with --unseen)")
    ap.add_argument("--unseen", action="store_true", help="run held-out set 1 instead of the demo calls")
    ap.add_argument("--blind", action="store_true", help="run the blind held-out set 2")
    ap.add_argument("--noise", action="store_true", help="make the audio sound like a phone line")
    ap.add_argument("--concurrency", type=int, default=3, help="calls at once (default 3)")
    ap.add_argument("--retry-errors", action="store_true",
                    help="re-run only the calls that failed in the saved results, and merge them in")
    ap.add_argument("--rescore", action="store_true",
                    help="score the saved Prisma transcripts again with the current detector (no Gnani calls)")
    args = ap.parse_args()
    out = config.ROOT / "cache" / ("benchmark" + ("_blind" if args.blind else "_unseen" if args.unseen else "") + ("_noise" if args.noise else ""))

    if args.rescore:
        saved = out / "results.json"
        if not saved.exists():
            sys.exit(f"No saved results in {out}; run the benchmark first.")
        results = [rescore(r) for r in json.loads(saved.read_text())["calls"]]
        for r in results:
            show(r)
        save(out, results, args.noise)
        return

    if not config.GNANI_API_KEY:
        sys.exit("Add GNANI_API_KEY to .env first.")
    previous = []
    if args.retry_errors:
        saved = out / "results.json"
        if not saved.exists():
            sys.exit(f"No saved results in {out}; run the benchmark first.")
        previous = json.loads(saved.read_text())["calls"]
        calls = [(r["lang"], r["script"]) for r in previous if "error" in r]
        if not calls:
            sys.exit("No failed calls to re-run.")
    else:
        calls = all_calls(args.lang, args.script, unseen=args.unseen, blind=args.blind)
    if not calls:
        sys.exit("No demo call matches that language and script.")
    print(f"Running {len(calls)} call(s){' with phone-line audio' if args.noise else ''}, "
          f"{args.concurrency} at a time…\n")

    t0 = time.monotonic()
    results = asyncio.run(run_all(calls, noise=args.noise, concurrency=args.concurrency, on_result=show))
    if previous:  # put the re-run calls back in their places
        fresh = {(r["lang"], r["script"]): r for r in results}
        results = [fresh.get((r["lang"], r["script"]), r) for r in previous]
    save(out, results, args.noise)
    print(f"Took {time.monotonic() - t0:.0f} s")


def show(r):
    name = f"{LANG_NAMES[r['lang']]:8s} {short(r):14s}"
    if "error" in r:
        print(f"  [ERROR] {name} {r['error']}")
    else:
        mark = "ok " if r["correct"] else "MISS" if r["kind"] == "scam" else "FALSE ALARM"
        print(f"  [{mark}] {name} {r['kind']:7s} highest risk {r['max_risk']:3d}"
              f"{'  warned at ' + str(r['warn_t']) + ' s' if r['warned'] else ''}")


def save(out, results, noise):
    s = summarize(results)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps({"summary": s, "calls": results}, indent=2, ensure_ascii=False))
    (out / "results.md").write_text(to_markdown(results, s, noise))
    (out / "chart.svg").write_text(chart_svg(results, s))
    print(f"\n{headline(s)}.")
    print(f"Median time from first sign to warning: {s['median_time_to_warning_s']} s · "
          f"median Prisma delay: {s['median_prisma_latency_ms']} ms")
    if s["errors"]:
        print(f"{len(s['errors'])} call(s) failed; see results.md.")
    print(f"Saved results.json, results.md and chart.svg in {out}")


if __name__ == "__main__":
    main()
