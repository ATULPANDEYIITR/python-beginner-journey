"use strict";

/*
 * POLYMORPHISM IN JAVASCRIPT
 *
 * Demonstrates:
 * 1. Dynamic method dispatch
 * 2. Prototype-based polymorphism
 * 3. Duck typing
 * 4. Interface contracts through validation
 * 5. Strategy pattern
 * 6. Event-driven polymorphism
 * 7. Asynchronous execution
 * 8. Promise-based error handling
 * 9. Runtime strategy registration
 * 10. Policy evaluation
 *
 * Runtime: Node.js 18+
 * Dependencies: None
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");
const { performance } = require("node:perf_hooks");


/* =========================================================
   1. PROTOTYPE-BASED POLYMORPHISM
   ========================================================= */

class DataSource {
    constructor(name) {
        if (typeof name !== "string" || !name.trim()) {
            throw new TypeError("Data source name is required.");
        }

        this.name = name;
    }

    async fetch() {
        throw new Error("Subclasses must implement fetch().");
    }
}


class DatabaseSource extends DataSource {
    async fetch() {
        return {
            source: this.name,
            records: 1250,
            type: "database"
        };
    }
}


class APIDataSource extends DataSource {
    async fetch() {
        return {
            source: this.name,
            records: 850,
            type: "api"
        };
    }
}


class FileDataSource extends DataSource {
    async fetch() {
        return {
            source: this.name,
            records: 450,
            type: "file"
        };
    }
}


/*
 * Every object receives the same method call.
 * The concrete class controls the implementation.
 */

async function collectData(sources) {
    if (!Array.isArray(sources)) {
        throw new TypeError("Sources must be an array.");
    }

    const results = [];

    for (const source of sources) {
        if (!source || typeof source.fetch !== "function") {
            throw new TypeError("Invalid data source.");
        }

        results.push(await source.fetch());
    }

    return results;
}


/* =========================================================
   2. DUCK TYPING AND STRUCTURAL CONTRACTS
   ========================================================= */

class JSONFormatter {
    format(data) {
        return JSON.stringify(data, null, 2);
    }
}


class CSVFormatter {
    format(data) {
        if (!Array.isArray(data)) {
            throw new TypeError("CSV input must be an array.");
        }

        if (data.length === 0) {
            return "";
        }

        if (
            data.some(
                row =>
                    row === null ||
                    typeof row !== "object" ||
                    Array.isArray(row)
            )
        ) {
            throw new TypeError("CSV rows must be objects.");
        }

        const columns = [...new Set(
            data.flatMap(row => Object.keys(row))
        )];

        const escape = value => {
            const text = String(value ?? "");

            return `"${text.replaceAll('"', '""')}"`;
        };

        return [
            columns.map(escape).join(","),
            ...data.map(row =>
                columns.map(column => escape(row[column])).join(",")
            )
        ].join("\n");
    }
}


class XMLFormatter {
    format(data) {
        const escape = value =>
            String(value ?? "")
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;")
                .replaceAll('"', "&quot;")
                .replaceAll("'", "&apos;");

        return `<records>${data.map(record => {
            const fields = Object.entries(record)
                .map(([key, value]) =>
                    `<field name="${escape(key)}">${escape(value)}</field>`
                )
                .join("");

            return `<record>${fields}</record>`;
        }).join("")}</records>`;
    }
}


function exportData(formatter, data) {
    if (
        !formatter ||
        typeof formatter.format !== "function"
    ) {
        throw new TypeError("Formatter must implement format().");
    }

    const output = formatter.format(data);

    if (typeof output !== "string") {
        throw new TypeError("Formatter must return a string.");
    }

    return output;
}


/* =========================================================
   3. STRATEGY PATTERN
   ========================================================= */

class DiscountStrategy {
    calculate(amount) {
        throw new Error("calculate() must be implemented.");
    }
}


class RegularDiscount extends DiscountStrategy {
    calculate(amount) {
        return amount * 0.02;
    }
}


class PremiumDiscount extends DiscountStrategy {
    calculate(amount) {
        return amount * 0.10;
    }
}


class EnterpriseDiscount extends DiscountStrategy {
    calculate(amount) {
        return amount * 0.15;
    }
}


class PricingEngine {
    constructor(strategy) {
        this.setStrategy(strategy);
    }

    setStrategy(strategy) {
        if (
            !strategy ||
            typeof strategy.calculate !== "function"
        ) {
            throw new TypeError("Invalid discount strategy.");
        }

        this.strategy = strategy;
    }

    calculateFinalPrice(amount) {
        if (
            typeof amount !== "number" ||
            !Number.isFinite(amount) ||
            amount < 0
        ) {
            throw new RangeError("Invalid purchase amount.");
        }

        const discount = this.strategy.calculate(amount);

        if (
            !Number.isFinite(discount) ||
            discount < 0 ||
            discount > amount
        ) {
            throw new Error("Invalid discount calculation.");
        }

        return {
            original: amount,
            discount,
            payable: amount - discount
        };
    }
}


/* =========================================================
   4. EVENT-DRIVEN POLYMORPHISM
   ========================================================= */

class DeliveryChannel {
    async deliver(recipient, message) {
        throw new Error("deliver() must be implemented.");
    }
}


class EmailDelivery extends DeliveryChannel {
    async deliver(recipient, message) {
        if (
            typeof recipient !== "string" ||
            !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(recipient)
        ) {
            throw new Error("Invalid email address.");
        }

        if (!message.trim()) {
            throw new Error("Empty message.");
        }

        return {
            channel: "email",
            recipient,
            status: "delivered"
        };
    }
}


class SMSDelivery extends DeliveryChannel {
    async deliver(recipient, message) {
        if (!/^\+?[1-9]\d{7,14}$/.test(recipient)) {
            throw new Error("Invalid phone number.");
        }

        if (!message.trim()) {
            throw new Error("Empty message.");
        }

        return {
            channel: "sms",
            recipient,
            status: "delivered"
        };
    }
}


class PushDelivery extends DeliveryChannel {
    async deliver(recipient, message) {
        if (
            typeof recipient !== "string" ||
            !/^[A-Za-z0-9_-]{10,128}$/.test(recipient)
        ) {
            throw new Error("Invalid device token.");
        }

        if (!message.trim()) {
            throw new Error("Empty message.");
        }

        return {
            channel: "push",
            recipient,
            status: "delivered"
        };
    }
}


/*
 * Registry-based dispatch avoids large conditional statements.
 * Only explicitly registered delivery strategies are accepted.
 */

class DeliveryRegistry {
    #channels = new Map();

    register(name, channel) {
        if (
            typeof name !== "string" ||
            !/^[a-z][a-z0-9_-]{0,30}$/.test(name)
        ) {
            throw new TypeError("Invalid channel name.");
        }

        if (
            !channel ||
            typeof channel.deliver !== "function"
        ) {
            throw new TypeError("Channel must implement deliver().");
        }

        if (this.#channels.has(name)) {
            throw new Error(`Channel already registered: ${name}`);
        }

        this.#channels.set(name, channel);
    }

    get(name) {
        const channel = this.#channels.get(name);

        if (!channel) {
            throw new Error(`Unsupported channel: ${name}`);
        }

        return channel;
    }

    names() {
        return [...this.#channels.keys()];
    }
}


class NotificationBus extends EventEmitter {
    constructor(registry) {
        super();

        this.registry = registry;
        this.setMaxListeners(50);
    }

    async publish(event) {
        if (!event || typeof event !== "object") {
            throw new TypeError("Invalid notification event.");
        }

        const {
            channel,
            recipient,
            message
        } = event;

        const handler = this.registry.get(channel);

        const result = await handler.deliver(
            recipient,
            message
        );

        this.emit("notification:completed", result);

        return result;
    }
}


/* =========================================================
   5. POLICY-BASED POLYMORPHISM
   ========================================================= */

class AccessPolicy {
    permits(context) {
        throw new Error("permits() must be implemented.");
    }
}


class AdministratorPolicy extends AccessPolicy {
    permits(context) {
        return context.role === "administrator";
    }
}


class DeveloperPolicy extends AccessPolicy {
    permits(context) {
        return (
            context.role === "developer" &&
            context.environment !== "production"
        );
    }
}


class ReadOnlyPolicy extends AccessPolicy {
    permits(context) {
        return context.operation === "read";
    }
}


class PolicyEngine {
    constructor() {
        this.policies = new Map();
    }

    add(name, policy) {
        if (
            typeof name !== "string" ||
            !policy ||
            typeof policy.permits !== "function"
        ) {
            throw new TypeError("Invalid policy registration.");
        }

        if (this.policies.has(name)) {
            throw new Error("Duplicate policy.");
        }

        this.policies.set(name, policy);
    }

    evaluate(name, context) {
        const policy = this.policies.get(name);

        if (!policy) {
            throw new Error("Unknown policy.");
        }

        const allowed = policy.permits(
            Object.freeze({ ...context })
        );

        return Object.freeze({
            policy: name,
            allowed: Boolean(allowed)
        });
    }
}


/* =========================================================
   6. ASYNCHRONOUS FAILURE HANDLING
   ========================================================= */

async function executeWithRetry(
    operation,
    maximumAttempts = 3
) {
    if (typeof operation !== "function") {
        throw new TypeError("Operation must be callable.");
    }

    if (
        !Number.isInteger(maximumAttempts) ||
        maximumAttempts < 1 ||
        maximumAttempts > 5
    ) {
        throw new RangeError("Invalid retry limit.");
    }

    let lastError;

    for (let attempt = 1; attempt <= maximumAttempts; attempt++) {
        try {
            return await operation();
        } catch (error) {
            lastError = error;

            if (attempt === maximumAttempts) {
                break;
            }

            // Bounded exponential backoff.
            const delay = Math.min(50 * 2 ** (attempt - 1), 500);

            await new Promise(resolve =>
                setTimeout(resolve, delay)
            );
        }
    }

    throw new Error(
        `Operation failed after ${maximumAttempts} attempts.`,
        { cause: lastError }
    );
}


/* =========================================================
   7. EXECUTABLE TEST SCENARIOS
   ========================================================= */

async function main() {
    console.log("\n1. PROTOTYPE POLYMORPHISM");

    const sources = [
        new DatabaseSource("Customer Database"),
        new APIDataSource("Inventory API"),
        new FileDataSource("Sales CSV")
    ];

    const collected = await collectData(sources);

    console.log(collected);

    console.log("\n2. DUCK TYPING");

    const records = [
        { name: "Ananya", department: "Engineering" },
        { name: "Rahul", department: "Security" }
    ];

    console.log(exportData(new JSONFormatter(), records));
    console.log(exportData(new CSVFormatter(), records));
    console.log(exportData(new XMLFormatter(), records));

    console.log("\n3. STRATEGY POLYMORPHISM");

    const pricing = new PricingEngine(new RegularDiscount());

    console.log(pricing.calculateFinalPrice(10000));

    pricing.setStrategy(new PremiumDiscount());

    console.log(pricing.calculateFinalPrice(10000));

    pricing.setStrategy(new EnterpriseDiscount());

    console.log(pricing.calculateFinalPrice(10000));

    console.log("\n4. EVENT-DRIVEN POLYMORPHISM");

    const registry = new DeliveryRegistry();

    registry.register("email", new EmailDelivery());
    registry.register("sms", new SMSDelivery());
    registry.register("push", new PushDelivery());

    const bus = new NotificationBus(registry);

    bus.on("notification:completed", result => {
        console.log("Event received:", result);
    });

    await bus.publish({
        channel: "email",
        recipient: "operations@example.com",
        message: "System operational."
    });

    await bus.publish({
        channel: "sms",
        recipient: "+919876543210",
        message: "System operational."
    });

    await bus.publish({
        channel: "push",
        recipient: "DeviceToken_123456",
        message: "Service notification."
    });

    console.log("\n5. POLICY POLYMORPHISM");

    const policyEngine = new PolicyEngine();

    policyEngine.add(
        "admin",
        new AdministratorPolicy()
    );

    policyEngine.add(
        "developer",
        new DeveloperPolicy()
    );

    policyEngine.add(
        "read-only",
        new ReadOnlyPolicy()
    );

    console.log(
        policyEngine.evaluate("admin", {
            role: "administrator",
            operation: "write",
            environment: "production"
        })
    );

    console.log(
        policyEngine.evaluate("developer", {
            role: "developer",
            operation: "write",
            environment: "production"
        })
    );

    console.log("\n6. RETRY HANDLING");

    let attempts = 0;

    const result = await executeWithRetry(async () => {
        attempts++;

        if (attempts < 3) {
            throw new Error("Temporary failure.");
        }

        return "Operation completed.";
    });

    console.log(result, "Attempts:", attempts);

    console.log("\n7. EDGE CASE TESTING");

    assert.equal(
        pricing.calculateFinalPrice(1000).payable,
        850
    );

    assert.equal(
        policyEngine.evaluate("admin", {
            role: "administrator"
        }).allowed,
        true
    );

    assert.equal(
        policyEngine.evaluate("developer", {
            role: "developer",
            environment: "production"
        }).allowed,
        false
    );

    assert.throws(
        () => exportData({}, records),
        TypeError
    );

    assert.throws(
        () => pricing.calculateFinalPrice(-100),
        RangeError
    );

    assert.throws(
        () => registry.register("email", new EmailDelivery()),
        /already registered/
    );

    await assert.rejects(
        bus.publish({
            channel: "email",
            recipient: "invalid-address",
            message: "Test"
        }),
        /Invalid email/
    );

    await assert.rejects(
        bus.publish({
            channel: "unknown",
            recipient: "test@example.com",
            message: "Test"
        }),
        /Unsupported channel/
    );

    console.log("All validation tests passed.");

    console.log("\n8. DISPATCH PERFORMANCE");

    const benchmark = new PricingEngine(
        new RegularDiscount()
    );

    const start = performance.now();

    let total = 0;

    for (let i = 0; i < 100000; i++) {
        total += benchmark.calculateFinalPrice(1000).payable;
    }

    const elapsed = performance.now() - start;

    console.log({
        iterations: 100000,
        total,
        elapsedMilliseconds: elapsed.toFixed(3)
    });

    console.log("\nExecution completed successfully.");
}


main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
