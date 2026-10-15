# Contributing

Issues and pull requests are welcome.

- **Reporting a problem:** include your Fusion version (`fusion_mcp.py ping` prints it), the script that failed and the error text.
- **Adding to the API notes:** only add what you ran. Mark anything unrun with **check**.
- **Adding a mode or a reference:** keep `SKILL.md` short and put detail in `skills/fusion-studio/references/`.
- **Before a pull request:** run `python tools/smoke_test.py`. With Fusion open it also rebuilds both examples in new documents.
- **Copy:** public pages and docs should read like a person wrote them. Run the slopmonster check if you have it.
- Open an issue before a large change so we agree on the direction first. Replies take about a week.
- Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md). Security problems go through [`SECURITY.md`](SECURITY.md), not a public issue.
- Do not commit generated zips, secrets or customer models.
