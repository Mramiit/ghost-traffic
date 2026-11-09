"""
Ghost Traffic - Chaos Fuzzing Engine
Coordinates concurrent asynchronous payload execution against the target server,
capturing latency, status codes, crash stack traces, and security verdicts.
"""

import asyncio
import json
import time
from typing import Any, Callable, Optional, Union
import urllib.error
import urllib.request

# Optional import of httpx with fallback to standard library urllib
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None  # type: ignore
    HTTPX_AVAILABLE = False


def classify_response(status_code: int) -> tuple[str, str, bool]:
    """
    Classifies HTTP status code into chaos categories and security verdicts:
        - CRASH (5xx) -> VULNERABLE
        - HANDLED (4xx) -> RESILIENT
        - BYPASSED (2xx) -> SUSPICIOUS
    """
    if status_code >= 500 or status_code == 0:
        return "CRASH (5xx)", "VULNERABLE", True
    elif 400 <= status_code < 500:
        return "HANDLED (4xx)", "RESILIENT", False
    elif 200 <= status_code < 300:
        return "BYPASSED (2xx)", "SUSPICIOUS", False
    return f"STATUS ({status_code})", "SUSPICIOUS", False


def truncate_preview(data: Any, max_chars: int = 400) -> str:
    """Truncates response body string to max_chars characters."""
    if isinstance(data, (dict, list)):
        raw = json.dumps(data)
    else:
        raw = str(data or "")
    if len(raw) > max_chars:
        return raw[:max_chars] + "..."
    return raw


async def _execute_single_attack(
    client: Optional[Any],
    target_url: str,
    method: str,
    attack: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    """
    Sends a single attack payload and measures execution metrics.
    """
    payload = attack.get("payload", {})
    start_time = time.perf_counter()
    status_code = 0
    data: Any = None
    error_message: Optional[str] = None

    if HTTPX_AVAILABLE and client is not None:
        try:
            response = await client.request(
                method=method.upper(),
                url=target_url,
                json=payload,
                timeout=timeout,
            )
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            status_code = response.status_code
            try:
                data = response.json()
            except Exception:
                data = response.text

        except httpx.TimeoutException:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            status_code = 504
            error_message = f"Request timed out after {timeout}s"
            data = {"error": "TimeoutException", "detail": error_message}

        except httpx.ConnectError as ce:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            status_code = 0
            error_message = f"Connection failed to {target_url}: {ce}"
            data = {"error": "ConnectError", "detail": str(ce)}

        except Exception as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            status_code = 0
            error_message = f"HTTP client error: {e}"
            data = {"error": e.__class__.__name__, "detail": str(e)}

    else:
        # Standard library urllib fallback in executor thread
        loop = asyncio.get_running_loop()

        def _sync_request() -> tuple[int, Any, Optional[str]]:
            body_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url=target_url,
                data=body_bytes,
                headers={"Content-Type": "application/json", "User-Agent": "Ghost-Traffic-Fuzzer/1.0"},
                method=method.upper(),
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    code = resp.status
                    raw = resp.read().decode("utf-8", errors="replace")
                    try:
                        return code, json.loads(raw), None
                    except Exception:
                        return code, raw, None
            except urllib.error.HTTPError as he:
                raw = he.read().decode("utf-8", errors="replace")
                try:
                    return he.code, json.loads(raw), None
                except Exception:
                    return he.code, raw, None
            except urllib.error.URLError as ue:
                return 0, {"error": "ConnectError", "detail": str(ue.reason)}, str(ue.reason)
            except Exception as ex:
                return 0, {"error": ex.__class__.__name__, "detail": str(ex)}, str(ex)

        status_code, data, error_message = await loop.run_in_executor(None, _sync_request)
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    category, verdict, is_crash = classify_response(status_code)
    response_preview = truncate_preview(data, max_chars=400)

    # Return enriched result dictionary
    result = {
        **attack,
        "target_url": target_url,
        "method": method.upper(),
        "status_code": status_code,
        "latency_ms": latency_ms,
        "category": category,
        "verdict": verdict,
        "is_crash": is_crash,
        "response_preview": response_preview,
        "raw_response": data,
        "error_message": error_message,
    }
    return result


async def execute_swarm(
    target_url: str,
    method: str = "POST",
    attacks: Optional[list[dict[str, Any]]] = None,
    on_progress_callback: Optional[Callable[[dict[str, Any]], Any]] = None,
    timeout: float = 5.0,
    concurrency: int = 3,
    delay_between_requests: float = 0.35,
) -> list[dict[str, Any]]:
    """
    Executes a swarm of chaos attack payloads against the target endpoint.

    Args:
        target_url: The full HTTP URL of the target endpoint.
        method: HTTP method (default "POST").
        attacks: List of attack dictionaries containing persona, attack_name, hypothesis, payload.
        on_progress_callback: Optional callback invoked after each request completes.
        timeout: Request timeout in seconds (default 5.0).
        concurrency: Semaphore concurrency limit (default 3).
        delay_between_requests: Pause duration in seconds between dispatches for dramatic pacing (default 0.35).

    Returns:
        Enriched list of test results with categories, verdicts, latencies, and previews.
    """
    if attacks is None:
        attacks = []

    semaphore = asyncio.Semaphore(concurrency)
    results: list[dict[str, Any]] = []

    async def _worker(client: Optional[Any], attack_item: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            if delay_between_requests > 0:
                await asyncio.sleep(delay_between_requests)

            res = await _execute_single_attack(
                client=client,
                target_url=target_url,
                method=method,
                attack=attack_item,
                timeout=timeout,
            )

            # Invoke optional live progress callback
            if on_progress_callback is not None:
                try:
                    if asyncio.iscoroutinefunction(on_progress_callback):
                        await on_progress_callback(res)
                    else:
                        on_progress_callback(res)
                except Exception:
                    pass

            return res

    if HTTPX_AVAILABLE:
        async with httpx.AsyncClient(timeout=timeout) as client:
            tasks = [_worker(client, attack) for attack in attacks]
            results = await asyncio.gather(*tasks)
    else:
        tasks = [_worker(None, attack) for attack in attacks]
        results = await asyncio.gather(*tasks)

    return list(results)


class ChaosFuzzer:
    """
    Object-oriented wrapper around the swarm execution engine.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        concurrency: int = 3,
        timeout: float = 5.0,
        delay_between_requests: float = 0.35,
    ):
        self.base_url = base_url.rstrip("/")
        self.concurrency = concurrency
        self.timeout = timeout
        self.delay_between_requests = delay_between_requests

    async def run_swarm(
        self,
        endpoint: str = "/api/v1/checkout",
        method: str = "POST",
        attacks: Optional[list[dict[str, Any]]] = None,
        on_progress_callback: Optional[Callable[[dict[str, Any]], Any]] = None,
    ) -> list[dict[str, Any]]:
        full_url = f"{self.base_url}{endpoint}"
        return await execute_swarm(
            target_url=full_url,
            method=method,
            attacks=attacks,
            on_progress_callback=on_progress_callback,
            timeout=self.timeout,
            concurrency=self.concurrency,
            delay_between_requests=self.delay_between_requests,
        )
