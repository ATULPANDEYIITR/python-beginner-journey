# Function Parameters and Arguments

## Purpose and scope

Function parameters and arguments define the interface through which a function receives information and communicates with its caller. Parameters are declared in a function definition. Arguments are the values or expressions supplied when the function is invoked.

A reliable function interface specifies which inputs are required, how optional values behave, how callers identify inputs, which types are accepted, and what happens when supplied values violate a contract. These decisions influence correctness, readability, testability, API compatibility, and the ability to evolve a software system.

The implementations in this collection examine these concerns through financial calculations, procurement pricing, payment authorization, data transformation, and file processing. Each language exposes a different set of mechanisms for expressing and enforcing an argument contract.

## Terminology and core mechanics

### Parameters and arguments

Consider a function that calculates an order line total:

`calculate_total(price, quantity)`

Here, `price` and `quantity` are parameters. In the call `calculate_total(250.0, 3)`, the values `250.0` and `3` are arguments.

The distinction matters when diagnosing errors. A parameter defines what the function expects; an argument supplies what the caller actually provides. A mismatch can produce a binding error, a type error, an invalid business result, or an exception during execution.

### Positional and named arguments

Positional arguments are matched to parameters according to their positions. They are concise when a function has a small number of inputs with an obvious order.

Named arguments identify parameters explicitly. They improve readability when several arguments have similar types, such as a tax rate and a discount rate. They can also make calls less sensitive to changes in the order of optional parameters.

Python supports named arguments directly. JavaScript commonly uses an object with named properties to obtain similar clarity. C++ offers overloads, domain structures, and named fields as alternatives to long positional call lists. Java commonly groups related configuration values in records or immutable classes. PostgreSQL supports named notation in function calls.

Named arguments do not eliminate validation. A correctly named argument may still contain an invalid value.

### Required and optional inputs

Required parameters represent information necessary for a valid operation. Optional parameters allow a caller to omit a value when a well-defined default is appropriate.

A default should represent a defensible business rule rather than hide missing data. For example, a default quantity of one may be reasonable for a line-item calculation. A default payment amount is not reasonable because it could conceal a missing transaction value.

Default behavior differs by language. Python evaluates default expressions when a function is defined, which makes mutable default objects particularly important. JavaScript applies default parameter expressions when an argument is omitted or is `undefined`, but not when it is `null`. PostgreSQL defaults apply when an eligible argument is omitted; an explicit SQL `NULL` remains a distinct value.

### Variadic arguments

Variadic functions accept a variable number of arguments. They are useful for aggregations, batch operations, and generic processing.

Python's `*args` collects extra positional arguments into a tuple, while `**kwargs` collects extra named arguments into a dictionary. JavaScript's rest parameter collects remaining positional arguments into an array. C++ parameter packs support generic functions over multiple argument types. PostgreSQL provides `VARIADIC` parameters backed by arrays.

A variadic interface must define what happens when no values are supplied and how invalid elements are handled. An average of zero values, for example, is undefined and should not silently return an arbitrary result.

## Argument binding and interface design

Argument binding associates supplied values with declared parameters. Languages enforce different parts of this process at different stages.

Python checks argument names, positions, required parameters, and many duplicate-value errors when a function is called. Its `inspect.signature` and `Signature.bind` mechanisms support runtime introspection and explicit validation of a proposed call.

JavaScript uses positional binding for ordinary parameters. Functions with many options benefit from a single destructured configuration object. Validation must account for the language's dynamic values, including `null`, `undefined`, `NaN`, and non-finite numbers.

C++ performs much of its argument matching at compile time. Overloads and templates provide type-directed selection, while references determine whether objects are copied, mutated, or forwarded. Runtime checks remain necessary for business constraints such as non-negative quantities.

Java uses declared parameter types, overload resolution, records, and interfaces to make contracts explicit. Runtime validation is still necessary because a value can satisfy its declared type while violating a business rule.

PostgreSQL resolves functions using their names, parameter types, and signatures. Overloads must be designed carefully when defaults or implicit type conversions could make a call ambiguous. Explicit casts and named notation help make intent clear.

## Python implementation

The Python script progresses from direct argument matching to more advanced function interfaces.

### Basic binding and defaults

`calculate_total` shows positional, named, and mixed argument calls. `calculate_invoice` accepts a quantity, tax rate, and discount with defaults. It validates monetary inputs and rounds the result to two decimal places.

`convert_temperature` uses positional-only and keyword-only parameters. The slash in its signature prevents callers from naming the first parameter, while the asterisk requires the unit to be supplied by name. This makes the intended call structure explicit.

### Variadic inputs and object references

`sum_values` accepts an arbitrary number of numeric inputs through `*args`. `build_profile` uses `**kwargs` to collect optional attributes.

`append_event` demonstrates a safe alternative to a mutable list default. Using `None` and constructing a list inside the function ensures independent calls do not share unintended state.

The functions `replace_local` and `mutate_shared` demonstrate Python's object-reference behavior. Rebinding a local parameter does not replace the caller's variable. Mutating a list referenced by both caller and function is visible to the caller.

### Introspection, decorators, and higher-order functions

`inspect_parameters` uses the standard library's inspection facilities to report parameter kinds and defaults. `validate_arguments` binds proposed arguments against a callable's signature before invoking it.

The `traced` decorator forwards positional and keyword arguments through `*args` and `**kwargs`. `functools.wraps` preserves metadata that would otherwise describe the wrapper rather than the original function.

`transform_all` accepts a transformation function as an argument. `partial` creates a callable with selected arguments already bound, as demonstrated by the configured invoice calculation.

### Structured data and failure handling

The immutable `Measurement` record groups related values into one domain object. `summarize_measurements` combines variadic positional objects with a keyword-only setting.

`load_json` demonstrates bounded file reading, encoding selection, JSON parsing, and explicit error handling for missing files and malformed input. The tests verify binding rules, validation, mutation behavior, partial application, and expected failures.

The script uses only the Python standard library and executes its tests when run directly.

## JavaScript implementation

The JavaScript file concentrates on dynamic argument contracts, immutable configuration, closures, callbacks, and asynchronous execution.

### Destructured options

`createPullRequest` accepts a single object containing a title, source branch, target branch, draft flag, and labels. The default parameter handles an omitted options object, while property defaults provide values for optional fields.

The returned object is frozen, and the labels array is copied and frozen. This prevents callers from changing the original array through the returned object. It is a useful boundary pattern when configuration should remain stable after validation.

`paginate` accepts its page number, page size, and sorting direction through an options object. It validates the settings before calculating the offset and returning a page. The source array is copied before sorting so the function does not unexpectedly mutate caller-owned data.

### Rest, spread, and closures

`average` receives an arbitrary number of arguments through a rest parameter. The call using `average(...measurements)` demonstrates spread syntax, which expands an iterable into individual arguments.

`createAmountValidator` returns a function that retains the selected minimum and maximum in its closure. Each generated validator has independent configuration without requiring shared mutable global state.

`processRecords` accepts both a selector and a predicate as callback arguments. This separates record selection from record transformation, allowing the same processing function to support different policies.

### Auditing and asynchronous calls

`withAudit` wraps a callable and forwards its arguments with `apply`. The wrapper records the operation name and argument count without logging the supplied values, reducing the risk of exposing sensitive data.

`fetchReleaseMetadata` demonstrates an asynchronous argument contract with an injectable transport function. Its timeout uses `Promise.race` and clears the timer after completion. The timeout bounds the caller's wait, but it does not automatically cancel the underlying transport. Cancellation requires cooperation from that transport, typically through an abort signal.

The automated checks cover defaults, invalid numeric inputs, request construction, callbacks, closure state, audit forwarding, successful asynchronous results, and timeout behavior.

## C++ case study: procurement pricing

The C++ program models an industrial procurement calculation involving multiple purchase lines, a pricing policy, an optional discount, and an optional shipping override.

### Parameter passing decisions

`line_total` receives a purchase line through a constant reference. This avoids copying the string and other members while preventing accidental mutation.

`calculate_purchase` receives the line collection and pricing policy through constant references. The discount and shipping override are small numeric values, so they are passed by value. A sentinel indicates that shipping should be calculated from the policy.

The alternative overload accepts `std::optional<double>` values. It represents absence explicitly rather than requiring callers to interpret a special negative value. This illustrates an important interface trade-off: sentinel values can be compact, but explicit optional types communicate intent more accurately.

### Result objects and validation

`CostBreakdown` returns subtotal, discount, taxable amount, tax, shipping, and final total as one structured result. Returning a structure avoids a long list of output parameters and keeps the calculated values associated with one purchase.

Validation rejects negative prices, invalid quantities, non-finite rates, excessive discounts, empty purchases, and arithmetic overflow. The calculation applies the discount before tax and computes shipping according to the configured policy or caller override.

`try_parse_quantity` uses reference output parameters to return both a parsed quantity and an error message. This is useful for demonstrating a traditional C++ interface, although a result structure or an expected-like type can be preferable in larger systems.

### Generic forwarding and callbacks

`invoke_checked` uses a variadic template, forwarding references, `std::forward`, and `std::invoke` to pass arguments through to another callable. This preserves the relevant value categories and avoids unnecessary copies when the wrapped operation supports them.

`sum_selected` accepts a callback that decides which purchase lines contribute to a total. The selection policy is supplied by the caller rather than hard-coded into the aggregation function.

The case study illustrates the balance between compile-time type safety, explicit domain structures, runtime validation, and flexible callable interfaces. It requires C++17 and the standard library only.

## Java implementation: enterprise payment processing

The Java program models a payment service with explicit request validation, policy evaluation, authorization, and state reporting.

### Domain types and immutable inputs

`PaymentRequest` is a record containing the request identifier, account, amount, currency, and payment channel. Its compact constructor rejects blank identifiers, invalid currency codes, null values, and non-positive amounts.

`PaymentPolicy` groups the single-payment limit, daily account limit, partner-channel setting, and blocked accounts. It copies the blocked-account list to avoid retaining a caller-owned mutable list.

Grouping related parameters in records is preferable to accepting a large sequence of unrelated strings, booleans, and numbers. The compiler enforces the declared types, while constructors enforce business constraints.

### Explicit policy evaluation

`validateAmount` checks an amount against the single-payment limit. `validateRequest` combines that result with account restrictions and channel availability.

The `PaymentAuthorizer` interface represents a replaceable authorization strategy. `processPayment` accepts the request, policy, and strategy as separate parameters, keeping transaction data, configuration, and behavior distinct.

The service records state transitions in an immutable result. Invalid requests are rejected before authorization. An authorization denial or runtime failure also results in rejection, demonstrating a fail-closed decision for this example.

The daily account limit is used by the sample authorization strategy. A production implementation would need authoritative, concurrency-safe accounting of cumulative daily spending; comparing a single payment with the daily limit alone cannot enforce an aggregate daily limit.

### Generic transformations and monetary arithmetic

`mapValidated` accepts a predicate and mapper through Java functional interfaces. It filters and transforms values with a typed stream pipeline and returns an unmodifiable list.

`calculateFee` uses `BigDecimal` instead of binary floating-point arithmetic for monetary values. It calculates a proportional fee, applies a minimum fee, and rounds to two decimal places. The selected rounding mode and currency scale should be aligned with the applicable financial rules in a production service.

The program checks successful authorization, policy rejection, blocked accounts, disabled channels, and authorization-service failures. These checks make parameter contracts part of an explicit domain workflow rather than relying on printed examples alone.

## SQL implementation: parameterized procurement calculations

The PostgreSQL script demonstrates how function interfaces, constraints, relational data, and transactional operations work together.

### Relational model

The `pricing_policy` table stores tax, discount, and shipping rules. `purchase_order` associates an order with a policy and stores selected overrides. `purchase_line` stores item prices and quantities, with foreign keys, non-negative checks, and a unique item code within each order.

`pricing_audit` records pricing events with JSONB details. Indexes support line lookup by order and retrieval of orders by status and creation time.

The schema separates reusable policy configuration from transactional purchase data. It avoids storing redundant calculated totals in the base order table, reducing the risk of totals becoming inconsistent with their lines.

### SQL function parameters

`calculate_line_total` demonstrates a default quantity. Its overloaded counterpart accepts a discount and tax rate, showing how PostgreSQL selects a function by signature and argument types.

`average_amounts` uses a variadic numeric array. It explicitly rejects an empty array and null elements. `normalize_reference` demonstrates an `INOUT` parameter, which receives a value and returns its normalized form.

`price_order` accepts an order identifier and optional overrides. Named notation identifies each argument, while `COALESCE` distinguishes an omitted override represented by SQL `NULL` from a non-null supplied value.

### Integrity, triggers, and transactions

The schema uses primary keys, foreign keys, unique constraints, and check constraints to enforce basic data integrity. These rules protect against invalid rows regardless of which application submits the data.

`guard_priced_order_lines` prevents line changes once an order reaches the `PRICED` state. It locks the corresponding order row while checking the state, helping coordinate changes to that order. A production implementation would also need carefully designed locking and isolation rules for concurrent status transitions and inserts.

The pricing block calculates a total, changes the order state, and records an audit event in one transaction. If the transaction fails, the associated data changes are rolled back.

The exception blocks demonstrate invalid argument handling without terminating the entire demonstration script. The view `order_line_summary` calculates subtotals from the underlying lines, rather than relying on duplicated totals.

## Cross-language distinctions

| Concern | Python | JavaScript | C++ | Java | PostgreSQL |
|---|---|---|---|---|---|
| Positional binding | Supported | Supported | Compile-time matching | Compile-time matching | Supported |
| Named arguments | Native keyword arguments | Commonly modeled with options objects | Domain structures and overloads | Records and configuration objects | Named notation |
| Defaults | Default parameters | Default parameters and destructuring | Default arguments and overloads | Overloads or configuration types | Default parameter values |
| Variable argument count | `*args`, `**kwargs` | Rest parameters | Parameter packs and variadic functions | Varargs | `VARIADIC` arrays |
| Type enforcement | Primarily runtime | Primarily runtime | Strong compile-time checking | Strong compile-time checking | Database function types |
| Argument inspection | `inspect.signature` | Runtime function metadata, limited signature enforcement | Primarily compile-time mechanisms | Reflection where appropriate | Catalog metadata |
| Multiple outputs | Tuples and records | Objects and arrays | Structures or output references | Records and result objects | Composite results and `OUT` parameters |
| Validation | Explicit exceptions and checks | Explicit checks and exceptions | Compile-time types plus runtime checks | Constructors, methods, and exceptions | Constraints and function logic |

These mechanisms are not interchangeable. A JavaScript options object improves call readability but does not create compile-time keyword-argument enforcement. C++ templates can preserve types across generic calls, while Python's runtime signature inspection supports flexible introspection. PostgreSQL constraints protect stored data even when application-level validation is bypassed.

## Validation, failure modes, and design trade-offs

A reliable parameter contract distinguishes structural errors from domain errors.

Structural errors include missing required arguments, unexpected names, duplicate argument assignments, and incompatible types. Domain errors include negative prices, unsupported rates, blank identifiers, invalid states, and values outside a policy limit.

The correct response depends on the boundary. A malformed function call may raise an argument-binding error. Invalid user input may produce a validation result. A failed authorization should prevent a payment from being accepted. An integrity violation should cause the database operation to fail.

Several recurring mistakes deserve particular attention:

- Mutable defaults in Python can leak state between calls because the same default object is reused.
- JavaScript defaults do not treat `null` and `undefined` identically.
- Long positional signatures make same-typed values easy to confuse, particularly when rates, limits, and flags are adjacent.
- Sentinel values can be ambiguous when the sentinel is also a legitimate domain value. Optional types or explicit configuration objects often communicate absence more clearly.
- Passing a mutable object by reference allows mutations to remain visible outside the function. Immutability or defensive copies can make ownership clearer.
- A callback may throw, block, or perform side effects. Callers must define how those failures affect the larger operation.
- A timeout on a promise race does not necessarily cancel the underlying asynchronous work.
- SQL defaults do not automatically replace explicitly supplied null values.
- Database constraints and application checks solve different problems. Application checks can provide useful messages, but database constraints remain essential for persistent integrity.
- Financial calculations require a deliberate policy for rounding, currency precision, overflow, and tax order. A correct parameter interface does not by itself guarantee a correct financial result.

## Performance and maintainability

Parameter design affects performance when calls copy large objects, allocate intermediate collections, or trigger repeated validation and transformation.

C++ constant references avoid unnecessary copies for large read-only inputs. Move semantics and forwarding references can preserve efficient transfer of temporary objects. The added template complexity should be justified by a real need for generic behavior.

Java immutable records make domain values easier to reason about, but copying large collections or repeatedly scanning lists can be expensive. Sets or indexed lookups may be more appropriate for large blocked-account collections.

Python decorators and dynamic argument forwarding improve reuse, but poorly designed wrappers can obscure signatures and errors. Preserving metadata and keeping wrappers narrow helps maintainability.

JavaScript object-based configuration reduces positional mistakes, but runtime validation is still required at external boundaries. Copying and freezing nested data also has a cost, and shallow freezing alone does not make arbitrary nested objects immutable.

In PostgreSQL, function calls inside row-processing queries can be evaluated many times. Indexes, query plans, set-based operations, and accurate function volatility declarations matter when calculations operate over large tables. Function declarations such as `IMMUTABLE` or `STABLE` must reflect actual behavior rather than being selected solely for optimization.

## Security and production boundaries

Arguments frequently cross trust boundaries. A caller can supply malformed values, unexpected object properties, oversized files, or values that satisfy a data type while violating a business rule.

Validate externally supplied values before using them. Bound file sizes, avoid logging credentials or sensitive argument contents, and use explicit policy objects instead of relying on caller-controlled flags to authorize privileged operations.

For database operations, parameterized queries and typed function signatures reduce accidental misuse. Constraints should enforce invariants that must hold for every stored record. Transaction boundaries should keep related changes consistent, while concurrency controls should prevent two individually valid operations from violating a shared aggregate limit.

The sample programs focus on parameter and argument mechanics, but production services also require authorization, observability, concurrency control, and domain-specific failure handling. Those responsibilities should remain explicit rather than being hidden inside defaults or implicit argument conversions.
