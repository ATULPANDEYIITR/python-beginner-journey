"use strict";

/*
 * Lambda Functions
 *
 * This Node.js program models serverless functions as small, independently
 * invocable handlers. It focuses on event-driven execution, validation,
 * asynchronous processing, retries, idempotency, and concurrency.
 */

const crypto = require("node:crypto");

class LambdaFunction {
  constructor(name, handler, { timeoutMs = 2000, memoryMb = 128 } = {}) {
    if (!name || typeof name !== "string") {
      throw new TypeError("Function name must be a non-empty string");
    }
    if (typeof handler !== "function") {
      throw new TypeError("Handler must be callable");
    }
    if (timeoutMs <= 0) {
      throw new RangeError("Timeout must be positive");
    }
    if (memoryMb < 128) {
      throw new RangeError("Memory must be at least 128 MB");
    }

    this.name = name;
    this.handler = handler;
    this.timeoutMs = timeoutMs;
    this.memoryMb = memoryMb;
    this.invocations = 0;
  }

  async invoke(event) {
    const requestId = crypto.randomUUID();
    const started = performance.now();
    this.invocations += 1;

    if (!event || typeof event !== "object" || Array.isArray(event)) {
      return {
        requestId,
        functionName: this.name,
        success: false,
        error: "Event must be an object",
      };
    }

    try {
      const result = await Promise.race([
        Promise.resolve(this.handler(event, { requestId })),
        new Promise((_, reject) =>
          setTimeout(
            () => reject(new Error("Function timeout")),
            this.timeoutMs
          )
        ),
      ]);

      return {
        requestId,
        functionName: this.name,
        success: true,
        result,
        durationMs: Number((performance.now() - started).toFixed(2)),
      };
    } catch (error) {
      return {
        requestId,
        functionName: this.name,
        success: false,
        error: error instanceof Error ? error.message : String(error),
        durationMs: Number((performance.now() - started).toFixed(2)),
      };
    }
  }
}

function validateOrder(event) {
  for (const field of ["orderId", "customerId", "amount"]) {
    if (!(field in event)) {
      throw new Error(`Missing field: ${field}`);
    }
  }

  if (
    typeof event.amount !== "number" ||
    !Number.isFinite(event.amount) ||
    event.amount <= 0
  ) {
    throw new Error("amount must be a positive finite number");
  }

  return {
    orderId: String(event.orderId),
    customerId: String(event.customerId),
    amount: Number(event.amount.toFixed(2)),
    currency: String(event.currency ?? "INR").toUpperCase(),
  };
}

async function enrichOrder(event, context) {
  const order = validateOrder(event);

  /*
   * This asynchronous boundary represents work that might normally call
   * another service, database, or API. The example stays dependency-free.
   */
  await Promise.resolve();

  return {
    ...order,
    requestId: context.requestId,
    validatedAt: new Date().toISOString(),
  };
}

function calculatePricing(event) {
  const rate =
    event.amount >= 10000
      ? 0.15
      : event.amount >= 5000
        ? 0.10
        : event.amount >= 1000
          ? 0.05
          : 0;

  const discount = Number((event.amount * rate).toFixed(2));

  return {
    ...event,
    discountRate: rate,
    discount,
    payable: Number((event.amount - discount).toFixed(2)),
  };
}

class EventBus {
  constructor() {
    this.routes = new Map();
  }

  register(eventType, lambdaFunction) {
    if (this.routes.has(eventType)) {
      throw new Error(`Route already exists: ${eventType}`);
    }
    this.routes.set(eventType, lambdaFunction);
  }

  async publish(eventType, payload) {
    const target = this.routes.get(eventType);

    if (!target) {
      throw new Error(`No handler registered for ${eventType}`);
    }

    return target.invoke(payload);
  }
}

async function invokeWithRetry(lambdaFunction, event, attempts = 3) {
  if (!Number.isInteger(attempts) || attempts < 1) {
    throw new RangeError("attempts must be a positive integer");
  }

  let lastResult;

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    lastResult = await lambdaFunction.invoke(event);

    if (lastResult.success) {
      return lastResult;
    }

    if (attempt < attempts) {
      await new Promise((resolve) =>
        setTimeout(resolve, 25 * 2 ** (attempt - 1))
      );
    }
  }

  return lastResult;
}

function createIdempotentHandler(handler) {
  const processedKeys = new Set();

  return async (event, context) => {
    const key = event.idempotencyKey;

    if (!key || typeof key !== "string") {
      throw new Error("idempotencyKey is required");
    }

    if (processedKeys.has(key)) {
      return {
        duplicate: true,
        message: "Previously processed event",
      };
    }

    const result = await handler(event, context);
    processedKeys.add(key);

    return {
      duplicate: false,
      result,
    };
  };
}

async function main() {
  const normalizeOrder = new LambdaFunction(
    "normalize-order",
    enrichOrder,
    { timeoutMs: 1000, memoryMb: 256 }
  );

  const pricing = new LambdaFunction(
    "calculate-pricing",
    calculatePricing,
    { timeoutMs: 1000, memoryMb: 256 }
  );

  const eventBus = new EventBus();

  eventBus.register("order.created", normalizeOrder);
  eventBus.register("order.validated", pricing);

  const created = await eventBus.publish("order.created", {
    orderId: "ORD-1001",
    customerId: "CUS-42",
    amount: 7500,
    currency: "INR",
  });

  if (!created.success) {
    throw new Error(created.error);
  }

  const priced = await eventBus.publish("order.validated", created.result);

  console.log("Successful event-driven invocation:");
  console.log(JSON.stringify(priced, null, 2));

  const idempotentProcessor = new LambdaFunction(
    "payment-event",
    createIdempotentHandler(async (event) => ({
      paymentId: event.paymentId,
      amount: event.amount,
      accepted: true,
    }))
  );

  const paymentEvent = {
    idempotencyKey: "PAYMENT-EVENT-1",
    paymentId: "PAY-7001",
    amount: 499.99,
  };

  const firstPayment = await idempotentProcessor.invoke(paymentEvent);
  const duplicatePayment = await idempotentProcessor.invoke(paymentEvent);

  console.log("\nIdempotency:");
  console.log(JSON.stringify(firstPayment.result, null, 2));
  console.log(JSON.stringify(duplicatePayment.result, null, 2));

  const failed = await invokeWithRetry(normalizeOrder, {
    orderId: "BAD-1",
    customerId: "CUS-1",
    amount: -100,
  });

  console.log("\nValidation failure:");
  console.log(JSON.stringify(failed, null, 2));

  const concurrentOrders = [
    { orderId: "ORD-1", customerId: "C1", amount: 1000 },
    { orderId: "ORD-2", customerId: "C2", amount: 5000 },
    { orderId: "ORD-3", customerId: "C3", amount: 12000 },
  ];

  const concurrentResults = await Promise.all(
    concurrentOrders.map((order) => normalizeOrder.invoke(order))
  );

  console.log("\nConcurrent invocations:");
  console.log(JSON.stringify(concurrentResults, null, 2));

  console.log("\nInvocation metrics:");
  console.log({
    normalizeOrder: normalizeOrder.invocations,
    pricing: pricing.invocations,
    paymentProcessor: idempotentProcessor.invocations,
  });
}

main().catch((error) => {
  console.error("Fatal error:", error.message);
  process.exitCode = 1;
});
