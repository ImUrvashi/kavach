"""Benchmark: how well does Kavach catch scams, end to end?

Every demo call (6 kinds of scam and 3 genuine look-alikes, in Hindi,
Hinglish and Kannada) is spoken by Timbre and streamed through Gnani Prisma
at real-time speed, exactly like a live call. The detector scores Prisma's
transcript, and we record whether Kavach warned, how fast, and whether it
named the scam correctly. Optionally the audio is made to sound like a phone
line first (narrow band plus background hiss).

Two sets of calls: the 27 demo calls (the detector was tuned on these), and
15 held-out calls in unseen_calls.py that were never used for tuning.

Run it with scripts/benchmark.py. The test calls are synthetic: one stock
voice per language, no real scam recordings.
"""
import asyncio
import statistics
import time

import numpy as np

from . import config
from .demo_audio import RATE, build_demo_call, to_frames
from .detector import ScamDetector
from .mock_calls import CALLS, EXPECTED_TYPE
from .blind_calls import BLIND
from .unseen_calls import UNSEEN
from .stt import GnaniSTTSession
from .warnings_text import SCAM_NAMES

SETTLE_S = 1.5  # after the audio ends, time for Prisma's last sentence

LANG_NAMES = {"hi-IN": "Hindi", "en-IN": "Hinglish", "kn-IN": "Kannada"}
SHORT = {  # short names for the chart
    "scam": "police", "family": "family", "upi": "UPI QR", "job": "job",
    "investment": "invest", "customer_care": "care",
    "legit": "bank/delivery", "legit_family": "family ✓", "legit_refund": "refund ✓",
}


SET_TITLES = {"demo": "demo calls", "unseen": "held-out set 1", "blind": "blind held-out set"}
SET_NOTES = {
    "demo": "These are the demo calls the detector was tuned on, so this is close to a best case.",
    "unseen": "Held-out set 1: written after the v1 tuning; the v2 rules were written knowing its misses.",
    "blind": "Blind set: written by a separate agent that never saw the rules, and run only after the rules were frozen.",
}
SET_SUBTITLES = {"demo": " (demo calls, tuned on)", "unseen": " (held-out set 1)",
                 "blind": " (blind set, written without seeing the rules)"}


def call_set(results: list[dict]) -> str:
    """Which set of calls these results come from."""
    keys = {(r["lang"], r["script"]) for r in results}
    if keys & set(BLIND):
        return "blind"
    if keys & set(UNSEEN):
        return "unseen"
    return "demo"


def short(r: dict) -> str:
    """A call's short label for tables and the chart."""
    return r.get("short") or SHORT.get(r["script"], r["script"])


def call_spec(lang: str, script: str) -> tuple[list[str], str | None, str]:
    """(lines, expected scam type or None for a genuine call, short label)."""
    for extra in (UNSEEN, BLIND):
        if (lang, script) in extra:
            u = extra[(lang, script)]
            return u["lines"], u["expected"], u["short"]
    return CALLS[(lang, script)], EXPECTED_TYPE.get(script), SHORT[script]


def all_calls(lang: str | None = None, script: str | None = None, unseen: bool = False,
              blind: bool = False) -> list[tuple[str, str]]:
    """(language, script) for every call in a set, scams first, optionally filtered.
    Sets: the demo calls (default), held-out set 1 (unseen) or the blind set 2."""
    source = list(BLIND) if blind else list(UNSEEN) if unseen else list(CALLS)
    calls = [(l, s) for (l, s) in source if (not lang or l == lang) and (not script or s == script)]

    def key(c):
        lines, expected, _ = call_spec(*c)
        return (list(LANG_NAMES).index(c[0]), expected is None, source.index(c))
    return sorted(calls, key=key)


def phone_quality(pcm: np.ndarray, snr_db: float = 20.0, seed: int = 0) -> np.ndarray:
    """Make clean audio sound like a phone line: keep only 300-3,400 Hz (the
    classic telephone band) and add steady background hiss at the given
    signal-to-noise ratio. Deterministic for a given seed."""
    x = pcm.astype(np.float64)
    spectrum = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / RATE)
    spectrum[(freqs < 300) | (freqs > 3400)] = 0
    x = np.fft.irfft(spectrum, n=len(x))
    speech = x[np.abs(x) > 1e-3]
    if len(speech):
        noise_rms = np.sqrt(np.mean(speech ** 2)) / (10 ** (snr_db / 20))
        x = x + np.random.default_rng(seed).normal(0, noise_rms, len(x))
    return np.clip(x, -32768, 32767).astype("<i2")


async def run_call(lang: str, script: str, noise: bool = False, session_cls=None) -> dict:
    """Play one demo call through Prisma and the detector; return what happened."""
    session_cls = session_cls or GnaniSTTSession
    lines_to_say, expected, label = call_spec(lang, script)
    kind = "scam" if expected else "genuine"
    result = {"lang": lang, "script": script, "short": label, "kind": kind,
              "expected_type": expected, "noise": noise}

    pcm = await build_demo_call(lang, script, lines_to_say)
    if pcm is None:
        return {**result, "error": "Timbre could not make the audio"}
    if noise:
        pcm = phone_quality(pcm)

    stt = session_cls(lang)
    try:
        await stt.connect()
    except Exception as e:  # e.g. too many sessions at once, or no credit
        return {**result, "error": f"Prisma: {e}"}

    det, lines, errors = ScamDetector(), [], []
    t0 = time.monotonic()

    async def receive():
        async for ev in stt.events():
            if ev.get("type") == "transcript" and ev.get("text", "").strip():
                t = time.monotonic() - t0
                r = det.update(ev["text"], t)
                lines.append({"t": round(t, 1), "text": ev["text"], "risk": r.risk,
                              "latency_ms": ev.get("latency")})
            elif ev.get("type") == "error":
                errors.append(str(ev.get("message")))

    receiver = asyncio.create_task(receive())
    frame_s = config.FRAME_BYTES / 2 / config.SAMPLE_RATE
    start = time.monotonic()
    for i, frame in enumerate(to_frames(pcm)):
        await stt.send_frame(frame)
        wait = start + (i + 1) * frame_s - time.monotonic()
        if wait > 0:
            await asyncio.sleep(wait)
    await asyncio.sleep(SETTLE_S)
    receiver.cancel()
    await stt.close()

    return _finish(result, det, round(len(pcm) / RATE, 1), lines, errors)


def _finish(result: dict, det: ScamDetector, duration_s: float, lines: list[dict], errors: list[str]) -> dict:
    """Turn a detector's state after a call into the benchmark's record."""
    kind = result["kind"]
    s = det.summary(duration_s)
    warned = det.level >= 2
    latencies = [l["latency_ms"] for l in lines if isinstance(l["latency_ms"], (int, float))]
    return {
        **result,
        "warned": warned,
        "correct": warned if kind == "scam" else not warned,
        "detected_type": s["scam_type"] if warned else None,
        "type_correct": (s["scam_type"] == result["expected_type"]) if kind == "scam" and warned else None,
        "max_risk": s["max_risk"],
        "warn_t": round(s["warn_t"], 1) if s["warn_t"] is not None else None,
        "time_to_warning_s": s["time_to_warning_s"],
        "duration_s": duration_s,
        "median_latency_ms": statistics.median(latencies) if latencies else None,
        "signs": [g["category"] for g in s["signs"]],
        "transcript": lines,
        "prisma_errors": errors,
    }


def rescore(r: dict) -> dict:
    """Score a saved call again from its Prisma transcript with the current
    detector: no Timbre, no Prisma, no credits. Used to check a tuning change."""
    if "error" in r:
        return r
    det = ScamDetector()
    lines = [{**l, "risk": det.update(l["text"], l["t"]).risk} for l in r["transcript"]]
    base = {k: r[k] for k in ("lang", "script", "short", "kind", "expected_type", "noise") if k in r}
    return {**_finish(base, det, r["duration_s"], lines, r.get("prisma_errors", [])), "rescored": True}


async def run_all(calls, noise=False, concurrency=3, session_cls=None, on_result=None) -> list[dict]:
    """Run several calls at once (each is real-time, so this saves wall-clock time)."""
    sem = asyncio.Semaphore(concurrency)

    async def one(lang, script):
        async with sem:
            r = await run_call(lang, script, noise, session_cls)
            if on_result:
                on_result(r)
            return r

    return await asyncio.gather(*(one(l, s) for l, s in calls))


def _median(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def summarize(results: list[dict]) -> dict:
    ok = [r for r in results if "error" not in r]
    scams = [r for r in ok if r["kind"] == "scam"]
    genuine = [r for r in ok if r["kind"] == "genuine"]
    caught = [r for r in scams if r["warned"]]
    by_lang = {}
    for lang, name in LANG_NAMES.items():
        ls = [r for r in scams if r["lang"] == lang]
        lg = [r for r in genuine if r["lang"] == lang]
        if ls or lg:
            by_lang[name] = {"scams_caught": sum(r["warned"] for r in ls), "scams": len(ls),
                             "false_alarms": sum(r["warned"] for r in lg), "genuine": len(lg)}
    by_type = {}
    for kind in SCAM_NAMES:
        rs = [r for r in scams if r["expected_type"] == kind]
        if rs:
            by_type[SCAM_NAMES[kind]] = {"caught": sum(r["warned"] for r in rs), "calls": len(rs),
                                         "named_right": sum(bool(r["type_correct"]) for r in rs)}
    return {
        "calls": len(results),
        "errors": [f'{r["lang"]} {r["script"]}: {r["error"]}' for r in results if "error" in r],
        "scams": len(scams),
        "scams_caught": len(caught),
        "scams_named_right": sum(bool(r["type_correct"]) for r in caught),
        "genuine": len(genuine),
        "false_alarms": sum(r["warned"] for r in genuine),
        "median_time_to_warning_s": _median([r["time_to_warning_s"] for r in caught]),
        "median_prisma_latency_ms": _median([r["median_latency_ms"] for r in ok]),
        "by_language": by_lang,
        "by_scam_type": by_type,
    }


def headline(s: dict) -> str:
    return (f"Kavach warned on {s['scams_caught']} of {s['scams']} scam calls "
            f"and {s['false_alarms']} of {s['genuine']} genuine calls")


def to_markdown(results: list[dict], s: dict, noise: bool) -> str:
    which = call_set(results)
    out = [f"# Kavach benchmark: {SET_TITLES[which]}\n",
           f"**{headline(s)}.**\n",
           SET_NOTES[which] + " " +
           f"Each call was spoken by Gnani Timbre and streamed through Gnani Prisma "
           f"at real-time speed{' with phone-line audio (300–3,400 Hz plus background hiss, 20 dB)' if noise else ''}. "
           f"Synthetic calls, one stock voice per language."
           f"{' Scores recomputed from the saved Prisma transcripts with the current detector.' if any(r.get('rescored') for r in results) else ''}\n",
           "| Measure | Result |", "|---|---|",
           f"| Scam calls warned | {s['scams_caught']} / {s['scams']} |",
           f"| Scam named correctly | {s['scams_named_right']} / {s['scams_caught']} |",
           f"| False alarms on genuine calls | {s['false_alarms']} / {s['genuine']} |",
           f"| Median time from first warning sign to warning | {s['median_time_to_warning_s']} s |",
           f"| Median Prisma delay per sentence | {s['median_prisma_latency_ms']} ms |", ""]
    out += ["## By language\n", "| Language | Scams warned | False alarms |", "|---|---|---|"]
    out += [f"| {k} | {v['scams_caught']} / {v['scams']} | {v['false_alarms']} / {v['genuine']} |"
            for k, v in s["by_language"].items()]
    out += ["", "## By kind of scam\n", "| Scam | Warned | Named correctly |", "|---|---|---|"]
    out += [f"| {k} | {v['caught']} / {v['calls']} | {v['named_right']} / {v['calls']} |"
            for k, v in s["by_scam_type"].items()]
    out += ["", "## Every call\n",
            "| Language | Call | Kind | Highest risk | Warned at | Detected as |", "|---|---|---|---|---|---|"]
    for r in results:
        if "error" in r:
            out.append(f"| {LANG_NAMES[r['lang']]} | {short(r)} | {r['kind']} | error: {r['error']} | | |")
            continue
        mark = "✅" if r["correct"] else "❌"
        out.append(f"| {LANG_NAMES[r['lang']]} | {short(r)} | {r['kind']} | {mark} {r['max_risk']} | "
                   f"{str(r['warn_t']) + ' s' if r['warn_t'] is not None else '—'} | "
                   f"{SCAM_NAMES.get(r['detected_type'], '—') if r['detected_type'] else '—'} |")
    if s["errors"]:
        out += ["", "## Errors\n"] + [f"- {e}" for e in s["errors"]]
    return "\n".join(out) + "\n"


def chart_svg(results: list[dict], s: dict) -> str:
    """Highest risk per call, scams vs genuine calls, grouped by language, with
    the warning level marked. A static SVG for the README; each bar has a
    native tooltip."""
    ok = [r for r in results if "error" not in r]
    W, H = 900, 412
    left, right, top, bottom = 56, 24, 96, 96
    plot_w, plot_h = W - left - right, H - top - bottom
    langs = [l for l in LANG_NAMES if any(r["lang"] == l for r in ok)]
    group_gap, bar_gap = 28, 4
    n_bars = len(ok)
    bar_w = (plot_w - group_gap * (len(langs) - 1) - bar_gap * max(n_bars - len(langs), 0)) / max(n_bars, 1)
    y = lambda v: top + plot_h * (1 - v / 100)  # noqa: E731
    colors = {"scam": "#2a78d6", "genuine": "#eb6834"}  # reference palette slots 1 and 2

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             f'font-family="system-ui, -apple-system, Segoe UI, sans-serif" role="img" aria-label="{headline(s)}">',
             f'<rect width="{W}" height="{H}" fill="#fcfcfb"/>',
             f'<text x="{left}" y="32" font-size="18" font-weight="600" fill="#0b0b0b">{headline(s)}</text>',
             f'<text x="{left}" y="54" font-size="13" fill="#52514e">Highest risk score per call'
             f'{SET_SUBTITLES[call_set(ok)]}'
             f' · spoken by Gnani Timbre, transcribed live by Gnani Prisma</text>']
    # recessive grid and y-axis labels
    for v in (0, 25, 50, 75, 100):
        parts.append(f'<line x1="{left}" x2="{W - right}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#e7e6e2" stroke-width="1"/>')
        parts.append(f'<text x="{left - 8}" y="{y(v) + 4:.1f}" font-size="11" fill="#52514e" text-anchor="end">{v}</text>')
    # bars
    x = left
    for gi, lang in enumerate(langs):
        group = [r for r in ok if r["lang"] == lang]
        gx0 = x
        for bi, r in enumerate(group):
            h = max(plot_h * r["max_risk"] / 100, 2)
            top_y = top + plot_h - h
            rad = min(4, bar_w / 2)
            # 4px rounded data end, square at the baseline
            path = (f"M{x:.1f},{top + plot_h:.1f} V{top_y + rad:.1f} Q{x:.1f},{top_y:.1f} {x + rad:.1f},{top_y:.1f} "
                    f"H{x + bar_w - rad:.1f} Q{x + bar_w:.1f},{top_y:.1f} {x + bar_w:.1f},{top_y + rad:.1f} V{top + plot_h:.1f} Z")
            tip = (f"{LANG_NAMES[lang]} · {short(r)} ({r['kind']}): highest risk {r['max_risk']}, "
                   f"{'warned' if r['warned'] else 'no warning'}")
            parts.append(f'<path d="{path}" fill="{colors[r["kind"]]}"><title>{tip}</title></path>')
            if not r["correct"]:  # call out mistakes directly
                parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{top_y - 6:.1f}" font-size="12" font-weight="700" '
                             f'fill="#0b0b0b" text-anchor="middle">✕</text>')
            lx, ly = x + bar_w / 2, top + plot_h + 12
            parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="10" fill="#52514e" text-anchor="end" '
                         f'transform="rotate(-40 {lx:.1f} {ly:.1f})">{short(r)}</text>')
            x += bar_w + (bar_gap if bi < len(group) - 1 else 0)
        parts.append(f'<text x="{(gx0 + x) / 2:.1f}" y="{H - 14}" font-size="13" font-weight="600" fill="#0b0b0b" '
                     f'text-anchor="middle">{LANG_NAMES[lang]}</text>')
        x += group_gap
    # the warning level
    parts.append(f'<line x1="{left}" x2="{W - right}" y1="{y(70):.1f}" y2="{y(70):.1f}" stroke="#0b0b0b" '
                 f'stroke-width="1.5" stroke-dasharray="5 4"/>')
    parts.append(f'<text x="{W - right}" y="{y(70) - 6:.1f}" font-size="11" fill="#0b0b0b" text-anchor="end">'
                 f'warns at 70+</text>')
    # legend, on its own line under the subtitle
    for i, (kind, label) in enumerate((("scam", "Scam call"), ("genuine", "Genuine call"))):
        parts.append(f'<rect x="{left + i * 120}" y="62" width="12" height="12" rx="3" fill="{colors[kind]}"/>')
        parts.append(f'<text x="{left + i * 120 + 18}" y="72" font-size="13" fill="#0b0b0b">{label}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
