"use strict";

/*
 * Variable scope through JavaScript lexical environments, closures,
 * block bindings, module-like encapsulation, and asynchronous callbacks.
 */

function heading(title) {
  console.log(`\n========== ${title} ==========`);
}

const repositoryName = "repository-scope-lab";
let deploymentVersion = 12;

function inspectModuleBindings() {
  const localLabel = "inspection";
  return {
    repositoryName,
    deploymentVersion,
    localLabel
  };
}

function demonstrateBlockScope() {
  let decision = "pending";

  if (true) {
    let decision = "approved";
    const reviewer = "reviewer-ada";
    console.log("Inner decision:", decision);
    console.log("Block-only reviewer:", reviewer);
  }

  console.log("Outer decision:", decision);

  try {
    console.log(reviewer);
  } catch (error) {
    console.log("Block binding inaccessible:", error.name);
  }
}

function demonstrateVarHoisting() {
  console.log("Before var assignment:", status);
  var status = "ready";
  console.log("After var assignment:", status);

  // var is function-scoped, not block-scoped.
  if (true) {
    var pipelineState = "passed";
  }

  console.log("var after block:", pipelineState);

  // let and const bindings exist in a temporal dead zone until initialized.
  try {
    console.log(approval);
    let approval = true;
  } catch (error) {
    console.log("Temporal dead zone:", error.name);
  }
}

function demonstrateShadowing() {
  const policy = "repository-policy";

  function inspectOverride() {
    const policy = "pull-request-policy";
    return policy;
  }

  console.log("Outer policy:", policy);
  console.log("Inner policy:", inspectOverride());
}

function createCounter(initialValue = 0) {
  let count = initialValue;

  // The returned function retains the lexical environment after createCounter returns.
  return Object.freeze({
    increment() {
      count += 1;
      return count;
    },
    current() {
      return count;
    }
  });
}

function createReviewSession(reviewer) {
  let state = "OPEN";
  const comments = [];

  function transition(nextState) {
    const permitted = {
      OPEN: new Set(["SUBMITTED", "DISMISSED"]),
      SUBMITTED: new Set(["OPEN", "APPROVED", "CHANGES_REQUESTED"]),
      APPROVED: new Set(["DISMISSED"]),
      CHANGES_REQUESTED: new Set(["OPEN", "DISMISSED"]),
      DISMISSED: new Set()
    };

    if (!permitted[state]?.has(nextState)) {
      throw new Error(`Invalid review transition: ${state} -> ${nextState}`);
    }

    state = nextState;
    return state;
  }

  function addInlineComment(path, line, body) {
    if (!path.trim() || !Number.isInteger(line) || line < 1 || !body.trim()) {
      throw new TypeError("A comment requires a path, positive line, and body");
    }

    comments.push(Object.freeze({ path, line, body }));
  }

  return Object.freeze({
    reviewer,
    transition,
    addInlineComment,
    snapshot() {
      return Object.freeze({
        reviewer,
        state,
        comments: comments.map(comment => ({ ...comment }))
      });
    }
  });
}

function demonstrateClosureCapture() {
  const lateBoundFunctions = [];

  for (var index = 0; index < 3; index += 1) {
    lateBoundFunctions.push(() => index);
  }

  const blockScopedFunctions = [];

  for (let index = 0; index < 3; index += 1) {
    blockScopedFunctions.push(() => index);
  }

  console.log("var closure values:", lateBoundFunctions.map(fn => fn()));
  console.log("let closure values:", blockScopedFunctions.map(fn => fn()));
}

function evaluateProtection(policy, pullRequest) {
  const failures = [];

  if (pullRequest.draft) {
    failures.push("Draft pull requests cannot be merged");
  }

  if (pullRequest.targetBranch !== policy.branch) {
    failures.push("Pull request targets a different branch");
  }

  if (policy.requiredReviews < 0) {
    failures.push("Invalid required-review count");
  }

  const distinctApprovals = new Set(
    pullRequest.reviews
      .filter(review => review.state === "APPROVED")
      .map(review => review.reviewer)
      .filter(reviewer => reviewer !== pullRequest.author)
  );

  if (distinctApprovals.size < policy.requiredReviews) {
    failures.push("Insufficient eligible approvals");
  }

  for (const requiredCheck of policy.requiredChecks) {
    if (pullRequest.checks[requiredCheck] !== "SUCCESS") {
      failures.push(`Required check not successful: ${requiredCheck}`);
    }
  }

  if (policy.dismissStaleApprovals && pullRequest.approvalsStale) {
    failures.push("Approvals are stale after new commits");
  }

  if (policy.requireResolvedConversations && pullRequest.unresolvedConversations > 0) {
    failures.push("Review conversations remain unresolved");
  }

  return Object.freeze({
    eligible: failures.length === 0,
    failures
  });
}

async function loadReviewEvidence(fetcher) {
  // Dependency injection keeps network access optional and makes failures testable.
  try {
    const evidence = await fetcher();
    if (!evidence || !Array.isArray(evidence.reviews)) {
      throw new TypeError("Review evidence has an invalid shape");
    }
    return evidence;
  } catch (error) {
    return {
      reviews: [],
      error: error.message
    };
  }
}

async function main() {
  heading("Lexical bindings");
  console.log(inspectModuleBindings());
  demonstrateBlockScope();

  heading("Hoisting and initialization");
  demonstrateVarHoisting();

  heading("Shadowing");
  demonstrateShadowing();

  heading("Closures");
  const counter = createCounter(3);
  console.log(counter.increment(), counter.increment(), counter.current());
  demonstrateClosureCapture();

  heading("Review state encapsulation");
  const session = createReviewSession("reviewer-lin");
  session.addInlineComment("src/payment.js", 42, "Validate the currency before charging.");
  session.transition("SUBMITTED");
  session.transition("APPROVED");
  console.log(session.snapshot());

  try {
    session.transition("OPEN");
  } catch (error) {
    console.log("Invalid transition:", error.message);
  }

  heading("Branch protection policy");
  const policy = Object.freeze({
    branch: "main",
    requiredReviews: 2,
    requiredChecks: Object.freeze(["unit-tests", "security-scan"]),
    dismissStaleApprovals: true,
    requireResolvedConversations: true
  });

  const pullRequest = {
    author: "developer-kim",
    targetBranch: "main",
    draft: false,
    reviews: [
      { reviewer: "reviewer-ada", state: "APPROVED" },
      { reviewer: "reviewer-lin", state: "APPROVED" },
      { reviewer: "reviewer-ada", state: "APPROVED" }
    ],
    checks: {
      "unit-tests": "SUCCESS",
      "security-scan": "SUCCESS"
    },
    approvalsStale: false,
    unresolvedConversations: 0
  };

  console.log(evaluateProtection(policy, pullRequest));
  console.log(
    evaluateProtection(policy, {
      ...pullRequest,
      approvalsStale: true,
      checks: { ...pullRequest.checks, "security-scan": "FAILURE" }
    })
  );

  heading("Asynchronous scope");
  const evidence = await loadReviewEvidence(async () => ({
    reviews: [{ reviewer: "reviewer-ada", state: "APPROVED" }]
  }));
  console.log("Review evidence:", evidence);

  const failedEvidence = await loadReviewEvidence(async () => {
    throw new Error("Review service unavailable");
  });
  console.log("Handled service failure:", failedEvidence);
}

main().catch(error => {
  console.error("Unexpected execution failure:", error);
  process.exitCode = 1;
});
