"""
local_predictor.py — توليد باسووردات محلي بالكامل بدون API
بيطبّق نفس القواعد اللي بيستخدمها الناس في بناء باسووردات من بياناتهم الشخصية
"""

from itertools import product as iproduct

# ── استبدالات اللييت سبيك ─────────────────────────────────────────────────
LEET_MAP = {
    'a': ['@', '4'],
    'e': ['3'],
    'i': ['1', '!'],
    'o': ['0'],
    's': ['5', '$'],
    't': ['7'],
    'l': ['1'],
    'g': ['9'],
}

# ── لاحقات شائعة ──────────────────────────────────────────────────────────
COMMON_SUFFIXES = [
    '1', '12', '123', '1234', '12345',
    '!', '!!', '!1', '1!', '#',
    '01', '99', '00', '007',
]

# ── بادئات شائعة ──────────────────────────────────────────────────────────
COMMON_PREFIXES = ['the', 'my', 'mr', 'dr', 'mr.', 'dr.', '1', '01']

# ── رموز وصل شائعة ───────────────────────────────────────────────────────
CONNECTORS = ['', '_', '.', '-', '@', '#']


def generate_passwords(info: dict) -> dict:
    """
    نقطة الدخول الرئيسية — بتاخد dict بالبيانات وبترجع dict على نفس شكل AI
    """
    tokens   = _extract_tokens(info)
    raw_list = _apply_rules(tokens, info)

    # إزالة المكررات مع الحفاظ على الترتيب
    seen = set()
    unique = []
    for item in raw_list:
        if item['password'] not in seen:
            seen.add(item['password'])
            unique.append(item)

    patterns = _detect_patterns(tokens)
    risk     = _assess_risk(tokens, unique)

    return {
        "reasoning": _build_reasoning(info, tokens),
        "predicted_passwords": unique,
        "patterns_identified": patterns,
        "risk_level": risk['level'],
        "risk_assessment": risk['text'],
    }


# ── استخراج الـ tokens من البيانات ──────────────────────────────────────────
def _extract_tokens(info: dict) -> dict:
    """تحويل البيانات الخام لـ tokens جاهزة للمعالجة."""
    t = {}

    # الأسماء
    fn = info.get('first_name', '')
    ln = info.get('last_name', '')
    nn = info.get('nickname', '')
    ini = info.get('initials', '')

    t['first']    = fn.strip()
    t['last']     = ln.strip()
    t['nick']     = nn.strip()
    t['initials'] = ini.strip()
    t['fullname'] = (fn + ln).strip()
    t['full_sep'] = (fn + '_' + ln).strip() if fn and ln else ''

    # تواريخ
    by = info.get('birth_year', '')
    bm = info.get('birth_month', '')
    bd = info.get('birth_day', '')
    bf = info.get('birth_full', '')

    t['year']      = by.strip()
    t['year2']     = by[-2:] if len(by) >= 2 else ''
    t['month']     = bm.strip().zfill(2) if bm.strip().isdigit() else bm.strip()
    t['day']       = bd.strip().zfill(2) if bd.strip().isdigit() else bd.strip()
    t['daymonth']  = (bd.zfill(2) + bm.zfill(2)) if bd and bm else ''
    t['monthday']  = (bm.zfill(2) + bd.zfill(2)) if bd and bm else ''
    t['fulldate']  = bf.replace('/', '').replace('-', '').strip()
    t['yearmonth'] = (by + bm.zfill(2)) if by and bm else ''

    # مقربون
    t['partner']  = info.get('partner_name', '').strip()
    t['p_year']   = info.get('partner_birth', '').strip()
    t['children'] = [c.strip() for c in info.get('children', '').split(',') if c.strip()]
    t['mother']   = info.get('mother_name', '').strip()
    t['father']   = info.get('father_name', '').strip()
    t['friend']   = info.get('best_friend', '').strip()

    # أماكن
    t['city']     = info.get('current_city', '').strip()
    t['hometown'] = info.get('hometown', '').strip()
    t['hood']     = info.get('neighborhood', '').strip()
    t['school']   = info.get('school', '').strip()

    # اهتمامات
    t['team']     = info.get('favorite_team', '').strip()
    t['player']   = info.get('favorite_player', '').strip()
    t['hobbies']  = [h.strip() for h in info.get('hobbies', '').split(',') if h.strip()]
    t['movie']    = info.get('favorite_movie', '').strip()
    t['singer']   = info.get('favorite_singer', '').strip()
    t['color']    = info.get('favorite_color', '').strip()

    # شغل
    t['job']      = info.get('job_title', '').strip()
    t['company']  = info.get('company', '').strip()
    t['username'] = info.get('username', '').strip()
    t['email_pfx']= info.get('email_prefix', '').strip()

    # أرقام
    t['ph4']      = info.get('phone_last4', '').strip()
    t['ph6']      = info.get('phone_last6', '').strip()
    t['fav_num']  = info.get('favorite_number', '').strip()
    t['id_hint']  = info.get('national_id_hint', '').strip()

    # كلمات إضافية
    extras = info.get('keywords', '')
    t['keywords'] = [k.strip() for k in extras.split(',') if k.strip()]

    # تنظيف الـ tokens الفارغة
    return {k: v for k, v in t.items() if v}


# ── تطبيق القواعد ─────────────────────────────────────────────────────────
def _apply_rules(t: dict, info: dict) -> list:
    results = []

    def add(password, likelihood, category, reason):
        if len(password) >= 4:
            results.append({
                'password': password,
                'likelihood': likelihood,
                'category': category,
                'reason': reason,
            })

    year  = t.get('year', '')
    year2 = t.get('year2', '')
    first = t.get('first', '')
    last  = t.get('last', '')
    nick  = t.get('nick', '')

    # ═══════════════════════════════════════════════════════
    # الفئة 1: الاسم الأول + الأرقام
    # ═══════════════════════════════════════════════════════
    if first:
        for f in _name_variants(first):
            # اسم فقط
            add(f, 'medium', 'name_only', f'الاسم الأول فقط')

            # اسم + سنة كاملة
            if year:
                add(f + year,        'high', 'name+year',   f'الاسم + سنة الميلاد')
                add(f + '_' + year,  'medium','name+year',  f'الاسم _ السنة')
                add(f + '.' + year,  'low',  'name+year',   f'الاسم . السنة')
                add(year + f,        'medium','year+name',  f'السنة قبل الاسم')

            # اسم + آخر سنتين
            if year2:
                add(f + year2,       'high', 'name+yr2',   f'الاسم + آخر رقمين من السنة')
                add(f + '@' + year2, 'medium','name+yr2',  f'الاسم @ السنة المختصرة')

            # اسم + يوم+شهر
            if t.get('daymonth'):
                add(f + t['daymonth'],  'high', 'name+date', f'الاسم + يوم وشهر الميلاد')
                add(f + '_' + t['daymonth'], 'medium', 'name+date', f'الاسم _ تاريخ')

            # اسم + شهر+يوم
            if t.get('monthday'):
                add(f + t['monthday'],  'medium', 'name+date', f'الاسم + شهر ويوم')

            # اسم + سنة + رمز
            if year:
                for sym in ['!', '#', '@', '$']:
                    add(f + year + sym,   'high', 'name+year+sym', f'الاسم + السنة + {sym}')
                    add(f + sym + year,   'medium','name+sym+yr',  f'الاسم + {sym} + السنة')

            # اسم + 123 وتنويعات
            for suf in COMMON_SUFFIXES:
                add(f + suf,          'high', 'name+suffix', f'الاسم + لاحقة شائعة "{suf}"')

            # اسم + رقم مفضل
            if t.get('fav_num'):
                add(f + t['fav_num'],     'medium', 'name+favnum', f'الاسم + الرقم المفضل')
                add(f + t['fav_num'] + '!', 'low', 'name+favnum', f'الاسم + الرقم المفضل + !')

            # اسم + آخر 4 أرقام تليفون
            if t.get('ph4'):
                add(f + t['ph4'],         'high', 'name+phone', f'الاسم + آخر 4 أرقام تليفون')

    # ═══════════════════════════════════════════════════════
    # الفئة 2: اسم العيلة + الأرقام
    # ═══════════════════════════════════════════════════════
    if last:
        for l in _name_variants(last):
            if year:
                add(l + year,         'high', 'lastname+year',  f'اسم العيلة + السنة')
                add(l + year + '!',   'high', 'lastname+year',  f'اسم العيلة + السنة + !')
            if year2:
                add(l + year2,        'medium','lastname+yr2',  f'اسم العيلة + السنة المختصرة')
            for suf in COMMON_SUFFIXES[:6]:
                add(l + suf,          'medium','lastname+sfx',  f'اسم العيلة + {suf}')

    # ═══════════════════════════════════════════════════════
    # الفئة 3: الاسم الكامل
    # ═══════════════════════════════════════════════════════
    if first and last:
        fl   = first + last
        fl_u = first.capitalize() + last.capitalize()

        add(fl,                       'high', 'fullname',      f'الاسم الكامل')
        add(fl_u,                     'high', 'fullname',      f'الاسم الكامل بحروف كبيرة')
        add(first + '_' + last,       'high', 'fullname',      f'الاسم + _ + العيلة')
        add(first + '.' + last,       'medium','fullname',     f'الاسم . العيلة')
        add(first.capitalize() + last, 'high','fullname',      f'الاسم بحرف كبير + العيلة')

        if year2:
            add(fl_u + year2,         'high', 'fullname+yr',   f'الاسم الكامل + السنة المختصرة')
            add(fl + year2,           'medium','fullname+yr',  f'الاسم الكامل صغير + السنة')
        if year:
            add(fl_u + year,          'high', 'fullname+year', f'الاسم الكامل + سنة الميلاد')
            add(fl + year,            'medium','fullname+year',f'الاسم الكامل صغير + السنة')
        for suf in ['123', '!', '1']:
            add(fl + suf,             'high', 'fullname+sfx',  f'الاسم الكامل + {suf}')
            add(fl_u + suf,           'medium','fullname+sfx', f'الاسم الكامل كبير + {suf}')

    # ═══════════════════════════════════════════════════════
    # الفئة 4: الكنية
    # ═══════════════════════════════════════════════════════
    if nick:
        for n in _name_variants(nick):
            add(n,                    'medium','nick',         f'الكنية فقط')
            if year:
                add(n + year,         'high', 'nick+year',    f'الكنية + السنة')
                add(n + year + '!',   'high', 'nick+year',    f'الكنية + السنة + !')
            if year2:
                add(n + year2,        'high', 'nick+yr2',     f'الكنية + السنة المختصرة')
            for suf in COMMON_SUFFIXES[:5]:
                add(n + suf,          'high', 'nick+suffix',  f'الكنية + {suf}')

    # ═══════════════════════════════════════════════════════
    # الفئة 5: الحروف الأولى
    # ═══════════════════════════════════════════════════════
    if t.get('initials'):
        ini = t['initials']
        add(ini + year if year else ini,    'medium','initials', f'الحروف الأولى')
        if year:
            add(ini + year,                 'medium','initials', f'الحروف الأولى + السنة')
            add(ini.upper() + year,         'medium','initials', f'الحروف الأولى كبيرة + السنة')
    elif first and last:
        ini = (first[0] + last[0]).upper()
        add(ini + year if year else ini,    'medium','initials', f'حروف أولى من الاسم والعيلة')
        if year:
            add(ini + year,                 'medium','initials+yr', f'الحروف الأولى + السنة')

    # ═══════════════════════════════════════════════════════
    # الفئة 6: اللييت سبيك
    # ═══════════════════════════════════════════════════════
    for name_token in [first, last, nick]:
        if name_token:
            for variant in _leet_variants(name_token):
                if variant.lower() != name_token.lower():
                    base = variant.capitalize() if name_token[0].isupper() else variant
                    if year:
                        add(base + year,      'medium','leet+year',  f'لييت سبيك + السنة')
                        add(base + year + '!','medium','leet+year',  f'لييت سبيك + السنة + !')
                    if year2:
                        add(base + year2,     'medium','leet+yr2',   f'لييت سبيك + السنة المختصرة')
                    add(base + '123',         'medium','leet+123',   f'لييت سبيك + 123')
                    add(base + '!',           'low',  'leet+sym',   f'لييت سبيك + !')

    # ═══════════════════════════════════════════════════════
    # الفئة 7: الفريق
    # ═══════════════════════════════════════════════════════
    if t.get('team'):
        for tm in _name_variants(t['team']):
            add(tm,                          'medium','team',        f'الفريق المفضل')
            if year:
                add(tm + year,               'high',  'team+year',  f'الفريق + سنة الميلاد')
                add(tm + year + '!',         'high',  'team+year',  f'الفريق + السنة + !')
            if year2:
                add(tm + year2,              'high',  'team+yr2',   f'الفريق + السنة المختصرة')
            for suf in COMMON_SUFFIXES[:5]:
                add(tm + suf,                'medium','team+sfx',   f'الفريق + {suf}')
            if first:
                add(first.capitalize() + t['team'].capitalize(),
                                             'medium','name+team',  f'الاسم + الفريق')
                add(t['team'].capitalize() + year2 if year2 else '',
                                             'medium','team+yr',    f'الفريق + السنة')

    # ═══════════════════════════════════════════════════════
    # الفئة 8: اللاعب المفضل
    # ═══════════════════════════════════════════════════════
    if t.get('player'):
        for pl in _name_variants(t['player']):
            if year:
                add(pl + year,               'medium','player+year', f'اللاعب المفضل + السنة')
            add(pl + '10',                   'medium','player+num',  f'اللاعب + رقم 10')
            add(pl + '7',                    'medium','player+num',  f'اللاعب + رقم 7')
            for suf in ['123', '!', '1']:
                add(pl + suf,                'medium','player+sfx',  f'اللاعب + {suf}')

    # ═══════════════════════════════════════════════════════
    # الفئة 9: الشريك والأسرة
    # ═══════════════════════════════════════════════════════
    for rel_key, rel_label in [('partner','الشريك'), ('mother','الأم'), ('father','الأب'), ('friend','الصديق')]:
        if t.get(rel_key):
            name = t[rel_key]
            for v in _name_variants(name):
                if year:
                    add(v + year,            'high', f'{rel_key}+year', f'اسم {rel_label} + السنة')
                if year2:
                    add(v + year2,           'high', f'{rel_key}+yr2',  f'اسم {rel_label} + السنة المختصرة')
                add(v + '123',               'high', f'{rel_key}+123',  f'اسم {rel_label} + 123')
                add(v + '!',                 'medium',f'{rel_key}+sym', f'اسم {rel_label} + !')
                if first:
                    for sep in CONNECTORS[:3]:
                        combo = first.capitalize() + sep + name.capitalize()
                        add(combo,           'medium','name+relation', f'اسمك + {rel_label}')

    # أطفال
    for child in t.get('children', []):
        for v in _name_variants(child):
            add(v + year if year else v,     'high', 'child+year',  f'اسم الطفل + السنة')
            add(v + '123',                   'high', 'child+123',   f'اسم الطفل + 123')
            add(v + '!',                     'medium','child+sym',  f'اسم الطفل + !')

    # ═══════════════════════════════════════════════════════
    # الفئة 10: المدينة
    # ═══════════════════════════════════════════════════════
    for city_key in ['city', 'hometown']:
        if t.get(city_key):
            city = t[city_key]
            for v in _name_variants(city):
                if year:
                    add(v + year,            'medium','city+year',  f'المدينة + السنة')
                add(v + '123',               'low',  'city+123',   f'المدينة + 123')
                if first:
                    add(first.capitalize() + v, 'medium','name+city', f'الاسم + المدينة')

    # ═══════════════════════════════════════════════════════
    # الفئة 11: الشغل والشركة
    # ═══════════════════════════════════════════════════════
    for work_key, work_label in [('job','الوظيفة'), ('company','الشركة')]:
        if t.get(work_key):
            work = t[work_key]
            for v in _name_variants(work):
                if year2:
                    add(v + year2,           'medium',f'{work_key}+yr', f'{work_label} + السنة المختصرة')
                add(v + '123',               'medium',f'{work_key}+123',f'{work_label} + 123')
                add(v + '!',                 'low',  f'{work_key}+sym', f'{work_label} + !')
                if first:
                    add(first.capitalize() + v.capitalize(),
                                             'low', 'name+work',  f'الاسم + {work_label}')

    # ═══════════════════════════════════════════════════════
    # الفئة 12: اليوزرنيم والإيميل
    # ═══════════════════════════════════════════════════════
    for ukey in ['username', 'email_pfx']:
        if t.get(ukey):
            u = t[ukey]
            add(u,                           'high', 'username',   f'اليوزرنيم المعتاد')
            add(u.capitalize(),              'high', 'username',   f'اليوزرنيم بحرف كبير')
            add(u + '!',                     'high', 'username+!', f'اليوزرنيم + !')
            add(u + '123',                   'high', 'username+123',f'اليوزرنيم + 123')
            if year:
                add(u + year,                'high', 'user+year',  f'اليوزرنيم + السنة')

    # ═══════════════════════════════════════════════════════
    # الفئة 13: الهوايات
    # ═══════════════════════════════════════════════════════
    for hobby in t.get('hobbies', []):
        for v in _name_variants(hobby):
            if year2:
                add(v + year2,               'low', 'hobby+yr',   f'الهواية + السنة المختصرة')
            add(v + '123',                   'low', 'hobby+123',  f'الهواية + 123')

    # ═══════════════════════════════════════════════════════
    # الفئة 14: التواريخ وحدها
    # ═══════════════════════════════════════════════════════
    if t.get('daymonth') and t.get('year'):
        add(t['daymonth'] + t['year'],       'medium','date_full',  f'تاريخ الميلاد كامل (يوم+شهر+سنة)')
        add(t['year'] + t['daymonth'],       'medium','date_full',  f'تاريخ الميلاد معكوس (سنة+يوم+شهر)')
        if first:
            add(first.capitalize() + t['daymonth'], 'high','name+dmyr', f'الاسم + يوم وشهر الميلاد')

    if t.get('fulldate'):
        add(t['fulldate'],                   'medium','fulldate',   f'التاريخ الكامل بدون فواصل')

    # ═══════════════════════════════════════════════════════
    # الفئة 15: الكلمات الإضافية
    # ═══════════════════════════════════════════════════════
    for kw in t.get('keywords', []):
        for v in _name_variants(kw):
            if year:
                add(v + year,                'medium','keyword+yr', f'كلمة مفتاحية + السنة')
            if year2:
                add(v + year2,               'medium','keyword+yr', f'كلمة مفتاحية + السنة المختصرة')
            add(v + '123',                   'medium','keyword+123',f'كلمة مفتاحية + 123')
            add(v + '!',                     'low',  'keyword+sym', f'كلمة مفتاحية + !')
            if first:
                add(first.capitalize() + v.capitalize(),
                                             'low', 'name+keyword',f'الاسم + كلمة مفتاحية')

    # ═══════════════════════════════════════════════════════
    # الفئة 16: توليفات متقدمة
    # ═══════════════════════════════════════════════════════
    _advanced_combos(t, add)

    return results


def _advanced_combos(t: dict, add):
    """توليفات متقدمة من عناصر متعددة."""
    first = t.get('first', '')
    year  = t.get('year', '')
    year2 = t.get('year2', '')
    team  = t.get('team', '')
    nick  = t.get('nick', '')

    # اسم + فريق + سنة
    if first and team and year2:
        add(first.capitalize() + team.capitalize() + year2,
            'medium', 'name+team+yr', f'الاسم + الفريق + السنة')

    # اسم + مدينة + سنة
    if first and t.get('city') and year2:
        add(first.capitalize() + t['city'].capitalize() + year2,
            'low', 'name+city+yr', f'الاسم + المدينة + السنة')

    # اسم + شريك + سنة
    if first and t.get('partner') and year2:
        add(first.capitalize() + t['partner'].capitalize() + year2,
            'medium', 'name+partner+yr', f'الاسم + الشريك + السنة المختصرة')
        add(first.capitalize() + '&' + t['partner'].capitalize(),
            'low', 'couple', f'الاسمين بـ &')

    # كنية + تاريخ كامل
    if nick and t.get('daymonth') and year:
        add(nick.capitalize() + t['daymonth'] + year,
            'medium', 'nick+fulldate', f'الكنية + تاريخ الميلاد كامل')

    # اسم + رقم تليفون
    if first and t.get('ph6'):
        add(first.capitalize() + t['ph6'],
            'medium', 'name+phone6', f'الاسم + آخر 6 أرقام تليفون')

    # أول حرف من كل اسم + سنة
    names = [n for n in [first, t.get('last',''), t.get('partner','')] if n]
    if len(names) >= 2 and year:
        combo = ''.join(n[0].upper() for n in names) + year
        add(combo, 'low', 'initials+year', f'حروف أولى من الأسماء + السنة')


# ── مساعدات ───────────────────────────────────────────────────────────────
def _name_variants(name: str) -> list:
    """يولّد تنويعات حروف الاسم (كبيرة، صغيرة، mixed)."""
    if not name:
        return []
    variants = set()
    variants.add(name.lower())
    variants.add(name.upper())
    variants.add(name.capitalize())
    # CamelCase لو فيه مسافة
    if ' ' in name:
        variants.add(''.join(w.capitalize() for w in name.split()))
        variants.add(''.join(name.split()))
    return list(variants)


def _leet_variants(name: str) -> list:
    """يطبّق استبدالات اللييت سبيك."""
    name_low = name.lower()
    variants = [name_low]

    # استبدال حرف واحد في كل مرة
    for char, subs in LEET_MAP.items():
        if char in name_low:
            for sub in subs:
                variants.append(name_low.replace(char, sub))

    # استبدال كل الحروف معاً (لو الاسم قصير)
    if len(name_low) <= 8:
        chars_to_replace = [c for c in name_low if c in LEET_MAP]
        if chars_to_replace:
            full_leet = name_low
            for c in chars_to_replace:
                full_leet = full_leet.replace(c, LEET_MAP[c][0])
            variants.append(full_leet)

    return list(set(variants))


def _detect_patterns(t: dict) -> list:
    patterns = []
    if t.get('first') and t.get('year'):
        patterns.append(f"اسم + سنة الميلاد → {t['first'].capitalize() + t.get('year','')}")
    if t.get('nick'):
        patterns.append(f"الكنية بدل الاسم الرسمي → {t['nick']}")
    if t.get('team'):
        patterns.append(f"الفريق المفضل → {t['team']}")
    if t.get('partner'):
        patterns.append(f"اسم الشريك → {t['partner']}")
    if t.get('username'):
        patterns.append(f"إعادة استخدام اليوزرنيم → {t['username']}")
    if t.get('daymonth'):
        patterns.append(f"تاريخ الميلاد الكامل → {t['daymonth']}")
    if t.get('children'):
        patterns.append(f"أسماء الأطفال → {', '.join(t['children'])}")
    patterns.append("إضافة 123/! في آخر الباسوورد")
    patterns.append("تكبير أول حرف فقط")
    patterns.append("استبدالات لييت سبيك (a→@, e→3, i→1)")
    return patterns


def _assess_risk(t: dict, passwords: list) -> dict:
    n = len(passwords)
    n_high = sum(1 for p in passwords if p['likelihood'] == 'high')
    has_personal = any([t.get('first'), t.get('year'), t.get('nick'), t.get('team')])

    if n_high >= 10 or (has_personal and n >= 40):
        return {
            'level': 'critical',
            'text': f'⛔ خطر حرج — تم توليد {n} باسوورد محتمل ({n_high} عالي الاحتمالية). البيانات المتاحة تجعل الباسوورد قابلاً للتخمين بسهولة شديدة.'
        }
    elif n_high >= 5:
        return {
            'level': 'high',
            'text': f'🔴 خطر عالي — {n_high} باسوورد بعلامة "عالية". المعلومات الشخصية تُسهّل التخمين بشكل كبير.'
        }
    elif n >= 20:
        return {
            'level': 'medium',
            'text': f'🟡 خطر متوسط — {n} باسوورد محتمل. بعض البيانات كافية لتضييق دائرة التخمين.'
        }
    else:
        return {
            'level': 'low',
            'text': f'🟢 خطر منخفض — بيانات قليلة. يُنصح بتوفير معلومات أكتر للتحليل الدقيق.'
        }


def _build_reasoning(info: dict, t: dict) -> str:
    parts = []
    if t.get('first'):
        parts.append(f"الاسم: {t['first']}")
    if t.get('last'):
        parts.append(f"العيلة: {t['last']}")
    if t.get('year'):
        parts.append(f"المولود: {t['year']}")
    if t.get('team'):
        parts.append(f"الفريق: {t['team']}")
    if t.get('partner'):
        parts.append(f"الشريك: {t['partner']}")
    if not parts:
        parts.append("بيانات محدودة")
    return (
        f"تحليل محلي بالكامل لبيانات: {' — '.join(parts)}. "
        f"تم تطبيق {len(t)} قاعدة توليد شاملة تغطي الأنماط الإنسانية الشائعة."
    )
