# Windfire Security Client

A small, installable Python package (`client`) that other Windfire services embed to talk to the [windfire-security](../windfire-security) authentication server. It is the client-side counterpart to that server's `/v1/security/auth` and `/v1/security/verify` endpoints, and is not meant to be run standalone in production — it's consumed as a dependency by other Windfire services (e.g. `windfire-calendar`).

## Features

- `authenticate(username, password, service)` — obtains an access token from the auth server.
- `verify(token, service)` — checks whether a token is still valid for a given service.
- Environment-driven configuration (dev/prod host resolution, HTTPS enforcement, TLS certificate verification against a Windfire Root CA).
- Color-coded logging to console and to a rotating file (`$HOME/logs/windfire-security-client.log`), shared with the same logger style used in `windfire-security`.

## Installation

This package is meant to be installed as an editable dependency by the service that needs it:

```bash
pip3 install -e $HOME/dev/windfire-security-client
```

## Usage

```python
from client.authClient import authClient

token = authClient.authenticate(username, password, service)
if token:
    is_valid = authClient.verify(token, service)
```

`authClient` is a module-level singleton (`AuthClient()`), so it should be imported and used directly rather than instantiated again.

## Configuration

The client resolves the auth server and its TLS behavior entirely from environment variables — there is no config file:

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `prod` | `dev` → `localhost:8443`; `prod` (or anything else) → `raspberry01:8444`. |
| `ENFORCE_AUTH_SERVER_HTTPS` | `true` | Whether to call the auth server over `https` or `http`. |
| `VERIFY_SSL_CERTS` | `false` | Whether to verify the server's TLS certificate against `ROOT_CA_PATH`. |
| `ROOT_CA_PATH` | — | Path to the Windfire Root CA bundle (produced by `windfire-security`'s `ssl/createRootCA.sh`), used when `VERIFY_SSL_CERTS=true`. |

`LOG_LEVEL` / `DEFAULT_LOG_LEVEL` control logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, or a numeric level).

## Running the built-in smoke test

There is no automated/unit test suite — `testAuth.py` is the only test entry point, and it authenticates against a **real, reachable** `windfire-security` auth server for the chosen environment, then verifies the resulting token.

```bash
./run-auth-client.sh          # prompts for environment (1=Development, 2=Test, 3=Production), then username/password/service
./run-auth-client.sh 1        # skip the environment prompt, go straight to Development
```

This will:

1. Create the `windfire-security-client` Python virtual environment, if it doesn't exist.
2. Activate it.
3. Install prerequisites, if not already installed.
4. Run `testAuth.py` against the selected environment.

Related scripts: `createPythonVenv.sh`, `activatePythonVenv.sh`, `deactivatePythonVenv.sh` manage that venv; `installPrereqs.sh` installs pinned dependencies; `common.sh` holds shared shell variables/functions (environment selection, credential prompts, terminal colors).

## Building/publishing the package

```bash
./createModule.sh    # pip install build; python3 -m build -> produces dist/*.whl and dist/*.tar.gz
```

Package metadata lives in [pyproject.toml](pyproject.toml) (name `client`, version `1.0.0`, single runtime dependency `requests`).

## Project structure

```
client/
├── authClient.py           # AuthClient class + module-level `authClient` singleton
└── logger/
    └── loggerFactory.py    # shared color-formatted logger, file + console handlers
testAuth.py                 # smoke test: authenticate then verify
run-auth-client.sh          # end-to-end runner (venv + prereqs + smoke test)
createPythonVenv.sh / activatePythonVenv.sh / deactivatePythonVenv.sh
installPrereqs.sh           # installs pinned dependencies
createModule.sh             # builds the distributable package
common.sh                   # shared shell variables/functions
pyproject.toml              # package metadata
```

## Notes

- Logging requires `$HOME/logs/` to exist on the host beforehand — the `TimedRotatingFileHandler` will fail to initialize otherwise.
- When changing the public API (`authClient.authenticate()` / `authClient.verify()`), check consumers in sibling repos (e.g. `windfire-calendar`), which import `from client.authClient import authClient` directly.
- See [CLAUDE.md](CLAUDE.md) for more detailed internal/architecture notes.
