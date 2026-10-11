#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Count SMS segments and detect the encoding (GSM-7 vs Unicode) for any language.

Usage:
  python3 sms_segments.py --file messages.txt     # separate several messages with a line containing only ---
  python3 sms_segments.py --text "SMS text"
  python3 sms_segments.py --file m.txt --recipients 5000 --price 0.12 --json

Standard library only (Python 3.8+).
Limits: GSM-7 allows 160 characters in one segment (153 per segment when longer),
Unicode allows 70 (67). Characters from the GSM-7 extension table (e.g. euro sign, [ ] { }) count as 2.
In Unicode, emoji count as 2 units.
Assumes the default GSM-7 alphabet; some providers support national language shift tables, so check yours.
"""
import argparse
import json
import re
import sys
import unicodedata

# Default GSM 03.38 alphabet: 127 characters (position 0x1B is ESC, not a character).
GSM7_BASIC = set(
    "@£$¥èéùìòÇ\nØø\rÅå"
    "Δ_ΦΓΛΩΠΨΣΘΞ"
    "ÆæßÉ"
    " !\"#¤%&'()*+,-./"
    "0123456789:;<=>?"
    "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§"
    "¿abcdefghijklmnopqrstuvwxyzäöñüà"
)
# Extension table: the character takes 2 positions (ESC + character).
GSM7_EXT = set("\f^{}\\[~]|€")

# Letters with no accent decomposition that are common in Central/Eastern European and Turkish text.
LATIN_MAP = {ord(a): b for a, b in zip("ąćęłńóśźżĄĆĘŁŃÓŚŹŻıİđĐ", "acelnoszzACELNOSZZiIdD")}
TYPO_MAP = {
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u2013": "-", "\u2014": "-", "\u2011": "-", "\u2212": "-",
    "\u2026": "...", "\u00a0": " ", "\u2009": " ", "\u202f": " ",
    "\u200b": "", "\u2022": "-", "\u00d7": "x",
}

GROUP_LABELS = {
    "letters": "letters outside the GSM-7 alphabet",
    "typographic": "typographic characters",
    "emoji": "emoji and symbols",
    "other": "other characters",
}


def gsm_units(ch):
    if ch in GSM7_BASIC:
        return 1
    if ch in GSM7_EXT:
        return 2
    return None


def measure(text):
    widths = [gsm_units(c) for c in text]
    is_gsm = all(w is not None for w in widths)
    if is_gsm:
        units, single, multi, enc = widths, 160, 153, "GSM-7"
    else:
        units = [2 if ord(c) > 0xFFFF else 1 for c in text]
        single, multi, enc = 70, 67, "Unicode"
    total = sum(units)
    if total == 0:
        segments = 0
    elif total <= single:
        segments = 1
    else:
        segments, used = 1, 0
        for u in units:  # a 2-unit character cannot be split across segments
            if used + u > multi:
                segments += 1
                used = 0
            used += u
    return {
        "encoding": enc, "gsm7": is_gsm, "units": total, "segments": segments,
        "limit_single": single, "limit_multi": multi, "over_by": max(0, total - single),
    }


def offenders(text):
    seen = {}
    for c in text:
        if gsm_units(c) is None:
            seen[c] = seen.get(c, 0) + 1
    groups = {"letters": [], "typographic": [], "emoji": [], "other": []}
    for c, n in seen.items():
        if c in TYPO_MAP:
            groups["typographic"].append([c, n])
        elif ord(c) > 0xFFFF or unicodedata.category(c) in ("So", "Sk", "Cs"):
            groups["emoji"].append([c, n])
        elif unicodedata.category(c).startswith("L"):
            groups["letters"].append([c, n])
        else:
            groups["other"].append([c, n])
    return {k: v for k, v in groups.items() if v}


def to_gsm(text):
    """Replace accented letters and typographic characters with GSM-7 equivalents. Returns (text, unconvertible)."""
    out, left = [], []
    for c in text:
        if gsm_units(c) is not None:
            out.append(c)
            continue
        c2 = c.translate(LATIN_MAP)
        c2 = TYPO_MAP.get(c2, c2)
        if all(gsm_units(x) is not None for x in c2):
            out.append(c2)
            continue
        base = "".join(x for x in unicodedata.normalize("NFKD", c2) if not unicodedata.combining(x))
        if base and all(gsm_units(x) is not None for x in base):
            out.append(base)
        else:
            out.append(c)
            left.append(c)
    return "".join(out), list(dict.fromkeys(left))


def expand(text, link_len, optout_len, token_len):
    t = re.sub(r"\[LINK\]", "x" * link_len, text, flags=re.I)
    t = re.sub(r"\[OPT-?OUT\]", "x" * optout_len, t, flags=re.I)
    return re.sub(r"\{\{.*?\}\}|\{[^{}\n]*\}", "x" * token_len, t)


def analyze_message(raw, a):
    text = expand(raw, a.link_len, a.optout_len, a.token_len)
    m = measure(text)
    res = {"text": raw, "chars": len(text), **m, "offenders": offenders(text)}
    if not m["gsm7"]:
        conv, left = to_gsm(raw)
        m2 = measure(expand(conv, a.link_len, a.optout_len, a.token_len))
        res["plain_variant"] = {"text": conv, "unconvertible": left, **m2}
    if a.recipients and a.price is not None:
        res["cost"] = {"current": round(m["segments"] * a.recipients * a.price, 2)}
        if "plain_variant" in res and res["plain_variant"]["gsm7"]:
            res["cost"]["plain"] = round(res["plain_variant"]["segments"] * a.recipients * a.price, 2)
    return res


def plural(n, word):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


def label(c):
    if c == "\u00a0" or unicodedata.category(c) in ("Cf", "Zs", "Zl", "Zp", "Cc"):
        return "U+%04X" % ord(c)
    return c


def hints(res):
    h = []
    off = res["offenders"]
    if "typographic" in off:
        h.append("Typographic characters (curly quotes, en/em dashes, ellipsis, non-breaking space) often arrive "
                 "from Word or Docs and silently force Unicode. Replace them with plain \" ' - ...")
    if "emoji" in off:
        h.append("Emoji and symbols force Unicode, and one emoji counts as 2 units.")
    if "letters" in off:
        h.append("Letters outside the GSM-7 alphabet (for example Polish ą ę ł, or Cyrillic) force Unicode: "
                 "the limit drops from 160 to 70 characters per segment.")
    if res["over_by"] > 0:
        h.append("To fit in 1 segment, shorten the text by %s." % plural(res["over_by"], "unit"))
    if res["segments"] > 1:
        h.append("Multi-segment message: the limit drops to %d per segment and every segment is billed."
                 % res["limit_multi"])
    return h


def render(res, i, a):
    seg = lambda n: plural(n, "segment")
    lines = ["Message %d" % i]
    prev = res["text"].replace("\n", " ")
    lines.append("  Text: %s%s" % (prev[:90], "..." if len(prev) > 90 else ""))
    reason = ""
    if res["offenders"]:
        parts = ["%s: %s" % (GROUP_LABELS[k], ", ".join(label(c) for c, _ in v)) for k, v in res["offenders"].items()]
        reason = " (because of " + "; ".join(parts) + ")"
    lines.append("  Encoding: %s%s" % (res["encoding"], reason))
    lines.append("  Length: %s (1-segment limit: %d) -> %s"
                 % (plural(res["units"], "unit"), res["limit_single"], seg(res["segments"])))
    pv = res.get("plain_variant")
    if pv and pv["gsm7"]:
        lines.append("  Plain variant without accents and typography (GSM-7): %s -> %s"
                     % (plural(pv["units"], "unit"), seg(pv["segments"])))
        lines.append("    Plain variant text: %s" % pv["text"].replace("\n", " "))
    elif pv:
        lines.append("  No GSM-7 variant is possible: these characters cannot be converted: %s"
                     % ", ".join(label(c) for c in pv["unconvertible"]))
    if "cost" in res:
        c = res["cost"]
        if "plain" in c and c["plain"] != c["current"]:
            saved = (1 - c["plain"] / c["current"]) * 100 if c["current"] else 0
            lines.append("  Campaign cost: %.2f -> %.2f with the plain variant (%.0f%% less)"
                         % (c["current"], c["plain"], saved))
        else:
            lines.append("  Campaign cost: %.2f" % c["current"])
    for h in hints(res):
        lines.append("  Tip: " + h)
    return "\n".join(lines)


def read_messages(a):
    if a.text is not None:
        raw = a.text
    elif a.file:
        with open(a.file, encoding="utf-8-sig") as f:
            raw = f.read()
    else:
        raw = sys.stdin.buffer.read().decode("utf-8-sig")
    parts = re.split(r"^[ \t]*---[ \t]*$", raw, flags=re.M)
    return [p.strip() for p in parts if p.strip()]


def main(argv=None):
    p = argparse.ArgumentParser(description="Count SMS segments (GSM-7 / Unicode).")
    p.add_argument("--file", help="UTF-8 file with one or more messages (separate with a line containing only ---)")
    p.add_argument("--text", help="a single message passed directly")
    p.add_argument("--link-len", type=int, default=23, help="length of a shortened link in place of [LINK] (default 23)")
    p.add_argument("--optout-len", type=int, default=30, help="length of the opt-out text in place of [OPT-OUT] (default 30)")
    p.add_argument("--token-len", type=int, default=8, help="length of a personalization value in place of {token} (default 8)")
    p.add_argument("--recipients", type=int, help="number of recipients (for the cost estimate)")
    p.add_argument("--price", type=float, help="price of one segment at your provider (for the cost estimate)")
    p.add_argument("--json", action="store_true", help="output JSON")
    a = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    msgs = read_messages(a)
    if not msgs:
        print("No messages to check (use --file, --text, or pipe text to stdin).", file=sys.stderr)
        return 2
    results = [analyze_message(m, a) for m in msgs]
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(render(r, i, a) for i, r in enumerate(results, 1)))
        print("\nAssumptions: [LINK]=%d chars, [OPT-OUT]=%d chars, {token}=%d chars. "
              "Adjust them to your provider (--link-len, --optout-len, --token-len). "
              "SMS providers count differently and some convert accented letters automatically, "
              "so confirm in your provider's panel."
              % (a.link_len, a.optout_len, a.token_len))
    return 0


if __name__ == "__main__":
    sys.exit(main())
