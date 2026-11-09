# Kavach: a real-time scam call shield for Indian families

Kavach listens to a phone call on speakerphone, spots a scam as it unfolds in
Hindi, Hinglish or Kannada, and warns the listener out loud in their own
language, optionally in a family member's cloned voice, before any money is lost.

**Demo video:** _link coming_

Built for the Great Indian AI Internship Challenge on Gnani AI's models:

- **Gnani Prisma** (speech to text, realtime WebSocket) transcribes the call live,
  with word boosting for scam vocabulary like CBI, OTP, AnyDesk and UPI.
- **Gnani Timbre** (text to speech, with voice cloning) speaks calm, clear warnings.

## The problem

Phone scams in India no longer look like spam. A caller claims to be the CBI,
a courier company, a bank or your own son on a new number, keeps you on the
line, builds fear or urgency, and talks you into moving money while you're
still on the call. "Digital arrest" calls can last hours. The people most
targeted, often parents and grandparents, are alone on the call when it
matters, and many think in Hindi or Kannada rather than English.

Kavach is the family member sitting next to them: it hears the call, knows
the shape of the common scams, and says "this is a scam, hang up" in their
language at the moment it becomes one.

## How it works

```
Browser mic --16 kHz PCM frames--> Kavach server --> Gnani Prisma (realtime STT)
                                         |
                              transcript segments
                                         v
                          Scam detector (risk 0-100)
                                         |
                       risk >= 70: spoken warning (Gnani Timbre)
                       risk >= 85: firm "hang up now" + helpline 1930
```

The detector looks for the signals that make up common Indian phone scams:
claims of police or government authority, threats of arrest, "digital arrest",
demands for secrecy, urgency, requests to move money, OTP or PIN requests,
remote-access apps, parcel stories, KYC or electricity-cut threats,
lottery or "sent by mistake" stories, family-emergency calls, "scan this QR
to receive money", paid part-time jobs, guaranteed-return investments and
fake customer care. Signals combine into a risk score, and genuine safety
advice ("the bank never asks for your OTP") lowers it. Signals are grouped
into the shape most phone scams share: a story, pressure, and a request for
money, a secret code or access; a request that comes with a story or
pressure raises the score sharply. It names 13 kinds of scam.

The detector is rules, not a model, on purpose: it adds no delay on top of
Prisma, works the same in all three languages and scripts, and every warning
can be explained by pointing at the exact words that triggered it.

When Kavach warns, it also shows the listener two or three questions to ask
the caller, such as "I'll call your office back on its official number". A
genuine caller agrees; a scammer refuses. After the call, a short report
(verdict, key moments, what Kavach said) can be copied and sent to family.

**Why Prisma and Timbre.** A warning is only useful mid-call, so speed
matters: Prisma returned each sentence about 140 ms after it ended in our
tests, and it handles Hindi, Kannada and code-mixed Hinglish. Word boosting
helps it catch the words scams depend on (CBI, OTP, AnyDesk, UPI). Timbre
speaks the warnings in the listener's language, and its voice cloning lets
the warning come in the voice of someone they trust.

## Results

Kavach was tested four ways, from easiest to hardest. Everything below uses
the current rules (lexicon v2, Nov 9). All calls are synthetic.

| Test | What it is | Scams warned | False alarms |
|---|---|---|---|
| Demo calls | 27 calls I wrote and tuned the rules on | 18 / 18 | 0 / 9 |
| **Blind set** | **30 calls written by a separate AI agent that never saw the rules; run once, after the rules were frozen** | **11 / 15** | **2 / 15** |
| ICFD-31k test split | 4,477 fraud-call transcripts by other researchers ([IJCAI 2026](https://www.ijcai.org/proceedings/2026/786)); never inspected | **61%** (2,736) | not measurable* |
| ICFD-31k cross-domain | 961 transcripts of five fraud types held out by the dataset's authors | 26% (251) | not measurable* |

\* ICFD-31k is about 99% fraud calls, and its few "normal" calls are mostly
failed scam attempts, so false alarms are measured on Kavach's own genuine
calls only.

For the demo and blind sets, every call is spoken by Gnani Timbre and
streamed through Gnani Prisma at real-time speed, exactly like a live call.
Prisma returned each sentence a median **140–170 ms** after it ended. A run
over a simulated phone line (300–3,400 Hz plus background hiss) gave the
same results except one blind scam (10 / 15). The ICFD-31k transcripts are
scored as text, with no audio.

![Highest risk per call in the blind set](assets/benchmark_blind.svg)

### How the rules got here, honestly

1. **v1 rules, tuned on the 27 demo calls:** 18 / 18 there. On 15 new calls
   I wrote afterwards (held-out set 1), only **4 / 9** scams. On ICFD-31k,
   about **11%**. The rules had learned the *words* of my calls, not the
   *idea* of a scam.
2. **v2 rules:** rebuilt around the shape almost every phone scam shares:
   a **story** (police, bank, prize, job, courier, tech support, loan…),
   **pressure** (threats, urgency, secrecy) and a **request** (money, a
   secret code, an app, a QR, a personal wallet). A request inside a story
   or under pressure scores high, whatever the exact words. The vocabulary
   was widened in English, Hindi and Kannada using ICFD-31k's *validation*
   split and held-out set 1, which are therefore development data now.
3. **Measured on data the rules never saw:** ICFD-31k test went from 11% to
   61%, cross-domain from 3% to 26%, and the blind set scored 11 / 15 with
   2 false alarms.

The gap between ICFD validation (77%) and test (61%) shows that some of the
gain is still fitting the development data; the test figure is the one to
trust.

### What the blind set shows

Every mistake is something keyword rules cannot do:

- **Negation:** "आपको कुछ भी भुगतान नहीं करना है" ("you don't need to pay
  anything") counted as a payment request. A power-maintenance notice
  became a false alarm.
- **Whose account:** "put money into your account before the EMI date"
  looked like "send money". A genuine loan reminder became a false alarm.
- **Description instead of the word:** "the three-digit number on the back
  of your card" is the CVV, but the word CVV is never said.
- **Thin Kannada:** "tell me the verification code" and "technical support"
  in Kannada aren't covered yet.

These are the reasons for the next step: a small language model that reads
the transcript when the rules are unsure. It would understand meaning, so
negation, paraphrase and new scam types stop being blind spots. The rules
would stay as the fast, explainable first line.

<details>
<summary>Charts for the demo calls and held-out set 1</summary>

![Highest risk per demo call](assets/benchmark_demo_calls.svg)

![Highest risk per call in held-out set 1](assets/benchmark_held_out.svg)

</details>

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste your Gnani API key into .env
python -m pytest -q         # 126 tests, offline, no API calls
```

## Run

```bash
python -m uvicorn app.server:app --port 8000
```

Open http://localhost:8000. Use Chrome or Edge; the mic only works on
localhost or HTTPS.

- **No API key yet?** Kavach starts in demo mode and plays scripted synthetic
  calls so you can see the detector and UI working.
- **With a key:** pick the call's language, click *Start listening*, and put
  the phone on speaker next to the laptop.
- **Demo calls with a key:** choose *Listen to: A demo call*. A scripted scam
  is spoken by Gnani Timbre and streamed through Gnani Prisma exactly like a
  real call, so you hear the caller and see real transcription and scoring.

To save the demo calls as audio files (for example, to play one from a
second phone during a live test):

```bash
python scripts/export_demo_calls.py --lang hi-IN --script upi
```

## Run the benchmark

```bash
python scripts/benchmark.py                 # 27 demo calls, clean audio
python scripts/benchmark.py --noise         # the same calls over a simulated phone line
python scripts/benchmark.py --unseen        # held-out set 1 (development data since v2)
python scripts/benchmark.py --blind         # blind held-out set 2
python scripts/benchmark.py --rescore       # re-score saved transcripts after a change (free)
python scripts/eval_icfd.py                 # ICFD-31k transcripts, text only (free, ~10 s)
```

ICFD-31k isn't included in this repository. `scripts/eval_icfd.py` explains
how to download its evaluation files (about 5 MB) from Hugging Face. It is
released for defensive research and education; cite Ahuja, Prateek and
Singh, *ICFD-31k*, IJCAI 2026.

Results go to `cache/benchmark*/` as `results.md`, `results.json` and
`chart.svg`. A full run takes about 4 minutes and uses Prisma and Timbre
credits; spoken lines are cached, so re-runs only use Prisma.

## Warn in a family member's voice (optional)

With their consent, record 10-20 seconds of them speaking naturally, then:

```bash
python scripts/clone_voice.py reference.wav
python scripts/prewarm_warnings.py
```

`prewarm_warnings.py` generates every warning once and caches it, so warnings
play instantly during calls and don't spend credits again. Listen to the
results in `cache/listen/`.

## Test a recorded synthetic call

```bash
python scripts/stream_file.py call.wav --lang hi-IN
```

## Project layout

| Path | What it does |
|---|---|
| `app/server.py` | FastAPI app: serves the page, relays mic audio to Prisma, sends transcripts, risk and warnings back |
| `app/stt.py` | Prisma realtime client (and a scripted stand-in for demo mode) |
| `app/lexicon.py` | The scam signals and their weights, in Latin, Devanagari and Kannada script |
| `app/detector.py` | Turns transcript lines into a risk score, level and scam type |
| `app/warnings_text.py`, `app/ask_caller.py` | What Kavach says, and the questions it suggests |
| `app/tts.py` | Timbre client: one request at a time, retries, cached clips, cloned voice |
| `app/demo_audio.py`, `app/mock_calls.py` | Spoken demo calls and their scripts |
| `app/benchmark.py` | The end-to-end benchmark (Timbre to Prisma to detector) |
| `app/unseen_calls.py`, `app/blind_calls.py` | Held-out set 1 (development data since v2) and the blind set 2 |
| `scripts/eval_icfd.py` | Scores the detector on ICFD-31k transcripts |
| `static/index.html` | The whole UI: risk shield, live transcript, warnings, ask card, call report |

## Limitations and next steps

- **Synthetic calls only.** No real scam recordings were used. Real callers
  talk over each other, use regional accents and change scripts; the next
  step is testing on consented real-world audio.
- **Rules don't understand meaning.** They miss negation ("you don't need
  to pay"), paraphrase ("the three-digit number on the back") and new scam
  types (26% on ICFD-31k's held-out fraud types). The planned next layer is
  a small language model that reads the transcript when the rules are
  unsure, while the rules stay as the fast, explainable first line.
- **Speakerphone only.** Kavach hears the call through the laptop or phone
  microphone. A phone app or a telecom-side integration would remove that
  step.
- **Kannada was checked less than Hindi.** The Kannada patterns and warnings
  need review by more native speakers.

## Privacy and safety

- All test calls are synthetic. No real call recordings, phone numbers,
  Aadhaar or PAN numbers are used.
- Kavach never hangs up a call by itself; the person stays in control.
- Audio is streamed for transcription and not stored by Kavach.
- Voice cloning is used only with the speaker's consent.
