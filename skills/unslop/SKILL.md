---
name: unslop
description: Cut AI tells from prose and add a human voice — the default register for human-facing text: replies, summaries, reports, READMEs, commit messages, PR text. Triggers: /unslop, unslop this, remove AI tells, humanize this text, de-AI this. Machine-facing strings (error messages, tool descriptions, prompts) follow asd-ste100 Strict instead.
version: 0.1.0
---

# Unslop

Edit prose so it reads as written by a person: no AI vocabulary, no crutch punctuation, no decorative structure, and a real point of view. Adapted from the Cursor `unslop` skill (https://github.com/cursor/plugins/tree/main/pstack/skills/unslop) for use beside `asd-ste100`. Note: the source repo declares no license, so keep this attribution line.

## Scope and precedence

This skill and [`asd-ste100`](../asd-ste100/SKILL.md) split one job. STE governs sentence *shape*. Unslop governs *word choice, punctuation habits, and voice*.

- **Machine-facing text** (error messages, tool and function descriptions, prompts, inter-agent instructions): asd-ste100 Strict governs alone. Voice in a tool description is noise. Do not add soul there.
- **Human-facing prose** (replies, summaries, docs, commit messages): apply this skill, and keep the STE structural rules (active voice, sentence length caps, no semicolons, one topic per paragraph).
- **When the two disagree, precision wins over voice.** Keep the last hedge ("may" stays "may"). Keep every number, scope qualifier, and safety condition. Voice never buys them back.

Structural fixes (passive voice, dense sentences, hedge stacks, synonym rotation, nominalization) live in `asd-ste100`. Apply them from there. This file lists only what STE does not cover.

## Process

1. Scan the text for the patterns below.
2. Rewrite each hit. Preserve the meaning and the modality exactly.
3. For human-facing prose, add voice (next section).
4. Self-audit: ask "what makes this obviously AI-generated?" and fix what remains.

## Adding voice

Pattern removal is half the job. Sterile, voiceless prose is just as recognizable.

- **Have opinions.** React to facts. A neutral pro/con list where you hold a view is a dodge.
- **Vary rhythm.** Short sentences. Then longer ones that take their time. The STE length caps leave room between three words and twenty-five.
- **Acknowledge complexity.** "Impressive but also kind of unsettling" beats "impressive".
- **Use "I" when it fits.** First person is not unprofessional.
- **Skip scaffolding the text does not need.** A direct answer needs no headers, no bold labels, no summary table. Structure that exists to look organized is machine-made.
- **Be specific.** Name the mechanism, the number, or the concrete moment, not the feeling about it.

Bound: voice never costs a fact, a number, or a hedge. "Let some mess in" means dropping decorative structure, never dropping precision.

## Patterns to detect and fix

### Content

1. **Puffery.** "pivotal moment", "testament to", "evolving landscape", "deeply rooted". State what happened.
2. **Superficial -ing tails.** "...highlighting", "...ensuring", "...showcasing", "...fostering". Delete, or expand with the real fact.
3. **Promotional adjectives.** "vibrant", "groundbreaking", "renowned", "stunning", "seamless". Use the neutral description or the measurement.
4. **Vague attributions.** "Experts believe", "Some critics argue". Name the source, or delete the claim.
5. **Generic conclusions.** "The future looks bright." State the specific plan or fact, or end earlier.

### Language

6. **AI vocabulary.** "delve", "crucial", "underscore", "tapestry", "interplay", "garner", "enhance", "leverage", "utilize", "landscape" (abstract). Use the plain word: "use", "important", "show".
7. **Fancy "is".** "serves as", "stands as", "boasts", "features". Write "is" or "has".
8. **"Not just X, but Y."** State Y directly.
9. **Rule of three.** Groups of three forced onto ideas. Use the natural number.
10. **False ranges.** "from X to Y" where X and Y share no scale. List the items directly.
11. **Abstract metaphor nouns.** "substrate", "wedge", "vector", "nexus", "flywheel", "north star", "scaffolding" (as metaphor), "surface" (as in "API surface"). Pick the concrete word: "base", "add", "way".

### Style

12. **Em dashes.** Write none. End the sentence, or use a comma. Parentheses as a replacement trade one tell for another. Write the second thought as its own sentence.
13. **Colon as connector.** A colon before a list or example is fine. A colon that splices two clauses mid-sentence is a crutch. Let the second clause stand as its own sentence.
14. **Boldface overuse.** Bold carries emphasis, so spend it rarely. Proper nouns and acronyms stay plain.
15. **Inline-header lists.** A bold label plus colon that restates its own line ("**Performance:** Performance improved...") becomes prose. A bold lead-in that names the item and is followed by new detail is fine.
16. **Title Case Headings.** Use sentence case.
17. **Decorative emojis.** Remove from headings and bullets.
18. **Curly quotes.** Replace with straight quotes.

### Communication artifacts

19. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Certainly!", "Great question!". Respond directly and stop.
20. **Filler openers.** "It is important to note that" gets deleted. "In order to" becomes "To".
21. **Feeling words for mechanisms.** "the types follow your schema" names a feeling. Name the mechanism or the number instead: "a column rename fails the build". If a sentence could sit unchanged in another project's docs, it says nothing about this one. Cut it.
22. **Adverb props.** "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured delta.

## Exemptions

- **Code is exempt.** Match the idiom of the surrounding codebase.
- **Quoted text is exempt.** Reproduce quotations, file contents, and command output exactly.
- **Machine-facing text is exempt from voice.** It follows asd-ste100 Strict (see Scope and precedence).
