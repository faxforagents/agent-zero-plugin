import { createStore } from "/js/AlpineStore.js";

const hosted = {
  mcpServers: {
    faxforagents_hosted: {
      type: "streamable-http",
      url: "https://mcp.faxforagents.com/mcp/",
      headers: { Authorization: "Bearer YOUR_API_KEY" },
    },
  },
};

const stdio = {
  mcpServers: {
    faxforagents_stdio: {
      command: "npx",
      args: ["-y", "faxforagents-mcp"],
      env: { FAXFORAGENTS_API_KEY: "YOUR_API_KEY" },
    },
  },
};

export const store = createStore("faxForAgentsSetup", {
  hostedJson: JSON.stringify(hosted, null, 2),
  stdioJson: JSON.stringify(stdio, null, 2),
});
