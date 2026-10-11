---
name: compliance-review
description: Checklist review of marketing email and SMS drafts for consent, opt-out, sender identity, honest claims, data minimization, tracking and send timing, with optional reference packs for the EU and Poland, the United States and health communication in Poland. Use when the user asks to check, review or audit a message, template or automation for compliance, and always before a flow from new-automation is finalized. It is a checklist and not legal advice, and it flags points for a lawyer or data protection officer. Polish keywords are sprawdź zgodność, zgody marketingowe, RODO.
license: MIT
compatibility: Designed for Claude chat on claude.ai and for Claude Code, as part of the flybit plugin. No scripts, it works on plain text and reads the reference files in this skill's references folder.
---

# Marketing compliance review

You are not a lawyer and you give no legal opinions. You check text against a checklist and **point out where a human must decide**. Never write "compliant" or "legal". The allowed wording is "no issues found against the checklist, a review by a lawyer or data protection officer is still needed".

Legal rules change. Every reference pack states when it was verified, and the user should confirm the current wording before relying on it.

## Input

The message texts (several if it is a flow), the channel, the country or countries of the recipients, the industry, how consent was collected, and the sending tool if known. Treat anything missing as "NEEDS HUMAN", and do not assume it is fine. If a message contains data about a specific person, stop and ask for it to be removed.

## Step 1: universal checks

| # | Check | What to look for |
|---|-------|------------------|
| U1 | Consent | The recipient opted in for this channel, or another lawful basis applies in their country, and the sender can show when and how |
| U2 | Sender | A clear sender name and a real way to reply or make contact |
| U3 | Opt-out | Easy and present in every email. SMS carries opt-out instructions. Requests are honored promptly and kept on a suppression list |
| U4 | Honest content | Subject and preview match the content. No fake urgency, fake scarcity, invented testimonials or misleading "Re:" and "Fwd:". Every claim can be backed up |
| U5 | Business details | Company identity and, where required, a postal address in the footer |
| U6 | Data minimization | No sensitive data in the message. Personalization has a fallback for empty fields |
| U7 | Exclusions | Unsubscribed, bounced, complaining and already-contacted people are left out. A frequency cap exists |
| U8 | Timing | A sensible send window. Suggest avoiding 22:00 to 08:00 recipient time. This is a policy and not a law |
| U9 | Links and tracking | One call to action, working links, tracking parameters, a privacy policy link. Ask whether tracking pixels or tracked links need disclosure or consent locally |
| U10 | Test send | Sent to the author first and checked on mobile. For SMS, check the lock-screen preview |

For SMS, also run the `sms-check` skill.

## Step 2: jurisdiction

Ask for the country or countries of the recipients. Then read the matching pack in `references/` (in Claude Code the folder is `${CLAUDE_SKILL_DIR}/references/`):

- Poland and the EU: `references/eu-pl.md`
- United States: `references/us.md`
- Other places: say that no pack exists yet, ask the user to check local law, and suggest contributing a pack.

If recipients are in several places, apply the strictest rule that applies to any of them.

## Step 3: industry

If the business is in a regulated industry (health, finance, insurance, gambling, alcohol, tobacco and vaping, supplements, cannabis, products for children), say that professional review is needed before sending. For health communication in Poland, read `references/health-pl.md`. For other industries, name the regulator type to ask (for example the financial supervisor) without quoting rules you have not verified.

## Output format

1. A short summary: how many checks are OK, FIX, or NEEDS HUMAN.
2. A table: `Check | Status | Note and fix`, with the statuses **OK**, **FIX**, **NEEDS HUMAN**. For FIX, quote the problem passage.
3. A corrected version of the text if there were FIX items. Mark the changes so the author sees what changed.
4. A list of questions for a lawyer or data protection officer, limited to the ones relevant to this flow.
