"""
analyzer.py — Core password analysis engine
"""

import math
import re
import os
import string
from dataclasses import dataclass, field
from typing import List, Optional
from patterns import PatternDetector
from suggestions import SuggestionEngine
from wordlist import WordlistChecker


# ── Scoring constants ────────────────────────────────────────────────────────
SCORE_THRESHOLDS = {
    "Very Weak":  (0,  20),
    "Weak":       (20, 40),
    "Fair":       (40, 60),
    "Strong":     (60, 80),
    "Very Strong":(80, 101),
}


@dataclass
class AnalysisResult:
    password: str
    masked: str
    length: int
    entropy: float
    charset_size: int
    charset_breakdown: dict
    score: int                          # 0–100
    strength_label: str
    is_common: bool
    common_reason: Optional[str]
    patterns: List[dict]
    suggestions: List[str]
    alternatives: List[str]
    crack_time_estimates: dict


class PasswordAnalyzer:
    def __init__(self, wordlist_path: Optional[str] = None):
        self.pattern_detector = PatternDetector()
        self.suggestion_engine = SuggestionEngine()
        self.wordlist_checker = WordlistChecker(wordlist_path)

    # ── Public API ────────────────────────────────────────────────────────────
    def analyze(self, password: str) -> AnalysisResult:
        masked        = self._mask(password)
        length        = len(password)
        charset_info  = self._charset_info(password)
        charset_size  = charset_info["total"]
        entropy       = self._entropy(length, charset_size)
        patterns      = self.pattern_detector.detect(password)
        is_common, common_reason = self.wordlist_checker.check(password)
        score         = self._score(password, entropy, patterns, is_common, length)
        strength      = self._label(score)
        crack_times   = self._crack_times(entropy)
        suggestions   = self.suggestion_engine.suggestions(
            password, patterns, is_common, score, charset_info
        )
        alternatives  = self.suggestion_engine.generate_alternatives(password)

        return AnalysisResult(
            password=password,
            masked=masked,
            length=length,
            entropy=round(entropy, 2),
            charset_size=charset_size,
            charset_breakdown=charset_info,
            score=score,
            strength_label=strength,
            is_common=is_common,
            common_reason=common_reason,
            patterns=patterns,
            suggestions=suggestions,
            alternatives=alternatives,
            crack_time_estimates=crack_times,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _mask(password: str) -> str:
        if len(password) <= 4:
            return "*" * len(password)
        return password[0] + "*" * (len(password) - 2) + password[-1]

    @staticmethod
    def _charset_info(password: str) -> dict:
        has_lower   = bool(re.search(r"[a-z]", password))
        has_upper   = bool(re.search(r"[A-Z]", password))
        has_digit   = bool(re.search(r"\d", password))
        has_symbol  = bool(re.search(r"[^a-zA-Z0-9]", password))
        has_unicode = any(ord(c) > 127 for c in password)

        size = (
            (26 if has_lower   else 0) +
            (26 if has_upper   else 0) +
            (10 if has_digit   else 0) +
            (32 if has_symbol  else 0) +
            (1114111 if has_unicode else 0)  # full Unicode plane estimate
        )
        return {
            "total":   max(size, 1),
            "lower":   has_lower,
            "upper":   has_upper,
            "digits":  has_digit,
            "symbols": has_symbol,
            "unicode": has_unicode,
        }

    @staticmethod
    def _entropy(length: int, charset: int) -> float:
        if charset <= 1 or length == 0:
            return 0.0
        return length * math.log2(charset)

    @staticmethod
    def _score(password: str, entropy: float, patterns: list,
               is_common: bool, length: int) -> int:
        score = 0

        # Entropy component (up to 60 pts)
        score += min(60, int(entropy * 60 / 128))

        # Length bonus (up to 15 pts)
        score += min(15, (length - 8) * 2) if length > 8 else 0

        # Pattern penalties
        penalty = sum(p.get("penalty", 5) for p in patterns)
        score -= penalty

        # Common password hard penalty
        if is_common:
            score -= 40

        return max(0, min(100, score))

    @staticmethod
    def _label(score: int) -> str:
        for label, (lo, hi) in SCORE_THRESHOLDS.items():
            if lo <= score < hi:
                return label
        return "Very Weak"

    @staticmethod
    def _crack_times(entropy: float) -> dict:
        """Estimate crack time at various attack speeds."""
        speeds = {
            "Online (throttled, 100/hr)":    100 / 3600,
            "Online (unthrottled, 10/s)":    10,
            "Offline (bcrypt, 10k/s)":       10_000,
            "Offline (MD5, 10B/s)":          10_000_000_000,
        }
        combinations = 2 ** entropy
        results = {}
        for scenario, guesses_per_sec in speeds.items():
            seconds = combinations / guesses_per_sec
            results[scenario] = _human_time(seconds)
        return results


def _human_time(seconds: float) -> str:
    if seconds < 1:
        return "Instant"
    units = [
        (60,             "second"),
        (3600,           "minute"),
        (86400,          "hour"),
        (86400 * 365,    "day"),
        (86400 * 365 * 1000, "year"),
    ]
    for limit, unit in units:
        if seconds < limit:
            val = seconds / (limit // 60 if unit != "second" else 1)
            val = max(1, int(val))
            return f"{val:,} {unit}{'s' if val != 1 else ''}"
    years = seconds / (86400 * 365)
    if years > 1e12:
        return "Longer than the age of the universe"
    return f"{years:,.0f} years"
