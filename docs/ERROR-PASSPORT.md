# NAIF Error Passport — free-first MCP discovery card

**Status:** public alpha CLI and optional offline GitHub composite action. No npm/PyPI package is published. Python 3.10+ standard library only.

NAIF Error Passport is a **small, local diagnostic summary**, not a repair engine, security certificate, or marketing tracker. It reuses the existing [MCP discovery probe](../tools/mcp_health_check.py) and its already-sanitized JSON. It does not send server responses, credentials, endpoint URLs, tool names, or payloads to NAIF Gravity. It does not execute tools/call, open checkout, edit repositories, or publish an issue.

## Use an existing sanitized report (offline by default)

From this repository:

    python3 tools/mcp_health_check.py https://your-authorized-server.example/mcp --json > sanitized-report.json
    python3 tools/error_passport.py --report sanitized-report.json --format markdown > error-passport.md

The first command makes the existing bounded discovery requests **only to an authorized endpoint**. The second command is fully offline: it only reads the sanitized JSON file and prints a Markdown report. For a known failing probe, the CLI exits 1 after printing the passport; this is expected and useful in CI. Invalid/untrusted data exits 2. Reports can also be streamed:

    python3 tools/error_passport.py --report - --format json < sanitized-report.json

The passport includes a *local grouping fingerprint* derived from the allowed fields in the sanitized evidence. **It is not a cryptographic signature, a proof of server identity, or a transaction receipt.** Different endpoints with identical observations may produce the same fingerprint.

## One command for an endpoint you explicitly own or can test

    python3 tools/error_passport.py --probe https://your-authorized-server.example/mcp --authorized

This command runs the existing safe MCP discovery probe locally with a per-request timeout and bounded total runtime; it does not send a request to NAIF Gravity. **Network activity is opt-in**: without --authorized it refuses to start a probe.

For an authenticated endpoint, set an environment variable in your own shell, then pass only its name:

    python3 tools/error_passport.py --probe https://your-authorized-server.example/mcp --authorized --token-env MCP_TEST_TOKEN --format json

Never paste an actual credential, bearer token, user:password URL, or secret-bearing query string into a command or report. Non-loopback HTTP URLs are rejected. Local loopback HTTP is supported for fixtures.

## Diagnose first, offer repair only when explicitly requested

- Healthy discovery: summarize success, note that tools were **not executed**, and **never show a paid option**.
- Failed discovery: identify the failure boundary and give free steps for timeout, JSON-RPC, tool descriptors, HTTP auth or route failures.
- Unknown failure: say it is undetermined rather than claiming a fix.
- If the operator specifically requests a commercial alternative, add --show-optional-service. A relevant failure *may* include a link to a scoped MCP service. No pricing is hardcoded; no tool automatically pays, submits samples or starts checkout. Confirm scope and eligibility separately at the live merchant.
- The CLI only covers MCP Streamable HTTP initialize and tools/list discovery. It does **not** diagnose n8n field mapping, JSON trailing commas, HMAC signatures, or actual tool-call execution. Use the [separate agent troubleshooting Skill](../skills/naif-agent-emergency-triage/SKILL.md) for routing among these problems.

## GitHub Actions: summary on manual, authorized workflows

This repository also has a local [offline composite action](../.github/actions/error-passport/action.yml). After checking out this same repository and producing a **sanitized** JSON report, an operator may add a local step:

    - name: Show free-first MCP passport
      if: always()
      uses: ./.github/actions/error-passport
      with:
        report: sanitized-report.json
        show_optional_service: 'false'

This creates a GitHub Step Summary without contacting a remote endpoint or starting a payment. A failed probe produces a summary and an Action failure; you can choose a workflow policy such as continue-on-error for informational usage. Ensure the report exists before calling the action.

**Do not run untrusted pull-request code with repository secrets, auto-probe third-party servers, or publish private diagnostics.** Do not turn the existing manual workflow into an automatic deployment or paid transaction. GitHub Actions may have usage quotas in the user's account.

## Portable GitHub Action for another repository

The repository root includes a **standalone, offline composite action** at [action.yml](../action.yml). A GitHub workflow in another repository can call it against an **existing sanitized report** produced under that repository's authorization:

    - name: Review MCP discovery failure
      if: always()
      uses: naief9961-tech/naif-gravity-mcp-diagnostics@ea39a4b7bd80819e2ad53ed9f648b8ecf89391e0
      with:
        report: sanitized-report.json
        show_optional_service: 'false'

For a readable version reference instead of the full commit SHA, use `naief9961-tech/naif-gravity-mcp-diagnostics@v0.2.0`, which was publicly released after passing 39 local tests. Pinning a reviewed full commit SHA remains preferable for stricter supply-chain control.

The full commit reference above pins the exact public source that introduced the root action. Review and update the pin when a later version is desired. The report path is local to the **calling job**, and the job must create that file before calling the action. The action reads it, generates a safe job summary, and preserves failure as a nonzero step status; no network, checkout or external account is required by the action itself.

This is **GitHub-action compatible**, not a claim of GitHub Marketplace publication. Marketplace listing requires a release and any applicable publisher agreements, which have not been completed.

## Local verification

    python3 -m unittest discover -s tests -p 'test_*.py' -v
    python3 tools/error_passport.py --help

The tests include loopback healthy, wrong JSON-RPC ID and invalid tool-schema fixtures; invalid reports, attempted secret injection, and opt-in requirements are tested without querying production systems.

## Measuring whether distribution works

The CLI and composite action alone do **not** prove discoverability or sales. Count only independently verifiable voluntary installs, forks, stars or citations when observable; do not treat clones or self-tests as buyers. Track referral traffic and *separately verified* purchases only with valid attribution and privacy controls. Never manufacture customer demand, installs, third-party reviews or paid receipts.

Published by NAIF Gravity under this repository's MIT license. No mandatory hosted dependency.
