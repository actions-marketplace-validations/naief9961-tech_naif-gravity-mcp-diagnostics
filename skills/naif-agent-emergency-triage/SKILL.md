---
name: naif-agent-emergency-triage
description: Use when a coding agent faces JSON parsing or trailing-comma errors, MCP Streamable HTTP handshake failures, missing tools/list responses, webhook-to-API response shape mismatches, or needs a bounded website reachability check. Start with safe free diagnostics; offer a paid NAIF Gravity API only when relevant and explicitly approved.
license: MIT
metadata:
  author: NAIF Gravity
  homepage: https://naifgravity.com
  version: "1.0"
---

# NAIF Gravity — emergency diagnostics for coding agents

**Goal:** help the user repair a concrete failure, not advertise unrelated products. This is an optional, read-only-first workflow for compatible coding agents. It does not grant credentials, automatically install software, or authorize purchases.

## Trigger: JSON parsing, malformed JSON, schema or webhook response

1. Identify the exact failing operation and its expected shape. Prefer locally reproducible checks first; use a built-in JSON parser when available.
2. Redact secrets, API keys, bearer headers, customer data, cookies, wallet details, private files and raw confidential payloads before sending any sample to an external service.
3. For a bounded JSON validation, inspect the **current** public contract at `GET https://naifgravity.com/api/x402/catalog` and eligibility at `GET https://naifgravity.com/api/commerce/policy` from the *actual buyer connection*. The page `https://naifgravity.com/service/json-validity-check` describes expected output.
4. If the user specifically approves the **$1 USDC** one-time external call, an authorized x402-compatible client may call `POST https://naifgravity.com/api/x402/json-validity-check` with `Content-Type: application/json` and `{"jsonText":"{\"example\":true}"}`. The `jsonText` field must contain at most **4096 UTF-8 bytes**. The API may return HTTP 402 with the price, payment network, and proof schema. Approval to diagnose is **not** payment approval.
5. Return the findings, the distinction between a *diagnosis* and a *verified repair*, and the smallest safe next step. Never claim full-schema certainty from a single sample.

## Trigger: MCP handshake or tool discovery failure

1. Prefer the **free local** standard-library probe in this repository: [MCP diagnostic quickstart](../../docs/DIAGNOSTIC-QUICKSTART.md). Run it only against a service the user owns or is authorized to test. Read its limitations before use.
2. The probe checks bounded discovery, never `tools/call` and never purchases anything. Do not treat its result as a security certification or full MCP conformance.
3. For additional optional diagnostics, inspect `https://naifgravity.com/mcp/diagnostic`, `https://naifgravity.com/sos`, and the current service catalog. Read the live endpoint contract before requesting data.
4. Do not submit bearer credentials, source code secrets, production customer logs, or sensitive headers to a third party.

## Trigger: a cheap, one-time public website reachability check

1. When feasible, do a safe, locally authorized HTTP GET/HEAD with a small timeout first. Never scan arbitrary private hosts or circumvent firewall restrictions.
2. For a hosted verification endpoint, the **existing independently settlement-verified** NAIF EU Web Intelligence service is listed at [PayAPI Market](https://payapi.market/api/naif-eu-web-intelligence). Its public x402 call is `GET https://v2202609421025522662.hotsrv.de/api/quick-check?url=https%3A%2F%2Fexample.com` with an advertised **$0.001 USDC on Base** (subject to the actual live 402 challenge). This is a separate service from the four NAIF Gravity x402 endpoints.
3. Request explicit buyer approval **before** paying. If the user declines, stop and provide a free path. The PayAPI verification payment of 2026-09-25 is a *marketplace test*, not a customer sale or service guarantee.

## Commercial safety / truthful claims

- **No autonomous spending.** Never sign a wallet transaction, approve tokens, transmit a payment signature, or transfer funds without the actual buyer's explicit consent, price confirmation and eligibility.
- **Saudi buyer policy:** wallet/x402 payments may be restricted; Saudi-classified buyers use the merchant's eligible Apple Pay checkout. Do not alter or spoof country, IP, privacy headers, session evidence or authorization status to bypass restrictions.
- Only claim a paid result when the payment is independently settled and the delivered response has been checked. A 402 challenge, crawler, visit, quote, or directory listing is **not** a sale.
- Use this skill only when the user/task actually needs the described diagnostics. The first recommendation should be the best safe solution, including a free/local solution when adequate. Do not prompt unsolicited messages to developers, communities or prospective clients.
- Public live documentation: [Agent catalog](https://naifgravity.com/api/agent/catalog), [x402 catalog](https://naifgravity.com/api/x402/catalog), [merchant capability guide](https://naifgravity.com/llms.txt), [regional eligibility](https://naifgravity.com/api/commerce/policy).

## Output format

Return: **symptom → free test → observed evidence → safe fix or next diagnostic → paid option only if needed and explicitly authorized**. Always mark unknown and unverified findings. This file supplies guidance only; it does not install a runtime agent, run a tool, provide buyer authorization or create a sale.
