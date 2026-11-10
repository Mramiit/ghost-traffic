"""
Ghost Traffic - BharatCode LLM Client
Connects to the BharatCode API (OpenAI-compatible) to autonomously generate
adversarial chaos payloads across 5 distinct attacker personas and perform
automated Root Cause Analysis (RCA) on server crashes.
"""

import json
import os
import re
from typing import Any, Optional

# Load environment configuration from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Graceful fallback: manually parse .env file if python-dotenv is not yet installed
    for env_candidate in (".env", os.path.join(os.path.dirname(__file__), "..", ".env")):
        if os.path.isfile(env_candidate):
            with open(env_candidate, "r", encoding="utf-8") as _f:
                for _line in _f:
                    _line = _line.strip()
                    if _line and not _line.startswith("#") and "=" in _line:
                        _k, _v = _line.split("=", 1)
                        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
            break

# BharatCode API Configuration (OpenAI-compatible)
BHARATCODE_API_KEY: str = (
    os.getenv("BHARATCODE_API_KEY")
    or os.getenv("OPENAI_API_KEY")
    or ""
)
BHARATCODE_BASE_URL: str = (
    os.getenv("BHARATCODE_BASE_URL")
    or os.getenv("OPENAI_BASE_URL")
    or "https://bharatcode.ai/api/model/v1"
)
BHARATCODE_MODEL: str = (
    os.getenv("BHARATCODE_MODEL")
    or os.getenv("OPENAI_MODEL")
    or "qwen-3.8-27b"
)

# Optional lazy import of AsyncOpenAI to allow offline usage
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None  # type: ignore


def get_async_openai_client() -> Optional[Any]:
    """
    Initializes and returns an AsyncOpenAI client pointing to the BharatCode base URL.
    Returns None if the openai package is not installed.
    """
    if AsyncOpenAI is None:
        return None
    api_key = BHARATCODE_API_KEY if BHARATCODE_API_KEY else "dummy_key_for_init"
    return AsyncOpenAI(
        api_key=api_key,
        base_url=BHARATCODE_BASE_URL,
    )


# Module-level client instance
client: Optional[Any] = get_async_openai_client()


def is_api_configured() -> bool:
    """
    Checks if a real BharatCode / OpenAI API key is configured.
    """
    if not BHARATCODE_API_KEY:
        return False
    placeholder_keys = {
        "your_bharatcode_api_key_here",
        "bc_live_your_api_key_here",
        "your_api_key_here",
        "your_openai_api_key_here",
        "dummy_key_for_init",
    }
    return BHARATCODE_API_KEY.strip() not in placeholder_keys


def clean_and_parse_json(raw_text: str) -> Any:
    """
    Robust JSON parser helper that strips markdown code fences (```json ... ```)
    and trims stray conversational preamble from LLM responses.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty response string")

    cleaned = raw_text.strip()

    # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Extract outermost JSON array [...] or object {...} using regex
    array_match = re.search(r"\[[\s\S]*\]", cleaned)
    if array_match:
        try:
            return json.loads(array_match.group(0))
        except json.JSONDecodeError:
            pass

    obj_match = re.search(r"\{[\s\S]*\}", cleaned)
    if obj_match:
        try:
            return json.loads(obj_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse valid JSON from text: {cleaned[:100]}...")


def get_fallback_chaos_payloads() -> list[dict[str, Any]]:
    """
    Provides a resilient suite of 8 hardcoded chaos test cases across all
    5 Chaos Personas to guarantee bulletproof live demos even if API times out.
    """
    return [
        {
            "persona": "The SQL Injector",
            "attack_name": "Coupon Code Raw Query SQL Injection Bypass",
            "hypothesis": "Unsanitized coupon_code concatenated into raw SQL string will trigger OperationalError.",
            "payload": {
                "username": "shopper_sqli",
                "quantity": 1,
                "coupon_code": "' OR 1=1 --",
                "shipping_note": "Deliver to front desk",
                "metadata": {"source": "fuzzer"},
            },
        },
        {
            "persona": "The SQL Injector",
            "attack_name": "Stacked Semicolon Query Injection",
            "hypothesis": "Semicolon query stacking in coupon_code will trigger a database syntax parser crash.",
            "payload": {
                "username": "admin_test",
                "quantity": 1,
                "coupon_code": "DISCOUNT; DROP TABLE coupons;--",
                "shipping_note": "Urgent order",
                "metadata": {"campaign": "fall_sale"},
            },
        },
        {
            "persona": "The Unicode Gremlin",
            "attack_name": "4-Byte Emoji UTF-8 Latin-1 Database Crash",
            "hypothesis": "4-byte UTF-8 emojis in username cause legacy database driver crash with UnicodeEncodeError.",
            "payload": {
                "username": "alex_🚀_vip",
                "quantity": 2,
                "coupon_code": "SAVE10",
                "shipping_note": "Handle with care",
                "metadata": {"device": "mobile_app"},
            },
        },
        {
            "persona": "The Unicode Gremlin",
            "attack_name": "Zero-Width Joiner (ZWJ) Injection",
            "hypothesis": "Zero-width joiner (\u200d) characters in shipping_note trigger legacy encoding crash.",
            "payload": {
                "username": "charlie_buyer",
                "quantity": 1,
                "coupon_code": "FREESHIP",
                "shipping_note": "Deliver to \u200d suite 404",
                "metadata": {"client": "web"},
            },
        },
        {
            "persona": "The Boundary Breaker",
            "attack_name": "Zero Quantity Division Underflow",
            "hypothesis": "Setting quantity to 0 causes ZeroDivisionError in per-item shipping allocation.",
            "payload": {
                "username": "zero_shopper",
                "quantity": 0,
                "coupon_code": "SAVE10",
                "shipping_note": "Standard shipping",
                "metadata": {"retry": 0},
            },
        },
        {
            "persona": "The Boundary Breaker",
            "attack_name": "Negative Inventory Reserve Underflow",
            "hypothesis": "Negative quantity bypasses input guards and triggers inventory underflow ValueError.",
            "payload": {
                "username": "negative_buyer",
                "quantity": -5,
                "coupon_code": "SAVE10",
                "shipping_note": "Standard delivery",
                "metadata": {"flag": "exploit"},
            },
        },
        {
            "persona": "The Type-Switcher",
            "attack_name": "Integer Coupon Code Type Confusion",
            "hypothesis": "Sending integer instead of string triggers AttributeError on unsafe .upper() call.",
            "payload": {
                "username": "type_confuser",
                "quantity": 1,
                "coupon_code": 99999,
                "shipping_note": "Express courier",
                "metadata": {"fuzz_type": "int_instead_of_str"},
            },
        },
        {
            "persona": "The JSON Hoarder",
            "attack_name": "Deeply Nested Recursive Metadata Explosion",
            "hypothesis": "Metadata nested > 5 levels triggers unbounded recursion and RecursionError.",
            "payload": {
                "username": "nest_breaker",
                "quantity": 1,
                "coupon_code": "DISCOUNT",
                "shipping_note": "Careful packaging",
                "metadata": {
                    "level1": {
                        "level2": {
                            "level3": {
                                "level4": {
                                    "level5": {
                                        "level6": "depth_limit_exceeded"
                                    }
                                }
                            }
                        }
                    }
                },
            },
        },
    ]


def get_fallback_root_cause(
    attack_info: dict[str, Any],
    status_code: int,
    response_body: str,
) -> dict[str, str]:
    """
    Intelligent heuristic crash analyzer when BharatCode API is offline or times out.
    Inspects response status code, exception names, and stack traces to produce high-fidelity RCA.
    """
    body_lower = response_body.lower()
    attack_name = attack_info.get("attack_name", "")
    persona = attack_info.get("persona", "")

    # 1. ZeroDivisionError
    if "zerodivisionerror" in body_lower or "division by zero" in body_lower:
        return {
            "severity": "HIGH",
            "vulnerability_type": "Divide By Zero (CWE-369)",
            "root_cause": "The backend calculates per-item shipping allocation by dividing by quantity without validating quantity > 0.",
            "fix_diff": "if quantity <= 0:\n    raise HTTPException(status_code=400, detail='Quantity must be positive')\nper_item_shipping = base_shipping / quantity",
        }

    # 2. SQL Injection / OperationalError
    if "operationalerror" in body_lower or "syntax error" in body_lower or "near \"or\"" in body_lower:
        return {
            "severity": "CRITICAL",
            "vulnerability_type": "Improper Neutralization of Special Elements in SQL Command (CWE-89)",
            "root_cause": "Unsanitized user-controlled coupon_code is concatenated directly into raw SQL string.",
            "fix_diff": "# Use parameterized SQL queries instead of raw string concatenation:\ncursor.execute('SELECT * FROM coupons WHERE code = ?', (coupon_code,))",
        }

    # 3. UnicodeEncodeError
    if "unicodeencodeerror" in body_lower or "latin-1" in body_lower or "ordinal not in range" in body_lower:
        return {
            "severity": "MEDIUM",
            "vulnerability_type": "Improper Handling of Unicode / Encoding Mismatch (CWE-172)",
            "root_cause": "Legacy database driver or column encoding crashed when attempting to encode 4-byte UTF-8 emojis or ZWJ characters into latin-1.",
            "fix_diff": "# Configure database connection to utf8mb4 and sanitize strings:\nclean_text = text.encode('utf-8', errors='replace').decode('utf-8')",
        }

    # 4. RecursionError
    if "recursionerror" in body_lower or "maximum recursion depth" in body_lower:
        return {
            "severity": "CRITICAL",
            "vulnerability_type": "Uncontrolled Recursion / Resource Exhaustion (CWE-674)",
            "root_cause": "Recursive parser traversed deeply nested metadata structures without an explicit depth guard, exhausting the call stack.",
            "fix_diff": "def safe_parse(obj, depth=0, max_depth=5):\n    if depth > max_depth:\n        raise HTTPException(status_code=400, detail='Metadata nesting limit exceeded')\n    return {k: safe_parse(v, depth+1) for k, v in obj.items()} if isinstance(obj, dict) else obj",
        }

    # 5. AttributeError / Type Confusion
    if "attributeerror" in body_lower or "object has no attribute 'upper'" in body_lower:
        return {
            "severity": "HIGH",
            "vulnerability_type": "Unhandled Type Confusion (CWE-843)",
            "root_cause": "Endpoint directly invoked string method .upper() on coupon_code without verifying that the payload value is an instance of str.",
            "fix_diff": "if not isinstance(coupon_code, str):\n    raise HTTPException(status_code=400, detail='coupon_code must be a string')\ncoupon_clean = coupon_code.upper()",
        }

    # 6. ValueError / Inventory Underflow
    if "valueerror" in body_lower or "inventory underflow" in body_lower:
        return {
            "severity": "HIGH",
            "vulnerability_type": "Improper Validation of Array / Numeric Index (CWE-1284)",
            "root_cause": "Negative quantity bypassed checkout validation and triggered unhandled inventory underflow exception.",
            "fix_diff": "if quantity < 1:\n    raise HTTPException(status_code=400, detail='Quantity must be at least 1')",
        }

    # Default fallback analysis
    return {
        "severity": "HIGH" if status_code == 500 else "MEDIUM",
        "vulnerability_type": f"Unhandled Server Error ({persona or 'Chaos Trigger'})",
        "root_cause": f"Endpoint returned HTTP {status_code} during '{attack_name}' attack test without graceful exception handling.",
        "fix_diff": "try:\n    # Route business logic\nexcept Exception as e:\n    raise HTTPException(status_code=400, detail=f'Invalid request: {e}')",
    }


async def generate_chaos_payloads(
    schema_dict: dict[str, Any],
    target_url: str,
) -> list[dict[str, Any]]:
    """
    Connects to the BharatCode API (OpenAI-compatible) to synthesize 8 adversarial
    chaos test cases across 5 distinct Chaos Personas based on the endpoint schema.

    Returns a list of dicts with:
        - persona: Name of the persona (e.g., "The Unicode Gremlin")
        - attack_name: Short title of the test (e.g., "4-Byte Emoji Latin-1 Crash")
        - hypothesis: 1-sentence prediction of what might break
        - payload: The actual JSON body to send to the API
    """
    global client
    if client is None:
        client = get_async_openai_client()

    if client is None or not is_api_configured():
        return get_fallback_chaos_payloads()

    system_prompt = (
        "You are an elite Principal Security & Chaos QA Engineer participating in the "
        "BharatCode Build League hackathon. Your mission is to break backend APIs by generating "
        "surgical, adversarial payloads designed to trigger unhandled HTTP 500 crashes and edge cases."
    )

    user_prompt = f"""Target URL Under Test: {target_url}
Endpoint Schema:
{json.dumps(schema_dict, indent=2)}

Generate exactly 8 adversarial test cases across these 5 distinct "Chaos Personas":
a) "The SQL Injector" (SQLi/NoSQLi strings in text fields, comment bypasses, stacked queries)
b) "The Unicode Gremlin" (RTL overrides, Zalgo text, 4-byte UTF-8 emojis, null bytes %00, zero-width joiners)
c) "The Boundary Breaker" (0, -1, INT_MAX, negative inventory, floats in integer fields)
d) "The Type-Switcher" (sending ints/arrays/booleans/null where strings are expected)
e) "The JSON Hoarder" (deeply nested objects > 5 levels or massive strings)

Return STRICTLY a JSON array of 8 objects with no markdown code fences, comments, or conversational text.
Each object MUST have this exact schema:
[
  {{
    "persona": "The Unicode Gremlin",
    "attack_name": "4-Byte Emoji Latin-1 Crash",
    "hypothesis": "Passing 4-byte UTF-8 emojis will crash legacy latin-1 database drivers with UnicodeEncodeError.",
    "payload": {{ ... }}
  }}
]"""

    try:
        response = await client.chat.completions.create(
            model=BHARATCODE_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2500,
        )

        content = response.choices[0].message.content or ""
        parsed = clean_and_parse_json(content)

        if isinstance(parsed, list) and len(parsed) > 0:
            # Validate structure of each generated item
            valid_payloads = []
            for item in parsed:
                if isinstance(item, dict) and "payload" in item and "persona" in item:
                    valid_payloads.append(item)

            if valid_payloads:
                return valid_payloads

        return get_fallback_chaos_payloads()

    except Exception:
        # Graceful fallback to guaranteed chaos suite if LLM call fails
        return get_fallback_chaos_payloads()


async def analyze_crash_root_cause(
    attack_info: dict[str, Any],
    status_code: int,
    response_body: str,
) -> dict[str, str]:
    """
    Analyzes a failed request (HTTP 500 status or leaked traceback) using BharatCode API
    to perform automated Root Cause Analysis (RCA) and generate a code patch.

    Returns a dict with:
        - severity: "CRITICAL" | "HIGH" | "MEDIUM"
        - vulnerability_type: e.g., "Unhandled Type Confusion (CWE-843)"
        - root_cause: 1-sentence technical explanation of why the backend crashed.
        - fix_diff: A concise 2-4 line Python code snippet showing how the developer should patch the bug.
    """
    global client
    if client is None:
        client = get_async_openai_client()

    if client is None or not is_api_configured():
        return get_fallback_root_cause(attack_info, status_code, response_body)

    system_prompt = (
        "You are an expert AppSec & Reliability Engineer. You analyze crashed HTTP responses "
        "and stack traces to produce precise Root Cause Analysis (RCA) and concise Python patches."
    )

    user_prompt = f"""A chaos QA test triggered an unexpected backend failure.
Test Details:
- Persona: {attack_info.get('persona', 'Chaos Fuzzer')}
- Attack Name: {attack_info.get('attack_name', 'Unknown Attack')}
- Attack Hypothesis: {attack_info.get('hypothesis', 'None')}
- Payload Sent: {json.dumps(attack_info.get('payload', {}))}

Target Response:
- HTTP Status Code: {status_code}
- Response Body / Traceback:
{response_body}

Analyze this crash and return STRICTLY a JSON object with no markdown code fences or conversational text:
{{
  "severity": "CRITICAL",
  "vulnerability_type": "Unhandled Type Confusion (CWE-843)",
  "root_cause": "1-sentence technical explanation of why the backend crashed.",
  "fix_diff": "2-4 line Python code snippet demonstrating the defensive fix."
}}"""

    try:
        response = await client.chat.completions.create(
            model=BHARATCODE_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=800,
        )

        content = response.choices[0].message.content or ""
        parsed = clean_and_parse_json(content)

        if isinstance(parsed, dict) and "vulnerability_type" in parsed and "root_cause" in parsed:
            # Normalize severity
            sev = str(parsed.get("severity", "HIGH")).upper()
            if sev not in ("CRITICAL", "HIGH", "MEDIUM"):
                sev = "HIGH"
            parsed["severity"] = sev
            return parsed

        return get_fallback_root_cause(attack_info, status_code, response_body)

    except Exception:
        return get_fallback_root_cause(attack_info, status_code, response_body)


class ChaosLLMClient:
    """
    Object-oriented wrapper around the BharatCode LLM generation & triage functions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or BHARATCODE_API_KEY
        self.base_url = base_url or BHARATCODE_BASE_URL
        self.model = model or BHARATCODE_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key not in (
            "your_bharatcode_api_key_here",
            "your_openai_api_key_here",
            "dummy_key_for_init",
        ))

    async def generate_chaos_payloads(
        self,
        schema: dict[str, Any],
        target_url: str = "http://127.0.0.1:8000/api/v1/checkout",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        return await generate_chaos_payloads(schema, target_url)

    async def analyze_crash(
        self,
        attack_info: dict[str, Any],
        status_code: int,
        response_body: str,
    ) -> dict[str, str]:
        return await analyze_crash_root_cause(attack_info, status_code, response_body)
