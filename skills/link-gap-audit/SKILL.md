---
name: link-gap-audit
description: Find the links and mentions competitors have that a brand lacks, then rank them into a link plan. Use for link gaps, backlink gaps, competitor links, link prospecting, SEO or AEO links.
---

# Link gap audit

Show a brand where its competitors are earning links and mentions that it lacks, then turn those gaps into a ranked plan the team can start on today.

Read `references/evidence-rules.md` before you begin. If LinkGecko tools are connected, follow `references/linkgecko-connector.md`.

## 1. Confirm the brief

Start from the domain and read the homepage and pricing page. Work out these details yourself, then confirm them in one message:

- Brand name and domain
- The category, in the words a buyer would use ("expense tracking app", rather than "fintech platform")
- The buyer's role and company size
- Three to five competitors
- Market and language, when they affect the results

Ask only about what you cannot work out. Also ask whether the user has a backlink export from Ahrefs, Semrush or Moz, since it makes step 5 stronger.

Pick the depth from the request:

- **Quick (default):** 8 buyer questions, about 25 pages read, top 10 gaps.
- **Full:** 25 buyer questions, about 60 pages read, top 25 gaps. Use it when the user asks for a full audit.

## 2. Write the buyer questions

Write questions a buyer would type into Google or an AI assistant. Spread them across these groups:

- **Category:** "best {category} for {buyer}"
- **Comparison:** "{competitor} vs {competitor}"
- **Alternatives:** "{competitor} alternatives", "cheaper than {competitor}"
- **Problem:** the pain the product solves, with no product words in it
- **Use case:** the category plus an industry, team size or integration

Avoid questions that contain the brand's own name. They only find pages that already know it.

## 3. Collect the sources

Search each question and log every useful result: URL, domain, the question that surfaced it, and its type from `references/source-types.md`. Skip the competitors' own domains, then count how many questions surfaced each page.

Web search shows what ranks. To add evidence from AI answers, offer the user the five most commercial questions to paste into ChatGPT, Perplexity or Gemini. Treat any answers they paste back as first-class data, and record the engine and date. Only those pages can be called AI-cited.

## 4. Read the pages

Open the pages that repeat across questions, then the strongest of the rest. For each page record:

- Whether the brand is **linked** (a direct link to its site), **indirect** (a redirect or an internal profile page), **mentioned without a link**, or **absent**
- The same status for each competitor
- Whether the page's audience matches the buyer
- When the page was last updated, if it says
- The realistic way in: author, editor, profile form, or thread

Mark a page "not read" when it blocks you. Do not guess its contents from a search snippet.

## 5. Remove weak targets

Drop or flag pages with the warning signs in `references/source-types.md`. A competitor's presence on a link farm is not a gap worth closing.

With a backlink export, add domains that link to two or more competitors and not to the brand. Label those as "from {tool} export" and read them before ranking.

## 6. Rank the gaps

Keep the ranking simple enough for the user to check:

- **Tier 1:** surfaced by 3 or more questions (2 or more in a Quick audit), at least 2 competitors hold a stronger status than the brand, and audience fit is strong.
- **Tier 2:** surfaced by 2 questions, or at least 1 competitor holds a stronger status, with good audience fit.
- **Tier 3:** useful and low effort, such as unclaimed profiles and unlinked mentions.

Cap any page published by a company selling in the category at Tier 3, since it rarely adds rivals. Within a tier, put the lowest effort first. Show the reason next to every rank.

## 7. Write the next action for each gap

Each gap gets one action, based on its type:

- **Best-of list or comparison:** pitch the author with `link-outreach`
- **Review site or directory:** claim the profile, complete it, and ask real customers for reviews
- **Unlinked mention:** ask for the link with `link-outreach`
- **Reddit thread:** run `reddit-link-builder`. Web search often hides Reddit, so if no threads surface, say so and suggest the skill anyway
- **Other forum thread:** run `community-replies`
- **Podcast or press:** pitch with `link-outreach`
- **Unknown site quality:** check it with `link-quality-check`

## 8. Deliver the plan

Fill in `references/plan-template.md` and save it as `link-plan-{domain}-{YYYY-MM-DD}.md`. If a file like this exists from an earlier run, reuse its questions and report what changed.

In your reply, give the three actions to start with and the reason for each. Keep that summary under 120 words and point to the file for the rest.
