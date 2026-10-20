# Lambda Functions

This project models Lambda functions as independently invocable units of serverless computation. The implementations focus on event-driven execution, stateless handlers, validation, retries, idempotency, routing, failure handling, timeout behavior, and operational reporting.

The five source files approach the same subject from different engineering perspectives rather than translating one implementation line by line.

## Core Model

A Lambda-style execution can be represented as:

`Event → Router → Function Invocation → Handler → Result or Failure`

The function is responsible for a bounded unit of computation. The surrounding platform is responsible for concerns such as invocation, routing, retries, concurrency, timeout enforcement, and operational monitoring.

The examples use an order-processing workflow:

`order.created → order-normalizer → order.validated → order-pricing → payment.requested → payment-processor`

The stages are deliberately separated. Validation and normalization are not the same operation as pricing, and payment processing has its own idempotency requirements.

## Lambda Function Mechanics

A Lambda function normally has a handler that receives an event and produces a result. The execution environment supplies invocation context such as a request identifier.

The examples model several important properties:

| Property | Meaning |
|---|---|
| Handler | The application function executed for an invocation |
| Event | Input supplied by an event source |
| Invocation | One execution attempt |
| Timeout | Maximum permitted execution duration |
| Memory | Configured runtime memory allocation |
| Request ID | Identifier used for tracing an invocation |
| Retry | Re-execution after an unsuccessful attempt |
| Idempotency | Protection against duplicate processing |
| Event routing | Mapping an event type to a function |

A function should avoid depending on process-local mutable state for durable application behavior. A runtime instance can be reused, replaced, or scaled independently of the application workflow.

## Python Implementation

The Python implementation models a Lambda runtime with the `LambdaFunction` class. It validates configuration, generates request identifiers, measures execution duration, captures handler failures, and returns a structured `InvocationResult`.

`normalize_order()` demonstrates a pure handler. It validates required fields, rejects invalid amounts, normalizes currency, and returns a new dictionary rather than mutating external state.

`calculate_discount()` represents a separate function with a separate responsibility. It applies order-specific pricing rules after normalization.

The `Event` data class represents an event envelope containing an event identifier, event type, payload, and timestamp.

`event_router()` separates event selection from handler execution. This is important because event routing and business logic are different responsibilities.

The retry implementation uses exponential backoff:

`delay = base_delay × 2^attempt`

Retries are useful for transient failures but can cause duplicate side effects. The Python example therefore emphasizes the need for idempotent handlers when a function can be invoked more than once.

The aggregation example uses `reduce()` for a functional calculation, while the production consideration is that large aggregations generally belong in an appropriate database or analytics system rather than inside an individual Lambda invocation.

## JavaScript Implementation

The JavaScript implementation uses asynchronous Node.js behavior to model event-driven Lambda execution.

`LambdaFunction.invoke()` uses `async` functions and `Promise.race()` to represent asynchronous execution with a timeout boundary.

The `EventBus` maps event names to Lambda functions. This produces a different architectural emphasis from the Python router: the JavaScript version treats event dispatch as an event-driven application component.

The implementation also demonstrates concurrent invocation with `Promise.all()`. Independent order events can therefore be processed concurrently rather than sequentially.

The idempotency wrapper maintains a set of processed keys. When the same idempotency key is received again, the handler returns a duplicate result instead of performing the business operation twice.

The local `Set` is intentionally only a model. A distributed production system cannot depend on a process-local set because different runtime instances may not share memory.

## C++ Implementation

The C++ program implements a repository-style runtime model using explicit classes and standard-library data structures.

`LambdaFunction` encapsulates:

- function configuration
- handler execution
- input validation
- invocation counting
- timeout measurement
- structured failure reporting

`LambdaRouter` uses `std::unordered_map` for event-to-function routing. Average lookup is O(1).

`IdempotencyStore` uses `std::unordered_set`, providing average O(1) membership and insertion operations.

`PricingEngine` is separated from execution infrastructure. This makes the business operation independently testable and prevents the Lambda runtime abstraction from becoming coupled to pricing rules.

The payment handler rejects duplicate idempotency keys. This illustrates an important serverless property: an invocation is not automatically equivalent to exactly-once business processing.

The program also demonstrates validation failure for negative amounts and reports invocation metrics.

## Java Implementation

The Java implementation models an enterprise-oriented serverless domain.

The `Order` record provides immutable domain data and validates its invariants when constructed.

`InvocationStatus` explicitly represents execution outcomes:

- `SUCCESS`
- `VALIDATION_FAILURE`
- `HANDLER_FAILURE`
- `TIMEOUT`
- `DUPLICATE`

This is useful in enterprise systems because a failed invocation can have materially different causes and operational responses.

`LambdaHandler<I, O>` is a generic functional abstraction for handler behavior. `LambdaFunction<I, O>` separates execution policy from the business handler.

`EventRouter` maps domain event types to strongly typed Lambda functions.

`IdempotencyRepository` models durable business protection conceptually. The sample uses an in-memory `HashSet`, but the source explicitly identifies the limitation: horizontally scaled production functions require shared durable storage.

`OrderPricingService` and `PaymentService` represent separate domain services rather than embedding every business rule inside the Lambda execution class.

## PostgreSQL Implementation

The SQL implementation represents Lambda operations relationally.

### Function Configuration

`lambda_functions` stores function name, runtime, memory, timeout, and enabled state.

Constraints enforce:

- non-empty function names
- minimum memory
- valid timeout ranges
- unique function names

This makes configuration validation a database-level responsibility where appropriate.

### Event Routing

`event_types` defines supported event categories.

`lambda_routes` associates functions with event types. The unique constraint prevents duplicate function-event registrations.

This models:

`event type → enabled route → Lambda function`

without placing routing information directly into invocation records.

### Invocation History

`invocation_events` records:

- invocation ID
- function
- event type
- idempotency key
- JSON payload
- status
- result
- error
- duration
- invocation time

`JSONB` is used for event and result payloads because event schemas can vary between function types while relational columns retain operational attributes that need indexing and aggregation.

### Database Validation

The `validate_invocation()` trigger prevents inconsistent invocation records.

A successful invocation must contain a result.

A failed or timed-out invocation must contain an error message.

These checks protect data integrity even when different applications write invocation records.

### Idempotency

The partial unique index:

`(function_id, idempotency_key) WHERE status = 'SUCCEEDED'`

prevents the same function from recording multiple successful executions for the same idempotency key.

The distinction between successful and failed invocations is deliberate. A transient failure should not necessarily prevent a later retry from succeeding.

### Transactional Recording

`record_invocation()` validates that the function exists, that the event type exists, and that an enabled route connects them before inserting an invocation.

The example transactions demonstrate atomic recording of invocation state and dead-letter information.

## Pull Request, Review, Approval, and Branch Protection Distinction

These concepts are not part of the Lambda implementation because they describe repository governance rather than function execution.

A Pull Request is a mechanism for proposing a set of source changes from one branch toward another branch.

Code Review evaluates those changes through review comments, review states, requested changes, and discussion resolution.

Approvals represent explicit reviewer decisions that may satisfy part of a repository's merge requirements.

Branch Protection is the repository-level enforcement layer that can require reviews, status checks, conversation resolution, linear history, or other conditions before a protected branch accepts a merge.

Their relationship can therefore be expressed as:

`Pull Request → Code Review → Approval Decisions → Branch Protection Evaluation → Merge`

Lambda execution is a separate runtime concern. A repository can contain Lambda source code, but branch governance determines whether that source code can be merged, while the Lambda platform determines how the deployed function executes.

## Failure and Retry Behavior

A failed Lambda invocation does not necessarily mean the underlying business operation is safe to repeat.

Transient failures may justify retries:

`Attempt 1 → failure → backoff → Attempt 2 → failure → backoff → Attempt 3`

Permanent validation failures should normally not be retried because the same invalid input will produce the same failure.

Examples include:

- missing required fields
- negative order amounts
- invalid configuration
- unsupported event types

Transient examples can include:

- temporary downstream unavailability
- network failures
- throttling
- short-lived service failures

The retry policy therefore needs to distinguish retryable failures from permanent failures.

## Idempotency

Idempotency is particularly important for event-driven functions.

Without idempotency:

`Event → Function → Side Effect`

can become:

`Event → Function → Side Effect → Retry → Duplicate Side Effect`

With an idempotency key:

`Event → Check Key → Process Once → Record Key`

A production idempotency mechanism should use durable shared storage with an atomic claim operation. An in-memory collection is insufficient when multiple function instances can execute concurrently.

## Stateless Execution

The implementations avoid treating local process memory as durable application state.

A serverless runtime can be:

- created for an invocation
- reused for later invocations
- recycled
- scaled to multiple instances
- terminated after inactivity

Application correctness should therefore not depend on a particular runtime instance remaining alive.

Temporary in-memory state can still be useful for caching or optimization, but correctness should come from durable systems.

## Timeout and Resource Boundaries

Timeouts limit how long a function may execute. Memory configuration affects the resources available to the runtime and can influence performance and cost depending on the serverless platform.

The source implementations model timeout validation and measurement but do not attempt to reproduce a cloud provider's actual billing or resource scheduler.

A production function should keep its execution scope appropriate to its configured timeout and avoid performing unbounded work inside one invocation.

## Performance Characteristics

The core data structures have the following expected characteristics:

| Operation | Data structure | Average complexity |
|---|---|---:|
| Event route lookup | Hash map | O(1) |
| Idempotency lookup | Hash set | O(1) |
| Pricing calculation | Scalar rules | O(1) |
| Invocation recording | Indexed relational insert | Approximately O(log n) index maintenance |
| Invocation aggregation | SQL aggregation | Depends on rows and indexes |

The database indexes focus on function/time retrieval, invocation status, and successful idempotency checks. Indexes should be introduced according to actual query patterns because unnecessary indexes increase write cost and storage usage.

## Security Considerations

Lambda handlers should validate untrusted event data before using it.

The examples validate:

- required identifiers
- numeric values
- positive amounts
- supported routing
- function configuration
- idempotency keys

Sensitive credentials should not be embedded in source code or event payloads. Production serverless applications should use the platform's secret-management facilities and grant functions only the permissions required for their specific operations.

Logging should also avoid exposing authentication credentials, payment credentials, or other sensitive payload fields.

## Operational Failure Modes

Important failure modes include:

| Failure | Appropriate response |
|---|---|
| Invalid input | Reject without repeated retries |
| Unknown event type | Routing failure |
| Function timeout | Record timeout and assess retry policy |
| Temporary downstream failure | Retry with bounded backoff |
| Repeated failure | Dead-letter or equivalent failure handling |
| Duplicate event | Apply idempotency protection |
| Runtime replacement | Do not depend on local durable state |
| Concurrent invocations | Use atomic shared-state operations |
| Excessive payload size | Validate and constrain event contracts |
| Slow downstream dependency | Apply timeout and failure isolation |

The SQL dead-letter table provides a durable location for events that require later inspection or recovery.

## Practical Architecture

The implementations collectively represent the following separation:

`Event Source`
  
`↓`

`Event Router`

`↓`

`Lambda Function`

`↓`

`Domain Handler`

`↓`

`Durable State / External Services`

`↓`

`Result + Metrics + Failure State`

The important architectural boundary is between execution infrastructure and business behavior. Lambda-style execution should remain small and bounded, while durable state, complex queries, and long-running workflows should be delegated to systems designed for those responsibilities.
