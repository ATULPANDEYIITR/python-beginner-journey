"use strict";

const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const EventEmitter = require("node:events");

class RepositoryError extends Error {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "RepositoryError";
  }
}

class ValidationError extends RepositoryError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "ValidationError";
  }
}

class RepositoryNotFoundError extends RepositoryError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "RepositoryNotFoundError";
  }
}

class StorageError extends RepositoryError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "StorageError";
  }
}

const WorkflowState = Object.freeze({
  DRAFT: "draft",
  OPEN: "open",
  MERGEABLE: "mergeable",
  BLOCKED: "blocked",
  MERGED: "merged",
  CLOSED: "closed",
});

function validateBranchName(branch) {
  if (typeof branch !== "string" || branch.trim() === "") {
    throw new ValidationError("Branch name is required.");
  }

  if (branch.length > 255) {
    throw new ValidationError("Branch name exceeds the maximum length.");
  }

  if (/\s/.test(branch)) {
    throw new ValidationError("Branch names cannot contain whitespace.");
  }
}

function evaluateMergePolicy(input) {
  try {
    validateBranchName(input.sourceBranch);
    validateBranchName(input.targetBranch);

    if (input.sourceBranch === input.targetBranch) {
      throw new ValidationError("Source and target branches must differ.");
    }

    if (!Number.isInteger(input.approvals) || input.approvals < 0) {
      throw new ValidationError("Approvals must be a non-negative integer.");
    }

    if (
      !Number.isInteger(input.requiredApprovals) ||
      input.requiredApprovals < 0
    ) {
      throw new ValidationError(
        "Required approvals must be a non-negative integer."
      );
    }

    if (!input.checksPassed) {
      return {
        state: WorkflowState.BLOCKED,
        reason: "Required status checks have failed.",
      };
    }

    if (!input.conversationsResolved) {
      return {
        state: WorkflowState.BLOCKED,
        reason: "Unresolved review conversations remain.",
      };
    }

    if (input.approvals < input.requiredApprovals) {
      return {
        state: WorkflowState.BLOCKED,
        reason: "Required approvals are missing.",
      };
    }

    return {
      state: WorkflowState.MERGEABLE,
      reason: "All merge conditions are satisfied.",
    };
  } catch (error) {
    if (error instanceof ValidationError) {
      return {
        state: WorkflowState.BLOCKED,
        reason: error.message,
      };
    }

    throw error;
  }
}

class RepositoryStore {
  constructor(filePath) {
    this.filePath = filePath;
  }

  async read() {
    try {
      const text = await fs.readFile(this.filePath, "utf8");

      if (text.trim() === "") {
        return {};
      }

      const data = JSON.parse(text);

      if (
        data === null ||
        typeof data !== "object" ||
        Array.isArray(data)
      ) {
        throw new StorageError("Repository store must contain an object.");
      }

      return data;
    } catch (error) {
      if (error instanceof StorageError) {
        throw error;
      }

      if (error.code === "ENOENT") {
        return {};
      }

      if (error.code === "EACCES") {
        throw new StorageError("Repository store cannot be read.", {
          cause: error,
        });
      }

      if (error instanceof SyntaxError) {
        throw new StorageError("Repository store contains invalid JSON.", {
          cause: error,
        });
      }

      throw new StorageError("Unexpected storage failure.", {
        cause: error,
      });
    }
  }

  async write(data) {
    try {
      await fs.mkdir(path.dirname(this.filePath), { recursive: true });
      await fs.writeFile(
        this.filePath,
        JSON.stringify(data, null, 2),
        "utf8"
      );
    } catch (error) {
      throw new StorageError("Repository store cannot be written.", {
        cause: error,
      });
    }
  }

  async save(repository) {
    if (!repository.name || !repository.owner) {
      throw new ValidationError("Repository name and owner are required.");
    }

    const data = await this.read();

    data[repository.name] = {
      owner: repository.owner,
      protected: Boolean(repository.protected),
      state: repository.state ?? WorkflowState.OPEN,
    };

    await this.write(data);
  }

  async get(name) {
    if (typeof name !== "string" || name.trim() === "") {
      throw new ValidationError("Repository name is required.");
    }

    const data = await this.read();

    if (!Object.hasOwn(data, name)) {
      throw new RepositoryNotFoundError(
        `Repository '${name}' was not found.`
      );
    }

    return {
      name,
      ...data[name],
    };
  }
}

class Workflow extends EventEmitter {
  transition(current, next) {
    const allowed = {
      [WorkflowState.DRAFT]: new Set([
        WorkflowState.OPEN,
        WorkflowState.CLOSED,
      ]),
      [WorkflowState.OPEN]: new Set([
        WorkflowState.MERGEABLE,
        WorkflowState.BLOCKED,
        WorkflowState.CLOSED,
      ]),
      [WorkflowState.MERGEABLE]: new Set([
        WorkflowState.MERGED,
        WorkflowState.BLOCKED,
        WorkflowState.CLOSED,
      ]),
      [WorkflowState.BLOCKED]: new Set([
        WorkflowState.OPEN,
        WorkflowState.CLOSED,
      ]),
      [WorkflowState.MERGED]: new Set(),
      [WorkflowState.CLOSED]: new Set(),
    };

    if (!allowed[current]?.has(next)) {
      throw new ValidationError(
        `Invalid workflow transition: ${current} -> ${next}`
      );
    }

    this.emit("transition", { from: current, to: next });
    return next;
  }
}

async function main() {
  const temporaryDirectory = await fs.mkdtemp(
    path.join(os.tmpdir(), "try-except-demo-")
  );

  const store = new RepositoryStore(
    path.join(temporaryDirectory, "repositories.json")
  );

  try {
    await store.save({
      name: "secure-platform",
      owner: "engineering",
      protected: true,
    });
    console.log("Repository saved.");
  } catch (error) {
    if (error instanceof ValidationError) {
      console.error(`Validation failed: ${error.message}`);
    } else if (error instanceof StorageError) {
      console.error(`Storage failed: ${error.message}`);
    } else {
      throw error;
    }
  }

  try {
    const repository = await store.get("secure-platform");
    console.log("Loaded:", repository);
  } catch (error) {
    console.error(`Lookup failed: ${error.message}`);
  }

  try {
    await store.get("unknown-repository");
  } catch (error) {
    if (error instanceof RepositoryNotFoundError) {
      console.log(`Expected lookup failure: ${error.message}`);
    } else {
      throw error;
    }
  }

  const decisions = [
    {
      sourceBranch: "feature/retry",
      targetBranch: "main",
      approvals: 2,
      requiredApprovals: 2,
      checksPassed: true,
      conversationsResolved: true,
    },
    {
      sourceBranch: "feature/check-failure",
      targetBranch: "main",
      approvals: 2,
      requiredApprovals: 2,
      checksPassed: false,
      conversationsResolved: true,
    },
    {
      sourceBranch: "feature/missing-review",
      targetBranch: "main",
      approvals: 1,
      requiredApprovals: 2,
      checksPassed: true,
      conversationsResolved: true,
    },
  ];

  for (const decision of decisions) {
    const result = evaluateMergePolicy(decision);
    console.log(`${result.state}: ${result.reason}`);
  }

  const workflow = new Workflow();

  workflow.on("transition", ({ from, to }) => {
    console.log(`Workflow transition: ${from} -> ${to}`);
  });

  try {
    let state = WorkflowState.DRAFT;
    state = workflow.transition(state, WorkflowState.OPEN);
    state = workflow.transition(state, WorkflowState.MERGEABLE);
    state = workflow.transition(state, WorkflowState.MERGED);
    console.log(`Final state: ${state}`);
  } catch (error) {
    if (error instanceof RepositoryError) {
      console.error(`Workflow error: ${error.message}`);
    } else {
      throw error;
    }
  }

  try {
    workflow.transition(WorkflowState.MERGED, WorkflowState.OPEN);
  } catch (error) {
    console.log(`Expected transition failure: ${error.message}`);
  }

  await fs.rm(temporaryDirectory, { recursive: true, force: true });
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exitCode = 1;
});
