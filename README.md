# Windfire Security Client
[![CI](https://github.com/robipozzi/windfire-security-client/actions/workflows/ci.yml/badge.svg)](https://github.com/robipozzi/windfire-security-client/actions/workflows/ci.yml)

A small, installable Python package (distribution `windfire-security-client`, import package `client`) that other Windfire services embed to talk to the [windfire-security](../windfire-security) authentication server. It is the client-side counterpart to that server's `/v1/security/auth` and `/v1/security/verify` endpoints, and is not meant to be run standalone in production — it's consumed as a dependency by other Windfire services (e.g. `windfire-calendar`).

## Features

- `authenticate(username, password, service)` — obtains an access token from the auth server.
- `verify(token, service)` — checks whether a token is still valid for a given service.
- Environment-driven configuration (dev/prod host resolution, explicit host/port override, HTTPS enforcement, TLS certificate verification against a Windfire Root CA).
- Color-coded logging to console and to a rotating file (`windfire-security-client.log` in `$WINDFIRE_SECURITY_CLIENT_LOG_DIR`, default `$HOME/logs`), shared with the same logger style used in `windfire-security`.

## Installation

This package is meant to be installed as an editable dependency by the service that needs it:

```bash
pip3 install -e $HOME/dev/windfire-security-client
```

or from the wheel built by `./createModule.sh`:

```bash
pip3 install windfire_security_client-1.1.0-py3-none-any.whl
```

The import package is still `client` (`from client.authClient import authClient`). Before 1.1.0 the distribution was named `client`: in an environment that has the old one installed, run `pip3 uninstall client` first, so that two distributions don't both own the `client/` package.

## Usage

```python
from client.authClient import authClient

token = authClient.authenticate(username, password, service)
if token:
    is_valid = authClient.verify(token, service)
```

`authClient` is a module-level singleton (`AuthClient()`), so it should be imported and used directly rather than instantiated again. Because it is created at import time, the environment variables below must be set **before** `client.authClient` is first imported.

`authenticate()` and `verify()` don't raise on failure:

- `authenticate()` calls `POST /v1/security/auth` and returns the `access_token` string, or `None`.
- `verify()` calls `POST /v1/security/verify` with the token as a Bearer header and returns `True` only on HTTP 200, otherwise `False`. Its optional `method` argument (default `'local'`) is currently not forwarded to the server — the verification method is decided server-side.

Use `verify_or_raise(token, service)` when a server should not blame the token for an auth server problem (`windfire-calendar` does, and answers `503`). It returns `True` for a valid token and `False` on 401/403, and raises `AuthServerError` on timeouts, connection or TLS errors, on any other status, and on a 200 without a JSON body. `verify()` wraps it, logging the error and returning `False`.

Every request has a timeout of 3 seconds to connect and 10 seconds to read. Timeouts and connection errors are logged, and `authenticate()` / `verify()` return `None` / `False`.

### Secure defaults

TLS certificate verification is **on by default** (`VERIFY_SSL_CERTS` unset means `true`) and needs `ROOT_CA_PATH` to point at the Windfire Root CA. If `ROOT_CA_PATH` is unset or is not an existing file, `authenticate()` and `verify()` log an error naming `ROOT_CA_PATH` and return `None` / `False` without sending the request, and `verify_or_raise()` raises `AuthServerError`. Importing the client never fails because of this. Setting `VERIFY_SSL_CERTS=false` disables verification and logs a warning once, when the client is created.

## Configuration

The client resolves the auth server and its TLS behavior entirely from environment variables — there is no config file:

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `prod` | `dev` → `localhost:8443`; `prod` → `raspberry01:8444`. Any other value (including `test`) leaves host/port empty unless overridden below. |
| `WINDFIRE_SECURITY_HOST` | — | When set (non-empty), overrides the host resolved from `ENVIRONMENT`. |
| `WINDFIRE_SECURITY_PORT` | — | When set (non-empty), overrides the port resolved from `ENVIRONMENT`. Must be an integer; an invalid value is logged and ignored. |
| `ENFORCE_AUTH_SERVER_HTTPS` | `true` | Whether to call the auth server over `https` or `http` (`1`/`true`/`yes`/`on` count as true). |
| `VERIFY_SSL_CERTS` | `true` | Whether to verify the server's TLS certificate against `ROOT_CA_PATH`; when false, TLS verification is disabled entirely and a warning is logged. |
| `ROOT_CA_PATH` | — | Path to the Windfire Root CA bundle (produced by `windfire-security`'s `ssl/createRootCA.sh`). Required when `VERIFY_SSL_CERTS` is true: if it is unset or not an existing file, no request is sent (see [Secure defaults](#secure-defaults)). |

Consumers such as `windfire-calendar` use `WINDFIRE_SECURITY_HOST` / `WINDFIRE_SECURITY_PORT` to select the auth server explicitly; the `ENVIRONMENT` mapping remains the fallback (e.g. for `run-auth-client.sh`). The resolved host/port and its source are logged at `DEBUG` level on startup.

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

The script sets `VERIFY_SSL_CERTS=true` (from `common.sh`) and `ROOT_CA_PATH=~/opt/windfire/ssl/truststore/WindfireRootCA.crt`, the same Root CA path that `windfire-security`'s test scripts use, so the server certificate is verified.

The username defaults to `windfire` and the service to `windfire-calendar-srv` (both set in `common.sh`). Note that the **Test** option sets `ENVIRONMENT=test`, which has no host mapping in `authClient.py` — to use it, also export `WINDFIRE_SECURITY_HOST` / `WINDFIRE_SECURITY_PORT` before running the script.

Related scripts: `createPythonVenv.sh`, `activatePythonVenv.sh`, `deactivatePythonVenv.sh` manage that venv (its name, `windfire-security-client`, is set in `common.sh` as `PYTHON_CLIENT_VIRTUAL_ENV`); `installPrereqs.sh` installs the dependencies pinned in `requirements.txt`; `common.sh` holds shared shell variables/functions (environment selection, credential prompts, terminal colors).

## Building/publishing the package

```bash
./createModule.sh    # builds dist/*.whl and dist/*.tar.gz inside the project venv
```

The script uses the `windfire-security-client` venv's own Python, creating the venv first if it doesn't exist. This avoids PEP 668 errors from externally managed system Pythons (e.g. Homebrew), which refuse `pip install`. It then installs/upgrades `build` in the venv and runs `python -m build`.

Package metadata lives in [pyproject.toml](pyproject.toml) (distribution `windfire-security-client`, version `1.1.0`, single runtime dependency `requests`; the import package stays `client`). The build produces `dist/windfire_security_client-1.1.0-py3-none-any.whl` and `dist/windfire_security_client-1.1.0.tar.gz`.

## Project structure

```
.github/
├── dependabot.yml          # weekly dependency update checks
└── workflows/ci.yml        # CI workflow: compile, dependency audit, dependency review
client/
├── authClient.py           # AuthClient class + module-level `authClient` singleton
└── logger/
    └── loggerFactory.py    # shared color-formatted logger, file + console handlers
testAuth.py                 # smoke test: authenticate then verify
run-auth-client.sh          # end-to-end runner (venv + prereqs + smoke test)
createPythonVenv.sh / activatePythonVenv.sh / deactivatePythonVenv.sh
installPrereqs.sh           # installs the dependencies pinned in requirements.txt
requirements.txt            # pinned dependencies of the smoke test environment
createModule.sh             # builds the distributable package inside the venv
common.sh                   # shared shell variables/functions
pyproject.toml              # package metadata
```

## CI and dependency monitoring

The CI badge at the top of this page shows the result of the latest [CI workflow](.github/workflows/ci.yml) run on `main`; click it to see all runs. The workflow runs on every pull request and on every push to `main`:

- **Python**, on the same Python version as raspberry01 (3.11.2): installs `requirements.txt`, compiles the sources with `python -m compileall`, and audits the dependencies with `pip-audit`. It does not run `testAuth.py`, which needs a live auth server.
- **Dependency review**, on pull requests only: fails if the pull request adds a dependency with a known vulnerability of high or critical severity.

[Dependabot](.github/dependabot.yml) checks `requirements.txt`, `pyproject.toml` and the GitHub Actions in the workflow every week. It groups minor and patch updates into one pull request for Python and one for GitHub Actions, and major updates get their own pull requests. Each of the two has at most 5 version update pull requests open at a time.

To read the alerts, open **Security → Dependabot** on GitHub (https://github.com/robipozzi/windfire-security-client/security/dependabot). You need access to the repository's security alerts. Each alert shows the affected package and file, the severity, the advisory and the first patched version. To fix one, merge the Dependabot pull request or change the pin in `requirements.txt`. From the terminal:

```bash
gh api 'repos/robipozzi/windfire-security-client/dependabot/alerts?state=open' \
  --jq '.[] | [.security_advisory.severity, .dependency.package.name, .security_vulnerability.first_patched_version.identifier] | @tsv'
```

Dependabot cannot read versions set in shell scripts, so add new pins to `requirements.txt`, not to `installPrereqs.sh`.

## Notes

- The log directory is created if missing and must be writable: services sandboxed by systemd (`ProtectHome=read-only`) must set `WINDFIRE_SECURITY_CLIENT_LOG_DIR` to a directory listed in `ReadWritePaths`, otherwise importing the client fails with `Read-only file system`.
- When changing the public API (`authClient.authenticate()` / `authClient.verify()`), check consumers in sibling repos (e.g. `windfire-calendar`), which import `from client.authClient import authClient` directly.
- See [CLAUDE.md](CLAUDE.md) for more detailed internal/architecture notes.
