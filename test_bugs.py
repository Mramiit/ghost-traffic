"""
Ghost Traffic - Target Server Bug Verification Test
Tests all 5 deliberate backend bugs and happy path in target_server/app.py.
Runs in-memory without external network dependencies.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Ensure UTF-8 stdout on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure target_server can be imported
sys.path.insert(0, str(Path(__file__).parent / "target_server"))

from app import app, process_checkout, unhandled_crash_exception_handler


class MockRequest:
    """Mock FastAPI/Starlette Request for in-memory testing."""

    def __init__(self, data: Any):
        self._data = data
        self.url = type("Url", (), {"path": "/api/v1/checkout"})()
        self.method = "POST"

    async def json(self) -> Any:
        return self._data


def run_coro(coro):
    """Executes an async route coroutine synchronously without socket loop."""
    try:
        sub = coro.send(None)
        # Handle inner coroutine await (e.g. await request.json())
        val = None
        while True:
            try:
                sub.send(None)
            except StopIteration as e:
                val = e.value
                break
        return coro.send(val)
    except StopIteration as e:
        return e.value


def test_endpoint(payload: Any) -> tuple[int, dict]:
    req = MockRequest(payload)
    try:
        res = run_coro(process_checkout(req))
        if hasattr(res, "status_code"):
            # Starlette JSONResponse
            body = json.loads(res.body.decode("utf-8")) if hasattr(res, "body") else {}
            return res.status_code, body
        return 200, res
    except Exception as exc:
        # Pass through the global exception handler
        crash_res = run_coro(unhandled_crash_exception_handler(req, exc))
        body = json.loads(crash_res.body.decode("utf-8"))
        return crash_res.status_code, body


def main():
    test_cases = [
        (
            "Happy Path Checkout",
            {
                "username": "alex_shopper",
                "quantity": 2,
                "coupon_code": "SUMMER20",
                "shipping_note": "Leave at front porch",
                "metadata": {"utm_source": "google"},
            },
            200,
            None,
        ),
        (
            "Bug 1: ZeroDivisionError (quantity = 0)",
            {"username": "tester", "quantity": 0},
            500,
            "ZeroDivisionError",
        ),
        (
            "Bug 1: Negative Logic (quantity < 0)",
            {"username": "tester", "quantity": -3},
            500,
            "ValueError",
        ),
        (
            "Bug 2: SQL Injection Simulation (contains ' OR)",
            {"username": "alice", "quantity": 1, "coupon_code": "DISCOUNT' OR 1=1 --"},
            500,
            "OperationalError",
        ),
        (
            "Bug 2: SQL Injection Simulation (contains --)",
            {"username": "alice", "quantity": 1, "coupon_code": "CODE--"},
            500,
            "OperationalError",
        ),
        (
            "Bug 3: Unicode 4-byte Emoji Crash in username",
            {"username": "alex_🚀_vip", "quantity": 1},
            500,
            "UnicodeEncodeError",
        ),
        (
            "Bug 3: Unicode Zero-Width Joiner in shipping_note",
            {"username": "alex", "quantity": 1, "shipping_note": "Deliver to \u200d suite"},
            500,
            "UnicodeEncodeError",
        ),
        (
            "Bug 4: Deep Nesting (> 5 levels) RecursionError",
            {
                "username": "charlie",
                "quantity": 1,
                "metadata": {"l1": {"l2": {"l3": {"l4": {"l5": {"l6": "deep"}}}}}},
            },
            500,
            "RecursionError",
        ),
        (
            "Bug 5: Type Confusion on coupon_code (integer)",
            {"username": "david", "quantity": 1, "coupon_code": 12345},
            500,
            "AttributeError",
        ),
        (
            "Bug 5: Type Confusion on coupon_code (array)",
            {"username": "david", "quantity": 1, "coupon_code": ["VIP", "SAVE"]},
            500,
            "AttributeError",
        ),
    ]

    print("=" * 80)
    print(" 👻 GHOST TRAFFIC TARGET SERVER VULNERABILITY VERIFICATION SUITE")
    print("=" * 80)

    all_passed = True
    for name, payload, expected_status, expected_error in test_cases:
        status, response_data = test_endpoint(payload)
        actual_error = response_data.get("error") if isinstance(response_data, dict) else None

        passed = (status == expected_status) and (
            expected_error is None or actual_error == expected_error
        )
        all_passed = all_passed and passed
        badge = "PASS" if passed else "FAIL"

        err_info = f" | Error: {actual_error}" if actual_error else ""
        print(f"[{badge}] {name:<50} -> HTTP {status}{err_info}")
        if status == 500:
            detail = response_data.get("detail", "")
            print(f"        Detail: {detail}")
            has_tb = bool(response_data.get("traceback"))
            print(f"        Traceback Included: {has_tb} ({len(response_data.get('traceback', []))} lines)")

    print("=" * 80)
    if all_passed:
        print("ALL 10 TESTS PASSED! Target server deliberately crashes on all 5 bugs with HTTP 500 and full traceback.")
    else:
        print("Test failures detected.")
        sys.exit(1)


if __name__ == "__main__":
    main()
