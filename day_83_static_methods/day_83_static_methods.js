"use strict";

/*
 * STATIC METHODS IN JAVASCRIPT
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only.
 *
 * Engineering coverage:
 * - Static methods and static inheritance.
 * - Static fields and class-level state.
 * - Private static methods.
 * - Static factory methods.
 * - Promise-based asynchronous static operations.
 * - Event-driven transaction processing.
 * - Policy evaluation.
 * - Caching.
 * - Cryptographic hashing.
 * - Error handling and automated assertions.
 */

const crypto = require("node:crypto");
const fs = require("node:fs/promises");
const assert = require("node:assert/strict");
const EventEmitter = require("node:events");

// ============================================================
// 1. BASIC STATIC OPERATIONS
// ============================================================

class MathService {
    static add(a, b) {
        MathService.#validateNumbers(a, b);
        return a + b;
    }

    static subtract(a, b) {
        MathService.#validateNumbers(a, b);
        return a - b;
    }

    static multiply(a, b) {
        MathService.#validateNumbers(a, b);
        return a * b;
    }

    static divide(a, b) {
        MathService.#validateNumbers(a, b);

        if (b === 0) {
            throw new RangeError("Division by zero.");
        }

        return a / b;
    }

    static #validateNumbers(a, b) {
        if (
            typeof a !== "number" ||
            typeof b !== "number" ||
            !Number.isFinite(a) ||
            !Number.isFinite(b)
        ) {
            throw new TypeError("Arguments must be finite numbers.");
        }
    }
}

// ============================================================
// 2. STATIC METHODS AND CLASS INHERITANCE
// ============================================================

class NotificationService {
    static provider = "Generic";

    static send(message) {
        if (typeof message !== "string" || !message.trim()) {
            throw new TypeError("Message cannot be empty.");
        }

        return `${this.provider}: ${message}`;
    }
}

class EmailNotification extends NotificationService {
    static provider = "Email";
}

class SMSNotification extends NotificationService {
    static provider = "SMS";
}

// ============================================================
// 3. STATIC FACTORY METHODS
// ============================================================

class Account {
    constructor(id, owner, balance) {
        if (!Number.isSafeInteger(id) || id <= 0) {
            throw new RangeError("Invalid account ID.");
        }

        if (typeof owner !== "string" || !owner.trim()) {
            throw new TypeError("Account owner is required.");
        }

        if (
            typeof balance !== "number" ||
            !Number.isFinite(balance) ||
            balance < 0
        ) {
            throw new RangeError("Invalid account balance.");
        }

        this.id = id;
        this.owner = owner.trim();
        this.balance = balance;
    }

    static fromJSON(payload) {
        let data;

        try {
            data = JSON.parse(payload);
        } catch {
            throw new TypeError("Malformed account JSON.");
        }

        if (!data || typeof data !== "object" || Array.isArray(data)) {
            throw new TypeError("Account JSON must be an object.");
        }

        return new Account(data.id, data.owner, data.balance);
    }
}

// ============================================================
// 4. STATIC VALIDATION AND POLICY EVALUATION
// ============================================================

class ValidationService {
    static emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    static validateEmail(email) {
        return (
            typeof email === "string" &&
            this.emailPattern.test(email)
        );
    }

    static validatePort(port) {
        return (
            Number.isInteger(port) &&
            port >= 1 &&
            port <= 65535
        );
    }

    static validateTransaction(amount) {
        return (
            typeof amount === "number" &&
            Number.isFinite(amount) &&
            amount > 0
        );
    }
}

class AuthorizationService {
    static permissions = new Map([
        ["reader", new Set(["read"])],
        ["analyst", new Set(["read", "analyze"])],
        ["administrator", new Set(["read", "analyze", "write", "delete"])]
    ]);

    static evaluate({ role, operation, resource }) {
        if (
            typeof role !== "string" ||
            typeof operation !== "string" ||
            typeof resource !== "string" ||
            !role.trim() ||
            !operation.trim() ||
            !resource.trim()
        ) {
            return {
                allowed: false,
                reason: "Invalid authorization request"
            };
        }

        const permissions = this.permissions.get(role.toLowerCase());

        if (!permissions || !permissions.has(operation.toLowerCase())) {
            return {
                allowed: false,
                reason: "Permission denied"
            };
        }

        return {
            allowed: true,
            reason: "Permission granted"
        };
    }
}

// ============================================================
// 5. PRIVATE STATIC METHODS AND CACHING
// ============================================================

class PricingEngine {
    static #cache = new Map();
    static #maximumCacheSize = 500;

    static calculatePrice(basePrice, taxRate, discountRate = 0) {
        if (
            !Number.isFinite(basePrice) ||
            !Number.isFinite(taxRate) ||
            !Number.isFinite(discountRate) ||
            basePrice < 0 ||
            taxRate < 0 ||
            discountRate < 0 ||
            discountRate > 1
        ) {
            throw new RangeError("Invalid pricing parameters.");
        }

        const key = `${basePrice}:${taxRate}:${discountRate}`;

        if (this.#cache.has(key)) {
            return this.#cache.get(key);
        }

        const discounted = basePrice * (1 - discountRate);
        const finalPrice = discounted * (1 + taxRate);

        if (this.#cache.size >= this.#maximumCacheSize) {
            const oldestKey = this.#cache.keys().next().value;
            this.#cache.delete(oldestKey);
        }

        this.#cache.set(key, finalPrice);

        return finalPrice;
    }

    static cacheStatistics() {
        return {
            entries: this.#cache.size,
            capacity: this.#maximumCacheSize
        };
    }
}

// ============================================================
// 6. ASYNCHRONOUS STATIC METHODS
// ============================================================

class FileService {
    static async readJSON(filePath) {
        if (typeof filePath !== "string" || !filePath.trim()) {
            throw new TypeError("A file path is required.");
        }

        const content = await fs.readFile(filePath, "utf8");

        try {
            return JSON.parse(content);
        } catch {
            throw new SyntaxError("File contains invalid JSON.");
        }
    }

    static async calculateSHA256(filePath) {
        const hash = crypto.createHash("sha256");
        const content = await fs.readFile(filePath);

        hash.update(content);

        return hash.digest("hex");
    }
}

// ============================================================
// 7. EVENT-DRIVEN TRANSACTION PROCESSING
// ============================================================

class TransactionProcessor extends EventEmitter {
    #balance;
    #processedTransactions = new Set();

    constructor(initialBalance) {
        super();

        if (
            typeof initialBalance !== "number" ||
            !Number.isFinite(initialBalance) ||
            initialBalance < 0
        ) {
            throw new RangeError("Invalid initial balance.");
        }

        this.#balance = initialBalance;
    }

    get balance() {
        return this.#balance;
    }

    async process(transaction) {
        const { id, type, amount } = transaction ?? {};

        if (
            typeof id !== "string" ||
            !id.trim() ||
            !["CREDIT", "DEBIT"].includes(type) ||
            !ValidationService.validateTransaction(amount)
        ) {
            this.emit("rejected", {
                reason: "Invalid transaction"
            });

            throw new TypeError("Transaction validation failed.");
        }

        if (this.#processedTransactions.has(id)) {
            throw new Error("Duplicate transaction ID.");
        }

        if (type === "DEBIT" && amount > this.#balance) {
            this.emit("rejected", {
                id,
                reason: "Insufficient balance"
            });

            throw new Error("Insufficient balance.");
        }

        // The mutation occurs only after all checks succeed.
        const previousBalance = this.#balance;

        this.#balance += type === "CREDIT" ? amount : -amount;
        this.#processedTransactions.add(id);

        const result = Object.freeze({
            id,
            type,
            amount,
            previousBalance,
            currentBalance: this.#balance,
            timestamp: new Date().toISOString()
        });

        this.emit("processed", result);

        return result;
    }
}

// ============================================================
// 8. STATIC METHODS FOR COLLECTION PROCESSING
// ============================================================

class AnalyticsService {
    static summarize(values) {
        if (!Array.isArray(values) || values.length === 0) {
            throw new TypeError("A non-empty array is required.");
        }

        if (!values.every(Number.isFinite)) {
            throw new TypeError("All values must be finite numbers.");
        }

        const sorted = [...values].sort((a, b) => a - b);

        const sum = values.reduce((total, value) => total + value, 0);

        const middle = Math.floor(sorted.length / 2);

        const median = sorted.length % 2 === 0
            ? (sorted[middle - 1] + sorted[middle]) / 2
            : sorted[middle];

        return Object.freeze({
            count: values.length,
            sum,
            average: sum / values.length,
            median,
            minimum: sorted[0],
            maximum: sorted[sorted.length - 1]
        });
    }

    static groupByCategory(records) {
        if (!Array.isArray(records)) {
            throw new TypeError("Records must be an array.");
        }

        const groups = new Map();

        for (const record of records) {
            if (
                !record ||
                typeof record.category !== "string" ||
                !record.category.trim()
            ) {
                throw new TypeError("Each record requires a category.");
            }

            if (!groups.has(record.category)) {
                groups.set(record.category, []);
            }

            groups.get(record.category).push(record);
        }

        return groups;
    }
}

// ============================================================
// 9. STATIC METHODS FOR CONFIGURATION
// ============================================================

class ConfigurationService {
    static validate(configuration) {
        const errors = [];

        if (!configuration || typeof configuration !== "object" ||
            Array.isArray(configuration)) {
            return {
                valid: false,
                errors: ["Configuration must be an object."]
            };
        }

        const required = ["application", "environment", "port"];

        for (const field of required) {
            if (!(field in configuration)) {
                errors.push(`Missing configuration field: ${field}`);
            }
        }

        if (
            "application" in configuration &&
            (
                typeof configuration.application !== "string" ||
                !configuration.application.trim()
            )
        ) {
            errors.push("Application name must be non-empty.");
        }

        if (
            "environment" in configuration &&
            !["development", "testing", "production"].includes(
                configuration.environment
            )
        ) {
            errors.push("Invalid environment.");
        }

        if (
            "port" in configuration &&
            !ValidationService.validatePort(configuration.port)
        ) {
            errors.push("Invalid network port.");
        }

        return Object.freeze({
            valid: errors.length === 0,
            errors: Object.freeze(errors)
        });
    }
}

// ============================================================
// 10. TEST SUITE
// ============================================================

async function runTests() {
    assert.equal(MathService.add(10, 20), 30);
    assert.equal(MathService.divide(100, 5), 20);

    assert.throws(
        () => MathService.divide(10, 0),
        RangeError
    );

    assert.equal(
        EmailNotification.send("Deployment complete"),
        "Email: Deployment complete"
    );

    assert.equal(
        SMSNotification.send("Alert"),
        "SMS: Alert"
    );

    const account = Account.fromJSON(
        '{"id":1,"owner":"Aarav","balance":5000}'
    );

    assert.equal(account.balance, 5000);

    assert.equal(
        ValidationService.validateEmail("admin@example.com"),
        true
    );

    assert.equal(
        ValidationService.validatePort(8080),
        true
    );

    assert.deepEqual(
        AuthorizationService.evaluate({
            role: "reader",
            operation: "delete",
            resource: "repository"
        }),
        {
            allowed: false,
            reason: "Permission denied"
        }
    );

    const price = PricingEngine.calculatePrice(1000, 0.18, 0.10);
    assert.equal(price, 1062);

    const processor = new TransactionProcessor(10000);

    let processedEvents = 0;

    processor.on("processed", () => {
        processedEvents++;
    });

    await processor.process({
        id: "TX-001",
        type: "CREDIT",
        amount: 500
    });

    assert.equal(processor.balance, 10500);
    assert.equal(processedEvents, 1);

    await assert.rejects(
        () => processor.process({
            id: "TX-001",
            type: "CREDIT",
            amount: 500
        }),
        /Duplicate/
    );

    assert.equal(
        processor.balance,
        10500,
        "Rejected transactions must not mutate state."
    );

    const statistics = AnalyticsService.summarize([10, 20, 30, 40]);

    assert.equal(statistics.average, 25);
    assert.equal(statistics.median, 25);

    const configuration = ConfigurationService.validate({
        application: "RepositoryService",
        environment: "production",
        port: 8080
    });

    assert.equal(configuration.valid, true);

    console.log("All JavaScript static method tests passed.");
}

// ============================================================
// 11. APPLICATION ENTRY POINT
// ============================================================

async function main() {
    console.log("STATIC METHODS: JAVASCRIPT IMPLEMENTATION");
    console.log("==========================================");

    console.log("\nMathematical operations:");
    console.log("Addition:", MathService.add(15, 25));
    console.log("Multiplication:", MathService.multiply(12, 8));

    console.log("\nInheritance:");
    console.log(NotificationService.send("System notification"));
    console.log(EmailNotification.send("Build successful"));

    console.log("\nFactory method:");
    const account = Account.fromJSON(
        '{"id":100,"owner":"Research Team","balance":25000}'
    );

    console.log(account);

    console.log("\nPricing:");
    console.log(PricingEngine.calculatePrice(50000, 0.18, 0.05));
    console.log(PricingEngine.cacheStatistics());

    console.log("\nAsynchronous transaction:");
    const processor = new TransactionProcessor(100000);

    processor.on("processed", event => {
        console.log("Transaction event:", event);
    });

    await processor.process({
        id: "TX-1001",
        type: "DEBIT",
        amount: 15000
    });

    console.log("\nAnalytics:");
    console.log(AnalyticsService.summarize([20, 40, 60, 80]));

    await runTests();
}

main().catch(error => {
    console.error("Application failed:", error.message);
    process.exitCode = 1;
});
