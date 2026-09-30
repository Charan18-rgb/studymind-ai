# Security policy

## Reporting a vulnerability

Please do not disclose an unpatched security issue in a public issue. Use GitHub's private vulnerability reporting for this repository when available, or contact the repository owner through GitHub to arrange a private report. Include the affected component, impact, and steps to reproduce without including real user data or secrets.

## Secret and data handling

- Keep Gemini keys, `AUTH_SECRET`, and all credentials in local ignored environment files or the deployment provider's secret manager.
- Do not commit uploaded PDFs, SQLite files, session cookies, or user records.
- Rotate any credential that may have been exposed and remove it from the provider where it was configured.
