# Getting the specification documents

The cache lives at `~/w/ai/spec-cache/<family>/`. It is outside the INET repository, and it stays
outside. Never commit spec text or a spec PDF into INET.

## The rule this file serves

No finding may come from model memory. You must read the clause you cite, in this run, from a
cached document. Model knowledge is a search aid. It tells you which clause to open. It is never
the evidence.

## IETF — RFC and Internet-Draft

Reachable from this machine without credentials.

- Text: `https://www.rfc-editor.org/rfc/rfc<N>.txt`
- Errata: the full dump at `https://www.rfc-editor.org/errata.json` (about 12 MB, 8000 records),
  filtered per document. The per-RFC HTML page redirects to a JavaScript search UI and does not
  parse. There is no per-RFC errata JSON endpoint.
- Metadata, obsoletes, and updates: `https://datatracker.ietf.org/doc/rfc<N>/`

Filter the dump by `doc-id` (`RFC0791`, zero-padded to 4 digits) and write one
`rfc<N>-errata.txt` per document. Keep only `Verified` and `Held for Document Update` records as
evidence. `Rejected` and `Reported` records carry no weight.

Always fetch the errata. Verified errata are a cheap source of real correctness findings, and
INET predates many of them.

Always check the datatracker page for `Obsoleted by` and `Updated by`. Reviewing an obsoleted RFC
and reporting gaps against it wastes the whole run.

### Checking status machine-readably

Do not read the obsoletes and updates relations from the HTML page. Use the per-RFC JSON:

```bash
curl -sL "https://www.rfc-editor.org/rfc/rfc<N>.json"
```

It returns `doc_id`, `title`, `status`, `pub_date`, `obsoletes`, `obsoleted_by`, `updates`,
`updated_by`, and `errata_url`. Loop over the candidate set at P0 and reject anything with a
non-empty `obsoleted_by`. Verified working 2026-08-25.

## IEEE 802

The IEEE Get Program publishes 802 standards at no cost, but it needs a license acceptance. An
agent cannot fetch the PDF unattended.

Procedure:

1. Ask the user to download the PDF and place it in `~/w/ai/spec-cache/<family>/`.
2. Convert it: `pdftotext -layout <file>.pdf <file>.txt`.
3. Record the revision year in the manifest. `IEEE 802.11-2020` and `IEEE 802.11-2024` differ, and
   a clause number alone is ambiguous without the revision.

## 3GPP and ITU-T

Both publish at no cost.

- 3GPP: `https://www.3gpp.org/ftp/Specs/` — record the series, the number, and the release.
- ITU-T: `https://www.itu.int/rec/T-REC/` — record the recommendation and its edition date.

## When a document cannot be obtained

Stop the family at P1. Set the index status to `spec-blocked`. Write what is missing, and what the
user must supply. Do not start P3.

Never substitute:

- a tutorial, a textbook, or a wiki page,
- a vendor document,
- model memory of the standard.

If only a public draft exists, you may use it. Then:

- mark every citation from it `confidence: medium`,
- name the draft and its revision in the Evidence column,
- say so in the manifest.

## The manifest

`spec-manifest.md` sits in the report directory and goes into the repository. One row per
document.

```markdown
| Document | Title | Version / date | Retrieved | Cache file |
|---|---|---|---|---|
| RFC 791 | Internet Protocol | September 1981 | 2026-08-25 | rfc791.txt |
| RFC 791 errata | Errata for RFC 791 | fetched 2026-08-25 | 2026-08-25 | rfc791-errata.html |
```
