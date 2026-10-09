"use strict";

const { EventEmitter } = require("node:events");
const { writeFile, readFile, mkdtemp, rm } = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const assert = require("node:assert/strict");

class WorkflowStore extends EventEmitter {
    constructor() {
        super();
        this.items = new Map();
        this.byCategory = new Map();
        this.completed = new Set();
        this.activity = [];
        this.revision = 0;
    }

    add({ id, title, category, priority, tags = [], dependencies = [] }) {
        if (typeof id !== "string" || id.trim() === "") {
            throw new TypeError("A non-empty string ID is required.");
        }
        if (this.items.has(id)) {
            throw new Error(`Duplicate item ID: ${id}`);
        }
        if (!Number.isInteger(priority) || priority < 1 || priority > 5) {
            throw new RangeError("Priority must be an integer from 1 to 5.");
        }
        if (typeof title !== "string" || title.trim() === "") {
            throw new TypeError("A non-empty title is required.");
        }
        if (!Array.isArray(tags) || !Array.isArray(dependencies)) {
            throw new TypeError("Tags and dependencies must be arrays.");
        }

        for (const dependency of dependencies) {
            if (!this.items.has(dependency)) {
                throw new Error(`Unknown dependency: ${dependency}`);
            }
        }

        const item = {
            id,
            title,
            category,
            priority,
            tags: new Set(tags),
            dependencies: new Set(dependencies),
            status: "pending",
        };

        this.items.set(id, item);

        if (!this.byCategory.has(category)) {
            this.byCategory.set(category, new Set());
        }
        this.byCategory.get(category).add(id);

        this.record("item.added", { id });
        return item;
    }

    record(type, payload) {
        const event = Object.freeze({
            revision: ++this.revision,
            type,
            payload: Object.freeze({ ...payload }),
            timestamp: new Date().toISOString(),
        });

        this.activity.push(event);
        this.emit(type, event);
    }

    readyItems() {
        return [...this.items.values()]
            .filter(item =>
                item.status === "pending" &&
                [...item.dependencies].every(id => this.completed.has(id))
            )
            .sort((a, b) => a.priority - b.priority || a.id.localeCompare(b.id));
    }

    transition(id, nextStatus) {
        const item = this.items.get(id);
        if (!item) {
            throw new Error(`Unknown item: ${id}`);
        }

        const allowed = {
            pending: new Set(["in_progress"]),
            in_progress: new Set(["completed"]),
            completed: new Set(),
        };

        if (!allowed[item.status].has(nextStatus)) {
            throw new Error(`Invalid transition: ${item.status} -> ${nextStatus}`);
        }

        if (nextStatus === "in_progress") {
            const blocked = [...item.dependencies]
                .filter(dependency => !this.completed.has(dependency));

            if (blocked.length > 0) {
                throw new Error(`Incomplete dependencies: ${blocked.join(", ")}`);
            }
        }

        const previousStatus = item.status;
        item.status = nextStatus;

        if (nextStatus === "completed") {
            this.completed.add(id);
        }

        this.record("item.transitioned", {
            id,
            previousStatus,
            nextStatus,
        });
    }

    searchByAllTags(requiredTags) {
        return [...this.items.values()].filter(item =>
            requiredTags.every(tag => item.tags.has(tag))
        );
    }

    commonItems(firstCategory, secondCategory) {
        const first = this.byCategory.get(firstCategory) ?? new Set();
        const second = this.byCategory.get(secondCategory) ?? new Set();
        return [...first].filter(id => second.has(id));
    }

    effortByCategory(hoursById) {
        const totals = new Map();

        for (const item of this.items.values()) {
            const hours = hoursById.get(item.id) ?? 0;

            if (!Number.isFinite(hours) || hours < 0) {
                throw new RangeError(`Invalid effort for ${item.id}`);
            }

            totals.set(
                item.category,
                (totals.get(item.category) ?? 0) + hours
            );
        }

        return totals;
    }

    serialize() {
        return {
            revision: this.revision,
            items: [...this.items.values()].map(item => ({
                ...item,
                tags: [...item.tags].sort(),
                dependencies: [...item.dependencies].sort(),
            })),
            activity: this.activity,
        };
    }
}

async function demonstrateAsynchronousPersistence(store) {
    const directory = await mkdtemp(path.join(os.tmpdir(), "structure-demo-"));
    const filename = path.join(directory, "workflow.json");

    try {
        await writeFile(filename, JSON.stringify(store.serialize(), null, 2), {
            encoding: "utf8",
            flag: "wx",
        });

        const restored = JSON.parse(await readFile(filename, "utf8"));

        assert.equal(restored.items.length, store.items.size);
        console.log("Persisted and restored records:", restored.items.length);
        console.log("Stored event revision:", restored.revision);
    } finally {
        await rm(directory, { recursive: true, force: true });
    }
}

async function main() {
    const store = new WorkflowStore();

    store.on("item.transitioned", event => {
        console.log(
            `Event ${event.revision}: ${event.payload.id} ` +
            `${event.payload.previousStatus} -> ${event.payload.nextStatus}`
        );
    });

    store.add({
        id: "ETL-10",
        title: "Validate imported customer records",
        category: "data",
        priority: 1,
        tags: ["validation", "quality"],
    });

    store.add({
        id: "ETL-11",
        title: "Normalize customer identifiers",
        category: "database",
        priority: 2,
        tags: ["normalization", "quality"],
        dependencies: ["ETL-10"],
    });

    store.add({
        id: "ETL-12",
        title: "Publish quality dashboard",
        category: "analytics",
        priority: 1,
        tags: ["dashboard", "reporting"],
        dependencies: ["ETL-11"],
    });

    console.log(
        "Initially ready:",
        store.readyItems().map(item => item.id)
    );

    assert.throws(() => store.transition("ETL-11", "in_progress"), /Incomplete/);

    store.transition("ETL-10", "in_progress");
    store.transition("ETL-10", "completed");

    console.log(
        "Ready after validation:",
        store.readyItems().map(item => item.id)
    );

    store.transition("ETL-11", "in_progress");
    store.transition("ETL-11", "completed");

    store.transition("ETL-12", "in_progress");

    console.log(
        "Tagged items:",
        store.searchByAllTags(["quality"]).map(item => item.id)
    );

    console.log(
        "Shared category IDs:",
        store.commonItems("data", "database")
    );

    const hours = new Map([
        ["ETL-10", 2.5],
        ["ETL-11", 3],
        ["ETL-12", 4],
    ]);

    console.log("Effort totals:", Object.fromEntries(store.effortByCategory(hours)));

    await demonstrateAsynchronousPersistence(store);

    assert.throws(() => store.transition("ETL-10", "pending"), /Invalid transition/);
    assert.throws(() => store.add({
        id: "ETL-10",
        title: "Duplicate",
        category: "data",
        priority: 1,
    }), /Duplicate/);

    console.log("All workflow assertions passed.");
}

main().catch(error => {
    console.error("Workflow failed:", error.message);
    process.exitCode = 1;
});
