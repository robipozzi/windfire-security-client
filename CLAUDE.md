# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

`windfire-security-client` is a small, installable Python package (`client`) that other Windfire services embed to talk to the [windfire-security](../windfire-security) authentication server — it is the client-side counterpart to that repo's `/v1/security/auth` and `/v1/security/verify` endpoints. It is not run standalone; it's consumed via editable pip install:

```bash
pip3 install -e $HOME/dev/windfire-security-client
```

`windfire-security`'s own `test/` scripts install it this way (see its `test/installPrereqs.sh`), and any other Windfire service that needs to authenticate/verify tokens is expected to do the same. When changing this package's public API (`authClient.authenticate()` / `authClient.verify()`), check consumers in sibling repos (e.g. `windfire-calendar`) since they import `from client.authClient import authClient` directly.

## Running the built-in smoke test

```bash
./run-auth-client.sh          # prompts for environment (1=dev,2=test,3=prod), then username/password/service
./run-auth-client.sh 1        # skip the environment prompt, go straight to dev
```

This creates/activates the `windfire-security-client` venv, installs prerequisites, and runs `testAuth.py`, which authenticates against the real auth server for the given environment and then verifies the resulting token. There is no automated/unit test suite — this is the only test entry point, and it requires a live `windfire-security` auth server to be reachable at the resolved host:port.

`createPythonVenv.sh` / `activatePythonVenv.sh` / `deactivatePythonVenv.sh` manage that venv (name defined in `common.sh` as `PYTHON_CLIENT_VIRTUAL_ENV`). `installPrereqs.sh` installs the pinned dependencies — note it currently also installs Google Calendar API packages (`google-auth-oauthlib`, `google-api-python-client`, etc.) that this package doesn't use; if editing dependencies, check whether that's cruft from copy-pasting another Windfire service's script before assuming it's required.

## Building/publishing the package

```bash
./createModule.sh    # pip install build; python3 -m build -> produces dist/*.whl and dist/*.tar.gz
```

Package metadata lives in `pyproject.toml` (name `client`, version `1.0.0`, single runtime dependency `requests`).

## Architecture

The entire package is `client/authClient.py`, exposing a module-level singleton `authClient = AuthClient()` — callers import and use that instance directly rather than instantiating `AuthClient()` themselves.

`AuthClient.__init__` resolves the target auth server purely from environment variables, no config file:
- `ENVIRONMENT` (default `prod`; `dev` → `localhost:8443`, `prod` → `raspberry01:8444`) — there is no `test` case in the mapping despite `common.sh`'s environment-selection menu offering "Test" as option 2; `test` (or any other value) leaves host/port empty unless overridden.
- `KEYCLOAK_SERVER_HOST` / `KEYCLOAK_SERVER_PORT` — when set (non-empty), override the host/port resolved from `ENVIRONMENT` (port is cast to `int`; an invalid port is logged and ignored). Consumers such as `windfire-calendar` use these to select the auth server explicitly; the `ENVIRONMENT` mapping remains the fallback (e.g. for `run-auth-client.sh`).
- `ENFORCE_AUTH_SERVER_HTTPS` (default `true`) — selects `https` vs `http` for `url_base`.
- `VERIFY_SSL_CERTS` (default `false`) — whether to verify against `ROOT_CA_PATH`, or disable TLS verification entirely.
- `ROOT_CA_PATH` — path to the Windfire Root CA bundle (produced by `windfire-security`'s `ssl/createRootCA.sh`), used as `requests`' `verify=` argument when `VERIFY_SSL_CERTS` is true.

Two methods, both POSTing JSON to the auth server and returning a simplified result rather than raising on failure (callers check for `None`/`False`, not exceptions):
- `authenticate(username, password, service) -> token | None` — calls `POST /v1/security/auth`, returns the `access_token` string or `None`.
- `verify(token, service, method='local') -> bool` — calls `POST /v1/security/verify` with the token as a Bearer header, returns `True` only on HTTP 200. Note: the `method` parameter is accepted but not actually forwarded to the server request — verification method is entirely determined server-side.

Logging: `client/logger/loggerFactory.py` mirrors the logger used in `windfire-security` (same `ColorFormatter`, `LOG_LEVEL`/`DEFAULT_LOG_LEVEL` env resolution) but hardcodes its file handler to `$HOME/logs/windfire-security-client.log` — that directory must exist on the host before any client code runs, or the `TimedRotatingFileHandler` will fail to initialize. Always get loggers via `logger_factory.get_logger(<name>)`, never `logging.getLogger` directly.
