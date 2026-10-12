"use strict";

/*
 * Function parameters and arguments in a Node.js-compatible environment.
 * Run with: node function_parameters.js
 *
 * This implementation focuses on closures, destructuring, rest parameters,
 * asynchronous calls, validation, and explicit argument normalization.
 */

const assert = require("node:assert/strict");

function section(title) {
  console.log(`\n${"=".repeat(68)}\n${title}\n${"=".repeat(68)}`);
}

// JavaScript matches ordinary arguments to parameters from left to right.
function calculateLineTotal(unitPrice, quantity) {
  if (
    typeof unitPrice !== "number" ||
    !Number.isFinite(unitPrice) ||
    unitPrice < 0
  ) {
    throw new TypeError("unitPrice must be a finite non-negative number");
  }
  if (!Number.isSafeInteger(quantity) || quantity < 0) {
    throw new TypeError("quantity must be a non-negative safe integer");
  }
  return Math.round(unitPrice * quantity * 100) / 100;
}

// Defaults apply when the argument is omitted or explicitly undefined.
// They do not apply to null.
function calculateOrderTotal(
  subtotal,
  taxRate = 0.18,
  discountRate = 0
) {
  if (![subtotal, taxRate, discountRate].every(Number.isFinite)) {
    throw new TypeError("All rates and amounts must be finite numbers");
  }
  if (subtotal < 0 || taxRate < 0 || taxRate > 1) {
    throw new RangeError("Invalid subtotal or tax rate");
  }
  if (discountRate < 0 || discountRate > 1) {
    throw new RangeError("Discount rate must be between 0 and 1");
  }

  const discounted = subtotal * (1 - discountRate);
  return Math.round(discounted * (1 + taxRate) * 100) / 100;
}

// Object destructuring makes optional settings self-documenting. A fresh
// object is created for each call, so the default configuration is isolated.
function createPullRequest({
  title,
  sourceBranch,
  targetBranch = "main",
  draft = false,
  labels = [],
} = {}) {
  for (const [name, value] of Object.entries({
    title,
    sourceBranch,
    targetBranch,
  })) {
    if (typeof value !== "string" || value.trim() === "") {
      throw new TypeError(`${name} must be a non-empty string`);
    }
  }

  if (sourceBranch === targetBranch) {
    throw new Error("Source and target branches must differ");
  }
  if (!Array.isArray(labels) || !labels.every(
    (label) => typeof label === "string" && label.trim() !== ""
  )) {
    throw new TypeError("labels must be an array of non-empty strings");
  }

  return Object.freeze({
    title: title.trim(),
    sourceBranch,
    targetBranch,
    draft: Boolean(draft),
    labels: Object.freeze([...labels]),
    state: "open",
  });
}

// Rest parameters collect remaining positional arguments into a real array.
function average(...values) {
  if (values.length === 0) {
    throw new RangeError("At least one value is required");
  }
  if (!values.every(Number.isFinite)) {
    throw new TypeError("Every value must be finite");
  }
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

// The spread operator expands an iterable into individual arguments.
function applyPricingAdjustment(base, adjustment) {
  return base + adjustment;
}

// JavaScript has no native keyword arguments. A named options object provides
// a readable alternative when a function has many optional settings.
function paginate(items, {
  page = 1,
  pageSize = 10,
  sort = "ascending",
} = {}) {
  if (!Array.isArray(items)) {
    throw new TypeError("items must be an array");
  }
  if (!Number.isSafeInteger(page) || page < 1) {
    throw new RangeError("page must be a positive integer");
  }
  if (!Number.isSafeInteger(pageSize) || pageSize < 1 || pageSize > 500) {
    throw new RangeError("pageSize must be between 1 and 500");
  }
  if (!["ascending", "descending"].includes(sort)) {
    throw new RangeError("Unsupported sort direction");
  }

  const sorted = [...items].sort((left, right) => {
    const comparison = String(left).localeCompare(String(right));
    return sort === "ascending" ? comparison : -comparison;
  });
  const offset = (page - 1) * pageSize;

  return {
    page,
    pageSize,
    totalItems: sorted.length,
    items: sorted.slice(offset, offset + pageSize),
  };
}

// Closures capture configuration at creation time. Each generated validator
// has a different limit without requiring global mutable state.
function createAmountValidator({ minimum = 0, maximum = 100000 } = {}) {
  if (
    !Number.isFinite(minimum) ||
    !Number.isFinite(maximum) ||
    minimum > maximum
  ) {
    throw new RangeError("Invalid validator range");
  }

  return function validateAmount(amount) {
    if (!Number.isFinite(amount) || amount < minimum || amount > maximum) {
      return {
        valid: false,
        message: `Amount must be between ${minimum} and ${maximum}`,
      };
    }
    return { valid: true, value: amount };
  };
}

// A callback is an argument that is invoked by another function.
function processRecords(records, selector, predicate = () => true) {
  if (!Array.isArray(records)) {
    throw new TypeError("records must be an array");
  }
  if (typeof selector !== "function" || typeof predicate !== "function") {
    throw new TypeError("selector and predicate must be functions");
  }

  return records
    .filter(predicate)
    .map(selector);
}

// Promises and async functions preserve the caller's argument contract while
// allowing the operation to complete asynchronously.
async function fetchReleaseMetadata(releaseId, {
  timeoutMs = 1000,
  transport = async (id) => ({ id, status: "published" }),
} = {}) {
  if (typeof releaseId !== "string" || releaseId.trim() === "") {
    throw new TypeError("releaseId is required");
  }
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new RangeError("timeoutMs must be positive");
  }
  if (typeof transport !== "function") {
    throw new TypeError("transport must be a function");
  }

  // Promise.race bounds waiting time; the underlying operation may continue
  // unless the transport itself supports cancellation.
  let timeoutHandle;
  const timeout = new Promise((_, reject) => {
    timeoutHandle = setTimeout(
      () => reject(new Error("Metadata request timed out")),
      timeoutMs
    );
  });

  try {
    return await Promise.race([
      Promise.resolve().then(() => transport(releaseId)),
      timeout,
    ]);
  } finally {
    clearTimeout(timeoutHandle);
  }
}

// This wrapper demonstrates explicit argument forwarding and error context.
function withAudit(functionToRun, audit) {
  if (typeof functionToRun !== "function" || typeof audit !== "function") {
    throw new TypeError("A callable and an audit callback are required");
  }

  return function audited(...args) {
    audit({
      operation: functionToRun.name || "anonymous",
      argumentCount: args.length,
    });
    return functionToRun.apply(this, args);
  };
}

async function runTests() {
  assert.equal(calculateLineTotal(25.5, 4), 102);
  assert.equal(calculateOrderTotal(100), 118);
  assert.equal(calculateOrderTotal(100, undefined, 0.1), 106.2);
  assert.throws(() => calculateOrderTotal(100, null), TypeError);

  const request = createPullRequest({
    title: "Validate payment limits",
    sourceBranch: "feature/payment-limits",
    draft: true,
    labels: ["security", "payments"],
  });
  assert.equal(request.targetBranch, "main");
  assert.equal(request.draft, true);
  assert.throws(() => {
    createPullRequest({
      title: "Invalid",
      sourceBranch: "main",
      targetBranch: "main",
    });
  }, Error);

  assert.equal(average(10, 20, 30), 20);
  assert.equal(applyPricingAdjustment(100, -5), 95);
  assert.deepEqual(
    paginate(["delta", "alpha", "charlie", "bravo"], {
      page: 2,
      pageSize: 2,
    }).items,
    ["charlie", "delta"]
  );

  const validateSmallAmounts = createAmountValidator({
    minimum: 10,
    maximum: 100,
  });
  assert.equal(validateSmallAmounts(50).valid, true);
  assert.equal(validateSmallAmounts(5).valid, false);

  const reviews = [
    { reviewer: "Asha", state: "APPROVED" },
    { reviewer: "Dev", state: "CHANGES_REQUESTED" },
    { reviewer: "Mira", state: "COMMENTED" },
  ];
  const blockingReviewers = processRecords(
    reviews,
    (review) => review.reviewer,
    (review) => review.state === "CHANGES_REQUESTED"
  );
  assert.deepEqual(blockingReviewers, ["Dev"]);

  const auditEvents = [];
  const auditedTotal = withAudit(
    calculateLineTotal,
    (event) => auditEvents.push(event)
  );
  assert.equal(auditedTotal(12, 5), 60);
  assert.equal(auditEvents[0].argumentCount, 2);

  const metadata = await fetchReleaseMetadata("release-42");
  assert.equal(metadata.status, "published");

  await assert.rejects(
    fetchReleaseMetadata("release-slow", {
      timeoutMs: 5,
      transport: () => new Promise(() => {}),
    }),
    /timed out/
  );

  await assert.rejects(
    fetchReleaseMetadata(""),
    /releaseId is required/
  );

  console.log("All JavaScript parameter and argument tests passed.");
}

async function main() {
  section("Argument matching and default values");
  console.log("Line total:", calculateLineTotal(85.5, 3));
  console.log("Order total:", calculateOrderTotal(1000, 0.18, 0.05));

  section("Destructured options and validated domain data");
  console.log(createPullRequest({
    title: "Improve authorization checks",
    sourceBranch: "feature/authz",
    targetBranch: "main",
    draft: false,
    labels: ["security"],
  }));

  section("Rest and spread arguments");
  const measurements = [12, 16, 20, 24];
  console.log("Average:", average(...measurements));
  console.log("Spread pricing:", applyPricingAdjustment(500, -35));

  section("Pagination and closure-based validation");
  console.log(paginate(
    ["release-8", "release-2", "release-5", "release-1"],
    { page: 1, pageSize: 3, sort: "ascending" }
  ));
  console.log(
    "Validation:",
    createAmountValidator({ minimum: 100, maximum: 500 })(350)
  );

  section("Callbacks and audit-aware argument forwarding");
  console.log(processRecords(
    [
      { name: "payments", enabled: true },
      { name: "search", enabled: false },
      { name: "identity", enabled: true },
    ],
    (record) => record.name.toUpperCase(),
    (record) => record.enabled
  ));

  section("Asynchronous argument contracts");
  console.log(await fetchReleaseMetadata("release-2026.10"));

  section("Automated checks");
  await runTests();
}

main().catch((error) => {
  console.error("Execution failed:", error.message);
  process.exitCode = 1;
});
