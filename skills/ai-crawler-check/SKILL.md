---
name: ai-crawler-check
description: Check whether AI crawlers can reach a site through robots.txt, headers and page signals. Use for GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot, llms.txt and AEO technical checks.
---

# AI crawler check

A link can bring an AI assistant to a site only if the assistant can read it. This skill finds the blocks that keep a site's pages out of AI search and answers.

Read `references/evidence-rules.md` before you begin. If LinkGecko tools are connected, follow `references/linkgecko-connector.md`.

## 1. Run the check

Ask for the domain if you don't have it, then run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/crawler_check.py example.com
```

Use `--json` for machine-readable output, or `--robots-file robots.txt` to check a saved file offline.

If you cannot run scripts or reach the network, fetch `/robots.txt`, `/llms.txt`, `/sitemap.xml` and the homepage with your web tool. Then apply `references/crawlers.md` by hand. If you cannot fetch them either, ask the user to paste the robots.txt file.

## 2. Read the results correctly

Use `references/crawlers.md` to separate the three kinds of agent, because their blocks have different effects:

- **Search indexers:** a block keeps the site out of that engine's live answers.
- **User-triggered fetchers:** a block may stop an assistant from opening a page when someone asks.
- **Training crawlers:** a block is a data-licensing choice. Report it as information and do not call it a fault.

The script sees what a plain, unauthenticated request sees. A CDN may treat verified crawlers differently, in either direction, so mark results as provisional. Server logs or the CDN dashboard can confirm them.

## 3. Check the layers the script cannot see

Ask the user which CDN or firewall they use, and name the setting to review. Section 3 of `references/crawlers.md` covers these layers.

## 4. Deliver

Save the report as `ai-crawler-check-{domain}-{YYYY-MM-DD}.md` and summarize it in your reply:

- The most serious finding first, with its exact fix
- A ready-to-paste robots.txt change when one is needed, for the user to apply
- Findings ranked P0, P1, P2 or information
- What still needs checking in logs or the CDN

Propose robots.txt changes and leave the decision on training crawlers to the user. Do not edit their files unless they ask.
