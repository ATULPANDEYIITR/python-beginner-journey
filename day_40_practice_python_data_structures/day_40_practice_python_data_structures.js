"use strict";

/*
 * Practice: Python Data Structures
 *
 * This companion implementation focuses on JavaScript's Map and Set
 * semantics, immutable transformations, event aggregation, and a bounded
 * event-processing queue. It runs with Node.js without external packages.
 */

function heading(title) {
  console.log(`\n${"=".repeat(68)}\n${title}\n${"=".repeat(68)}`);
}

function demonstrateArrayOperations() {
  heading("Arrays: ordered collections");

  const orders = [
    { id: "ORD-201", amount: 1200, status: "paid" },
    { id: "ORD-202", amount: 750, status: "pending" },
    { id: "ORD-203", amount: 2500, status: "paid" },
    { id: "ORD-204", amount: 500, status: "cancelled" },
  ];

  const paidOrders = orders.filter((order) => order.status === "paid");
  const paidTotal = paidOrders.reduce((sum, order) => sum + order.amount, 0);

  // map() returns a new array and does not modify the source array.
  const summaries = orders.map(({ id, amount, status }) => ({
    id,
    amount,
    status,
  }));

  // sort() mutates its receiver, so sort a copy when the source must be preserved.
  const highestValueFirst = [...orders].sort((a, b) => b.amount - a.amount);

  console.log("Paid total:", paidTotal);
  console.log("Order summaries:", summaries);
  console.log("Highest value order:", highestValueFirst[0]);

  const emptyAverage = (values) =>
    values.length === 0
      ? null
      : values.reduce((sum, value) => sum + value, 0) / values.length;

  console.log("Average of an empty list:", emptyAverage([]));
}

function demonstrateMapAndSet() {
  heading("Map and Set: keyed records and uniqueness");

  // Map supports arbitrary key types and avoids object-property coercion.
  const userRoles = new Map([
    ["u-101", "administrator"],
    ["u-102", "reviewer"],
    ["u-103", "contributor"],
  ]);

  userRoles.set("u-104", "reviewer");
  console.log("Role for u-102:", userRoles.get("u-102"));
  console.log("Unknown role:", userRoles.get("u-999"));

  const requestedRoles = new Set(["reviewer", "contributor", "reviewer"]);
  console.log("Unique requested roles:", [...requestedRoles]);

  const assignedUsers = new Set(userRoles.keys());
  const activeUsers = new Set(["u-101", "u-104", "u-105"]);

  const intersection = [...assignedUsers].filter((id) => activeUsers.has(id));
  const unassignedActive = [...activeUsers].filter(
    (id) => !assignedUsers.has(id)
  );

  console.log("Active assigned users:", intersection);
  console.log("Active users without assignments:", unassignedActive);

  // Objects compare by identity in Set, not by structural equality.
  const first = { code: "A1" };
  const second = { code: "A1" };
  console.log("Structurally equal objects are identical:", first === second);
  console.log("Both object references survive in a Set:", new Set([first, second]).size);
}

function demonstrateFrequencyIndex() {
  heading("Map-based frequency indexing");

  function buildFrequencyIndex(events) {
    const counts = new Map();

    for (const event of events) {
      if (typeof event !== "string" || event.trim() === "") {
        throw new TypeError("Every event must be a non-empty string");
      }

      const normalized = event.trim().toLowerCase();
      counts.set(normalized, (counts.get(normalized) ?? 0) + 1);
    }

    return counts;
  }

  const events = [
    "Login",
    "purchase",
    "login",
    "search",
    "purchase",
    "LOGIN",
  ];

  const counts = buildFrequencyIndex(events);
  const ranked = [...counts.entries()].sort(
    ([eventA, countA], [eventB, countB]) =>
      countB - countA || eventA.localeCompare(eventB)
  );

  console.log("Ranked events:", ranked);

  try {
    buildFrequencyIndex(["login", "  ", "logout"]);
  } catch (error) {
    console.log("Invalid event rejected:", error.message);
  }
}

class EventQueue {
  constructor(maxCapacity = 100) {
    if (!Number.isInteger(maxCapacity) || maxCapacity < 1) {
      throw new RangeError("maxCapacity must be a positive integer");
    }

    this.maxCapacity = maxCapacity;
    this.items = [];
    this.head = 0;
  }

  enqueue(event) {
    if (this.items.length - this.head >= this.maxCapacity) {
      throw new Error("Queue capacity exceeded");
    }

    this.items.push(event);
  }

  dequeue() {
    if (this.head >= this.items.length) {
      return undefined;
    }

    const item = this.items[this.head];
    this.head += 1;

    // Periodically compact the array so consumed items do not accumulate.
    if (this.head > 32 && this.head * 2 >= this.items.length) {
      this.items = this.items.slice(this.head);
      this.head = 0;
    }

    return item;
  }

  get size() {
    return this.items.length - this.head;
  }
}

function demonstrateEventQueue() {
  heading("Bounded event-processing queue");

  const queue = new EventQueue(3);
  queue.enqueue({ id: "EV-1", type: "login" });
  queue.enqueue({ id: "EV-2", type: "purchase" });
  queue.enqueue({ id: "EV-3", type: "logout" });

  try {
    queue.enqueue({ id: "EV-4", type: "search" });
  } catch (error) {
    console.log("Backpressure:", error.message);
  }

  while (queue.size > 0) {
    console.log("Consumed:", queue.dequeue());
  }

  console.log("Empty dequeue:", queue.dequeue());
}

function demonstrateObjectIndexing() {
  heading("Object indexes and safe property access");

  const inventory = Object.create(null);
  inventory["part-100"] = { quantity: 12, minimum: 5 };
  inventory["part-200"] = { quantity: 2, minimum: 8 };

  const lowStock = Object.entries(inventory)
    .filter(([, item]) => item.quantity < item.minimum)
    .map(([sku, item]) => ({ sku, ...item }));

  console.log("Low-stock items:", lowStock);

  // Object.create(null) has no inherited prototype keys.
  console.log("Prototype-free inventory:", Object.getPrototypeOf(inventory));

  // For arbitrary external keys, Map is often simpler and safer than a normal
  // object. Never assume input keys such as "__proto__" are ordinary data
  // properties on every object configuration.
}

function demonstrateStableDeduplication() {
  heading("Deduplication while preserving insertion order");

  function uniqueById(records) {
    const seen = new Set();
    const result = [];

    for (const record of records) {
      if (
        record === null ||
        typeof record !== "object" ||
        typeof record.id !== "string" ||
        record.id.trim() === ""
      ) {
        throw new TypeError("Each record requires a non-empty string id");
      }

      if (!seen.has(record.id)) {
        seen.add(record.id);
        result.push({ ...record });
      }
    }

    return result;
  }

  const records = [
    { id: "A-1", owner: "Operations" },
    { id: "A-2", owner: "Finance" },
    { id: "A-1", owner: "Duplicate import" },
  ];

  console.log("First record per ID:", uniqueById(records));
}

async function demonstrateAsynchronousAggregation() {
  heading("Asynchronous collection processing");

  const sources = [
    Promise.resolve(["login", "search"]),
    Promise.resolve(["purchase", "login"]),
    Promise.resolve(["search", "logout"]),
  ];

  // Promise.all preserves the input promise order in its result array.
  const batches = await Promise.all(sources);
  const allEvents = batches.flat();
  const counts = new Map();

  for (const event of allEvents) {
    counts.set(event, (counts.get(event) ?? 0) + 1);
  }

  console.log("Events across batches:", Object.fromEntries(counts));

  // A rejected promise makes Promise.all reject. A production ingestion
  // pipeline may use Promise.allSettled to retain successful batches.
  const partialResults = await Promise.allSettled([
    Promise.resolve(["accepted"]),
    Promise.reject(new Error("Source unavailable")),
  ]);

  console.log(
    "Batch outcomes:",
    partialResults.map((result) => result.status)
  );
}

function runAssertions() {
  const unique = new Set([1, 1, 2, 3]);
  if (unique.size !== 3) throw new Error("Set uniqueness check failed");

  const queue = new EventQueue(1);
  queue.enqueue("first");

  let rejected = false;
  try {
    queue.enqueue("second");
  } catch {
    rejected = true;
  }

  if (!rejected) throw new Error("Queue limit was not enforced");
  if (queue.dequeue() !== "first") throw new Error("Queue order is incorrect");
  if (queue.size !== 0) throw new Error("Queue size is incorrect");

  console.log("\nAll JavaScript data-structure checks passed.");
}

async function main() {
  demonstrateArrayOperations();
  demonstrateMapAndSet();
  demonstrateFrequencyIndex();
  demonstrateEventQueue();
  demonstrateObjectIndexing();
  demonstrateStableDeduplication();
  await demonstrateAsynchronousAggregation();
  runAssertions();
}

main().catch((error) => {
  console.error("Execution failed:", error);
  process.exitCode = 1;
});
