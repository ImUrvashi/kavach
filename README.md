# Kavach: a real-time scam call shield for Indian families

Kavach listens to a phone call on speakerphone, spots a scam as it unfolds in
Hindi, Hinglish or Kannada, and warns the listener out loud in their own
language, optionally in a family member's cloned voice, before any money is lost.

Built for the Great Indian AI Internship Challenge on Gnani AI's models:

- **Gnani Prisma** (speech to text, realtime WebSocket) transcribes the call live,
  with word boosting for scam vocabulary like CBI, OTP and AnyDesk.
- **Gnani Timbre** (text to speech, with voice cloning) speaks calm, clear warnings.

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
advice ("the bank never asks for your OTP") lowers it.

When Kavach warns, it also shows the listener two or three questions to ask
the caller, such as "I'll call your office back on its official number". A
genuine caller agrees; a scammer refuses.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste your Gnani API key into .env
python -m pytest -q         # detector tests
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

## Privacy and safety

- All test calls are synthetic. No real call recordings, phone numbers,
  Aadhaar or PAN numbers are used.
- Kavach never hangs up a call by itself; the person stays in control.
- Audio is streamed for transcription and not stored by Kavach.
- Voice cloning is used only with the speaker's consent.
