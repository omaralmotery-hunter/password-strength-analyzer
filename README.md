# 🔐 Password Strength Analyzer

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A professional command-line tool for analyzing password security — built in Python with zero external dependencies.

---

## Features

| Feature | Details |
|---|---|
| **Entropy Calculation** | Bit-level entropy based on charset size and length |
| **Common Password Check** | Built-in list of 200+ commonly used passwords + suffix/prefix/reverse detection |
| **Pattern Detection** | Keyboard walks, sequential runs, repeated chars, dates, leet-speak, palindromes |
| **Crack Time Estimates** | Four attack scenarios from online throttled to GPU-speed offline |
| **Suggestions** | Actionable tips tailored to detected weaknesses |
| **Stronger Alternatives** | Passphrase, enhanced variant, and cryptographically random option |
| **Batch Mode** | Analyze an entire file of passwords at once |
| **JSON Output** | Machine-readable output for scripting/pipelines |
| **Color-coded CLI** | Clear visual hierarchy with ANSI colors |

---

## Project Structure

```
password-strength-analyzer/
├── main.py          # CLI entry point and argument parsing
├── analyzer.py      # Core analysis engine
├── patterns.py      # Pattern detection (walks, sequences, dates…)
├── wordlist.py      # Common password detection
├── suggestions.py   # Tip generation and alternative passwords
├── display.py       # Color-coded terminal output and JSON mode
├── requirements.txt # Dependency specification
├── pyproject.toml   # Project metadata
└── README.md
```

---

## Installation

No external dependencies required — pure Python 3.8+.

```bash
# Clone or copy the directory, then:
cd password-strength-analyzer
python main.py
```

Make it executable (Linux/macOS):

```bash
chmod +x main.py
./main.py
```

---

## Usage

### Interactive Mode (Recommended)
Input is hidden — safe for use on shared or recorded terminals.

```
python main.py
```

### Inline Password
```
python main.py -p "MyP@ssword99"
```
> ⚠️ The password may be saved in shell history. Use interactive mode on shared systems.

### Batch Analysis
Analyze a list of passwords from a file (one per line):

```
python main.py --batch passwords.txt
```

### JSON Output
Pipe into `jq` or other tools:

```
python main.py -p "hunter2" --json | jq .score
```

### Custom Wordlist
Add your own common-password file (one word per line):

```
python main.py --wordlist /path/to/rockyou.txt
```

### All Options

```
usage: passcheck [-h] [-p PASSWORD] [--batch FILE] [--json]
                 [--no-color] [--no-suggestions] [--wordlist FILE]

options:
  -h, --help           Show this help message and exit
  -p, --password       Password to analyze
  --batch FILE         Analyze passwords from a file (one per line)
  --json               Output results as JSON
  --no-color           Disable ANSI colors
  --no-suggestions     Skip suggestions and alternatives section
  --wordlist FILE      Custom wordlist file for common password check
```

---

## Sample Output

```
╔══════════════════════════════════════╗
║   🔐 Password Strength Analyzer v1.0  ║
╚══════════════════════════════════════╝

── OVERVIEW
  Password:          q****y
  Length:            6 characters
  Character set:     a-z (26 possible chars)
  Entropy:           28.20 bits

── STRENGTH
  Weak (22/100)
  [██████░░░░░░░░░░░░░░░░░░░░░░░░] 22%

── COMMON PASSWORD CHECK
  ✖  FOUND in common password database
  Exact match in common password list

── PATTERN ANALYSIS
  ⚠  Keyboard walk detected: "qwerty"
  ⚠  All letters are lowercase

── ESTIMATED CRACK TIME
  Online (throttled, 100/hr)             3 minutes
  Online (unthrottled, 10/s)             30 seconds
  Offline (bcrypt, 10k/s)               Instant
  Offline (MD5, 10B/s)                  Instant

── RECOMMENDATIONS
  ⚠️  This is a well-known password — change it immediately.
  📏 Increase length to at least 16 characters (currently 6).
  🔠 Add uppercase letters (A–Z).
  🔢 Add digits (0–9).
  💥 Add symbols (!@#$%^&* etc.).
  ⌨️  Avoid keyboard walks like 'qwerty' or '12345'.

── STRONGER ALTERNATIVES
  Passphrase:    Prism-Vortex-Ember-Solar7!
  Enhanced:      Qw!93erty!
  Random:        kR7@mNpX!2wLvQ9$Yt
```

---

## How Scoring Works

The score (0–100) is calculated from:

1. **Entropy** (up to 60 pts) — based on charset size × length
2. **Length bonus** (up to 15 pts) — extra credit for passwords > 8 chars
3. **Pattern penalties** — deductions for each weakness found
4. **Common password penalty** — –40 pts for dictionary matches

| Score | Label |
|---|---|
| 0–19 | Very Weak |
| 20–39 | Weak |
| 40–59 | Fair |
| 60–79 | Strong |
| 80–100 | Very Strong |

---

## Using a Large Wordlist (e.g. RockYou)

For maximum coverage, download the RockYou wordlist and pass it in:

```bash
# After obtaining rockyou.txt:
python main.py --wordlist rockyou.txt -p "mypassword"
```

---

## Tips for Strong Passwords

1. **Use a passphrase** — four random words joined by symbols: `Cedar-Frost!Onyx9`
2. **Aim for 16+ characters**
3. **Mix all character classes** — upper, lower, digits, symbols
4. **Avoid personal info** — birthdays, names, places
5. **Use a password manager** — it generates and remembers truly random passwords

---

## License

MIT — free to use, modify, and distribute.
