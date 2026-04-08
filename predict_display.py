"""
predict_display.py — عرض نتايج التنبؤ بالكامل
"""

RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
RED = "\033[91m"; YL = "\033[93m"; GN = "\033[92m"
CY = "\033[96m"; BL = "\033[94m"; MG = "\033[95m"
WH = "\033[97m"; GR = "\033[90m"

LIKELIHOOD_META = {
    "high":   ("🔴", RED + BOLD,  "عالية"),
    "medium": ("🟡", YL,          "متوسطة"),
    "low":    ("⚪", GR,          "منخفضة"),
}
STRENGTH_COLOR = {
    "Very Weak": RED, "Weak": RED, "Fair": YL,
    "Strong": GN, "Very Strong": CY,
}
RISK_COLOR = {
    "critical": RED + BOLD, "high": RED,
    "medium": YL, "low": GN,
}


def render_prediction_report(prediction: dict, analyzed: list, display, output_file=None):
    c = display._c
    lines = []

    def p(text=""):
        print(text)
        lines.append(text)

    # ── Header ────────────────────────────────────────────────────────────────
    p()
    p(c(CY + BOLD, "  ╔══════════════════════════════════════════════════════╗"))
    p(c(CY + BOLD, "  ║") + c(WH + BOLD, "        🤖 تقرير التنبؤ بالذكاء الاصطناعي            ") + c(CY + BOLD, "║"))
    p(c(CY + BOLD, "  ╚══════════════════════════════════════════════════════╝"))
    p()

    # ── Risk level ────────────────────────────────────────────────────────────
    risk = prediction.get("risk_level", "medium")
    risk_color = RISK_COLOR.get(risk, YL)
    risk_labels = {"critical": "⛔ خطر حرج", "high": "🔴 خطر عالي",
                   "medium": "🟡 خطر متوسط", "low": "🟢 خطر منخفض"}
    risk_ar = risk_labels.get(risk, risk)
    p(c(CY + BOLD, "  ── مستوى الخطر ──────────────────────────"))
    p(f"  {c(risk_color, risk_ar)}")
    p()

    # ── Reasoning ─────────────────────────────────────────────────────────────
    reasoning = prediction.get("reasoning", "")
    if reasoning:
        p(c(CY + BOLD, "  ── استراتيجية التنبؤ ───────────────────"))
        for chunk in _wrap(reasoning, 68):
            p(c(GR, f"  {chunk}"))
        p()

    # ── Risk assessment ───────────────────────────────────────────────────────
    assessment = prediction.get("risk_assessment", "")
    if assessment:
        p(c(CY + BOLD, "  ── تقييم المخاطر ────────────────────────"))
        for chunk in _wrap(assessment, 68):
            p(f"  {c(risk_color, chunk)}")
        p()

    # ── Behavioral patterns ───────────────────────────────────────────────────
    patterns = prediction.get("patterns_identified", [])
    if patterns:
        p(c(CY + BOLD, "  ── الأنماط السلوكية المكتشفة ──────────"))
        for pat in patterns:
            p(f"  {c(YL, '▸')} {pat}")
        p()

    # ── Stats summary ─────────────────────────────────────────────────────────
    total   = len(analyzed)
    n_high  = sum(1 for x in analyzed if x["candidate"].get("likelihood") == "high")
    n_med   = sum(1 for x in analyzed if x["candidate"].get("likelihood") == "medium")
    n_low   = sum(1 for x in analyzed if x["candidate"].get("likelihood") == "low")
    n_weak  = sum(1 for x in analyzed if x["result"].score < 40)
    n_common= sum(1 for x in analyzed if x["result"].is_common)
    avg_sc  = sum(x["result"].score for x in analyzed) / total if total else 0
    avg_ent = sum(x["result"].entropy for x in analyzed) / total if total else 0

    p(c(CY + BOLD, "  ── إحصائيات القائمة ────────────────────"))
    stats = [
        ("إجمالي الباسووردات",      c(WH + BOLD, str(total))),
        ("احتمالية عالية 🔴",        c(RED + BOLD, str(n_high))),
        ("احتمالية متوسطة 🟡",      c(YL, str(n_med))),
        ("احتمالية منخفضة ⚪",      c(GR, str(n_low))),
        ("باسووردات ضعيفة (<40)",   c(RED, str(n_weak))),
        ("موجودة في قوائم شائعة",   c(RED, str(n_common))),
        ("متوسط السكور",             f"{avg_sc:.1f}/100"),
        ("متوسط الـ Entropy",         f"{avg_ent:.1f} bits"),
    ]
    for label, val in stats:
        p(f"  {c(GR, label + ':')}  {val}")
    p()

    # ── Password table ────────────────────────────────────────────────────────
    p(c(CY + BOLD, "  ── قائمة الباسووردات المتوقعة ─────────"))
    p()
    hdr = (f"  {'#':<4}{'احتمال':<10}{'الباسوورد':<28}"
           f"{'سكور':<7}{'قوة':<14}{'Entropy':<10}{'شائع':<6}{'الفئة'}")
    p(c(BOLD, hdr))
    p(c(GR, "  " + "─" * 90))

    for i, item in enumerate(analyzed, 1):
        cand   = item["candidate"]
        res    = item["result"]
        lk     = cand.get("likelihood", "low")
        icon, lc, lk_ar = LIKELIHOOD_META.get(lk, ("⚪", GR, lk))
        sc     = STRENGTH_COLOR.get(res.strength_label, WH)
        pw     = cand["password"]
        pw_disp = (pw[:24] + "…") if len(pw) > 25 else pw
        common_str = c(RED, "نعم") if res.is_common else c(GN, "لا")
        category   = cand.get("category", "—")[:16]

        p(f"  {str(i):<4}"
          f"{c(lc, icon + ' ' + lk_ar):<19}"
          f"{pw_disp:<28}"
          f"{c(sc + BOLD, str(res.score)):<16}"
          f"{c(sc, res.strength_label):<23}"
          f"{res.entropy:<10}"
          f"{common_str:<15}"
          f"{c(GR, category)}")

        reason = cand.get("reason", "")
        if reason:
            p(c(GR, f"  {'':4}└─ {reason}"))

    p()
    p(c(GR, "  " + "═" * 90))
    p()

    # Save to file if requested
    if output_file:
        _save_report(output_file, analyzed, lines)


def _wrap(text: str, width: int):
    words = text.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > width:
            yield line.rstrip()
            line = word + " "
        else:
            line += word + " "
    if line.strip():
        yield line.rstrip()


def _save_report(path: str, analyzed: list, lines: list):
    """Save plain-text report + password-only list."""
    # Clean ANSI from lines
    import re
    ansi_escape = re.compile(r"\033\[[0-9;]*m")

    report_path = path if path.endswith(".txt") else path + "_report.txt"
    pwlist_path = path.replace(".txt", "") + "_passwords.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(ansi_escape.sub("", line) + "\n")

    with open(pwlist_path, "w", encoding="utf-8") as f:
        f.write("# قائمة الباسووردات المتوقعة\n")
        f.write(f"# الإجمالي: {len(analyzed)}\n\n")
        # High first
        for lk in ["high", "medium", "low"]:
            items = [x for x in analyzed if x["candidate"].get("likelihood") == lk]
            if items:
                ar = {"high": "عالية", "medium": "متوسطة", "low": "منخفضة"}[lk]
                f.write(f"\n# ── احتمالية {ar} ──\n")
                for item in items:
                    pw   = item["candidate"]["password"]
                    sc   = item["result"].score
                    ent  = item["result"].entropy
                    cat  = item["candidate"].get("category", "")
                    rsn  = item["candidate"].get("reason", "")
                    f.write(f"{pw}\t[score:{sc}] [entropy:{ent}] [{cat}] {rsn}\n")

    print(f"\033[92m  ✔ التقرير الكامل: {report_path}")
    print(f"  ✔ قائمة الباسووردات: {pwlist_path}\033[0m\n")
