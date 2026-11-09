"""
Ghost Traffic - Deliberately Vulnerable Target Server
Designed for Autonomous Chaos QA Swarm fuzzing validation.

Endpoints:
    POST /api/v1/checkout - Realistic e-commerce checkout with 5 deliberate backend bugs:
        1. ZeroDivisionError / Negative Logic (quantity <= 0)
        2. SQL Injection Simulation (coupon_code with SQL operators)
        3. Unicode/Emoji Encoding Crash (legacy driver crash on 4-byte UTF-8 / ZWJ)
        4. Deep Nesting / RecursionError (metadata nested > 5 levels)
        5. Type Confusion (raw JSON access, coupon_code.upper() on non-string)
"""

import json
import os
import sqlite3
import traceback
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Ghost Market - Vulnerable Target Server",
    description="Intentionally vulnerable e-commerce checkout service for Chaos QA Swarm testing.",
    version="1.0.0",
)


@app.exception_handler(Exception)
async def unhandled_crash_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global crash handler that intercepts unhandled backend errors and returns
    detailed traceback information in the JSON payload with HTTP 500.
    """
    tb_str = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.__class__.__name__,
            "detail": str(exc),
            "exception_type": f"{exc.__class__.__module__}.{exc.__class__.__name__}",
            "traceback": tb_str.splitlines(),
            "raw_traceback": tb_str,
            "path": request.url.path,
            "method": request.method,
        },
    )


def verify_legacy_encoding(text: str, field_name: str) -> None:
    """
    Simulates a legacy database driver (e.g. latin-1 or MySQL 3-byte utf8mb3)
    that crashes with a UnicodeEncodeError when encountering 4-byte UTF-8 emojis
    or zero-width joiners (ZWJ/ZWNJ).
    """
    if not isinstance(text, str):
        return

    for idx, ch in enumerate(text):
        code_point = ord(ch)
        # 4-byte UTF-8 code points (>= 0x10000) or Zero-Width Joiner (U+200D) / Non-Joiner (U+200C)
        if code_point >= 0x10000 or ch in ("\u200d", "\u200c"):
            raise UnicodeEncodeError(
                "latin-1",
                text,
                idx,
                idx + 1,
                f"ordinal not in range(256): legacy driver failed encoding character '{ch}' (U+{code_point:04X}) for column '{field_name}'",
            )


def calculate_nesting_depth(obj: Any, current_depth: int = 1) -> int:
    """
    Recursively determines the maximum nesting depth of JSON structures.
    """
    if isinstance(obj, dict):
        if not obj:
            return current_depth
        return max(calculate_nesting_depth(v, current_depth + 1) for v in obj.values())
    elif isinstance(obj, list):
        if not obj:
            return current_depth
        return max(calculate_nesting_depth(item, current_depth + 1) for item in obj)
    return current_depth


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "Ghost Traffic Vulnerable Target Server",
        "status": "online",
        "checkout_endpoint": "/api/v1/checkout",
        "schema_endpoint": "/schema",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/schema")
async def get_schema() -> JSONResponse:
    schema_path = Path(__file__).parent / "sample_schema.json"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            return JSONResponse(content=json.load(f))
    return JSONResponse(status_code=404, content={"error": "SchemaNotFound"})


@app.post("/api/v1/checkout")
async def process_checkout(request: Request) -> Any:
    """
    E-Commerce checkout endpoint intentionally implemented with raw JSON parsing
    and 5 deliberate backend vulnerability triggers.
    """
    # Parse raw JSON body without strict Pydantic model validation
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "MalformedJSON", "message": "Request payload must be valid JSON."},
        )

    if not isinstance(body, dict):
        return JSONResponse(
            status_code=400,
            content={"error": "InvalidPayload", "message": "Payload must be a JSON object."},
        )

    # Extract request attributes
    username = body.get("username")
    quantity = body.get("quantity")
    coupon_code = body.get("coupon_code")
    shipping_note = body.get("shipping_note")
    metadata = body.get("metadata")

    # =========================================================================
    # BUG 5: Type Confusion
    # Unsafely calling string method .upper() without checking instance type.
    # Passing an integer or array triggers an unhandled AttributeError.
    # =========================================================================
    if coupon_code is not None:
        coupon_normalized = coupon_code.upper()

        # =====================================================================
        # BUG 2: SQL Injection Simulation
        # Simulated raw unparameterized SQL query execution for coupon lookup.
        # =====================================================================
        if "' OR" in coupon_normalized or "--" in str(coupon_code) or ";" in str(coupon_code):
            raise sqlite3.OperationalError('near "OR": syntax error in raw query')

    # =========================================================================
    # BUG 1: ZeroDivisionError / Negative Logic
    # Dividing shipping cost by quantity or raising ValueError on underflow.
    # =========================================================================
    if quantity is not None:
        if quantity == 0:
            base_shipping_charge = 45.0
            # Division by zero when allocating per-item shipping cost
            per_item_shipping = base_shipping_charge / quantity
        elif isinstance(quantity, (int, float)) and quantity < 0:
            raise ValueError("Inventory underflow: negative reserve")

    # =========================================================================
    # BUG 3: Unicode/Emoji Encoding Crash
    # Simulates legacy driver/database column crash when encountering 4-byte
    # UTF-8 emojis or zero-width joiners in username or shipping_note.
    # =========================================================================
    if username is not None:
        verify_legacy_encoding(str(username) if not isinstance(username, str) else username, "username")

    if shipping_note is not None:
        verify_legacy_encoding(str(shipping_note) if not isinstance(shipping_note, str) else shipping_note, "shipping_note")

    # =========================================================================
    # BUG 4: Deep Nesting / RecursionError
    # If metadata is nested deeper than 5 levels, execute recursive parsing
    # without termination guard, triggering RecursionError.
    # =========================================================================
    if metadata is not None and isinstance(metadata, (dict, list)):
        depth = calculate_nesting_depth(metadata)
        if depth > 5:
            def _recursive_parser(node: Any) -> Any:
                return _recursive_parser(node)

            _recursive_parser(metadata)

    # -------------------------------------------------------------------------
    # Happy Path / Validation
    # -------------------------------------------------------------------------
    if not username or quantity is None:
        return JSONResponse(
            status_code=400,
            content={
                "error": "ValidationError",
                "message": "Both 'username' and 'quantity' are required fields.",
            },
        )

    # Calculate valid checkout totals
    unit_price = 49.99
    subtotal = unit_price * quantity
    discount_amount = 10.0 if coupon_code else 0.0
    shipping_cost = 15.0
    total_amount = max(0.0, subtotal + shipping_cost - discount_amount)

    return {
        "status": "success",
        "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
        "username": username,
        "quantity": quantity,
        "coupon_applied": coupon_code,
        "shipping_cost": shipping_cost,
        "discount_applied": discount_amount,
        "total_amount": round(total_amount, 2),
        "message": "Checkout completed successfully.",
    }


if __name__ == "__main__":
    host = os.getenv("TARGET_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("TARGET_SERVER_PORT", "8000"))
    print(f"Starting Ghost Traffic Target Server on http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=True)

