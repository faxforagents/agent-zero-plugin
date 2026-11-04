"""Check local artifacts against the fetched runtime and index validator."""

import ast
import base64
import importlib.util
import json
from pathlib import Path
import re

import pytest
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / ".coding-agent/upstream"
INDEX = ROOT / ".coding-agent/a0-plugins"
NAME = "fax_for_agents"


@pytest.fixture
def validator(monkeypatch):
    monkeypatch.syspath_prepend(str(INDEX / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "index_validator", INDEX / "scripts/validate_plugin_submission.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_matches_runtime_fields():
    manifest = yaml.safe_load((ROOT / "plugin.yaml").read_text())
    tree = ast.parse((UPSTREAM / "helpers/plugins.py").read_text())
    model = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PluginMetadata")
    fields = {n.target.id for n in model.body if isinstance(n, ast.AnnAssign)}
    # The user requested author. This runtime ignores it and reads repository metadata.
    assert set(manifest) - fields == {"author"}
    assert manifest["name"] == NAME
    assert manifest["version"] == "0.1.0"
    assert manifest["author"] == "faxforagents"
    assert manifest["title"] and manifest["description"]
    assert manifest["settings_sections"] == []
    assert manifest["per_project_config"] is False
    assert manifest["per_agent_config"] is False
    assert (ROOT / "LICENSE").is_file()
    assert (ROOT / "webui/main.html").is_file()


def test_hook_paths_exist_in_runtime():
    assert 'callJsExtensions("initFw_end")' in (UPSTREAM / "webui/js/initFw.js").read_text()
    assert '"extensions/webui"' in (UPSTREAM / "helpers/extension.py").read_text()
    assert 'await extension.module.default(...data)' in (UPSTREAM / "webui/js/extensions.js").read_text()
    for hook in (ROOT / "extensions/webui").iterdir():
        if hook.name == "initFw_end":
            code = (hook / "bootstrap-fax-setup.js").read_text()
            assert "export default async function" in code
            assert '/plugins/fax_for_agents/webui/fax-setup.js' in code
        else:
            assert f'id="{hook.name}"' in (
                UPSTREAM / "webui/components/sidebar/top-section/quick-actions.html"
            ).read_text()
    assert (UPSTREAM / "webui/components/settings/mcp/client/mcp-servers.html").is_file()


def test_editor_configuration():
    config = json.loads((ROOT / "examples/mcp-api-key.json").read_text())
    assert set(config) == {"mcpServers"}
    hosted, stdio = config["mcpServers"].values()
    assert hosted["url"] == "https://mcp.faxforagents.com/mcp/"
    assert hosted["headers"] == {"Authorization": "Bearer YOUR_API_KEY"}
    assert stdio["command"] == "npx"
    assert stdio["args"] == ["-y", "faxforagents-mcp"]
    assert stdio["env"] == {"FAXFORAGENTS_API_KEY": "YOUR_API_KEY"}
    assert stdio["disabled"] is True
    assert sum(not s.get("disabled", False) for s in config["mcpServers"].values()) == 1
    guide = (UPSTREAM / "docs/guides/mcp-setup.md").read_text()
    assert '"mcpServers"' in guide and '"Authorization": "Bearer YOUR_API_KEY"' in guide
    handler = (UPSTREAM / "helpers/mcp_handler.py").read_text()
    assert 'if server_item.get("disabled", False)' in handler


def test_hosted_selects_streamable_http_in_runtime():
    tree = ast.parse((UPSTREAM / "helpers/mcp_handler.py").read_text())
    names = {"_determine_server_type", "_is_streaming_http_type"}
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    namespace = {}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "upstream_transport", "exec"), namespace)
    hosted = json.loads((ROOT / "examples/mcp-api-key.json").read_text())["mcpServers"]["faxforagents_hosted"]
    assert namespace["_determine_server_type"](hosted) == "MCPServerRemote"
    assert namespace["_is_streaming_http_type"](hosted["type"])
    model = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MCPServerRemote")
    field = next(n for n in model.body if isinstance(n, ast.AnnAssign) and n.target.id == "type")
    default = next(k.value.value for k in field.value.keywords if k.arg == "default")
    assert not namespace["_is_streaming_http_type"](default)


def test_index_validator_with_local_inputs(validator, monkeypatch, capsys):
    """Run unmodified validation logic with explicit local Git and HTTP adapters."""
    staged = {
        f"plugins/{NAME}/index.yaml": (ROOT / "submissions/index.yaml").read_bytes(),
        f"plugins/{NAME}/thumbnail.png": (ROOT / "submissions/thumbnail.png").read_bytes(),
    }
    requests = []

    def request_json(url):
        requests.append(url)
        repo = "https://api.github.com/repos/faxforagents/agent-zero-plugin"
        if url == repo:
            return {"full_name": "faxforagents/agent-zero-plugin"}
        assert url == repo + "/contents/plugin.yaml"
        return {
            "type": "file", "encoding": "base64",
            "content": base64.b64encode((ROOT / "plugin.yaml").read_bytes()).decode(),
        }

    monkeypatch.setattr(validator, "_changed_entries", lambda: [("A", [p]) for p in staged])
    monkeypatch.setattr(validator, "_head_sha", lambda: "local-artifacts")
    monkeypatch.setattr(validator, "_git_path_exists", lambda commit, path: path in staged)
    monkeypatch.setattr(validator, "_git_read_text", lambda commit, path: staged[path].decode())
    monkeypatch.setattr(validator, "_git_read_bytes", lambda commit, path: staged[path])
    monkeypatch.setattr(validator, "_git_plugin_files", lambda commit, name: [Path(p).name for p in staged])
    monkeypatch.setattr(validator, "_request_json", request_json)
    assert validator.main() == 0
    output = capsys.readouterr().out
    assert "Validation passed for plugin: fax_for_agents" in output
    print("Local input adapter only. Git and HTTP inputs use local package files.")
    print(output, end="")
    assert len(requests) == 2


def test_index_rejects_wrong_identity(validator):
    content = base64.b64encode(b"name: wrong_plugin\n").decode()
    with pytest.raises(validator.ValidatePluginSubmissionError, match="exactly match"):
        validator._validate_remote_plugin_name({"encoding": "base64", "content": content}, NAME)


def test_index_rejects_extra_fields(validator):
    meta = yaml.safe_load((ROOT / "submissions/index.yaml").read_text())
    meta["version"] = "0.1.0"
    with pytest.raises(validator.ValidatePluginSubmissionError, match="unsupported fields"):
        validator._validate_fields(meta, NAME)


def test_index_shape_and_thumbnail(validator):
    raw = (ROOT / "submissions/index.yaml").read_text()
    meta = yaml.safe_load(raw)
    assert set(meta) == {"title", "description", "github", "tags"}
    assert len(raw) <= validator.INDEX_YAML_MAX_CHARS
    assert len(meta["title"]) <= validator.TITLE_MAX_LEN
    assert len(meta["description"]) <= validator.DESCRIPTION_MAX_LEN
    assert len(meta["tags"]) <= validator.MAX_TAGS
    assert meta["github"] == "https://github.com/faxforagents/agent-zero-plugin"
    assert re.fullmatch(r"[a-z0-9_]+", NAME)
    assert not (INDEX / "plugins" / NAME).exists()
    image_path = ROOT / "submissions/thumbnail.png"
    with Image.open(image_path) as image:
        assert image.width == image.height == 128
        assert image.format == "PNG"
    assert image_path.stat().st_size <= validator.THUMBNAIL_MAX_BYTES


def test_no_credential_collection():
    code = (ROOT / "webui/fax-setup.js").read_text()
    html = (ROOT / "webui/main.html").read_text()
    for forbidden in ("localStorage", "sessionStorage", "document.cookie", "fetch(", "callJsonApi", "x-model", "<input", "<textarea"):
        assert forbidden not in code + html
    assert 'x-if="$store.faxForAgentsSetup"' in html
    assert 'x-text="$store.faxForAgentsSetup.hostedJson"' in html


def test_sandbox_rules_and_current_tool_names():
    doc = (ROOT / "docs/sandbox-check.md").read_text()
    for text in ("+15550000001", "ffa_test_", "prepare_fax", "quote_fax",
                 "send_approved_fax", "get_fax_status", "get_fax_document",
                 "request_human_review", "get_review_status", "partial", "unknown",
                 "delegated policy", "untrusted", "idempotency"):
        assert text in doc
    assert "`get_document`" not in doc
