"""Isolated browser checks with upstream Alpine and its JS extension loader."""

import json
from pathlib import Path
import re

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / ".coding-agent/upstream/webui"
PREFIX = "/plugins/fax_for_agents/"


def harness():
    page = (ROOT / "webui/main.html").read_text()
    sidebar = (ROOT / "extensions/webui/sidebar-quick-actions-main-start/fax-setup.html").read_text()
    sidebar = re.search(r"<body>(.*?)</body>", sidebar, re.S).group(1)
    # The boot hook must populate the store, without help from the page's import.
    page = re.sub(r'<script type="module" src="[^"]+"></script>', "", page)
    boot = """
    <script type="module">
      window.modalCalls = [];
      window.openModal = path => window.modalCalls.push(path);
      window.runtimeInfo = {webuiExtensions: {js: {initFw_end: [
        '/plugins/fax_for_agents/extensions/webui/initFw_end/bootstrap-fax-setup.js'
      ]}}};
      const extensions = await import('/js/extensions.js');
      await extensions.callJsExtensions('initFw_end');
      const originalStore = (await import('/js/AlpineStore.js')).getStore('faxForAgentsSetup');
      await extensions.callJsExtensions('initFw_end');
      window.sameStore = originalStore === (await import('/js/AlpineStore.js')).getStore('faxForAgentsSetup');
      await import('/vendor/alpine/alpine.min.js');
    </script>
    """
    return page.replace("</body>", sidebar + boot + "</body>")


@pytest.mark.parametrize("width,height", [(1280, 900), (390, 844)])
def test_setup_in_browser(width, height):
    errors = []
    unexpected = []

    def route_request(route):
        from urllib.parse import urlparse
        url = urlparse(route.request.url)
        path = url.path
        if url.netloc != "fax.test":
            unexpected.append(route.request.url)
            return route.abort()
        if path == "/":
            return route.fulfill(content_type="text/html", body=harness())
        if path == "/js/api.js":
            return route.fulfill(content_type="text/javascript", body="export function callJsonApi() { throw new Error('Unexpected API call'); }")
        if path == "/js/cache.js":
            return route.fulfill(content_type="text/javascript", body="const cache = new Map(); export const get = (a,k,d) => cache.get(a+k) ?? d; export const add = (a,k,v) => cache.set(a+k,v); export const clear = () => cache.clear();")
        file = ROOT / path.removeprefix(PREFIX) if path.startswith(PREFIX) else UPSTREAM / path.lstrip("/")
        if file.is_file():
            return route.fulfill(content_type="text/javascript", body=file.read_text())
        unexpected.append(path)
        route.abort()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
        page.route("**/*", route_request)
        page.goto("http://fax.test/")
        page.get_by_role("heading", name="Connect Fax for Agents").wait_for()
        assert page.evaluate("window.sameStore")
        expected = json.loads((ROOT / "examples/mcp-api-key.json").read_text())["mcpServers"]
        for label, name in (("Hosted MCP configuration", "faxforagents_hosted"), ("Stdio MCP configuration", "faxforagents_stdio")):
            rendered = json.loads(page.get_by_label(label).inner_text())["mcpServers"][name]
            assert rendered == {k: v for k, v in expected[name].items() if k != "disabled"}
        assert page.locator("input, textarea, [contenteditable=true]").count() == 0
        assert page.evaluate("localStorage.length + sessionStorage.length") == 0
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.get_by_role("link", name="Connection check", exact=True).click()
        assert page.url.endswith("#ffa-connection-check")
        page.get_by_role("button", name="Open External MCP Servers").click()
        page.get_by_role("button", name="Fax setup", exact=True).click()
        assert page.evaluate("window.modalCalls") == [
            "settings/mcp/client/mcp-servers.html", "/plugins/fax_for_agents/webui/main.html"
        ]
        page.get_by_role("button", name="Fax setup", exact=True).focus()
        page.keyboard.press("Enter")
        assert page.evaluate("window.modalCalls.length") == 3
        assert errors == []
        assert unexpected == []
        page.screenshot(path=str(ROOT / f".coding-agent/tmp/setup-{width}.png"), full_page=True)
        browser.close()
