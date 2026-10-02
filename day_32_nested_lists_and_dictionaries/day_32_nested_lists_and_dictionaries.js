/**
 * Nested Lists and Dictionaries
 *
 * JavaScript represents dictionary-like structures primarily with Objects
 * and Map, while ordered collections are represented with Arrays. Real
 * application data frequently combines them: arrays of objects, objects
 * containing arrays, and deeper mixtures.
 *
 * Execute with:
 *   node nested-lists-dictionaries.js
 */

"use strict";

function printTitle(title) {
    console.log(`\n${"=".repeat(72)}`);
    console.log(title);
    console.log("=".repeat(72));
}

function nestedArrays() {
    printTitle("Nested arrays");

    const matrix = [
        [10, 20, 30],
        [40, 50, 60],
        [70, 80, 90],
    ];

    console.log("Matrix:", matrix);
    console.log("Row:", matrix[1]);
    console.log("Cell:", matrix[1][2]);

    const flattened = matrix.flat();
    console.log("Flattened:", flattened);

    const total = matrix.flat().reduce((sum, value) => sum + value, 0);
    console.log("Total:", total);

    // Array.from creates independent rows. Using Array(n).fill([]) would
    // make every row reference the same nested array.
    const safeGrid = Array.from({ length: 3 }, () => Array(3).fill(0));
    safeGrid[0][0] = 99;

    console.log("Independent grid rows:", safeGrid);
}

function nestedObjects() {
    printTitle("Nested objects");

    const employee = {
        id: "EMP-104",
        name: "Anika Rao",
        department: {
            name: "Engineering",
            location: "Bengaluru",
        },
        skills: {
            JavaScript: {
                level: "advanced",
                years: 5,
            },
            SQL: {
                level: "advanced",
                years: 4,
            },
        },
    };

    console.log("Department:", employee.department.name);
    console.log("JavaScript experience:", employee.skills.JavaScript.years);

    employee.skills.JavaScript.years += 1;
    employee.department.location = "Hyderabad";

    console.log("Updated employee:", employee);
}

function optionalChainingAndNullishCoalescing() {
    printTitle("Safe nested access");

    const configuration = {
        application: {
            database: {
                host: "localhost",
                port: 5432,
            },
        },
    };

    console.log(
        "Database host:",
        configuration.application?.database?.host ?? "not configured"
    );

    console.log(
        "Cache host:",
        configuration.application?.cache?.host ?? "not configured"
    );

    // Optional chaining prevents TypeError when an intermediate property is
    // missing. Nullish coalescing supplies a default only for null or undefined.
}

function mixedApplicationData() {
    printTitle("Arrays of objects containing arrays and objects");

    const orders = [
        {
            id: "ORD-1001",
            customer: {
                name: "Priya",
                city: "Delhi",
            },
            items: [
                { sku: "KB-01", quantity: 2, price: 2500 },
                { sku: "MS-02", quantity: 1, price: 1200 },
            ],
        },
        {
            id: "ORD-1002",
            customer: {
                name: "Rahul",
                city: "Mumbai",
            },
            items: [
                { sku: "MN-03", quantity: 1, price: 15000 },
                { sku: "HD-04", quantity: 2, price: 4500 },
            ],
        },
    ];

    const orderTotals = orders.map((order) => ({
        id: order.id,
        customer: order.customer.name,
        total: order.items.reduce(
            (sum, item) => sum + item.quantity * item.price,
            0
        ),
    }));

    console.log(orderTotals);
}

function getByPath(root, path, defaultValue = undefined) {
    let current = root;

    for (const key of path) {
        if (
            current === null ||
            current === undefined ||
            (typeof current !== "object" && !Array.isArray(current))
        ) {
            return defaultValue;
        }

        if (!(key in current)) {
            return defaultValue;
        }

        current = current[key];
    }

    return current;
}

function demonstratePathLookup() {
    printTitle("Generic path lookup");

    const document = {
        profile: {
            addresses: [
                {
                    city: "Pune",
                    postalCode: 411001,
                },
            ],
        },
    };

    console.log(
        "City:",
        getByPath(document, ["profile", "addresses", 0, "city"])
    );

    console.log(
        "Missing country:",
        getByPath(
            document,
            ["profile", "addresses", 0, "country"],
            "Unknown"
        )
    );
}

function walkNestedValue(value, path = [], callback) {
    if (Array.isArray(value)) {
        value.forEach((child, index) => {
            walkNestedValue(child, [...path, index], callback);
        });
        return;
    }

    if (value !== null && typeof value === "object") {
        Object.entries(value).forEach(([key, child]) => {
            walkNestedValue(child, [...path, key], callback);
        });
        return;
    }

    callback(path, value);
}

function demonstrateRecursiveTraversal() {
    printTitle("Recursive traversal");

    const configuration = {
        service: {
            name: "inventory",
            features: ["stock", "pricing"],
            limits: {
                requests: 120,
                connections: 20,
            },
        },
    };

    walkNestedValue(configuration, [], (path, value) => {
        console.log(`${path.join(".")} ->`, value);
    });
}

function validateOrder(order) {
    const errors = [];

    if (!order || typeof order !== "object" || Array.isArray(order)) {
        return ["Order must be an object."];
    }

    if (typeof order.id !== "string" || order.id.trim() === "") {
        errors.push("id must be a non-empty string.");
    }

    if (
        !order.customer ||
        typeof order.customer !== "object" ||
        Array.isArray(order.customer)
    ) {
        errors.push("customer must be an object.");
    } else if (typeof order.customer.name !== "string") {
        errors.push("customer.name must be a string.");
    }

    if (!Array.isArray(order.items)) {
        errors.push("items must be an array.");
    } else {
        order.items.forEach((item, index) => {
            if (!item || typeof item !== "object") {
                errors.push(`items[${index}] must be an object.`);
                return;
            }

            if (typeof item.sku !== "string") {
                errors.push(`items[${index}].sku must be a string.`);
            }

            if (!Number.isInteger(item.quantity) || item.quantity <= 0) {
                errors.push(
                    `items[${index}].quantity must be a positive integer.`
                );
            }

            if (typeof item.price !== "number" || item.price < 0) {
                errors.push(
                    `items[${index}].price must be a non-negative number.`
                );
            }
        });
    }

    return errors;
}

function demonstrateValidation() {
    printTitle("Nested structure validation");

    const validOrder = {
        id: "ORD-1",
        customer: {
            name: "Meera",
        },
        items: [
            {
                sku: "BOOK-1",
                quantity: 2,
                price: 750,
            },
        ],
    };

    const invalidOrder = {
        id: 77,
        customer: {
            name: null,
        },
        items: [
            {
                sku: "BROKEN",
                quantity: -2,
                price: "500",
            },
        ],
    };

    console.log("Valid order errors:", validateOrder(validOrder));
    console.log("Invalid order errors:", validateOrder(invalidOrder));
}

function groupNestedData() {
    printTitle("Grouping nested records with Map");

    const transactions = [
        { region: "North", category: "Software", amount: 12000 },
        { region: "North", category: "Hardware", amount: 18000 },
        { region: "South", category: "Software", amount: 9000 },
        { region: "North", category: "Software", amount: 7000 },
        { region: "South", category: "Hardware", amount: 11000 },
    ];

    const grouped = new Map();

    for (const transaction of transactions) {
        if (!grouped.has(transaction.region)) {
            grouped.set(transaction.region, new Map());
        }

        const categories = grouped.get(transaction.region);

        if (!categories.has(transaction.category)) {
            categories.set(transaction.category, []);
        }

        categories.get(transaction.category).push(transaction.amount);
    }

    const report = Object.fromEntries(
        [...grouped.entries()].map(([region, categories]) => [
            region,
            Object.fromEntries(
                [...categories.entries()].map(([category, amounts]) => [
                    category,
                    {
                        count: amounts.length,
                        total: amounts.reduce((sum, value) => sum + value, 0),
                    },
                ])
            ),
        ])
    );

    console.log(report);
}

function flattenObject(object, prefix = "", output = {}) {
    for (const [key, value] of Object.entries(object)) {
        const path = prefix ? `${prefix}.${key}` : key;

        if (
            value !== null &&
            typeof value === "object" &&
            !Array.isArray(value)
        ) {
            flattenObject(value, path, output);
        } else {
            output[path] = value;
        }
    }

    return output;
}

function demonstrateFlattening() {
    printTitle("Flattening nested objects");

    const settings = {
        server: {
            http: {
                host: "0.0.0.0",
                port: 8080,
            },
            limits: {
                requestsPerMinute: 120,
            },
        },
        logging: {
            level: "INFO",
            outputs: ["console", "file"],
        },
    };

    console.log(flattenObject(settings));
}

function demonstrateReferenceBehavior() {
    printTitle("References, shallow copies, and deep copies");

    const original = {
        items: [
            {
                name: "Keyboard",
                tags: ["input", "usb"],
            },
        ],
    };

    const shallow = { ...original };
    shallow.items[0].tags.push("mechanical");

    console.log("Original after shallow copy mutation:", original);

    // structuredClone recursively copies supported structured data. It avoids
    // JSON serialization problems for several built-in types, but it still
    // cannot clone every JavaScript value, such as functions.
    const deep = structuredClone(original);
    deep.items[0].tags.push("office");

    console.log("Original after deep copy mutation:", original);
    console.log("Deep copy:", deep);
}

class InventoryIndex {
    constructor(products) {
        this.bySku = new Map();
        this.byCategory = new Map();

        for (const product of products) {
            if (this.bySku.has(product.sku)) {
                throw new Error(`Duplicate SKU: ${product.sku}`);
            }

            this.bySku.set(product.sku, product);

            if (!this.byCategory.has(product.category)) {
                this.byCategory.set(product.category, []);
            }

            this.byCategory.get(product.category).push(product);
        }
    }

    findBySku(sku) {
        return this.bySku.get(sku);
    }

    findByCategory(category) {
        return this.byCategory.get(category) ?? [];
    }

    totalStockByCity() {
        const totals = new Map();

        for (const product of this.bySku.values()) {
            for (const warehouse of product.warehouses) {
                totals.set(
                    warehouse.city,
                    (totals.get(warehouse.city) ?? 0) + warehouse.quantity
                );
            }
        }

        return Object.fromEntries(totals);
    }
}

function inventoryCaseStudy() {
    printTitle("Case study: inventory indexes");

    const products = [
        {
            sku: "LAP-100",
            name: "Developer Laptop",
            category: "computing",
            pricing: {
                currency: "INR",
                amount: 95000,
            },
            warehouses: [
                { city: "Delhi", quantity: 12 },
                { city: "Pune", quantity: 8 },
            ],
        },
        {
            sku: "MON-200",
            name: "4K Monitor",
            category: "display",
            pricing: {
                currency: "INR",
                amount: 42000,
            },
            warehouses: [
                { city: "Delhi", quantity: 5 },
                { city: "Pune", quantity: 11 },
            ],
        },
    ];

    const index = new InventoryIndex(products);

    console.log("SKU lookup:", index.findBySku("LAP-100"));
    console.log(
        "Computing products:",
        index.findByCategory("computing").map((product) => product.name)
    );
    console.log("Stock by city:", index.totalStockByCity());
}

function jsonRoundTrip() {
    printTitle("JSON serialization");

    const payload = {
        application: {
            name: "inventory",
            features: ["stock", "pricing"],
            replicas: [
                { host: "db-1", readOnly: true },
                { host: "db-2", readOnly: true },
            ],
        },
    };

    const serialized = JSON.stringify(payload, null, 2);
    const restored = JSON.parse(serialized);

    console.log(serialized);
    console.log("Restored replica count:", restored.application.replicas.length);
}

function asynchronousNestedProcessing() {
    printTitle("Asynchronous processing of nested data");

    const batches = [
        {
            id: "BATCH-A",
            records: [
                { id: "A-1", value: 10 },
                { id: "A-2", value: 20 },
            ],
        },
        {
            id: "BATCH-B",
            records: [
                { id: "B-1", value: 30 },
                { id: "B-2", value: 40 },
            ],
        },
    ];

    return Promise.all(
        batches.map(
            (batch) =>
                new Promise((resolve) => {
                    setTimeout(() => {
                        const total = batch.records.reduce(
                            (sum, record) => sum + record.value,
                            0
                        );

                        resolve({
                            batchId: batch.id,
                            total,
                        });
                    }, 10);
                })
        )
    ).then((results) => {
        console.log("Asynchronous batch results:", results);
    });
}

async function main() {
    nestedArrays();
    nestedObjects();
    optionalChainingAndNullishCoalescing();
    mixedApplicationData();
    demonstratePathLookup();
    demonstrateRecursiveTraversal();
    demonstrateValidation();
    groupNestedData();
    demonstrateFlattening();
    demonstrateReferenceBehavior();
    inventoryCaseStudy();
    jsonRoundTrip();
    await asynchronousNestedProcessing();

    printTitle("Completed");
    console.log("Nested list and dictionary demonstrations completed.");
}

main().catch((error) => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
