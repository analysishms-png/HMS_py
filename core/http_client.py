"""HTTP client foundation (VB6 MobWebAPI.bas port).

Ports MobWebAPI.bas:
- Proc_344_0: GET  (MSXML2.ServerXMLHTTP, WaitForResponse 10000 ms)
- Proc_344_1: POST (Content-Type: application/json; charset=utf-8)

Stdlib only (urllib.request); no requests dependency required.
Returns (status, body, headers). Transport failures: retry once on
timeout, then log_error + raise HTTPClientError. HTTP-level 4xx/5xx
are responses (ServerXMLHTTP semantics) — returned, not raised.
url_encode: reuse HMS_py.core.url_utils.encode_url.
"""
from __future__ import annotations

import socket
import urllib.error
import urllib.request
from typing import Any, Mapping

from HMS_py.core.error_handling import log_error
from HMS_py.core.url_utils import decode_url, encode_url  # noqa: F401  (re-export)

DEFAULT_TIMEOUT = 10.0  # VB6 WaitForResponse 10000 ms
JSON_CONTENT_TYPE = "application/json; charset=utf-8"  # VB6 Proc_344_1
_DEFAULT_HEADERS = {
    "User-Agent": "HMS_py/1.0 (+urllib)",
    "Accept": "*/*",
}


class HTTPClientError(OSError):
    """Transport-level HTTP failure (timeout/DNS/connect) after retry."""

    def __init__(self, message: str, url: str = "", cause: BaseException | None = None):
        super().__init__(message)
        self.url = url
        self.cause = cause


def build_query(params: Mapping[str, Any] | None = None, **kwargs: Any) -> str:
    """Percent-encoded query string via url_utils.encode_url (space -> '+')."""
    items: dict[str, Any] = dict(params or {})
    items.update(kwargs)
    return "&".join(
        f"{encode_url(k)}={encode_url(v)}" for k, v in items.items()
    )


def _is_timeout(exc: BaseException) -> bool:
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return True
    if isinstance(exc, urllib.error.URLError) and exc.reason is not None:
        return isinstance(exc.reason, (socket.timeout, TimeoutError))
    return False


def _read_body(resp) -> str:
    raw = resp.read()
    if not raw:
        return ""
    charset = "utf-8"
    headers = getattr(resp, "headers", None)
    if headers is not None:
        try:
            charset = headers.get_content_charset() or "utf-8"
        except (AttributeError, LookupError):
            charset = "utf-8"
    try:
        return raw.decode(charset, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def _request(
    method: str,
    url: str,
    data: bytes | str | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    retry_on_timeout: bool = True,
    procedure: str = "",
) -> tuple[int, str, dict[str, str]]:
    """Single HTTP request. Returns (status, body, headers dict)."""
    if not url or not str(url).strip():
        raise HTTPClientError("URL empty", url=str(url))

    body_bytes: bytes | None = None
    if data is not None:
        body_bytes = data if isinstance(data, bytes) else str(data).encode("utf-8")

    hdrs = dict(_DEFAULT_HEADERS)
    if headers:
        hdrs.update(headers)

    attempts = 2 if retry_on_timeout else 1
    last_exc: BaseException | None = None

    for attempt in range(attempts):
        req = urllib.request.Request(url, data=body_bytes, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = int(getattr(resp, "status", None) or resp.getcode() or 0)
                body = _read_body(resp)
                hdr_out = {k: v for k, v in resp.headers.items()} if resp.headers else {}
                return status, body, hdr_out
        except urllib.error.HTTPError as exc:
            # Server responded — HTTP-level error, not transport failure.
            try:
                body = _read_body(exc)
            except OSError:
                body = ""
            hdr_out = {k: v for k, v in (exc.headers or {}).items()}
            log_error(
                f"HTTP {exc.code} {method} {url}",
                procedure=procedure or f"http_client.{method.lower()}",
                severity=20,
                extra=body[:300],
            )
            return int(exc.code), body, hdr_out
        except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
            last_exc = exc
            if attempt + 1 < attempts and _is_timeout(exc):
                continue
            break

    err = last_exc or HTTPClientError("unknown transport failure", url=url)
    log_error(
        err,
        procedure=procedure or f"http_client.{method.lower()}",
        severity=30,
        extra=f"url={url}",
    )
    if isinstance(err, HTTPClientError):
        raise err
    raise HTTPClientError(str(err), url=url, cause=err) from err


def http_get(
    url: str,
    timeout: float = DEFAULT_TIMEOUT,
    headers: Mapping[str, str] | None = None,
    *,
    retry_on_timeout: bool = True,
    procedure: str = "",
) -> tuple[int, str, dict[str, str]]:
    """VB6 MobWebAPI Proc_344_0 — GET, returns (status, body, headers).

    Empty body + non-2xx is still returned (caller decides). Transport
    failure after one timeout-retry raises HTTPClientError (logged).
    """
    return _request(
        "GET", url, data=None, headers=headers, timeout=timeout,
        retry_on_timeout=retry_on_timeout, procedure=procedure or "http_client.http_get",
    )


def http_post(
    url: str,
    data: bytes | str | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    json_body: str | bytes | None = None,
    retry_on_timeout: bool = True,
    procedure: str = "",
) -> tuple[int, str, dict[str, str]]:
    """VB6 MobWebAPI Proc_344_1 — POST.

    Default Content-Type: application/json; charset=utf-8 (VB6).
    Pass raw `data` (bytes/str) or `json_body` (str/dict-serialised).
    Returns (status, body, headers); raises HTTPClientError on transport
    failure after one timeout-retry (logged via log_error).
    """
    payload = json_body if json_body is not None else data
    hdrs = {"Content-Type": JSON_CONTENT_TYPE}
    if headers:
        hdrs.update(headers)
    elif payload is None:
        # still declare JSON content-type per VB6 when body empty
        pass
    return _request(
        "POST", url, data=payload, headers=hdrs, timeout=timeout,
        retry_on_timeout=retry_on_timeout, procedure=procedure or "http_client.http_post",
    )


__all__ = [
    "DEFAULT_TIMEOUT",
    "JSON_CONTENT_TYPE",
    "HTTPClientError",
    "build_query",
    "encode_url",
    "decode_url",
    "http_get",
    "http_post",
]
