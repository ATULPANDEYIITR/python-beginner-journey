"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");

class FileOperationError extends Error {
    constructor(message) {
        super(message);
        this.name = "FileOperationError";
    }
}

class FileStore {
    constructor(baseDirectory, options = {}) {
        this.baseDirectory = path.resolve(baseDirectory);
        this.encoding = options.encoding ?? "utf8";
        this.maxBytes = options.maxBytes ?? 5 * 1024 * 1024;
        this.auditLog = [];
    }

    async initialize() {
        await fs.mkdir(this.baseDirectory, { recursive: true });
    }

    safePath(filename) {
        if (typeof filename !== "string" || filename.trim() === "") {
            throw new FileOperationError("A valid filename is required.");
        }

        const target = path.resolve(this.baseDirectory, filename);
        const relative = path.relative(this.baseDirectory, target);

        if (relative === ".." || relative.startsWith(`..${path.sep}`)) {
            throw new FileOperationError("Path escapes the configured directory.");
        }

        return target;
    }

    validateContent(content) {
        if (typeof content !== "string") {
            throw new TypeError("Content must be a string.");
        }

        const bytes = Buffer.byteLength(content, this.encoding);

        if (bytes > this.maxBytes) {
            throw new FileOperationError(
                `Content exceeds the ${this.maxBytes} byte limit.`
            );
        }

        return bytes;
    }

    async write(filename, content) {
        return this.save(filename, content, "write");
    }

    async append(filename, content) {
        return this.save(filename, content, "append");
    }

    async save(filename, content, operation) {
        const bytes = this.validateContent(content);
        const target = this.safePath(filename);

        await fs.mkdir(path.dirname(target), { recursive: true });

        try {
            if (operation === "write") {
                await fs.writeFile(target, content, {
                    encoding: this.encoding,
                    flag: "w"
                });
            } else if (operation === "append") {
                await fs.writeFile(target, content, {
                    encoding: this.encoding,
                    flag: "a"
                });
            } else {
                throw new FileOperationError(`Unsupported operation: ${operation}`);
            }
        } catch (error) {
            if (error instanceof FileOperationError) {
                throw error;
            }

            throw new FileOperationError(
                `File operation failed: ${error.message}`
            );
        }

        const lineCount = content.length === 0
            ? 0
            : content.split("\n").length - (content.endsWith("\n") ? 1 : 0);

        const record = {
            operation,
            filename: path.relative(this.baseDirectory, target),
            bytes,
            lines: lineCount,
            timestamp: new Date().toISOString()
        };

        this.auditLog.push(record);

        return {
            path: target,
            ...record
        };
    }

    async appendLines(filename, lines) {
        if (!Array.isArray(lines)) {
            throw new TypeError("lines must be an array.");
        }

        const content = lines
            .map((line) => {
                if (typeof line !== "string") {
                    throw new TypeError("Every line must be a string.");
                }
                return line.replace(/\r?\n/g, "") + "\n";
            })
            .join("");

        return this.append(filename, content);
    }

    async read(filename) {
        const target = this.safePath(filename);

        try {
            return await fs.readFile(target, this.encoding);
        } catch (error) {
            throw new FileOperationError(
                `Unable to read ${filename}: ${error.message}`
            );
        }
    }

    async size(filename) {
        const target = this.safePath(filename);

        try {
            const statistics = await fs.stat(target);
            return statistics.size;
        } catch (error) {
            throw new FileOperationError(
                `Unable to inspect ${filename}: ${error.message}`
            );
        }
    }
}

async function demonstrate() {
    const temporaryDirectory = await fs.mkdtemp(
        path.join(process.cwd(), "file-writing-")
    );

    try {
        const store = new FileStore(temporaryDirectory);
        await store.initialize();

        await store.write(
            "logs/application.log",
            "Application started\n"
        );

        await store.append(
            "logs/application.log",
            "Configuration loaded\n"
        );

        await store.appendLines(
            "logs/application.log",
            [
                "Database connection established",
                "Worker process started",
                "Application ready"
            ]
        );

        const content = await store.read("logs/application.log");

        const expected =
            "Application started\n" +
            "Configuration loaded\n" +
            "Database connection established\n" +
            "Worker process started\n" +
            "Application ready\n";

        if (content !== expected) {
            throw new Error("File content validation failed.");
        }

        const size = await store.size("logs/application.log");

        if (size !== Buffer.byteLength(expected, "utf8")) {
            throw new Error("File size validation failed.");
        }

        try {
            await store.append("../outside.txt", "blocked\n");
            throw new Error("Path traversal was not rejected.");
        } catch (error) {
            if (!(error instanceof FileOperationError)) {
                throw error;
            }
        }

        try {
            await store.read("missing.txt");
            throw new Error("Missing-file access was not rejected.");
        } catch (error) {
            if (!(error instanceof FileOperationError)) {
                throw error;
            }
        }

        console.log("File content:");
        console.log(content);
        console.log("Audit records:");
        console.table(store.auditLog);
    } finally {
        await fs.rm(temporaryDirectory, {
            recursive: true,
            force: true
        });
    }
}

demonstrate().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});
