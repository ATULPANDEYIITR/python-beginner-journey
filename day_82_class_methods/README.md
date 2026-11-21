# Class Methods

## 1. Introduction

A class method is an operation associated with a class rather than an individual object.

It is useful when an operation needs to work with class-level information, create objects through alternative construction procedures, manage shared registries, or implement behavior that belongs to a type rather than a particular instance.

Class methods are particularly relevant to object-oriented domain modeling, factory patterns, shared configuration, object creation, and centralized business operations.

The exact implementation differs between programming languages.

Python provides a dedicated `@classmethod` decorator. Java, C++, and JavaScript provide static methods, which offer class-level behavior but do not have identical semantics.

## 2. Understanding Class-Level and Instance-Level Behavior

An object-oriented program can contain three different categories of operations.

| Category | Associated with | Primary responsibility |
|---|---|---|
| Instance method | Individual object | Operates on object-specific data |
| Class method | Class | Operates on class-level information or creates objects |
| Static method | Class namespace | Performs a related operation without requiring instance or class state |

Consider an employee-management system.

An individual employee has:

- Employee ID
- Name
- Department
- Salary

The employee class can maintain:

- An employee registry
- A minimum salary policy
- Employee creation statistics
- Department-level reports

The distinction is important because changing one employee's salary should not require changing the entire employee class.

Similarly, retrieving an employee from a shared registry should not require constructing another employee object.

## 3. Class Methods in Python

Python provides the `@classmethod` decorator.

Its first parameter is conventionally named `cls`.

`cls` refers to the class on which the method is called.

It is different from `self`, which refers to an individual object.

### 3.1 Syntax

A class method follows this structure:

- Declare a method inside a class.
- Apply `@classmethod`.
- Receive the class through `cls`.
- Access class-level information or create objects using `cls`.

### 3.2 Instance Method Versus Class Method

| Property | Instance method | Class method |
|---|---|---|
| First parameter | `self` | `cls` |
| Receives | Object instance | Calling class |
| Accesses instance attributes | Yes | Not directly |
| Accesses class attributes | Yes | Yes |
| Creates objects | Possible | Common use |
| Uses `@classmethod` | No | Yes |

Example:

`Employee.give_raise()` is not a suitable class-level operation because a salary increase belongs to an individual employee.

An operation such as `Employee.find_by_id()` is appropriate because it searches the shared employee registry.

### 3.3 Alternative Constructors

An alternative constructor creates an object using a different input representation.

The employee implementation supports:

- Dictionary-based construction through `from_record()`.
- CSV-based construction through `from_csv_line()`.

Both methods eventually construct an employee object.

This avoids duplicating object validation and initialization logic.

The factory method delegates construction to `cls`, preserving the class responsible for creating the object.

### 3.4 Inheritance and Polymorphism

A significant property of Python class methods is that `cls` refers to the actual calling class.

Consider:

- `Employee`
- `ContractEmployee`

When an inherited class method is called through `ContractEmployee`, its `cls` argument refers to `ContractEmployee`.

This supports inheritance-aware factories.

The contract employee implementation overrides the alternative constructor because its constructor requires an additional contract-duration argument.

### 3.5 Shared Class Attributes

A class attribute is shared through the class rather than independently created for every object.

Examples include:

- Minimum salary
- Object registries
- Configuration values
- Counters

Mutable class attributes require careful handling.

If a dictionary is defined at class level, every instance can potentially interact with the same dictionary.

This is useful for a shared registry but can cause unexpected behavior when independent instances are expected.

The employee implementation uses a class-level dictionary to maintain registered employees.

### 3.6 Static Methods

A Python static method uses `@staticmethod`.

It does not automatically receive `self` or `cls`.

For example, calculating annual salary from a supplied monthly salary does not require access to an employee instance or the employee class.

The distinction is:

- Class methods receive the calling class.
- Static methods receive neither an object nor a class automatically.

## 4. Class Methods in JavaScript

JavaScript implements class-level operations through the `static` keyword.

A static method is invoked using the class name.

Example:

`Product.create(data)`

An instance method is invoked using an object.

Example:

`product.applyDiscount(10)`

### 4.1 Static Factory Methods

The JavaScript implementation provides `Product.create()`.

It validates the supplied data and creates a new product.

It also provides `Product.fromCSV()` for alternative construction.

The two methods demonstrate how static methods can centralize object creation.

### 4.2 Static Inheritance

JavaScript classes use prototype-based inheritance.

Static methods are inherited through the constructor's prototype chain.

A subclass can therefore access inherited static methods.

Using `new this(data)` inside a static factory allows the factory to construct the class through which it was invoked.

This differs from hardcoding `new Product(data)`.

### 4.3 Private Static Fields

JavaScript supports private static fields using the `#` prefix.

The product implementation uses:

- A private product registry
- A private minimum-price configuration
- A private event emitter

These fields cannot be accessed directly outside their declaring class.

Private static fields provide encapsulation for shared class-level state.

An important limitation is that a subclass cannot directly access a private static field declared by its parent class.

### 4.4 Static Initialization Blocks

A static initialization block executes when the class is initialized.

It is useful for initializing shared class resources.

The example configures the event emitter through a static initialization block.

### 4.5 Event-Driven Class Operations

The product registry publishes events when products are created or removed.

Other application components can subscribe to these events without modifying the object creation process.

The implementation also returns an unsubscribe function to prevent unnecessary event listeners from accumulating.

## 5. Class Methods in C++17

C++ implements class-level operations through static member functions.

A static member function belongs to the class.

It can be called without creating an object.

### 5.1 Static Member Functions

A static member function does not receive an implicit object pointer.

It cannot directly access non-static data members because there is no individual object associated with the call.

The C++ implementation uses static functions for:

- Product creation
- Registry lookup
- Product counting
- Minimum-price configuration
- Category aggregation
- Tax calculation

### 5.2 Static Data Members

Static data members represent state shared by all objects of a class.

In the example:

- `registry_` stores products.
- `minimum_price_` stores the shared minimum price.
- `created_count_` tracks successful product creation.

Their definitions are provided outside the class.

This is the traditional C++17 approach for non-inline static data members.

### 5.3 Static Factory Methods

The `Product::create()` method implements a factory operation.

It validates the product input, creates the object, inserts it into the shared registry, and returns a smart pointer.

The implementation uses `std::shared_ptr` to manage object lifetime automatically.

Copy construction and copy assignment are disabled to avoid accidental duplication of registered product objects.

### 5.4 Inheritance

Static member functions are inherited, but they are not virtual instance methods.

A subclass can declare another static method with the same name, hiding the inherited method.

This is different from runtime polymorphism through virtual functions.

The subscription product demonstrates a subclass-specific factory operation.

### 5.5 Performance Considerations

The implementation uses:

| Data structure | Purpose | Typical complexity |
|---|---|---|
| `unordered_map` | Product registry | Average O(1) lookup |
| `map` | Ordered category report | O(log n) insertion |
| `shared_ptr` | Shared object ownership | Constant-time reference-count operations |

The hash-based registry provides efficient lookup, although worst-case hash-table operations can be linear.

## 6. Class Methods in Java 17

Java provides static methods rather than Python-style class methods.

A static method belongs to the class and does not receive an implicit object reference.

The Java implementation applies static operations to an enterprise product catalog.

### 6.1 Static Factory Methods

`Product.create()` is a static factory method.

It creates and registers a product.

Static factory methods are useful when object construction requires:

- Input validation
- Business-rule enforcement
- Registry updates
- Alternative construction formats
- Controlled object creation

A factory method also provides a meaningful operation name instead of requiring callers to use a constructor directly.

### 6.2 Records

Java 17 records provide concise immutable data carriers.

The implementation defines:

- `ProductInput`
- `CategoryReport`
- `AuditEvent`

Records are appropriate when the purpose of a type is to carry structured data.

They are different from ordinary classes that maintain mutable business state.

### 6.3 Concurrent Class-Level State

The Java implementation uses `ConcurrentHashMap` for the product registry.

It supports concurrent access to shared registry operations.

`putIfAbsent()` provides an atomic insertion operation that prevents duplicate identifiers.

An `AtomicLong` maintains the creation counter.

The minimum-price configuration is declared `volatile` so updates to the reference are visible across threads.

These mechanisms do not automatically make every operation on a product or the entire catalog transactional.

Additional synchronization is necessary when several related changes must occur atomically.

### 6.4 Static Method Hiding

Static methods in Java are resolved using the class reference rather than runtime object dispatch.

A subclass can hide an inherited static method by declaring another static method with the same signature.

This is not method overriding.

Instance methods use runtime polymorphism when they are appropriately overridden.

### 6.5 Service Layer

The `ProductService` class separates application-level operations from product-domain behavior.

It coordinates:

- Product registration
- Product discontinuation
- Audit-event recording

This separation is useful in enterprise applications because domain objects should not necessarily manage every application workflow.

## 7. Static Methods and Class Methods Across Languages

The terminology is similar, but the mechanisms differ.

| Feature | Python | JavaScript | C++17 | Java 17 |
|---|---|---|---|---|
| Class-level declaration | `@classmethod` | `static` | `static` | `static` |
| Receives calling class automatically | Yes | No | No | No |
| Receives instance automatically | No | No | No | No |
| Static shared attributes | Class attributes | Static fields | Static data members | Static fields |
| Alternative construction | Class method | Static factory | Static factory | Static factory |
| Static inheritance | `cls` supports dynamic subclass construction | Constructor inheritance | Static members inherited | Static members inherited |
| Dynamic factory dispatch | Through `cls` | Through `this` | Explicit implementation | Explicit implementation |

Python class methods and static methods should not be treated as identical.

In JavaScript, C++, and Java, static methods provide class-level operations but do not reproduce Python's automatic `cls` parameter.

## 8. PostgreSQL Representation of Class-Level Operations

PostgreSQL is a relational database system rather than an object-oriented programming language.

It does not provide native Python-style class methods.

Database functions, procedures, triggers, and shared configuration tables can implement similar operational responsibilities.

The SQL implementation models a product catalog.

### 8.1 Configuration Table

The `catalog_configuration` table stores the shared minimum-price policy.

It represents configuration that applies across the product catalog.

The single-row constraint ensures that only one configuration record can exist.

### 8.2 Product Registry

The `products` table represents the persistent product registry.

It contains:

- Product identity
- Name
- Category
- Price
- Status
- Creation timestamp
- Modification timestamp

Primary keys prevent duplicate product identifiers.

Check constraints reject invalid values.

Foreign keys connect specialized subscription records to their corresponding products.

### 8.3 Factory Functions

`create_product()` provides controlled product construction.

It validates the input and inserts the product.

`create_product_from_json()` provides an alternative input format.

These functions perform responsibilities similar to alternative constructors and static factories.

### 8.4 Triggers

The price-validation trigger checks the configured minimum price before inserting or updating a product.

The audit trigger records product creation, modification, and deletion.

Database triggers are useful when an integrity rule must apply regardless of which application performs the database operation.

### 8.5 Aggregation

`get_catalog_statistics()` calculates:

- Product count
- Total category value
- Average category price

It operates over the entire catalog rather than requiring an individual product object.

This is analogous to a class-level reporting operation.

### 8.6 Transaction Management

The SQL script demonstrates savepoints and rollback.

A savepoint establishes an intermediate transaction boundary.

Rolling back to a savepoint reverses operations performed after that point without discarding earlier work in the transaction.

The final commit makes the remaining transaction changes permanent.

## 9. Practical Design Patterns

Class-level operations are useful in several common software-design situations.

| Pattern | Purpose | Example |
|---|---|---|
| Factory Method | Centralized object creation | `Product.create()` |
| Alternative Constructor | Multiple input formats | `Employee.from_csv_line()` |
| Registry | Shared object lookup | `Product.find()` |
| Configuration Manager | Shared policy management | `update_minimum_price()` |
| Aggregation | Class-wide reporting | `generateReport()` |
| Utility Method | Independent calculation | `calculate_tax()` |

### 9.1 Factory Method

A factory method centralizes object creation.

It can enforce validation before an object becomes available to the application.

### 9.2 Registry

A registry maintains a collection of objects or identifiers.

It is useful when objects must be located without maintaining individual references throughout the application.

### 9.3 Shared Configuration

Class-level configuration is useful when a rule applies to all objects of a particular type.

Examples include:

- Minimum permitted price
- Maximum permitted discount
- Default currency
- Supported product categories

In production applications, configuration changes may require validation, authorization, audit logging, and synchronization.

### 9.4 Utility Operations

A static utility method is appropriate when a calculation is logically associated with a class but does not require access to its state.

If a method requires shared class information, a class method or another class-level operation may be more appropriate.

## 10. Important Edge Cases and Failure Conditions

| Condition | Potential problem | Appropriate control |
|---|---|---|
| Empty input | Invalid object construction | Input validation |
| Duplicate identifier | Registry inconsistency | Unique identifiers |
| Invalid numeric value | Incorrect calculations | Numeric validation |
| Shared mutable state | Unexpected cross-instance changes | Encapsulation |
| Invalid subclass construction | Incorrect factory behavior | Inheritance-aware construction |
| Concurrent insertion | Duplicate registry entries | Atomic insertion |
| Concurrent configuration changes | Inconsistent policy observations | Synchronization |
| Invalid state transition | Business-rule violation | State validation |
| Failed database transaction | Partial persistence | Transaction rollback |
| Missing audit record | Incomplete operational history | Database auditing |

### 10.1 Shared Mutable State

A mutable class-level dictionary or map is shared by every object using that class-level attribute.

Modifying it through one reference can affect other users of the same registry.

A class-level registry should therefore have clearly defined ownership and access rules.

### 10.2 Thread Safety

A static or class-level method is not automatically thread-safe.

Multiple threads can attempt to modify shared state simultaneously.

Thread-safe collections and synchronization mechanisms can help, but the complete business operation must also be considered.

For example, checking whether an identifier exists and inserting it as two independent operations can still create a race condition.

Atomic insertion is preferable.

### 10.3 Inheritance

Factory methods should account for subclasses that require additional constructor parameters.

Hardcoding the parent class can accidentally create the wrong object type.

Python's `cls` and JavaScript's static `this` provide useful inheritance-aware construction mechanisms.

Java and C++ generally require explicit subclass factories or other construction arrangements.

### 10.4 Database Consistency

Application-level validation does not replace database constraints.

The database must enforce important persistent-data rules because multiple applications, services, and administrative operations may access the same tables.

## 11. Security Considerations

Class-level operations can affect many objects and therefore require appropriate access controls.

Important controls include:

- Restrict access to configuration-changing methods.
- Validate all externally supplied identifiers.
- Reject invalid numeric and textual inputs.
- Avoid exposing internal registries directly.
- Use parameterized database queries.
- Apply least-privilege database permissions.
- Maintain audit records for sensitive operations.
- Avoid logging confidential object attributes.
- Protect shared configuration against unauthorized modification.
- Use atomic database transactions for related operations.

A static method is not inherently secure because it is declared at class level.

Security depends on its implementation and the permissions of the calling application.

## 12. Performance Considerations

Class methods can improve application organization, but they do not automatically improve execution speed.

Performance depends on the work performed.

| Operation | Typical implementation | Performance consideration |
|---|---|---|
| Identifier lookup | Hash map | Average O(1) |
| Full registry traversal | Dictionary or map | O(n) |
| Category aggregation | Grouping operation | O(n) |
| Sorted reporting | Sorting | O(n log n) |
| Database lookup | Indexed primary key | Typically O(log n) |
| Concurrent insertion | Atomic map operation | Contention depends on workload |

For large registries, retrieving every object to calculate a report may consume unnecessary memory.

Database aggregation can be more efficient when the authoritative data already resides in PostgreSQL.

## 13. Execution and File Organization

The five source implementations are independent.

| File | Runtime | Main implementation |
|---|---|---|
| `class_methods.py` | Python 3.10+ | Decorated class methods and inheritance-aware factories |
| `class_methods.js` | Node.js 18+ | Static methods, private fields, and event-driven operations |
| `ClassMethods.cpp` | C++17 | Static member functions and smart-pointer registry |
| `ClassMethods.java` | Java 17 | Static factories, records, and concurrent registry |
| `class_methods.sql` | PostgreSQL 15+ | Functions, procedures, triggers, and transactions |

### Python

Run:

`python class_methods.py`

### JavaScript

Run:

`node class_methods.js`

### C++17

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic ClassMethods.cpp -o class_methods`

Run:

`./class_methods`

On Windows:

`class_methods.exe`

### Java 17

Compile:

`javac ClassMethods.java`

Run:

`java ClassMethods`

### PostgreSQL

Execute the complete SQL file using a PostgreSQL client connected to the intended database.

The script creates a dedicated schema named `class_methods_demo`.

It drops an existing schema with that name before rebuilding the demonstration database objects. It should therefore be executed only in an appropriate learning or testing database.

## 14. Core Conceptual Distinctions

The most important distinctions are:

1. An instance method operates on an individual object.
2. A class method in Python receives the calling class through `cls`.
3. A static method operates without an automatically supplied instance or class reference.
4. A static factory method centralizes object creation.
5. A class attribute or static field represents shared class-level state.
6. Inheritance-aware factories must preserve the intended subclass type.
7. Database functions and procedures provide class-level operational equivalents, not native object-oriented class methods.

Class-level operations are most effective when the responsibility genuinely belongs to the type or to shared domain state rather than to an individual object.
