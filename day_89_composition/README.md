# Composition in Python

## 1. Introduction

Composition is an object-oriented programming principle in which a complex object is constructed from smaller, independent objects.

An object uses other objects as its internal components rather than implementing every responsibility itself.

Composition represents a **HAS-A relationship**.

Examples:

- A car has an engine and a transmission.
- A computer has a processor, memory, and storage.
- An order has a customer and multiple order items.
- A document-processing application has validators, storage, and notification services.
- A building-management system has multiple smart devices.

The central principle is separation of responsibilities. Each component performs a specific function, while a larger object coordinates those functions.

## 2. Composition and Inheritance

Composition and inheritance are different approaches to structuring object-oriented software.

| Property | Composition | Inheritance |
|---|---|---|
| Relationship | HAS-A | IS-A |
| Structure | Objects contain other objects | Classes extend other classes |
| Reuse | Reuses independent components | Reuses parent-class behavior |
| Coupling | Usually lower | Can be higher |
| Flexibility | Dependencies can be replaced | Class hierarchy is generally fixed |
| Runtime configuration | Supports dependency replacement | Usually requires a different subtype |
| Testing | Components can be tested independently | Parent and child behavior may be coupled |

For example:

- A `Car` has an `Engine`: composition.
- An `ElectricCar` is a type of `Car`: inheritance.

Composition is useful when an application combines several independent responsibilities. Inheritance is appropriate when a genuine subtype relationship exists.

## 3. Fundamental Composition in Python

### 3.1 Creating independent classes

A component should have a clearly defined responsibility.

The Python implementation defines:

- `Engine`: manages engine operations.
- `Transmission`: manages gear selection.
- `Car`: coordinates both components.

The `Car` object receives an engine and a transmission through its constructor.

Its methods delegate operations to these objects.

For example, `Car.start()` calls `Engine.start()`, while `Car.drive()` delegates gear selection to `Transmission`.

The car does not need to reproduce the internal implementation of either component.

### 3.2 Object references

Composition commonly uses instance attributes to maintain references to component objects.

The following conceptual relationship describes the implementation:

Car
|
|-- Engine
|
|-- Transmission

The component objects retain their own attributes and behavior.

Python does not automatically enforce exclusive ownership or destroy components when their containing object is destroyed. Object lifetime is governed by references and garbage collection.

Consequently, composition and object ownership are related but distinct concepts.

### 3.3 Nested composition

Composition can be hierarchical.

An `Order` contains:

- A `Customer`.
- A collection of `OrderItem` objects.

A `Customer` contains an `Address`.

Each order item references a `Product`.

The resulting structure is:

Order
|
|-- Customer
|   |
|   |-- Address
|
|-- OrderItem
|   |
|   |-- Product
|
|-- OrderItem
    |
    |-- Product

This structure allows individual domain objects to remain independent while supporting more complex business operations.

## 4. Dependency Injection

Dependency injection is a technique for supplying an object with the components it requires.

Instead of constructing a storage implementation internally, a repository receives a storage object through its constructor.

The Python implementation uses the `Storage` protocol.

Two implementations satisfy this interface:

| Implementation | Responsibility |
|---|---|
| `MemoryStorage` | Stores records in memory |
| `FileStorage` | Stores records in JSON files |

`UserRepository` depends on the storage interface rather than a particular implementation.

This provides several benefits:

- Storage implementations can be exchanged.
- Components can be tested independently.
- Business logic does not depend on storage details.
- Application configuration becomes more flexible.

Dependency injection is particularly useful in large applications where databases, APIs, messaging systems, and external services may change independently.

## 5. Interfaces and Protocols

Python supports structural typing through `Protocol`.

A protocol specifies the operations an object must provide without requiring it to inherit from a particular base class.

For example, a storage component must implement:

- `save(key, value)`
- `load(key)`

An object satisfying these operations can be used by `UserRepository`.

Python also supports abstract base classes through `ABC` and `abstractmethod`.

The notification implementation uses an abstract `NotificationChannel`.

Its concrete implementations are:

- `EmailChannel`
- `SMSChannel`

`NotificationService` delegates notification delivery to its injected channel.

This design separates notification coordination from delivery mechanisms.

## 6. Composition Using Dataclasses

The Python implementation uses `dataclasses` for structured domain objects.

The principal classes are:

- `Address`
- `Customer`
- `Product`
- `OrderItem`
- `Order`

A dataclass automatically provides useful object features, including generated initialization and representation methods.

The `field(default_factory=list)` declaration gives each order an independent item collection.

This avoids sharing a mutable list between different order instances.

The `__post_init__()` method validates values immediately after object construction.

For example:

- Product prices cannot be negative.
- Order quantities must be positive.
- Address fields cannot be empty.

Dataclasses reduce repetitive class code while retaining normal object composition.

## 7. Delegation

Delegation occurs when an object forwards an operation to one of its components.

In the example:

`Car.start()` delegates to `Engine.start()`.

`NotificationService.notify()` delegates to the configured notification channel.

`OrderApplication.process()` coordinates inventory, payment, and notification services.

Delegation prevents large classes from accumulating unrelated implementation details.

It also makes individual components easier to replace and maintain.

## 8. Advanced Application Composition

The Python implementation includes an order-processing application composed of three services.

| Component | Responsibility |
|---|---|
| `Inventory` | Tracks available products and reserves stock |
| `PaymentProcessor` | Processes payment requests |
| `NotificationService` | Communicates order outcomes |

The application follows this workflow:

1. Validate the order.
2. Check that the order contains items.
3. Reserve inventory.
4. Process payment.
5. Send a notification.
6. Return the processing result.

If inventory reservation or payment processing fails before payment completion, previously reserved inventory is released.

This is an example of compensating operations.

A production payment system requires stronger guarantees, including payment idempotency, durable transaction records, retry policies, and reconciliation.

Releasing inventory alone cannot reverse an external payment that has already succeeded.

## 9. JavaScript Composition

The JavaScript implementation provides a complementary event-driven architecture.

### 9.1 Component factories

JavaScript functions can construct objects that expose a controlled set of operations.

The implementation includes:

- `createLogger()`
- `createCache()`
- `createRepository()`
- `createAccessPolicy()`

These factories encapsulate internal state and return public interfaces.

The cache uses a `Map`, providing efficient key-based lookup and insertion.

The repository combines caching and record management without exposing its internal collections.

### 9.2 Event-driven composition

The `EventBus` composes independent event subscribers.

A component subscribes to a named event and receives notifications when that event is published.

The event bus uses:

- `Map` to organize event subscriptions.
- `Set` to prevent duplicate callback registration.
- `Promise.allSettled()` to collect subscriber outcomes independently.

A failed subscriber does not prevent other subscribers from receiving the event.

This design is useful in applications involving notifications, audit events, background tasks, and loosely coupled services.

### 9.3 Asynchronous composition

The JavaScript order-processing example uses asynchronous methods.

`OrderService` coordinates:

- `InventoryService`
- `PaymentService`
- `EventBus`
- Logger

The service uses `async` and `await` to express the workflow.

`structuredClone()` provides defensive copies of supported structured data, preventing external callers from directly modifying stored records or event payloads.

The example uses in-memory components and does not implement durable distributed transactions.

## 10. C++17 Composition

The C++17 implementation models an enterprise smart-building system.

The hierarchy is:

Building
|
|-- SmartDevice
    |
    |-- HVACController
        |
        |-- TemperatureSensor
        |
        |-- Actuator

The implementation emphasizes object lifetime, ownership, and memory management.

### 10.1 Unique ownership

`std::unique_ptr` represents exclusive ownership.

An `HVACController` owns its sensor and actuator.

A `SmartDevice` owns its controller.

A `Building` owns its smart devices.

When an owning object is destroyed, its uniquely owned components are automatically destroyed.

This follows the RAII principle: resource acquisition and release are tied to object lifetime.

### 10.2 Shared ownership

`std::shared_ptr` is used for the logger and notification interface.

Several objects can share these components.

The shared component is destroyed when its final owning reference is released.

Reference counting introduces some overhead, so shared ownership should be used only when multiple owners genuinely exist.

### 10.3 Interface-based composition

`INotification` defines a common notification contract.

`ConsoleNotification` implements the contract.

`AlertService` receives a shared notification interface.

This permits alternative notification implementations without changing the alert service.

### 10.4 Runtime validation

The smart-building example validates:

- Sensor readings.
- Humidity ranges.
- Device configuration.
- Missing dependencies.
- Duplicate device identifiers.
- Invalid device operations.
- Authorization permissions.

The program uses exceptions to report invalid states and operational failures.

The C++ implementation also demonstrates the distinction between composition and inheritance: inheritance supplies a common notification interface, while `AlertService` composes an implementation of that interface.

## 11. Java 17 Composition

The Java implementation models an enterprise document-processing platform.

Its architecture combines domain objects, validation services, storage, notification, authorization, and approval evaluation.

### 11.1 Records and immutable objects

Java records provide concise immutable data carriers.

The implementation defines:

- `Document`
- `ReviewDecision`
- `ReviewPolicy`

Records provide generated constructors, accessors, and value-based equality behavior.

Compact constructors validate record values.

This reduces the risk of invalid objects entering the application.

### 11.2 Composite validation

`CompositeValidator` contains multiple `DocumentValidator` implementations.

The two validators are:

- `ClassificationValidator`
- `ContentValidator`

The composite validator executes each validation component in sequence.

Each validator addresses a separate business constraint.

Additional validators can be introduced without changing the existing validation implementations.

### 11.3 State transitions

`DocumentWorkflow` maintains document lifecycle state.

The states are:

| State | Meaning |
|---|---|
| DRAFT | Document is being prepared |
| SUBMITTED | Document has been submitted |
| UNDER_REVIEW | Review is in progress |
| APPROVED | Required approvals have been obtained |
| REJECTED | Approval requirements have not been satisfied |

The workflow controls legal state transitions.

An invalid transition raises a `CompositionException`.

`AtomicReference` supports atomic state updates, while synchronized methods protect compound operations involving the review collection.

### 11.4 Approval evaluation

The `ApprovalEvaluator` composes a `ReviewPolicy`.

The policy specifies:

- Minimum approval count.
- Whether reviewers must be distinct.
- Whether negative decisions prevent approval.

Approval evaluation is separated from the document workflow.

This allows different approval policies to be introduced without rewriting the workflow's state-management logic.

### 11.5 Enterprise service composition

`DocumentApplication` coordinates independent services.

Its dependencies include:

- Document validation.
- Document storage.
- Notification delivery.
- Approval evaluation.
- Authorization.

The application service coordinates business operations, while individual components maintain their own responsibilities.

This structure supports independent testing and replacement of implementations.

## 12. PostgreSQL Composition

The SQL implementation models composition through a relational product-assembly system.

It uses a Bill of Materials (BOM) to represent how products are constructed from components and subassemblies.

### 12.1 Relational domain model

| Table | Responsibility |
|---|---|
| `suppliers` | Supplier information |
| `components` | Component catalog |
| `component_inventory` | Available and reserved inventory |
| `product_assemblies` | Product and subassembly definitions |
| `assembly_components` | Component relationships |
| `assembly_executions` | Assembly operations |
| `composition_audit` | Historical activity |

The `assembly_components` table supports two possible child types:

1. An ordinary component.
2. Another product assembly.

The `exactly_one_child` constraint ensures that an assembly relationship references exactly one type of child.

### 12.2 Bill of Materials

A Bill of Materials specifies the quantities of individual components required to produce a product.

For example:

Enterprise Workstation
|
|-- Processing Unit: 1
|
|-- Computer Chassis: 1
|
|-- Cooling Subassembly: 1
|   |
|   |-- Cooling Fan: 2
|
|-- Memory Subassembly: 1
    |
    |-- Memory Module: 2

This model demonstrates hierarchical composition in a relational database.

### 12.3 Recursive CTEs

A recursive Common Table Expression allows PostgreSQL to traverse nested assemblies.

The SQL implementation uses recursive queries for:

- Calculating total component requirements.
- Evaluating nested assembly costs.
- Generating assembly hierarchies.
- Detecting circular dependencies.

The recursive traversal maintains a path array to avoid repeatedly visiting an assembly already present in the current traversal path.

The cycle-prevention trigger rejects relationships that would create circular composition.

The trigger handles individual insertions and updates, but concurrent modifications to the same assembly graph require additional transaction-level serialization or locking for complete cycle-prevention guarantees.

### 12.4 Inventory eligibility

An assembly is eligible for production only when all required components are available.

For nested assemblies, the required quantities are multiplied through each level.

For example, if one workstation requires:

- Two memory modules.
- Two cooling fans.

Producing five workstations requires:

- Ten memory modules.
- Ten cooling fans.

The `check_assembly_inventory()` function evaluates these requirements against available stock.

### 12.5 Transaction management

The `start_assembly()` procedure demonstrates inventory reservation.

The operation:

1. Checks assembly eligibility.
2. Locks the assembly.
3. Creates an execution record.
4. Locks inventory rows.
5. Reserves required quantities.
6. Records the operation in the audit table.

The database transaction ensures that partial reservations are rolled back if an error occurs.

The `complete_assembly()` procedure consumes reserved inventory and updates execution status.

A production manufacturing system would also need explicit failure and cancellation procedures that release reservations, together with idempotency controls for external execution requests.

## 13. Important Design Principles

### 13.1 High cohesion

Each component should perform a focused responsibility.

An inventory component should manage inventory rather than also implement payment processing and notification delivery.

### 13.2 Low coupling

Components should depend on clearly defined interfaces rather than unnecessary implementation details.

This makes replacement and testing easier.

### 13.3 Dependency injection

Dependencies should be supplied externally when flexibility or independent testing is important.

Constructor injection is used in the Python, C++17, and Java implementations.

### 13.4 Delegation

A composite object should coordinate component operations instead of reproducing their internal logic.

### 13.5 Encapsulation

Internal state should be protected from uncontrolled external modification.

The JavaScript implementation uses private class fields, while C++ uses private members and controlled accessors.

### 13.6 Ownership and lifecycle

Composition does not automatically determine ownership.

A system must establish whether components are:

- Exclusively owned.
- Shared between multiple objects.
- Borrowed from an external owner.
- Managed independently.

This distinction is particularly important in C++ and in systems with external resources.

## 14. Performance Considerations

| Mechanism | Performance consideration |
|---|---|
| Python object composition | Object references and method delegation introduce some runtime overhead |
| Python protocols | Runtime structural checks are not automatic unless explicitly requested |
| JavaScript Maps | Average constant-time key lookup |
| JavaScript event bus | Dispatch cost grows with subscriber count |
| C++ unique pointers | Exclusive ownership avoids reference-counting overhead |
| C++ shared pointers | Reference counting adds ownership-management overhead |
| Java collections | Hash-based collections provide efficient average lookup |
| PostgreSQL recursive CTEs | Processing cost increases with hierarchy size and traversal depth |
| PostgreSQL indexes | Improve selected reads but add storage and write overhead |

Composition should not be expanded into excessive numbers of tiny objects without a practical design benefit.

The appropriate component boundaries depend on responsibility, reuse, testability, and expected system complexity.

## 15. Security Considerations

Composition improves modularity, but it does not automatically provide security.

Important controls include:

- Validate all external input.
- Restrict access through explicit authorization policies.
- Avoid exposing mutable internal state.
- Protect sensitive configuration and credentials.
- Use parameterized SQL queries.
- Apply database permissions using least privilege.
- Record important state changes.
- Avoid logging secrets or sensitive personal information.
- Make financial and inventory operations idempotent.
- Define recovery procedures for partial failures.

The example programs use in-memory implementations and demonstration payment and notification services. They are educational domain models rather than complete production integrations.

## 16. Common Composition Mistakes

| Mistake | Consequence | Better approach |
|---|---|---|
| Constructing every dependency internally | Tight coupling | Inject dependencies |
| Creating a class with too many responsibilities | Difficult maintenance | Separate components |
| Sharing mutable default collections | Unexpected state sharing | Use independent collections |
| Ignoring ownership | Resource-management problems | Define lifecycle rules |
| Excessive delegation layers | Unnecessary complexity | Keep meaningful component boundaries |
| Depending on concrete implementations | Reduced flexibility | Use interfaces or protocols |
| Ignoring component failure | Inconsistent application state | Implement validation and compensation |
| Allowing circular composition | Infinite traversal or invalid architecture | Detect cycles |
| Mixing business logic with infrastructure | Difficult testing | Separate domain and infrastructure components |

## 17. Comparison of the Five Implementations

| Language | Main composition perspective | Important mechanisms |
|---|---|---|
| Python | Object modeling and dependency injection | Classes, dataclasses, protocols, ABC, delegation |
| JavaScript | Event-driven application architecture | Factories, closures, Maps, Sets, Promises |
| C++17 | Ownership and resource lifecycle | Unique pointers, shared pointers, interfaces, RAII |
| Java 17 | Enterprise service architecture | Records, interfaces, policies, state transitions |
| PostgreSQL | Hierarchical relational composition | Foreign keys, BOM, recursive CTEs, triggers, procedures |

## 18. When to Use Composition

Composition is particularly appropriate when:

- A class requires several independent capabilities.
- Components need to be exchanged at runtime.
- Different implementations share the same interface.
- Business logic needs independent testing.
- An application contains hierarchical domain structures.
- Services need to coordinate independent responsibilities.
- A system must support changing infrastructure without rewriting domain logic.

Composition provides a practical foundation for modular, maintainable software. Its central advantage is the ability to construct complex behavior from smaller components with clearly defined responsibilities and controlled interactions.
