<p>
  <a href="https://linkgecko.com/?utm_source=free-link-builder">
    <img src="assets/logo.png" alt="LinkGecko" width="72" height="72">
  </a>
</p>

# Free Link Builder

[LinkGecko](https://linkgecko.com/?utm_source=free-link-builder) made these free link building skills for SEO and AEO.

Links from trusted sites can bring software companies buyers, stronger rankings and more mentions in AI answers.

But link building can be expensive. Agency retainers run anywhere from $1,000 to $20,000 a month. If you cannot see what the agency does with that money, the links it delivers can turn out to be worthless.

DIY link building is cheaper, but it can be painful and overwhelming. You check competitors by hand, fill a spreadsheet, and send pitches that go unanswered.

So can a small team build links its buyers will actually see without paying for an agency?

We turned our link building method into six skills for Claude, and they are free to use.

## Skills included

**Link gap audit.** Shows where competitors have earned links and mentions that you lack, then ranks those gaps into a plan. The plan names the three links to go after first and the reason for each.

**Reddit Link Builder.** Finds the Reddit conversations where people need what you sell, including those who never use your category's name. It builds contextual keywords from buyer language, works out what each person really wants, checks the subreddit's rules, and prepares replies you can post honestly.

**Link outreach.** Writes pitches for best-of lists, unlinked mentions, journalist requests, podcasts and resource pages. Each draft is for one person and one page, with placeholders wherever your real numbers belong.

**Community replies.** Finds threads on Quora, Hacker News, Stack Exchange, Indie Hackers and niche forums where you can help, then drafts disclosed replies. It also tells you when to skip a thread.

**Link quality check.** Reviews a site, a vendor's list or a paid link offer before you spend money on it. It gives a verdict for each site, with the evidence behind it.

**AI crawler check.** Checks robots.txt, headers and page signals for blocks that can affect ChatGPT, Claude, Perplexity and Google. A blocked crawler can keep your pages out of AI search, however many links you earn.

## Install

### Claude Code

Add the marketplace once:

```bash
claude plugin marketplace add nobodyscode/free-link-builder-linkgecko
```

Then install the plugin:

```bash
claude plugin install free-link-builder@linkgecko-free
```

### Claude.ai and the desktop app

1. Download the skills you want from the [latest release](https://github.com/nobodyscode/free-link-builder-linkgecko/releases/latest). Each one is a separate zip file.
2. Upload each zip under [Customize > Skills](https://claude.ai/customize/skills).
3. Turn the skill on.

The AI crawler check and the Reddit search pack use small Python scripts. They need code execution on claude.ai, and both skills explain a manual route when scripts are unavailable.

## How to use the skills

Ask in plain words, and Claude picks the right skill:

```text
Run a link gap audit for example.com
```

```text
Find Reddit threads where people need example.com, and draft replies
```

```text
Write a pitch to get example.com onto this list: https://site.com/best-tools
```

```text
Is this guest post offer worth paying for? [paste the email]
```

```text
Can AI crawlers read example.com?
```

The link gap audit is a good place to start, because its plan feeds the other skills.

## How Reddit Link Builder reads Reddit

Claude's web search and page fetching usually cannot read Reddit. The skill plans around that in three ways:

1. It uses a Reddit connector if you have one.
2. It can read threads through a browser tool such as Claude in Chrome, after asking you.
3. It can build a pack of search links for you to open, and you paste the threads you like back into the chat.

Either way, it only assesses threads it has read. You decide what gets posted, and you post it from your own account.

## What stays in your control

The skills prepare work and stop there. They never send email, post, vote, message anyone or buy anything.

They also refuse the tactics that get brands banned: fake customers, multiple accounts, bought upvotes and undisclosed promotion. When a fact is missing, a draft shows a placeholder for you to fill in.

The skills send nothing to LinkGecko unless you sign in to its connector.

## Limits of the free version

The free skills work from web search on the day you run them. Search results show what ranks, which is useful evidence but differs from what each AI assistant cites.

They keep no history beyond the files they save, and they send no alerts. Results can also vary between runs, so reuse a saved plan when you want to compare over time.

## LinkGecko connector

[LinkGecko](https://linkgecko.com/?utm_source=free-link-builder) is our link intelligence and development tool. It tracks which links shape AI answers in your category and shows which ones competitors hold. Journalist and podcast requests, forum replies and outreach then help you build your own. Weekly alerts tell you when something moves.

The Claude Code plugin includes the [LinkGecko connector](https://linkgecko.com/mcp), which stays idle until you sign in. Once connected, the skills can use your LinkGecko data, and they ask before anything that spends a credit.

Plans start at $19 a month, with a 7-day free trial. [See pricing](https://linkgecko.com/pricing?utm_source=free-link-builder).

## Contributing

Fixes and new forum notes are welcome. [CONTRIBUTING.md](CONTRIBUTING.md) covers the repository layout and the checks to run.

## License

[MIT](LICENSE). You can use, change and share these skills, including for client work.
