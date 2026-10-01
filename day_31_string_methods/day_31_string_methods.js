"use strict";

/*
 * String Methods: practical JavaScript laboratory.
 *
 * This Node.js program focuses on JavaScript-specific string behavior:
 * UTF-16 code units, immutable strings, method chaining, template literals,
 * regular-expression methods, normalization, parsing, validation, and
 * event-driven processing of textual records.
 */

const readline = require("node:readline");

function heading(title) {
    console.log(`\n${"=".repeat(78)}\n${title}\n${"=".repeat(78)}`);
}

function show(label, value) {
    console.log(`${label.padEnd(38)} ${JSON.stringify(value)}`);
}

// ---------------------------------------------------------------------------
// Fundamental methods and immutable transformations.
// ---------------------------------------------------------------------------

function demonstrateFundamentals() {
    heading("Fundamental String Methods");

    const text = "  JavaScript String Methods  ";

    show("Original", text);
    show("trim()", text.trim());
    show("trimStart()", text.trimStart());
    show("trimEnd()", text.trimEnd());
    show("toLowerCase()", text.toLowerCase());
    show("toUpperCase()", text.toUpperCase());
    show("toLocaleLowerCase()", "İSTANBUL".toLocaleLowerCase("tr-TR"));
    show("charAt(2)", text.charAt(2));
    show("at(-2)", text.at(-2));
    show("includes('String')", text.includes("String"));
    show("startsWith('  Java')", text.startsWith("  Java"));
    show("endsWith('  ')", text.endsWith("  "));

    // JavaScript strings are immutable. trim() creates a new string rather
    // than modifying the original value.
    const trimmed = text.trim();
    show("Original after trim()", text);
    show("Returned string", trimmed);

    const phrase = "Node.js handles server-side text processing";

    show("length", phrase.length);
    show("indexOf('server')", phrase.indexOf("server"));
    show("lastIndexOf('e')", phrase.lastIndexOf("e"));
    show("indexOf('missing')", phrase.indexOf("missing"));
    show("repeat(2)", "JS ".repeat(2));
}

// ---------------------------------------------------------------------------
// Slicing, splitting, joining, replacement, and extraction.
// ---------------------------------------------------------------------------

function demonstrateStructuralMethods() {
    heading("Structural String Methods");

    const csv = "ATUL,JavaScript,Advanced,120";
    show("split(',')", csv.split(","));
    show("split(',', 2)", csv.split(",", 2));

    const text = "alpha   beta\tgamma";
    // split() with an explicit separator does not collapse arbitrary
    // whitespace. A regular expression is appropriate when whitespace runs
    // should be treated as one delimiter.
    show("split(' ')", text.split(" "));
    show("split(/\\s+/)", text.trim().split(/\s+/));

    const words = ["String", "methods", "are", "composable"];
    show("join(' ')", words.join(" "));
    show("join('|')", words.join("|"));

    const url = "https://example.com/orders/42";
    show("slice()", url.slice(8));
    show("substring()", url.substring(8, 19));
    show("substr-like slice()", url.slice(-2));

    const message = "ERROR: connection failed; ERROR: retrying";
    show("replace()", message.replace("ERROR", "WARNING"));
    show("replaceAll()", message.replaceAll("ERROR", "WARNING"));

    const filename = "report.final.csv";
    show("replace suffix", filename.replace(/\.csv$/, ""));
    show("split extension", filename.split(".").pop());

    const protocolParts = url.split("://");
    show("URL protocol", protocolParts[0]);
    show("URL remainder", protocolParts[1]);
}

// ---------------------------------------------------------------------------
// Classification and validation.
// ---------------------------------------------------------------------------

function isAsciiIdentifier(value) {
    const candidate = value.trim();

    if (candidate.length === 0) {
        return { valid: false, reason: "identifier is empty" };
    }

    // JavaScript has no built-in isIdentifier string method. A regular
    // expression supplies an explicit application rule for ASCII names.
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(candidate)) {
        return { valid: false, reason: "invalid identifier characters" };
    }

    return { valid: true, reason: "valid ASCII identifier" };
}

function demonstrateValidation() {
    heading("Validation and Classification");

    const values = [
        "",
        "12345",
        "ABC123",
        "hello_world",
        "hello-world",
        "  ",
        "42.50",
        "abc@example.com"
    ];

    for (const value of values) {
        console.log(`\nValue: ${JSON.stringify(value)}`);
        show("length", value.length);
        show("includes('@')", value.includes("@"));
        show("startsWith('A')", value.startsWith("A"));
        show("endsWith('0')", value.endsWith("0"));
        show("identifier validation", isAsciiIdentifier(value));
    }

    for (const value of ["customer_id", "2026_report", "order-id", "_cache"]) {
        show(`validate ${value}`, isAsciiIdentifier(value));
    }
}

// ---------------------------------------------------------------------------
// Regular-expression string methods.
// ---------------------------------------------------------------------------

function demonstratePatternProcessing() {
    heading("Pattern Processing with String Methods");

    const logLine =
        "2026-10-01 07:30:42 [ERROR] service=payments request_id=req-42 latency=187ms";

    const fields = logLine.match(
        /^(?<date>\S+)\s+(?<time>\S+)\s+\[(?<level>[A-Z]+)\]\s+service=(?<service>\S+)\s+request_id=(?<requestId>\S+)\s+latency=(?<latency>\d+)ms$/
    );

    if (fields?.groups) {
        show("Parsed log fields", fields.groups);
    }

    show(
        "matchAll()",
        [..."error=12 warning=4 error=7".matchAll(/(\w+)=(\d+)/g)]
            .map(match => ({ key: match[1], value: Number(match[2]) }))
    );

    const redacted = "Authorization: Bearer abc123xyz";
    show(
        "Sensitive-value replacement",
        redacted.replace(
            /^(Authorization:\s+Bearer\s+).+$/i,
            "$1[REDACTED]"
        )
    );
}

// ---------------------------------------------------------------------------
// Unicode behavior.
// ---------------------------------------------------------------------------

function demonstrateUnicode() {
    heading("Unicode and UTF-16 Behavior");

    const word = "café";
    const emoji = "🚀";

    show("word.length", word.length);
    show("emoji.length", emoji.length);

    // JavaScript's length and indexed access operate on UTF-16 code units.
    // Array.from() iterates Unicode code points and therefore handles the
    // surrogate pair used by this emoji as one logical character.
    show("Array.from(emoji).length", Array.from(emoji).length);
    show("emoji.at(0)", emoji.at(0));
    show("Array.from(emoji)[0]", Array.from(emoji)[0]);

    show(
        "NFC normalized",
        "cafe\u0301".normalize("NFC")
    );
    show(
        "NFD normalized code points",
        [..."café".normalize("NFD")].map(character =>
            character.codePointAt(0).toString(16)
        )
    );

    const caseInsensitiveA = "Straße".toLocaleLowerCase("de-DE");
    const caseInsensitiveB = "STRASSE".toLocaleLowerCase("de-DE");
    show("Locale lower-case comparison", caseInsensitiveA === caseInsensitiveB);
}

// ---------------------------------------------------------------------------
// Application-specific normalization.
// ---------------------------------------------------------------------------

function normalizeDisplayName(value) {
    const cleaned = value.trim().replace(/\s+/g, " ");

    if (cleaned.length === 0) {
        throw new TypeError("display name cannot be empty");
    }

    return cleaned
        .split(" ")
        .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
        .join(" ");
}

function canonicalEmail(value) {
    const email = value.trim().toLowerCase();

    // This deliberately validates structure without pretending to implement
    // the full RFC email grammar.
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        throw new TypeError("invalid basic email structure");
    }

    return email;
}

function demonstrateNormalization() {
    heading("Normalization Pipelines");

    for (const name of [
        "  atul   pandey ",
        "ATUL PANDEY",
        " Atul\tPandey ",
        "maria   fernández"
    ]) {
        try {
            show("raw name", name);
            show("normalized name", normalizeDisplayName(name));
        } catch (error) {
            show("normalization error", error.message);
        }
    }

    for (const email of [
        " ATUL.PANDEY@EXAMPLE.COM ",
        "user@example.com",
        "not-an-email"
    ]) {
        try {
            show("canonical email", canonicalEmail(email));
        } catch (error) {
            show("email validation error", error.message);
        }
    }
}

// ---------------------------------------------------------------------------
// Realistic event-driven text pipeline.
// ---------------------------------------------------------------------------

class LogStreamProcessor {
    constructor() {
        this.records = [];
        this.counts = new Map();
    }

    processLine(line) {
        const cleaned = line.trim();

        if (!cleaned) {
            return { accepted: false, reason: "blank line" };
        }

        const parts = cleaned.split("|");

        if (parts.length !== 4) {
            return {
                accepted: false,
                reason: "expected timestamp|level|service|message"
            };
        }

        const [timestamp, rawLevel, service, message] =
            parts.map(part => part.trim());

        const level = rawLevel.toUpperCase();

        if (!/^[A-Z]+$/.test(level)) {
            return { accepted: false, reason: "invalid severity" };
        }

        if (!["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].includes(level)) {
            return { accepted: false, reason: `unsupported level ${level}` };
        }

        if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(service)) {
            return { accepted: false, reason: "invalid service name" };
        }

        if (!message) {
            return { accepted: false, reason: "message is empty" };
        }

        const record = { timestamp, level, service, message };
        this.records.push(record);
        this.counts.set(level, (this.counts.get(level) ?? 0) + 1);

        return { accepted: true, record };
    }

    findMessages(term) {
        const normalized = term.trim().toLocaleLowerCase();

        if (!normalized) {
            return [];
        }

        return this.records.filter(record =>
            record.message.toLocaleLowerCase().includes(normalized)
        );
    }

    statistics() {
        return Object.fromEntries(this.counts);
    }
}

async function runEventDrivenPipeline(lines) {
    heading("Event-Driven Log Processing");

    const processor = new LogStreamProcessor();
    const input = readline.createInterface({
        input: require("node:stream").Readable.from(lines),
        crlfDelay: Infinity
    });

    const rejected = [];

    // for-await-of consumes the asynchronous readline event stream. This
    // mirrors how a larger Node.js application can process text incrementally
    // without loading an entire file into memory.
    let lineNumber = 0;

    for await (const line of input) {
        lineNumber += 1;

        const result = processor.processLine(line);

        if (!result.accepted) {
            rejected.push(`line ${lineNumber}: ${result.reason}`);
        }
    }

    show("Accepted records", processor.records.length);
    show("Rejected records", rejected.length);
    show("Severity counts", processor.statistics());

    console.log("\nRejected input:");
    for (const reason of rejected) {
        console.log(`  ${reason}`);
    }

    console.log("\nDatabase-related messages:");
    for (const record of processor.findMessages("DATABASE")) {
        console.log(
            `  ${record.timestamp} [${record.level}] ${record.service}: ${record.message}`
        );
    }

    return processor;
}

// ---------------------------------------------------------------------------
// Security and edge cases.
// ---------------------------------------------------------------------------

function demonstrateSecurity() {
    heading("Security and Edge Cases");

    const userSupplied = "admin\nX-Injected: true";
    show("Original user input", userSupplied);
    show(
        "Single-line display form",
        userSupplied.replace(/[\r\n]/g, " ")
    );

    // HTML escaping must happen before inserting untrusted text into HTML.
    // String methods alone do not make arbitrary input safe for a browser.
    function escapeHtml(value) {
        return value
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    show(
        "Escaped HTML",
        escapeHtml('<img src=x onerror="attack()">')
    );

    const commaData = "a,,b";
    show("split preserves empty field", commaData.split(","));

    const repeated = "abc".repeat(3);
    show("repeat()", repeated);

    // Avoid constructing enormous strings from untrusted repeat counts.
    try {
        const count = Number("not-a-number");

        if (!Number.isSafeInteger(count) || count < 0 || count > 1000) {
            throw new RangeError("repeat count is outside the permitted range");
        }

        show("safe repeat", "x".repeat(count));
    } catch (error) {
        show("repeat validation error", error.message);
    }
}

// ---------------------------------------------------------------------------
// Assertions.
// ---------------------------------------------------------------------------

function runAssertions() {
    heading("Executable Checks");

    console.assert("  JavaScript  ".trim() === "JavaScript");
    console.assert("JAVASCRIPT".toLowerCase() === "javascript");
    console.assert("a,b,c".split(",").length === 3);
    console.assert(["2026", "10", "01"].join("-") === "2026-10-01");
    console.assert("report.csv".endsWith(".csv"));
    console.assert("database failure".includes("database"));
    console.assert("hello".replace("l", "L") === "heLlo");
    console.assert("a-b-c".replaceAll("-", "/") === "a/b/c");
    console.assert("  x  ".trim() === "x");
    console.assert("🚀".length === 2);
    console.assert(Array.from("🚀").length === 1);

    console.log("All JavaScript string-method assertions passed.");
}

async function main() {
    console.log("STRING METHODS LABORATORY");
    console.log("Node.js standard-library implementation");

    demonstrateFundamentals();
    demonstrateStructuralMethods();
    demonstrateValidation();
    demonstratePatternProcessing();
    demonstrateUnicode();
    demonstrateNormalization();

    await runEventDrivenPipeline([
        "2026-10-01T07:20:01|INFO|gateway|Request accepted",
        "2026-10-01T07:20:02|INFO|auth|User authentication succeeded",
        "2026-10-01T07:20:03|WARNING|gateway|Request latency exceeded threshold",
        "2026-10-01T07:20:04|ERROR|payments|Database connection failed",
        "2026-10-01T07:20:05|ERROR|payments|Database connection retry succeeded",
        "2026-10-01T07:20:06|CRITICAL|gateway|Upstream service unavailable",
        "bad|record",
        "2026-10-01T07:20:07|TRACE|gateway|Unsupported severity"
    ]);

    demonstrateSecurity();
    runAssertions();
}

main().catch(error => {
    console.error("Fatal error:", error.message);
    process.exitCode = 1;
});
