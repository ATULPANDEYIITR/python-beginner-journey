from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce
from typing import Callable, Iterable, Any
import json
import logging
import math
import time
import uuid


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    payload: dict[str, Any]
    timestamp: float


@dataclass
class InvocationResult:
    request_id: str
    function_name: str
    success: bool
    result: Any = None
    error: str | None = None
    duration_ms: float = 0.0


class LambdaFunction:
    """
    A small in-process model of a serverless lambda function.

    The function is deliberately stateless between invocations. A separate
    mutable object is used only for metrics, illustrating why operational
    state should not be treated as reliable application state.
    """

    def __init__(
        self,
        name: str,
        handler: Callable[[dict[str, Any]], Any],
        timeout_seconds: float = 2.0,
        memory_mb: int = 128,
    ) -> None:
        if not name or not name.strip():
            raise ValueError("Function name cannot be empty")
        if timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")
        if memory_mb < 128:
            raise ValueError("Memory must be at least 128 MB")

        self.name = name
        self.handler = handler
        self.timeout_seconds = timeout_seconds
        self.memory_mb = memory_mb
        self.invocation_count = 0

    def invoke(self, payload: dict[str, Any]) -> InvocationResult:
        request_id = str(uuid.uuid4())
        started = time.perf_counter()
        self.invocation_count += 1

        try:
            if not isinstance(payload, dict):
                raise TypeError("Lambda payload must be a dictionary")

            result = self.handler(payload)
            duration = (time.perf_counter() - started) * 1000

            if duration > self.timeout_seconds * 1000:
                raise TimeoutError(
                    f"Function exceeded {self.timeout_seconds:.2f}s timeout"
                )

            return InvocationResult(
                request_id=request_id,
                function_name=self.name,
                success=True,
                result=result,
                duration_ms=duration,
            )

        except Exception as exc:
            duration = (time.perf_counter() - started) * 1000
            logging.error("%s failed: %s", self.name, exc)

            return InvocationResult(
                request_id=request_id,
                function_name=self.name,
                success=False,
                error=str(exc),
                duration_ms=duration,
            )


def normalize_order(event: dict[str, Any]) -> dict[str, Any]:
    """
    Pure function: no network, filesystem, clock, or global mutable state.
    This makes the function easy to test and safely retry.
    """
    required = {"order_id", "customer_id", "amount"}
    missing = required - event.keys()

    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")

    amount = event["amount"]
    if not isinstance(amount, (int, float)) or isinstance(amount, bool):
        raise TypeError("amount must be numeric")
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("amount must be finite and greater than zero")

    return {
        "order_id": str(event["order_id"]),
        "customer_id": str(event["customer_id"]),
        "amount": round(float(amount), 2),
        "currency": str(event.get("currency", "INR")).upper(),
        "normalized": True,
    }


def calculate_discount(order: dict[str, Any]) -> dict[str, Any]:
    amount = order["amount"]

    if amount >= 10000:
        rate = 0.15
    elif amount >= 5000:
        rate = 0.10
    elif amount >= 1000:
        rate = 0.05
    else:
        rate = 0.0

    discount = round(amount * rate, 2)

    return {
        **order,
        "discount_rate": rate,
        "discount": discount,
        "payable": round(amount - discount, 2),
    }


def event_router(event: Event, functions: dict[str, LambdaFunction]) -> InvocationResult:
    """
    Event-driven dispatch resembles an event source invoking different
    serverless handlers based on event type.
    """
    function_name = {
        "order.created": "normalize-order",
        "order.validated": "calculate-discount",
    }.get(event.event_type)

    if function_name is None:
        raise ValueError(f"Unsupported event type: {event.event_type}")

    function = functions[function_name]
    return function.invoke(event.payload)


def retry(
    function: LambdaFunction,
    payload: dict[str, Any],
    attempts: int = 3,
    base_delay: float = 0.05,
) -> InvocationResult:
    """
    Exponential backoff is useful for transient failures, but retries can
    duplicate side effects. Production handlers should therefore be
    idempotent when duplicate delivery is possible.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least one")

    last_result: InvocationResult | None = None

    for attempt in range(attempts):
        last_result = function.invoke(payload)

        if last_result.success:
            return last_result

        if attempt < attempts - 1:
            time.sleep(base_delay * (2**attempt))

    assert last_result is not None
    return last_result


def aggregate_amounts(orders: Iterable[dict[str, Any]]) -> float:
    """
    reduce() demonstrates a functional aggregation over immutable-style
    dictionaries. In real systems, database-side aggregation is usually
    preferable for very large datasets.
    """
    return round(
        reduce(lambda total, order: total + order["payable"], orders, 0.0),
        2,
    )


def main() -> None:
    normalize = LambdaFunction(
        "normalize-order",
        normalize_order,
        timeout_seconds=1,
        memory_mb=256,
    )

    discount = LambdaFunction(
        "calculate-discount",
        calculate_discount,
        timeout_seconds=1,
        memory_mb=256,
    )

    functions = {
        normalize.name: normalize,
        discount.name: discount,
    }

    raw_event = Event(
        event_id=str(uuid.uuid4()),
        event_type="order.created",
        payload={
            "order_id": "ORD-1001",
            "customer_id": "CUS-42",
            "amount": 7500,
            "currency": "inr",
        },
        timestamp=time.time(),
    )

    first = event_router(raw_event, functions)

    if not first.success:
        raise RuntimeError(first.error)

    validated_event = Event(
        event_id=str(uuid.uuid4()),
        event_type="order.validated",
        payload=first.result,
        timestamp=time.time(),
    )

    second = event_router(validated_event, functions)

    print("Successful invocation:")
    print(json.dumps(second.result, indent=2))

    invalid_payload = {
        "order_id": "ORD-INVALID",
        "customer_id": "CUS-42",
        "amount": -10,
    }

    failure = retry(normalize, invalid_payload, attempts=2)

    print("\nFailure handling:")
    print(
        json.dumps(
            {
                "success": failure.success,
                "request_id": failure.request_id,
                "error": failure.error,
            },
            indent=2,
        )
    )

    sample_orders = [
        {"payable": 100.0},
        {"payable": 250.0},
        {"payable": 425.50},
    ]

    print(f"\nAggregated payable amount: {aggregate_amounts(sample_orders):.2f}")

    print("\nOperational metrics:")
    print(f"{normalize.name}: {normalize.invocation_count} invocations")
    print(f"{discount.name}: {discount.invocation_count} invocations")


if __name__ == "__main__":
    main()
