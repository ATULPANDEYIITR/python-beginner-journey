"use strict";

/*
 * Unpacking in JavaScript
 *
 * This file focuses on destructuring assignment and parameter
 * destructuring as JavaScript's primary mechanisms corresponding to
 * Python-style unpacking.
 *
 * The examples move from arrays and objects into nested structures,
 * rest elements, function parameters, defaults, iterables, generators,
 * asynchronous data, validation, and practical data-processing workflows.
 */

function heading(title) {
    console.log(`\n${"=".repeat(78)}\n${title}\n${"=".repeat(78)}`);
}

function show(label, value) {
    console.log(`${label}:`, value);
}

// ---------------------------------------------------------------------------
// Array destructuring
// ---------------------------------------------------------------------------

function demonstrateArrayDestructuring() {
    heading("Basic array destructuring");

    const employee = ["E101", "Atul", "Operations"];
    const [employeeId, name, department] = employee;

    show("employeeId", employeeId);
    show("name", name);
    show("department", department);

    // JavaScript array destructuring depends on iterable position.
    const coordinates = [28.6139, 77.2090];
    const [latitude, longitude] = coordinates;

    show("latitude", latitude);
    show("longitude", longitude);

    // Missing values become undefined instead of causing an arity error.
    const [first, second, third] = [10, 20];
    show("missing third value", third);

    // Extra source values are ignored unless a rest element captures them.
    const [a, b] = [100, 200, 300];
    show("extra values ignored", [a, b]);
}

// ---------------------------------------------------------------------------
// Rest elements
// ---------------------------------------------------------------------------

function demonstrateRestElements() {
    heading("Rest elements in array destructuring");

    const values = [10, 20, 30, 40, 50];

    const [first, ...middle] = values;
    show("first", first);
    show("middle", middle);

    const [head, ...tail] = values;
    show("head", head);
    show("tail", tail);

    // A rest element must be the final element in an array pattern.
    // The following would be a SyntaxError:
    // const [...items, last] = values;

    // The rest target is always an array.
    const [...copy] = new Set([1, 2, 3]);
    show("rest from Set", copy);
}

// ---------------------------------------------------------------------------
// Nested destructuring
// ---------------------------------------------------------------------------

function demonstrateNestedDestructuring() {
    heading("Nested destructuring");

    const records = [
        ["E101", ["Engineering", "Platform"], 92000],
        ["E102", ["Operations", "Analytics"], 87000]
    ];

    for (const [employeeId, [division, team], salary] of records) {
        console.log({
            employeeId,
            division,
            team,
            salary
        });
    }

    const response = {
        status: 200,
        body: {
            message: "OK",
            metadata: {
                requestId: "req-782"
            }
        }
    };

    const {
        status,
        body: {
            message,
            metadata: { requestId }
        }
    } = response;

    show("status", status);
    show("message", message);
    show("requestId", requestId);
}

// ---------------------------------------------------------------------------
// Swapping
// ---------------------------------------------------------------------------

function demonstrateSwapping() {
    heading("Swapping values");

    let environment = "production";
    let target = "staging";

    [environment, target] = [target, environment];

    show("environment", environment);
    show("target", target);

    // The right-hand array is created before assignment, which makes the
    // simultaneous swap safe without a temporary variable.
}

// ---------------------------------------------------------------------------
// Function parameter destructuring
// ---------------------------------------------------------------------------

function calculateRiskScore([volatility, exposure, confidence]) {
    return Number((volatility * exposure * confidence).toFixed(4));
}

function describeEmployee({
    id,
    department,
    role = "Analyst"
}) {
    return `${id}: ${department} / ${role}`;
}

function demonstrateParameterDestructuring() {
    heading("Function parameter destructuring");

    const values = [0.18, 0.75, 0.92];
    show("risk score", calculateRiskScore(values));

    const employee = {
        id: "E104",
        department: "Operations"
    };

    show("employee description", describeEmployee(employee));

    // Defaults apply when the property is undefined.
    show(
        "default role",
        describeEmployee({
            id: "E105",
            department: "Finance"
        })
    );
}

// ---------------------------------------------------------------------------
// Object destructuring and property renaming
// ---------------------------------------------------------------------------

function demonstrateObjectDestructuring() {
    heading("Object destructuring");

    const configuration = {
        host: "api.internal",
        port: 8443,
        enabled: true
    };

    const {
        host,
        port,
        enabled
    } = configuration;

    show("host", host);
    show("port", port);
    show("enabled", enabled);

    // A property can be assigned to a differently named local variable.
    const {
        host: serverHost,
        port: serverPort
    } = configuration;

    show("serverHost", serverHost);
    show("serverPort", serverPort);

    // Default values apply only when the property is undefined.
    const {
        timeout = 30,
        retries = 3
    } = {};

    show("default timeout", timeout);
    show("default retries", retries);
}

// ---------------------------------------------------------------------------
// Object rest
// ---------------------------------------------------------------------------

function demonstrateObjectRest() {
    heading("Object rest properties");

    const employee = {
        id: "E101",
        name: "Atul",
        department: "Operations",
        role: "Analyst",
        location: "Lucknow"
    };

    const {
        id,
        name,
        ...organizationalData
    } = employee;

    show("id", id);
    show("name", name);
    show("remaining object", organizationalData);

    // Rest creates a new object. It does not remove properties from the
    // original source object.
    show("original object", employee);
}

// ---------------------------------------------------------------------------
// Spread syntax
// ---------------------------------------------------------------------------

function demonstrateSpreadSyntax() {
    heading("Spread syntax as the construction counterpart");

    const baseConfiguration = {
        timeout: 30,
        retries: 3,
        mode: "safe"
    };

    const productionConfiguration = {
        ...baseConfiguration,
        timeout: 60,
        mode: "strict"
    };

    show("base configuration", baseConfiguration);
    show("production configuration", productionConfiguration);

    const firstBatch = [1, 2, 3];
    const secondBatch = [4, 5];

    const combined = [...firstBatch, ...secondBatch];

    show("combined arrays", combined);
}

// ---------------------------------------------------------------------------
// Iterable destructuring
// ---------------------------------------------------------------------------

function* eventStream() {
    yield "created";
    yield "validated";
    yield "processed";
    yield "archived";
}

function demonstrateIterableDestructuring() {
    heading("Destructuring arbitrary iterables");

    const values = new Set(["north", "south", "west"]);
    const [first, ...remaining] = values;

    show("first Set value", first);
    show("remaining Set values", remaining);

    const [event, ...futureEvents] = eventStream();

    show("first generated event", event);
    show("future events", futureEvents);

    // Strings are iterable too, so destructuring a string works character
    // by character.
    const [character, ...remainingCharacters] = "API";

    show("first character", character);
    show("remaining characters", remainingCharacters);
}

// ---------------------------------------------------------------------------
// Map destructuring
// ---------------------------------------------------------------------------

function demonstrateMapDestructuring() {
    heading("Map entries and destructuring");

    const metrics = new Map([
        ["latency", 84.5],
        ["throughput", 920],
        ["errors", 3]
    ]);

    for (const [metric, value] of metrics) {
        console.log(`${metric}=${value}`);
    }

    const firstEntry = [...metrics][0];
    const [metricName, metricValue] = firstEntry;

    show("first metric", metricName);
    show("first metric value", metricValue);
}

// ---------------------------------------------------------------------------
// Practical record parser
// ---------------------------------------------------------------------------

function parseCsvLikeRecord(line) {
    const fields = line.split(",").map((field) => field.trim());

    if (fields.length < 3) {
        throw new Error(
            "Record must contain id, department, and status"
        );
    }

    const [id, department, status, ...extraFields] = fields;

    if (!id) {
        throw new Error("Record ID cannot be empty");
    }

    if (!department) {
        throw new Error("Department cannot be empty");
    }

    const allowedStatuses = new Set([
        "active",
        "inactive",
        "pending"
    ]);

    if (!allowedStatuses.has(status)) {
        throw new Error(`Unsupported status: ${status}`);
    }

    return {
        id,
        department,
        status,
        extraFields
    };
}

function demonstrateRecordParsing() {
    heading("Record parsing with destructuring");

    const lines = [
        "E101,Engineering,active,platform",
        "E102,Operations,pending,analytics",
        "E103,Finance,inactive"
    ];

    for (const line of lines) {
        console.log(parseCsvLikeRecord(line));
    }

    try {
        parseCsvLikeRecord("E999,,active");
    } catch (error) {
        console.log(`Rejected record: ${error.message}`);
    }
}

// ---------------------------------------------------------------------------
// API response processing
// ---------------------------------------------------------------------------

function processApiResponse(response) {
    if (
        response === null ||
        typeof response !== "object"
    ) {
        throw new TypeError("response must be an object");
    }

    const {
        status,
        data: {
            requestId,
            records = [],
            nextPage = null
        } = {}
    } = response;

    if (!Number.isInteger(status)) {
        throw new TypeError("status must be an integer");
    }

    if (status < 200 || status >= 600) {
        throw new RangeError("status must be HTTP-style");
    }

    if (!Array.isArray(records)) {
        throw new TypeError("records must be an array");
    }

    return {
        status,
        requestId,
        recordCount: records.length,
        nextPage
    };
}

function demonstrateApiResponse() {
    heading("API response destructuring");

    const response = {
        status: 200,
        data: {
            requestId: "req-2048",
            records: [
                { id: "R1", value: 18 },
                { id: "R2", value: 21 }
            ],
            nextPage: null
        }
    };

    show("processed API response", processApiResponse(response));

    try {
        processApiResponse({
            status: 200
        });
    } catch (error) {
        console.log(`Invalid response: ${error.message}`);
    }
}

// ---------------------------------------------------------------------------
// Function arguments and rest parameters
// ---------------------------------------------------------------------------

function collectMetrics(...values) {
    const metadata = values.at(-1);

    if (
        metadata === null ||
        typeof metadata !== "object" ||
        Array.isArray(metadata)
    ) {
        return {
            measurements: values,
            metadata: {}
        };
    }

    return {
        measurements: values.slice(0, -1),
        metadata
    };
}

function demonstrateRestParameters() {
    heading("Rest parameters");

    const result = collectMetrics(
        91.2,
        88.7,
        94.5,
        {
            source: "production",
            owner: "operations"
        }
    );

    show("collected metrics", result);
}

// ---------------------------------------------------------------------------
// Default values and null handling
// ---------------------------------------------------------------------------

function demonstrateDefaultsAndNull() {
    heading("Defaults and null");

    const {
        timeout = 30
    } = {};

    const {
        retries = 3
    } = {
        retries: undefined
    };

    show("undefined activates default", timeout);
    show("explicit undefined activates default", retries);

    const {
        value = 100
    } = {
        value: null
    };

    // null does not activate a destructuring default.
    show("null remains null", value);

    const safeResponse = null;

    // Nullish coalescing supplies an object before destructuring.
    const {
        status: safeStatus = 500
    } = safeResponse ?? {};

    show("safe destructuring from null", safeStatus);
}

// ---------------------------------------------------------------------------
// Event-driven workflow
// ---------------------------------------------------------------------------

class WorkflowEventProcessor {
    constructor() {
        this.handlers = new Map();
    }

    on(eventName, handler) {
        this.handlers.set(eventName, handler);
    }

    emit(eventName, payload) {
        const handler = this.handlers.get(eventName);

        if (!handler) {
            throw new Error(`No handler registered for ${eventName}`);
        }

        const {
            id,
            actor,
            metadata = {}
        } = payload;

        return handler({
            id,
            actor,
            metadata
        });
    }
}

function demonstrateEventWorkflow() {
    heading("Event-driven destructuring");

    const processor = new WorkflowEventProcessor();

    processor.on("processed", ({ id, actor, metadata }) => {
        return {
            message: `Request ${id} processed by ${actor}`,
            region: metadata.region ?? "unknown"
        };
    });

    const result = processor.emit("processed", {
        id: "REQ-42",
        actor: "worker-7",
        metadata: {
            region: "north"
        }
    });

    show("event result", result);
}

// ---------------------------------------------------------------------------
// Asynchronous workflow
// ---------------------------------------------------------------------------

async function fetchOperationalRecord() {
    return {
        status: 200,
        payload: {
            id: "OPS-100",
            metrics: [84.5, 91.2, 88.1]
        }
    };
}

async function demonstrateAsyncDestructuring() {
    heading("Asynchronous destructuring");

    const {
        status,
        payload: {
            id,
            metrics
        }
    } = await fetchOperationalRecord();

    const [firstMetric, ...remainingMetrics] = metrics;

    show("status", status);
    show("id", id);
    show("first metric", firstMetric);
    show("remaining metrics", remainingMetrics);
}

// ---------------------------------------------------------------------------
// Practical ETL processing
// ---------------------------------------------------------------------------

function processSalesRows(rows) {
    const totals = new Map();

    for (const row of rows) {
        if (!Array.isArray(row) || row.length !== 4) {
            throw new Error("Each sales row must contain exactly four fields");
        }

        const [transactionId, region, amount, status] = row;

        if (typeof transactionId !== "string" || !transactionId.trim()) {
            throw new Error("transactionId must be non-empty");
        }

        if (typeof region !== "string" || !region.trim()) {
            throw new Error("region must be non-empty");
        }

        if (
            typeof amount !== "number" ||
            !Number.isFinite(amount) ||
            amount < 0
        ) {
            throw new Error(
                `Invalid amount for ${transactionId}`
            );
        }

        if (status === "completed") {
            totals.set(
                region,
                (totals.get(region) ?? 0) + amount
            );
        } else if (
            status !== "pending" &&
            status !== "cancelled"
        ) {
            throw new Error(`Unknown status: ${status}`);
        }
    }

    return Object.fromEntries(totals);
}

function demonstrateETL() {
    heading("Practical ETL workflow");

    const rows = [
        ["TX001", "North", 12500, "completed"],
        ["TX002", "North", 3000, "pending"],
        ["TX003", "South", 8900, "completed"],
        ["TX004", "North", 1500, "cancelled"],
        ["TX005", "South", 2100, "completed"]
    ];

    show("regional totals", processSalesRows(rows));

    try {
        processSalesRows([
            ["TX999", "West", -10, "completed"]
        ]);
    } catch (error) {
        console.log(`Rejected ETL row: ${error.message}`);
    }
}

// ---------------------------------------------------------------------------
// Pattern-based message classification
// ---------------------------------------------------------------------------

function classifyMessage(message) {
    if (Array.isArray(message)) {
        const [type, code, ...details] = message;

        if (type === "ERROR") {
            return {
                kind: "error",
                code,
                details
            };
        }

        if (type === "SUCCESS") {
            return {
                kind: "success",
                code,
                details
            };
        }
    }

    if (
        message !== null &&
        typeof message === "object"
    ) {
        const {
            status,
            ...metadata
        } = message;

        return {
            kind: "object",
            status,
            metadata
        };
    }

    return {
        kind: "unknown"
    };
}

function demonstrateMessageClassification() {
    heading("Structured message classification");

    const messages = [
        ["ERROR", 503, "service unavailable"],
        ["SUCCESS", 200, "cached", "validated"],
        {
            status: "pending",
            requestId: "REQ-12"
        },
        "unexpected"
    ];

    for (const message of messages) {
        console.log(classifyMessage(message));
    }
}

// ---------------------------------------------------------------------------
// Security-conscious destructuring
// ---------------------------------------------------------------------------

function extractPublicUserData(user) {
    if (
        user === null ||
        typeof user !== "object"
    ) {
        throw new TypeError("user must be an object");
    }

    const {
        id,
        name,
        role = "user"
    } = user;

    return {
        id,
        name,
        role
    };
}

function demonstrateSecurityBoundary() {
    heading("Destructuring at a security boundary");

    const untrustedUser = {
        id: "U-100",
        name: "Atul",
        role: "analyst",
        passwordHash: "sensitive-value",
        internalToken: "sensitive-value"
    };

    // Selecting approved properties is safer than forwarding an entire
    // untrusted object to another subsystem.
    show(
        "public user",
        extractPublicUserData(untrustedUser)
    );
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
    demonstrateArrayDestructuring();
    demonstrateRestElements();
    demonstrateNestedDestructuring();
    demonstrateSwapping();
    demonstrateParameterDestructuring();
    demonstrateObjectDestructuring();
    demonstrateObjectRest();
    demonstrateSpreadSyntax();
    demonstrateIterableDestructuring();
    demonstrateMapDestructuring();
    demonstrateRecordParsing();
    demonstrateApiResponse();
    demonstrateRestParameters();
    demonstrateDefaultsAndNull();
    demonstrateEventWorkflow();
    await demonstrateAsyncDestructuring();
    demonstrateETL();
    demonstrateMessageClassification();
    demonstrateSecurityBoundary();
}

main().catch((error) => {
    console.error("Execution failed:", error);
    process.exitCode = 1;
});
