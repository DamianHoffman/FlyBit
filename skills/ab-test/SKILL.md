---
name: ab-test
description: Plans and evaluates A/B tests for email and SMS campaigns, covering the hypothesis, a single variable, the primary metric (clicks or conversions rather than opens), the required sample size, a significance test on the results, and a plain-language report with a conclusion and the next test. Use for questions about A/B tests, sample size, statistical significance, analyzing campaign results or a post-campaign report, or when new-automation needs a test plan. Polish keywords are test A/B, wielkość próby, istotność statystyczna.
license: MIT
compatibility: Needs Python 3.8+ with the standard library only. Designed for Claude chat on claude.ai (code execution must be enabled) and for Claude Code, as part of the flybit plugin.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/ab_significance.py *)
---

# A/B tests for email and SMS

The script does two things: it works out how many people a test needs (`plan`) and whether a result is more than chance (`analyze`). You handle the rest: a good hypothesis, one variable and an honest report.

## Running the script

The script lives in `scripts/ab_significance.py`, next to this SKILL.md. The commands below use `${CLAUDE_SKILL_DIR}`, which Claude Code replaces with the skill folder. Claude chat does not replace it and copies the skill folder into the code execution environment, so run `cd <this skill's folder> && python3 scripts/ab_significance.py ...` with the same arguments. If you cannot find the folder, search for the script with `find / -name ab_significance.py 2>/dev/null`. If `python3` does not exist (typical on Windows in Claude Code), use `python` or `py -3`. If you cannot run code, say so plainly and ask the user to enable "Code execution and file creation" in Settings > Capabilities. Do not guess numbers or p-values.

## Mode 1: plan the test (before sending)

Collect from the user, or assume and state as assumptions:

- the primary metric (by default a click or a conversion, not an open),
- the current success rate (the baseline). If there is no data, give a cautious range and say clearly that it is an assumption,
- the smallest difference that matters to the business (for example +1 percentage point),
- the size of the segment.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/ab_significance.py plan --baseline 0.03 --mde 0.01 --segment-size 4000
```

Instead of `--mde` (absolute difference) you can pass `--mde-rel 0.25` (relative difference, here +25% over the baseline).

Write the plan in this layout:

1. Hypothesis: "If we change X to Y, the rate of Z will rise, because ...".
2. Variable: exactly one. Give the full text of variant A and B.
3. Primary metric and guardrail metrics (unsubscribes, complaints).
4. Sample size per variant and in total, from the script.
5. Duration and decision rule, fixed before sending.

If the segment is too small, say so directly and show the smallest difference that can be detected at that size. There are then four honest options: test a bigger change, combine several sends, treat the result as directional, or skip the test and send one variant.

## Mode 2: analyze the results (after sending)

You need, for each variant, the number delivered (not sent) and the number of successes.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/ab_significance.py analyze --a-n 1000 --a-x 30 --b-n 1000 --b-x 45
```

Do not recompute in your head. Quote the script's result, then write the report:

- **Result in one sentence.** Who won and by how much, or that no difference was shown.
- **Table.** Variant, delivered, successes, rate.
- **Confidence.** The p-value and the confidence interval of the difference, in plain words.
- **Conclusion.** What this means for the next message.
- **Next test.** One next hypothesis.
- **Limits.** Sample size, duration, and any warnings from the script.

## Rules

1. One variable per test. Two changes at once do not tell you which one worked.
2. Do not treat opens as the primary metric. Since 2021 Apple Mail Privacy Protection loads images automatically and inflates opens, so they are a supporting signal at most.
3. Do not peek at the results during the test and do not stop early because it looks good. Fix the duration up front.
4. No significant result is not proof of no difference. Word it so that nobody draws the wrong conclusion.
5. Significant does not mean important. Always give the size of the effect and the interval, not just "p < 0.05".
6. The script compares two variants. With three or more, say that a different method is needed instead of running a series of pairwise comparisons.
7. For regulated industries, test the form (subject line, length, day and time of sending, layout), not the strength of persuasion.
