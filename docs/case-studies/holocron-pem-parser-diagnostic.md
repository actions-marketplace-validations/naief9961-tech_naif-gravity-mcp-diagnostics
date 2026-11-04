# NAIF Auto-Rescue: Holocron PEM parser diagnostic (experimental)

A [public Holocron issue](https://github.com/theholocron/holocron/issues/1713) describes a failure in dotenv parsing: an unquoted multiline PEM value is truncated to its first line. Downstream key import may fail even after webhook signature verification succeeds.

## Reproducible evidence

We inspected the public `parse-dotenv.ts` source and reproduced the truncation using **dummy text only**. An isolated candidate parser preserved PEM lines through the matching END marker while retaining subsequent variables. The original upstream parser-specific Vitest file passed **10/10** tests against the candidate; three additional synthetic PEM regression tests passed **3/3**. Total **13/13** in the isolated lab.

## Limits

This is an independent diagnostic demonstration, **not** an upstream-accepted or production-deployed fix. The full Holocron repository test suite was not run. No real secrets, client credentials or production payloads were used. No independent customer purchase or business outcome is implied.

## Self-service next step

[Check eligibility for NAIF Gravity Automation Rescue](https://naifgravity.com/service/automation-rescue#check).

Do not submit private keys, tokens, or confidential production data to public forms.
