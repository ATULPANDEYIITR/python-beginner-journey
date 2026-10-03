# Mutable and Immutable Data

## Scope

Mutable and immutable data describe two different approaches to managing state.

**Mutable data** can be changed after the object has been created. A list can gain an element, a dictionary can have a value replaced, or an object can have one of its fields modified.

**Immutable data** cannot be changed in place after creation. An operation that appears to update immutable data instead produces another value representing the updated state.

The distinction is important for ownership, aliasing, caching, concurrency, state management, auditing, debugging, and API design. The three implementations use repository-review state as a realistic domain because review records naturally benefit from preserving historical snapshots.

The implementations deliberately use different techniques:

- Python compares mutable lists and dictionaries with immutable tuples, frozen dataclasses, read-only mapping views, defensive copies, and immutable state transitions.
- JavaScript focuses on references, spread syntax, `structuredClone`, shallow and recursive freezing, copy-on-write collections, and event-driven state updates.
- C++ models a review service in which mutable construction state is converted into immutable published snapshots that can be retained in an audit history.

## Core distinction

Mutation changes an existing object.

For example, a Python list can be modified with `append`, and a JavaScript array can be modified with `push`. The identity of the collection remains the same while its contents change.

Rebinding is different from mutation. If a Python variable containing an integer is assigned a new integer, the original integer is not modified. The variable simply refers to another immutable value.

The same distinction appears in JavaScript primitive values. A string operation such as converting text to uppercase produces another string rather than changing the existing string.

The important question is therefore not simply whether a variable can be assigned a new value. The useful question is whether an existing object can be changed through one of its references.

## Aliasing

Aliasing occurs when multiple references point to the same mutable object.

In the Python implementation, `another_reference = labels` does not create another list. Both names refer to the same list. An append through either reference is visible through the other.

JavaScript behaves similarly:

`const secondReference = labels`

does not copy the array. It copies the reference to the same array.

Aliasing can be useful when shared mutation is intentional, but accidental aliasing is a common source of difficult bugs. A function may receive a mutable object, modify it internally, and unexpectedly change state held by its caller.

Immutable values reduce this class of problem because consumers cannot modify the shared value in place.

## Shallow copying and deep copying

A shallow copy creates a new outer container while retaining references to nested objects.

The Python example copies a review dictionary with `review.copy()`. The new dictionary is independent at the outer level, but its nested `metadata` dictionary and nested lists remain shared.

JavaScript spread syntax has the same property:

`const shallow = { ...review }`

creates a new outer object but does not recursively copy every nested object.

Deep copying creates independent nested structures. Python uses `deepcopy` for this purpose. Modern JavaScript can use `structuredClone` for supported structured data.

Deep copying is not universally appropriate. It can consume more memory and CPU than a shallow copy, and some objects have semantics that cannot be represented by a simple recursive clone. The correct choice depends on ownership requirements and the data being copied.

## Immutable collections and values

Python provides several naturally immutable values.

A tuple cannot be structurally changed after construction. It can therefore represent a fixed sequence of labels or approvals more safely than a list when the collection should not change.

Strings and numbers are also immutable.

The Python implementation uses:

`tuple[str, ...]`

for immutable collections inside `ImmutablePullRequest` and `ReviewSnapshot`.

The JavaScript standard library does not provide a general immutable object type comparable to Python's tuple. JavaScript instead provides mechanisms such as `Object.freeze`, immutable programming conventions, copy-on-write updates, and APIs that return new objects.

C++ provides stronger tools for value-oriented design. The case study uses `const` members in `ReviewSnapshot` and returns new `ReviewSnapshot` values from update operations.

## Read-only is not always immutable

A read-only interface and immutable ownership are related but distinct concepts.

Python's `MappingProxyType` prevents mutation through the proxy:

`read_only["required_reviewers"] = 3`

raises `TypeError`.

The underlying dictionary can still be changed by the code that owns it. If the original dictionary is changed, the mapping proxy reflects the new value.

This is a critical design distinction:

> A read-only view restricts one access path. Immutability requires control over the underlying state itself.

JavaScript's `Object.freeze` has another important limitation. It is shallow. Freezing an object does not automatically freeze its nested arrays and objects. The JavaScript implementation therefore includes a recursive `deepFreeze` function when complete object-graph freezing is required.

## Mutable domain state

Mutable state is often convenient during construction or controlled processing.

The Python `MutablePullRequest` class stores labels and changed files in lists. Its `add_label` and `add_file` methods modify those lists directly.

The C++ `MutableReviewBuilder` follows a similar idea. A builder can collect labels, approvals, and status checks before the resulting state is published.

This pattern is useful because constructing a complicated object may naturally involve several incremental operations.

The important architectural boundary is what happens after construction.

## Immutable domain state

The Python `ImmutablePullRequest` uses a frozen dataclass and tuples. Its `with_label` and `with_file` methods do not modify the existing object. They return another `ImmutablePullRequest`.

For example, conceptually:

`updated = original.with_label("review")`

leaves `original` unchanged.

This is an immutable state transition.

The JavaScript `ImmutablePullRequest` uses a different implementation strategy. Its arrays are copied before being frozen, and the instance itself is frozen. `withLabel` and `withFile` construct new instances when the requested value changes.

The C++ `ReviewSnapshot` takes the same conceptual approach using value semantics and `const` data members.

## Immutable state transitions

Immutable systems do not eliminate state changes. They represent state changes differently.

Suppose a review has:

- revision 1
- one approval
- passing tests
- passing lint

A new approval does not modify that historical state. Instead, the system creates a new snapshot containing both approvals.

The previous snapshot remains valid.

This creates a useful relationship:

`old state -> transition -> new state`

rather than:

`shared object -> in-place mutation`

The Python `ReviewSnapshot` demonstrates this with `approve`, `set_check`, and `next_revision`.

The C++ case study applies the same model to repository review state. A new revision produces a new snapshot, and prior approvals are cleared in the new revision while the old revision remains available to the audit history.

## Revision boundaries

Revision-aware systems demonstrate why immutable state can be valuable.

Consider a review state with two approvals. If new code is pushed and the system mutates the same object in place, historical information can become ambiguous. Was an approval associated with the old code or the new code?

The C++ implementation avoids this ambiguity by making the revision explicit.

`next_revision()` creates a new `ReviewSnapshot`. In this case study, approvals are cleared because the review decision belongs to the earlier revision.

The previous snapshot still contains the earlier approvals and remains available in `ReviewHistory`.

This is useful for auditing because the historical state is not overwritten.

## Hashability and immutable values

Immutable values can often be hashed safely.

The Python implementation demonstrates that a list cannot be hashed because lists are mutable. A tuple containing hashable values can be hashed and used as part of a dictionary key.

This matters for caches and sets.

A cache key should not change after it has been inserted into a hash table. If a mutable object used as a key could change its hash-related state, the container could no longer reliably locate it.

Immutability is therefore useful for representing stable identifiers and compound cache keys.

## Defensive copying

Defensive copying protects ownership boundaries.

The Python `process_batch` function deep-copies incoming records before transforming nested values. A caller can therefore retain its original data without having its nested structures unexpectedly modified.

The JavaScript examples apply similar reasoning when a constructor copies arrays before storing them.

The rule is not that every function should copy every object. Excessive copying can waste memory and processing time. Copying is most useful when an API needs to establish independent ownership or when mutation of caller-owned data would violate the API contract.

## Event-driven immutable state

The JavaScript `ReviewStateStore` demonstrates immutable state combined with an event-driven design.

The store owns a private current state. Consumers receive a snapshot through the `snapshot` getter. Updates are expressed as transformations:

`store.update(state => ({ ...state, ... }))`

The update creates a new state object instead of modifying the existing state.

Listeners are then notified of the replacement state.

This design has a useful debugging property. A previously retained snapshot continues to describe the state that existed when it was obtained.

The implementation also returns an unsubscribe function. This prevents listeners from being retained indefinitely when a consumer no longer needs notifications.

## C++ case study architecture

The C++ program models a review service with three layers.

### Mutable construction

`MutableReviewBuilder` collects the initial review data.

It owns mutable vectors and a mutable map because construction naturally involves incremental operations such as:

- adding labels
- adding reviewers
- setting check results

The builder validates basic input before accepting it.

### Immutable published state

`ReviewSnapshot` represents a published review state.

Its important properties are:

- the Pull Request identifier is fixed
- the revision number is fixed
- approval records are stored as a value
- check results are stored as a value
- labels are stored as a value
- update operations return another snapshot

A published snapshot therefore does not depend on later modifications to the builder.

### Historical state

`ReviewHistory` stores snapshots rather than one continually mutated review object.

The history can consequently contain:

`initial -> reviewed -> fully approved -> revised -> failed check`

Each element represents a distinct state.

This is a direct application of immutability to auditability.

## Merge-policy evaluation in the C++ case study

The C++ program contains a small merge-eligibility engine to give the immutable state a realistic purpose.

`MergePolicy` specifies:

- the minimum number of approvals
- whether all checks must pass

`evaluate_merge` examines a `ReviewSnapshot` and returns a `MergeDecision`.

It does not modify the snapshot.

This separation is intentional. The snapshot describes state, while the evaluator applies policy to that state.

For example, a snapshot with one approval and passing checks fails a policy requiring two approvals. A later snapshot with two approvals satisfies that part of the policy.

When the revision changes, the new snapshot starts without the old approvals in this model.

## JavaScript collection updates

JavaScript `Set` and `Map` are mutable by default.

The JavaScript implementation demonstrates copy-on-write handling:

`const nextApprovals = new Set(originalApprovals)`

followed by modification of `nextApprovals`.

The original set remains unchanged.

The same technique is used for `Map`.

This pattern is useful when an application wants native collection behavior while maintaining immutable state boundaries.

It is important not to confuse the copying convention with a language-level guarantee. A `Set` copied this way is still mutable. The immutability comes from keeping ownership disciplined and replacing the old value rather than modifying the published one.

## Performance considerations

Mutation can be efficient because an existing object can often be changed without allocating another complete container.

For example, appending to a mutable vector or list can avoid copying the entire logical sequence.

Immutable updates generally require creating a new representation.

The Python performance demonstration contrasts list append with tuple concatenation. Tuple concatenation creates another tuple containing the resulting elements.

The C++ case study has the same trade-off. Returning a new `ReviewSnapshot` may copy vectors and maps.

For moderate review-state objects, this can be a reasonable trade for simpler ownership and reliable snapshots. For very large state trees or extremely frequent updates, repeatedly copying complete structures can become expensive.

Persistent data structures address this problem through structural sharing, where unchanged portions are reused while changed paths are replaced.

Immutability therefore does not automatically mean better performance. Its primary advantages concern correctness, ownership, reasoning, and state history. Performance should be evaluated against the actual access and update patterns.

## Common mutation mistakes

### Mutating through an alias

Assigning one variable to another does not necessarily copy the object.

Python:

`second_reference = labels`

JavaScript:

`const secondReference = labels`

Both create another reference to the same mutable collection.

### Assuming a shallow copy is recursive

Python dictionary copying and JavaScript spread syntax create shallow copies.

Nested objects remain shared unless they are explicitly copied.

### Assuming freeze is deep

JavaScript `Object.freeze` only freezes the immediate object.

Nested arrays and objects require additional handling if they must also be protected.

### Returning internal mutable state

A class that returns its internal list directly gives callers a path to mutate private state.

Returning immutable values, defensive copies, or read-only views can establish a stronger boundary.

### Confusing rebinding with mutation

Changing what a variable refers to is not necessarily the same as modifying an existing object.

This distinction is particularly important for Python immutable values and JavaScript primitive values.

### Using mutable values as stable keys

Mutable objects are poor choices for hash-based identities when their relevant state can change after insertion.

Stable immutable representations are safer for cache keys and set membership.

## Debugging implications

Mutable state can make debugging difficult when an object has several aliases. A mutation may occur far from the location where the object was originally created.

Immutable state reduces this uncertainty because a previous value remains unchanged.

Snapshot-oriented debugging can therefore answer questions such as:

- What state existed before the update?
- Which transition produced the new state?
- Which revision did an approval belong to?
- Which status checks were recorded at that point?

The C++ audit history is specifically designed around this property.

JavaScript reference equality provides another useful mechanism. When immutable updates replace only the changed branch, code can use reference identity to detect whether a portion of state changed.

This technique only works reliably when code follows the ownership rule and does not mutate published state directly.

## Validation and failure handling

Immutability does not replace validation.

The Python implementation validates required configuration fields and rejects an invalid negative approval count.

The JavaScript implementation validates identifiers, labels, files, reviewers, and update functions.

The C++ implementation rejects invalid identifiers, revisions, reviewer names, check names, and labels using exceptions.

Validation should happen at meaningful boundaries rather than relying on immutability to make invalid state valid.

An immutable invalid object is still invalid. Immutability preserves state; it does not establish semantic correctness.

## Concurrency and shared state

Immutable snapshots can simplify concurrent read access because readers can retain a state value without worrying that another component will mutate that same value underneath them.

This does not mean immutable data automatically makes an entire application thread-safe.

The ownership and publication mechanism still matters. Mutable infrastructure surrounding the immutable values can introduce races.

The useful design pattern is to keep mutable coordination narrow and publish stable values across broader boundaries.

The C++ `ReviewSnapshot` is suited to this pattern because a snapshot's state cannot be reassigned after construction.

## Choosing between mutation and immutability

Mutation is useful when:

- an object has a clearly defined owner
- changes happen during controlled construction
- in-place updates are important for performance
- the object is not exposed across ownership boundaries

Immutability is useful when:

- state must be retained as a historical snapshot
- multiple consumers need the same state safely
- cache keys must remain stable
- changes should be represented as explicit transitions
- debugging requires reliable before-and-after states
- data crosses API or concurrency boundaries

Many practical systems combine both approaches. The C++ case study intentionally does this by using mutable construction and immutable publication.

## Relationship between the three implementations

The Python implementation emphasizes the semantic distinction between object mutation, rebinding, copying, frozen data structures, and immutable state transitions.

The JavaScript implementation emphasizes the fact that JavaScript objects and collections are reference-based and mutable by default. It demonstrates how spread, `structuredClone`, `Object.freeze`, recursive freezing, and copy-on-write patterns can establish stronger state boundaries.

The C++ implementation focuses on system architecture. Mutable construction is separated from immutable published review state, and immutable snapshots are retained as an audit history.

The same underlying design principle appears in all three implementations:

**state that is intentionally shared should have a clearly defined ownership and mutation policy.**

When state must remain stable, representing an update as a new value makes that stability explicit.
