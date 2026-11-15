# Introduction to Classes and Objects

## 1. Introduction

Object-oriented programming (OOP) is a programming approach in which software is organized around objects that combine data and behavior.

An object represents an entity with:

- Identity: What distinguishes it from other objects.
- State: The information stored in the object.
- Behavior: The operations that the object can perform.

A class defines the structure and behavior that its objects share. An object is an individual instance created from that class.

For example, a `BankAccount` class describes the properties and operations of bank accounts. Two objects created from that class can represent different customers with independent account numbers, balances, and transaction histories.

### Class and object relationship

    Class: BankAccount
           |
           | Object creation
           |
           +----------------------+
           |                      |
           v                      v
       Account A              Account B
       Owner: Aarav            Owner: Meera
       Balance: 5000           Balance: 8000
       Status: Active          Status: Frozen

Both objects follow the same class definition but maintain independent states.

## 2. Fundamental terminology

| Term | Meaning |
|---|---|
| Class | Definition of object attributes and methods |
| Object | Instance of a class |
| Attribute | Data associated with an object |
| Method | Function defined inside a class |
| Constructor | Initialization mechanism executed during object creation |
| Instance | An individual object created from a class |
| Instance variable | Data belonging to a particular object |
| Class variable | Data shared at the class level |
| Instance method | Operation performed using an object |
| Static method | Utility operation that does not require object state |
| Class method | Operation that receives the class as its first argument in Python |
| Encapsulation | Restricting direct access to internal object state |
| Abstraction | Exposing essential operations while hiding implementation details |
| Inheritance | Creating specialized classes from existing classes |
| Polymorphism | Providing different implementations through a common interface |
| Composition | Building complex objects using other objects |

## 3. Classes and object creation

A class defines the structure of an object.

Its definition normally includes:

- Attributes describing its state.
- Constructors initializing its state.
- Methods implementing its behavior.
- Validation rules protecting its integrity.

Object creation allocates an individual instance and initializes its attributes.

For example, the Python implementation defines `BankAccount`. Creating two accounts produces two independent objects.

The account number, balance, transaction history, and status belong to individual instances.

The Java implementation follows a similar domain model through an enterprise order-processing system. Its `Product`, `Customer`, and `Order` classes represent separate business entities.

## 4. Constructors and initialization

A constructor establishes a valid initial object state.

| Language | Constructor mechanism |
|---|---|
| Python | `__init__()` |
| JavaScript | `constructor()` |
| C++ | Constructor with the class name |
| Java | Constructor with the class name |

A constructor should validate essential information before the object becomes available for normal operations.

Examples include:

- Rejecting empty customer names.
- Rejecting negative account balances.
- Rejecting invalid product prices.
- Rejecting negative vehicle mileage.
- Rejecting invalid object relationships.

Constructor validation reduces the possibility of objects entering inconsistent states.

## 5. Attributes, methods, and object state

Attributes store information associated with an object.

Methods define operations that use or modify that information.

Consider a bank account:

| Attribute | Example |
|---|---|
| Account number | 1001 |
| Owner | Aarav Sharma |
| Balance | 10000.00 |
| Status | ACTIVE |

Its methods include:

- `deposit()`
- `withdraw()`
- `freeze()`
- `unfreeze()`
- `close()`
- `calculate_interest()`

The distinction between attributes and methods is important: attributes describe what an object knows, while methods describe what it does.

Object state can change during execution. For example, a vehicle can move from `AVAILABLE` to `IN_USE` and subsequently return to `AVAILABLE`.

## 6. Encapsulation

Encapsulation combines data and operations while controlling access to internal state.

Without encapsulation, external code could directly modify sensitive attributes.

For example, unrestricted access to a bank account balance could allow an application to assign an arbitrary value without recording a transaction.

The Python implementation uses `_balance` and exposes a read-only `balance` property.

The JavaScript implementation uses private fields such as `#status`.

The C++ implementation uses private data members and public methods.

The Java implementation uses private attributes with controlled accessors.

The PostgreSQL implementation uses constraints and database functions to protect stored information.

### Practical benefits

- Prevents uncontrolled modifications.
- Centralizes validation.
- Maintains object consistency.
- Makes debugging easier.
- Reduces unintended dependencies between components.

Encapsulation does not automatically provide complete application security. Authentication, authorization, access control, and secure interfaces remain necessary.

## 7. Abstraction

Abstraction exposes the operations necessary to use an object without requiring users to understand its internal implementation.

The C++ implementation defines an abstract `Vehicle` class.

Every concrete vehicle must implement:

- `operatingCost()`
- `category()`

The caller can calculate operating costs through a common interface without knowing whether the underlying object represents a car or a truck.

Java provides abstraction through abstract classes and interfaces.

An interface specifies a behavioral contract, while an abstract class can also provide shared state and implementation.

Abstraction helps separate what an object does from how it performs that operation.

## 8. Inheritance

Inheritance allows one class to extend another class.

The original class is called the base class or parent class. The specialized class is called the derived class or child class.

The implementations demonstrate inheritance through different domain models.

### Python

    BankAccount
       |
       +-- SavingsAccount
       |
       +-- CurrentAccount

`SavingsAccount` introduces an interest rate and minimum balance.

`CurrentAccount` introduces an overdraft limit.

Both reuse the fundamental account behavior.

### JavaScript

    Task
       |
       +-- UrgentTask

The specialized task assigns the highest priority and exposes its category.

### C++

    Vehicle
       |
       +-- Car
       |
       +-- Truck

The derived classes implement different operating-cost and category behaviors.

### Java

    Product
       |
       +-- PhysicalProduct
       |
       +-- DigitalProduct

Physical products have a weight, whereas digital products have a download format.

### Important distinction

Inheritance should represent a genuine specialization relationship.

A truck is a type of vehicle. A digital product is a type of product.

Unrelated objects should not be connected through inheritance merely to reuse code. Composition is often more appropriate for combining independent responsibilities.

## 9. Polymorphism

Polymorphism allows different objects to respond to a common operation according to their individual implementations.

For example, the C++ fleet program stores both cars and trucks using pointers to the abstract `Vehicle` class.

Calling `operatingCost()` invokes the implementation belonging to the actual object.

This is runtime polymorphism.

The Python implementation demonstrates method overriding through `calculate_interest()` and `withdraw()`.

The Java implementation demonstrates polymorphism through the `DiscountPolicy` interface.

The caller depends on the interface rather than a specific discount implementation.

### Polymorphism comparison

| Concept | Description |
|---|---|
| Method overriding | A derived class replaces inherited behavior |
| Runtime polymorphism | The implementation is selected according to the actual object type |
| Interface-based polymorphism | Different classes implement a shared contract |
| Compile-time polymorphism | Behavior is selected during compilation, such as through C++ function overloading |

Polymorphism reduces dependency on concrete implementation classes and supports extensible designs.

## 10. Composition

Composition builds a larger object from smaller independent objects.

Unlike inheritance, composition does not establish an is-a relationship.

Examples implemented in the source files include:

| Container object | Component objects |
|---|---|
| Bank | Bank accounts |
| Project | Users and tasks |
| Fleet | Vehicles |
| Order | Customer, order items, and discount policy |
| Library loan | Member and book relationships |

The C++ fleet uses `std::unique_ptr` to establish clear ownership of vehicle objects.

The JavaScript project maintains task and user objects using `Map` collections.

The Python bank maintains account objects in a dictionary.

Composition encourages modularity and makes responsibilities easier to test independently.

## 11. Static methods, class methods, and instance methods

These methods differ in the information available to them.

| Method type | Python | Purpose |
|---|---|---|
| Instance method | `self` | Accesses an individual object's state |
| Class method | `cls` | Operates on class-level information |
| Static method | No automatic receiver | Performs a utility operation |

The Python implementation uses:

- `total_accounts()` as a class method.
- `_validate_amount()` as a static method.
- `deposit()` as an instance method.

JavaScript demonstrates static class fields for managing generated identifiers.

## 12. Object identity and equality

Two objects may contain identical attributes while remaining separate objects.

Consider two customer objects with the same name and address.

They can still represent different customer records.

Three concepts should be distinguished:

- Identity: Whether two references represent the same object.
- Equality: Whether two objects have equivalent values according to a defined comparison.
- Uniqueness: Whether an identifier distinguishes an object within a specified domain.

Java records automatically provide value-based `equals()` and `hashCode()` implementations.

The PostgreSQL schema uses primary keys to establish persistent entity identity.

The JavaScript implementation uses UUIDs for task identifiers.

The C++ implementation assigns unique vehicle identifiers.

## 13. Object lifecycle and state management

Objects are created, used, modified, and eventually destroyed or become unreachable.

A typical lifecycle is:

    Definition
        |
        v
    Construction
        |
        v
    Initialization
        |
        v
    Normal Operations
        |
        v
    State Transitions
        |
        v
    Cleanup / Destruction

Different languages manage object lifecycles differently.

| Language | Memory and lifecycle mechanism |
|---|---|
| Python | Reference counting and garbage collection |
| JavaScript | Automatic garbage collection |
| C++ | Deterministic object lifetime and RAII |
| Java | Garbage collection |

The C++ implementation uses smart pointers to manage dynamically allocated vehicle objects.

The Java implementation models business lifecycle separately from memory management. An order may be delivered or cancelled while its Java object remains in memory.

These are different concepts: business object state is not the same as memory lifecycle.

## 14. State transitions and validation

A state transition defines which changes are permitted for an object.

For example, an order follows this workflow:

    CREATED
       |
       v
    CONFIRMED
       |
       v
    PROCESSING
       |
       v
    SHIPPED
       |
       v
    DELIVERED

Cancellation is permitted only at specific stages.

An already delivered order cannot be cancelled through the implemented transition rules.

The JavaScript task model similarly restricts transitions between `TODO`, `IN_PROGRESS`, `COMPLETED`, and `CANCELLED`.

The C++ vehicle model prevents an assigned vehicle from entering maintenance.

The Python bank account prevents financial operations when an account is frozen or closed.

The PostgreSQL implementation enforces borrowing rules through constraints, triggers, and functions.

Centralized state-transition logic is preferable to allowing arbitrary modifications of status attributes.

## 15. Implementation analysis

### Python: Bank account management

The Python implementation emphasizes object modeling and encapsulation.

Its main mechanisms are:

- `BankAccount` as a reusable base class.
- `SavingsAccount` and `CurrentAccount` as specialized classes.
- `Transaction` as an immutable dataclass.
- `AccountStatus` as an enumeration.
- `Bank` as a composition-based container.
- `Decimal` for monetary calculations.
- Exceptions for invalid transactions.
- JSON serialization for reporting.

The bank transfer operation validates both accounts before changing balances. It also includes rollback handling for a failed destination deposit.

The demonstration includes insufficient funds, minimum-balance violations, frozen accounts, overdraft limits, and invalid monetary values.

### JavaScript: Event-driven project management

The JavaScript implementation uses an event-driven design.

Its main mechanisms are:

- `User` for identity and membership.
- `Task` for task state.
- `UrgentTask` for specialized behavior.
- `Project` for object composition.
- `EventEmitter` for notifications.
- `Map` for object lookup.
- `Set` for valid state transitions.
- `async` and `await` for asynchronous operations.
- Private class fields for encapsulation.

The project emits events when members are added, tasks are created, and tasks change state.

The implementation uses Node.js built-in modules without third-party packages.

### C++17: Fleet management

The C++ implementation emphasizes type relationships, ownership, and runtime polymorphism.

Its main mechanisms are:

- Abstract `Vehicle` class.
- Derived `Car` and `Truck` classes.
- Virtual methods.
- Private data members.
- `std::unique_ptr` for exclusive ownership.
- `std::unordered_map` for average constant-time lookup.
- `std::vector` for result collections.
- STL algorithms for reporting and sorting.
- Exceptions for invalid operations.

The virtual destructor ensures correct destruction through base-class pointers.

The program uses no external libraries.

### Java 17: Enterprise order processing

The Java implementation emphasizes enterprise domain modeling.

Its main mechanisms are:

- `Product` as an abstract class.
- `PhysicalProduct` and `DigitalProduct` as specialized classes.
- `DiscountPolicy` as an interface.
- `StandardDiscount` as a policy implementation.
- Records for immutable address and event data.
- Generic `Inventory<T>` for type-safe storage.
- `OrderItem` for product and quantity relationships.
- `Order` for order lifecycle management.
- `OrderService` for application-level operations.

`BigDecimal` provides more appropriate monetary precision than floating-point arithmetic.

Immutable collections reduce accidental modification of order contents.

Streams provide filtering, grouping, and aggregation.

### PostgreSQL: Relational object model

The PostgreSQL implementation represents a library lending system.

Its primary entities are:

- Members
- Books
- Borrowing policies
- Loans

A primary key identifies each stored entity. Foreign keys establish relationships between entities.

Enums restrict object states to defined values.

Constraints validate individual attributes and relationships.

Triggers maintain consistency between loan state and book availability.

Functions provide controlled borrowing and returning operations.

Views simplify reporting and retrieval.

CTEs organize aggregation queries.

Indexes support common lookup and reporting patterns.

The database demonstrates relational persistence rather than in-memory object inheritance. Membership-specific behavior is represented through borrowing-policy records rather than subclass tables.

## 16. Database representation of objects

An in-memory object and a database record are related concepts, but they are not identical.

| Object-oriented concept | Relational equivalent |
|---|---|
| Object identity | Primary key |
| Object attribute | Column |
| Object collection | Table |
| Object relationship | Foreign key |
| Object validation | Check constraint |
| Object lifecycle | State column and controlled operations |
| Object operation | Function or stored procedure |
| Object collection retrieval | SQL query |
| Object integrity | Constraints and triggers |

A database record represents persisted state.

An application object represents state and behavior during program execution.

The application can load database records into objects, modify those objects, and persist validated changes back to the database.

## 17. Error handling and failure conditions

Robust object-oriented systems must account for invalid input, illegal operations, and unexpected failures.

| Failure condition | Implemented handling |
|---|---|
| Empty object name | Constructor validation |
| Negative monetary amount | Numeric validation |
| Insufficient funds | Custom exception |
| Invalid account state | State validation |
| Duplicate project member | Collection-level uniqueness check |
| Invalid task transition | Domain exception |
| Missing vehicle | Exception-based lookup |
| Negative vehicle mileage | Attribute validation |
| Invalid product price | Constructor validation |
| Invalid order transition | Custom state exception |
| Duplicate active book loan | Unique partial index |
| Ineligible library member | Database trigger |
| Borrowing limit exceeded | Database function and trigger |

Errors should be handled at appropriate boundaries.

A validation failure should not silently produce an inconsistent object or database record.

## 18. Performance and scalability

The implementations make different data-structure and storage decisions.

| Implementation | Data structure | Expected performance |
|---|---|---|
| Python bank | Dictionary | Average O(1) account lookup |
| JavaScript project | Map | Average O(1) task lookup |
| JavaScript project | Set | Average O(1) membership checks |
| C++ fleet | Unordered map | Average O(1) vehicle lookup |
| C++ fleet | Vector | O(n) filtering and O(n log n) sorting |
| Java inventory | HashMap | Average O(1) product lookup |
| Java order | Immutable list | O(n) item aggregation |
| PostgreSQL | B-tree indexes | Efficient indexed retrieval |

Actual database performance depends on table size, selectivity, query plans, and workload characteristics.

For large applications, additional concerns include:

- Transaction boundaries.
- Concurrent updates.
- Database connection management.
- Object serialization costs.
- Memory consumption.
- Logging overhead.
- Cache consistency.
- Input validation at external boundaries.

## 19. Security considerations

Object-oriented design does not independently guarantee application security.

Important controls include:

- Restricting access to sensitive attributes.
- Validating all external inputs.
- Enforcing authorization before sensitive operations.
- Avoiding exposure of internal object representations.
- Protecting database credentials.
- Using parameterized SQL in application code.
- Enforcing database permissions.
- Recording security-relevant state changes.
- Avoiding unrestricted object deserialization.
- Preventing unauthorized state transitions.

The SQL functions in this implementation demonstrate controlled business operations, but production deployment must also configure suitable database roles, ownership, and execution privileges.

The sample systems are educational domain models rather than complete production banking, fleet, commerce, or library platforms.

## 20. Execution requirements

| Deliverable | Runtime | Dependencies |
|---|---|---|
| Python | Python 3.10+ | Standard library |
| JavaScript | Node.js 18+ | Node.js standard library |
| C++ | C++17 compiler | Standard library |
| Java | Java 17 | JDK standard library |
| PostgreSQL | PostgreSQL 14+ | PostgreSQL server |

### Python

The script can be executed directly using Python. It includes demonstration operations and assertions.

### JavaScript

Run the file using Node.js. The program demonstrates events, task transitions, asynchronous execution, and object serialization.

### C++17

Compile with a C++17-compatible compiler. The implementation uses standard library containers, smart pointers, exceptions, and virtual functions.

### Java 17

The source file is named `Main.java` because its public class is `Main`.

Compile and execute it using the Java 17 compiler and runtime.

### PostgreSQL

Execute the SQL script using a PostgreSQL client with permission to create schemas, types, tables, functions, and triggers.

The script creates the `object_learning` schema and populates it with sample records. It is designed as an executable demonstration and should be run in an isolated learning database.

## 21. Learning outcomes

The five implementations demonstrate how the same fundamental object-oriented principles can support different software architectures.

- Python demonstrates encapsulated business objects and controlled financial operations.
- JavaScript demonstrates event-driven objects and asynchronous project management.
- C++17 demonstrates abstract classes, runtime polymorphism, and deterministic resource ownership.
- Java 17 demonstrates enterprise domain modeling, interfaces, records, generics, and business-state transitions.
- PostgreSQL demonstrates persistent entities, relational relationships, integrity enforcement, and controlled database operations.

The central design principle is that an object should maintain a valid state, expose meaningful behavior, and interact with other objects through clearly defined relationships and interfaces.
