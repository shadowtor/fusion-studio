# Security

## What counts

The skill runs Python inside your own Fusion session through its local MCP server. A vulnerability here is anything that lets the skill's scripts do more than the user asked: writing outside the project folder, sending data off the machine, saving or closing a document unprompted, or running code from untrusted input.

## Reporting

Use GitHub's private vulnerability reporting: **Security** tab, then **Report a vulnerability**. Please do not open a public issue for a security problem.

I aim to reply within 7 days and to fix confirmed issues in the next release. This is a one-person project, so those are goals and not guarantees.

## Supported versions

Only the latest release on `main`.
