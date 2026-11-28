"use strict";

/*
 * COMPOSITION IN JAVASCRIPT
 *
 * Demonstrates:
 * 1. Object composition
 * 2. Component factories
 * 3. Delegation
 * 4. Dependency injection
 * 5. Event-driven composition
 * 6. Asynchronous workflows
 * 7. Policy evaluation
 * 8. Failure handling
 *
 * Runtime: Node.js 18+
 */

// -----------------------------------------------------
// 1. Component validation
// -----------------------------------------------------

class DomainError extends Error {
    constructor(message, code) {
        super(message);
        this.name = "DomainError";
        this.code = code;
    }
}

function requireString(value, field) {
    if (typeof value !== "string" || !value.trim()) {
        throw new DomainError(
            `${field} must be a non-empty string`,
            "INVALID_INPUT"
        );
    }
}

function requirePositiveNumber(value, field) {
    if (!Number.isFinite(value) || value <= 0) {
        throw new DomainError(
            `${field} must be positive`,
            "INVALID_NUMBER"
        );
    }
}


// -----------------------------------------------------
// 2. Composition through reusable objects
// -----------------------------------------------------

function createLogger(componentName) {
    requireString(componentName, "componentName");

    return Object.freeze({
        info(message, metadata = {}) {
            console.log({
                level: "INFO",
                component: componentName,
                message,
                metadata
            });
        },

        error(message, metadata = {}) {
            console.error({
                level: "ERROR",
                component: componentName,
                message,
                metadata
            });
        }
    });
}


function createCache() {
    const entries = new Map();

    return Object.freeze({
        set(key, value) {
            requireString(key, "key");
            entries.set(key, value);
        },

        get(key) {
            return entries.get(key);
        },

        has(key) {
            return entries.has(key);
        },

        delete(key) {
            return entries.delete(key);
        },

        size() {
            return entries.size;
        }
    });
}


function createRepository(cache, logger) {
    if (!cache || typeof cache.get !== "function") {
        throw new DomainError(
            "A valid cache component is required",
            "INVALID_DEPENDENCY"
        );
    }

    const records = new Map();

    return Object.freeze({
        async save(id, record) {
            requireString(id, "id");

            if (record === null || typeof record !== "object") {
                throw new DomainError(
                    "Record must be an object",
                    "INVALID_RECORD"
                );
            }

            const serialized = structuredClone(record);

            records.set(id, serialized);
            cache.set(id, structuredClone(serialized));

            logger.info("Record saved", { id });
        },

        async find(id) {
            requireString(id, "id");

            if (cache.has(id)) {
                logger.info("Cache hit", { id });
                return structuredClone(cache.get(id));
            }

            const record = records.get(id);

            if (!record) {
                return null;
            }

            cache.set(id, structuredClone(record));

            return structuredClone(record);
        },

        async delete(id) {
            const existed = records.delete(id);
            cache.delete(id);
            return existed;
        }
    });
}


// -----------------------------------------------------
// 3. Composition using classes
// -----------------------------------------------------

class Engine {
    #running = false;

    constructor(power) {
        requirePositiveNumber(power, "power");
        this.power = power;
    }

    start() {
        if (this.#running) {
            throw new DomainError(
                "Engine already running",
                "INVALID_STATE"
            );
        }

        this.#running = true;
    }

    stop() {
        if (!this.#running) {
            throw new DomainError(
                "Engine already stopped",
                "INVALID_STATE"
            );
        }

        this.#running = false;
    }

    get running() {
        return this.#running;
    }
}


class Vehicle {
    constructor({ engine, logger }) {
        if (!(engine instanceof Engine)) {
            throw new DomainError(
                "Vehicle requires an Engine",
                "INVALID_DEPENDENCY"
            );
        }

        this.engine = engine;
        this.logger = logger;
    }

    start() {
        this.engine.start();
        this.logger.info("Vehicle started");
    }

    stop() {
        this.engine.stop();
        this.logger.info("Vehicle stopped");
    }
}


// -----------------------------------------------------
// 4. Event-driven composition
// -----------------------------------------------------

class EventBus {
    #listeners = new Map();

    subscribe(eventName, callback) {
        requireString(eventName, "eventName");

        if (typeof callback !== "function") {
            throw new DomainError(
                "Callback must be a function",
                "INVALID_CALLBACK"
            );
        }

        if (!this.#listeners.has(eventName)) {
            this.#listeners.set(eventName, new Set());
        }

        const listeners = this.#listeners.get(eventName);
        listeners.add(callback);

        // Return an unsubscribe function.
        return () => {
            listeners.delete(callback);

            if (listeners.size === 0) {
                this.#listeners.delete(eventName);
            }
        };
    }

    async publish(eventName, payload) {
        const listeners = [
            ...(this.#listeners.get(eventName) || [])
        ];

        // All subscribers receive the same event.
        const results = await Promise.allSettled(
            listeners.map(listener =>
                Promise.resolve().then(() => listener(payload))
            )
        );

        return results;
    }
}


// -----------------------------------------------------
// 5. Asynchronous service composition
// -----------------------------------------------------

class InventoryService {
    #stock = new Map();

    constructor(initialStock) {
        for (const [productId, quantity] of Object.entries(initialStock)) {
            if (!Number.isInteger(quantity) || quantity < 0) {
                throw new DomainError(
                    "Stock must be a non-negative integer",
                    "INVALID_STOCK"
                );
            }

            this.#stock.set(productId, quantity);
        }
    }

    async reserve(productId, quantity) {
        requireString(productId, "productId");

        if (!Number.isInteger(quantity) || quantity <= 0) {
            throw new DomainError(
                "Quantity must be a positive integer",
                "INVALID_QUANTITY"
            );
        }

        const available = this.#stock.get(productId) || 0;

        if (available < quantity) {
            throw new DomainError(
                `Insufficient stock for ${productId}`,
                "INSUFFICIENT_STOCK"
            );
        }

        this.#stock.set(productId, available - quantity);

        return {
            productId,
            quantity,
            remaining: available - quantity
        };
    }

    async release(productId, quantity) {
        const available = this.#stock.get(productId) || 0;

        this.#stock.set(productId, available + quantity);
    }

    available(productId) {
        return this.#stock.get(productId) || 0;
    }
}


class PaymentService {
    async charge(amount, idempotencyKey) {
        requirePositiveNumber(amount, "amount");
        requireString(idempotencyKey, "idempotencyKey");

        return {
            transactionId: `TX-${idempotencyKey}`,
            amount,
            status: "SUCCESS"
        };
    }
}


class OrderService {
    constructor({
        inventory,
        payment,
        events,
        logger
    }) {
        this.inventory = inventory;
        this.payment = payment;
        this.events = events;
        this.logger = logger;
    }

    async process(order) {
        requireString(order.id, "order.id");

        if (!Array.isArray(order.items) || order.items.length === 0) {
            throw new DomainError(
                "Order requires at least one item",
                "EMPTY_ORDER"
            );
        }

        const reservations = [];
        let paymentCompleted = false;

        const total = order.items.reduce((sum, item) => {
            requirePositiveNumber(item.price, "item.price");

            if (!Number.isInteger(item.quantity) || item.quantity <= 0) {
                throw new DomainError(
                    "Item quantity must be positive",
                    "INVALID_QUANTITY"
                );
            }

            return sum + item.price * item.quantity;
        }, 0);

        try {
            for (const item of order.items) {
                const reservation = await this.inventory.reserve(
                    item.productId,
                    item.quantity
                );

                reservations.push(reservation);
            }

            const paymentResult = await this.payment.charge(
                total,
                order.id
            );

            paymentCompleted = true;

            const result = {
                orderId: order.id,
                total,
                payment: paymentResult,
                status: "PAID"
            };

            const eventResults = await this.events.publish(
                "order.paid",
                structuredClone(result)
            );

            this.logger.info("Order processed", {
                orderId: order.id
            });

            return {
                ...result,
                eventFailures: eventResults.filter(
                    item => item.status === "rejected"
                ).length
            };

        } catch (error) {
            // Inventory can be compensated before payment succeeds.
            // A completed payment must not be silently reversed here.
            if (!paymentCompleted) {
                for (const reservation of reservations.reverse()) {
                    await this.inventory.release(
                        reservation.productId,
                        reservation.quantity
                    );
                }
            }

            this.logger.error("Order processing failed", {
                orderId: order.id,
                error: error.message
            });

            throw error;
        }
    }
}


// -----------------------------------------------------
// 6. Composed authorization policy
// -----------------------------------------------------

function createAccessPolicy() {
    const rules = new Map([
        ["admin", new Set(["READ", "WRITE", "DELETE"])],
        ["reviewer", new Set(["READ", "REVIEW"])],
        ["developer", new Set(["READ", "WRITE"])],
        ["observer", new Set(["READ"])]
    ]);

    return Object.freeze({
        can(role, action) {
            requireString(role, "role");
            requireString(action, "action");

            return rules.get(role)?.has(action) ?? false;
        },

        permissions(role) {
            return [...(rules.get(role) || [])];
        }
    });
}


// -----------------------------------------------------
// 7. Automated tests
// -----------------------------------------------------

async function runTests() {
    const logger = createLogger("composition-demo");

    // Test component composition.
    const engine = new Engine(150);
    const vehicle = new Vehicle({ engine, logger });

    vehicle.start();

    if (!engine.running) {
        throw new Error("Vehicle failed to start");
    }

    vehicle.stop();

    // Test repository composition.
    const cache = createCache();
    const repository = createRepository(cache, logger);

    await repository.save("USER1", {
        name: "Atul",
        active: true
    });

    const user = await repository.find("USER1");

    console.assert(user.name === "Atul");

    // Verify defensive copying.
    user.name = "Modified";

    const original = await repository.find("USER1");

    console.assert(original.name === "Atul");

    // Test event composition.
    const eventBus = new EventBus();
    let eventReceived = false;

    const unsubscribe = eventBus.subscribe(
        "system.ready",
        () => {
            eventReceived = true;
        }
    );

    await eventBus.publish("system.ready", { status: true });

    console.assert(eventReceived);

    unsubscribe();

    // Test asynchronous order composition.
    const inventory = new InventoryService({
        LAPTOP: 5,
        MOUSE: 10
    });

    const payment = new PaymentService();

    const orderService = new OrderService({
        inventory,
        payment,
        events: eventBus,
        logger
    });

    const result = await orderService.process({
        id: "ORDER100",
        items: [
            {
                productId: "LAPTOP",
                price: 60000,
                quantity: 1
            },
            {
                productId: "MOUSE",
                price: 1000,
                quantity: 2
            }
        ]
    });

    console.assert(result.status === "PAID");
    console.assert(result.total === 62000);
    console.assert(inventory.available("LAPTOP") === 4);

    // Test rollback after reservation failure.
    try {
        await orderService.process({
            id: "ORDER101",
            items: [
                {
                    productId: "LAPTOP",
                    price: 60000,
                    quantity: 1
                },
                {
                    productId: "MOUSE",
                    price: 1000,
                    quantity: 100
                }
            ]
        });

        throw new Error("Expected inventory failure");
    } catch (error) {
        console.assert(error.code === "INSUFFICIENT_STOCK");
    }

    console.assert(inventory.available("LAPTOP") === 4);

    // Test policy composition.
    const policy = createAccessPolicy();

    console.assert(policy.can("admin", "DELETE"));
    console.assert(!policy.can("observer", "WRITE"));

    console.log("All JavaScript composition tests passed.");
}


// -----------------------------------------------------
// 8. Application entry point
// -----------------------------------------------------

async function main() {
    const logger = createLogger("main");

    logger.info("Starting composition demonstration");

    try {
        await runTests();
    } catch (error) {
        logger.error("Application failed", {
            message: error.message,
            code: error.code || "UNEXPECTED_ERROR"
        });

        process.exitCode = 1;
    }
}

main();
