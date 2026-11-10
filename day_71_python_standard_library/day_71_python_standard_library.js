"use strict";

/*
 * Python Standard Library: Complementary JavaScript Engineering Model
 *
 * Node.js built-in modules provide comparable capabilities:
 * events, filesystem access, cryptography, streams, worker threads,
 * asynchronous operations, validation and structured persistence.
 *
 * Requirements: Node.js 18+
 * Dependencies: None.
 */

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { EventEmitter } = require("node:events");
const { Worker, isMainThread, parentPort, workerData } =
    require("node:worker_threads");
const { performance } = require("node:perf_hooks");
const { pipeline } = require("node:stream/promises");
const { Readable, Transform, Writable } = require("node:stream");
const { setTimeout: delay } = require("node:timers/promises");
const os = require("node:os");

const Status = Object.freeze({
    PENDING: "pending",
    RUNNING: "running",
    COMPLETED: "completed",
    FAILED: "failed"
});

const Priority = Object.freeze({
    LOW: 1,
    NORMAL: 2,
    HIGH: 3,
    CRITICAL: 4
});

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class Job {
    constructor({
        id,
        name,
        priority = Priority.NORMAL,
        metadata = {}
    }) {
        if (!Number.isSafeInteger(id) || id <= 0) {
            throw new ValidationError("Job ID must be positive");
        }

        if (typeof name !== "string" || !name.trim()) {
            throw new ValidationError("Job name is required");
        }

        if (!Object.values(Priority).includes(priority)) {
            throw new ValidationError("Invalid priority");
        }

        if (
            metadata === null ||
            typeof metadata !== "object" ||
            Array.isArray(metadata)
        ) {
            throw new ValidationError("Metadata must be an object");
        }

        this.id = id;
        this.name = name.trim();
        this.priority = priority;
        this.metadata = structuredClone(metadata);
        this.status = Status.PENDING;
        this.attempts = 0;
        this.createdAt = new Date().toISOString();
    }
}

class JobRegistry extends EventEmitter {
    #jobs = new Map();
    #allowedTransitions = new Map([
        [Status.PENDING, new Set([Status.RUNNING])],
        [Status.RUNNING, new Set([
            Status.COMPLETED,
            Status.FAILED
        ])],
        [Status.FAILED, new Set([Status.PENDING])],
        [Status.COMPLETED, new Set()]
    ]);

    add(job) {
        if (!(job instanceof Job)) {
            throw new ValidationError("Expected a Job instance");
        }

        if (this.#jobs.has(job.id)) {
            throw new ValidationError("Duplicate job ID");
        }

        this.#jobs.set(job.id, job);

        this.emit("job:created", this.snapshot(job));
    }

    transition(id, nextStatus) {
        const job = this.#jobs.get(id);

        if (!job) {
            throw new Error(`Job ${id} does not exist`);
        }

        const allowed = this.#allowedTransitions.get(job.status);

        if (!allowed.has(nextStatus)) {
            throw new ValidationError(
                `Invalid transition ${job.status} -> ${nextStatus}`
            );
        }

        const previousStatus = job.status;
        job.status = nextStatus;

        if (nextStatus === Status.RUNNING) {
            job.attempts += 1;
        }

        this.emit("job:transitioned", {
            id,
            previousStatus,
            nextStatus,
            attempts: job.attempts
        });

        return this.snapshot(job);
    }

    snapshot(job) {
        return structuredClone(job);
    }

    list() {
        return [...this.#jobs.values()]
            .map(job => this.snapshot(job))
            .sort((a, b) =>
                b.priority - a.priority || a.id - b.id
            );
    }

    statistics() {
        const counts = new Map();

        for (const job of this.#jobs.values()) {
            counts.set(
                job.status,
                (counts.get(job.status) || 0) + 1
            );
        }

        return Object.fromEntries(counts);
    }
}

class RetryPolicy {
    constructor(maxAttempts = 3, initialDelay = 100) {
        if (
            !Number.isInteger(maxAttempts) ||
            maxAttempts < 1 ||
            initialDelay < 0
        ) {
            throw new ValidationError("Invalid retry configuration");
        }

        this.maxAttempts = maxAttempts;
        this.initialDelay = initialDelay;
    }

    async execute(operation) {
        let lastError;

        for (let attempt = 1; attempt <= this.maxAttempts; attempt++) {
            try {
                return await operation(attempt);
            } catch (error) {
                lastError = error;

                if (attempt === this.maxAttempts) {
                    break;
                }

                await delay(
                    this.initialDelay * 2 ** (attempt - 1)
                );
            }
        }

        throw lastError;
    }
}

class FileRepository {
    constructor(directory) {
        this.directory = path.resolve(directory);
        fs.mkdirSync(this.directory, { recursive: true });
    }

    async writeJson(filename, data) {
        if (
            typeof filename !== "string" ||
            filename !== path.basename(filename) ||
            !filename.endsWith(".json")
        ) {
            throw new ValidationError("Invalid filename");
        }

        const destination = path.join(this.directory, filename);
        const temporary = `${destination}.${crypto.randomUUID()}.tmp`;

        try {
            await fs.promises.writeFile(
                temporary,
                JSON.stringify(data, null, 2),
                { encoding: "utf8", flag: "wx" }
            );

            await fs.promises.rename(temporary, destination);
        } catch (error) {
            await fs.promises.rm(temporary, { force: true });
            throw error;
        }
    }

    async readJson(filename) {
        if (
            typeof filename !== "string" ||
            filename !== path.basename(filename)
        ) {
            throw new ValidationError("Invalid filename");
        }

        const content = await fs.promises.readFile(
            path.join(this.directory, filename),
            "utf8"
        );

        return JSON.parse(content);
    }
}

function calculateDigest(data) {
    return crypto
        .createHash("sha256")
        .update(data)
        .digest("hex");
}

function createStreamProcessor() {
    const transform = new Transform({
        objectMode: true,

        transform(chunk, encoding, callback) {
            try {
                if (!Number.isFinite(chunk)) {
                    throw new ValidationError("Invalid stream value");
                }

                callback(null, chunk * chunk);
            } catch (error) {
                callback(error);
            }
        }
    });

    const output = [];

    const sink = new Writable({
        objectMode: true,

        write(chunk, encoding, callback) {
            output.push(chunk);
            callback();
        }
    });

    return { transform, sink, output };
}

async function runStream(values) {
    const processor = createStreamProcessor();

    await pipeline(
        Readable.from(values),
        processor.transform,
        processor.sink
    );

    return processor.output;
}

async function processConcurrently(values, concurrency = 4) {
    if (
        !Number.isInteger(concurrency) ||
        concurrency < 1 ||
        concurrency > 64
    ) {
        throw new ValidationError("Invalid concurrency limit");
    }

    const results = new Array(values.length);
    let nextIndex = 0;

    async function worker() {
        while (true) {
            const index = nextIndex++;

            if (index >= values.length) {
                return;
            }

            await delay(10);
            results[index] = values[index] ** 2;
        }
    }

    await Promise.all(
        Array.from(
            { length: Math.min(concurrency, values.length) },
            () => worker()
        )
    );

    return results;
}

function runWorkerThread(value) {
    return new Promise((resolve, reject) => {
        const worker = new Worker(__filename, {
            workerData: { operation: "square", value }
        });

        worker.once("message", resolve);
        worker.once("error", reject);

        worker.once("exit", code => {
            if (code !== 0) {
                reject(new Error(`Worker exited with code ${code}`));
            }
        });
    });
}

function validateRecord(record) {
    const errors = [];

    if (!Number.isSafeInteger(record.id) || record.id <= 0) {
        errors.push("Invalid identifier");
    }

    if (typeof record.name !== "string" || !record.name.trim()) {
        errors.push("Invalid name");
    }

    if (!Object.values(Priority).includes(record.priority)) {
        errors.push("Invalid priority");
    }

    return {
        valid: errors.length === 0,
        errors
    };
}

async function runTests() {
    const assert = require("node:assert/strict");

    assert.equal(
        validateRecord({
            id: 1,
            name: "Test",
            priority: Priority.HIGH
        }).valid,
        true
    );

    assert.equal(calculateDigest("abc").length, 64);

    assert.deepEqual(
        await runStream([1, 2, 3]),
        [1, 4, 9]
    );

    assert.deepEqual(
        await processConcurrently([2, 3]),
        [4, 9]
    );

    const registry = new JobRegistry();
    const job = new Job({ id: 1, name: "Integration test" });

    registry.add(job);
    registry.transition(1, Status.RUNNING);
    registry.transition(1, Status.COMPLETED);

    assert.equal(
        registry.list()[0].status,
        Status.COMPLETED
    );

    assert.throws(
        () => registry.add(job),
        ValidationError
    );

    assert.throws(
        () => registry.transition(1, Status.RUNNING),
        ValidationError
    );

    console.log("All tests passed.");
}

async function main() {
    const outputDirectory = path.resolve("stdlib_js_output");

    const registry = new JobRegistry();

    registry.on("job:created", event => {
        console.log("EVENT job:created", event.id);
    });

    registry.on("job:transitioned", event => {
        console.log("EVENT job:transitioned", event);
    });

    registry.add(new Job({
        id: 101,
        name: "Process transaction records",
        priority: Priority.HIGH,
        metadata: { department: "finance" }
    }));

    registry.add(new Job({
        id: 102,
        name: "Generate operational report",
        priority: Priority.NORMAL
    }));

    registry.transition(101, Status.RUNNING);
    registry.transition(101, Status.COMPLETED);

    const repository = new FileRepository(outputDirectory);

    await repository.writeJson("jobs.json", {
        generatedAt: new Date().toISOString(),
        jobs: registry.list(),
        statistics: registry.statistics()
    });

    const saved = await repository.readJson("jobs.json");

    const results = {
        platform: process.platform,
        architecture: os.arch(),
        nodeVersion: process.version,
        digest: calculateDigest("standard library"),
        streamResults: await runStream([1, 2, 3, 4]),
        concurrentResults: await processConcurrently([2, 4, 6]),
        workerThreadResult: await runWorkerThread(12),
        savedJobCount: saved.jobs.length
    };

    const retryPolicy = new RetryPolicy(3, 50);
    let executions = 0;

    results.retryResult = await retryPolicy.execute(async () => {
        executions++;

        if (executions < 2) {
            throw new Error("Temporary failure");
        }

        return "Operation completed";
    });

    results.executionTime = performance.now();

    console.log("\nRESULTS");
    console.log(JSON.stringify(results, null, 2));

    await runTests();
}

if (!isMainThread) {
    if (
        workerData.operation === "square" &&
        Number.isFinite(workerData.value)
    ) {
        parentPort.postMessage(workerData.value ** 2);
    } else {
        throw new Error("Unsupported worker operation");
    }
} else if (require.main === module) {
    main().catch(error => {
        console.error("Execution failed:", error);
        process.exitCode = 1;
    });
}

module.exports = {
    Job,
    JobRegistry,
    RetryPolicy,
    FileRepository,
    validateRecord,
    calculateDigest,
    processConcurrently
};
