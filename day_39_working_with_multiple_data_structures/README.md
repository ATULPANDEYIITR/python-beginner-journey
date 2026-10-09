# Working with Multiple Data Structures

## Scope

A practical data-processing system rarely relies on a single collection. A workflow planner, for example, may need fast record lookup, predictable reporting order, unique labels, priority-based scheduling, dependency tracking, and a bounded activity history.

These requirements lead to different data structures because each structure optimizes a different operation. Choosing the correct combination requires understanding the operations the application performs, the relationships between records, and the invariants that must remain true as records change.

The implementations model an operations-planning workflow in which supplier validation precedes inventory reconciliation, analytics publication, and evidence archiving. The same records are represented through several complementary views, each serving a specific purpose.

## Core data structures and their distinct responsibilities

| Structure | Principal behavior | Application role |
|---|---|---|
| List or vector | Preserves sequence and supports indexed access | Stable reporting and insertion order |
| Dictionary, map, or hash map | Associates keys with values | Direct lookup of work items by identifier |
| Set | Stores unique elements and supports membership tests and set operations | Completed identifiers, labels, and category membership |
| Queue or deque | Processes elements in a defined order | Activity history and dependency-ready processing |
| Heap or priority queue | Retrieves the smallest or largest priority key efficiently | Scheduling the most urgent eligible work |
| Graph | Represents vertices and directed relationships | Work prerequisites and downstream dependencies |
| Counter or frequency map | Aggregates repeated values | Classification and operational summaries |
| Relational tables | Stores related records with integrity constraints | Persistent, queryable operational state |

These structures are related but not interchangeable. A set can efficiently determine whether an identifier is present, but it does not preserve meaningful insertion order as part of its contract. A list preserves sequence but does not enforce uniqueness. A heap prioritizes its root element but does not provide globally sorted iteration. A graph expresses relationships that would be cumbersome to represent as isolated records.

Combining structures is useful when an application needs several of these behaviors at the same time.

## Modeling a workflow with dependencies

Each work item has an identifier, title, department or category, priority, estimated effort, labels, prerequisites, and current status.

The dependency graph contains a directed edge from a prerequisite to the item that depends on it. If supplier validation must finish before inventory reconciliation, the validation item is a prerequisite for reconciliation.

An item is eligible to start only when all its prerequisites are completed. This is a separate condition from priority. An urgent task can remain blocked when its prerequisites are incomplete.

The workflow uses three states:

- `pending`: the item has not started.
- `in_progress`: the item has started and has not completed.
- `completed`: the item has finished.

Valid transitions are `pending` to `in_progress` and `in_progress` to `completed`. A transition back to `pending`, or direct completion without starting, is rejected by the application models.

### Maintaining consistent representations

When an item is registered, the system updates its primary lookup structure, its reporting sequence, its category index, and its dependency representation. These are multiple representations of the same underlying entity.

This arrangement improves lookup and reporting performance but creates an invariant-management responsibility. Every update must keep the representations consistent. If an item is removed from the primary map but remains in a category index, category queries may return a nonexistent item.

The examples avoid implementing record deletion because deleting a node that has dependents requires a deliberate policy. Possible policies include rejecting deletion, cascading deletion, or retaining a historical record. The appropriate choice depends on the application.

## Python implementation

The Python program defines `WorkItem` as a dataclass and `WorkQueue` as a coordinator for several data structures.

The `items` dictionary maps identifiers to mutable domain objects. `insertion_order` preserves a stable sequence for reports. `categories` maps each category to a set of identifiers. `completed_ids` provides fast membership checks when evaluating prerequisites. `dependencies` stores prerequisite relationships, and the bounded `activity` deque retains recent events without allowing history to grow indefinitely.

### Tag queries and aggregation

`search_tags` implements an AND search. An item matches only when the required tag set is a subset of the item's tags. The set inclusion operation expresses the requirement directly instead of checking each tag through separate application-level loops.

`effort_by_category` aggregates estimated hours into a dictionary. A `defaultdict(float)` makes accumulation straightforward, while the returned ordinary dictionary provides a simple result for display or serialization.

The record-validation function demonstrates a different combination of structures. A list retains accepted records, another list retains rejected records with their error details, and a set detects duplicate identifiers. The validation rejects negative amounts and explicitly rejects Boolean values as numeric amounts because Python's `bool` type is a subclass of `int`.

### Priority queues and dependency graphs

The pending heap stores tuples containing priority and identifier. Python's heap implementation retrieves the smallest tuple first, making lower numeric priorities more urgent in this model. The identifier acts as a deterministic tie-breaker.

Heap entries can become stale when the status of an item changes. The scheduler therefore checks the authoritative item state before using a heap entry. The heap does not itself establish dependency eligibility; that rule belongs to the workflow model.

The `dependency_order` method uses Kahn's topological sorting algorithm. It calculates incoming-edge counts, queues nodes with zero incoming edges, and progressively releases dependent nodes. If the number of emitted nodes is smaller than the number of items, a cycle exists.

The cycle test deliberately introduces a reverse dependency to verify that the algorithm rejects an invalid graph. A production system should validate graph changes before committing them rather than relying on a later reporting operation to discover the problem.

### Serialization and verification

`snapshot` converts sets and dataclass instances into JSON-compatible dictionaries and lists. `export_json` writes UTF-8 JSON to a file. This explicit conversion is necessary because the standard JSON encoder does not directly serialize arbitrary sets or domain objects.

The unit tests cover duplicate identifiers, blocked transitions, prerequisite completion, dependency cycles, and Boolean validation. They verify domain behavior rather than merely checking whether the script starts.

## JavaScript implementation

The JavaScript file uses Node.js and its standard library to model an event-driven workflow.

`WorkflowStore` uses `Map` for identifier-based record lookup and category membership, and `Set` for tags and completed identifiers. These choices make membership and keyed updates explicit. The class extends `EventEmitter`, allowing consumers to react to state transitions without embedding all event-handling behavior in the state-management methods.

### Event-driven state changes

The `record` method assigns a monotonically increasing revision, creates an event object, appends it to the activity history, and emits an event. Revision numbers provide a local ordering mechanism for the recorded events.

`Object.freeze` prevents ordinary mutation of the event and its payload after creation. This is shallow immutability; nested objects would require additional handling if they were present. The store retains its own mutable domain objects, while emitted events represent recorded state changes.

The `transition` method checks the current state and the requested next state. It separately validates prerequisites before allowing a task to start. This separation prevents a valid-looking state transition from bypassing a dependency rule.

### Asynchronous persistence

The persistence demonstration uses Node.js promise-based filesystem operations. It creates a temporary directory, serializes the workflow state, reads the file back, and verifies the record count. A `finally` block removes temporary files even if an assertion or filesystem operation fails.

The file is written with the exclusive-create flag, which prevents accidentally overwriting an existing file at that path. This is appropriate for the temporary demonstration but is not a substitute for transactional database persistence in a multi-process production service.

The event-driven design is useful when other components need to update a dashboard, send notifications, or record operational metrics in response to state changes. Production event consumers must account for failures, retries, duplicate delivery, and the possibility that a consumer receives an event after the underlying state has changed again.

## C++ case study: operations planning

The C++ program models operational work orders with a focus on explicit data ownership, deterministic reporting, and graph processing.

`OperationsPlanner` uses an `unordered_map` for identifier lookup, a vector for insertion order, a map of departments to sets of work-order identifiers, and a reverse dependency map for traversing downstream work.

The unordered map provides average constant-time lookup under normal hash-distribution assumptions. It does not guarantee sorted iteration. The vector therefore serves a different purpose: preserving the order in which records were registered.

### Dependency traversal

The reverse dependency map stores the dependents of each prerequisite. Kahn's algorithm uses incoming-edge counts to determine which work orders can appear next in a valid dependency ordering.

For a graph with \(V\) vertices and \(E\) edges, topological sorting runs in \(O(V + E)\) time when graph traversal operations are constant-time on average. The program checks whether every work order appears in the resulting order and reports a cycle if the graph is not acyclic.

`readyOrders` evaluates current eligibility separately from topological ordering. Topological ordering establishes a valid ordering of the dependency graph; readiness additionally depends on runtime completion state.

### Input and state validation

The registration method rejects empty identifiers, duplicate identifiers, invalid priorities, non-finite effort estimates, negative effort, repeated dependencies, self-dependencies, and references to unknown prerequisites.

The transition method rejects attempts to start blocked work or complete work that has not started. Exceptions allow the caller to handle these failures at the system boundary instead of silently accepting invalid state.

The example uses standard-library containers and requires no external dependencies. In a larger concurrent application, synchronization would be required around shared mutable state. Hash-map complexity is also average-case rather than an unconditional worst-case guarantee.

## Java implementation: enterprise workflow modeling

The Java program uses records, enums, immutable collection copies, a service class, and explicit state transitions to represent an operations workflow.

`WorkRequest` is a record that validates incoming domain data. Its compact constructor copies the label and dependency collections into immutable representations, preventing a caller from modifying the request indirectly through a collection reference retained elsewhere.

`WorkItem` separates immutable request details from mutable lifecycle state. This distinction prevents ordinary status updates from changing the original title, department, labels, or dependency declaration.

### Typed state and collection behavior

`WorkStatus` and `Department` are enums rather than arbitrary strings. Invalid department names and unsupported status values therefore cannot enter the domain model as ordinary string values.

`PlanningService` uses a `LinkedHashMap` to preserve registration order while providing keyed access. An `EnumMap` indexes department membership efficiently by enum keys. A `HashSet` tracks completed identifiers, and a bounded `ArrayDeque` retains recent activity.

The effort report uses `Map.merge` with `Double::sum` to accumulate values by department. The label search uses streams and `containsAll`, expressing a requirement that every requested label must exist on a record.

The `PriorityQueue` represents the scheduling mechanism. The service still checks current readiness independently, because a priority queue cannot by itself enforce prerequisites or guarantee that all entries represent currently eligible work.

### State transitions and exceptions

The domain object permits only the defined transitions. The service performs dependency checks before invoking the transition method, keeping orchestration rules separate from the basic lifecycle rules.

A production service would normally also centralize authorization, persistence transactions, concurrent-update detection, and durable audit records. Immutable request data and typed states improve clarity but do not automatically provide thread safety for the mutable service.

## SQL implementation: relational integrity and reporting

The PostgreSQL script represents the same class of operational workflow as relational records.

### Relational model

- `departments` stores the permitted department records.
- `work_items` stores the main domain entities and their lifecycle states.
- `work_tags` models the many-to-many relationship between work items and labels.
- `work_dependencies` models directed prerequisite relationships between work items.
- `work_activity` records status-transition events.

Primary keys uniquely identify records. Foreign keys prevent references to nonexistent departments or work items. Unique constraints prevent duplicate item codes and department names. Check constraints enforce priority ranges, non-negative estimated effort, non-empty titles, and valid status values.

The composite primary key on `work_tags` prevents assigning the same tag to an item more than once. The composite key on `work_dependencies` prevents duplicate dependency edges. A separate check constraint rejects direct self-dependencies.

### Database-level workflow enforcement

The status-transition trigger allows only `pending` to `in_progress` and `in_progress` to `completed`. It also rejects starting an item whose prerequisites are unfinished, records the transition, and sets the completion timestamp.

The recursive trigger function for dependency insertion checks reachability before accepting a new edge. It rejects a dependency that would introduce a cycle. This protects the relational graph from a class of errors that ordinary foreign keys do not prevent.

The demonstration assumes serialized dependency-graph modifications. Concurrent transactions that add conflicting edges may require stronger coordination or a transaction-level locking strategy to prevent write-skew anomalies.

### Views, queries, and indexes

`ready_work_items` selects pending items for which no unfinished prerequisite exists. This query translates the dependency-eligibility rule into a relational anti-join expressed with `NOT EXISTS`.

The tag query uses nested `NOT EXISTS` expressions to implement relational division: a result is returned only when every required tag is present.

`category_effort` groups records by department and calculates item counts, total estimated hours, and completed-item counts. PostgreSQL's filtered aggregate counts only rows that meet the specified condition.

The indexes support status-and-priority filtering, department-based reporting, reverse dependency traversal, tag lookup, and chronological activity queries. Indexes impose storage and update costs, so their value depends on actual query patterns and table size.

The transaction and savepoint demonstrate how a state-change example can be rolled back without discarding the rest of the script. The final commit preserves the schema and sample records while leaving the demonstrated prerequisite in its original pending state.

## Cross-language design distinctions

The implementations share a domain problem, but they do not impose identical collection choices or architecture.

| Concern | Python | JavaScript | C++ | Java | PostgreSQL |
|---|---|---|---|---|---|
| Keyed lookup | Dictionary | `Map` | `unordered_map` | `LinkedHashMap` | Primary-key indexes |
| Unique membership | `set` | `Set` | `set` and `unordered_set` | `HashSet` | Unique and composite constraints |
| Priority selection | `heapq` | Readiness sort | Sorted eligible work | `PriorityQueue` | Indexed filtering and ordering |
| Dependency relationships | Dictionary of sets | Sets inside map-backed records | Reverse adjacency map | Immutable dependency lists | Foreign-key relationship table |
| State enforcement | Domain methods | Transition method | Transition method | Typed domain objects | Trigger and check constraints |
| Persistence | JSON file | Asynchronous JSON file | In-memory case study | In-memory case study | Relational transaction |

The choice of structure should follow the required operations, not a desire to use as many structures as possible. Maintaining multiple indexes is justified when their query benefits exceed the memory and consistency costs.

## Complexity and operational trade-offs

Dictionary and hash-map lookups are typically \(O(1)\) on average. Balanced-tree maps and sets typically provide \(O(\log n)\) lookup and update operations while retaining sorted order. Hash-based collections generally trade ordering guarantees for average lookup speed.

Set intersection depends on the implementation and collection sizes. For sorted sets, an intersection can be performed in time proportional to the combined input sizes. For hash-based sets, membership-based intersection is commonly proportional to the size of the smaller collection when the other set supports expected constant-time membership tests.

A heap supports insertion and removal of the highest-priority entry in \(O(\log n)\) time, with access to its root in \(O(1)\) time. It does not support efficient arbitrary deletion without an auxiliary indexing strategy.

A dependency graph requires explicit cycle handling. The cost of validation becomes increasingly important as the number of relationships grows. Topological sorting is linear in the number of vertices and edges, but validating every proposed edge through a full graph traversal can become expensive when updates are frequent.

Relational constraints provide durable enforcement across multiple application clients, while in-memory checks provide immediate feedback within an individual service. A robust system often needs both. Database enforcement does not replace application-level error messages, and application validation does not replace database integrity constraints.

## Failure modes and production considerations

Several failures arise specifically because a single entity is represented in multiple structures.

- **Stale secondary indexes:** updating a primary record without updating its category or tag index can produce inconsistent query results.
- **Invalid references:** a dependency may point to a nonexistent item unless registration or a foreign key rejects it.
- **Dependency cycles:** mutually dependent items cannot be ordered into a valid execution sequence.
- **Stale scheduling entries:** an item may remain represented in a heap after its state changes, requiring lazy invalidation or an indexed priority queue.
- **Illegal transitions:** a caller may attempt to complete work before it starts or start work before prerequisites finish.
- **Invalid numeric values:** negative effort, non-finite floating-point values, and Boolean values mistakenly accepted as numbers can corrupt operational calculations.
- **Unbounded history:** retaining every event indefinitely can consume excessive memory. Bounded in-memory history is useful for recent activity, while complete audit history normally belongs in durable storage.
- **Concurrent updates:** two workers may simultaneously evaluate the same item as ready. Production systems need locking, atomic claims, optimistic concurrency, or equivalent coordination.
- **Partial persistence:** writing a file and updating an in-memory index are not a single atomic operation. A database transaction or an explicit recovery protocol is needed when several state changes must succeed together.

These are not merely language-specific concerns. They follow from the underlying requirement to keep multiple representations of related information consistent.

## Running the implementations

The Python script uses the standard library and runs with Python 3.10 or later. It includes executable demonstrations and a `unittest` test suite.

The JavaScript file targets Node.js with support for private-free standard collection APIs, promise-based filesystem operations, and `EventEmitter`. It uses only built-in modules.

The C++ program requires a C++17-compatible compiler. The Java program requires Java 17 or later.

The SQL script targets PostgreSQL and uses PL/pgSQL triggers, recursive common table expressions, filtered aggregates, identity columns, and transaction savepoints. It should be executed against a PostgreSQL database in which the executing role has permission to create and drop the demonstration objects.

The relational script intentionally recreates its own demonstration tables. It should be run in a dedicated practice database or schema because its initial statements drop objects with the same names.
