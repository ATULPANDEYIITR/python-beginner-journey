# Local and Global Variables

## Scope as a Rule for Name Visibility

Variable scope determines where a name can be accessed and which binding an expression refers to. Scope is not the same as lifetime or storage duration. A variable can be visible within a function while referring to an object that remains alive elsewhere, and a global binding can exist throughout a module's execution without being available in every module.

The implementations compare scope rules in Python, JavaScript, C++, Java, and PostgreSQL. They use an inventory-management scenario to distinguish short-lived calculation values from object state, shared application configuration, and persistent database records.

## Local Variables

A local variable is declared or assigned within a limited execution context, such as a function, method, block, or database routine. Its visibility depends on the language.

Local variables are appropriate for intermediate calculations, validation results, temporary collections, and values that should not be changed by unrelated operations.

In the invoice calculation, the subtotal, tax amount, and final total are local values. Keeping them local makes the calculation easier to reason about because the values do not become shared mutable application state.

A common error occurs when a variable is referenced before it has been initialized. The exact behavior varies by language. Python can raise `UnboundLocalError`; JavaScript's `let` and `const` bindings have a temporal dead zone; Java rejects many uninitialized local-variable reads at compile time.

## Global and Shared State

A global variable is available outside a narrow local scope according to the language's rules. The term does not mean exactly the same thing in every language.

| Language | Relevant mechanism | Important distinction |
|---|---|---|
| Python | Module-level names | Reading a global name is straightforward, but rebinding it inside a function normally requires `global`. |
| JavaScript | Global environment and `globalThis` | Top-level declarations in a Node.js module are not automatically properties of `globalThis`. |
| C++ | Namespace-scope variables | Storage duration and linkage determine how declarations behave across the program and translation units. |
| Java | Static fields | A static field belongs to a class, while an instance field belongs to an object. |
| PostgreSQL | Configuration tables and session settings | PostgreSQL has no ordinary application-style global variable shared automatically across all sessions. |

Shared state is useful for configuration and counters, but it introduces risks. If many functions can modify the same value, the effect of a change becomes harder to trace. Concurrent execution can also cause race conditions unless updates are appropriately synchronized.

Immutable configuration is often safer than mutable global state. Values such as a fixed tax rate can be declared as constants where supported. Persistent business information, such as stock quantities, belongs in an explicitly managed data store rather than in an unprotected global variable.

## Python Implementation

The Python script demonstrates module-level constants, a mutable module-level dictionary, local shadowing, and the `global` and `nonlocal` declarations.

The `update_request_counter()` function uses `global` because it reassigns the module-level integer. By contrast, `demonstrate_global_mutable_object()` changes a value inside the existing dictionary. Mutating an object and rebinding the name that refers to that object are different operations.

The stock-reservation closure demonstrates `nonlocal`. Its nested function changes a binding from the enclosing function rather than a module-level binding. Returning the nested function keeps the enclosing state alive after the original call finishes.

The `Warehouse` class uses instance attributes through `self`. Two warehouse objects can therefore hold different stock quantities even though they use the same class definition. The examples also demonstrate comprehension scope, function defaults, and Python's scope-inspection functions.

A mutable default argument is deliberately avoided in the event-recording example. Creating a new list inside the function prevents unrelated calls from accidentally sharing one list.

## JavaScript Implementation

JavaScript distinguishes function scope from block scope.

- `var` is function-scoped and can be accessed outside the block where it was declared.
- `let` and `const` are block-scoped.
- `const` prevents reassignment of a binding, but it does not make the referenced object deeply immutable.
- A closure retains access to lexical bindings from its surrounding environment.

The loop-callback example shows why `var` can produce unexpected results: callbacks refer to the same function-scoped binding. A `let` declaration creates a separate loop binding for each iteration.

The asynchronous example shows another subtle distinction. A closure retains access to a binding, not necessarily a frozen copy of the value it held when the callback was created. Capturing a value in a separate `const` can preserve the intended value.

The stock-reservation factory keeps its internal stock variable inaccessible through ordinary external references. Its returned methods provide controlled access. This is a practical way to encapsulate mutable state without exposing a global variable.

## C++ Case Study

The C++ program models two distribution centres. Each `Warehouse` object owns its stock, capacity, and audit trail. The namespace-scope tax rate and application name serve as configuration, while the transaction counter represents shared mutable state.

The unnamed namespace gives its declarations internal linkage within the translation unit. This is useful for implementation details that should not be exported as externally linked symbols.

The tax calculator returns a lambda that captures its rate by value. The lambda remains usable after the factory function returns because the captured value is stored in the closure object. This avoids returning a reference to a local variable whose lifetime has ended.

The audit trail is stored in a vector owned by the warehouse. A reference returned by the `audit()` accessor avoids copying the collection, while the accessor's `const` qualification prevents callers from modifying it through that reference.

In production code, a shared transaction counter accessed by multiple threads requires synchronization or an appropriate atomic type. The demonstration is single-threaded and does not claim to provide concurrent safety.

## Java Enterprise Model

Java makes the distinction between class state and object state explicit.

The `processedTransactions` field is static, so it is shared by all instances of `VariableScopeEnterprise`. Fields such as `stock` and `capacity` are associated with individual warehouse objects. Local variables inside `calculateInvoice()` are created for that method invocation.

The `demonstrateShadowing()` method deliberately declares a local variable with the same name as an instance field. The local name takes precedence within the method, while `this.warehouseName` refers explicitly to the object's field.

The markup calculator returns a lambda that captures an effectively final local value. Java does not permit a lambda to capture a local variable that is later reassigned. This restriction makes the captured value's relationship to the enclosing method more predictable.

The audit accessor returns `List.copyOf(auditTrail)`. Callers can inspect the returned snapshot without directly modifying the object's internal list. Validation occurs before inventory changes, and a rejected dispatch leaves stock unchanged.

The static transaction counter is suitable only for this simple sequential example. A multi-threaded service would need appropriate concurrency controls, and a distributed application would generally use a durable transactional counter or event-based accounting when global consistency matters.

## PostgreSQL Scope and Persistence

PostgreSQL illustrates why local variables and shared values should not be treated as interchangeable.

The `calculate_invoice()` function declares `v_subtotal`, `v_tax_rate`, `v_tax_amount`, and `v_total` in its PL/pgSQL `DECLARE` section. Those variables exist for the duration of that routine invocation. The tax rate itself is read from `application_config`, which stores durable configuration as table data.

The `receive_stock()` function locks the selected warehouse row with `FOR UPDATE`, calculates a local candidate stock value, validates capacity, updates the row, and writes an audit record. The row lock prevents competing transactions from independently validating against the same stale stock value.

The `warehouse_stock` constraints enforce non-negative stock and prevent stock from exceeding capacity. The audit table uses a foreign key to ensure that each audit record refers to an existing warehouse.

The custom setting `scope_lab.current_region` is session state. `SET LOCAL` overrides that setting for the current transaction and the override ends with the transaction. Neither form is a durable replacement for a configuration table.

The SQL aliases used in reporting queries exist only within their query scope. They do not create stored variables.

## Closures and Captured State

A closure combines a function with access to its surrounding lexical environment. This allows a function to retain information without placing it in a global namespace.

The Python reservation function uses `nonlocal` to update an enclosing binding. The JavaScript reservation factory returns methods that close over a private variable. The C++ tax calculator stores a value in a lambda capture, while the Java markup calculator captures an effectively final local value.

These mechanisms have different language rules, but they support a common design principle: state can be owned by a specific operation or object and exposed through a limited interface.

Closures do not automatically make state thread-safe. If several threads or asynchronous operations modify shared captured state, synchronization and transaction boundaries may still be necessary.

## Common Failure Modes

| Failure | Cause | Safer approach |
|---|---|---|
| Unexpected name changes | A local name shadows an outer name | Use descriptive names and explicit qualification when necessary. |
| Python `UnboundLocalError` | A function assigns to a name and reads it before local initialization | Initialize the local value or use the correct scope declaration. |
| JavaScript temporal dead zone | A `let` or `const` binding is accessed before initialization | Initialize the binding before use. |
| Shared mutable state | Many functions modify the same global object or static field | Encapsulate state and expose controlled operations. |
| Dangling C++ reference | A reference outlives the object it refers to | Return values or use an ownership model that guarantees lifetime. |
| Java captured-variable error | A lambda captures a local variable that is later reassigned | Capture an effectively final value or model changing state in an object. |
| PostgreSQL state confusion | Session configuration is mistaken for durable shared data | Store persistent business values in tables and update them transactionally. |

## Design and Performance Considerations

Local state limits accidental coupling and often makes functions easier to test. Passing dependencies as parameters makes data flow explicit and avoids hidden reliance on module-level state.

Global or static state can be appropriate for immutable configuration, shared registries, or carefully controlled process-wide services. Mutable global state should be limited because its changes can affect unrelated operations and make tests order-dependent.

In concurrent systems, scope alone does not guarantee safety. A variable can be local to a request while referring to a shared object, and a closure can retain shared mutable state. Correctness depends on ownership, object lifetime, synchronization, and transaction design as well as name visibility.

For persistent business operations, database constraints and transactional updates provide stronger guarantees than an application variable alone. The warehouse example combines local calculation values, explicit object state, and database-enforced integrity to show how each scope serves a different purpose.
