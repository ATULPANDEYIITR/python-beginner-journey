"use strict";

const fs = require("node:fs/promises");

class ApplicationError extends Error {
    constructor(message, options = {}) {
        super(message, options);
        this.name = new.target.name;
    }
}

class ValidationError extends ApplicationError {}
class ConfigurationError extends ApplicationError {}
class StorageError extends ApplicationError {}

class UserRepository {
    constructor(filePath) {
        if (typeof filePath !== "string" || filePath.length === 0) {
            throw new ConfigurationError("A repository file path is required.");
        }

        this.filePath = filePath;
    }

    async save(user) {
        try {
            await fs.appendFile(
                this.filePath,
                `${user.id},${user.name},${user.email}\n`,
                "utf8"
            );
        } catch (error) {
            throw new StorageError(
                `Unable to save user to ${this.filePath}`,
                { cause: error }
            );
        }
    }
}

function validateUser(id, name, email) {
    if (!Number.isInteger(id)) {
        throw new ValidationError("id must be an integer.");
    }

    if (id <= 0) {
        throw new ValidationError("id must be greater than zero.");
    }

    if (typeof name !== "string" || name.trim().length === 0) {
        throw new ValidationError("name must be a non-empty string.");
    }

    if (typeof email !== "string" || !email.includes("@")) {
        throw new ValidationError("email must contain '@'.");
    }

    return Object.freeze({
        id,
        name: name.trim(),
        email: email.trim().toLowerCase()
    });
}

function parseInteger(value) {
    if (typeof value !== "string" || !/^-?\d+$/.test(value.trim())) {
        throw new ValidationError(`Invalid integer: ${String(value)}`);
    }

    return Number.parseInt(value.trim(), 10);
}

function divide(total, divisor) {
    if (!Number.isFinite(total) || !Number.isFinite(divisor)) {
        throw new ValidationError("Arguments must be finite numbers.");
    }

    if (divisor === 0) {
        throw new RangeError("divisor cannot be zero.");
    }

    return total / divisor;
}

function loadConfiguration(configuration) {
    const databaseUrl = configuration?.databaseUrl;

    if (typeof databaseUrl !== "string" || databaseUrl.trim() === "") {
        throw new ConfigurationError("databaseUrl is required.");
    }

    return databaseUrl.trim();
}

async function processUser(repository, id, name, email) {
    const user = validateUser(id, name, email);

    // The repository converts low-level filesystem errors into a domain error.
    await repository.save(user);

    return user;
}

async function demonstrateAsyncPropagation() {
    const repository = new UserRepository("users_demo_js.csv");

    try {
        await processUser(repository, 200, "Katherine Johnson", "KJ@Example.com");
        console.log("User saved successfully.");
    } catch (error) {
        if (error instanceof StorageError) {
            console.error(`Storage failure: ${error.message}`);
            console.error(`Original error: ${error.cause?.code ?? "unknown"}`);
        } else {
            throw error;
        }
    }
}

async function runTests() {
    const user = validateUser(1, "Ada", "ADA@EXAMPLE.COM");
    console.assert(user.email === "ada@example.com");

    try {
        validateUser(0, "Ada", "ada@example.com");
        throw new Error("Expected ValidationError.");
    } catch (error) {
        console.assert(error instanceof ValidationError);
    }

    try {
        divide(10, 0);
        throw new Error("Expected RangeError.");
    } catch (error) {
        console.assert(error instanceof RangeError);
    }

    try {
        parseInteger("abc");
        throw new Error("Expected ValidationError.");
    } catch (error) {
        console.assert(error instanceof ValidationError);
    }

    try {
        loadConfiguration({});
        throw new Error("Expected ConfigurationError.");
    } catch (error) {
        console.assert(error instanceof ConfigurationError);
    }
}

async function main() {
    console.log("Raising Exceptions Demonstration");

    try {
        const url = loadConfiguration({
            databaseUrl: "postgresql://localhost/example"
        });
        console.log(`Configuration accepted: ${url}`);
    } catch (error) {
        console.error(`Configuration failure: ${error.message}`);
    }

    try {
        await processUser(
            new UserRepository("users_demo_js.csv"),
            101,
            "Grace Hopper",
            "Grace@Example.com"
        );
        console.log("User workflow completed.");
    } catch (error) {
        console.error(`Application failure: ${error.message}`);
    }

    try {
        await processUser(
            new UserRepository("users_demo_js.csv"),
            -4,
            "Invalid User",
            "invalid@example.com"
        );
    } catch (error) {
        console.log(`Expected validation failure: ${error.message}`);
    }

    try {
        divide(25, 0);
    } catch (error) {
        console.log(`Expected arithmetic failure: ${error.message}`);
    }

    await demonstrateAsyncPropagation();
    await runTests();

    console.log("All exception assertions passed.");
}

main().catch((error) => {
    console.error(`Unhandled fatal error: ${error.message}`);
    process.exitCode = 1;
});
