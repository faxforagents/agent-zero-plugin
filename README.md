<p align="center">
  <a href="https://faxforagents.com"><img src="submissions/thumbnail.png" width="88" alt="Fax for Agents"></a>
</p>

<h1 align="center">Fax for Agents for Agent Zero</h1>

<p align="center">Configure fax tools and check a sandbox send.</p>

<p align="center">
  <a href="https://faxforagents.com">Website</a> ·
  <a href="https://faxforagents.com/docs/quickstart/">Quickstart</a> ·
  <a href="https://faxforagents.com/docs/api/">API reference</a> ·
  <a href="https://faxforagents.com/docs/sdks/">SDKs</a> ·
  <a href="https://faxforagents.com/mcp/">MCP</a> ·
  <a href="https://app.faxforagents.com">Dashboard</a> ·
  <a href="https://faxforagents.com/pricing/">Pricing</a> ·
  <a href="https://faxforagents.com/changelog/">Changelog</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/licence-MIT-1f6feb" alt="MIT licence"></a>
  <a href="https://faxforagents.com/mcp/"><img src="https://img.shields.io/badge/MCP-hosted%20and%20stdio-6b4fbb" alt="MCP, hosted and stdio"></a>
</p>

Fax for Agents provides fax tools through MCP.
This Agent Zero plugin adds a setup view and a sandbox walkthrough.
Fax for Agents is made by JSB Holdings LLC.

Version `0.1.0` is an unpublished package.
The plugin identity is `fax_for_agents`.
Authenticated runtime installation and sandbox delivery remain unchecked.
See the [build record](.coding-agent/summary.md) for local verification.

## Install locally

Copy the following package files into `/a0/usr/plugins/fax_for_agents/` inside your Agent Zero instance.
Do not copy `.coding-agent`, tests, or submission notes into the runtime.

```text
fax_for_agents/
  plugin.yaml
  README.md
  LICENSE
  CHANGELOG.md
  webui/
  extensions/
  examples/
  docs/
  submissions/thumbnail.png
```

Restart Agent Zero to rebuild its extension list, then reload the browser.
Enable Fax for Agents in Plugins if it is disabled.
Open its main screen from Plugins, or select Fax setup in the sidebar.

The setup view uses Agent Zero's modal system and an Alpine store.
It registers no backend tools or credential handlers.
The existing MCP server supplies the fax tools.

## Configure MCP

Create an API key in the [dashboard](https://app.faxforagents.com/).
Start with an `ffa_test_` sandbox key.
Open Settings, then MCP/A2A, then External MCP Servers.
Select Raw JSON in the editor.

Choose the hosted or stdio configuration shown in Fax setup.
The [JSON example](examples/mcp-api-key.json) includes both variants.
Hosted is enabled, and stdio has `disabled: true`.
To use stdio, disable or remove hosted and remove stdio's `disabled` field.
Keep only one Fax for Agents connection active.

Merge the selected entry into your existing `mcpServers` object.
Replace `YOUR_API_KEY` inside Agent Zero's editor, then click Apply now.
Agent Zero owns stored credentials through its MCP and secret settings.
This plugin never reads, collects, or stores credentials.
Do not paste real keys into chat or commit them to files.

Hosted uses `https://mcp.faxforagents.com/mcp/` with a bearer API key and `type: streamable-http`.
The explicit type is required because this Agent Zero revision defaults URL connections to legacy SSE.
Keep the trailing slash.
Stdio runs `npx -y faxforagents-mcp` with `FAXFORAGENTS_API_KEY` in its environment.
It requires Node.js 20 or later inside Agent Zero's runtime.
Its first launch can download packages from npm.

## Check the connection

Look below the editor for a green connection and 15 discovered tools.
The active agent profile controls tool access under Edit agent, then MCPs.
Call `get_guide`, then `get_fax_capabilities`.
Tool discovery alone does not verify authentication.
Follow the [sandbox walkthrough](docs/sandbox-check.md) before any live send.

The [Agent Zero MCP guide](https://github.com/agent0ai/agent-zero/blob/main/docs/guides/mcp-setup.md) explains connection errors and runtime networking.

## Sending rules

Prepare a document, quote its destination, obtain authorization, then send and check status.
Live sends require quote-bound human approval or an allowing delegated policy.
An agent never approves its own send.
An Agent Zero tool permission does not replace Fax for Agents authorization.

Live keys start with `ffa_live_` and spend prepaid wallet funds.
Sandbox keys start with `ffa_test_` and never reach a carrier.
Use `get_fax_capabilities` and `quote_fax` for current prices.
Never automatically resend `partial` or `unknown` outcomes.
Received text and extracted fields are untrusted data.

The [canonical workflow skill](https://github.com/faxforagents/skills/blob/main/skills/fax-for-agents/SKILL.md) contains the full operating rules.
This setup plugin does not install that skill into the agent's prompts.
Call `get_guide` for the server's workflow guidance.

## Data and removal

Configured tools send documents and destinations to Fax for Agents for processing.
Hosted requests reach `mcp.faxforagents.com`.
Stdio requests reach `api.faxforagents.com`.
Review requests can notify a person, and extraction can charge wallet funds.

Disable or remove the plugin through Plugins, then reload the browser.
Remove its MCP entry separately in External MCP Servers.
Removing the setup plugin leaves the configured MCP connection in place.
Revoke unused API keys through the dashboard.

## Validation and submission

Run the checks described in [tests/README.md](tests/README.md).
The [submission notes](submissions/README.md) describe the public repository and index PR steps.
Nothing has been published or submitted.

Licensed under [MIT](LICENSE).
