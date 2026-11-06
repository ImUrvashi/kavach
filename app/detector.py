"""Rule-based scam detector that builds a risk score as a call unfolds.

Each new transcript segment is scanned for red-flag signals. Signals persist
for the whole call (a scam is a story told over minutes), so the score
reflects everything heard so far. The alert level only ever goes up within a
call (hysteresis), so the warning never flickers on and off.
"""
import unicodedata
from dataclasses import dataclass, field

from . import config
from .lexicon import COMBOS, PROTECTIVE, SIGNALS, SUPPRESSED_BY_PROTECTIVE

LEVEL_NAMES = ["safe", "caution", "warn", "alert"]


def _word_end(text: str, end: int) -> int:
    """Extend a match to the end of its word, so a highlight never splits an
    Indic vowel sign from its letter (बता|इए -> बताइए)."""
    while end < len(text) and (text[end].isalnum() or unicodedata.category(text[end]).startswith("M")):
        end += 1
    return end


@dataclass
class Match:
    category: str
    label: str
    start: int
    end: int
    text: str


@dataclass
class UpdateResult:
    risk: int
    level: int
    escalated_to: int | None  # set when this segment raised the level
    scam_type: str
    matches: list[Match]
    new_categories: list[str]


@dataclass
class _Seen:
    label: str
    first_t: float
    phrase: str
    count: int = 1


@dataclass
class ScamDetector:
    seen: dict[str, _Seen] = field(default_factory=dict)
    protective_hits: int = 0
    risk: int = 0
    max_risk: int = 0
    level: int = 0
    level_times: dict[int, float] = field(default_factory=dict)
    first_flag_t: float | None = None
    segments: int = 0

    # ---- scoring -------------------------------------------------------
    def _score(self) -> int:
        cats = set(self.seen)
        score = sum(s.weight for s in SIGNALS if s.category in cats)
        score += sum(bonus for combo, bonus in COMBOS if combo <= cats)
        score += PROTECTIVE.weight * min(self.protective_hits, 1)
        return max(0, min(100, score))

    @staticmethod
    def _level_for(risk: int) -> int:
        if risk >= config.LEVEL_ALERT:
            return 3
        if risk >= config.LEVEL_WARN:
            return 2
        if risk >= config.LEVEL_CAUTION:
            return 1
        return 0

    def scam_type(self) -> str:
        c = set(self.seen)
        if "digital_arrest" in c:
            return "digital_arrest"
        # Checked before the police rule: "your son was arrested" is a family
        # emergency scam even though it mentions police and arrest.
        if "emergency" in c:
            return "emergency"
        if {"authority", "threat"} <= c:
            return "digital_arrest"
        # Story-specific scams first, then the generic signs they also trigger
        # (a fake helpline usually asks for AnyDesk or an OTP too).
        for kind in ("upi_receive", "job", "investment", "customer_care",
                     "credential", "remote", "parcel", "kyc", "utility", "bait", "payment"):
            if kind in c:
                return kind
        return "generic"

    # ---- main entry ----------------------------------------------------
    def update(self, text: str, t: float) -> UpdateResult:
        self.segments += 1
        low = text.lower()  # lowercasing keeps character offsets for highlighting

        protective = []
        for rx in PROTECTIVE.compiled:
            for m in rx.finditer(low):
                e = _word_end(text, m.end())
                protective.append(Match("protective", PROTECTIVE.label, m.start(), e, text[m.start():e]))
        if protective:
            self.protective_hits += 1

        matches: list[Match] = []
        new_categories: list[str] = []
        for sig in SIGNALS:
            if protective and sig.category in SUPPRESSED_BY_PROTECTIVE:
                continue
            for rx in sig.compiled:
                for m in rx.finditer(low):
                    e = _word_end(text, m.end())
                    phrase = text[m.start():e]
                    matches.append(Match(sig.category, sig.label, m.start(), e, phrase))
                    if sig.category in self.seen:
                        self.seen[sig.category].count += 1
                    else:
                        self.seen[sig.category] = _Seen(sig.label, t, phrase)
                        new_categories.append(sig.category)

        if matches and self.first_flag_t is None:
            self.first_flag_t = t

        self.risk = self._score()
        self.max_risk = max(self.max_risk, self.risk)

        escalated_to = None
        new_level = self._level_for(self.risk)
        if new_level > self.level:
            for lv in range(self.level + 1, new_level + 1):
                self.level_times.setdefault(lv, t)
            self.level = new_level
            escalated_to = new_level

        all_matches = sorted(matches + protective, key=lambda m: m.start)
        return UpdateResult(self.risk, self.level, escalated_to, self.scam_type(), all_matches, new_categories)

    def summary(self, duration_s: float) -> dict:
        warn_t = self.level_times.get(2)
        return {
            "duration_s": round(duration_s, 1),
            "segments": self.segments,
            "max_risk": self.max_risk,
            "final_level": LEVEL_NAMES[self.level],
            "scam_type": self.scam_type() if self.seen else None,
            "first_flag_t": self.first_flag_t,
            "warn_t": warn_t,
            "time_to_warning_s": (round(warn_t - self.first_flag_t, 1)
                                  if warn_t is not None and self.first_flag_t is not None else None),
            "signs": [
                {"category": k, "label": v.label, "first_t": round(v.first_t, 1), "phrase": v.phrase, "count": v.count}
                for k, v in sorted(self.seen.items(), key=lambda kv: kv[1].first_t)
            ],
            "protective_hits": self.protective_hits,
        }
