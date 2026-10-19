"use strict";

/*
 * Recursion in JavaScript
 *
 * This program focuses on JavaScript-specific recursive behavior:
 * call-stack growth, closures, asynchronous recursion, event-driven
 * traversal, object graphs, divide-and-conquer, and memoization.
 */

function factorial(n) {
  if (!Number.isSafeInteger(n)) {
    throw new TypeError("factorial requires a safe integer");
  }
  if (n < 0) {
    throw new RangeError("factorial requires n >= 0");
  }
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}

function fibonacciMemoized(n, memo = new Map([[0, 0], [1, 1]])) {
  if (!Number.isSafeInteger(n) || n < 0) {
    throw new RangeError("n must be a non-negative safe integer");
  }

  if (memo.has(n)) return memo.get(n);

  const value =
    fibonacciMemoized(n - 1, memo) +
    fibonacciMemoized(n - 2, memo);

  memo.set(n, value);
  return value;
}

function recursiveReduce(values, index = 0, accumulator = 0) {
  if (index === values.length) return accumulator;
  return recursiveReduce(
    values,
    index + 1,
    accumulator + values[index]
  );
}

function binarySearch(values, target, low = 0, high = values.length - 1) {
  if (low > high) return -1;

  const middle = low + Math.floor((high - low) / 2);

  if (values[middle] === target) return middle;
  if (target < values[middle]) {
    return binarySearch(values, target, low, middle - 1);
  }

  return binarySearch(values, target, middle + 1, high);
}

function mergeSort(values) {
  if (values.length <= 1) return [...values];

  const middle = Math.floor(values.length / 2);
  const left = mergeSort(values.slice(0, middle));
  const right = mergeSort(values.slice(middle));

  const result = [];
  let i = 0;
  let j = 0;

  while (i < left.length && j < right.length) {
    if (left[i] <= right[j]) {
      result.push(left[i++]);
    } else {
      result.push(right[j++]);
    }
  }

  return result.concat(left.slice(i), right.slice(j));
}

class TreeNode {
  constructor(value) {
    this.value = value;
    this.left = null;
    this.right = null;
  }
}

function insert(root, value) {
  if (root === null) return new TreeNode(value);

  if (value < root.value) {
    root.left = insert(root.left, value);
  } else if (value > root.value) {
    root.right = insert(root.right, value);
  }

  return root;
}

function inorder(root, output = []) {
  if (root === null) return output;

  inorder(root.left, output);
  output.push(root.value);
  inorder(root.right, output);

  return output;
}

function evaluateExpression(node) {
  /*
   * The tree is an AST-like object. Recursive evaluation naturally
   * follows the expression's nested structure.
   */
  if (typeof node === "number") return node;

  if (!node || typeof node !== "object") {
    throw new TypeError("invalid expression node");
  }

  const left = evaluateExpression(node.left);
  const right = evaluateExpression(node.right);

  switch (node.operator) {
    case "+":
      return left + right;
    case "-":
      return left - right;
    case "*":
      return left * right;
    case "/":
      if (right === 0) throw new RangeError("division by zero");
      return left / right;
    default:
      throw new Error(`unsupported operator: ${node.operator}`);
  }
}

function flatten(value, output = []) {
  if (!Array.isArray(value)) {
    output.push(value);
    return output;
  }

  for (const item of value) {
    flatten(item, output);
  }

  return output;
}

function generatePermutations(items) {
  if (items.length <= 1) return [items.slice()];

  const result = [];

  for (let index = 0; index < items.length; index += 1) {
    const selected = items[index];
    const remaining = items
      .slice(0, index)
      .concat(items.slice(index + 1));

    for (const suffix of generatePermutations(remaining)) {
      result.push([selected, ...suffix]);
    }
  }

  return result;
}

function createAsyncRecursiveProcessor(items, index = 0, output = []) {
  /*
   * setTimeout schedules the next recursive step as a new event-loop
   * callback. Unlike synchronous recursion, each completed callback
   * returns before another callback is executed.
   */
  if (index >= items.length) {
    return Promise.resolve(output);
  }

  return new Promise((resolve) => {
    setTimeout(() => {
      output.push({
        item: items[index],
        processedAt: new Date().toISOString()
      });

      resolve(
        createAsyncRecursiveProcessor(items, index + 1, output)
      );
    }, 0);
  });
}

function walkFileSystem(node, path = node.name, result = []) {
  result.push(path);

  if (node.children) {
    for (const child of node.children) {
      walkFileSystem(child, `${path}/${child.name}`, result);
    }
  }

  return result;
}

function safeRecursiveDepth(depth) {
  if (!Number.isSafeInteger(depth) || depth < 0) {
    throw new RangeError("depth must be a non-negative safe integer");
  }

  if (depth > 5000) {
    throw new RangeError(
      "depth intentionally limited to avoid exhausting the JavaScript call stack"
    );
  }

  if (depth === 0) return 0;
  return 1 + safeRecursiveDepth(depth - 1);
}

function run(name, operation) {
  try {
    console.log(`${name}:`, operation());
  } catch (error) {
    console.log(`${name}: ${error.name}: ${error.message}`);
  }
}

async function main() {
  console.log("=== Fundamental recursion ===");
  run("factorial(6)", () => factorial(6));
  run("factorial(-2)", () => factorial(-2));
  run("memoized fibonacci(30)", () => fibonacciMemoized(30));

  console.log("\n=== Recursive data processing ===");
  const values = [18, 4, 27, 9, 13, 2];
  run("recursive sum", () => recursiveReduce(values));
  run("binary search for 13", () => binarySearch([2, 4, 9, 13, 18, 27], 13));
  run("merge sort", () => mergeSort(values));

  console.log("\n=== Recursive object tree ===");
  let root = null;
  for (const value of [50, 30, 70, 20, 40, 60, 80]) {
    root = insert(root, value);
  }
  console.log("inorder:", inorder(root));

  console.log("\n=== Recursive expression evaluation ===");
  const expression = {
    operator: "*",
    left: {
      operator: "+",
      left: 8,
      right: 4
    },
    right: {
      operator: "-",
      left: 10,
      right: 3
    }
  };
  run("((8 + 4) * (10 - 3))", () => evaluateExpression(expression));

  console.log("\n=== Nested arrays ===");
  run(
    "flatten",
    () => flatten([1, [2, [3, 4]], [[5], 6]])
  );

  console.log("\n=== Recursive combinatorial generation ===");
  run(
    "permutations",
    () => generatePermutations(["A", "B", "C"])
  );

  console.log("\n=== Recursive hierarchy traversal ===");
  const fileSystem = {
    name: "repository",
    children: [
      {
        name: "src",
        children: [
          { name: "index.js" },
          { name: "parser.js" }
        ]
      },
      {
        name: "tests",
        children: [
          { name: "parser.test.js" }
        ]
      }
    ]
  };

  console.log("paths:", walkFileSystem(fileSystem));

  console.log("\n=== Asynchronous recursion ===");
  const processed = await createAsyncRecursiveProcessor([
    "commit",
    "review",
    "test",
    "merge"
  ]);
  console.log("processed events:", processed);

  console.log("\n=== Recursion depth ===");
  run("safe depth 50", () => safeRecursiveDepth(50));
  run("negative depth", () => safeRecursiveDepth(-1));

  console.log("\n=== Important JavaScript behavior ===");
  console.log(
    "Synchronous recursion consumes the JavaScript call stack; JavaScript engines do not generally guarantee tail-call optimization."
  );
  console.log(
    "Memoization changes repeated recursive computation from exponential recomputation to approximately linear work for Fibonacci."
  );
  console.log(
    "Asynchronous recursion using timers yields control to the event loop between recursive steps."
  );
  console.log(
    "Recursive tree traversal matches hierarchical object structures naturally, while very deep or attacker-controlled input should be depth-limited or processed iteratively."
  );
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exitCode = 1;
});
