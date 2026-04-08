#!/usr/bin/env python3
"""
Password Strength Analyzer — Main CLI
"""
import sys, argparse, getpass, os
from analyzer import PasswordAnalyzer
from display import Display


def parse_args():
    p = argparse.ArgumentParser(
        prog="passcheck",
        description="🔐 Password Strength Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة:
  python3 main.py                          # تحليل باسوورد (مخفي)
  python3 main.py -p "Ahmed1992"           # باسوورد مباشر
  python3 main.py --predict                # وضع التنبؤ (سؤال وجواب) — بدون API
  python3 main.py --predict --name Ahmed --birth-year 1992
  python3 main.py --predict --api-key sk-ant-xxx  # مع AI (اختياري)
  python3 main.py --batch list.txt         # تحليل ملف
        """)

    p.add_argument("-p", "--password")
    p.add_argument("--batch", metavar="FILE")
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-color", action="store_true")
    p.add_argument("--no-suggestions", action="store_true")
    p.add_argument("--wordlist", metavar="FILE")

    pr = p.add_argument_group("وضع التنبؤ")
    pr.add_argument("--predict", action="store_true", help="توليد باسووردات محتملة من بياناتك")
    pr.add_argument("--api-key", metavar="KEY", dest="api_key",
                    help="Anthropic API key للتوليد بالذكاء الاصطناعي (اختياري)")
    pr.add_argument("--output",  metavar="FILE", help="حفظ التقرير في ملف")
    pr.add_argument("--top",     metavar="N", type=int, help="اعرض أول N باسوورد فقط")

    # بيانات شخصية كـ flags
    pr.add_argument("--name");         pr.add_argument("--last-name", dest="last_name")
    pr.add_argument("--nickname");     pr.add_argument("--birth-year", dest="birth_year")
    pr.add_argument("--birth-day",  dest="birth_day")
    pr.add_argument("--birth-month", dest="birth_month")
    pr.add_argument("--city");         pr.add_argument("--hometown")
    pr.add_argument("--partner");      pr.add_argument("--partner-birth", dest="partner_birth")
    pr.add_argument("--children");     pr.add_argument("--pet")
    pr.add_argument("--team");         pr.add_argument("--player", dest="favorite_player")
    pr.add_argument("--hobbies");      pr.add_argument("--job");  pr.add_argument("--company")
    pr.add_argument("--username");     pr.add_argument("--email-prefix", dest="email_prefix")
    pr.add_argument("--phone-last4", dest="phone_last4")
    pr.add_argument("--phone-last6", dest="phone_last6")
    pr.add_argument("--number",  dest="favorite_number")
    pr.add_argument("--keywords");     pr.add_argument("--notes", dest="extra_notes")

    return p.parse_args()


def main():
    args    = parse_args()
    display = Display(color=not args.no_color, json_mode=args.json)
    display.banner()
    analyzer = PasswordAnalyzer(wordlist_path=args.wordlist)

    if args.predict:
        _run_predict(args, display, analyzer)
        return

    if args.batch:
        try:
            passwords = [l.strip() for l in open(args.batch, encoding="utf-8") if l.strip()]
        except FileNotFoundError:
            display.error(f"ملف مش موجود: {args.batch}"); sys.exit(1)
        display.batch_header(len(passwords))
        display.batch_results([analyzer.analyze(pw) for pw in passwords])
        return

    password = args.password
    if not password:
        try:
            password = getpass.getpass("  أدخل الباسوورد: ")
        except (KeyboardInterrupt, EOFError):
            print(); sys.exit(0)

    if not password:
        display.error("مفيش باسوورد اتكتب."); sys.exit(1)

    result = analyzer.analyze(password)
    if args.json:
        display.json_result(result)
    else:
        display.full_report(result, show_suggestions=not args.no_suggestions)


def _run_predict(args, display, analyzer):
    from info_collector import collect_info, collect_info_from_args
    from predict_display import render_prediction_report

    # جمع البيانات
    flag_map = {
        "first_name": args.name,           "last_name": args.last_name,
        "nickname": args.nickname,         "birth_year": args.birth_year,
        "birth_day": args.birth_day,       "birth_month": args.birth_month,
        "current_city": args.city,         "hometown": args.hometown,
        "partner_name": args.partner,      "partner_birth": args.partner_birth,
        "children": args.children,         "pet_name": args.pet,
        "favorite_team": args.team,        "favorite_player": args.favorite_player,
        "hobbies": args.hobbies,           "job_title": args.job,
        "company": args.company,           "username": args.username,
        "email_prefix": args.email_prefix, "phone_last4": args.phone_last4,
        "phone_last6": args.phone_last6,   "favorite_number": args.favorite_number,
        "keywords": args.keywords,         "extra_notes": args.extra_notes,
    }

    info = (collect_info_from_args(flag_map)
            if any(v for v in flag_map.values())
            else collect_info(display))

    # تحديد المحرك: محلي أو AI
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY", "").strip()

    if api_key:
        print(f"  {display._c(chr(27)+'[96m', '🤖 جاري التحليل بالذكاء الاصطناعي...')}")
        print()
        try:
            from ai_predictor import predict_passwords
            prediction = predict_passwords(info, api_key)
        except Exception as e:
            display.error(f"خطأ في API: {e}\n  هيتم التبديل للتوليد المحلي...")
            prediction = _local_predict(info, display)
    else:
        prediction = _local_predict(info, display)

    candidates = prediction.get("predicted_passwords", [])
    if not candidates:
        display.error("مفيش باسووردات اتولدت."); sys.exit(1)

    if args.top:
        candidates = candidates[:args.top]

    print(f"  {display._c(chr(27)+'[92m', f'✔ تم توليد {len(candidates)} باسوورد — جاري التحليل...')}")
    print()

    analyzed = [
        {"candidate": c, "result": analyzer.analyze(c["password"])}
        for c in candidates if c.get("password")
    ]

    render_prediction_report(prediction, analyzed, display, output_file=args.output)


def _local_predict(info: dict, display) -> dict:
    from local_predictor import generate_passwords
    print(f"  {display._c(chr(27)+'[93m', '⚡ جاري التوليد المحلي (بدون API)...')}")
    print()
    return generate_passwords(info)


if __name__ == "__main__":
    main()
