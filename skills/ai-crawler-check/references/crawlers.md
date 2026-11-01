# AI crawlers

New agents appear regularly and vendors change their documentation. When you find an unfamiliar token, check the operator's bot page before you classify it.

## 1. Who fetches, and why

### Search indexers

A block here keeps the site out of that engine's live results.

- `OAI-SearchBot` (OpenAI): ChatGPT search results and links. It does not affect training.
- `Claude-SearchBot` (Anthropic): Claude's search index. It is separate from ClaudeBot.
- `PerplexityBot` (Perplexity): Perplexity's answer index.
- `Googlebot` (Google): Google Search, AI Overviews and AI Mode. AI Overviews have no separate crawler.
- `Bingbot` (Microsoft): Bing and Copilot answers.
- `DuckAssistBot` (DuckDuckGo): DuckAssist answers.
- `YouBot` (You.com): You.com answers.

### User-triggered fetchers

These fire when someone asks an assistant to open a page. A block on marketing pages usually hurts the site itself.

- `ChatGPT-User` (OpenAI), where OpenAI says robots.txt rules may not apply
- `Claude-User` (Anthropic)
- `Perplexity-User` (Perplexity), documented as generally ignoring robots.txt
- `meta-externalfetcher` (Meta), which may bypass robots.txt
- `MistralAI-User` (Mistral)

### Training crawlers

A block here is a data-licensing choice. It has little to do with appearing in live answers.

- `GPTBot` (OpenAI)
- `ClaudeBot` (Anthropic), with older tokens such as `anthropic-ai` still found in some files
- `meta-externalagent` (Meta)
- `Amazonbot` (Amazon)
- `CCBot` (Common Crawl), a dataset many labs use
- `Bytespider` (ByteDance), widely reported to ignore robots.txt
- `Ai2Bot` (Allen Institute)
- `Diffbot` (Diffbot)
- `cohere-training-data-crawler` (Cohere)

### Control tokens

These are robots.txt directives and do not appear in logs.

- `Google-Extended`: controls use of content for Gemini training and grounding. It does not affect Google Search.
- `Applebot-Extended`: controls use of content for training Apple's models.

## 2. Reading robots.txt

- A crawler follows the group with the most specific `User-agent` match, and uses `*` only when no specific group exists.
- Within that group, the longest matching path wins, and `Allow` beats `Disallow` on a tie.
- An empty `Disallow:` allows everything.
- A misspelled token such as `GPT-Bot` matches nothing, so the crawler falls back to `*`.
- A robots.txt that returns a 4xx status generally counts as no restrictions. A 5xx or a timeout can make crawlers treat the whole site as disallowed.

Report site-wide and partial blocks differently. Blocking `/checkout/` is routine, while blocking `/` from a search indexer is serious.

## 3. Layers robots.txt cannot show

A clean robots.txt proves little on its own. Ask the user to review:

1. **CDN bot settings.** Cloudflare, Akamai, Fastly and AWS WAF can block AI crawlers regardless of robots.txt. In Cloudflare, review AI Crawl Control and the bot settings.
2. **Firewall and rate limits.** AI crawlers fetch from cloud IP ranges, which strict rules can catch.
3. **Meta robots and X-Robots-Tag.** `noindex` removes a page from search indexes. `nosnippet` and `max-snippet:0` can keep a page out of AI Overviews.
4. **JavaScript challenges and bot-detection walls.** Many AI fetchers do not run JavaScript.
5. **Login walls and cookie gates** that serve thin HTML to non-browser clients.

## 4. Confirming a result

From strongest evidence to weakest:

1. **Server logs or CDN analytics.** A 200 proves access and a 403 proves a block. Absence over weeks needs more context.
2. **CDN dashboard.** It shows the rules directly.
3. **A plain fetch, as the script does.** Treat the result as provisional, since CDNs can allow verified bots and block others.
4. **IP checks.** OpenAI, Anthropic and Perplexity publish IP ranges, and Google and Bing support reverse DNS checks. These help when a user agent may be spoofed.

## 5. Baseline policy for a brand that wants AI visibility

- Allow search indexers and user-triggered fetchers.
- Treat training crawlers as a business decision and present the trade-off.
- Keep `Sitemap:` lines absolute and current.
- Never use robots.txt for security, because anyone can read the paths it lists.

## 6. Severity

- **P0:** a search indexer is blocked site-wide, or key commercial pages carry `noindex`.
- **P1:** fetchers are blocked on marketing pages, `nosnippet` is on key pages, CDN settings are unreviewed, or robots.txt returns a 5xx.
- **P2:** misspelled tokens, partial blocks to verify, no sitemap, or no llms.txt. An llms.txt file is optional and major engines have not committed to using it.
- **Information:** training crawlers blocked on purpose.
