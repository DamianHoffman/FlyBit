---
name: sms-check
description: Counts SMS segments and detects the encoding (GSM-7 or Unicode) for any language, shows which characters (Polish letters, Cyrillic, emoji, curly quotes pasted from Word) force Unicode, proposes a plain variant without accents and estimates the cost of a campaign. Use when the user pastes SMS text, asks about SMS length, character limits, number of segments, accents in SMS or SMS cost, or when an SMS is drafted in an automation (for example from new-automation). Polish keywords are segmenty SMS, polskie znaki, koszt SMS.
license: MIT
compatibility: Needs Python 3.8+ with the standard library only. Designed for Claude chat on claude.ai (code execution must be enabled) and for Claude Code, as part of the flybit plugin.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/sms_segments.py *)
---

# SMS length and encoding check

Letters outside the basic GSM-7 alphabet (Polish ą ę ł, Turkish ş, Cyrillic, Arabic, CJK) and many "pretty" characters (curly quotes, en dashes, ellipsis, emoji) switch an SMS from GSM-7 (160 characters per segment) to Unicode (70). A 115-character message with a single "ę" is therefore 2 billed segments instead of 1. This skill shows that before the message is sent.

## How to check

1. Save the text to a UTF-8 file. In Claude Code, for example `flybit-output/sms-input.txt`, written with the Write tool. In Claude chat, any temporary file in the code execution environment. Separate several messages with a line that contains only `---`. Do not pass the text to the shell in quotes: accented letters and quotes break easily that way, especially in PowerShell.
2. Run the script:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/sms_segments.py --file flybit-output/sms-input.txt
```

3. The script lives in `scripts/sms_segments.py`, next to this SKILL.md. Claude Code replaces `${CLAUDE_SKILL_DIR}` with the skill folder. Claude chat does not, and copies the whole skill folder into the code execution environment, so run the script by a path relative to the skill folder, for example `cd <this skill's folder> && python3 scripts/sms_segments.py --file <full path to the messages file>`. If you cannot find the folder, search for the script with `find / -name sms_segments.py 2>/dev/null`. If `python3` does not exist (typical on Windows in Claude Code), use `python` or `py -3`.
4. Optionally add `--recipients 5000 --price 0.12` when the user knows the size of the audience and the price of one segment at their provider. Never guess the price: ask, or skip the cost.
5. The script replaces `[LINK]`, `[OPT-OUT]` and `{token}` with characters of a typical length (`--link-len 23`, `--optout-len 30`, `--token-len 8`). If the user knows the values from their provider's panel, set them.
6. If you cannot run code (for example code execution is turned off in chat), say so plainly and ask the user to enable "Code execution and file creation" in Settings > Capabilities. Until then give only a rough manual estimate: any letter outside GSM-7 means Unicode (70 characters per segment, 67 when longer), otherwise 160 and 153. Say it is an estimate made without the script.

Add `--json` for machine-readable output.

## How to present the result

In plain language, in the user's language, without unexplained acronyms. For each message give the number of segments, the exact characters that raise it, the plain variant, and the cost difference if it was calculated.

## Rules

- The plain variant is an option, not an order. It lowers the cost, but some brands find unaccented text less polished. Show both and let the user decide. Some providers convert accented letters automatically, so it is worth checking in their panel.
- Some languages cannot be converted (Cyrillic, Arabic, CJK). The script says so. Do not invent a GSM-7 version.
- Never remove the sender name or `[OPT-OUT]` to save characters. Compliance matters more than cost.
- If a message is 2 segments or more, suggest shortening it to one only when the meaning survives, and give the exact number of characters to cut.
- The numbers are estimates. Providers count slightly differently (link shortening, appended footers), so say that the final figure comes from the provider's panel.
- Avoid emoji in messages from regulated industries.
