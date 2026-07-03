---
name: rst-editing
description: how to property format .rst files
---

When making changes to .rst files, make sure to:

- match the section header underlines to the title length. for example:

Step 25. PCAP recording
=======================

is correct.

Step 25. PCAP recording
=====================

is not.

Step 25. PCAP recording
=========================

also not.

Step 25. PCAP recording  
=======================

this is correct even though there are spaces after the title.

the rule is that the underline has to be the same length of the title with all spaces except the trailing spaces.
so that it looks nice for humans. and doesnt generate any sphinx errors.

- add a newline before bulletpoint lists and numbered lists. for example:

correct:

INET's PCAP recorder module can capture network traffic at specific interfaces and save it in
PCAP format, which can later be analyzed with tools like Wireshark. This is useful for:

*   Debugging OSPF protocol issues
*   Understanding packet-level protocol behavior
*   Verifying LSA contents and exchanges
*   Analyzing timing and sequencing of OSPF messages

incorrect:

INET's PCAP recorder module can capture network traffic at specific interfaces and save it in
PCAP format, which can later be analyzed with tools like Wireshark. This is useful for:
*   Debugging OSPF protocol issues
*   Understanding packet-level protocol behavior
*   Verifying LSA contents and exchanges
*   Analyzing timing and sequencing of OSPF messages

- wrap the text at 80 columns

when asked to check certain .rst files if they are formatted correctly, you can check if these rules are observed and fix them.