"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const os = require("node:os");
const { EventEmitter } = require("node:events");

class FileOperationError extends Error {
    constructor(message, options = {}) {
        super(message, options);
        this.name = this.constructor.name;
    }
}

class ValidationError extends FileOperationError {}
class FileFormatError extends FileOperationError {}
class StorageError extends FileOperationError {}
class NotFoundError extends FileOperationError {}

const TaskStatus = Object.freeze({
    PENDING: "pending",
    COMPLETED: "completed",
    FAILED: "failed"
});

class Task {
    constructor({ id, title, priority, status = TaskStatus.PENDING }) {
        if (!Number.isSafeInteger(id) || id <= 0) {
            throw new ValidationError("Task ID must be a positive integer.");
        }

        if (typeof title !== "string" || !title.trim()) {
            throw new ValidationError("Task title cannot be empty.");
        }

        if (!Number.isInteger(priority) || priority < 1 || priority > 5) {
            throw new ValidationError("Priority must be between 1 and 5.");
        }

        if (!Object.values(TaskStatus).includes(status)) {
            throw new ValidationError("Invalid task status.");
        }

        this.id = id;
        this.title = title.trim();
        this.priority = priority;
        this.status = status;
        this.createdAt = new Date().toISOString();
    }
}

class AsyncFileStore {
    constructor(directory) {
        this.directory = path.resolve(directory);
        this.filePath = path.join(this.directory, "tasks.json");
        this.locked = false;
        this.queue = [];
    }

    async initialize() {
        await fs.mkdir(this.directory, { recursive: true });
    }

    async withLock(operation) {
        const previous = this.queue.reduce(
            (_, current) => current,
            Promise.resolve()
        );

        let release;
        const current = new Promise(resolve => {
            release = resolve;
        });

        this.queue.push(current);
        await previous;

        try {
            return await operation();
        } finally {
            release();
            this.queue.shift();
        }
    }

    async read() {
        try {
            const content = await fs.readFile(this.filePath, "utf8");
            const data = JSON.parse(content);

            if (!Array.isArray(data)) {
                throw new FileFormatError("JSON root must be an array.");
            }

            const ids = new Set();

            return data.map(item => {
                if (
                    !Number.isSafeInteger(item.id) ||
                    typeof item.title !== "string" ||
                    !Number.isInteger(item.priority) ||
                    !Object.values(TaskStatus).includes(item.status)
                ) {
                    throw new FileFormatError("Invalid task record.");
                }

                if (ids.has(item.id)) {
                    throw new FileFormatError("Duplicate task ID.");
                }

                ids.add(item.id);
                return item;
            });
        } catch (error) {
            if (error.code === "ENOENT") {
                return [];
            }

            if (error instanceof FileOperationError) {
                throw error;
            }

            if (error instanceof SyntaxError) {
                throw new FileFormatError(
                    `Malformed JSON: ${error.message}`,
                    { cause: error }
                );
            }

            throw new StorageError(
                `Read failed: ${error.message}`,
                { cause: error }
            );
        }
    }

    async write(records) {
        const temporary = path.join(
            this.directory,
            `.tasks-${crypto.randomUUID()}.tmp`
        );

        try {
            const content = JSON.stringify(records, null, 2);

            await fs.writeFile(temporary, content, {
                encoding: "utf8",
                flag: "wx",
                mode: 0o600
            });

            await fs.rename(temporary, this.filePath);
        } catch (error) {
            await fs.rm(temporary, { force: true }).catch(() => {});

            throw new StorageError(
                `Write failed: ${error.message}`,
                { cause: error }
            );
        }
    }

    async add(task) {
        return this.withLock(async () => {
            const records = await this.read();

            if (records.some(item => item.id === task.id)) {
                throw new ValidationError("Duplicate task ID.");
            }

            records.push(task);
            await this.write(records);
            return task;
        });
    }

    async changeStatus(id, status) {
        if (!Object.values(TaskStatus).includes(status)) {
            throw new ValidationError("Invalid status.");
        }

        return this.withLock(async () => {
            const records = await this.read();
            const record = records.find(item => item.id === id);

            if (!record) {
                throw new NotFoundError(`Task ${id} does not exist.`);
            }

            record.status = status;
            await this.write(records);
            return record;
        });
    }

    async remove(id) {
        return this.withLock(async () => {
            const records = await this.read();
            const updated = records.filter(item => item.id !== id);

            if (updated.length === records.length) {
                return false;
            }

            await this.write(updated);
            return true;
        });
    }
}

class FileEventProcessor extends EventEmitter {
    constructor(store) {
        super();
        this.store = store;
        this.on("task-added", task => {
            console.log(`Event: task ${task.id} added`);
        });

        this.on("task-failed", error => {
            console.error(`Event: ${error.message}`);
        });
    }

    async submit(taskData) {
        try {
            const task = new Task(taskData);
            await this.store.add(task);
            this.emit("task-added", task);
            return task;
        } catch (error) {
            this.emit("task-failed", error);
            throw error;
        }
    }
}

async function readLogFile(filePath) {
    try {
        const content = await fs.readFile(filePath, "utf8");
        return content.split(/\r?\n/).filter(Boolean);
    } catch (error) {
        if (error.code === "ENOENT") {
            throw new NotFoundError(`Log file not found: ${filePath}`);
        }

        if (error.code === "EISDIR") {
            throw new FileFormatError("Expected a file, received a directory.");
        }

        throw new StorageError(
            `Log read failed: ${error.message}`,
            { cause: error }
        );
    }
}

async function calculateHash(filePath) {
    const hash = crypto.createHash("sha256");

    try {
        const handle = await fs.open(filePath, "r");

        try {
            const stream = handle.createReadStream();
            for await (const chunk of stream) {
                hash.update(chunk);
            }
        } finally {
            await handle.close().catch(() => {});
        }

        return hash.digest("hex");
    } catch (error) {
        throw new StorageError(
            `Hash calculation failed: ${error.message}`,
            { cause: error }
        );
    }
}

async function writeAuditLog(filePath, event) {
    const line = JSON.stringify({
        timestamp: new Date().toISOString(),
        event
    }) + os.EOL;

    await fs.appendFile(filePath, line, {
        encoding: "utf8",
        mode: 0o600
    });
}

async function run() {
    const directory = await fs.mkdtemp(
        path.join(os.tmpdir(), "file-practice-")
    );

    const store = new AsyncFileStore(path.join(directory, "data"));
    await store.initialize();

    const processor = new FileEventProcessor(store);

    try {
        await processor.submit({
            id: 1,
            title: "Inspect application logs",
            priority: 2
        });

        await processor.submit({
            id: 2,
            title: "Create encrypted backup",
            priority: 1
        });

        await store.changeStatus(1, TaskStatus.COMPLETED);

        // Promise.allSettled preserves individual failure information.
        const results = await Promise.allSettled([
            processor.submit({
                id: 3,
                title: "Validate database exports",
                priority: 3
            }),
            processor.submit({
                id: 1,
                title: "Duplicate identifier",
                priority: 2
            })
        ]);

        for (const result of results) {
            if (result.status === "rejected") {
                console.log("Rejected:", result.reason.message);
            }
        }

        const records = await store.read();
        console.log("\nStored records:");
        console.log(JSON.stringify(records, null, 2));

        const auditPath = path.join(directory, "audit.jsonl");

        await writeAuditLog(auditPath, "task-created");
        await writeAuditLog(auditPath, "task-completed");

        console.log("\nAudit events:");
        console.log((await readLogFile(auditPath)).join("\n"));

        console.log("\nSHA-256:", await calculateHash(auditPath));

        console.log("\nTests:");

        if (records.length !== 3) {
            throw new Error("Unexpected record count.");
        }

        if (records.find(item => item.id === 1).status !== "completed") {
            throw new Error("Status update failed.");
        }

        try {
            await store.changeStatus(999, TaskStatus.COMPLETED);
            throw new Error("Missing task should have failed.");
        } catch (error) {
            if (!(error instanceof NotFoundError)) {
                throw error;
            }
        }

        console.log("All tests passed.");
    } finally {
        await fs.rm(directory, {
            recursive: true,
            force: true
        });
    }
}

run().catch(error => {
    console.error(`${error.name}: ${error.message}`);
    process.exitCode = 1;
});
