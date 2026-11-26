"use strict";

/*
 * Method Overriding
 * Event-driven order fulfillment and shipping policy.
 *
 * Runtime: Node.js 18+
 */

const EventEmitter = require("node:events");
const crypto = require("node:crypto");

class DomainError extends Error {
    constructor(message, code) {
        super(message);
        this.name = "DomainError";
        this.code = code;
    }
}

const OrderStatus = Object.freeze({
    CREATED: "CREATED",
    VALIDATED: "VALIDATED",
    SHIPPED: "SHIPPED",
    REJECTED: "REJECTED"
});

class Order {
    constructor(id, amount, destination) {
        if (!id || typeof id !== "string") {
            throw new DomainError("Invalid order ID", "INVALID_ID");
        }

        if (!Number.isFinite(amount) || amount <= 0) {
            throw new DomainError("Invalid order amount", "INVALID_AMOUNT");
        }

        if (!destination || typeof destination !== "string") {
            throw new DomainError(
                "Destination is required",
                "INVALID_DESTINATION"
            );
        }

        this.id = id;
        this.amount = amount;
        this.destination = destination;
        this.status = OrderStatus.CREATED;
        this.shippingCost = 0;
        this.history = [];
    }

    transition(nextStatus, details = {}) {
        const allowed = {
            CREATED: ["VALIDATED", "REJECTED"],
            VALIDATED: ["SHIPPED", "REJECTED"],
            SHIPPED: [],
            REJECTED: []
        };

        if (!allowed[this.status].includes(nextStatus)) {
            throw new DomainError(
                `Invalid transition: ${this.status} -> ${nextStatus}`,
                "INVALID_TRANSITION"
            );
        }

        this.status = nextStatus;

        this.history.push({
            status: nextStatus,
            timestamp: new Date().toISOString(),
            ...details
        });
    }
}

class ShippingPolicy {
    constructor(name) {
        this.name = name;
    }

    calculateCost(order) {
        throw new Error("calculateCost() must be overridden");
    }

    validate(order) {
        if (!(order instanceof Order)) {
            throw new DomainError(
                "Expected an Order instance",
                "INVALID_ORDER"
            );
        }

        if (order.status !== OrderStatus.CREATED) {
            throw new DomainError(
                "Only newly created orders can be validated",
                "INVALID_ORDER_STATE"
            );
        }

        return true;
    }

    describe() {
        return `${this.name} shipping policy`;
    }
}

class StandardShipping extends ShippingPolicy {
    calculateCost(order) {
        this.validate(order);
        return 50 + order.amount * 0.02;
    }
}

class ExpressShipping extends ShippingPolicy {
    calculateCost(order) {
        this.validate(order);

        if (order.destination === "RESTRICTED") {
            throw new DomainError(
                "Express delivery unavailable",
                "UNAVAILABLE_SERVICE"
            );
        }

        return 150 + order.amount * 0.03;
    }
}

class InternationalShipping extends ShippingPolicy {
    calculateCost(order) {
        this.validate(order);

        if (order.destination === "DOMESTIC") {
            throw new DomainError(
                "International shipping requires an overseas destination",
                "INVALID_DESTINATION"
            );
        }

        return 500 + order.amount * 0.08;
    }
}

class SubscriptionShipping extends StandardShipping {
    calculateCost(order) {
        // Reuse the inherited calculation and override the final policy.
        const standardCost = super.calculateCost(order);
        return Math.max(0, standardCost - 75);
    }

    describe() {
        return "Subscription member shipping policy";
    }
}

class ShippingRegistry {
    #policies = new Map();

    register(policy) {
        if (!(policy instanceof ShippingPolicy)) {
            throw new TypeError("Invalid shipping policy");
        }

        if (this.#policies.has(policy.name)) {
            throw new DomainError(
                "Shipping policy already registered",
                "DUPLICATE_POLICY"
            );
        }

        this.#policies.set(policy.name, policy);
    }

    get(name) {
        const policy = this.#policies.get(name);

        if (!policy) {
            throw new DomainError(
                `Unknown shipping policy: ${name}`,
                "UNKNOWN_POLICY"
            );
        }

        return policy;
    }
}

class FulfillmentService extends EventEmitter {
    constructor(registry) {
        super();
        this.registry = registry;
        this.processedOrders = new Set();
    }

    async process(order, policyName) {
        if (!(order instanceof Order)) {
            throw new DomainError("Invalid order", "INVALID_ORDER");
        }

        if (this.processedOrders.has(order.id)) {
            throw new DomainError(
                "Duplicate order processing",
                "DUPLICATE_ORDER"
            );
        }

        const policy = this.registry.get(policyName);

        try {
            // The selected object's override is invoked at runtime.
            const cost = policy.calculateCost(order);

            if (!Number.isFinite(cost) || cost < 0) {
                throw new DomainError(
                    "Shipping policy returned an invalid cost",
                    "INVALID_POLICY_RESULT"
                );
            }

            order.shippingCost = Number(cost.toFixed(2));
            order.transition(OrderStatus.VALIDATED, {
                policy: policyName,
                shippingCost: order.shippingCost
            });

            this.emit("order:validated", {
                orderId: order.id,
                policy: policyName,
                cost: order.shippingCost
            });

            // Simulate an asynchronous fulfillment operation.
            await Promise.resolve();

            order.transition(OrderStatus.SHIPPED);
            this.processedOrders.add(order.id);

            this.emit("order:shipped", {
                orderId: order.id,
                cost: order.shippingCost
            });

            return {
                orderId: order.id,
                status: order.status,
                shippingCost: order.shippingCost,
                policy: policy.describe()
            };
        } catch (error) {
            if (
                order.status === OrderStatus.CREATED ||
                order.status === OrderStatus.VALIDATED
            ) {
                order.transition(OrderStatus.REJECTED, {
                    reason: error.message
                });
            }

            this.emit("order:rejected", {
                orderId: order.id,
                error: error.message
            });

            throw error;
        }
    }
}

async function main() {
    const registry = new ShippingRegistry();

    registry.register(new StandardShipping("standard"));
    registry.register(new ExpressShipping("express"));
    registry.register(new InternationalShipping("international"));
    registry.register(new SubscriptionShipping("subscription"));

    const fulfillment = new FulfillmentService(registry);

    fulfillment.on("order:validated", event => {
        console.log("VALIDATED:", event);
    });

    fulfillment.on("order:shipped", event => {
        console.log("SHIPPED:", event);
    });

    fulfillment.on("order:rejected", event => {
        console.log("REJECTED:", event);
    });

    const orders = [
        new Order("ORD-1001", 2000, "DOMESTIC"),
        new Order("ORD-1002", 3000, "DOMESTIC"),
        new Order("ORD-1003", 5000, "OVERSEAS"),
        new Order("ORD-1004", 1000, "DOMESTIC")
    ];

    const policies = [
        "standard",
        "express",
        "international",
        "subscription"
    ];

    for (let index = 0; index < orders.length; index++) {
        try {
            const result = await fulfillment.process(
                orders[index],
                policies[index]
            );

            console.log("RESULT:", result);
        } catch (error) {
            console.log("PROCESSING ERROR:", error.message);
        }
    }

    console.log("\nORDER HISTORY");

    for (const order of orders) {
        console.log(order.id, order.history);
    }

    console.log("\nFAILURE HANDLING");

    const invalidOrder = new Order(
        "ORD-1005",
        1000,
        "RESTRICTED"
    );

    try {
        await fulfillment.process(invalidOrder, "express");
    } catch (error) {
        console.log(error.code, error.message);
    }

    try {
        await fulfillment.process(orders[0], "standard");
    } catch (error) {
        console.log(error.code, error.message);
    }

    console.log("\nPOLYMORPHIC POLICY EVALUATION");

    for (const name of [
        "standard",
        "express",
        "international",
        "subscription"
    ]) {
        const policy = registry.get(name);
        console.log(`${name}: ${policy.describe()}`);
    }

    console.log("\nExecution identifier:", crypto.randomUUID());
}

main().catch(error => {
    console.error("Fatal execution error:", error);
    process.exitCode = 1;
});
