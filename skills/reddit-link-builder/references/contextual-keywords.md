# Contextual keywords

People on Reddit rarely describe their problem in a vendor's language. Someone looking for "accounts payable automation" may write "I'm drowning in supplier invoices and my bookkeeper quit". Searching only for the category name misses that person.

## Start from the buyer

Turn each feature into the moment that creates the need. Write how that person would say it to a colleague.

- **Feature:** automated invoice reminders
- **Moment:** a client is 30 days late and asking again feels awkward
- **Phrases:** "client won't pay invoice", "how do you chase late payments", "awkward following up on invoices"

## Keyword layers

Cover every layer that applies. Each one finds a different kind of thread.

1. **Problem:** the pain with no product words. "clients keep paying late"
2. **Job to be done:** the task they want finished. "how do you track freelance invoices"
3. **Category:** the plain name buyers use. "invoicing app", "invoice software for freelancers"
4. **Competitor and alternative:** "{competitor} alternative", "switching from {competitor}", "{competitor} too expensive", "{competitor} vs {competitor}", "anyone left {competitor}"
5. **Workaround:** what they do today. "invoices in a spreadsheet", "tracking payments in Excel", "Zapier for invoices"
6. **Trigger event:** what changed for them. "just went freelance", "first employee", "our contract renews next month"
7. **Community language:** the terms and abbreviations that a subreddit uses. "1099", "net 30", "retainer client"

## Where to find real wording

Use these in order, and quote only what you can actually see:

1. Threads you have read during this run
2. Complaints and praise in competitor reviews on G2, Capterra, Trustpilot, Product Hunt, app stores or plugin directories. Some of these block automated reading, so try another and note which were blocked
3. The brand's customer stories and support docs
4. Your own reasoning, marked as "untested" until a thread confirms it

After the first few threads, replace untested phrases with the real ones. Stop adding phrases once new searches return mostly threads you have seen.

## Remove false matches

Check every short or common word for other meanings before searching:

- **Brand names that are common words:** a product named "Monday", "Notion" or "Linear" needs a context word, such as "Linear issue tracker".
- **Words shared across fields:** "lead" means different things to a salesperson and a chemist. "Pipeline" has separate meanings in sales, data and oil. Pair them with a word from the buyer's world.
- **Acronyms:** spell them out or add a context word. "ATS" could mean a hiring system or a transfer switch.

Write a negative list as you go. Include other meanings, jobs posts, student questions and vendor roundups, if those keep appearing.

## Combine words carefully

- Prefer two to five words. Long phrases return almost nothing on Reddit search.
- Use quotes only for a fixed term. Quoting a whole sentence hides useful threads.
- Search within a subreddit with shorter phrases, since the subreddit supplies the context.
- Keep site-wide searches more specific, because they have no context to lean on.

## Output format

Save the keywords as JSON for the search pack script:

```json
[
  {
    "phrase": "client won't pay invoice",
    "layer": "problem",
    "intent": "problem-solving",
    "subreddits": ["freelance", "smallbusiness"],
    "source": "competitor review on G2"
  }
]
```

`phrase` is required. `subreddits` is optional, and the other fields are carried into the search pack as notes. Keep the negative terms in the plan.
