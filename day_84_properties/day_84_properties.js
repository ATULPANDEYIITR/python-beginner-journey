"use strict";

/*
 * Python property concepts implemented through JavaScript accessors,
 * descriptors, proxies, validation, and event-driven state management.
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

function requireFiniteNumber(value, field) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new ValidationError(`${field} must be a finite number.`);
    }
}

// 1. Getter and setter accessors
class Temperature {
    #celsius;

    constructor(value) {
        this.celsius = value;
    }

    get celsius() {
        return this.#celsius;
    }

    set celsius(value) {
        requireFiniteNumber(value, "Temperature");

        if (value < -273.15 || value > 1000) {
            throw new ValidationError("Temperature outside supported range.");
        }

        this.#celsius = value;
    }

    get fahrenheit() {
        return this.#celsius * 9 / 5 + 32;
    }

    set fahrenheit(value) {
        requireFiniteNumber(value, "Fahrenheit");
        this.celsius = (value - 32) * 5 / 9;
    }
}

// 2. Read-only accessor
class Employee {
    #id;

    constructor(id, name) {
        if (!Number.isInteger(id) || id <= 0) {
            throw new ValidationError("Invalid employee ID.");
        }

        this.#id = id;
        this.name = name;
    }

    get id() {
        return this.#id;
    }
}

// 3. Computed properties
class Rectangle {
    #width;
    #height;

    constructor(width, height) {
        this.width = width;
        this.height = height;
    }

    get width() {
        return this.#width;
    }

    set width(value) {
        requireFiniteNumber(value, "Width");
        if (value <= 0) throw new ValidationError("Width must be positive.");
        this.#width = value;
    }

    get height() {
        return this.#height;
    }

    set height(value) {
        requireFiniteNumber(value, "Height");
        if (value <= 0) throw new ValidationError("Height must be positive.");
        this.#height = value;
    }

    get area() {
        return this.#width * this.#height;
    }

    get perimeter() {
        return 2 * (this.#width + this.#height);
    }
}

// 4. Property-like behavior using a Proxy
function createValidatedConfiguration(initialValues) {
    const rules = {
        port(value) {
            return Number.isInteger(value) && value >= 1 && value <= 65535;
        },
        environment(value) {
            return ["development", "testing", "production"].includes(value);
        },
        debug(value) {
            return typeof value === "boolean";
        }
    };

    const state = { ...initialValues };

    return new Proxy(state, {
        set(target, property, value) {
            const validator = rules[property];

            if (!validator) {
                throw new ValidationError(`Unknown configuration property: ${String(property)}`);
            }

            if (!validator(value)) {
                throw new ValidationError(`Invalid value for ${String(property)}.`);
            }

            target[property] = value;
            return true;
        },

        defineProperty() {
            throw new ValidationError("Defining new configuration fields is prohibited.");
        }
    });
}

// 5. Descriptor-based property validation
function positiveNumberDescriptor() {
    const values = new WeakMap();

    return {
        get() {
            return values.get(this);
        },

        set(value) {
            requireFiniteNumber(value, "Account balance");

            if (value < 0) {
                throw new ValidationError("Balance cannot be negative.");
            }

            values.set(this, value);
        },

        enumerable: true,
        configurable: false
    };
}

class Account {
    constructor(accountNumber, balance) {
        if (!/^[A-Z0-9]{6,20}$/.test(accountNumber)) {
            throw new ValidationError("Invalid account number.");
        }

        this.accountNumber = accountNumber;
        this.balance = balance;
    }

    deposit(amount) {
        requireFiniteNumber(amount, "Deposit");
        if (amount <= 0) throw new ValidationError("Deposit must be positive.");
        this.balance += amount;
    }

    withdraw(amount) {
        requireFiniteNumber(amount, "Withdrawal");
        if (amount <= 0) throw new ValidationError("Withdrawal must be positive.");
        if (amount > this.balance) throw new ValidationError("Insufficient funds.");
        this.balance -= amount;
    }
}

Object.defineProperty(
    Account.prototype,
    "balance",
    positiveNumberDescriptor()
);

// 6. Cached computed property with invalidation
class Inventory {
    #items;
    #cachedValue;
    #dirty = true;
    #calculations = 0;

    constructor(items) {
        this.#items = new Map();

        for (const [name, quantity] of Object.entries(items)) {
            this.setQuantity(name, quantity);
        }
    }

    setQuantity(name, quantity) {
        if (typeof name !== "string" || !name.trim()) {
            throw new ValidationError("Product name cannot be empty.");
        }

        if (!Number.isInteger(quantity) || quantity < 0) {
            throw new ValidationError("Quantity must be a non-negative integer.");
        }

        this.#items.set(name, quantity);
        this.#dirty = true;
    }

    get totalUnits() {
        if (this.#dirty) {
            this.#calculations++;
            this.#cachedValue = [...this.#items.values()]
                .reduce((total, value) => total + value, 0);

            this.#dirty = false;
        }

        return this.#cachedValue;
    }

    get calculationCount() {
        return this.#calculations;
    }
}

// 7. Event-driven property changes
class ObservableUser extends EventEmitter {
    #email;

    constructor(email) {
        super();
        this.email = email;
    }

    get email() {
        return this.#email;
    }

    set email(value) {
        if (typeof value !== "string" ||
            !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value)) {
            throw new ValidationError("Invalid email.");
        }

        const normalized = value.trim().toLowerCase();
        const previous = this.#email;

        if (previous === normalized) return;

        this.#email = normalized;

        this.emit("emailChanged", {
            previous,
            current: normalized,
            changedAt: new Date().toISOString()
        });
    }
}

// 8. Asynchronous property-backed data service
class ReportService {
    #cache = new Map();

    constructor(loader) {
        if (typeof loader !== "function") {
            throw new ValidationError("Loader must be a function.");
        }

        this.loader = loader;
    }

    async getReport(reportId) {
        if (typeof reportId !== "string" || !reportId.trim()) {
            throw new ValidationError("Report ID is required.");
        }

        if (this.#cache.has(reportId)) {
            return this.#cache.get(reportId);
        }

        // Store the pending promise to avoid duplicate concurrent requests.
        const pending = Promise.resolve()
            .then(() => this.loader(reportId))
            .then(result => {
                if (result === null || typeof result !== "object") {
                    throw new Error("Invalid report response.");
                }

                return Object.freeze({ ...result });
            });

        this.#cache.set(reportId, pending);

        try {
            const result = await pending;
            this.#cache.set(reportId, Promise.resolve(result));
            return result;
        } catch (error) {
            this.#cache.delete(reportId);
            throw error;
        }
    }

    invalidate(reportId) {
        this.#cache.delete(reportId);
    }
}

// 9. Tests and demonstration
async function runTests() {
    const temperature = new Temperature(25);
    assert.equal(temperature.fahrenheit, 77);

    temperature.fahrenheit = 32;
    assert.equal(temperature.celsius, 0);

    assert.throws(() => {
        temperature.celsius = -300;
    }, ValidationError);

    const employee = new Employee(101, "Asha");
    assert.equal(employee.id, 101);

    const rectangle = new Rectangle(10, 5);
    assert.equal(rectangle.area, 50);
    assert.equal(rectangle.perimeter, 30);

    const config = createValidatedConfiguration({
        port: 3000,
        environment: "development",
        debug: true
    });

    config.port = 8080;
    assert.equal(config.port, 8080);

    assert.throws(() => {
        config.port = 70000;
    }, ValidationError);

    const account = new Account("BANK1234", 1000);
    account.deposit(500);
    account.withdraw(200);
    assert.equal(account.balance, 1300);

    assert.throws(() => {
        account.withdraw(5000);
    }, ValidationError);

    const inventory = new Inventory({
        laptops: 10,
        keyboards: 20
    });

    assert.equal(inventory.totalUnits, 30);
    assert.equal(inventory.totalUnits, 30);
    assert.equal(inventory.calculationCount, 1);

    inventory.setQuantity("mice", 5);
    assert.equal(inventory.totalUnits, 35);
    assert.equal(inventory.calculationCount, 2);

    const user = new ObservableUser("ATUL@example.com");
    let eventCount = 0;

    user.on("emailChanged", event => {
        eventCount++;
        console.log("Email event:", event.previous, "->", event.current);
    });

    user.email = "new@example.com";
    assert.equal(eventCount, 1);

    const reportService = new ReportService(async id => ({
        id,
        total: 12500
    }));

    const [first, second] = await Promise.all([
        reportService.getReport("R001"),
        reportService.getReport("R001")
    ]);

    assert.deepEqual(first, second);

    console.log("\nAll JavaScript property tests passed.");
    console.log("Rectangle area:", rectangle.area);
    console.log("Inventory units:", inventory.totalUnits);
    console.log("Account balance:", account.balance);
    console.log("Report:", first);
}

runTests().catch(error => {
    console.error("Execution failed:", error);
    process.exitCode = 1;
});
