# Contributing to FlyBit

FlyBit is a set of skills for Claude (plain-text instructions in `SKILL.md` files) plus two Python scripts. Contributions are welcome. Please keep each change small and focused.

## Run the tests

From the repository root:

```bash
python3 -m unittest discover -s tests -v
```

On Windows use `python` or `py -3` instead of `python3`. The tests use only the Python standard library. Besides the two scripts, they check that every skill folder is consistent: the skill name matches its folder, script paths are written both with `${CLAUDE_SKILL_DIR}` and as a relative `scripts/...` path, every file named under `references/` exists, every file in a `references/` folder is mentioned in its `SKILL.md`, and the frontmatter does not contain the sequence `: ` inside a value.

Run the tests before you open a pull request. The same command runs in GitHub Actions on every push and pull request.

## Add a flow playbook

Playbooks live in `skills/new-automation/references/flow-playbooks.md`.

1. Add a new numbered section after the last flow, before "Regulated industries".
2. Use the same fields as the existing sections: Trigger, Goal, Steps (starting point), Exit, Primary metric, Common mistakes.
3. Present delays and message counts as starting points, not as benchmarks.
4. If the flow should be offered by name, add it to the `description` in the frontmatter and to Step 1 of `skills/new-automation/SKILL.md`.

## Add a language

There is no translation system. The skills are written in English and Claude replies in the user's language. Adding support for a language currently means one or both of the following.

- **SMS counter.** Letters that cannot be converted to the basic GSM-7 alphabet are handled in `skills/sms-check/scripts/sms_segments.py`. To improve the plain (accent-free) variant for a language, extend `LATIN_MAP` (letters) or `TYPO_MAP` (typographic characters) and add tests in `tests/test_sms_segments.py`.
- **Discovery.** To help a skill trigger in another language, add keywords in that language to the `description` in its `SKILL.md` frontmatter. Do not use the sequence `: ` inside the description, because it breaks the YAML frontmatter (a test checks this).

Rules for a country are a rule pack, described next.

## Add a rule pack (country or industry)

Rule packs live in `skills/compliance-review/references/`.

1. Add a Markdown file there, for example `skills/compliance-review/references/<country-or-industry>.md`.
2. Mention it by its path in `skills/compliance-review/SKILL.md`: under Step 2 for a country, under Step 3 for an industry. A test fails if a file in `references/` is not mentioned in the `SKILL.md`.
3. State your sources and the date you verified them. Say what you read: the text of the law, or only commentary about it.
4. Write checks and questions for a professional. Never state that a message is "compliant" or "legal".
5. End the pack with questions for a lawyer or data protection officer.

## Rules for all contributions

- **No invented numbers.** Do not add benchmarks, conversion rates or savings without a source.
- **No legal advice.** FlyBit flags points for a human decision.
- **No data collection.** The scripts use only the Python standard library and have no network code. Open an issue before proposing anything that would change that.
- **Plain language.** Short sentences, no hype.

## Pull requests

Describe what changed and why, and confirm that the tests pass. New rules or numbers should cite a source and the date checked.

Contributions are accepted under the MIT license of this project.
