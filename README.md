# FlyBit

Open-source plugin for [Claude](https://claude.ai) that helps small businesses and startups **plan, write, check and measure email and SMS automations**. It prepares drafts for you to approve and **sends nothing**.

> Early version, not yet run through a full conversation. See [Limitations](#limitations).

*Po polsku:* FlyBit to plugin open source do Claude, który pomaga małym firmom i startupom zaplanować, napisać, sprawdzić i zmierzyć automatyzacje e-mail i SMS. Niczego nie wysyła. Instrukcje są po angielsku, a Claude odpowiada w języku użytkownika.

**Goal:** take a small business from zero to a working, measured automation in an afternoon, using the email or SMS tool it already has or a free tier. This is a goal, not a measured result.

## What is inside

FlyBit contains four skills (instructions for Claude) and two Python scripts that Claude runs locally.

| Command | What it does |
|---|---|
| `/flybit:new-automation` | Guided builder with playbooks for five flows: welcome series, abandoned cart, post-purchase and review request, win-back, lead nurture. Produces audience and exclusions, a flow map, email and SMS copy, a review card and a `flow.md` blueprint with a tool-agnostic setup checklist. Can also improve an existing automation. |
| `/flybit:sms-check` | Counts SMS segments, detects GSM-7 vs Unicode, lists characters that raise the cost (accented letters, Cyrillic, emoji, curly quotes), offers a plain variant when possible, estimates cost when you give the price per segment. |
| `/flybit:compliance-review` | Universal checklist of 10 checks plus reference packs for the EU and Poland, the United States, and health communication in Poland (optional). Never says "compliant"; flags points for a lawyer. |
| `/flybit:ab-test` | Sample-size planning, significance test on results, plain-language report with a conclusion and a next test. |

The skills also start on their own when you describe a task in your own words.

## How it works

1. Install the plugin in Claude (see below).
2. Describe the task, e.g. "help me set up a welcome series for my online shop".
3. Claude asks at most one round of questions, then builds the audience, flow map and email and SMS copy, and runs the SMS and compliance checks.
4. It saves `flow.md` with a setup checklist.
5. You approve it and build the flow in your own email or SMS tool.

## Install

- **Claude chat** (claude.ai and the desktop app, paid plans: Pro, Max, Team, Enterprise): *Customize > Plugins > Add > Upload plugin* and choose the ZIP from the latest [release](../../releases/latest). Turn on "Code execution and file creation" in *Settings > Capabilities*, start a new conversation and ask "What skills do you have from plugins?".
- **Claude Code** 2.1.128 or later: `claude --plugin-dir ./flybit-plugin.zip` loads it for one session.
- **Cowork:** according to Anthropic's documentation it loads there; not tested.
- **Free plan:** skills can be uploaded one by one; not tested.

Requires a paid Claude plan for chat, or Claude Code with Python 3.8+. No API keys and no external accounts.

## What it does not do

FlyBit designs the automation, writes the messages, checks them and plans the measurement. It does **not** send messages, connect to customer data or run automations itself. It is not legal advice and does not manage consents or unsubscribes.

## Privacy

No servers, no data collection. The scripts import only the Python standard library and contain no network code. In Claude Code the builder writes `flow.md` into a `flybit-output` folder; in chat it creates a downloadable file or pastes the content. Conversation text is processed by Claude under your account's terms.

## Limitations

- Sends nothing; no integrations with email or SMS platforms; blueprints are tool-agnostic and untested against specific tools.
- Rule packs were verified in September 2026: EU and Poland and the health pack against legal commentary, US email rules against the FTC guide, US SMS rules only against law firm commentary.
- SMS segment counts are estimates (providers count slightly differently).
- A/B analysis compares two variants only.
- In chat the scripts need "Code execution and file creation" enabled; plugins in chat need a paid plan.
- Not yet run through a full conversation.

## Repository layout

```
.claude-plugin/  plugin manifest
skills/          the four skills (SKILL.md, references, scripts)
tests/           unit tests
docs/            landing page (GitHub Pages)
CHANGELOG.md  CONTRIBUTING.md  SECURITY.md  LICENSE  README.md
```

## Ideas for later (no commitment)

Connectors to email and SMS tools, more playbooks and rule packs, more languages.

## Contributing

Issues and pull requests are welcome.

## License

[MIT](LICENSE). Not affiliated with Anthropic or GitHub; "Claude" is a trademark of Anthropic.
