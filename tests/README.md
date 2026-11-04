# Local validation

Run these commands from the package root with Python 3.12 or later.
The fetched Agent Zero and index repositories must remain under `.coding-agent`.
Their checked revisions are recorded in [source-lock.json](../.coding-agent/source-lock.json).

```bash
mkdir -p .coding-agent/tmp
export TMPDIR="$PWD/.coding-agent/tmp"
export PIP_CACHE_DIR="$PWD/.coding-agent/tmp/pip-cache"
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.coding-agent/tmp/browsers"
export PYTHONDONTWRITEBYTECODE=1
python3 -m venv .coding-agent/tmp/venv
.coding-agent/tmp/venv/bin/pip install -r tests/requirements.txt
.coding-agent/tmp/venv/bin/python -m playwright install chromium
.coding-agent/tmp/venv/bin/python -m pytest -v -rP -p no:cacheprovider --basetemp=.coding-agent/tmp/pytest tests
```

If the source checkouts are missing, clone these repositories into their matching paths.
Check out the commits recorded in the source lock before comparing results.

```bash
git clone --depth 1 https://github.com/agent0ai/agent-zero.git .coding-agent/upstream
git clone --depth 1 https://github.com/agent0ai/a0-plugins.git .coding-agent/a0-plugins
```

## What these checks cover

The layout tests compare metadata and hook paths with the fetched source.
They execute the runtime's transport selectors against the hosted configuration.
They confirm the explicit HTTP type avoids the legacy SSE default.

The index test invokes the upstream validator's `main()` with local input adapters.
Git reads use the draft submission files.
GitHub responses use local manifest bytes and a repository identity fixture.
The validation rules remain unchanged.
Wrong identities and unsupported index fields must fail.
This does not prove remote publication or validate a real PR range.

The browser tests use upstream Alpine, `createStore`, and the JavaScript extension loader.
They render the setup view at desktop and phone widths.
They check repeated initialization, JSON parity, keyboard activation, links, and horizontal overflow.
Unexpected network requests, credential controls, storage writes, and browser errors fail the checks.

The harness substitutes the API, cache, and modal dispatcher.
It does not run Agent Zero's backend or full modal shell.
It does not authenticate, send a fax, or verify the full runtime theme.
Ben must complete the [sandbox walkthrough](../docs/sandbox-check.md) in Agent Zero.

## Thumbnail reproduction

Run this from the package root with the sibling logo available.
Pillow runs from the virtual environment above.

```bash
.coding-agent/tmp/venv/bin/python - <<'PY'
from pathlib import Path
from PIL import Image

source = Image.open('../chatgpt-plugin/logo.png')
image = source.convert('RGBA').resize((128, 128), Image.Resampling.LANCZOS)
target = Path('submissions/thumbnail.png')
image.save(target, optimize=True)
print(image.size, target.stat().st_size)
PY
```

The recorded result is 128 by 128 pixels and 2,272 bytes.
