"""
display.py — Color-coded terminal output and JSON rendering
"""

import json
import sys
from dataclasses import asdict
from typing import List

# ── ANSI color codes ─────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
MAGENTA= "\033[95m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"

STRENGTH_COLORS = {
    "Very Weak":   RED,
    "Weak":        RED,
    "Fair":        YELLOW,
    "Strong":      GREEN,
    "Very Strong": CYAN,
}

SCORE_BAR_COLORS = {
    (0,  20): RED,
    (20, 40): RED,
    (40, 60): YELLOW,
    (60, 80): GREEN,
    (80, 101): CYAN,
}


class Display:
    def __init__(self, color: bool = True, json_mode: bool = False):
        self._color = color and sys.stdout.isatty() or color
        self._json = json_mode

    # ── Color helpers ─────────────────────────────────────────────────────────
    def _c(self, code: str, text: str) -> str:
        if not self._color:
            return text
        return f"{code}{text}{RESET}"

    def _bold(self, text: str) -> str:
        return self._c(BOLD, text)

    def _dim(self, text: str) -> str:
        return self._c(DIM, text)

    # ── Banner ────────────────────────────────────────────────────────────────
    def banner(self):
        if self._json:
            return
        lines = [
            "",
            self._c(CYAN + BOLD, "  ╔══════════════════════════════════════╗"),
            self._c(CYAN + BOLD, "  ║") + self._c(WHITE + BOLD, "   🔐 Password Strength Analyzer v1.0  ") + self._c(CYAN + BOLD, "║"),
            self._c(CYAN + BOLD, "  ╚══════════════════════════════════════╝"),
            "",
        ]
        print("\n".join(lines))

    # ── Full single-password report ───────────────────────────────────────────
    def full_report(self, result, show_suggestions: bool = True):
        self._section("OVERVIEW")
        print(f"  {'Password:':<18} {self._c(DIM, result.masked)}")
        print(f"  {'Length:':<18} {result.length} characters")

        # Charset
        active = []
        if result.charset_breakdown["lower"]:   active.append("a-z")
        if result.charset_breakdown["upper"]:   active.append("A-Z")
        if result.charset_breakdown["digits"]:  active.append("0-9")
        if result.charset_breakdown["symbols"]: active.append("symbols")
        if result.charset_breakdown["unicode"]: active.append("unicode")
        charset_str = ", ".join(active) if active else "none detected"
        print(f"  {'Character set:':<18} {charset_str} ({result.charset_size} possible chars)")
        print(f"  {'Entropy:':<18} {result.entropy} bits")
        print()

        # Strength score bar
        self._section("STRENGTH")
        color = STRENGTH_COLORS.get(result.strength_label, WHITE)
        label = self._c(color + BOLD, f"{result.strength_label} ({result.score}/100)")
        print(f"  {label}")
        print(f"  {self._score_bar(result.score)}")
        print()

        # Common password warning
        self._section("COMMON PASSWORD CHECK")
        if result.is_common:
            print(f"  {self._c(RED + BOLD, '✖  FOUND in common password database')}")
            print(f"  {self._c(GRAY, result.common_reason)}")
        else:
            print(f"  {self._c(GREEN, '✔  Not found in common password database')}")
        print()

        # Patterns
        self._section("PATTERN ANALYSIS")
        if result.patterns:
            for p in result.patterns:
                match_str = f" → \"{p['match']}\"" if p.get("match") else ""
                print(f"  {self._c(YELLOW, '⚠')}  {p['description']}{self._c(DIM, match_str)}")
        else:
            print(f"  {self._c(GREEN, '✔  No problematic patterns detected')}")
        print()

        # Crack times
        self._section("ESTIMATED CRACK TIME")
        for scenario, time_str in result.crack_time_estimates.items():
            # Color-code by severity
            if "Instant" in time_str or "second" in time_str or "minute" in time_str:
                tc = RED
            elif "hour" in time_str or "day" in time_str:
                tc = YELLOW
            elif "year" in time_str and "universe" not in time_str:
                yrs = float(time_str.replace(",", "").split()[0]) if time_str[0].isdigit() else 0
                tc = GREEN if yrs > 100 else YELLOW
            else:
                tc = CYAN
            print(f"  {self._c(GRAY, f'{scenario:<38}')} {self._c(tc + BOLD, time_str)}")
        print()

        if show_suggestions:
            # Tips
            self._section("RECOMMENDATIONS")
            for tip in result.suggestions:
                print(f"  {tip}")
            print()

            # Alternatives
            self._section("STRONGER ALTERNATIVES")
            labels = ["Passphrase", "Enhanced",  "Random"]
            for label, alt in zip(labels, result.alternatives):
                lbl = (label + ":").ljust(14)
                print(f"  {self._c(BLUE, lbl)} {self._c(GREEN + BOLD, alt)}")
            print()

        print(self._c(GRAY, "  " + "─" * 50))
        print()

    # ── Batch output ──────────────────────────────────────────────────────────
    def batch_header(self, count: int):
        print(f"  Analyzing {self._bold(str(count))} passwords...\n")
        header = f"  {'#':<5}{'Password':<22}{'Score':<9}{'Strength':<14}{'Entropy':<10}{'Common?'}"
        print(self._c(BOLD, header))
        print(self._c(GRAY, "  " + "─" * 72))

    def batch_results(self, results: list):
        for i, r in enumerate(results, 1):
            color = STRENGTH_COLORS.get(r.strength_label, WHITE)
            common = self._c(RED, "YES") if r.is_common else self._c(GREEN, "no")
            score_str = self._c(color + BOLD, str(r.score))
            strength  = self._c(color, r.strength_label)
            masked = r.masked[:20].ljust(20)
            print(f"  {str(i):<5}{masked:<22}{score_str:<18}{strength:<23}{r.entropy:<10}{common}")
        print()

    # ── JSON output ───────────────────────────────────────────────────────────
    def json_result(self, result):
        d = asdict(result)
        d.pop("password")           # Never echo plaintext in JSON
        print(json.dumps(d, indent=2))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _section(self, title: str):
        print(self._c(CYAN + BOLD, f"  ── {title} "))

    def _score_bar(self, score: int, width: int = 30) -> str:
        filled = int(score / 100 * width)
        empty  = width - filled
        color = self._bar_color(score)
        bar = self._c(color, "█" * filled) + self._c(GRAY, "░" * empty)
        return f"[{bar}] {score}%"

    def _bar_color(self, score: int) -> str:
        for (lo, hi), color in SCORE_BAR_COLORS.items():
            if lo <= score < hi:
                return color
        return WHITE

    def error(self, msg: str):
        print(f"\n  {self._c(RED + BOLD, '✖  Error:')} {msg}\n", file=sys.stderr)

    def info(self, msg: str):
        print(msg)
