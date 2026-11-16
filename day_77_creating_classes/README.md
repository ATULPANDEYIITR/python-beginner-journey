# Creating Classes: Object-Oriented Programming and Class Design

## 1. Introduction

A class is a programmer-defined structure that describes the properties and behaviour of objects. It provides a reusable design from which individual objects can be created.

A class combines data and operations into one logical unit. The data represents an object's state, while its methods define the operations that can be performed on that state.

For example, a banking application can define an `Account` class containing:

- Account identifier
- Account owner
- Account balance
- Account status
- Deposit operation
- Withdrawal operation
- Account closure operation

Individual bank accounts are objects created from this class. Each object has its own state while sharing the behaviour defined by the class.

The implementations use a banking domain to demonstrate class construction, inheritance, encapsulation, object creation, polymorphism, validation, and state management. The PostgreSQL implementation provides a relational representation of class definitions and their instances.

## 2. Class and Object Fundamentals

### 2.1 Class

A class is a blueprint that defines the structure and behaviour of objects.

A class typically contains:

| Component | Purpose |
|---|---|
| Fields | Store object data |
| Constructors | Initialize new objects |
| Methods | Define object behaviour |
| Properties | Control access to data |
| Static members | Belong to the class rather than an individual object |
| Access modifiers | Control visibility |
| Invariants | Define conditions that must remain valid |

### 2.2 Object

An object is a runtime instance of a class.

For example, two objects created from `SavingsAccount` may have different:

- Account identifiers
- Owners
- Balances
- Interest rates
- Transaction histories

They share the same class definition but maintain independent state.

### 2.3 Class versus object

| Characteristic | Class | Object |
|---|---|---|
| Meaning | Blueprint | Instance |
| Definition | Programmer-defined | Created at runtime |
| State | Defines available fields | Stores actual values |
| Behaviour | Defines methods | Executes methods |
| Identity | Class identity | Object identity |
| Multiplicity | One definition can produce many objects | Each instance has its own identity |

The distinction is important because changing one object's balance should not automatically change another object's balance.

## 3. Creating Classes in Different Languages

### 3.1 Python

Python uses the `class` keyword to define classes.

The implementation demonstrates:

- Constructors through `__init__`.
- Instance attributes through `self`.
- Encapsulation using underscore-prefixed attributes.
- Controlled access through `@property`.
- Class variables through `ClassVar`.
- Class methods through `@classmethod`.
- Static methods through `@staticmethod`.
- Inheritance through subclass declarations.
- Abstract classes through `ABC`.
- Abstract methods through `@abstractmethod`.
- Object representations through `__str__` and `__repr__`.
- Data structures through dictionaries, lists, and tuples.
- Structured records through dataclasses.
- Enumerations through `Enum`.

The `Account` class defines shared account behaviour. `SavingsAccount` and `CurrentAccount` specialize that behaviour.

The abstract `available_balance()` method requires every concrete account type to provide its own implementation.

The `Bank` dataclass demonstrates composition: a bank maintains a collection of account objects.

### 3.2 JavaScript

JavaScript uses the `class` keyword and supports constructor methods, inheritance, static members, and private fields.

The implementation uses:

- `constructor()` for initialization.
- `extends` for inheritance.
- `super()` for parent-class initialization.
- `#` private fields for encapsulation.
- Getters for controlled access.
- Static methods and properties.
- `Map` for account registration.
- `EventEmitter` for event-driven behaviour.
- Promises and asynchronous file operations.
- `Object.freeze()` for immutable exposed records.
- UUIDs for object identification.

The `Bank` class extends `EventEmitter`. It publishes account creation and transfer events.

This separates account operations from event consumers. Reporting or monitoring components can respond to events without being embedded inside account classes.

The transfer method validates both accounts before modifying balances. Its rollback logic demonstrates failure recovery for an in-memory operation. A production banking system requires durable database transactions rather than relying on in-memory rollback.

### 3.3 C++17

C++ uses class definitions with explicit access control.

The implementation demonstrates:

- `class` and `struct`.
- Constructors and destructors.
- Private and public members.
- Protected methods.
- Static members.
- Constant object identifiers.
- Abstract base classes.
- Virtual functions.
- Function overriding.
- Runtime polymorphism.
- Smart pointers.
- STL containers.
- Exceptions.
- Deleted copy operations.

The `Account` class defines an abstract interface.

The `SavingsAccount` and `CurrentAccount` classes implement the required virtual methods.

The `Bank` class uses `std::map` for indexed account lookup and `std::unique_ptr` for exclusive ownership.

Smart pointers reduce the risk of memory leaks by automatically managing object lifetime.

Deleting copy operations prevents accidental copying of account objects that have unique identities.

### 3.4 Java 17

Java provides a class-oriented type system suitable for enterprise applications.

The implementation demonstrates:

- Classes and constructors.
- Interfaces.
- Abstract classes.
- Records.
- Enums.
- Inheritance.
- Method overriding.
- Encapsulation.
- Generics.
- Collections.
- Streams.
- Immutable collection views.
- Custom exceptions.
- Atomic identifiers.
- Synchronized operations.
- Service and repository separation.

The `Account` class defines the shared domain model.

The `AccountOperations` interface specifies available operations, while `Auditable` defines transaction-history access.

The `AccountRepository` class uses generics to maintain strongly typed account collections.

The `TransferService` separates business operations from persistence.

The `ReportingService` performs collection processing using Java Streams.

Java records provide immutable transaction data structures without requiring manually written accessor methods.

## 4. Constructors and Object Initialization

A constructor initializes an object when it is created.

A constructor generally establishes:

- Required values
- Default values
- Initial state
- Object identity
- Validity constraints

An object should not become available to other components in an invalid state.

The banking implementations validate the owner and opening balance during construction.

For example, an account must not be initialized with:

- An empty owner name
- A negative opening balance
- An infinite monetary value
- An invalid configuration

### Constructor responsibilities

A well-designed constructor should:

1. Validate mandatory inputs.
2. Initialize all required fields.
3. Establish valid defaults.
4. Protect object invariants.
5. Avoid unnecessary external operations.

Complex operations such as database communication and report generation should generally remain outside constructors.

## 5. Encapsulation and Access Control

Encapsulation combines object data and its permitted operations.

It prevents arbitrary external modification of internal state.

Consider an account balance.

Directly assigning a new balance from unrelated application code could bypass business rules.

A safer design keeps the balance private and exposes controlled operations.

The implementations use:

| Language | Encapsulation mechanism |
|---|---|
| Python | Naming conventions, properties and controlled methods |
| JavaScript | Private fields using `#` |
| C++ | `private`, `protected`, and `public` |
| Java | Access modifiers and private fields |

The account balance can be read through a getter, while changes must pass through `deposit()` or `withdraw()`.

This makes it possible to enforce validation consistently.

### Object invariants

An invariant is a condition that must remain true throughout an object's valid lifetime.

Examples include:

- Account balance cannot be negative for an account without overdraft.
- A closed account cannot accept transactions.
- A frozen account cannot perform normal transactions.
- A savings account must preserve its minimum balance.
- An interest rate must remain within its permitted range.

Encapsulation allows these rules to be enforced at the object boundary.

## 6. Instance Members, Class Members and Static Members

### 6.1 Instance members

Instance members belong to individual objects.

For example, every account has its own:

- Owner
- Balance
- Status
- Transaction history

Two accounts can therefore have different values for the same fields.

### 6.2 Class members

Class members belong to the class rather than a particular object.

Examples include:

- Number of registered objects.
- Shared configuration.
- Class-wide counters.
- Common utility operations.

Python demonstrates class variables and class methods.

C++ demonstrates static members.

JavaScript demonstrates static getters.

### 6.3 Static methods

Static methods do not require an individual object to perform their operation.

Amount validation is an appropriate example because it can be performed independently of a particular account.

Static methods should be used when the operation logically belongs to the class but does not depend on individual instance state.

## 7. Inheritance and Class Hierarchies

Inheritance allows one class to extend another class.

The banking implementation uses the following hierarchy:

    Account
       |
       +-------------------+
       |                   |
    SavingsAccount    CurrentAccount

`Account` contains common behaviour.

`SavingsAccount` introduces:

- Minimum balance
- Interest rate
- Interest calculation

`CurrentAccount` introduces:

- Overdraft limit
- Extended withdrawal availability

The subclasses reuse the common account implementation while adding their own business rules.

### Parent and child classes

| Term | Meaning |
|---|---|
| Parent class | Class whose behaviour is inherited |
| Child class | Class that inherits another class |
| Base class | General class defining common functionality |
| Derived class | Specialized class extending a base class |
| Superclass | Another term for parent class |
| Subclass | Another term for child class |

### Method overriding

Method overriding occurs when a subclass supplies its own implementation of an inherited method.

The two account subclasses implement `availableBalance()` differently.

For a savings account:

Available balance = Current balance - Minimum balance

For a current account:

Available balance = Current balance + Overdraft limit

The same method name therefore produces different behaviour depending on the object type.

## 8. Abstraction and Interfaces

Abstraction exposes essential behaviour while hiding implementation details.

An abstract class defines common operations and can require subclasses to implement specific methods.

An interface defines a contract that implementing classes must satisfy.

### Abstract classes

The banking `Account` class is abstract because a generic account does not define one universal withdrawal-availability policy.

Concrete account classes provide the required implementation.

### Interfaces

Java demonstrates `AccountOperations` and `Auditable`.

These interfaces separate capabilities from implementation.

A reporting service can depend on an auditing contract instead of depending on a specific account subclass.

This reduces coupling between application components.

## 9. Polymorphism

Polymorphism allows different object types to be used through a common interface.

For example, both savings and current accounts implement `availableBalance()`.

A collection of account references can invoke the same operation on different object types.

The runtime selects the appropriate overridden method.

This is useful when an application must support new account categories without rewriting every component that uses the common account interface.

Polymorphism is demonstrated through:

- Python abstract methods.
- JavaScript method overriding.
- C++ virtual functions.
- Java abstract methods and interfaces.

## 10. Composition and Object Relationships

Composition means that one object contains or manages other objects.

The `Bank` class maintains a collection of account instances.

    Bank
      |
      +-- Account 1001
      |
      +-- Account 1002
      |
      +-- Account 1003

The bank manages account registration, lookup, reporting, and transfers.

The account objects maintain their own state.

This separation avoids placing every responsibility inside one large class.

### Composition versus inheritance

| Characteristic | Inheritance | Composition |
|---|---|---|
| Relationship | Is-a | Has-a |
| Main purpose | Specialization | Collaboration |
| Reuse | Inherited behaviour | Delegated behaviour |
| Example | SavingsAccount is an Account | Bank has Accounts |
| Coupling | Parent-child relationship | Object dependency |

Inheritance should represent a genuine specialization relationship. Composition is often preferable when a class needs to use another object's functionality without becoming its subtype.

## 11. Object State and State Transitions

An object can move between defined states.

The account model uses three states:

| State | Meaning |
|---|---|
| ACTIVE | Normal operations permitted |
| FROZEN | Transactions restricted |
| CLOSED | Account permanently closed |

The intended transitions are:

    ACTIVE -> FROZEN
    FROZEN -> ACTIVE
    ACTIVE -> CLOSED
    FROZEN -> CLOSED: Not permitted

The implementations enforce the principal transition rules through methods.

A closed account cannot be reopened through the normal unfreeze operation.

A frozen account cannot deposit or withdraw.

A valid account closure requires a zero balance.

Explicit state management prevents arbitrary modifications from producing contradictory object behaviour.

## 12. Validation, Exceptions and Failure Handling

Class design must consider invalid input and invalid operations.

The implementations validate:

- Empty owner names.
- Negative amounts.
- Non-finite numbers.
- Invalid interest rates.
- Negative overdraft limits.
- Missing accounts.
- Duplicate account registration.
- Insufficient available balances.
- Invalid account states.
- Invalid transfer participants.

Exceptions communicate failure conditions to calling components.

A useful distinction exists between:

**Validation failures:** The supplied input violates a rule.

**State failures:** The object is not in a state that permits the requested operation.

**Operational failures:** An operation cannot complete because another component or operation failed.

Exception handling should not silently convert an unsuccessful transaction into a successful result.

For financial operations, durable transaction processing and reconciliation are essential.

## 13. Class Creation and Software Design Principles

The implementations illustrate several object-oriented design principles.

### Single Responsibility Principle

A class should have a focused responsibility.

The banking examples separate:

- Account state management.
- Bank-level account management.
- Transaction processing.
- Reporting.
- Repository operations.

### Open-Closed Principle

Software components should support extension without unnecessary modification to existing behaviour.

A new account subclass can implement the existing account abstraction.

### Liskov Substitution Principle

A subclass should remain usable wherever its parent type is expected without breaking the parent contract.

The account subclasses implement the same fundamental account operations while applying their own availability rules.

### Interface Segregation Principle

Interfaces should represent focused capabilities.

The Java implementation separates account operations from auditing.

### Dependency Inversion Principle

Higher-level services should depend on stable abstractions rather than unnecessary implementation details.

The Java service and repository structure demonstrates this separation.

These principles are design guidelines rather than automatic guarantees of good architecture.

## 14. Advanced Class Design Considerations

### 14.1 Immutability

An immutable object cannot have its state modified after construction.

The implementations use immutable transaction records or snapshots where appropriate.

Python uses a frozen dataclass.

Java uses records.

JavaScript exposes frozen transaction records.

C++ uses controlled access to transaction data.

Immutability is particularly useful for audit records and data transfer structures.

### 14.2 Object identity

Two objects can contain identical values but still represent different objects.

Object identity is important when tracking:

- Database records.
- Transactions.
- Registered entities.
- Resource ownership.
- Distributed application state.

The examples use identifiers to distinguish account instances.

### 14.3 Object lifecycle

An object typically progresses through:

    Construction
        |
    Initialization
        |
    Active use
        |
    State changes
        |
    Closure or disposal

In C++, object destruction and smart-pointer ownership are important lifecycle mechanisms.

In Java and Python, garbage collection manages memory reclamation, although application-level resource management remains necessary.

JavaScript also uses garbage collection, while asynchronous operations may continue beyond the lifetime of a particular calling function.

### 14.4 Thread safety

Shared objects require synchronization when multiple threads can modify their state concurrently.

The Java implementation synchronizes important account operations and uses concurrent collections for repository storage.

A production transfer should use an atomic database transaction and appropriate locking.

The Python and JavaScript implementations are demonstrations of domain behaviour, not distributed concurrency-control systems.

## 15. PostgreSQL: Relational Representation of Classes

Relational databases do not directly implement programming-language classes.

The PostgreSQL script represents class definitions and their associated objects using relational structures.

The model includes:

| Database object | Purpose |
|---|---|
| `class_definition` | Stores class definitions and parent relationships |
| `class_attribute` | Stores class fields and their data types |
| `class_method` | Stores method metadata |
| `object_instance` | Stores object instances |
| `object_attribute_value` | Stores individual object values |
| `object_audit` | Records object-related operations |

### 15.1 Class definitions

The `class_definition` table stores class identity, name, description, and parent class.

The `parent_class_id` foreign key represents inheritance.

### 15.2 Attributes

The `class_attribute` table records attribute names, types, visibility, mandatory status, and default values.

A unique constraint prevents duplicate attribute names within the same class.

### 15.3 Methods

The `class_method` table stores method metadata, including return type, access modifier, and static or abstract status.

It describes methods rather than executing programming-language method bodies.

### 15.4 Object instances

The `object_instance` table identifies individual instances of registered classes.

Each object references its corresponding class definition.

### 15.5 Attribute values

The `object_attribute_value` table stores actual object values separately from class metadata.

This is a metadata-driven relational design.

It allows different class definitions and instances to be represented without creating a separate physical database table for every programming-language class.

### 15.6 Triggers and procedures

The PostgreSQL implementation uses:

- Recursive CTEs for inheritance traversal.
- Triggers to prevent inheritance cycles.
- Triggers to validate attribute ownership.
- Type validation for attribute values.
- Abstract-class instantiation restrictions.
- Deferred constraints for required attributes.
- A procedure for creating objects.
- Views for class and object reporting.

The database demonstrates relational integrity enforcement rather than reproducing the complete runtime semantics of Python, JavaScript, C++, or Java.

## 16. Practical Execution

### Python

Save the first implementation as `main.py`.

Execute using Python 3:

`python main.py`

The script uses the Python standard library.

### JavaScript

Save the second implementation as `main.js`.

Execute using Node.js:

`node main.js`

The implementation uses built-in Node.js modules and does not require npm packages.

### C++17

Save the third implementation as `main.cpp`.

Compile:

`g++ -std=c++17 -Wall -Wextra -pedantic -O2 main.cpp -o classes`

Execute:

`./classes`

On Windows:

`classes.exe`

### Java 17

Save the fourth implementation as `Main.java`.

Compile:

`javac Main.java`

Execute:

`java Main`

### PostgreSQL

Save the fifth implementation as `classes.sql`.

Execute it against a PostgreSQL 15 or later database using:

`psql -U postgres -d postgres -f classes.sql`

The script creates the `class_lab` schema and its associated database objects.

The database user requires permission to create schemas, tables, functions, procedures, triggers, and types.

## 17. Complexity and Performance

Class design influences application performance through object creation, method calls, memory usage, collection selection, and data access patterns.

| Operation | Implementation | Typical complexity |
|---|---|---|
| Object construction | Constructor | O(1), excluding internal allocations |
| Field access | Getter | O(1) |
| Transaction append | Dynamic array or vector | Amortized O(1) |
| Python dictionary lookup | Dictionary | Average O(1) |
| JavaScript Map lookup | Map | Average sublinear, typically O(1) |
| C++ map lookup | `std::map` | O(log n) |
| Java concurrent map lookup | ConcurrentHashMap | Typically O(1) |
| Account report | Collection traversal | O(n) |
| In-memory transfer | Account lookup and update | Depends on collection lookup |

The PostgreSQL implementation uses indexes on class relationships, object states, attribute lookups, and audit timestamps.

These indexes improve common retrieval operations but introduce storage and write-maintenance costs.

## 18. Security Considerations

Class encapsulation improves the control of application state but does not independently guarantee security.

Important considerations include:

- Validate all externally supplied values.
- Restrict direct access to internal fields.
- Avoid exposing sensitive object properties in reports.
- Enforce authorization independently of object state.
- Record important state changes in audit logs.
- Protect database credentials.
- Use parameterized SQL for externally supplied data.
- Use database transactions for multi-record changes.
- Apply least-privilege database permissions.
- Avoid logging passwords, authentication tokens, or sensitive personal data.
- Use appropriate synchronization for shared mutable state.

The SQL implementation uses constraints, foreign keys, triggers, and database functions to enforce selected integrity rules.

Production deployments should also define appropriate roles and privileges.

## 19. Limitations and Design Trade-offs

The examples are educational domain implementations rather than complete banking systems.

Important limitations include:

- Monetary values use floating-point numbers in the programming-language examples. Production financial systems should use decimal arithmetic or integer minor currency units.
- The in-memory implementations do not provide durable transaction processing.
- The JavaScript transfer rollback is not equivalent to an ACID database transaction.
- The C++ example assumes single-threaded execution.
- The Java synchronization strategy does not replace distributed locking.
- PostgreSQL stores method metadata rather than executable class methods.
- The relational metadata design does not implement full programming-language inheritance semantics.
- Audit records require additional retention and access-control policies in production.

These distinctions matter because object-oriented modelling, relational modelling, transaction management, and application security solve different problems.

## 20. Key Terminology

| Term | Definition |
|---|---|
| Class | Blueprint defining object structure and behaviour |
| Object | Runtime instance of a class |
| Instance | Individual realization of a class |
| Attribute | Data member belonging to an object or class |
| Method | Operation defined inside a class |
| Constructor | Initialization mechanism |
| Destructor | Object destruction mechanism in languages that support it |
| Encapsulation | Controlled access to object state |
| Abstraction | Exposure of essential behaviour |
| Inheritance | Extension of an existing class |
| Polymorphism | Common interface with different implementations |
| Composition | Building objects using other objects |
| Overriding | Replacing inherited method behaviour |
| Overloading | Defining multiple compatible method signatures |
| Interface | Contract specifying supported operations |
| Abstract class | Class that cannot be directly instantiated |
| Static member | Member associated with the class |
| Instance member | Member associated with an individual object |
| Invariant | Condition that must remain valid |
| Immutability | Property of data that cannot be modified after construction |
| Object lifecycle | Sequence of object creation, usage, and termination |
| Association | Relationship between independent objects |
| Aggregation | Whole-part relationship with independent component lifetimes |
| Access modifier | Mechanism controlling member visibility |

## 21. Educational Outcomes

The five implementations provide practical exposure to:

- Creating classes and constructing objects.
- Defining fields, methods, and constructors.
- Managing instance and class-level data.
- Implementing encapsulation.
- Applying inheritance and abstraction.
- Using interfaces and abstract methods.
- Implementing runtime polymorphism.
- Designing object relationships.
- Managing object state transitions.
- Validating object construction and operations.
- Handling exceptions and operational failures.
- Working with immutable records.
- Applying object-oriented design principles.
- Representing class metadata in a relational database.
- Enforcing data integrity using PostgreSQL constraints and triggers.

The central design principle is that a class should define a coherent responsibility, maintain valid internal state, and expose operations through a controlled interface.
