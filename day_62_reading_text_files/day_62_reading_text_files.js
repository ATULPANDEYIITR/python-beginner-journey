"use strict";

const fs = require("node:fs");
const fsp = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const crypto = require("node:crypto");
const readline = require("node:readline");

class TextFileError extends Error {
    constructor(message) {
        super(message);
        this.name = "TextFileError";
    }
}

class TextFileValidationError extends TextFileError {
    constructor(message) {
        super(message);
        this.name = "TextFileValidationError";
    }
}

class TextFileReader {
    constructor({ maxBytes = 5 * 1024 * 1024 } = {}) {
        if (!Number.isInteger(maxBytes) || maxBytes <= 0) {
            throw new TextFileValidationError(
                "maxBytes must be a positive integer."
            );
        }

        this.maxBytes = maxBytes;
    }

    async validate(filePath) {
        let stats;

        try {
            stats = await fsp.stat(filePath);
        } catch (error) {
            throw new TextFileError(
                `Unable to access file: ${error.message}`
            );
        }

        if (!stats.isFile()) {
            throw new TextFileError(
                `Path is not a regular file: ${filePath}`
            );
        }

        if (stats.size > this.maxBytes) {
            throw new TextFileError(
                `File exceeds ${this.maxBytes} bytes.`
            );
        }

        return stats;
    }

    async read(filePath) {
        await this.validate(filePath);

        try {
            return await fsp.readFile(filePath, {
                encoding: "utf8",
            });
        } catch (error) {
            throw new TextFileError(
                `Unable to read ${filePath}: ${error.message}`
            );
        }
    }

    async *lines(filePath) {
        await this.validate(filePath);

        const stream = fs.createReadStream(filePath, {
            encoding: "utf8",
            highWaterMark: 64 * 1024,
        });

        const lineReader = readline.createInterface({
            input: stream,
            crlfDelay: Infinity,
        });

        try {
            for await (const line of lineReader) {
                yield line;
            }
        } finally {
            lineReader.close();
            stream.destroy();
        }
    }

    async search(filePath, term) {
        if (typeof term !== "string" || term.length === 0) {
            throw new TextFileValidationError(
                "Search term must be a non-empty string."
            );
        }

        const matches = [];
        let lineNumber = 0;
        const normalizedTerm = term.toLocaleLowerCase();

        for await (const line of this.lines(filePath)) {
            lineNumber += 1;

            if (line.toLocaleLowerCase().includes(normalizedTerm)) {
                matches.push({
                    lineNumber,
                    text: line,
                });
            }
        }

        return matches;
    }

    async statistics(filePath) {
        await this.validate(filePath);

        let characters = 0;
        let lines = 0;
        let nonEmptyLines = 0;
        let words = 0;
        const frequency = new Map();

        const hash = crypto.createHash("sha256");

        for await (const line of this.lines(filePath)) {
            lines += 1;
            characters += line.length + 1;
            hash.update(`${line}\n`);

            if (line.trim().length > 0) {
                nonEmptyLines += 1;
            }

            const tokens = line.toLocaleLowerCase().match(
                /[\p{L}\p{N}_'-]+/gu
            ) ?? [];

            words += tokens.length;

            for (const token of tokens) {
                frequency.set(
                    token,
                    (frequency.get(token) ?? 0) + 1
                );
            }
        }

        return {
            filePath,
            characters,
            lines,
            nonEmptyLines,
            words,
            uniqueWords: frequency.size,
            sha256: hash.digest("hex"),
        };
    }

    async topWords(filePath, limit = 10) {
        if (!Number.isInteger(limit) || limit <= 0) {
            throw new TextFileValidationError(
                "limit must be a positive integer."
            );
        }

        const stats = new Map();

        for await (const line of this.lines(filePath)) {
            const tokens = line.toLocaleLowerCase().match(
                /[\p{L}\p{N}_'-]+/gu
            ) ?? [];

            for (const token of tokens) {
                stats.set(token, (stats.get(token) ?? 0) + 1);
            }
        }

        return [...stats.entries()]
            .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
            .slice(0, limit);
    }
}

async function createDemoFile() {
    const filePath = path.join(
        await fsp.mkdtemp(path.join(os.tmpdir(), "text-reader-")),
        "sample.txt"
    );

    await fsp.writeFile(
        filePath,
        [
            "Reading text files requires explicit encoding.",
            "Streaming reads reduce memory usage.",
            "Validation prevents unsafe input.",
            "Streaming reads are useful for large files.",
        ].join("\n") + "\n",
        "utf8"
    );

    return filePath;
}

async function main() {
    const reader = new TextFileReader();
    const filePath = await createDemoFile();

    try {
        console.log("=== Complete Text ===");
        console.log(await reader.read(filePath));

        console.log("=== Search ===");
        console.table(await reader.search(filePath, "streaming"));

        console.log("=== Statistics ===");
        console.table(await reader.statistics(filePath));

        console.log("=== Top Words ===");
        console.table(await reader.topWords(filePath, 5));

        const statistics = await reader.statistics(filePath);

        if (statistics.lines !== 4) {
            throw new Error("Unexpected line count.");
        }

        const matches = await reader.search(filePath, "STREAMING");

        if (matches.length !== 2) {
            throw new Error("Unexpected search result count.");
        }

        console.log("Validation checks passed.");
    } finally {
        await fsp.rm(path.dirname(filePath), {
            recursive: true,
            force: true,
        });
    }
}

main().catch((error) => {
    console.error(`[ERROR] ${error.message}`);
    process.exitCode = 1;
});
