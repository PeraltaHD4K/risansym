# Security Policy

## Supported versions

Security fixes are provided for the latest stable release published on PyPI.
Release candidates are supported while they are the active candidate for the
next stable release. The `main` branch receives fixes but is development code,
not a published support target.

| Version | Supported |
| --- | --- |
| Latest stable 1.x | Yes |
| Active 1.0 release candidate | Until 1.0.0 is released |
| Older prereleases and 0.x | No |

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability.

Use GitHub's private reporting flow:

1. Open the repository's
   [Security Advisories](https://github.com/PeraltaHD4K/risansym/security/advisories).
2. Select **Report a vulnerability**.
3. Include the affected version, environment, impact, reproduction steps or
   proof of concept, and any suggested mitigation.

If the **Report a vulnerability** button is unavailable, open a public issue
that only requests a private reporting channel. Do not include vulnerability
details, proof-of-concept code, secrets, or affected-user data in that issue.

## Response process

The maintainer will aim to:

- acknowledge a complete report within seven calendar days;
- confirm whether it is accepted or requires more information;
- coordinate a fix and disclosure date with the reporter;
- publish an advisory and patched release when users need to take action.

Timelines may vary because this is a maintainer-led open-source project. Please
allow a reasonable remediation period before public disclosure.

## Scope

Relevant reports include vulnerabilities in:

- parsing or exporting untrusted topology and trace files;
- package installation or release artifacts;
- the web visualizer's handling of uploaded traces;
- dependency chains that create a practical exploit in Risansym.

General hardening suggestions, unsupported-version bugs, and denial of service
caused solely by intentionally enormous simulations are normally not security
vulnerabilities, but may still be reported as regular issues.
