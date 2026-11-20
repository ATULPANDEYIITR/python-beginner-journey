"use strict";

const { EventEmitter } = require("node:events");
const crypto = require("node:crypto");
const fs = require("node:fs/promises");

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class RepositoryEvent {
    constructor(type, repositoryId, timestamp = new Date()) {
        this.type = type;
        this.repositoryId = repositoryId;
        this.timestamp = timestamp.toISOString();
    }
}

class Repository {
    // Static class attributes shared across all instances.
    static organization = "OpenSystems";
    static maximumRepositories = 100;
    static defaultVisibility = "private";
    static supportedLanguages = Object.freeze([
        "JavaScript",
        "Python",
        "Java",
        "C++"
    ]);

    static #repositories = new Map();
    static #creationLock = Promise.resolve();

    constructor(name, owner, visibility = Repository.defaultVisibility) {
        Repository.validateText(name, "Repository name");
        Repository.validateText(owner, "Owner");

        if (!["public", "private", "internal"].includes(visibility)) {
            throw new ValidationError("Invalid visibility.");
        }

        this.id = crypto.randomUUID();
        this.name = name;
        this.owner = owner;
        this.visibility = visibility;

        // Instance attributes.
        this.commitCount = 0;
        this.active = true;
        this.createdAt = new Date().toISOString();
    }

    static validateText(value, field) {
        if (typeof value !== "string" || value.trim().length === 0) {
            throw new ValidationError(`${field} cannot be empty.`);
        }
    }

    // Serialize creation operations to avoid asynchronous race conditions.
    static async create(name, owner, visibility) {
        const operation = Repository.#creationLock.then(() => {
            Repository.validateText(name, "Repository name");

            if (Repository.#repositories.has(name)) {
                throw new ValidationError("Duplicate repository.");
            }

            if (
                Repository.#repositories.size >=
                Repository.maximumRepositories
            ) {
                throw new ValidationError("Repository capacity reached.");
            }

            const repository = new Repository(name, owner, visibility);
            Repository.#repositories.set(name, repository);

            return repository;
        });

        Repository.#creationLock = operation.then(
            () => undefined,
            () => undefined
        );

        return operation;
    }

    static getByName(name) {
        return Repository.#repositories.get(name) ?? null;
    }

    static getAll() {
        return [...Repository.#repositories.values()];
    }

    static getStatistics() {
        return Object.freeze({
            organization: Repository.organization,
            count: Repository.#repositories.size,
            maximum: Repository.maximumRepositories,
            repositories: Repository.getAll().map(repo => repo.name)
        });
    }

    static setDefaultVisibility(value) {
        if (!["public", "private", "internal"].includes(value)) {
            throw new ValidationError("Invalid default visibility.");
        }

        Repository.defaultVisibility = value;
    }

    addCommit() {
        if (!this.active) {
            throw new ValidationError("Repository is inactive.");
        }

        this.commitCount += 1;
        return this.commitCount;
    }

    close() {
        this.active = false;
    }

    describe() {
        return {
            id: this.id,
            name: this.name,
            owner: this.owner,
            visibility: this.visibility,
            commitCount: this.commitCount,
            organization: this.organization
        };
    }
}

class EnterpriseRepository extends Repository {
    static organization = "EnterpriseSystems";
    static maximumRepositories = 50;
    static complianceRequired = true;

    constructor(name, owner) {
        super(name, owner, "internal");
        this.auditEnabled = true;
    }
}

class RepositoryManager extends EventEmitter {
    static eventPrefix = "repository";

    constructor() {
        super();

        this.metrics = {
            created: 0,
            commits: 0,
            closed: 0
        };
    }

    async createRepository(name, owner, visibility) {
        const repository = await Repository.create(
            name,
            owner,
            visibility
        );

        this.metrics.created++;

        this.emit(
            "repository:created",
            new RepositoryEvent("created", repository.id)
        );

        return repository;
    }

    addCommit(repository) {
        const count = repository.addCommit();
        this.metrics.commits++;

        this.emit(
            "repository:commit",
            new RepositoryEvent("commit", repository.id)
        );

        return count;
    }

    closeRepository(repository) {
        if (!repository.active) {
            return false;
        }

        repository.close();
        this.metrics.closed++;

        this.emit(
            "repository:closed",
            new RepositoryEvent("closed", repository.id)
        );

        return true;
    }
}

class Configuration {
    static environment = "development";

    static limits = Object.freeze({
        requestTimeoutMs: 5000,
        maximumConnections: 20
    });

    static setEnvironment(environment) {
        if (!["development", "testing", "production"].includes(environment)) {
            throw new ValidationError("Invalid environment.");
        }

        Configuration.environment = environment;
    }
}

async function saveAuditLog(events, filePath) {
    // Avoid arbitrary object serialization and use a controlled event schema.
    const content = events
        .map(event => JSON.stringify(event))
        .join("\n");

    await fs.writeFile(filePath, content + "\n", {
        encoding: "utf8",
        mode: 0o600,
        flag: "w"
    });
}

async function main() {
    console.log("CLASS ATTRIBUTES: JAVASCRIPT DEMONSTRATION");

    const manager = new RepositoryManager();
    const events = [];

    manager.on("repository:created", event => {
        events.push(event);
        console.log("Created:", event.repositoryId);
    });

    manager.on("repository:commit", event => {
        events.push(event);
        console.log("Commit recorded:", event.repositoryId);
    });

    manager.on("repository:closed", event => {
        events.push(event);
        console.log("Closed:", event.repositoryId);
    });

    const first = await manager.createRepository(
        "payment-platform",
        "finance-team"
    );

    const second = await manager.createRepository(
        "analytics-platform",
        "data-team",
        "public"
    );

    manager.addCommit(first);
    manager.addCommit(first);
    manager.addCommit(second);

    console.log("\nINSTANCE ATTRIBUTES");
    console.log(first.describe());
    console.log(second.describe());

    console.log("\nCLASS ATTRIBUTES");
    console.log("Organization:", Repository.organization);
    console.log("Maximum:", Repository.maximumRepositories);
    console.log("Languages:", Repository.supportedLanguages);

    // An instance property shadows the inherited static class property
    // only on that instance; it does not modify the constructor.
    first.organization = "LocalOrganization";

    console.log("First instance:", first.organization);
    console.log("Second instance:", second.organization);
    console.log("Class value:", Repository.organization);

    console.log("\nSTATIC INHERITANCE");

    const enterprise = await EnterpriseRepository.create(
        "secure-infrastructure",
        "security-team"
    );

    console.log("Standard organization:", Repository.organization);
    console.log("Enterprise organization:", EnterpriseRepository.organization);
    console.log("Enterprise audit:", enterprise.auditEnabled);
    console.log("Enterprise compliance:", EnterpriseRepository.complianceRequired);

    console.log("\nCLASS-LEVEL CONFIGURATION");

    Repository.setDefaultVisibility("internal");
    Configuration.setEnvironment("production");

    const third = await manager.createRepository(
        "monitoring-platform",
        "operations-team"
    );

    console.log("Default visibility:", third.visibility);
    console.log("Environment:", Configuration.environment);
    console.log("Shared limits:", Configuration.limits);

    console.log("\nVALIDATION");

    try {
        await manager.createRepository("", "owner");
    } catch (error) {
        console.log(error.name, error.message);
    }

    try {
        await manager.createRepository("payment-platform", "another-owner");
    } catch (error) {
        console.log(error.name, error.message);
    }

    manager.closeRepository(first);

    try {
        manager.addCommit(first);
    } catch (error) {
        console.log("Inactive repository:", error.message);
    }

    console.log("\nCLASS STATISTICS");
    console.log(Repository.getStatistics());

    console.log("\nEVENT METRICS");
    console.log(manager.metrics);

    // The event log uses a local, fixed filename.
    await saveAuditLog(events, "class_attributes_audit.jsonl");

    console.log("\nAudit log written successfully.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
