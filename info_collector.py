"""
info_collector.py — جمع البيانات الشخصية الكاملة
"""
import sys

SECTIONS = [
    ("═══ البيانات الأساسية ═══", [
        ("first_name",       "الاسم الأول",                    "مثال: Ahmed"),
        ("last_name",        "اسم العيلة",                     "مثال: Hassan"),
        ("nickname",         "الكنية / اللقب",                 "مثال: Hamada, Besho"),
        ("initials",         "الحروف الأولى",                  "مثال: AH, AMH"),
    ]),
    ("═══ تاريخ الميلاد ═══", [
        ("birth_year",       "سنة الميلاد",                    "مثال: 1995"),
        ("birth_month",      "شهر الميلاد",                    "مثال: 03 أو March"),
        ("birth_day",        "يوم الميلاد",                    "مثال: 23"),
        ("birth_full",       "التاريخ كامل",                   "مثال: 23031995 أو 23/03/1995"),
    ]),
    ("═══ المقربون ═══", [
        ("partner_name",     "اسم الشريك / الزوج / الزوجة",   "مثال: Sara"),
        ("partner_birth",    "سنة ميلاد الشريك",               "مثال: 1997"),
        ("children",         "أسماء الأطفال",                  "افصل بفاصلة — مثال: Youssef, Nour"),
        ("mother_name",      "اسم الأم",                       "مثال: Mona"),
        ("father_name",      "اسم الأب",                       "مثال: Mohamed"),
        ("best_friend",      "اسم أقرب صديق",                  "مثال: Karim"),
    ]),
    ("═══ الحيوانات والأماكن ═══", [
        ("pet_name",         "اسم الأليف",                     "مثال: Max, Luna"),
        ("hometown",         "مدينة الميلاد",                  "مثال: Aswan"),
        ("current_city",     "المدينة الحالية",                "مثال: Cairo, Alex"),
        ("neighborhood",     "الحي / المنطقة",                 "مثال: Maadi, Zamalek"),
        ("school",           "المدرسة أو الجامعة",             "مثال: AUC, Ain Shams"),
    ]),
    ("═══ الاهتمامات ═══", [
        ("favorite_team",    "الفريق المفضل",                  "مثال: Ahly, Zamalek, Liverpool"),
        ("favorite_player",  "اللاعب المفضل",                  "مثال: Salah, Zizou"),
        ("hobbies",          "الهوايات",                       "مثال: gaming, music, football"),
        ("favorite_movie",   "الفيلم / المسلسل المفضل",        "مثال: Naruto, Breaking Bad"),
        ("favorite_singer",  "المغني / الفرقة المفضلة",        "مثال: Amr Diab, Drake"),
        ("favorite_color",   "اللون المفضل",                   "مثال: blue, red"),
    ]),
    ("═══ الشغل والتقنية ═══", [
        ("job_title",        "المسمى الوظيفي",                 "مثال: engineer, doctor"),
        ("company",          "الشركة / المؤسسة",               "مثال: Vodafone, CIB"),
        ("username",         "اليوزر نيم المعتاد",             "مثال: ahmed95, hamada_x"),
        ("email_prefix",     "أول الإيميل (قبل @)",           "مثال: ahmed.hassan"),
    ]),
    ("═══ أرقام مهمة ═══", [
        ("favorite_number",  "الرقم المفضل",                   "مثال: 7, 77"),
        ("phone_last4",      "آخر 4 أرقام من التليفون",        "مثال: 7890"),
        ("phone_last6",      "آخر 6 أرقام من التليفون",        "مثال: 457890"),
        ("national_id_hint", "أول أو آخر 4 من الرقم القومي",   "مثال: 2995 (اختياري جداً)"),
        ("lucky_number",     "رقم التميمة / رقم الميلاد",      "مثال: 10, 99"),
    ]),
    ("═══ كلمات إضافية ═══", [
        ("keywords",         "كلمات مهمة تانية",               "أي حاجة ليها معنى خاص — افصل بفاصلة"),
        ("old_passwords",    "باسووردات قديمة أو أنماط معروفة","مثال: كنت بحط اسمي + سنتي دايماً"),
        ("extra_notes",      "ملاحظات إضافية",                 "أي تفاصيل تانية تعتقد إنها مهمة"),
    ]),
]


def collect_info(display) -> dict:
    c = display._c
    CY = "\033[96m"
    YL = "\033[93m"
    GR = "\033[90m"
    GN = "\033[92m"
    BD = "\033[1m"

    print()
    print(c(YL + BD, "  ╔══════════════════════════════════════════╗"))
    print(c(YL + BD, "  ║  ") + c(BD, " استيفاء البيانات الشخصية الكاملة      ") + c(YL + BD, "║"))
    print(c(YL + BD, "  ╚══════════════════════════════════════════╝"))
    print()
    print(c(GR, "  ⚡ كل الحقول اختيارية — اضغط Enter لأي حقل مش عارفه أو مش بدك تحطه"))
    print(c(GR, "  🔒 البيانات بتتحلل محلياً + بتتبعت لـ Claude API فقط للتحليل"))
    print()

    info = {}
    filled = 0

    for section_title, fields in SECTIONS:
        print(c(CY + BD, f"\n  {section_title}"))

        for key, arabic_label, hint in fields:
            try:
                val = input(f"  {c(GN, arabic_label)}{c(GR, f' ({hint})')}: ").strip()
            except (KeyboardInterrupt, EOFError):
                print()
                sys.exit(0)

            if val:
                info[key] = val
                filled += 1

    print()
    print(c(GN, f"  ✔ تم جمع {filled} معلومة — جاري التحليل..."))
    print()

    if filled < 2:
        display.error("محتاج معلومتين على الأقل.")
        sys.exit(1)

    return info


def collect_info_from_args(args_dict: dict) -> dict:
    return {k: v for k, v in args_dict.items() if v}
