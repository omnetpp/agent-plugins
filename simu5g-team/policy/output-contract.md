# The output contract

The parent agent sees what a subagent returns — not what it did. A return is
therefore small and pointed.

Every return has five parts:

1. The answer or the result, first, in 1–3 sentences.
2. Evidence as pointers: `src/stack/pdcp_rrc/NRPdcpRrc.cc:142`. Never a
   pasted file body. At most 3 quoted lines of code.
3. What changed: the file list, one line each.
4. What was not checked. A silent limit reads as full coverage.
5. The next step or the open question, in one line.

The whole return stays under 30 lines; a review or an audit may take 60.

Never paste raw build or fingerprint output. Counts and the first real error
only. `fp_stdout.log` stays on disk; a return quotes its verdict and its
counts.

No preamble. A fact is stated as a fact, a guess as a guess.

When the caller gives a schema, fill the schema and return nothing else.
