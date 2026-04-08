"""
wordlist.py — Common password detection
"""

import os
from typing import Optional, Tuple

# Embedded top-200 common passwords (no external file needed by default)
COMMON_PASSWORDS = {
    "123456", "password", "123456789", "12345678", "12345", "1234567",
    "qwerty", "abc123", "football", "monkey", "letmein", "shadow",
    "master", "666666", "qwertyuiop", "123321", "mustang", "1234567890",
    "michael", "superman", "batman", "trustno1", "dragon", "baseball",
    "iloveyou", "sunshine", "princess", "welcome", "admin", "login",
    "hello", "charlie", "donald", "password1", "qwerty123", "1q2w3e4r",
    "aa123456", "dragon", "passw0rd", "p@ssword", "p@ssw0rd",
    "pass", "test", "user", "guest", "root", "toor", "alpine",
    "changeme", "secret", "default", "blank", "password123", "letmein1",
    "111111", "222222", "333333", "444444", "555555", "777777", "888888",
    "999999", "000000", "11111111", "22222222", "1111", "12341234",
    "fuckyou", "qazwsx", "zxcvbnm", "asdfgh", "qweasd", "1q2w3e",
    "q1w2e3r4", "a1b2c3", "abc", "abcdef", "abcdefg", "abcdefgh",
    "ninja", "maggie", "jessica", "daniel", "george", "jordan",
    "harley", "ranger", "dakota", "cookie", "cheese", "butter",
    "hunter", "summer", "winter", "spring", "autumn", "forever",
    "freedom", "america", "flower", "soccer", "hockey", "tennis",
    "matrix", "starwars", "stargate", "pokemon", "pikachu", "naruto",
    "android", "windows", "internet", "google", "facebook", "twitter",
    "myspace", "linkedin", "youtube", "amazon", "apple", "microsoft",
    "photoshop", "office", "outlook", "gmail", "yahoo", "hotmail",
    "corvette", "ferrari", "porsche", "mustang", "harley", "davidson",
    "dallas", "boston", "chicago", "london", "paris", "berlin",
    "moscow", "tokyo", "sydney", "toronto", "canada", "mexico",
    "coffee", "burger", "pizza", "tacos", "sushi", "pasta", "bacon",
    "money", "power", "glory", "honor", "noble", "valor", "brave",
    "love", "hate", "hope", "fear", "pain", "joy", "anger",
    "god", "jesus", "allah", "buddha", "christ", "devil", "angel",
}


class WordlistChecker:
    def __init__(self, custom_path: Optional[str] = None):
        self.wordlist = set(COMMON_PASSWORDS)
        if custom_path:
            self._load_file(custom_path)

    def _load_file(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    word = line.strip().lower()
                    if word:
                        self.wordlist.add(word)
        except FileNotFoundError:
            pass  # Custom file missing — fall back to built-in list

    def check(self, password: str) -> Tuple[bool, Optional[str]]:
        """Return (is_common, reason_string)."""
        pw_lower = password.lower()

        # Direct match
        if pw_lower in self.wordlist:
            return True, "Exact match in common password list"

        # Strip trailing digits/symbols and recheck
        stripped = pw_lower.rstrip("0123456789!@#$%^&*")
        if stripped and stripped != pw_lower and stripped in self.wordlist:
            return True, f'Common password with suffix: "{password[len(stripped):]}"'

        # Strip leading digits/symbols and recheck
        stripped2 = pw_lower.lstrip("0123456789!@#$%^&*")
        if stripped2 and stripped2 != pw_lower and stripped2 in self.wordlist:
            return True, f'Common password with prefix: "{password[:len(password)-len(stripped2)]}"'

        # Reversed
        if pw_lower[::-1] in self.wordlist:
            return True, "Common password written in reverse"

        return False, None
