# MCP Failure Triage Card — free, evidence-first

**For developers whose MCP client connects but the tool or workflow still fails.** This is a short manual decision aid, not a security certification or a full MCP conformance test.

> Use only synthetic fixtures or an endpoint you own / are explicitly authorized to check. Redact credentials, tokens, customer payloads, cookies, raw session IDs, and private URLs **before** sharing logs.

## 60-second decision tree

1. **Did the transport connect?** DNS, TLS, connection, proxy and timeout failures belong in **TRANSPORT**. An HTTP `200` alone proves neither MCP initialization nor downstream execution.
2. **Did `initialize` succeed with a compatible protocol revision?** If not, record **INITIALIZE / SESSION** and the response *shape* (not secrets).
3. **Can the client complete `tools/list`?** If not, record **DISCOVERY / DESCRIPTOR**. An advertised tool is not proof the tool can execute.
4. **Did a separately authorized `tools/call` run?** If no, label execution **NOT TESTED**. The free NAIF MCP Doctor probe intentionally **does not** call tools.
5. **Was the downstream response valid and verifiable?** A completed call with malformed/missing output is **OUTPUT_INVALID**; claims lacking verifiable support are **OUTPUT_UNVERIFIED**.
6. **Evidence missing or conflicting?** Use **UNKNOWN** rather than inventing a root cause.

| Symptom | Classification | Minimum safe next check |
| --- | --- | --- |
| Connection refused, TLS error, timeout before MCP exchange | TRANSPORT | Local endpoint/proxy reachability and sanitized timing |
| `initialize` rejected or version mismatch | INITIALIZE / SESSION | Request ID, negotiated revision, status, lifecycle step |
| `tools/list` errors or repeats a cursor | DISCOVERY | Pagination, JSON-RPC envelope, advertised descriptors |
| `401` or `403` after reaching a protected endpoint | AUTH / POLICY | Audience, scope, role, expiry (never paste the token) |
| Tool invocation returns a tool error | INVOCATION | Tool name, sanitized inputs, trace ID, minimal reproduction |
| Invocation completes but output is missing/wrong schema | OUTPUT_INVALID | Expected vs actual response fields |
| Output makes a claim without testable evidence | OUTPUT_UNVERIFIED | Source, observation, fingerprint, verification method |
| No safe reproduction or insufficient log context | UNKNOWN | Ask for a redacted minimal trace; keep claim unverified |

**Important distinction:** `OUTPUT_INVALID` and `OUTPUT_UNVERIFIED` describe **downstream observations**. The NAIF Gravity MCP Doctor `initialize`/`tools/list` probe cannot establish either outcome on its own.

## Copyable issue template

```text
Title: [MCP stage] short symptom
Transport: Streamable HTTP / other / unknown
Expected:
Actual:
Last confirmed successful stage: connect / initialize / tools-list / call / unknown
Observed status or error code (redacted):
Protocol revision (if known):
Runtime and client version:
Reproduction with synthetic data:
Trace ID (synthetic or redacted):
What was NOT tested:
Secrets removed? yes / no (do not post if no)
Current classification: TRANSPORT / INITIALIZE / DISCOVERY / AUTH /
                        INVOCATION / OUTPUT_INVALID / OUTPUT_UNVERIFIED / UNKNOWN
```

## Minimal synthetic examples

**Discovery succeeded, execution untested:**

```text
POST initialize -> HTTP 200, JSON-RPC result, matching request id
POST notifications/initialized -> completed
POST tools/list -> HTTP 200, one advertised descriptor
Conclusion: bounded discovery PASS; tools/call NOT TESTED.
```

**Output failure, not a transport failure:**

```text
Connection and MCP initialization succeeded.
Authorized tool call completed; expected JSON: {"ok": true, "items": []}
Actual sanitized result: {"ok": true}
Conclusion: OUTPUT_INVALID (missing "items"), not TRANSPORT.
```

## Use the existing free diagnostic

- [MCP Doctor diagnostic quickstart](DIAGNOSTIC-QUICKSTART.md) — bounded Streamable HTTP discovery, with authorization and safety constraints.
- [Offline Error Passport](ERROR-PASSPORT.md) — package an *already sanitized* report into reproducible evidence.
- [Main project README](../README.md) — local synthetic demo, supported runtimes and explicitly excluded tests.

The offline report mode does not contact the store. Remote `--probe` requires `--authorized` and only checks `initialize`, initialization notification and `tools/list`. It does not repair, invoke tools, handle generic n8n/webhook mapping, or verify production profitability or security.

## Discuss a redacted case

Join the developer community: **[NAIF Gravity Discord](https://discord.gg/A2MNvYayfG)** (non-expiring invite; subject to revocation), then use **#free-triage** for one specific issue or **#mcp-api-webhooks** for technical discussion. No direct messages or sales pitch required.

Project: [NAIF Gravity MCP Doctor](https://github.com/naief9961-tech/naif-gravity-mcp-diagnostics) · [NAIF Gravity](https://naifgravity.com/)

*This card is a manual, free community resource. It is not a guarantee of resolution or an independently verified test report.*
