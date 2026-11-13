# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

`windfire-security-client` is a small, installable Python package (distribution `windfire-security-client`, import package `client`) that other Windfire services embed to talk to the [windfire-security](../windfire-security) authentication server — it is the client-side counterpart to that repo's `/v1/security/auth` and `/v1/security/verify` endpoints. It is not run standalone; it's consumed via editable pip install:

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

`createPythonVenv.sh` / `activatePythonVenv.sh` / `deactivatePythonVenv.sh` manage that venv (name defined in `common.sh` as `PYTHON_CLIENT_VIRTUAL_ENV`). `installPrereqs.sh` installs the dependencies pinned in `requirements.txt`, which holds only `requests`, the package's single runtime dependency.

## Building/publishing the package

```bash
./createModule.sh    # pip install build; python3 -m build -> produces dist/*.whl and dist/*.tar.gz
```

Package metadata lives in `pyproject.toml` (distribution `windfire-security-client`, version `1.1.0`, single runtime dependency `requests`). The import package is still `client`, so consumers keep `from client.authClient import authClient`. The wheel is `dist/windfire_security_client-1.1.0-py3-none-any.whl`. Before 1.1.0 the distribution was named `client` (wheels `client-1.0.x-py3-none-any.whl`): environments that have it installed should `pip uninstall client` before installing the new one.

`run-auth-client.sh` passes `VERIFY_SSL_CERTS=true` (from `common.sh`) and `ROOT_CA_PATH=$HOME/opt/windfire/ssl/truststore/WindfireRootCA.crt`, the same Root CA path `windfire-security`'s test scripts use.

## Architecture

The entire package is `client/authClient.py`, exposing a module-level singleton `authClient = AuthClient()` — callers import and use that instance directly rather than instantiating `AuthClient()` themselves.

`AuthClient.__init__` resolves the target auth server purely from environment variables, no config file:
- `ENVIRONMENT` (default `prod`; `dev` → `localhost:8443`, `prod` → `raspberry01:8444`) — there is no `test` case in the mapping despite `common.sh`'s environment-selection menu offering "Test" as option 2; `test` (or any other value) leaves host/port empty unless overridden.
- `WINDFIRE_SECURITY_HOST` / `WINDFIRE_SECURITY_PORT` — when set (non-empty), override the host/port resolved from `ENVIRONMENT` (port is cast to `int`; an invalid port is logged and ignored). Consumers such as `windfire-calendar` use these to select the auth server explicitly; the `ENVIRONMENT` mapping remains the fallback (e.g. for `run-auth-client.sh`).
- `ENFORCE_AUTH_SERVER_HTTPS` (default `true`) — selects `https` vs `http` for `url_base`.
- `VERIFY_SSL_CERTS` (default `true`, secure by default) — whether to verify against `ROOT_CA_PATH`, or disable TLS verification entirely. An explicit false value logs a warning once, in `__init__`.
- `ROOT_CA_PATH` — path to the Windfire Root CA bundle (produced by `windfire-security`'s `ssl/createRootCA.sh`), used as `requests`' `verify=` argument when `VERIFY_SSL_CERTS` is true. `__init__` never raises, because the singleton is built at import time. Instead `_tls_config_ok()` runs at the start of `authenticate()`, `verify()` and `verify_or_raise()`: when verification is on and `ROOT_CA_PATH` is unset or not an existing file, it logs an error naming `ROOT_CA_PATH` and no request is sent (`None` / `False` / `AuthServerError`).

The `verify=` argument is built only in `_requests_verify()`. Every request uses `REQUEST_TIMEOUT_SECONDS = (3, 10)` (connect, read). `requests.Timeout` and `requests.ConnectionError` are logged and become `None` / `False`; `verify_or_raise()` raises `AuthServerError` for them.

Two main methods, both POSTing JSON to the auth server and returning a simplified result rather than raising on failure (callers check for `None`/`False`, not exceptions):
- `authenticate(username, password, service) -> token | None` — calls `POST /v1/security/auth`, returns the `access_token` string or `None`.
- `verify(token, service, method='local') -> bool` — calls `POST /v1/security/verify` with the token as a Bearer header, returns `True` only on HTTP 200. Note: the `method` parameter is accepted but not actually forwarded to the server request — verification method is entirely determined server-side.

`verify()` wraps `verify_or_raise(token, service) -> bool`, which returns `False` only on 401/403 and raises `AuthServerError` when the server gives no usable answer (connection/TLS error, other status, 200 without a JSON body). `windfire-calendar` calls it to return 503 instead of a misleading 401.

Logging: `client/logger/loggerFactory.py` mirrors the logger used in `windfire-security` (same `ColorFormatter`, `LOG_LEVEL`/`DEFAULT_LOG_LEVEL` env resolution) and writes its file handler to `windfire-security-client.log` in `WINDFIRE_SECURITY_CLIENT_LOG_DIR` (default `$HOME/logs`), creating the directory if missing. The handler is built at import time, so an unwritable directory (e.g. `/home/pi` under systemd `ProtectHome=read-only`) makes importing `client.authClient` fail — sandboxed consumers must point the variable at a writable path. Always get loggers via `logger_factory.get_logger(<name>)`, never `logging.getLogger` directly.
