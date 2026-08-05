# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

We take the security of SimBot seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@ehoomaan79.github.io**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

### What to Expect

After you submit a report, we will:

1. Acknowledge receipt of your vulnerability report within 48 hours
2. Provide a more detailed response within 7 days indicating the next steps in handling your report
3. Keep you informed of the progress towards a fix and full announcement
4. Credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices

When deploying this bot, please follow these security best practices:

1. **Keep dependencies updated** - Run `pip install -r requirements.txt --upgrade` regularly
2. **Use strong tokens** - Ensure your Discord bot token and Kingshot signing secret are strong and kept secret
3. **Limit bot permissions** - Only grant the bot the minimum Discord permissions it needs
4. **Monitor logs** - Regularly check bot logs for suspicious activity
5. **Use HTTPS** - Ensure all API communications use HTTPS
6. **Restrict network access** - Run the bot on a secure network with firewall rules

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine the affected versions
2. Audit code to find any potential similar problems
3. Prepare fixes for all supported versions
4. Release the fixes as soon as possible
5. Publish a security advisory