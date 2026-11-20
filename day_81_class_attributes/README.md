# Class Attributes

## Technical Scope

This project examines class attributes through five executable implementations using Python, JavaScript, C++17, Java 17, and PostgreSQL.

A class attribute is a value or property associated with a class rather than independently created for every object. Instances can access class attributes through their class definitions. An instance can also define an attribute with the same name, creating an instance-level override.

The implementations demonstrate shared state, instance isolation, inheritance, attribute shadowing, configuration management, validation, and database-backed attribute resolution.

## Core Concepts

### Class Attributes

A class attribute belongs to the class itself.

For example, a repository management system might define:

- Organization name
- Maximum repository capacity
- Supported programming languages
- Default repository visibility
- Shared configuration values

All instances that do not override these attributes can access the same class-level definitions.

A class attribute is useful when multiple objects need to share a common configuration or reference value.

### Instance Attributes

An instance attribute belongs to one particular object.

Examples include:

- Repository name
- Repository owner
- Commit count
- Creation timestamp
- Current operational state

Changing an instance attribute normally affects only that object.

| Property | Class Attribute | Instance Attribute |
|---|---|---|
| Ownership | Class | Individual object |
| Storage | Class-level definition | Object-level state |
| Sharing | Available to instances | Normally isolated |
| Creation | Defined on the class | Defined on an instance |
| Modification | Can affect all inheriting instances | Affects the selected instance |
| Typical use | Shared configuration | Object-specific information |

### Attribute Lookup

When an instance accesses an attribute, the programming language follows its attribute-resolution rules.

In Python, the general lookup process searches the instance and then its class hierarchy, subject to descriptors and other lookup mechanisms.

Consider the following conceptual arrangement:

- Repository class defines `organization`.
- Repository instance A does not define `organization`.
- Repository instance B defines its own `organization`.

The resulting values are:

| Access | Result |
|---|---|
| Repository class | Shared organization value |
| Instance A | Shared organization value |
| Instance B | Instance-specific value |

This behavior is called attribute shadowing.

Shadowing does not automatically modify the original class attribute.

### Mutable Class Attributes

Mutable class attributes require particular attention.

A shared dictionary, list, or set can be modified through any instance accessing the same object.

For example, two instances accessing one class-level dictionary can observe changes made by either instance.

This can cause unexpected state sharing.

The Python implementation demonstrates this behavior using a shared dictionary and then shows how instance assignment creates a separate reference.

Safer approaches include:

- Use immutable values for shared configuration.
- Create mutable collections inside the constructor when they belong to individual objects.
- Protect shared mutable state with appropriate synchronization.
- Avoid exposing internal mutable collections directly.
- Use controlled methods for modifying shared state.

A thread-safe counter or registry requires more than simply declaring a class attribute.

## Class Attributes Across Programming Languages

### Python

Python supports class attributes through variables declared directly inside a class body.

The implementation uses:

- `ClassVar` to identify class-level attributes in type annotations.
- `dataclass` for structured attribute definitions.
- `Enum` for attribute scope.
- Dictionaries for shared repository registries.
- Lists and tuples for collection handling.
- `classmethod` for operations that receive the class.
- `staticmethod` for validation independent of object state.
- `threading.Lock` for synchronized registry updates.
- Exceptions for validation and state failures.

**Class methods**

A class method receives the class as its first argument, conventionally named `cls`.

It is appropriate for:

- Class-level configuration changes.
- Factory methods.
- Shared registry operations.
- Class-level statistics.

**Static methods**

A static method does not automatically receive either an instance or a class reference.

It is useful for validation and utility operations that do not depend on object state.

**Inheritance**

A subclass can inherit a class attribute from its parent.

It can also define another attribute with the same name. The subclass definition then shadows the inherited class attribute for normal subclass lookup.

The implementation uses `Repository` and `EnterpriseRepository` to demonstrate this distinction.

### JavaScript

JavaScript provides static class fields and static methods.

A static field belongs to the constructor rather than an individual instance.

The implementation uses:

- Static class fields for shared configuration.
- Private static fields for registry management.
- `Map` for repository storage.
- `Object.freeze()` for immutable configuration objects and arrays.
- `Promise` for asynchronous creation operations.
- `EventEmitter` for repository lifecycle events.
- `crypto.randomUUID()` for repository identifiers.
- Node.js file operations for audit logging.

A static property is accessed through the class:

`Repository.organization`

An instance property is accessed through an object:

`repository.name`

JavaScript also supports inheritance of static properties through the constructor inheritance chain.

An important distinction is that assigning a property to an instance does not modify the corresponding static property on its constructor.

Static fields are not automatically shared with unrelated classes.

### C++17

C++ uses static data members to represent attributes shared by instances of a class.

The implementation demonstrates:

- Static data members.
- Static member functions.
- `std::atomic` for concurrent counter access.
- `std::mutex` for synchronized registry operations.
- `std::map` for repository lookup.
- `std::weak_ptr` for non-owning registry references.
- `std::shared_ptr` for controlled object ownership.
- Enumerations for visibility and repository state.
- Exceptions for invalid operations.

A static data member has one class-level storage location rather than one independent copy per object.

In this implementation, static members are declared in the class and defined outside the class.

The `const` organization name and language collection represent shared configuration.

The enterprise subclass defines its own organization attribute, hiding the parent member when accessed through the subclass.

C++ static member functions do not receive a `this` pointer because they are not associated with a particular instance.

### Java 17

Java uses the `static` keyword for class-level fields and methods.

The implementation uses:

- Static final fields for shared constants.
- Static volatile configuration for visibility across threads.
- `AtomicInteger` for concurrent counter updates.
- `ConcurrentHashMap` for repository registration.
- Records for immutable review and status-check data.
- Interfaces for eligibility rules.
- Streams for approval evaluation.
- Enums for domain states.
- Custom exceptions for invalid operations.
- Service classes for enterprise policy evaluation.

A static field belongs to the declaring class.

A static field declared again in a subclass hides the parent field. Static fields are resolved according to the reference used to access them rather than through runtime method overriding.

Java static methods also use method hiding rather than instance-method overriding.

The implementation distinguishes class-level configuration from instance-level repository state.

## Inheritance and Class Attribute Shadowing

Inheritance allows a subclass to reuse attributes defined by a parent class.

Consider this hierarchy:

    Repository
        |
        +-- EnterpriseRepository

The parent class defines:

- Organization
- Maximum repository capacity
- Default configuration

The enterprise subclass defines its own organization and capacity values.

The child class therefore has different class-level configuration without modifying the parent's definitions.

| Access | Parent Class | Enterprise Subclass |
|---|---|---|
| Organization | OpenSystems | EnterpriseSystems |
| Maximum capacity | 100 | 50 |
| Compliance requirement | Not defined | Enabled |

This demonstrates class attribute shadowing.

Shadowing should not be confused with changing a parent class attribute. A child definition establishes a separate class-level value.

Inheritance rules vary between programming languages, particularly regarding static members, property lookup, and access restrictions.

## Class Attributes and Configuration Management

Class attributes are useful for shared application settings.

Examples include:

- Default access levels.
- Service limits.
- Organization identifiers.
- Supported feature lists.
- Default processing policies.
- Shared application configuration.

The implementations use repository management as the domain scenario.

The class-level organization and repository capacity represent shared configuration. Each repository maintains independent operational data.

The configuration distinction is:

    Shared class configuration
              |
              v
        Repository class
              |
        +-----+-----+
        |           |
        v           v
    Repository A  Repository B
        |           |
        v           v
    Own commits   Own commits
    Own owner     Own owner

Changes to shared configuration can affect instances that have not created their own overrides.

An instance override preserves its own value independently.

## PostgreSQL Data Model

The PostgreSQL implementation represents class attributes using relational tables.

| Table | Responsibility |
|---|---|
| `class_definition` | Stores classes and parent-class relationships |
| `class_attribute` | Stores shared class-level attribute definitions |
| `class_instance` | Stores individual objects |
| `instance_attribute` | Stores instance-level overrides |
| `attribute_audit` | Records attribute modification history |

### Class Definition

The `class_definition` table stores each class and its optional parent.

A parent-child relationship is represented through `parent_class_id`.

The database uses a self-referencing foreign key to maintain referential integrity.

A recursive trigger validation prevents circular inheritance.

### Class Attributes

The `class_attribute` table stores:

- Attribute name.
- Owning class.
- Data type.
- Attribute value.
- Mutability metadata.
- Description.

Typed columns support text, integer, Boolean, and numeric values.

Check constraints enforce the relationship between the declared data type and its stored value.

The unique constraint prevents duplicate attribute definitions within the same class.

### Instance Attributes

The `class_instance` table stores individual objects.

The `instance_attribute` table stores overrides separately.

This separation is important because an instance override must not change the shared class-level definition.

For example:

- The parent class defines organization as `OpenSystems`.
- A repository instance overrides it with `CustomFinanceSystems`.
- Other instances continue using their effective class-level values.

### Effective Attribute Resolution

The `effective_instance_attributes` view resolves attribute values using this precedence:

1. Instance-level override.
2. Current class definition.
3. Nearest parent-class definition.
4. Higher inherited class definitions.

The recursive hierarchy query discovers parent classes.

`DISTINCT ON` selects the nearest class definition for each instance and attribute name.

`COALESCE` selects an instance override when available, otherwise the resolved class-level value.

The `attribute_source` column identifies whether the result comes from an instance override or a class default.

The `get_effective_attribute` function supports retrieval of a specific effective attribute.

### Audit History

The `attribute_audit` table records:

- Entity type.
- Entity identifier.
- Attribute name.
- Operation.
- Previous value.
- New value.
- Modification timestamp.
- Database user.

An `AFTER` trigger records changes to instance attributes.

This creates an audit trail for instance-level configuration changes.

## Validation and Integrity

The implementations enforce different validation requirements.

| Validation | Purpose |
|---|---|
| Required names | Prevent empty identifiers |
| Unique repository names | Prevent duplicate registration |
| Valid visibility | Restrict configuration values |
| Repository capacity | Enforce operational limits |
| Active-state validation | Prevent operations on archived objects |
| Attribute type validation | Prevent incompatible values |
| Inheritance validation | Prevent circular relationships |
| Override validation | Require an inherited attribute definition |
| Audit validation | Restrict supported operation types |

Validation should occur at the appropriate boundary.

Application validation provides useful error messages and prevents invalid operations from proceeding.

Database constraints provide an additional integrity layer when multiple applications access the same database.

## Practical Differences Between Shared and Independent State

A class attribute is not a universal substitute for instance storage.

Consider the following requirements:

| Requirement | Appropriate Scope |
|---|---|
| Organization name shared by repositories | Class |
| Supported language collection | Class |
| Default repository visibility | Class |
| Repository owner | Instance |
| Commit count | Instance |
| Repository identifier | Instance |
| Repository creation timestamp | Instance |
| Per-repository audit configuration | Instance override |
| Shared service capacity | Class |

Choosing the wrong scope can introduce unwanted coupling.

For example, storing a repository's commit count as a class attribute would cause multiple repositories to share the same counter.

Storing an organization-wide configuration independently on every repository would introduce duplicated configuration and synchronization problems.

## Performance and Concurrency

### Python

- Dictionary lookup provides average constant-time access.
- Shared registry updates use a lock.
- Immutable tuples are suitable for shared collections.
- Lock scope should remain small.
- Shared state should not be exposed without appropriate controls.

### JavaScript

- `Map` provides efficient key-based lookup.
- Promise chaining serializes repository creation.
- EventEmitter separates lifecycle notifications from business operations.
- Immutable configuration reduces accidental modifications.
- Audit logging introduces file I/O and should be managed appropriately in production.

### C++17

- `std::map` provides logarithmic lookup and insertion.
- Atomic operations support concurrent counter updates.
- Mutexes protect compound registry operations.
- Smart pointers express object ownership.
- Static collections should have controlled initialization and lifetime.

### Java 17

- `ConcurrentHashMap` supports concurrent registry access.
- `AtomicInteger` provides atomic counter updates.
- `volatile` supports visibility of shared configuration changes.
- Immutable records simplify data exchange.
- Synchronization is used for instance operations requiring atomic state changes.

Atomicity of an individual field does not automatically make a multi-step business operation thread-safe.

A production implementation must define the consistency requirements for related updates.

## Failure Conditions and Limitations

The implementations demonstrate several failure scenarios:

- Empty repository names.
- Duplicate repository registration.
- Capacity limits.
- Unsupported visibility settings.
- Attempts to modify inactive repositories.
- Shared mutable state.
- Instance-level shadowing.
- Inherited attribute shadowing.
- Invalid database attribute types.
- Circular class inheritance.

The PostgreSQL implementation also demonstrates audit logging and transactional execution.

There are important implementation boundaries:

- The C++ and Java examples use in-memory registries rather than durable storage.
- The JavaScript audit file is a local demonstration rather than a centralized audit service.
- The PostgreSQL schema supports four basic data types rather than arbitrary structured attribute values.
- The PostgreSQL override validation uses database triggers and requires additional synchronization if class definitions are modified concurrently.
- The examples do not implement distributed configuration synchronization.
- Class attributes should not contain credentials or other sensitive values without appropriate protection.

The PostgreSQL inheritance model supports single-parent inheritance. Multiple inheritance would require a more extensive relationship and conflict-resolution model.

The database implementation also distinguishes class-level definitions from instance-level overrides, rather than attempting to reproduce every programming language's native object model.

## Execution

| File | Runtime | Execution |
|---|---|---|
| Python | Python 3.10+ | `python class_attributes.py` |
| JavaScript | Node.js 18+ | `node class_attributes.js` |
| C++17 | C++17 compiler | `g++ -std=c++17 -pthread class_attributes.cpp -o class_attributes` |
| Java | Java 17 | `javac ClassAttributesDemo.java` followed by `java ClassAttributesDemo` |
| PostgreSQL | PostgreSQL 15+ | Execute the SQL script using `psql` |

The Python and JavaScript implementations use standard-library capabilities.

The C++ implementation requires no external libraries.

The Java implementation requires no third-party dependencies.

The SQL implementation uses native PostgreSQL features.

## Educational Outcomes

The implementations demonstrate the following distinctions:

| Concept | Technical Understanding |
|---|---|
| Class attributes | Shared properties associated with a class |
| Instance attributes | Properties belonging to individual objects |
| Attribute lookup | Rules used to resolve attribute access |
| Shadowing | Defining another attribute with an existing name |
| Inheritance | Reusing parent-class definitions |
| Static members | Class-associated members in Java and C++ |
| Static fields | Constructor-associated fields in JavaScript |
| Class methods | Python methods receiving the class |
| Mutable class state | Shared mutable objects and synchronization risks |
| Immutable configuration | Preventing unintended shared-state changes |
| Attribute overrides | Instance-specific values replacing shared defaults |
| Database normalization | Separating class definitions, instances, and overrides |
| Recursive queries | Resolving inherited attribute definitions |
| Audit triggers | Recording database attribute modifications |
