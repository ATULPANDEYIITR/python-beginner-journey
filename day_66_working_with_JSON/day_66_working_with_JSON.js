"use strict";

/*
 * Working with JSON
 *
 * Demonstrates:
 * - Serialization and parsing
 * - Nested JSON navigation
 * - Schema validation
 * - JSON transformations
 * - Asynchronous file operations
 * - Event-driven processing
 * - API response handling
 * - Safe output filtering
 *
 * Runtime: Node.js 18+
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const os = require("node:os");
const EventEmitter = require("node:events");

const MAX_FILE_SIZE = 2 * 1024 * 1024;
const MAX_DEPTH = 30;

class JSONProcessingError extends Error {
    constructor(message) {
        super(message);
        this.name = "JSONProcessingError";
    }
}

class JSONValidator {
    static validateDepth(value, depth = 0) {
        if (depth > MAX_DEPTH) {
            throw new JSONProcessingError(
                "Maximum JSON nesting depth exceeded"
            );
        }

        if (value === null || typeof value !== "object") {
            return;
        }

        if (Array.isArray(value)) {
            for (const item of value) {
                this.validateDepth(item, depth + 1);
            }
            return;
        }

        for (const [key, item] of Object.entries(value)) {
            if (typeof key !== "string") {
                throw new JSONProcessingError("Invalid object key");
            }

            this.validateDepth(item, depth + 1);
        }
    }

    static validateCustomer(customer) {
        if (
            customer === null ||
            typeof customer !== "object" ||
            Array.isArray(customer)
        ) {
            throw new JSONProcessingError(
                "Customer must be a JSON object"
            );
        }

        const required = [
            "customerId",
            "name",
            "email",
            "status",
            "balance"
        ];

        for (const field of required) {
            if (!Object.hasOwn(customer, field)) {
                throw new JSONProcessingError(
                    `Missing field: ${field}`
                );
            }
        }

        if (
            !Number.isSafeInteger(customer.customerId) ||
            customer.customerId <= 0
        ) {
            throw new JSONProcessingError(
                "Invalid customer ID"
            );
        }

        if (
            typeof customer.name !== "string" ||
            !customer.name.trim()
        ) {
            throw new JSONProcessingError(
                "Invalid customer name"
            );
        }

        if (
            typeof customer.email !== "string" ||
            !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customer.email)
        ) {
            throw new JSONProcessingError(
                "Invalid email address"
            );
        }

        if (!["active", "inactive", "pending"].includes(customer.status)) {
            throw new JSONProcessingError(
                "Invalid customer status"
            );
        }

        if (
            typeof customer.balance !== "number" ||
            !Number.isFinite(customer.balance) ||
            customer.balance < 0
        ) {
            throw new JSONProcessingError(
                "Invalid customer balance"
            );
        }

        return true;
    }
}

class JSONCodec {
    static stringify(value, pretty = true) {
        JSONValidator.validateDepth(value);

        const result = JSON.stringify(
            value,
            null,
            pretty ? 4 : 0
        );

        if (result === undefined) {
            throw new JSONProcessingError(
                "Value cannot be represented as JSON"
            );
        }

        return result;
    }

    static parse(content) {
        if (typeof content !== "string") {
            throw new TypeError("JSON content must be a string");
        }

        const result = JSON.parse(content);

        JSONValidator.validateDepth(result);

        return result;
    }

    static canonicalize(value) {
        if (Array.isArray(value)) {
            return value.map(item => this.canonicalize(item));
        }

        if (value !== null && typeof value === "object") {
            return Object.fromEntries(
                Object.keys(value)
                    .sort()
                    .map(key => [
                        key,
                        this.canonicalize(value[key])
                    ])
            );
        }

        return value;
    }
}

class JSONPath {
    static get(data, pathExpression) {
        const segments = pathExpression.split(".");
        let current = data;

        for (const segment of segments) {
            if (Array.isArray(current)) {
                const index = Number(segment);

                if (
                    !Number.isInteger(index) ||
                    index < 0 ||
                    index >= current.length
                ) {
                    throw new JSONProcessingError(
                        `Invalid array index: ${segment}`
                    );
                }

                current = current[index];
            } else if (
                current !== null &&
                typeof current === "object" &&
                Object.hasOwn(current, segment)
            ) {
                current = current[segment];
            } else {
                throw new JSONProcessingError(
                    `Property not found: ${segment}`
                );
            }
        }

        return current;
    }
}

class OrderService {
    constructor() {
        this.orders = new Map();
    }

    add(order) {
        if (
            !Number.isSafeInteger(order.orderId) ||
            order.orderId <= 0
        ) {
            throw new JSONProcessingError("Invalid order ID");
        }

        if (this.orders.has(order.orderId)) {
            throw new JSONProcessingError("Duplicate order ID");
        }

        if (!Array.isArray(order.items)) {
            throw new JSONProcessingError(
                "Order items must be an array"
            );
        }

        const normalizedItems = order.items.map(item => {
            if (
                typeof item.price !== "number" ||
                !Number.isFinite(item.price) ||
                item.price < 0 ||
                !Number.isSafeInteger(item.quantity) ||
                item.quantity <= 0
            ) {
                throw new JSONProcessingError(
                    "Invalid order item"
                );
            }

            return {
                product: String(item.product),
                price: item.price,
                quantity: item.quantity
            };
        });

        const normalized = Object.freeze({
            orderId: order.orderId,
            customerId: order.customerId,
            status: order.status,
            items: Object.freeze(normalizedItems)
        });

        this.orders.set(order.orderId, normalized);

        return normalized;
    }

    total(orderId) {
        const order = this.orders.get(orderId);

        if (!order) {
            throw new JSONProcessingError("Order not found");
        }

        return order.items.reduce(
            (sum, item) => sum + item.price * item.quantity,
            0
        );
    }

    export() {
        return [...this.orders.values()];
    }
}

class JSONFileRepository {
    constructor(filePath) {
        this.filePath = filePath;
    }

    async save(data) {
        const content = JSONCodec.stringify(data);

        if (Buffer.byteLength(content, "utf8") > MAX_FILE_SIZE) {
            throw new JSONProcessingError(
                "JSON document exceeds size limit"
            );
        }

        const temporaryPath = `${this.filePath}.tmp`;

        try {
            await fs.writeFile(
                temporaryPath,
                content,
                {
                    encoding: "utf8",
                    flag: "wx"
                }
            );

            await fs.rename(temporaryPath, this.filePath);
        } catch (error) {
            await fs.rm(temporaryPath, { force: true });
            throw error;
        }
    }

    async load() {
        const stats = await fs.stat(this.filePath);

        if (!stats.isFile() || stats.size > MAX_FILE_SIZE) {
            throw new JSONProcessingError(
                "Invalid JSON file or excessive file size"
            );
        }

        const content = await fs.readFile(
            this.filePath,
            "utf8"
        );

        return JSONCodec.parse(content);
    }
}

class OrderEventProcessor extends EventEmitter {
    constructor(service) {
        super();
        this.service = service;

        this.on("order.created", order => {
            const stored = this.service.add(order);

            console.log(
                `Event processed: order ${stored.orderId}`
            );
        });
    }

    publish(order) {
        this.emit("order.created", order);
    }
}

function removeSensitiveFields(value) {
    const sensitive = new Set([
        "password",
        "token",
        "secret",
        "access_token",
        "api_key"
    ]);

    if (Array.isArray(value)) {
        return value.map(removeSensitiveFields);
    }

    if (value === null || typeof value !== "object") {
        return value;
    }

    const result = {};

    for (const [key, item] of Object.entries(value)) {
        if (!sensitive.has(key.toLowerCase())) {
            result[key] = removeSensitiveFields(item);
        }
    }

    return result;
}

async function processAPIResponse(response) {
    if (!response.ok) {
        throw new JSONProcessingError(
            `API request failed: HTTP ${response.status}`
        );
    }

    const contentType = response.headers.get("content-type") || "";

    if (!contentType.toLowerCase().includes("application/json")) {
        throw new JSONProcessingError(
            "Unexpected API response content type"
        );
    }

    const text = await response.text();

    if (Buffer.byteLength(text, "utf8") > MAX_FILE_SIZE) {
        throw new JSONProcessingError(
            "API response exceeds size limit"
        );
    }

    return JSONCodec.parse(text);
}

async function main() {
    console.log("\n=== JSON Serialization ===");

    const customer = {
        customerId: 101,
        name: "Atul Pandey",
        email: "atul@example.com",
        status: "active",
        balance: 12500.50
    };

    JSONValidator.validateCustomer(customer);

    const customerJSON = JSONCodec.stringify(customer);

    console.log(customerJSON);

    console.log("\n=== JSON Deserialization ===");

    const parsedCustomer = JSONCodec.parse(customerJSON);

    console.log("Customer:", parsedCustomer.name);

    console.log("\n=== Nested JSON Navigation ===");

    const order = {
        orderId: 5001,
        customer: {
            address: {
                city: "Lucknow",
                country: "India"
            }
        },
        items: [
            { product: "Laptop", price: 65000, quantity: 1 },
            { product: "Mouse", price: 800, quantity: 2 }
        ]
    };

    console.log(
        "City:",
        JSONPath.get(order, "customer.address.city")
    );

    console.log("\n=== Order Processing ===");

    const service = new OrderService();

    const processor = new OrderEventProcessor(service);

    processor.publish({
        orderId: 5001,
        customerId: 101,
        status: "completed",
        items: order.items
    });

    console.log("Total:", service.total(5001));

    console.log("\n=== JSON Array Transformation ===");

    const reports = [
        { department: "IT", revenue: 50000 },
        { department: "Finance", revenue: 35000 },
        { department: "Operations", revenue: 25000 }
    ];

    const totalRevenue = reports.reduce(
        (sum, item) => sum + item.revenue,
        0
    );

    const revenueReport = {
        generatedAt: new Date().toISOString(),
        totalRevenue,
        departments: reports
    };

    console.log(JSONCodec.stringify(revenueReport));

    console.log("\n=== Sensitive Data Filtering ===");

    const apiPayload = {
        user: "atul",
        access_token: "secret",
        profile: {
            email: "atul@example.com",
            password: "hidden",
            department: "Engineering"
        }
    };

    console.log(
        JSONCodec.stringify(
            removeSensitiveFields(apiPayload)
        )
    );

    console.log("\n=== Asynchronous File Handling ===");

    const directory = await fs.mkdtemp(
        path.join(os.tmpdir(), "json-workflow-")
    );

    try {
        const repository = new JSONFileRepository(
            path.join(directory, "orders.json")
        );

        await repository.save(service.export());

        const loaded = await repository.load();

        console.log("Loaded records:", loaded.length);
    } finally {
        await fs.rm(directory, {
            recursive: true,
            force: true
        });
    }

    console.log("\n=== Canonical JSON Hash ===");

    const canonical = JSONCodec.stringify(
        JSONCodec.canonicalize(customer),
        false
    );

    const checksum = crypto
        .createHash("sha256")
        .update(canonical)
        .digest("hex");

    console.log(checksum);

    console.log("\n=== Error Handling ===");

    const invalidDocuments = [
        '{"name": "Atul",}',
        '{"balance": NaN}',
        '{"name": "Atul"'
    ];

    for (const document of invalidDocuments) {
        try {
            JSONCodec.parse(document);
        } catch (error) {
            console.log("Rejected:", error.message);
        }
    }

    console.log("\n=== Assertions ===");

    if (service.total(5001) !== 66600) {
        throw new Error("Order calculation failed");
    }

    if (JSONPath.get(order, "customer.address.city") !== "Lucknow") {
        throw new Error("Nested property lookup failed");
    }

    if (removeSensitiveFields(apiPayload).profile.password !== undefined) {
        throw new Error("Sensitive field filtering failed");
    }

    console.log("All JSON workflow checks passed.");
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
