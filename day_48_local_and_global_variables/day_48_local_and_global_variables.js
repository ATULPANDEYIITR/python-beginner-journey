"use strict";

/*
 * Local and Global Variables in JavaScript
 * Run with Node.js or in a browser console.
 *
 * Demonstrates lexical scope, var/let/const, closures, module/global
 * environments, asynchronous callbacks, shadowing, and encapsulation.
 */

// Top-level let and const in a Node.js CommonJS module are module-scoped.
// They do not automatically become properties of globalThis.
const applicationConfig = Object.freeze({
    name: "Inventory Control",
    currency: "INR",
    maxRetries: 3
});

let processedOrders = 0;

function demonstrateFunctionScope() {
    var functionScoped = "Visible throughout this function";
    let blockScoped = "Visible inside this block";
    const fixedReference = { status: "active" };

    if (true) {
        var declaredWithVar = "var escapes the block";
        let declaredWithLet = "let remains in the block";
        const declaredWithConst = "const remains in the block";

        console.log(declaredWithLet);
        console.log(declaredWithConst);
    }

    console.log(functionScoped);
    console.log(blockScoped);
    console.log(declaredWithVar);

    try {
        console.log(declaredWithLet);
    } catch (error) {
        console.log(`Expected block-scope error: ${error.name}`);
    }

    // const prevents rebinding the reference, not object mutation.
    fixedReference.status = "updated";
    console.log(fixedReference);
}

function demonstrateShadowing() {
    const status = "module operation";

    function processShipment() {
        const status = "shipment operation";
        console.log(`Inner status: ${status}`);
    }

    processShipment();
    console.log(`Outer status: ${status}`);
}

function incrementOrderCount() {
    processedOrders += 1;
    return processedOrders;
}

function demonstrateTemporalDeadZone() {
    try {
        // The binding exists but cannot be accessed before initialization.
        console.log(customerRegion);
    } catch (error) {
        console.log(`Expected temporal dead zone error: ${error.name}`);
    }

    let customerRegion = "Uttar Pradesh";
    console.log(`Initialized region: ${customerRegion}`);
}

function createStockReservation(initialStock) {
    if (!Number.isInteger(initialStock) || initialStock < 0) {
        throw new RangeError("Initial stock must be a non-negative integer.");
    }

    // The closure retains private access to remainingStock after this
    // outer function returns.
    let remainingStock = initialStock;

    return Object.freeze({
        reserve(quantity) {
            if (!Number.isInteger(quantity) || quantity <= 0) {
                throw new RangeError("Quantity must be a positive integer.");
            }

            if (quantity > remainingStock) {
                throw new Error("Insufficient stock.");
            }

            remainingStock -= quantity;
            return remainingStock;
        },

        getRemainingStock() {
            return remainingStock;
        }
    });
}

function createPriceCalculator(taxRate) {
    if (!Number.isFinite(taxRate) || taxRate < 0 || taxRate > 1) {
        throw new RangeError("Tax rate must be between zero and one.");
    }

    return function calculateTotal(price, quantity) {
        if (!Number.isFinite(price) || price < 0) {
            throw new RangeError("Price must be finite and non-negative.");
        }

        if (!Number.isInteger(quantity) || quantity < 0) {
            throw new RangeError("Quantity must be a non-negative integer.");
        }

        const subtotal = price * quantity;
        return Number((subtotal * (1 + taxRate)).toFixed(2));
    };
}

function demonstrateIndependentClosures() {
    const warehouseA = createStockReservation(100);
    const warehouseB = createStockReservation(50);

    warehouseA.reserve(20);

    // Each closure owns a separate lexical environment.
    console.log(`Warehouse A: ${warehouseA.getRemainingStock()}`);
    console.log(`Warehouse B: ${warehouseB.getRemainingStock()}`);
}

function demonstrateGlobalEnvironment() {
    console.log(`Config: ${applicationConfig.name}`);
    console.log(`globalThis.processedOrders exists: ${
        Object.hasOwn(globalThis, "processedOrders")
    }`);

    // Explicit globalThis properties are different from top-level
    // lexical bindings. Avoid adding application state to globalThis
    // because it increases collision and accidental mutation risks.
    globalThis.inventoryDiagnostics = {
        checkedAt: new Date().toISOString(),
        orders: processedOrders
    };

    console.log(globalThis.inventoryDiagnostics);
    delete globalThis.inventoryDiagnostics;
}

async function demonstrateAsynchronousScope() {
    let currentBatch = "BATCH-001";

    const task = new Promise((resolve) => {
        setTimeout(() => {
            // The callback retains access to currentBatch through closure.
            resolve(`Completed ${currentBatch}`);
        }, 10);
    });

    currentBatch = "BATCH-002";
    console.log(await task);

    // The callback reads the current binding value when it executes.
    // To preserve the original value, capture it in a separate const.
    const capturedBatch = currentBatch;

    const stableTask = new Promise((resolve) => {
        setTimeout(() => resolve(`Captured ${capturedBatch}`), 10);
    });

    currentBatch = "BATCH-003";
    console.log(await stableTask);
}

function demonstrateLoopClosures() {
    const callbacksUsingVar = [];
    const callbacksUsingLet = [];

    for (var index = 0; index < 3; index++) {
        callbacksUsingVar.push(() => index);
    }

    for (let index = 0; index < 3; index++) {
        callbacksUsingLet.push(() => index);
    }

    console.log("var callbacks:", callbacksUsingVar.map(callback => callback()));
    console.log("let callbacks:", callbacksUsingLet.map(callback => callback()));
}

async function main() {
    console.log(`=== ${applicationConfig.name} ===`);

    demonstrateFunctionScope();
    demonstrateShadowing();
    demonstrateTemporalDeadZone();

    console.log(`Processed orders: ${incrementOrderCount()}`);
    console.log(`Processed orders: ${incrementOrderCount()}`);

    const reserve = createStockReservation(75);
    console.log(`Stock after reservation: ${reserve.reserve(25)}`);

    try {
        reserve.reserve(100);
    } catch (error) {
        console.log(`Reservation rejected: ${error.message}`);
    }

    const calculateTotal = createPriceCalculator(0.18);
    console.log(`Order total: ₹${calculateTotal(1250, 3).toFixed(2)}`);

    demonstrateIndependentClosures();
    demonstrateGlobalEnvironment();
    demonstrateLoopClosures();
    await demonstrateAsynchronousScope();
}

main().catch(error => {
    console.error("Application failed:", error.message);
    process.exitCode = 1;
});
