---
name: new-automation
description: Guided builder for small-business marketing automations in email and SMS. Walks the user through choosing a flow (welcome series, abandoned cart, post-purchase and review request, win-back, lead nurture), defining the audience, mapping the steps, writing the copy, checking compliance and planning a test, then produces a paste-ready blueprint for whatever email or SMS tool they already use. Use when the user wants to create, plan, write or improve an automation, drip sequence, email flow or SMS flow, or asks how to start with marketing automation. Polish keywords are automatyzacja marketingowa, sekwencja e-mail, kampania SMS. Drafts for human approval and nothing is sent.
license: MIT
compatibility: Designed for Claude chat on claude.ai and for Claude Code, as part of the flybit plugin. Uses the sms-check, compliance-review and ab-test skills from the same plugin.
---

# FlyBit: build a marketing automation

FlyBit's goal is to take a small business or startup from zero to a working, measured automation in an afternoon, using the email or SMS tool they already have or a free tier. You design the flow, write the messages, run the checks and plan the measurement. The user sends with their own tool.

## Ground rules

1. You send nothing and have no access to the user's customers or sending tools. You work from descriptions and numbers the user gives you.
2. Do not accept or copy personal data. If the user pastes customer lists, names with emails, or health or financial details, stop, ask them to remove it, and keep it out of every file you create.
3. Never say a message is "compliant" or "legal". Say "no issues found against the checklist" and leave legal decisions to a professional.
4. Write in the user's language. Use placeholders instead of invented details: `[BRAND]`, `[LINK]`, `[UNSUBSCRIBE_LINK]`, `[BUSINESS_ADDRESS]`, `[OPT-OUT]`.
5. Be honest about results. Do not promise uplift. Quote only numbers the user supplied or a script computed.
6. Keep it simple. Build the smallest flow that works, with one goal per flow. Many users are beginners.

## Step 1: Intake

Ask only for what is missing, in one round of questions at most, and state your assumptions in one line.

- What the business sells and who the customers are
- Which flow they want (see `references/flow-playbooks.md`; in Claude Code the file is at `${CLAUDE_SKILL_DIR}/references/flow-playbooks.md`)
- Channels: email, SMS or both, and the tool they use (or none yet)
- Roughly how many contacts they have, and how consent was collected
- Country or countries of the recipients (needed for the compliance check)
- Tone and language

If the user does not know where to start, recommend a welcome series first (every business with a signup form needs one). After that, abandoned cart for online shops, lead nurture for services and B2B, and win-back once there is an older list.

Read the matching section of the playbook file before you build the flow.

## Step 2: Goal and metric

Pick one primary metric tied to a real conversion: purchase, booking, trial start, reply or a click that leads to one of these. Do not use opens as the primary metric, because Apple Mail Privacy Protection has inflated them since 2021. Add guardrail metrics: unsubscribes and spam complaints.

## Step 3: Audience

Describe the entry trigger, the segment in plain language and as a pseudo-query the user can copy into their tool, for example `signed up in the last 24 hours AND consent = yes`. List the exclusions: no consent for the channel, unsubscribed, bounced or invalid, already in another automation, contacted too recently. Define the exit conditions: goal reached, unsubscribed, replied.

## Step 4: Flow map

Give a table: `step | delay | channel | purpose | condition | exit`. Start from the playbook defaults. For beginners, three emails, plus one SMS only when SMS consent exists. Present delays and counts as starting points to adjust with data, not as benchmarks.

## Step 5: Copy

**Email.** Subject up to about 50 characters, a preheader, a short body, one call to action, a clear sender name, and a footer with `[UNSUBSCRIBE_LINK]` and `[BUSINESS_ADDRESS]` placeholders.

**SMS.** Brand name first, one idea, `[LINK]`, and `[OPT-OUT]` in the format the provider requires. If the language has accented or non-Latin letters, write two variants and check both with the `sms-check` skill. Show the user the segment count of each.

**Both.** Personalize with a fallback for empty fields. Use honest claims only: no fake urgency, fake scarcity or invented testimonials. Keep one consistent tone.

If the business is in a regulated industry (health, finance, insurance, gambling, alcohol, supplements, anything involving children), say so, use a neutral informational tone, and run the compliance review with the matching reference pack.

## Step 6: Compliance gate

Run the `compliance-review` skill on the whole flow. Apply the fixes it marks as needed and show what changed. Put every "needs a human decision" item on the approval list.

## Step 7: Test plan

Use the `ab-test` skill in plan mode: one variable, a hypothesis, the primary metric and the sample size against the list size. If the list is too small for a statistical test, say so plainly and suggest an honest alternative.

## Step 8: Review card

One table: audience and its size, channels, number of messages, estimated SMS cost (only if the user gave you the price per segment), tracking links, send window (suggest not sending between 22:00 and 08:00 recipient time, as a policy to confirm), consent source, and the compliance result. Under it, a list titled "Needs human approval".

## Step 9: Blueprint file

Create `flow.md` with these sections:

1. Status: `DRAFT FOR HUMAN APPROVAL`, date, flow type
2. Assumptions
3. Audience and exclusions
4. Flow map
5. Messages: one block per message with subject, preheader and body ready to copy, and for SMS both variants with segment counts
6. Compliance review result
7. Test plan
8. Review card and approval list
9. Setup checklist for any tool: create the segment or list; create the automation with its trigger; add the delays and conditions; add the messages; add the exit conditions; send a test to yourself and check mobile, links and the unsubscribe; start with a small slice of contacts; record baseline numbers and review after two weeks

Where to save it: in Claude Code, as `flybit-output/<flow-name>/flow.md`. In Claude chat, create the file in the folder where you save downloadable files and give it to the user as a file. If you cannot create files, paste the whole content in your reply.

In your reply, summarize in a few sentences what was created and the three most important things the user must approve.

## Improving an existing automation

If the user pastes existing copy or results, skip the builder. Run `compliance-review` and `sms-check` on the content, then propose up to three concrete improvements, each as its own testable hypothesis. If they give you results, use `ab-test` in analyze mode. Do not promise a percentage improvement without data.
