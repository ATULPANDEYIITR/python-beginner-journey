"use strict";

/*
 * Mutable and Immutable Data in JavaScript
 *
 * Run with:
 *   node mutable-immutable-data.js
 *
 * The examples emphasize JavaScript-specific behavior:
 * references, object identity, shallow copies, structuredClone,
 * Object.freeze, readonly-style API boundaries, immutable state transitions,
 * Sets/Maps, and event-driven state management.
 */

function heading(title) {
  console.log(`\n${"=".repeat(72)}\n${title}\n${"=".repeat(72)}`);
}

function demonstratePrimitiveImmutability() {
  heading("Primitive values and reassignment");

  let count = 10;
  const original = count;

  // Numbers are immutable primitive values. The assignment changes the
  // variable's value; it does not mutate the number 10.
  count += 5;

  console.log({ original, count });

  let title = "pull request";
  const before = title;
  title = title.toUpperCase();

  console.log({ before, title });
}

function demonstrateReferenceAliasing() {
  heading("Object references and aliasing");

  const labels = ["backend", "database"];
  const secondReference = labels;

  // Both variables point to the same array, so push mutates the shared object.
  secondReference.push("security");

  console.log("labels:", labels);
  console.log("same object:", labels === secondReference);

  const independent = [...labels];
  independent.push("testing");

  console.log("original:", labels);
  console.log("independent copy:", independent);
}

function demonstrateNestedCopies() {
  heading("Nested objects: shallow copy versus deep copy");

  const review = {
    title: "Improve validation",
    files: ["validator.js", "validator.test.js"],
    metadata: {
      priority: "high",
      labels: ["review", "backend"]
    }
  };

  const shallow = { ...review };
  const deep = structuredClone(review);

  // Spread creates a new outer object but preserves references to nested
  // objects and arrays.
  shallow.metadata.labels.push("security");
  shallow.files.push("README.md");

  // structuredClone recursively copies supported structured data.
  deep.metadata.labels.push("documentation");

  console.log("original:", review);
  console.log("shallow:", shallow);
  console.log("deep:", deep);
  console.log(
    "nested metadata shared by shallow:",
    review.metadata === shallow.metadata
  );
  console.log(
    "nested metadata shared by deep:",
    review.metadata === deep.metadata
  );
}

function demonstrateObjectFreeze() {
  heading("Object.freeze and shallow immutability");

  const policy = Object.freeze({
    protectedBranch: "main",
    requiredApprovals: 2,
    checks: ["lint", "tests"]
  });

  try {
    // In strict mode this assignment throws because the top-level property
    // cannot be changed.
    policy.requiredApprovals = 3;
  } catch (error) {
    console.log("top-level mutation blocked:", error.name);
  }

  // Object.freeze is shallow. The nested array remains mutable.
  policy.checks.push("security-scan");

  console.log("frozen policy:", policy);
  console.log("nested array remained mutable:", policy.checks);
}

function deepFreeze(value, seen = new WeakSet()) {
  if (value === null || typeof value !== "object") {
    return value;
  }

  if (seen.has(value)) {
    return value;
  }

  seen.add(value);

  for (const child of Object.values(value)) {
    deepFreeze(child, seen);
  }

  return Object.freeze(value);
}

function demonstrateDeepFreeze() {
  heading("Recursive freezing");

  const policy = deepFreeze({
    protectedBranch: "main",
    checks: ["lint", "tests"],
    reviewers: {
      required: 2,
      teams: ["platform"]
    }
  });

  try {
    policy.reviewers.teams.push("security");
  } catch (error) {
    console.log("nested mutation blocked:", error.name);
  }

  console.log("deep-frozen policy:", policy);
}

class ImmutablePullRequest {
  constructor({ id, title, labels = [], files = [] }) {
    if (!id || !title) {
      throw new TypeError("id and title are required");
    }

    this.id = id;
    this.title = title;

    // New arrays prevent callers from retaining a mutable reference to the
    // arrays supplied to the constructor.
    this.labels = Object.freeze([...labels]);
    this.files = Object.freeze([...files]);

    Object.freeze(this);
  }

  withLabel(label) {
    if (typeof label !== "string" || label.length === 0) {
      throw new TypeError("label must be a non-empty string");
    }

    if (this.labels.includes(label)) {
      return this;
    }

    return new ImmutablePullRequest({
      id: this.id,
      title: this.title,
      labels: [...this.labels, label],
      files: this.files
    });
  }

  withFile(file) {
    if (typeof file !== "string" || file.length === 0) {
      throw new TypeError("file must be a non-empty string");
    }

    if (this.files.includes(file)) {
      return this;
    }

    return new ImmutablePullRequest({
      id: this.id,
      title: this.title,
      labels: this.labels,
      files: [...this.files, file]
    });
  }
}

function demonstrateImmutableDomainObject() {
  heading("Immutable domain object");

  const original = new ImmutablePullRequest({
    id: "PR-1042",
    title: "Improve validation",
    labels: ["backend"],
    files: ["validator.js"]
  });

  const reviewed = original.withLabel("review");
  const expanded = reviewed.withFile("validator.test.js");

  console.log("original:", original);
  console.log("reviewed:", reviewed);
  console.log("expanded:", expanded);
  console.log("original unchanged:", original.labels);
  console.log(
    "non-changing operation returns same instance:",
    expanded.withLabel("review") === expanded
  );
}

function demonstrateSetAndMap() {
  heading("Immutable-friendly Sets and Maps through copy-on-write");

  const originalApprovals = new Set(["reviewer-a"]);
  const nextApprovals = new Set(originalApprovals);
  nextApprovals.add("reviewer-b");

  const originalChecks = new Map([
    ["lint", "passed"],
    ["tests", "pending"]
  ]);

  const nextChecks = new Map(originalChecks);
  nextChecks.set("tests", "passed");

  console.log("original approvals:", [...originalApprovals]);
  console.log("next approvals:", [...nextApprovals]);
  console.log("original checks:", [...originalChecks]);
  console.log("next checks:", [...nextChecks]);
}

class ReviewStateStore {
  #state;
  #listeners = new Set();

  constructor(initialState) {
    this.#state = deepFreeze(structuredClone(initialState));
  }

  get snapshot() {
    // A deeply frozen state can safely be shared with consumers that are not
    // trusted to preserve ownership rules.
    return this.#state;
  }

  subscribe(listener) {
    if (typeof listener !== "function") {
      throw new TypeError("listener must be a function");
    }

    this.#listeners.add(listener);

    return () => {
      this.#listeners.delete(listener);
    };
  }

  update(transform) {
    if (typeof transform !== "function") {
      throw new TypeError("transform must be a function");
    }

    const candidate = transform(this.#state);

    if (candidate === this.#state) {
      return this.#state;
    }

    this.#state = deepFreeze(candidate);

    // Copy the listener set before iteration so an unsubscribe during a
    // notification cannot create surprising iterator behavior.
    for (const listener of [...this.#listeners]) {
      listener(this.#state);
    }

    return this.#state;
  }
}

function demonstrateEventDrivenImmutableState() {
  heading("Event-driven immutable state");

  const store = new ReviewStateStore({
    id: "PR-1042",
    revision: 1,
    approvals: [],
    checks: {
      lint: "pending",
      tests: "pending"
    }
  });

  const unsubscribe = store.subscribe((state) => {
    console.log("state changed:", state);
  });

  const firstSnapshot = store.snapshot;

  store.update((state) => ({
    ...state,
    approvals: [...state.approvals, "reviewer-a"]
  }));

  store.update((state) => ({
    ...state,
    checks: {
      ...state.checks,
      lint: "passed"
    }
  }));

  const beforeRevision = store.snapshot;

  store.update((state) => ({
    ...state,
    revision: state.revision + 1,
    approvals: []
  }));

  console.log("first snapshot remains:", firstSnapshot);
  console.log("pre-revision snapshot remains:", beforeRevision);

  unsubscribe();
}

function createReviewSnapshot(state) {
  return Object.freeze({
    id: state.id,
    revision: state.revision,
    approvals: Object.freeze([...state.approvals]),
    checks: Object.freeze({ ...state.checks })
  });
}

function processReviewsWithoutMutation(reviews) {
  if (!Array.isArray(reviews)) {
    throw new TypeError("reviews must be an array");
  }

  return reviews.map((review) => {
    if (!review || typeof review.reviewer !== "string") {
      throw new TypeError("each review must have a reviewer");
    }

    return {
      ...review,
      normalizedReviewer: review.reviewer.trim().toLowerCase(),
      approved: review.state === "approved"
    };
  });
}

function demonstrateFunctionalTransformation() {
  heading("Functional transformation of collections");

  const reviews = [
    { reviewer: "Reviewer-A", state: "approved" },
    { reviewer: "Reviewer-B", state: "changes_requested" },
    { reviewer: "Reviewer-C", state: "commented" }
  ];

  const processed = processReviewsWithoutMutation(reviews);

  console.log("original reviews:", reviews);
  console.log("processed reviews:", processed);
}

function demonstrateReferenceEquality() {
  heading("Reference equality and change detection");

  const state = {
    checks: {
      tests: "passed",
      lint: "passed"
    }
  };

  const unchanged = state;
  const changed = {
    ...state,
    checks: {
      ...state.checks,
      lint: "failed"
    }
  };

  console.log("unchanged reference:", state === unchanged);
  console.log("changed root reference:", state !== changed);
  console.log("changed nested reference:", state.checks !== changed.checks);

  /*
   * This identity-based pattern is useful in state systems because consumers
   * can detect which branch was replaced without recursively comparing every
   * field. It also requires disciplined ownership: direct mutation defeats
   * the assumption that reference identity represents state changes.
   */
}

function demonstrateSerializationBoundary() {
  heading("Serialization as an immutable snapshot boundary");

  const state = {
    pullRequest: "PR-1042",
    labels: ["backend", "review"],
    checks: {
      tests: "passed"
    }
  };

  const serialized = JSON.stringify(state);
  const snapshot = JSON.parse(serialized);

  snapshot.labels.push("security");

  console.log("serialized:", serialized);
  console.log("original:", state);
  console.log("deserialized copy:", snapshot);
}

function run() {
  demonstratePrimitiveImmutability();
  demonstrateReferenceAliasing();
  demonstrateNestedCopies();
  demonstrateObjectFreeze();
  demonstrateDeepFreeze();
  demonstrateImmutableDomainObject();
  demonstrateSetAndMap();
  demonstrateEventDrivenImmutableState();
  demonstrateFunctionalTransformation();
  demonstrateReferenceEquality();
  demonstrateSerializationBoundary();

  heading("Completed");
  console.log("All mutable and immutable data demonstrations completed.");
}

run();
