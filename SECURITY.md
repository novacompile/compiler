# Security Policy

We take the security of our project, data, and users very seriously. This document outlines our supported versions and the procedure for reporting vulnerabilities found within our code.

## Supported Versions

Please check the table below to see if the version of the software you are running is currently receiving security updates. We do not patch older versions that have reached End-of-Life (EOL).

| Version | Supported?         |
| ------- | ------------------ |
| 2.3.x   | ✅ Yes             |
| 1.2.x   | ✅ Yes             |
| 1.1.x   | 🔄 Security Only   |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues, pull requests, or community chat channels.** 

Instead, please use one of the following methods to report vulnerabilities responsibly:

### Option 1: GitHub Private Vulnerability Reporting (Preferred)
If enabled on this repository, you can submit a private report directly through GitHub:
1. Navigate to the **Security** tab of this repository.
2. Click on **Vulnerability reporting** in the left sidebar.
3. Click **Report a vulnerability** to open a secure form.

### Option 2: Email Disclosure
If private reporting is unavailable, please email your report to:
* **Email:** security@example.com
* **PGP Key:** [Link to PGP Key or Key ID if applicable]

### What to Include in Your Report
To help us triage and fix the issue quickly, please include:
* A detailed description of the vulnerability and its potential impact.
* Clear, step-by-step instructions to reproduce the exploit.
* A proof-of-concept (PoC) script, payload, or screenshot (if applicable).
* Any specific configurations or environment factors required to trigger the issue.

## Our Response Process

Once a vulnerability report is received, our core maintenance team will:
1. **Acknowledge:** Confirm receipt of your report within 48 hours.
2. **Triage:** Validate the exploit and determine its severity impact rating.
3. **Fix:** Develop a patch to address the vulnerability securely.
4. **Release:** Publish a new release containing the fix along with a security advisory acknowledging your contribution (unless you request to remain anonymous).

We ask that you maintain strict confidentiality regarding the issue until we have had a reasonable amount of time to release a patch and protect our active user base.
