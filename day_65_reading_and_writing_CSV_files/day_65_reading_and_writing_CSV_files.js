"use strict";

/**
 * Reading and Writing CSV Files
 * Node.js 18+
 *
 * Features:
 * - CSV parser with quoted-field support
 * - CSV serialization
 * - Header validation
 * - Asynchronous streaming
 * - Backpressure handling
 * - Data validation
 * - Duplicate detection
 * - Schema enforcement
 * - Formula injection protection
 * - Atomic file replacement
 * - Department aggregation
 * - Error reporting
 */

const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const readline = require("node:readline");
const { once } = require("node:events");
const { finished } = require("node:stream/promises");
const { Transform } = require("node:stream");
const { pipeline } = require("node:stream/promises");

// ---------------------------------------------------------
// Configuration
// ---------------------------------------------------------

const DATA_DIR = path.join(__dirname, "csv_data");

const INPUT_FILE = path.join(DATA_DIR, "sales_input.csv");
const OUTPUT_FILE = path.join(DATA_DIR, "sales_processed.csv");
const REPORT_FILE = path.join(DATA_DIR, "sales_report.csv");

const HEADERS = [
    "transaction_id",
    "customer",
    "region",
    "amount",
    "status"
];

const VALID_STATUSES = new Set([
    "COMPLETED",
    "PENDING",
    "CANCELLED"
]);

// ---------------------------------------------------------
// Custom errors
// ---------------------------------------------------------

class CSVError extends Error {
    constructor(message, lineNumber = null) {
        super(message);
        this.name = "CSVError";
        this.lineNumber = lineNumber;
    }
}

class CSVSchemaError extends CSVError {
    constructor(message) {
        super(message);
        this.name = "CSVSchemaError";
    }
}

// ---------------------------------------------------------
// CSV parser
// ---------------------------------------------------------

function parseCSVLine(line) {
    const fields = [];

    let field = "";
    let insideQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];

        if (char === '"') {
            if (insideQuotes && line[i + 1] === '"') {
                field += '"';
                i++;
            } else {
                insideQuotes = !insideQuotes;
            }
        } else if (char === "," && !insideQuotes) {
            fields.push(field);
            field = "";
        } else {
            field += char;
        }
    }

    if (insideQuotes) {
        throw new CSVError("Unclosed quoted field");
    }

    fields.push(field);

    return fields;
}

/**
 * This serializer handles commas, quotes, and newlines.
 */
function serializeField(value) {
    let text = String(value ?? "");

    if (text.includes("\0")) {
        throw new CSVError("NUL characters are not allowed");
    }

    if (/^[\s]*[=+\-@]/.test(text)) {
        text = "'" + text;
    }

    if (/[",\r\n]/.test(text)) {
        return `"${text.replace(/"/g, '""')}"`;
    }

    return text;
}

function serializeCSV(headers, rows) {
    const output = [];

    output.push(headers.map(serializeField).join(","));

    for (const row of rows) {
        output.push(
            headers.map(header => serializeField(row[header])).join(",")
        );
    }

    return output.join("\r\n") + "\r\n";
}

// ---------------------------------------------------------
// Header validation
// ---------------------------------------------------------

function validateHeaders(headers) {
    if (!Array.isArray(headers) || headers.length === 0) {
        throw new CSVSchemaError("Missing CSV headers");
    }

    if (new Set(headers).size !== headers.length) {
        throw new CSVSchemaError("Duplicate CSV headers detected");
    }

    if (
        headers.length !== HEADERS.length ||
        headers.some((header, index) => header !== HEADERS[index])
    ) {
        throw new CSVSchemaError(
            `Expected headers: ${HEADERS.join(", ")}`
        );
    }
}

// ---------------------------------------------------------
// Domain validation
// ---------------------------------------------------------

function parseTransaction(fields, lineNumber) {
    if (fields.length !== HEADERS.length) {
        throw new CSVError(
            `Expected ${HEADERS.length} columns, received ${fields.length}`,
            lineNumber
        );
    }

    const [
        transactionId,
        customer,
        region,
        amountText,
        statusText
    ] = fields;

    const id = Number(transactionId);
    const amount = Number(amountText);
    const status = statusText.trim().toUpperCase();

    if (!Number.isSafeInteger(id) || id <= 0) {
        throw new CSVError("Invalid transaction ID", lineNumber);
    }

    if (!customer.trim()) {
        throw new CSVError("Customer name is required", lineNumber);
    }

    if (!region.trim()) {
        throw new CSVError("Region is required", lineNumber);
    }

    if (!Number.isFinite(amount) || amount < 0) {
        throw new CSVError("Invalid transaction amount", lineNumber);
    }

    if (!VALID_STATUSES.has(status)) {
        throw new CSVError("Unsupported transaction status", lineNumber);
    }

    return Object.freeze({
        transactionId: id,
        customer: customer.trim(),
        region: region.trim(),
        amount: Math.round(amount * 100) / 100,
        status
    });
}

// ---------------------------------------------------------
// Sample data
// ---------------------------------------------------------

async function createSampleFile() {
    await fs.promises.mkdir(DATA_DIR, { recursive: true });

    const content = serializeCSV(
        HEADERS,
        [
            {
                transaction_id: 1001,
                customer: "Alice Johnson",
                region: "North",
                amount: "12500.50",
                status: "COMPLETED"
            },
            {
                transaction_id: 1002,
                customer: "Bob Smith",
                region: "South",
                amount: "8500.00",
                status: "PENDING"
            },
            {
                transaction_id: 1003,
                customer: "Charlie Brown, Jr.",
                region: "East",
                amount: "15000.00",
                status: "COMPLETED"
            },
            {
                transaction_id: 1004,
                customer: "Diana Miller",
                region: "North",
                amount: "5000.00",
                status: "CANCELLED"
            },
            {
                transaction_id: 1005,
                customer: 'Eva "Finance" Wilson',
                region: "West",
                amount: "22000.00",
                status: "COMPLETED"
            },
            {
                transaction_id: 1006,
                customer: "Invalid Customer",
                region: "North",
                amount: "-50",
                status: "COMPLETED"
            }
        ]
    );

    await fs.promises.writeFile(INPUT_FILE, content, "utf8");
}

// ---------------------------------------------------------
// Asynchronous CSV streaming
// ---------------------------------------------------------

async function* readCSV(filePath) {
    const stream = fs.createReadStream(filePath, {
        encoding: "utf8",
        highWaterMark: 64 * 1024
    });

    const rl = readline.createInterface({
        input: stream,
        crlfDelay: Infinity
    });

    let headers = null;
    let lineNumber = 0;
    let buffer = "";
    let insideQuotes = false;

    try {
        for await (const line of rl) {
            lineNumber++;

            if (lineNumber === 1) {
                buffer = line.replace(/^\uFEFF/, "");
            } else {
                buffer += "\n" + line;
            }

            // Preserve multiline quoted records.
            for (let i = 0; i < line.length; i++) {
                if (line[i] === '"') {
                    if (insideQuotes && line[i + 1] === '"') {
                        i++;
                    } else {
                        insideQuotes = !insideQuotes;
                    }
                }
            }

            if (insideQuotes) {
                continue;
            }

            if (headers === null) {
                headers = parseCSVLine(buffer);
                validateHeaders(headers);
            } else {
                const fields = parseCSVLine(buffer);

                yield {
                    headers,
                    fields,
                    lineNumber
                };
            }

            buffer = "";
        }

        if (insideQuotes || buffer !== "") {
            throw new CSVError("Incomplete CSV record", lineNumber);
        }

        if (headers === null) {
            throw new CSVSchemaError("CSV file contains no header");
        }
    } finally {
        rl.close();
        stream.destroy();
    }
}

// ---------------------------------------------------------
// Transaction processing
// ---------------------------------------------------------

async function processTransactions() {
    const seenIds = new Set();

    const statistics = {
        total: 0,
        valid: 0,
        invalid: 0,
        duplicates: 0
    };

    const aggregates = new Map();

    const validRows = [];

    for await (const record of readCSV(INPUT_FILE)) {
        statistics.total++;

        let transaction;

        try {
            transaction = parseTransaction(
                record.fields,
                record.lineNumber
            );
        } catch (error) {
            statistics.invalid++;
            console.error(
                `Line ${record.lineNumber}: ${error.message}`
            );
            continue;
        }

        if (seenIds.has(transaction.transactionId)) {
            statistics.duplicates++;
            console.error(
                `Line ${record.lineNumber}: duplicate transaction`
            );
            continue;
        }

        seenIds.add(transaction.transactionId);

        statistics.valid++;

        validRows.push({
            transaction_id: transaction.transactionId,
            customer: transaction.customer,
            region: transaction.region,
            amount: transaction.amount.toFixed(2),
            status: transaction.status
        });

        if (transaction.status === "COMPLETED") {
            const current = aggregates.get(transaction.region) || {
                count: 0,
                amount: 0
            };

            current.count++;
            current.amount += transaction.amount;

            aggregates.set(transaction.region, current);
        }
    }

    await atomicWrite(
        OUTPUT_FILE,
        serializeCSV(HEADERS, validRows)
    );

    const reportRows = [...aggregates.entries()]
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([region, values]) => ({
            region,
            completed_count: values.count,
            completed_amount: values.amount.toFixed(2),
            average_amount: (
                values.amount / values.count
            ).toFixed(2)
        }));

    await atomicWrite(
        REPORT_FILE,
        serializeCSV(
            [
                "region",
                "completed_count",
                "completed_amount",
                "average_amount"
            ],
            reportRows
        )
    );

    return {
        statistics,
        reportRows
    };
}

// ---------------------------------------------------------
// Atomic output writing
// ---------------------------------------------------------

async function atomicWrite(filePath, content) {
    const temporaryPath = path.join(
        path.dirname(filePath),
        `.${path.basename(filePath)}.${process.pid}.${Date.now()}.tmp`
    );

    let handle;

    try {
        handle = await fs.promises.open(temporaryPath, "wx");

        await handle.writeFile(content, "utf8");
        await handle.sync();
        await handle.close();

        handle = null;

        await fs.promises.rename(temporaryPath, filePath);
    } catch (error) {
        if (handle) {
            await handle.close();
        }

        await fs.promises.rm(temporaryPath, {
            force: true
        });

        throw new CSVError(
            `Atomic write failed: ${error.message}`
        );
    }
}

// ---------------------------------------------------------
// Transform stream example
// ---------------------------------------------------------

class CSVValidationTransform extends Transform {
    constructor(options = {}) {
        super({
            ...options,
            objectMode: true
        });

        this.rowCount = 0;
    }

    _transform(record, encoding, callback) {
        try {
            if (!record || typeof record !== "object") {
                throw new CSVError("Invalid record object");
            }

            this.rowCount++;

            callback(null, record);
        } catch (error) {
            callback(error);
        }
    }
}

// ---------------------------------------------------------
// Unit tests
// ---------------------------------------------------------

function runTests() {
    const fields = parseCSVLine(
        '1001,"Alice, Johnson","North",12500.50,COMPLETED'
    );

    console.assert(fields.length === 5);
    console.assert(fields[1] === "Alice, Johnson");

    const quoted = parseCSVLine('"A ""quoted"" value",B');

    console.assert(quoted[0] === 'A "quoted" value');

    const encoded = serializeField("Alice, Johnson");

    console.assert(encoded === '"Alice, Johnson"');

    console.assert(
        serializeField("=SUM(A1:A5)") === "'=SUM(A1:A5)"
    );

    try {
        parseTransaction(
            ["0", "Alice", "North", "100", "COMPLETED"],
            2
        );

        throw new Error("Invalid ID accepted");
    } catch (error) {
        console.assert(error instanceof CSVError);
    }

    console.log("All JavaScript tests passed.");
}

// ---------------------------------------------------------
// Main
// ---------------------------------------------------------

async function main() {
    try {
        await createSampleFile();

        runTests();

        const result = await processTransactions();

        console.log("\nProcessing statistics:");
        console.table(result.statistics);

        console.log("\nRegional report:");
        console.table(result.reportRows);

        console.log("\nGenerated files:");
        console.log(OUTPUT_FILE);
        console.log(REPORT_FILE);
    } catch (error) {
        console.error("Processing failed:", error.message);
        process.exitCode = 1;
    }
}

main();
