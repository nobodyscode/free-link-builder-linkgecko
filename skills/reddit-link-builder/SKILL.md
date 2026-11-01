---
name: reddit-link-builder
description: Find Reddit threads where buyers need a product, using contextual keywords and intent, then draft rule-safe replies. Use for Reddit link building, Reddit marketing and Reddit brand mentions.
---

# Reddit Link Builder

Find the Reddit conversations where a brand can honestly help, work out what each person actually wants, and prepare replies that fit the thread and the subreddit's rules.

Read `references/evidence-rules.md` and `references/writing-rules.md` before you begin. If LinkGecko tools are connected, follow `references/linkgecko-connector.md`.

## Rules that never bend

- Prepare drafts only. Never post, comment, vote, message or create an account.
- Never suggest fake customers, multiple accounts, bought upvotes, aged accounts or paid posters.
- Every reply that mentions the brand discloses the poster's connection to it.
- Never write a first-hand story the poster has not lived. Use a placeholder and ask for the real one.
- Never analyze or quote a thread you have not read. A snippet or a third-party summary is only a lead.
- Never route around Reddit's blocks with mirror sites or scrapers.

## 1. Choose how to read Reddit

Claude's built-in web search and page fetching usually cannot read Reddit. Check what this session has, then use the first route available and tell the user which one you chose:

1. **A Reddit connector**, if one is connected.
2. **A browser tool**, such as Claude in Chrome. Ask first, read only, and never click anything that posts, votes or joins.
3. **Links and paste.** You build the search links in step 4, the user opens them, and they paste the threads back. Full text, or a saved page, both work.

Run a quick test if you are unsure. Do not report that a thread does not exist because a tool failed to find it.

## 2. Build the product brief

Read the brand's homepage, pricing page and any customer stories. Then confirm these in one message:

- What the product does, in one plain sentence
- Who buys it: role, company size and situation
- The pain that sends them looking
- Price range, and who it does **not** suit
- Main competitors and the tools or manual work it replaces
- Who will post, and what they have really done in this field

The "does not suit" line matters most. It stops you from pitching into threads where the honest answer is another tool.

## 3. Build contextual keywords

Follow `references/contextual-keywords.md`. Produce 20 to 40 phrases in the words buyers use, across these layers: problem, job to be done, category, competitor and alternative, workaround, trigger event, and community language.

Give each phrase its likely intent, and check every ambiguous word against its other meanings. Add a list of negative terms.

Search for reviews of the competitors with web search. Complaints on review sites are often the closest public match to how buyers talk on Reddit.

## 4. Choose subreddits and build the search pack

Use `references/subreddit-fit.md` to list 5 to 12 subreddits, sorted into buyer, peer and tool groups. Save the keywords as JSON in the format the script expects, with the highest-intent phrases first, because the user will start at the top. Then run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_search_links.py keywords.json --domain example.com
```

The script writes `reddit-search-pack-{domain}.md`, with three kinds of links for each phrase:

- **Fresh threads** in chosen subreddits, sorted by new, where a reply can still be read by the asker
- **Top Reddit results** across the past year
- **Google results** limited to Reddit, which show threads that attract readers from search

If you cannot run scripts, build the same links from the patterns in `references/subreddit-fit.md`.

## 5. Read the threads

Read the post, the top replies and the newest replies. Record:

- URL, subreddit, age and number of comments
- Whether it is locked or archived
- The asker's exact question and constraints: budget, team size, stack, region
- Tools already recommended, and how people reacted to them
- Any moderator comment
- Whether the brand or a competitor is named

Then harvest new phrases from what people wrote and add the best ones to the keyword list. A second search with their language usually finds better threads than the first.

## 6. Work out the intent

Classify each thread with `references/intent.md`. The title alone is not enough, so read the post and ask: **what would this person do tomorrow if they got a perfect answer?**

Then check fit against the asker's constraints. A buying-intent thread with a budget below the product's price gets no mention.

## 7. Check the subreddit's rules

Read the rules and any wiki or pinned post on promotion for each subreddit you plan to reply in. Record what they say about self-promotion, links, account age, karma, and promotion threads. If you cannot read them, mark the rules "not checked" and have the user confirm them before posting.

A rule against the planned reply ends that plan. Change it to a reply with no mention, or skip the thread.

## 8. Score and decide

Score each thread whose rules passed or are "not checked". A verdict on a "not checked" thread stays pending until the user confirms the rules. Complaints about the brand go straight to the user with no score.

- **Intent, 0 to 3:** 3 for buying, comparing or seeking an alternative, 2 for problem-solving, 1 for learning, opinions or open promotion threads, 0 for venting or false matches.
- **Fit, 0 to 3:** 3 if the product meets every stated constraint, 2 if it meets the main ones, 1 if it is a stretch, 0 if it conflicts with one.
- **Reader value, 0 to 2:** 2 if the thread ranks on Google for a buyer phrase or the subreddit is the category's main home, 1 if it has steady discussion, 0 if neither or if you could not check. Label a score of 0 from an unverified check.
- **Reply window, 0 to 2:** 2 if open and under 7 days old, 1 if open and older, and 0 if locked or archived.

Add the scores for a total out of 10 and answer the highest totals first. Then choose a verdict:

- **Reply and mention:** intent and fit both score 2 or more, and the thread is open.
- **Reply without a mention:** the thread is open and the poster has something useful to add, but the mention conditions are not met.
- **Skip:** the thread is locked or archived, it is a false match, or the poster has nothing to add.

Show the score parts next to each thread so the user can overrule you.

## 9. Draft the replies

Follow `references/reply-playbook.md`. Each reply answers the asker's question using a detail from their post, keeps the brand to one disclosed mention at most, and leaves out the link unless the playbook's three conditions are met. If a required first-hand detail is missing, use a placeholder.

## 10. Deliver the plan

Fill in `references/plan-template.md` and save it as `reddit-link-plan-{domain}-{YYYY-MM-DD}.md`.

In your reply, name up to three threads to answer first and the reason for each. Remind the user to edit each draft into their own words and post from their own account. If a reply is removed, they should ask the moderators why and should not repost it.
