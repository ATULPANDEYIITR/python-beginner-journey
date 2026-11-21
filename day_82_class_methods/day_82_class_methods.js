"use strict";

/*
 * CLASS METHODS IN JAVASCRIPT
 *
 * Demonstrates:
 * - Static methods
 * - Static inheritance
 * - Alternative object construction
 * - Shared class-level state
 * - Static initialization
 * - Private static fields
 * - Runtime validation
 * - Event-driven registry operations
 *
 * Run:
 * node class_methods.js
 */

const { randomUUID } = require("node:crypto");
const { EventEmitter } = require("node:events");

class DomainError extends Error {
    constructor(message) {
        super(message);
        this.name = "DomainError";
    }
}

class Product {
    static #products = new Map();
    static #minimumPrice = 100;
    static #events = new EventEmitter();

    static {
        // Static initialization executes once when the class is initialized.
        this.#events.setMaxListeners(50);
    }

    constructor({ id, name, price, category }) {
        if (typeof id !== "string" || !id.trim()) {
            throw new TypeError("Product ID is required.");
        }

        if (typeof name !== "string" || !name.trim()) {
            throw new TypeError("Product name is required.");
        }

        if (typeof category !== "string" || !category.trim()) {
            throw new TypeError("Product category is required.");
        }

        if (!Number.isFinite(price) || price < Product.#minimumPrice) {
            throw new RangeError("Product price is below the minimum.");
        }

        if (Product.#products.has(id)) {
            throw new DomainError(`Duplicate product ID: ${id}`);
        }

        this.id = id;
        this.name = name.trim();
        this.category = category.trim();
        this.price = price;

        Product.#products.set(id, this);

        Product.#events.emit("product:created", {
            id: this.id,
            name: this.name
        });
    }

    // Static method: called on the class, not an object instance.
    static create(data) {
        return new this(data);
    }

    static fromCSV(line) {
        if (typeof line !== "string") {
            throw new TypeError("CSV input must be a string.");
        }

        const fields = line.split(",").map(value => value.trim());

        if (fields.length !== 4) {
            throw new DomainError("Expected four CSV fields.");
        }

        const [id, name, priceText, category] = fields;

        if (!/^\d+(\.\d{1,2})?$/.test(priceText)) {
            throw new DomainError("Invalid price format.");
        }

        return this.create({
            id,
            name,
            price: Number(priceText),
            category
        });
    }

    static find(id) {
        return this.#products.get(id) ?? null;
    }

    static getAll() {
        return [...this.#products.values()];
    }

    static getCount() {
        return this.#products.size;
    }

    static getReport() {
        const report = new Map();

        for (const product of this.#products.values()) {
            const current = report.get(product.category) ?? {
                count: 0,
                totalValue: 0
            };

            current.count++;
            current.totalValue += product.price;

            report.set(product.category, current);
        }

        return Object.fromEntries(report);
    }

    static setMinimumPrice(value) {
        if (!Number.isFinite(value) || value <= 0) {
            throw new RangeError("Minimum price must be positive.");
        }

        this.#minimumPrice = value;
    }

    static getMinimumPrice() {
        return this.#minimumPrice;
    }

    static on(event, listener) {
        this.#events.on(event, listener);

        return () => this.#events.off(event, listener);
    }

    static remove(id) {
        const product = this.#products.get(id);

        if (!product) {
            return false;
        }

        this.#products.delete(id);

        this.#events.emit("product:removed", {
            id,
            name: product.name
        });

        return true;
    }

    static reset() {
        this.#products.clear();
    }

    static generateId() {
        return `PRD-${randomUUID()}`;
    }

    // Static methods can be inherited, but private static state belongs
    // to the declaring class and is not accessible through subclasses.
    static formatMoney(value) {
        if (!Number.isFinite(value)) {
            throw new TypeError("Expected a finite number.");
        }

        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR"
        }).format(value);
    }

    applyDiscount(percent) {
        if (!Number.isFinite(percent) || percent < 0 || percent > 50) {
            throw new RangeError("Discount must be between 0 and 50.");
        }

        this.price *= (100 - percent) / 100;
    }
}

class DigitalProduct extends Product {
    constructor(data) {
        super(data);

        if (typeof data.downloadUrl !== "string") {
            Product.remove(data.id);
            throw new TypeError("A download URL is required.");
        }

        let url;

        try {
            url = new URL(data.downloadUrl);
        } catch {
            Product.remove(data.id);
            throw new TypeError("Invalid download URL.");
        }

        if (url.protocol !== "https:") {
            Product.remove(data.id);
            throw new TypeError("Download URLs must use HTTPS.");
        }

        this.downloadUrl = url.href;
    }

    static fromDownload(data) {
        return new this(data);
    }
}

async function main() {
    Product.reset();

    console.log("1. Subscribe to domain events");

    const unsubscribe = Product.on(
        "product:created",
        event => console.log("Created:", event.name)
    );

    console.log("\n2. Create products through static methods");

    const laptop = Product.create({
        id: "P101",
        name: "Business Laptop",
        price: 75000,
        category: "Electronics"
    });

    Product.fromCSV("P102,Office Chair,12500,Furniture");

    console.log("\n3. Search through the class registry");

    console.log(Product.find("P101"));

    console.log("\n4. Class-level policy");

    Product.setMinimumPrice(500);

    console.log("Minimum price:", Product.getMinimumPrice());

    console.log("\n5. Subclass factory");

    const software = DigitalProduct.fromDownload({
        id: "D101",
        name: "Security Software",
        price: 2500,
        category: "Software",
        downloadUrl: "https://example.com/download"
    });

    console.log(software instanceof DigitalProduct);
    console.log(software.downloadUrl);

    console.log("\n6. Instance-level operation");

    laptop.applyDiscount(10);

    console.log(Product.formatMoney(laptop.price));

    console.log("\n7. Aggregate report");

    console.log(Product.getReport());

    console.log("\n8. Asynchronous processing");

    const result = await Promise.resolve().then(() => {
        return {
            totalProducts: Product.getCount(),
            generatedId: Product.generateId()
        };
    });

    console.log(result);

    console.log("\n9. Validation and failure handling");

    try {
        Product.create({
            id: "P103",
            name: "Invalid Product",
            price: -10,
            category: "Testing"
        });
    } catch (error) {
        console.log(error.name, error.message);
    }

    try {
        Product.create({
            id: "P101",
            name: "Duplicate",
            price: 2000,
            category: "Testing"
        });
    } catch (error) {
        console.log(error.name, error.message);
    }

    console.log("\n10. Event subscription management");

    unsubscribe();

    Product.remove("P102");

    console.log("Remaining products:", Product.getCount());
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
