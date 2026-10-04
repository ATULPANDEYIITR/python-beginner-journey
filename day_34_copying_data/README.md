# Copying Data

Copying data is the process of creating another representation of existing state while defining how much of that state is independent from the original. The distinction is important because an apparent copy may actually preserve references to the same mutable objects.

The three implementations in this repository approach the subject from different language models:

- The Python program examines object identity, shallow copying, recursive deep copying, custom objects, snapshots, selective copying, serialization boundaries, and defensive ownership.
- The JavaScript program focuses on reference semantics, spread syntax, `Object.assign`, `structuredClone`, circular structures, built-in objects, event-driven snapshots, and defensive API boundaries.
- The C++ program treats copying as an ownership and value-semantics problem, using standard containers, explicit ownership, copy constructors, snapshots, copy-on-write, validation, and rollback.

The central engineering question is not simply whether data can be copied. It is whether the resulting object has the ownership, identity, mutability, lifetime, and performance characteristics required by the application.

## Core distinction: value versus reference

Consider a mutable configuration containing nested structures. There are several fundamentally different operations that may be described informally as "copying":

- An alias creates another name for the same object.
- A shallow copy creates a new outer container while retaining references to nested objects.
- A deep copy recursively creates independent objects for the supported mutable object graph.
- A selective copy duplicates only the levels where independent ownership is required.
- Serialization converts state into a representation that can be reconstructed elsewhere. This creates a data-transfer boundary, but it is not automatically equivalent to an object clone.
- Copy-on-write delays duplication until one owner actually needs to mutate shared state.

These mechanisms solve different problems and should not be treated as interchangeable.

## Python copying model

Python variables hold references to objects. Assignment therefore does not duplicate the object.

If `alias = source`, both names refer to the same object. Mutating the object through `alias` is visible through `source`.

A shallow copy changes the outer identity but normally preserves references contained inside the copied object. For a dictionary such as `{"limits": {"timeout": 5}}`, `source.copy()` creates a new dictionary, but the nested `limits` dictionary remains shared.

The Python implementation demonstrates this with configuration dictionaries and nested lists.

`copy.copy()` provides a generic shallow-copy operation. `copy.deepcopy()` recursively copies supported objects while maintaining an internal memo table so that shared references and cycles can be handled correctly.

The program deliberately includes a cyclic dictionary in which `node["parent"]` points back to `node`. The deep-copy demonstration verifies that the copied graph preserves the cycle while giving the copied root its own identity.

## Python custom objects

The `Account` dataclass demonstrates why copying becomes more significant when application objects contain nested mutable state.

The object contains:

- `UserPreferences`
- a notification-channel list
- feature flags
- audit metadata

A shallow copy of the `Account` creates a new `Account` object but keeps references to its nested objects. A deep copy creates independent nested structures.

This distinction matters when an application treats an object as an isolated working version. A caller modifying a nested list through a shallow copy may unintentionally modify the source object.

## Python snapshot design

The configuration snapshot example uses `deepcopy()` because the snapshot is intended to remain stable after the live configuration changes.

The live configuration contains nested timeout settings, feature flags, and region lists. After the snapshot is created, the live configuration is modified. The snapshot retains the earlier nested values because its mutable state was recursively copied.

This is a common pattern for:

- configuration history
- rollback state
- audit snapshots
- simulation inputs
- transaction preparation
- test fixtures

Deep copying is not automatically the best solution for every snapshot system. Large object graphs can make repeated deep copies expensive. In a production system, immutable structures, database versioning, persistent data structures, structural sharing, or explicit serialization may provide better characteristics.

## Selective copying in Python

The selective-copying example copies the outer dictionary, then explicitly copies the nested `runtime` and `timeouts` dictionaries.

This approach is appropriate when the ownership model is well understood.

Its advantage is control. Its risk is incomplete isolation. If another mutable layer is later introduced and the selective-copy implementation is not updated, that new layer may remain shared.

`deepcopy()` is safer when the requirement is "make this supported object graph independently mutable." Selective copying is more appropriate when copying only specific ownership boundaries is intentional.

## Defensive API boundaries in Python

The `ConfigurationStore` class returns a deep copy from `read()` rather than exposing its internal dictionary directly.

Without that boundary, a caller could obtain an internal reference and mutate repository state without invoking a controlled update method.

The store also creates historical copies before modifications. This gives rollback operations an isolated previous state.

This design demonstrates an important ownership rule:

> If an object owns mutable state, do not expose a mutable reference to that state unless shared mutation is explicitly part of the API contract.

Returning a copy is one way to enforce that boundary.

## Serialization is a different operation

The Python and JavaScript implementations both demonstrate JSON as a copying or transfer boundary.

A JSON round trip can produce a structurally separate representation for ordinary JSON-compatible data:

`json.loads(json.dumps(value))`

This technique has important limitations. It is not a general Python object cloning mechanism. Custom classes, object identity, sets, tuples with their original semantics, functions, special numeric cases, and cyclic graphs are not preserved as arbitrary Python objects.

Serialization is more appropriate when the requirement is to produce a defined wire representation, such as an API request or durable document.

Copying and serialization therefore answer different questions:

| Requirement | Appropriate concept |
|---|---|
| Another reference to the same state | Alias |
| Independent outer container | Shallow copy |
| Independent supported object graph | Deep copy |
| Independent selected layers | Selective copy |
| Data exchange across a boundary | Serialization |
| Shared state until mutation | Copy-on-write |
| Stable historical version | Snapshot or immutable state |

## JavaScript reference semantics

JavaScript objects and arrays are reference values for assignment and ordinary object manipulation.

The JavaScript implementation starts with:

`const alias = liveConfig`

The alias and the original point to the same object. Mutating a nested object through one reference changes what the other reference observes.

Object spread, as used in `{ ...source }`, creates a new outer object but performs a shallow copy of its own enumerable properties. If a property contains an object or array, the reference to that nested value is copied.

`Object.assign({}, source)` has the same fundamental shallow-copy characteristic for this use case.

Array spread, such as `[...deployments]`, also creates a new outer array while preserving references to its object elements.

## JavaScript structured cloning

The JavaScript implementation uses `structuredClone()` when recursive data isolation is required.

For nested application data, `structuredClone()` creates an independent supported object graph. The program modifies nested retry settings and region arrays in the clone and verifies that the source remains unchanged.

The circular-reference example demonstrates another distinction. JSON serialization cannot stringify a cyclic object because the representation would recursively encounter the same object. `structuredClone()` can handle supported circular object graphs.

The implementation also demonstrates cloning of `Date`, `Set`, and `Map`, which are handled more appropriately by structured cloning than by a JSON round trip.

## JavaScript prototype behavior

Generic structured cloning should not be treated as a mechanism for reproducing arbitrary application class behavior.

The JavaScript program creates a `Deployment` class with a `scale()` method. After cloning the instance, the example checks whether the cloned object still behaves as the original class instance.

The important design lesson is that copying data and copying application behavior are separate concerns. When an application relies on class methods, invariants, private state, resources, or custom reconstruction logic, a domain-specific cloning method or factory may be more appropriate than a generic clone operation.

## JavaScript event-driven snapshots

The `StateBus` example uses `EventTarget` and `CustomEvent` to model an event-driven state system.

Before an update, the system creates a snapshot of the previous state. It then creates an independent working state, applies the mutation, publishes the new state, and emits an event containing both snapshots.

The event payload itself is cloned before being exposed to consumers. This limits the ability of event listeners to accidentally modify internal state.

This pattern is useful in stateful front-end or Node.js systems where consumers need stable before-and-after representations.

## C++ value semantics

C++ provides a different default model for ordinary value-owned objects.

The `ServiceConfiguration` structure contains `std::string`, `std::vector`, and `std::map`. Copying the structure invokes the copy operations of those members. The resulting configuration owns its own container contents.

The case study modifies the copied configuration and verifies that the original configuration remains unchanged.

This is different from JavaScript object spread and Python shallow dictionary copying because C++ standard containers generally represent ownership of their contained values rather than references to the same nested JavaScript-style objects.

C++ still permits shared and pointer-based ownership, so this behavior depends on the actual data model.

## Explicit ownership in C++

The `DeepConfiguration` class deliberately contains a `std::unique_ptr<RetryPolicy>`.

An owning raw pointer would create a dangerous copy problem: copying the pointer value would produce two objects referring to the same allocation, potentially resulting in shared mutable state or double deletion.

The example uses `std::unique_ptr` and an explicit copy constructor that creates a separate `RetryPolicy`.

The preferred production rule is to express ownership through RAII types such as `std::unique_ptr`, `std::shared_ptr`, containers, and ordinary value members rather than manually managing owning raw pointers.

## Transactional copy-and-commit workflow

The C++ `ConfigurationStore` demonstrates a configuration workflow based on working copies.

`workingCopy()` returns a value copy of the published configuration. The caller can modify the candidate without changing the currently published state.

`commit()` validates the candidate, stores the previous configuration as a snapshot, and publishes the candidate.

`rollback()` restores the stored historical value.

This provides a simple transactional mental model:

`published state -> working copy -> validation -> commit -> snapshot`

The key property is that the candidate does not become published merely because a caller has a mutable copy.

## Copy-on-write in C++

The `CopyOnWriteConfiguration` class uses `std::shared_ptr` for shared state.

Copying the wrapper initially shares the same configuration object. A mutation checks whether the state has multiple owners. If so, it creates a separate configuration before modifying it.

This can reduce unnecessary copying when many consumers only read data.

The trade-off is additional complexity. Copy-on-write is useful only when its ownership and mutation patterns justify that complexity. A straightforward value copy can be easier to reason about and may be faster for small objects.

## Performance implications

Copying is not free.

A shallow copy generally duplicates only the outer container structure. A deep copy traverses the relevant object graph and allocates or constructs additional objects.

The cost depends on:

- number of elements
- nesting depth
- allocation count
- size of strings and buffers
- container implementation
- object graph topology
- frequency of copying
- cache behavior
- allocator behavior
- amount of shared versus mutable state

The C++ case study includes a simple timing demonstration over thousands of configuration objects. It is intentionally not presented as a benchmark because meaningful benchmarking requires controlled compiler settings, allocator behavior, workload distributions, warm-up, repeated measurements, and statistical analysis.

For large systems, copying an entire configuration on every request may be inappropriate. Alternatives include immutable state, structural sharing, copy-on-write, database versioning, or targeted updates.

## Edge cases

### Nested mutable objects

A shallow copy can leave nested dictionaries, arrays, vectors, or objects shared. Tests should mutate nested state, not only top-level fields.

### Circular references

Recursive structures require mechanisms that understand graph identity. JSON serialization cannot represent arbitrary cycles, while Python's `deepcopy()` and JavaScript's `structuredClone()` support relevant cyclic structures.

### Shared references inside a graph

An object graph can contain two paths pointing to the same child. A correct deep-copy mechanism should preserve the intended graph relationships rather than blindly producing unrelated duplicates for every traversal.

### Class instances

Generic cloning may not preserve application-specific behavior, invariants, private resources, or prototype expectations. Domain-specific copying can be safer.

### Sensitive information

Copying credentials, access tokens, or other secrets creates additional in-memory representations. Copying does not encrypt the data, revoke the original, or securely erase old copies.

The Python and JavaScript examples intentionally use obviously illustrative credentials rather than real secrets.

### Invalid data

Copying should not be confused with validation. A copy of invalid state remains invalid.

The C++ implementation validates configurations before they enter the published store, and the Python and JavaScript repository examples validate their state boundaries.

## Common mistakes

### Mistaking assignment for copying

Writing `alias = source` in Python or `const alias = source` in JavaScript does not create an independent object.

### Assuming spread is deep

`{ ...source }` and `[...source]` are shallow operations.

### Using JSON cloning indiscriminately

A JSON round trip changes representation and loses information that is not part of JSON.

### Deep-copying everything

Deep copying can be wasteful when most state is immutable or safely shared.

### Returning internal mutable state

A getter that exposes an internal mutable object gives callers an unintended mutation path.

### Copying pointer addresses in C++

A copied pointer is still a pointer to the same object. Ownership must be explicit.

### Ignoring domain invariants

A copied object can still violate application rules. Copy constructors, clone functions, validation functions, and factory methods should preserve the invariants expected by the domain.

## Debugging copying problems

When a mutation unexpectedly affects another object, inspect identity before inspecting values.

Python provides the `is` operator for identity checks. JavaScript uses `===` for reference identity. C++ requires understanding whether a value is owned directly, referenced, pointed to, or shared through a smart pointer.

A useful debugging pattern is:

- identify which layer was expected to be independent
- compare object or reference identity
- mutate one nested value deliberately
- inspect the original and copied structures
- determine where ownership diverged from the intended model

Tests should explicitly verify mutation isolation rather than merely comparing initial values.

The Python and JavaScript implementations include assertions for nested identity. The C++ implementation uses assertions to verify that mutations to copied value objects do not alter the originals.

## Security considerations

Copying can affect security because sensitive data may exist in multiple memory locations after a copy.

Particular care is required for:

- access tokens
- credentials
- cryptographic material
- personally identifiable data
- authorization state
- session information

A defensive copy can prevent unauthorized mutation, but it does not provide confidentiality.

For sensitive data, the preferred architecture is usually to minimize unnecessary duplication, define ownership clearly, avoid logging secrets, restrict access to mutable state, and use appropriate secure-storage mechanisms.

## Production design principles

A robust copying policy should be based on ownership rather than convenience.

If state is intentionally shared, make that sharing explicit.

If a consumer receives a working representation that it may mutate independently, provide an isolated copy.

If a historical state must remain stable, preserve it through immutable state, a snapshot, versioned persistence, or an appropriately isolated copy.

If copying is expensive, measure the workload before introducing a more complex strategy such as structural sharing or copy-on-write.

If data crosses a process or API boundary, use an explicit serialization format and validate the received representation rather than treating serialization as a generic object-cloning mechanism.

The most important distinction is between **duplicating a value** and **duplicating ownership**. A technically correct copy operation is one whose resulting identity and mutation behavior match the ownership contract of the system.
