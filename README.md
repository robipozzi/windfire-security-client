# Windfire Security Client

A small, installable Python package (`client`) that other Windfire services embed to talk to the [windfire-security](../windfire-security) authentication server. It is the client-side counterpart to that server's `/v1/security/auth` and `/v1/security/verify` endpoints, and is not meant to be run standalone in production — it's consumed as a dependency by other Windfire services (e.g. `windfire-calendar`).

## Features

- `authenticate(username, password, service)` — obtains an access token from the auth server.
- `verify(token, service)` — checks whether a token is still valid for a given service.
- Environment-driven configuration (dev/prod host resolution, explicit host/port override, HTTPS enforcement, TLS certificate verification against a Windfire Root CA).
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

`authClient` is a module-level singleton (`AuthClient()`), so it should be imported and used directly rather than instantiated again. Because it is created at import time, the environment variables below must be set **before** `client.authClient` is first imported.

Neither method raises on failure:

- `authenticate()` calls `POST /v1/security/auth` and returns the `access_token` string, or `None`.
- `verify()` calls `POST /v1/security/verify` with the token as a Bearer header and returns `True` only on HTTP 200, otherwise `False`. Its optional `method` argument (default `'local'`) is currently not forwarded to the server — the verification method is decided server-side.

## Configuration

The client resolves the auth server and its TLS behavior entirely from environment variables — there is no config file:

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `prod` | `dev` → `localhost:8443`; `prod` → `raspberry01:8444`. Any other value (including `test`) leaves host/port empty unless overridden below. |
| `KEYCLOAK_SERVER_HOST` | — | When set (non-empty), overrides the host resolved from `ENVIRONMENT`. |
| `KEYCLOAK_SERVER_PORT` | — | When set (non-empty), overrides the port resolved from `ENVIRONMENT`. Must be an integer; an invalid value is logged and ignored. |
| `ENFORCE_AUTH_SERVER_HTTPS` | `true` | Whether to call the auth server over `https` or `http` (`1`/`true`/`yes`/`on` count as true). |
| `VERIFY_SSL_CERTS` | `false` | Whether to verify the server's TLS certificate against `ROOT_CA_PATH`; when false, TLS verification is disabled entirely. |
| `ROOT_CA_PATH` | — | Path to the Windfire Root CA bundle (produced by `windfire-security`'s `ssl/createRootCA.sh`), used when `VERIFY_SSL_CERTS=true`. |

Consumers such as `windfire-calendar` use `KEYCLOAK_SERVER_HOST` / `KEYCLOAK_SERVER_PORT` to select the auth server explicitly; the `ENVIRONMENT` mapping remains the fallback (e.g. for `run-auth-client.sh`). The resolved host/port and its source are logged at `DEBUG` level on startup.

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

The username defaults to `windfire` and the service to `windfire-calendar-srv` (both set in `common.sh`). Note that the **Test** option sets `ENVIRONMENT=test`, which has no host mapping in `authClient.py` — to use it, also export `KEYCLOAK_SERVER_HOST` / `KEYCLOAK_SERVER_PORT` before running the script.

Related scripts: `createPythonVenv.sh`, `activatePythonVenv.sh`, `deactivatePythonVenv.sh` manage that venv (its name, `windfire-security-client`, is set in `common.sh` as `PYTHON_CLIENT_VIRTUAL_ENV`); `installPrereqs.sh` installs pinned dependencies; `common.sh` holds shared shell variables/functions (environment selection, credential prompts, terminal colors).

> `installPrereqs.sh` also installs packages this client doesn't use (Google Calendar API libraries, FastAPI, uvicorn, etc.), apparently carried over from another Windfire service. The package itself only needs `requests`.

## Building/publishing the package

```bash
./createModule.sh    # builds dist/*.whl and dist/*.tar.gz inside the project venv
```

The script uses the `windfire-security-client` venv's own Python, creating the venv first if it doesn't exist. This avoids PEP 668 errors from externally managed system Pythons (e.g. Homebrew), which refuse `pip install`. It then installs/upgrades `build` in the venv and runs `python -m build`.

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
createModule.sh             # builds the distributable package inside the venv
common.sh                   # shared shell variables/functions
pyproject.toml              # package metadata
```

## Notes

- Logging requires `$HOME/logs/` to exist on the host beforehand — the `TimedRotatingFileHandler` will fail to initialize otherwise.
- When changing the public API (`authClient.authenticate()` / `authClient.verify()`), check consumers in sibling repos (e.g. `windfire-calendar`), which import `from client.authClient import authClient` directly.
- See [CLAUDE.md](CLAUDE.md) for more detailed internal/architecture notes.
