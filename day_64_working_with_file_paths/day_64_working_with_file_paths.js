"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");
const os = require("node:os");

class PathSecurityError extends Error {
    constructor(message) {
        super(message);
        this.name = "PathSecurityError";
    }
}

class FilePathManager {
    constructor(root) {
        this.root = path.resolve(root);
    }

    safePath(relativePath) {
        if (
            typeof relativePath !== "string" ||
            relativePath.length === 0 ||
            relativePath.includes("\0")
        ) {
            throw new PathSecurityError("Invalid path");
        }

        const candidate = path.resolve(this.root, relativePath);
        const relative = path.relative(this.root, candidate);

        if (
            relative === ".." ||
            relative.startsWith(`..${path.sep}`) ||
            path.isAbsolute(relative)
        ) {
            throw new PathSecurityError(
                `Path escapes managed root: ${relativePath}`
            );
        }

        return candidate;
    }

    async createDirectory(relativePath) {
        const directory = this.safePath(relativePath);
        await fs.mkdir(directory, { recursive: true });
        return directory;
    }

    async writeText(relativePath, content) {
        const file = this.safePath(relativePath);
        await fs.mkdir(path.dirname(file), { recursive: true });
        await fs.writeFile(file, content, "utf8");
        return file;
    }

    async inspect(relativePath) {
        const file = this.safePath(relativePath);

        try {
            const stats = await fs.stat(file);

            return {
                original: relativePath,
                normalized: file,
                kind: stats.isFile()
                    ? "file"
                    : stats.isDirectory()
                        ? "directory"
                        : "other"
            };
        } catch (error) {
            if (error.code === "ENOENT") {
                return {
                    original: relativePath,
                    normalized: file,
                    kind: "missing"
                };
            }
            throw error;
        }
    }

    async listFiles(relativePath = ".") {
        const directory = this.safePath(relativePath);
        const result = [];

        async function walk(current) {
            const entries = await fs.readdir(current, { withFileTypes: true });

            for (const entry of entries) {
                const full = path.join(current, entry.name);

                if (entry.isDirectory()) {
                    await walk(full);
                } else if (entry.isFile()) {
                    result.push(full);
                }
            }
        }

        const stats = await fs.stat(directory);
        if (!stats.isDirectory()) {
            throw new Error(`${directory} is not a directory`);
        }

        await walk(directory);
        return result.sort();
    }

    async extensionReport(relativePath = ".") {
        const files = await this.listFiles(relativePath);
        const counts = new Map();

        for (const file of files) {
            const extension = path.extname(file).toLowerCase() || "[no extension]";
            counts.set(extension, (counts.get(extension) || 0) + 1);
        }

        return Object.fromEntries(
            [...counts.entries()].sort(([a], [b]) => a.localeCompare(b))
        );
    }

    relativeToRoot(file) {
        return path.relative(this.root, path.resolve(file));
    }

    async copyFile(source, destination) {
        const sourcePath = this.safePath(source);
        const destinationPath = this.safePath(destination);

        const stats = await fs.stat(sourcePath);
        if (!stats.isFile()) {
            throw new Error(`Source is not a regular file: ${sourcePath}`);
        }

        await fs.mkdir(path.dirname(destinationPath), { recursive: true });
        await fs.copyFile(sourcePath, destinationPath);

        return destinationPath;
    }
}

async function demonstratePathSyntax() {
    console.log("Separator:", path.sep);
    console.log("Joined:", path.join("reports", "2026", "november", "report.csv"));
    console.log("Resolved:", path.resolve("reports", "2026", "report.csv"));
    console.log(
        "Parsed:",
        path.parse(path.join("reports", "2026", "report.csv"))
    );
    console.log(
        "Extension:",
        path.extname("reports/2026/november/report.csv")
    );
}

async function main() {
    await demonstratePathSyntax();

    const root = await fs.mkdtemp(path.join(os.tmpdir(), "path-demo-"));
    const manager = new FilePathManager(root);

    try {
        await manager.createDirectory("reports/2026/november");
        await manager.createDirectory("archive");

        await manager.writeText(
            "reports/2026/november/report.txt",
            "Quarterly operational report\n"
        );

        await manager.writeText(
            "reports/2026/november/data.csv",
            "id,value\n1,100\n2,250\n"
        );

        await manager.writeText(
            "archive/README",
            "Archived files are retained here.\n"
        );

        console.log("\nManaged root:", manager.root);

        for (const name of [
            "reports/2026/november/report.txt",
            "reports/2026/november",
            "missing.txt"
        ]) {
            console.log(await manager.inspect(name));
        }

        console.log("\nFiles:");
        for (const file of await manager.listFiles()) {
            console.log(" ", manager.relativeToRoot(file));
        }

        console.log("\nExtensions:", await manager.extensionReport());

        const copied = await manager.copyFile(
            "reports/2026/november/report.txt",
            "archive/report.txt"
        );

        console.log("Copied:", manager.relativeToRoot(copied));

        try {
            manager.safePath("../../outside.txt");
        } catch (error) {
            console.log("Blocked traversal:", error.message);
        }

        try {
            manager.safePath("reports/\0bad");
        } catch (error) {
            console.log("Blocked invalid path:", error.message);
        }

        const copiedInfo = await manager.inspect("archive/report.txt");
        console.assert(copiedInfo.kind === "file");

        const missingInfo = await manager.inspect("missing.txt");
        console.assert(missingInfo.kind === "missing");

        const report = await manager.extensionReport();
        console.assert(report[".csv"] === 1);

        console.log("\nPath workflow completed successfully.");
    } finally {
        await fs.rm(root, { recursive: true, force: true });
    }
}

main().catch((error) => {
    console.error("Fatal error:", error.message);
    process.exitCode = 1;
});
