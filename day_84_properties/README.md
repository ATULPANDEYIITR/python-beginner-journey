# Properties in Python

## 1. Property Fundamentals

A property provides controlled attribute access through an object's public interface. It allows a class to expose an attribute-like interface while controlling how its value is retrieved, modified, or deleted.

Python implements properties through the built-in `property` class and the descriptor protocol.

A conventional attribute stores and exposes data directly:

- Reading an attribute retrieves its stored value.
- Assigning an attribute replaces its value.
- Deleting an attribute removes it.

A property introduces methods between the caller and the underlying state.

The four property operations are:

| Operation | Property mechanism | Purpose |
|---|---|---|
| Read | Getter | Retrieve a value |
| Write | Setter | Validate or transform a value |
| Delete | Deleter | Control removal |
| Documentation | Property docstring | Describe the attribute |

The public attribute name can remain unchanged even when the internal implementation becomes more sophisticated.

## 2. Python Property Implementation

The Python implementation uses the `@property` decorator and its associated setter and deleter decorators.

### Getter

A getter executes when a property is read.

The `Temperature` class exposes Celsius through `celsius`. The getter returns the internally stored `_celsius` value.

### Setter

A setter executes when a property receives a new value.

The temperature setter validates numeric input and enforces the supported temperature range before updating internal state.

This prevents invalid values from entering the object through its public interface.

The `fahrenheit` setter converts Fahrenheit into Celsius and delegates validation to the Celsius setter. This avoids maintaining two independent temperature values.

### Deleter

A deleter executes when the `del` statement targets a property.

The `SecureDocument` class demonstrates controlled deletion by replacing its content with a deletion marker rather than removing the internal attribute.

This is an application-level deletion operation, not secure erasure of the underlying memory.

### Read-only properties

The `Employee` class exposes an employee identifier through a getter without providing a setter.

The public interface permits reading but not ordinary assignment.

Read-only properties are useful for identifiers, calculated metadata, and values that should not be changed through normal application operations.

They do not automatically provide deep immutability. Other mutable attributes within the same object can still change.

## 3. Computed Properties

A computed property derives its value from other attributes instead of maintaining a separate stored value.

The `Rectangle` class provides:

- `area`: width multiplied by height.
- `perimeter`: twice the sum of width and height.

The calculated values remain consistent with the current dimensions because they are evaluated when accessed.

This design avoids storing redundant state.

For a constant number of arithmetic operations, both calculations have O(1) time complexity.

Computed properties are appropriate for inexpensive calculations. Expensive calculations may require caching.

## 4. Property Validation and Encapsulation

Encapsulation controls how internal object state is accessed and modified.

A property acts as a validation boundary between the caller and the object's internal representation.

The `UserAccount` class applies validation to:

| Property | Validation |
|---|---|
| `username` | Length and permitted characters |
| `email` | Basic email format and normalization |
| `age` | Integer between 18 and 120 |
| `active` | Boolean value |

Validation occurs during assignment rather than being repeated throughout the application.

The `ValidationError` exception provides a consistent failure mechanism.

The use of private-by-convention attributes such as `_email` communicates that callers should interact through the public property.

Python does not enforce underscore-based privacy. It is an access convention.

## 5. Property Inheritance and Overriding

Properties participate in inheritance and method resolution.

The `Product` class defines a `display_price` property.

`DiscountedProduct` overrides that property to display the price after applying a percentage discount.

The public interface remains the same, while the derived class changes the calculation.

This supports polymorphism and allows application code to work with different product types through a consistent interface.

## 6. The Descriptor Protocol

Descriptors provide a lower-level mechanism for controlling attribute access.

A descriptor implements one or more of these methods:

| Method | Responsibility |
|---|---|
| `__get__` | Retrieve the attribute |
| `__set__` | Assign the attribute |
| `__delete__` | Delete the attribute |
| `__set_name__` | Receive the owning class and attribute name |

The `PositiveNumber` descriptor centralizes numeric validation.

The `BankAccount` class uses it for balance management.

The descriptor stores the actual value under a private instance attribute. This prevents recursive calls to the descriptor when updating the value.

Descriptors are useful when the same validation mechanism must be reused across several classes.

A property is itself a descriptor.

### Property versus descriptor

| Characteristic | Property | Custom descriptor |
|---|---|---|
| Primary use | Control an individual class attribute | Reuse attribute behavior |
| Implementation | `property()` or decorators | Descriptor methods |
| Reusability | Usually class-specific | Across multiple classes |
| Complexity | Lower | Higher |
| Storage | Commonly private instance attributes | Depends on descriptor design |

## 7. Cached Properties and Cache Invalidation

Repeated computation can become expensive when a derived value depends on a large collection.

The `ExpensiveReport` class demonstrates a cached computed property.

The first access calculates the total and stores it. Later accesses reuse the cached result.

When `add_value()` modifies the underlying collection, the cached value is invalidated.

The next access recalculates the total.

For N values:

- Initial calculation: O(N).
- Cached access: O(1).
- Cache invalidation: O(1).
- Recalculation after modification: O(N).

The implementation uses an explicit invalidation flag rather than assuming that cached values remain correct.

This is important because a cached property becomes incorrect when its dependencies change without invalidation.

Python also provides `functools.cached_property` for suitable instances with an instance dictionary. That decorator caches the computed value as an instance attribute. It does not automatically invalidate the value when dependencies change.

## 8. JavaScript Property Engineering

JavaScript implements property behavior through accessor descriptors.

The JavaScript source provides several distinct approaches.

### Getter and setter accessors

The `Temperature` class uses `get` and `set` declarations.

Private class fields use the `#` prefix, providing language-enforced private state.

### Proxy

`createValidatedConfiguration()` uses a `Proxy` to intercept property assignments.

The proxy checks permitted configuration fields and rejects unknown or invalid values.

This is useful for dynamic objects whose valid fields are determined by a runtime policy.

A proxy introduces additional runtime behavior and should be used selectively.

### Property descriptors

`Object.defineProperty()` creates an accessor descriptor for the account balance.

A `WeakMap` stores the underlying value without exposing it as an ordinary object field.

### Event-driven properties

`ObservableUser` extends `EventEmitter`.

Changing the email address emits an event containing the previous value, the new value, and a timestamp.

This allows other components to react to state changes without tightly coupling themselves to the setter implementation.

### Asynchronous property-backed services

`ReportService` maintains a cache of pending promises and completed results.

Concurrent requests for the same report share one pending operation.

Failed requests remove their cached promise, allowing subsequent attempts.

This is an asynchronous service abstraction rather than a native asynchronous JavaScript property. JavaScript getters do not provide a dedicated asynchronous property mechanism.

## 9. C++17 Property Modeling

C++ does not provide Python-style built-in properties.

The C++ implementation models property behavior through encapsulation, getter methods, setter methods, and controlled object state.

The `Temperature` class demonstrates controlled assignment and conversion.

The `Employee` class demonstrates an immutable identifier using a `const` member.

The `Rectangle` class exposes computed values through getter methods.

The `Inventory` class demonstrates cached aggregate calculations using a `dirty_` flag.

The `BankAccount` class restricts balance modifications to validated operations.

### C++ design considerations

- Private members prevent unrestricted direct access.
- Const-qualified getters indicate that reading does not modify the object.
- Setter methods centralize validation.
- Exceptions communicate invalid operations.
- STL containers provide established collection management.
- Virtual methods support polymorphic property calculations.

The implementation uses `std::map` for inventory records. Lookup and insertion have O(log N) complexity.

Recomputing the inventory total takes O(N). Repeated cached reads take O(1).

## 10. Java 17 Enterprise Property Modeling

Java provides conventional getter and setter methods rather than Python-style property decorators.

The Java implementation combines encapsulation with records, enums, immutable identifiers, and service classes.

### Records

`EmployeeIdentity` uses a Java record.

Records provide a compact representation of immutable data carriers. Their components are final, and their canonical constructor can enforce validation.

### Monetary properties

`BankAccount` uses `BigDecimal` instead of floating-point arithmetic for financial values.

The implementation enforces two decimal places and prevents negative balances.

This avoids common precision problems associated with binary floating-point representations of decimal currency.

### State properties

`CustomerAccount` uses an enum to represent account states:

- `ACTIVE`
- `SUSPENDED`
- `CLOSED`

A closed account cannot return to an active or suspended state.

This is a state-transition rule, not merely a value-format validation rule.

### Concurrent caching

`ReportService` uses `ConcurrentHashMap.computeIfAbsent()` to maintain computed report values.

The concurrent map provides thread-safe map operations.

The calculation counter records cache misses that invoke the report supplier.

The design assumes that the underlying report source is safe for concurrent access.

## 11. PostgreSQL Property Modeling

The PostgreSQL implementation models properties as relational data and uses database constraints to enforce data integrity.

### Property definitions

`property_definitions` stores metadata about available properties.

Each definition specifies:

- Property name.
- Data type.
- Required status.
- Read-only status.
- Optional minimum value.
- Optional maximum value.

PostgreSQL ENUM types restrict the supported property categories.

### Typed property values

`employee_properties` stores values using separate typed columns.

The `one_property_value` constraint requires exactly one non-null value column.

A trigger verifies that the populated column matches the property definition.

This separates property metadata from property values.

The composite primary key prevents duplicate definitions of the same property for one employee.

### Validation triggers

`validate_employee_property()` checks:

1. Whether the property definition exists.
2. Whether exactly one value is supplied.
3. Whether the property is read-only.
4. Whether the selected value column matches the declared type.
5. Whether numeric values satisfy configured boundaries.

A trigger executes this function before inserts and updates.

This protects the database against invalid writes that bypass application-level validation.

### Generated properties

The `inventory` table defines `inventory_value` as a stored generated column.

Its value is derived from quantity multiplied by unit price.

PostgreSQL maintains the generated value when its dependent columns change.

A B-tree index supports queries that sort or filter inventory by calculated value.

### Audit properties

The `property_audit` table stores salary changes.

An `AFTER UPDATE` trigger captures the old and new salary values.

This creates an application-level audit history.

A database audit table should be protected with appropriate permissions. An application role that can modify audit records can undermine its reliability.

### Transaction management

The SQL script uses a transaction to group database operations.

A savepoint establishes a recoverable point within that transaction.

PL/pgSQL exception blocks isolate intentionally invalid operations so that their failures do not abort the surrounding transaction.

## 12. Distinguishing Property Mechanisms

The implementations demonstrate several mechanisms that should not be treated as interchangeable.

| Mechanism | Main responsibility | Example |
|---|---|---|
| Getter | Retrieve a value | `celsius` |
| Setter | Control assignment | `email` |
| Deleter | Control deletion | `content` |
| Read-only property | Prevent ordinary assignment | `employee_id` |
| Computed property | Derive a value | `area` |
| Cached property | Reuse an expensive result | `total` |
| Descriptor | Reuse attribute behavior | `PositiveNumber` |
| Proxy | Intercept dynamic property operations | Configuration |
| Event-driven accessor | Publish changes | Email updates |
| Database trigger | Enforce database-side behavior | Property validation |
| Generated column | Maintain a derived database value | `inventory_value` |

## 13. Edge Cases and Failure Handling

The implementations address several important failure conditions.

| Condition | Expected behavior |
|---|---|
| Temperature below absolute zero | Reject assignment |
| Non-numeric measurement | Reject assignment |
| Invalid email | Reject assignment |
| Negative financial balance | Reject assignment |
| Withdrawal exceeding available balance | Reject transaction |
| Zero or negative rectangle dimension | Reject assignment |
| Invalid inventory quantity | Reject update |
| Invalid employee identifier | Reject construction |
| Invalid property data type | Reject database operation |
| Modification of a read-only property | Reject database operation |
| Invalid account state transition | Reject transition |
| Failed asynchronous report retrieval | Remove failed cache entry |

These controls reduce the likelihood of inconsistent object state and invalid persisted data.

## 14. Performance Considerations

Property access usually introduces a method call or descriptor operation.

The performance impact is generally small relative to database access, network operations, or expensive calculations, but it can matter in high-frequency execution paths.

Important considerations include:

- Avoid unnecessary computation inside getters.
- Avoid database queries inside frequently accessed properties.
- Cache expensive calculations when their dependencies are controlled.
- Invalidate caches whenever underlying data changes.
- Avoid unnecessary descriptor complexity.
- Use appropriate collection types for the expected access pattern.
- Use database indexes for frequently filtered or sorted properties.
- Avoid storing redundant computed state unless consistency can be maintained.

A property should behave predictably. A getter that silently performs expensive external operations can make ordinary attribute access difficult to reason about.

## 15. Security and Reliability

Properties can enforce application-level invariants, but they are not a complete security boundary.

Important security practices include:

- Keep sensitive internal attributes inaccessible through normal public interfaces.
- Validate inputs at every trusted boundary.
- Do not assume underscore-prefixed Python attributes are private.
- Avoid exposing credentials or confidential information through property getters.
- Restrict database permissions independently of application validation.
- Use parameterized SQL rather than constructing SQL statements from untrusted input.
- Protect audit tables against unauthorized modification.
- Use decimal arithmetic for monetary values.
- Avoid returning mutable internal collections when callers should not modify them.
- Define explicit cache invalidation behavior.
- Consider concurrency when multiple operations can modify shared state.

## 16. Executing the Implementations

| File | Runtime | Execution |
|---|---|---|
| Python | Python 3.10+ | `python properties.py` |
| JavaScript | Node.js 18+ | `node properties.js` |
| C++17 | C++ compiler | `g++ -std=c++17 -O2 properties.cpp -o properties` |
| Java | Java 17 | `javac PropertiesEnterprise.java` followed by `java PropertiesEnterprise` |
| PostgreSQL | PostgreSQL 15+ | Execute the SQL script using `psql` |

The Python implementation includes unit tests using `unittest`.

The JavaScript implementation uses Node.js assertions.

The C++ implementation demonstrates validation and exception handling through executable scenarios.

The Java implementation uses assertions for test scenarios. Execute it with assertions enabled using `java -ea PropertiesEnterprise`.

The PostgreSQL script creates a dedicated schema, inserts sample records, creates reporting views, validates property values, records audit events, and demonstrates transaction handling.

## 17. Implementation Limitations

The implementations intentionally use different language mechanisms.

- Python properties are native descriptors and support getter, setter, and deleter behavior.
- JavaScript accessors and proxies operate through JavaScript property semantics but do not reproduce every Python descriptor capability.
- C++ uses explicit methods rather than native property syntax.
- Java uses conventional accessors, immutable records, and service abstractions.
- PostgreSQL models persistent property metadata and values rather than in-memory object attributes.

The Python cached-report example invalidates its cache when changes pass through `add_value()`. Direct mutation of its public `values` list can bypass that invalidation mechanism.

The JavaScript inventory example uses controlled mutation through `setQuantity()`. Its cache is not designed as a distributed cache.

The C++ inventory example is single-threaded and does not provide synchronization for concurrent modifications.

The Java report service provides an in-memory concurrent cache. It does not persist report results or coordinate cache invalidation across application instances.

The PostgreSQL generic property model supports typed values and numeric range checks. More advanced requirements, such as complex cross-property validation, tenant-specific authorization, and schema versioning, require additional domain rules.

## 18. Technical Relationship Across Implementations

The central design principle is controlled access to object or database state.

The Python property model provides the most direct attribute-oriented implementation.

The JavaScript implementation emphasizes runtime interception, event-driven changes, and asynchronous caching.

The C++ implementation emphasizes explicit interfaces, compile-time types, and controlled state mutation.

The Java implementation emphasizes enterprise domain modeling, immutable data structures, monetary precision, and concurrent services.

The PostgreSQL implementation extends validation and integrity enforcement to persisted data.

These mechanisms address different layers of the same engineering problem:

**A property is not simply a stored value. It is an interface through which a value is accessed, validated, calculated, transformed, observed, or protected.**
