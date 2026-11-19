#!/usr/bin/env python3
"""Synchronize bank memo data from Google Sheets without changing its original UI.

Requires GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON repository secret.
Uses formatted values, preserves original section order, filters and UI schema.
Ambiguous rows are preserved, and diagnostics are emitted in the Actions log.
"""
import difflib
import json
import os
import re
import sys
from pathlib import Path
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SHEET_ID = "1BIwMWMBAB7LR9MbR5qGrIXYbq_LdFshCPz1Q_l-Mqcs"
DATA_FILE = Path(__file__).resolve().parent.parent / "memo-data.js"
MAPPING = {
    "s0": "Общие условия",
    "s1": "Стандартная ипотека",
    "s3": "Семейная(условия с 01.10.2026)",
    "s4": "IT Ипотека",
    "s5": "КОМБО ИПОТЕКА",
    "s6": "Военная ипотека",
    "s7": "Ипотека траншами",
    "s8": "Коммерция/Кладовки/Машино-место",
    "s9": "Субсидия(Стандарт, IT)",
    "s10": "Субсидия СИ(Москва, МО)",
    "s11": "Субсидия СИ(Регионы)",
    "s12": "Матрицы субсидирования",
    "s14": "Совкомбанк Сниженый платеж/Поэтап-е снижение ставк",
    "s15": "СТАВКИ",
    "s17": "Переход с рассрочки на ипотеку",
    "s16": "МАТ КАП",
    "s19": "Аккредитация/Договоры Субсидирования",
    "s21": "Контакты банков",
    "s13": "Сбер.ПЛ 01.10.2026",
    "s18": "Для Брокера!",
    "s20": "БКИ",
}
PREFIX = "window.MEMO_DATA="
EXCLUDED_DEFAULT = {"s21"}  # public repository: contains named bank contacts

def norm(s):
    return re.sub(r"[^а-яa-z0-9]+", "", str(s or "").casefold().replace("ё", "е"))

def value(row, i):
    return str(row[i] if i < len(row) and row[i] is not None else "").strip()

def fit(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()

def canon(bank):
    n = norm(bank)
    common = {
        "сбер": "сбер", "сбербанк": "сбер",
        "домрф": "домрф", "банкдомрф": "домрф",
        "альфа": "альфа", "альфабанк": "альфа",
        "промсвязь": "промсвязьбанк", "псб": "промсвязьбанк",
        "металлинвест": "металлинвестбанк", "металлинвестбанк": "металлинвестбанк",
        "совкомбанк": "совкомбанк", "мкб": "мкб",
        "банквтб": "втб", "втб": "втб",
        "уралфд": "уралфд", "уралфдмосквамоекб": "уралфд",
        "санктпетербург": "санктпетербург", "банксaнктпетербург": "санктпетербург",
    }
    return common.get(n, n)

def find_header(rows):
    for idx, r in enumerate(rows[:25]):
        if norm(value(r, 0)) in {"банк", "банки", "банкидом", "банкнаименование"}:
            return idx
    return None

def source_row_for(card, rows, header_idx, used):
    wanted = canon(card.get("n", ""))
    matches = []
    for i in range(header_idx + 1, len(rows)):
        if i in used:
            continue
        name = canon(value(rows[i], 0))
        if not name:
            continue
        if name == wanted:
            matches.append(i)
        elif wanted and (wanted in name or name in wanted) and min(len(wanted), len(name)) > 3:
            matches.append(i)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        return matches[0]  # repeated group labels: match in original card sequence
    return None

def match_column(label, headers):
    n = norm(label.split("·")[-1])
    if not n:
        return None
    matches = [i for i, h in enumerate(headers) if i > 0 and norm(h) == n]
    if len(matches) == 1:
        return matches[0]
    scored = [(fit(n, h), i) for i, h in enumerate(headers) if i > 0 and norm(h)]
    if scored:
        score, index = max(scored)
        if score >= 0.89 and sum(x[0] >= score - 0.02 for x in scored) == 1:
            return index
    return None

def refresh_cards(section, rows):
    header_idx = find_header(rows)
    if header_idx is None:
        return (0, 0, "No unique BANK header; left unchanged")
    header = rows[header_idx]
    used = set()
    changed = 0
    matched = 0
    for card in section.get("items", []):
        if card.get("t") != "card":
            continue
        i = source_row_for(card, rows, header_idx, used)
        if i is None:
            continue
        used.add(i)
        matched += 1
        row = rows[i]
        for kv in card.get("kv", []):
            if not isinstance(kv, list) or len(kv) < 2:
                continue
            j = match_column(kv[0], header)
            if j is None:
                continue
            nv = value(row, j)
            if nv and nv != kv[1]:
                kv[1] = nv
                changed += 1
    for card in section.get("items", []):
        if card.get("t") == "card":
            card["s"] = (card.get("n", "") + " " + " ".join(str(z) for kv in card.get("kv", []) for z in kv)).casefold()
    return changed, matched, f"Matched {matched} cards; {changed} updated fields"

def refresh_table(section, rows):
    old = section.get("rows", [])
    if not old or not rows:
        return (0, 0, "No source rows")
    # Find the source row corresponding to the first currently displayed data row.
    # Never shift data if the match is ambiguous.
    def similarity(left, right):
        sample = [(a, b) for a, b in zip(left, right) if norm(a) and norm(b)]
        return sum(fit(a, b) for a, b in sample[:15]) / max(len(sample[:15]), 1)
    candidates = [(similarity(old[0].get("c", []), r), i) for i, r in enumerate(rows[:35])]
    best, start = max(candidates)
    if best < 0.52:
        return (0, 0, f"Unsafe table offset (match {best:.2f}); left unchanged")
    changed = 0
    count = 0
    for i, rec in enumerate(old):
        if start + i >= len(rows):
            break
        row = rows[start+i]
        # Keep the source table's original width and formatting metadata.
        original = rec.get("c", [])
        cells = [value(row, j) for j in range(len(original))]
        if any(cells):
            rec["c"] = cells
            count += 1
            if cells != original:
                changed += 1
    return changed, count, f"Table offset {start+1}, {count} rows refreshed"

def refresh_rates(section, rows):
    # 'СТАВКИ' uses horizontal bank blocks; original layout is not row-oriented.
    changed = 0
    done = 0
    if not rows: return (0, 0, "No rate data")
    for card in section.get("items", []):
        if card.get("t") != "card":
            continue
        name = canon(card.get("n", ""))
        heading = None
        for r in rows[:4]:
            for j, val in enumerate(r):
                if name and canon(val) == name:
                    heading = j
                    break
            if heading is not None: break
        if heading is None: continue
        done += 1
        ratepairs = [(value(r, heading), value(r, heading+1)) for r in rows[1:] if value(r, heading)]
        for pair in card.get("kv", []):
            if len(pair) < 2: continue
            for label, rate in ratepairs:
                if fit(pair[0], "ПВ от "+label) >= 0.78 or norm(pair[0]) == norm(label):
                    if rate and pair[1] != rate:
                        pair[1] = rate
                        changed += 1
                    break
    return (changed, done, f"Updated {changed} rates across {done} bank blocks")

def read_sheets():
    secret = os.environ.get("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON")
    if not secret:
        raise SystemExit("Set repository secret GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON; see SYNC_SETUP.md")
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(secret), scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    credentials.refresh(Request())
    token = credentials.token
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {token}"
    ranges = [f"'{name.replace(chr(39), chr(39)*2)}'!A1:AR1100" for name in set(MAPPING.values())]
    result = {}
    for name, rg in zip(set(MAPPING.values()), ranges):
        response = session.get(f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{requests.utils.quote(rg, safe='')}",params={"valueRenderOption":"FORMATTED_VALUE"},timeout=90)
        if response.status_code != 200:
            raise RuntimeError(f"Unable to read tab {name}: HTTP {response.status_code} — {response.text[:200]}")
        result[name] = response.json().get("values", [])
    return result

def main():
    if not DATA_FILE.exists():
        raise SystemExit(f"Missing {DATA_FILE}")
    raw = DATA_FILE.read_text(encoding="utf-8")
    if not raw.startswith(PREFIX):
        raise SystemExit("Unexpected memo-data.js format")
    data = json.loads(raw[len(PREFIX):].rstrip().rstrip(";"))
    source = read_sheets()
    updates = 0
    untouched = []
    for section in data["secs"]:
        sid = section["id"]
        if sid in EXCLUDED_DEFAULT and os.environ.get("SYNC_CONTACTS") != "true":
            print(f"{sid} {section['t']}: skipped (contains personal contacts)")
            continue
        rows = source[MAPPING[sid]]
        if sid == "s15":
            changed, count, diagnostic = refresh_rates(section, rows)
        elif section["kind"] == "table":
            changed, count, diagnostic = refresh_table(section, rows)
        else:
            changed, count, diagnostic = refresh_cards(section, rows)
        updates += changed
        print(f"{sid} {section['t']}: {diagnostic}")
        if count == 0:
            untouched.append(sid)
    if untouched:
        print("WARNING: no records matched in: " + ", ".join(untouched), file=sys.stderr)
    if updates:
        DATA_FILE.write_text(PREFIX+json.dumps(data, ensure_ascii=False, separators=(",",":"))+";\n",encoding="utf-8")
    print(f"Synchronization finished: {updates} updated cells/rows.")
    if untouched and os.environ.get("STRICT_SYNC") == "true":
        raise SystemExit("Strict mode: some sections could not be refreshed")
if __name__ == "__main__":
    main()
