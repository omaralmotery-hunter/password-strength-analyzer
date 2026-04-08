"""
patterns.py — Detect structural weaknesses in passwords
"""

import re
import string
from typing import List, Dict


class PatternDetector:
    """Identifies common password anti-patterns."""

    KEYBOARD_ROWS = [
        "qwertyuiop", "asdfghjkl", "zxcvbnm",
        "1234567890", "qwerty", "azerty",
    ]
    COMMON_SUBSTITUTIONS = {
        "@": "a", "4": "a", "3": "e", "1": "i", "!": "i",
        "0": "o", "5": "s", "$": "s", "7": "t", "+": "t",
    }

    def detect(self, password: str) -> List[Dict]:
        patterns = []
        pw_lower = password.lower()

        checks = [
            self._repeated_chars,
            self._sequential_chars,
            self._keyboard_walk,
            self._date_pattern,
            self._leet_speak,
            self._common_suffix_prefix,
            self._all_same_case,
            self._mirrored,
        ]
        for check in checks:
            result = check(password, pw_lower)
            if result:
                patterns.extend(result if isinstance(result, list) else [result])

        return patterns

    # ── Individual detectors ──────────────────────────────────────────────────

    def _repeated_chars(self, pw: str, pw_lower: str) -> List[Dict]:
        found = []
        # Three or more of the same character
        for m in re.finditer(r"(.)\1{2,}", pw, re.IGNORECASE):
            found.append({
                "type": "repeated_chars",
                "description": f'Repeated character "{m.group(1)}" × {len(m.group())}',
                "match": m.group(),
                "penalty": 8,
            })
        return found

    def _sequential_chars(self, pw: str, pw_lower: str) -> List[Dict]:
        found = []
        seen_spans = []
        for seq_type, charset in [("alphabetic", string.ascii_lowercase),
                                   ("numeric",    string.digits)]:
            for direction in [1, -1]:
                seq = charset if direction == 1 else charset[::-1]
                for i in range(len(seq)):
                    for length in range(min(len(pw), len(seq) - i), 3, -1):
                        chunk = seq[i:i + length]
                        pos = pw_lower.find(chunk)
                        if pos != -1:
                            span = (pos, pos + length)
                            if not any(s[0] <= span[0] and s[1] >= span[1] for s in seen_spans):
                                seen_spans.append(span)
                                found.append({
                                    "type": "sequential",
                                    "description": f"Sequential {seq_type} run: \"{chunk}\"",
                                    "match": chunk,
                                    "penalty": 7,
                                })
                            break
        return found

    def _keyboard_walk(self, pw: str, pw_lower: str) -> List[Dict]:
        found = []
        seen_spans = []
        for row in self.KEYBOARD_ROWS:
            # Find longest match for each position
            for i in range(len(row)):
                for length in range(min(len(pw), len(row) - i), 3, -1):
                    chunk = row[i:i + length]
                    pos = pw_lower.find(chunk)
                    if pos != -1:
                        span = (pos, pos + length)
                        if not any(s[0] <= span[0] and s[1] >= span[1] for s in seen_spans):
                            seen_spans.append(span)
                            found.append({
                                "type": "keyboard_walk",
                                "description": f'Keyboard walk detected: "{chunk}"',
                                "match": chunk,
                                "penalty": 10,
                            })
                        break  # Found longest match starting at i
        return found

    def _date_pattern(self, pw: str, pw_lower: str) -> List[Dict]:
        found = []
        patterns = [
            (r"\b(19|20)\d{2}\b",       "Year pattern (e.g. 1990, 2024)"),
            (r"\b\d{2}[/-]\d{2}[/-]\d{2,4}\b", "Date pattern (DD/MM/YY)"),
            (r"\b(0?[1-9]|1[0-2])(0?[1-9]|[12]\d|3[01])\d{2,4}\b", "Compact date"),
        ]
        for pattern, description in patterns:
            for m in re.finditer(pattern, pw):
                found.append({
                    "type": "date",
                    "description": description,
                    "match": m.group(),
                    "penalty": 6,
                })
        return found

    def _leet_speak(self, pw: str, pw_lower: str) -> List[Dict]:
        """Detect obvious leet substitutions that add little entropy."""
        normalized = pw_lower
        for sub, letter in self.COMMON_SUBSTITUTIONS.items():
            normalized = normalized.replace(sub, letter)
        if normalized != pw_lower and any(c.isalpha() for c in normalized):
            return [{
                "type": "leet_speak",
                "description": "Leet-speak substitutions detected (e.g. @ → a, 3 → e)",
                "match": None,
                "penalty": 5,
            }]
        return []

    def _common_suffix_prefix(self, pw: str, pw_lower: str) -> List[Dict]:
        found = []
        bad_affixes = ["123", "!", "1", "12", "1234", "123456", "!", "!!", "1!", "#1"]
        for affix in bad_affixes:
            if pw.startswith(affix) or pw.endswith(affix):
                found.append({
                    "type": "common_affix",
                    "description": f'Common affix detected: "{affix}"',
                    "match": affix,
                    "penalty": 6,
                })
        return found

    def _all_same_case(self, pw: str, pw_lower: str) -> List[Dict]:
        letters = [c for c in pw if c.isalpha()]
        if len(letters) >= 4:
            if all(c.islower() for c in letters):
                return [{"type": "all_lowercase", "description": "All letters are lowercase", "match": None, "penalty": 5}]
            if all(c.isupper() for c in letters):
                return [{"type": "all_uppercase", "description": "All letters are uppercase", "match": None, "penalty": 5}]
        return []

    def _mirrored(self, pw: str, pw_lower: str) -> List[Dict]:
        if len(pw) >= 4 and pw_lower == pw_lower[::-1]:
            return [{
                "type": "palindrome",
                "description": "Password is a palindrome",
                "match": None,
                "penalty": 8,
            }]
        return []
