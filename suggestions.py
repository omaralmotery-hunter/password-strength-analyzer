"""
suggestions.py — Human-readable tips and stronger password alternatives
"""

import random
import secrets
import string
from typing import List


STRONG_WORDS = [
    "Amber", "Falcon", "River", "Cobalt", "Prism",
    "Quartz", "Nebula", "Cipher", "Vortex", "Zenith",
    "Lunar", "Ember", "Frost", "Storm", "Cedar",
    "Onyx", "Solar", "Drift", "Blaze", "Rune",
]

CONNECTORS = ["-", "_", ".", "!", "#", "@"]
SYMBOLS    = "!@#$%^&*()_+-=[]{}|;:,.<>?"
DIGITS     = string.digits


class SuggestionEngine:

    def suggestions(self, password: str, patterns: list, is_common: bool,
                    score: int, charset_info: dict) -> List[str]:
        tips = []

        if is_common:
            tips.append("⚠️  This is a well-known password — change it immediately.")

        if len(password) < 12:
            tips.append(f"📏 Increase length to at least 16 characters (currently {len(password)}).")

        if not charset_info["upper"]:
            tips.append("🔠 Add uppercase letters (A–Z).")
        if not charset_info["lower"]:
            tips.append("🔡 Add lowercase letters (a–z).")
        if not charset_info["digits"]:
            tips.append("🔢 Add digits (0–9).")
        if not charset_info["symbols"]:
            tips.append("💥 Add symbols (!@#$%^&* etc.).")

        pattern_types = {p["type"] for p in patterns}

        if "keyboard_walk" in pattern_types:
            tips.append("⌨️  Avoid keyboard walks like 'qwerty' or '12345'.")
        if "sequential" in pattern_types:
            tips.append("🔢 Avoid sequential runs like 'abcd' or '1234'.")
        if "repeated_chars" in pattern_types:
            tips.append("🔁 Avoid repeating the same character multiple times.")
        if "date" in pattern_types:
            tips.append("📅 Avoid dates — they're easy to guess from social media.")
        if "leet_speak" in pattern_types:
            tips.append("🤖 Simple leet substitutions (@ for 'a') are well-known to crackers.")
        if "common_affix" in pattern_types:
            tips.append("🔚 Avoid appending '123', '!', or similar common suffixes.")
        if "all_lowercase" in pattern_types:
            tips.append("🔠 Mix upper and lowercase letters.")
        if "all_uppercase" in pattern_types:
            tips.append("🔡 Mix upper and lowercase — don't shout the whole thing.")
        if "palindrome" in pattern_types:
            tips.append("🔄 Palindromes (same forwards/backwards) halve your effective entropy.")

        if score >= 80:
            tips.append("✅ Great password! Consider using a password manager to store it safely.")
        elif score >= 60:
            tips.append("💡 Tip: Use a passphrase — four random words joined by symbols.")

        if not tips:
            tips.append("💡 Consider using a password manager to generate and store unique passwords.")

        return tips

    def generate_alternatives(self, password: str) -> List[str]:
        """Generate 3 stronger password alternatives."""
        return [
            self._passphrase(),
            self._enhanced(password),
            self._random_secure(),
        ]

    # ── Generators ─────────────────────────────────────────────────────────

    def _passphrase(self) -> str:
        """Random 4-word passphrase with connector and digit."""
        words = secrets.SystemRandom().sample(STRONG_WORDS, 4)
        connector = secrets.choice(CONNECTORS)
        digit = secrets.choice(DIGITS)
        symbol = secrets.choice("!@#$")
        phrase = connector.join(words)
        return f"{phrase}{digit}{symbol}"

    def _enhanced(self, password: str) -> str:
        """Take the original and make it meaningfully stronger."""
        # Capitalize first letter if not already
        base = password
        if base and base[0].islower():
            base = base[0].upper() + base[1:]

        # Add random symbol + 2 random digits in the middle
        mid = len(base) // 2
        insert = secrets.choice(SYMBOLS) + "".join(secrets.choice(DIGITS) for _ in range(2))
        base = base[:mid] + insert + base[mid:]

        # Append a random symbol
        base += secrets.choice(SYMBOLS)

        return base

    def _random_secure(self) -> str:
        """Cryptographically random 18-character password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        while True:
            pwd = "".join(secrets.choice(alphabet) for _ in range(18))
            # Ensure all character classes present
            if (any(c.isupper() for c in pwd) and
                any(c.islower() for c in pwd) and
                any(c.isdigit() for c in pwd) and
                any(c in SYMBOLS for c in pwd)):
                return pwd
