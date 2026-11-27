# Polymorphism in Python

## 1. Introduction

Polymorphism is an object-oriented programming concept in which different objects can be accessed through a common interface while providing different implementations of the same operation.

The term originates from two Greek words:

- Poly: Many
- Morph: Forms

In programming, polymorphism allows a common operation to behave differently according to the object receiving the operation.

For example, different employee categories calculate salaries differently. A full-time employee receives a fixed salary and bonus, a contract employee receives payment based on hours, and a commission employee receives a base salary with commission.

A common method, `calculate_salary()`, provides a consistent interface for all three implementations.

The central principle is:

**One interface, multiple implementations.**

Polymorphism improves extensibility, reduces conditional logic, supports modular design, and allows software components to interact without depending on every concrete implementation.

## 2. Learning Objectives

The implementations cover the following concepts:

| Concept | Main mechanism | Implementation |
|---|---|---|
| Built-in polymorphism | Common functions operating on different types | Python |
| Method overriding | Subclass-specific implementation | Python, Java, C++ |
| Runtime polymorphism | Dynamic method dispatch | Python, Java, C++ |
| Duck typing | Object behavior determines compatibility | Python, JavaScript |
| Structural typing | Compatibility through required methods | Python Protocol |
| Abstract classes | Enforced implementation contracts | Python, C++ |
| Interfaces | Common behavioral contracts | Java |
| Operator overloading | Custom operator behavior | Python, C++ |
| Multiple inheritance | Combining inherited capabilities | Python |
| Strategy pattern | Replaceable algorithms | JavaScript, Java |
| Event-driven polymorphism | Common asynchronous event handling | JavaScript |
| Policy polymorphism | Replaceable governance rules | C++ and Java |
| Database polymorphism | Type discrimination and specialized behavior | PostgreSQL |

## 3. Fundamental Concepts

### 3.1 Common Interface

An interface defines the operations that different objects are expected to support.

Consider an employee management system.

The employee interface defines `calculate_salary()`.

Different employee classes implement that method according to their compensation rules.

The calling code does not need to know how each employee calculates compensation.

This separation provides two benefits:

- Callers depend on a consistent operation.
- Implementations can change independently.

### 3.2 Method Overriding

Method overriding occurs when a subclass provides its own implementation of a method inherited from a parent class.

Python example:

- `Employee` defines `calculate_salary()`.
- `FullTimeEmployee` overrides it.
- `ContractEmployee` overrides it.
- `CommissionEmployee` overrides it.

Each implementation calculates compensation using a different formula.

Method overriding is an important mechanism behind runtime polymorphism.

### 3.3 Runtime Polymorphism

Runtime polymorphism occurs when the implementation selected for a method call depends on the actual object type at execution time.

For example:

- A full-time employee receives a salary calculation based on monthly compensation.
- A contract employee receives a calculation based on hourly compensation.
- A commission employee receives a calculation based on sales.

The payroll function invokes the same method for every employee.

The appropriate implementation is selected dynamically.

Conceptually:

`Employee reference → calculate_salary() → Concrete implementation`

The caller does not need to use separate payroll functions for every employee category.

### 3.4 Static and Dynamic Polymorphism

Polymorphism can be classified according to how the appropriate operation is selected.

| Characteristic | Static polymorphism | Dynamic polymorphism |
|---|---|---|
| Selection | Compile time | Runtime |
| Common mechanisms | Overloading and templates | Overriding and virtual dispatch |
| Typical languages | C++ | Python, Java, C++ |
| Flexibility | Determined before execution | Determined by actual object |
| Main purpose | Compile-time specialization | Runtime substitution |

Python is dynamically typed and does not support conventional method overloading based solely on different parameter signatures.

C++ supports compile-time function overloading and runtime polymorphism through virtual functions.

Java supports method overloading and runtime method overriding.

## 4. Polymorphism in Python

Python provides several mechanisms for implementing polymorphic behavior.

### 4.1 Built-in Polymorphism

Python's built-in functions operate on different object types.

The `len()` function illustrates this behavior.

It can operate on:

- Lists
- Strings
- Tuples
- Sets
- Dictionaries

The function remains the same, while the object determines how its length is obtained.

This demonstrates polymorphism through Python's object model.

### 4.2 Duck Typing

Duck typing is a programming approach in which an object's suitability depends on its behavior rather than its declared class or inheritance relationship.

The underlying principle is:

If an object provides the required operation, it can be used where that operation is expected.

The Python implementation uses three document classes:

- `PDFDocument`
- `HTMLDocument`
- `SpreadsheetDocument`

Each provides a `render()` method.

The `render_document()` function accepts these objects without requiring them to inherit from a shared parent class.

It validates the existence of a callable method and verifies its return type.

Duck typing provides flexibility when integrating independently developed components.

Its main limitation is that an incompatible object may fail at runtime if it does not satisfy the expected behavioral contract.

### 4.3 Abstract Base Classes

An Abstract Base Class (ABC) establishes a common interface and prevents incomplete implementations from being instantiated.

Python provides the `abc` module.

Important components include:

- `ABC`
- `abstractmethod`

The payment example defines an abstract `PaymentProcessor` class.

Its concrete implementations are:

- `CardPayment`
- `BankTransfer`
- `UpiPayment`

Every implementation must provide `process_payment()`.

The abstract class also provides shared amount validation.

This design separates common validation from payment-specific processing.

An abstract class is particularly useful when implementations share common behavior or state.

### 4.4 Structural Typing with Protocol

Python's `typing.Protocol` supports structural typing.

A Protocol specifies the methods and attributes expected from an object without requiring explicit inheritance.

The `Exportable` Protocol defines an `export()` method returning bytes.

Two unrelated classes satisfy this contract:

- `JSONReport`
- `TextReport`

The `save_report()` function accepts either implementation.

Protocol-based design improves compatibility with independently developed components and supports static type checking.

Unlike an abstract base class, a Protocol does not require explicit inheritance to satisfy its structural contract.

### 4.5 Operator Overloading

Operator overloading allows user-defined classes to implement familiar operators.

Python provides special methods for this purpose.

| Operator | Python special method |
|---|---|
| `+` | `__add__()` |
| `-` | `__sub__()` |
| `*` | `__mul__()` |
| `==` | `__eq__()` |
| `<` | `__lt__()` |
| `len()` | `__len__()` |

The `Vector` class implements addition, subtraction, and scalar multiplication.

For example, adding two vectors produces another vector.

The implementation validates finite numerical values and returns `NotImplemented` for unsupported operand types where appropriate.

Operator overloading should preserve intuitive mathematical or domain-specific meaning.

### 4.6 Multiple Inheritance

Multiple inheritance allows a Python class to inherit behavior from multiple parent classes.

The implementation uses:

- `LoggerMixin`
- `ValidatorMixin`

The `SecureService` class combines both capabilities.

A mixin provides a focused reusable behavior without necessarily representing a complete domain entity.

Python resolves methods using the Method Resolution Order (MRO).

The MRO determines the order in which Python searches parent classes for attributes and methods.

The method `SecureService.__mro__` can be used to inspect this resolution order.

Multiple inheritance requires careful design because conflicting method definitions and complicated inheritance hierarchies can reduce maintainability.

### 4.7 Composition and Dependency Injection

Composition creates functionality by combining independent objects rather than relying entirely on inheritance.

The notification example uses:

- `NotificationChannel`
- `EmailChannel`
- `SMSChannel`
- `NotificationService`

The notification service receives a channel object through its constructor.

This is dependency injection.

The service depends on the common notification interface instead of directly depending on a particular delivery implementation.

A different channel can be substituted without modifying the notification service.

Composition is often preferable when an object needs interchangeable capabilities without inheriting their entire class hierarchy.

### 4.8 Factory Pattern

A factory centralizes object creation.

The `PaymentFactory` maps supported payment types to their corresponding processor classes.

The calling code requests a processor using a supported identifier.

The factory returns an object implementing the common payment interface.

This separates object creation from object usage.

A production factory should validate input, restrict supported implementations, and avoid constructing arbitrary classes from untrusted input.

## 5. JavaScript Polymorphism

JavaScript implements polymorphism through its prototype-based object model and dynamic method dispatch.

### 5.1 Prototype-Based Inheritance

JavaScript classes provide a convenient syntax over the prototype system.

The data-source example defines a base class with an asynchronous `fetch()` method.

Concrete classes implement different retrieval behaviors:

- `DatabaseSource`
- `APIDataSource`
- `FileDataSource`

The `collectData()` function invokes the same operation for each object.

The runtime selects the appropriate implementation.

### 5.2 Duck Typing

JavaScript does not require a formal interface declaration for an object to participate in a polymorphic operation.

The `exportData()` function checks whether an object provides a callable `format()` method.

The JSON, CSV, and XML formatters implement this operation differently.

This provides structural compatibility.

The caller does not need to know the concrete formatter class.

### 5.3 Strategy Pattern

The Strategy pattern encapsulates interchangeable algorithms behind a common interface.

The pricing example implements:

- `RegularDiscount`
- `PremiumDiscount`
- `EnterpriseDiscount`

Each strategy calculates a discount using a different formula.

`PricingEngine` receives a strategy and allows the strategy to be replaced at runtime.

The pricing calculation remains independent of the discount policy.

This avoids embedding multiple discount conditions inside one large function.

### 5.4 Event-Driven Polymorphism

The notification implementation demonstrates asynchronous polymorphism.

Different delivery channels provide a common `deliver()` operation.

The implementations validate different recipient formats.

`DeliveryRegistry` stores supported implementations in a `Map`.

`NotificationBus` selects the appropriate implementation when an event is published.

The Node.js `EventEmitter` publishes completion events.

This design separates:

- Event production
- Channel selection
- Delivery execution
- Completion notification

Asynchronous execution uses Promises and `async`/`await`.

The retry implementation demonstrates bounded retries with exponential backoff.

Real delivery systems must distinguish transient failures from permanent failures and should use idempotency keys to prevent duplicate external operations.

### 5.5 Policy-Based Polymorphism

The JavaScript access-control example uses interchangeable policy objects.

Its implementations include:

- Administrator policy
- Developer policy
- Read-only policy

The policy engine delegates authorization decisions to the selected policy.

This separates access-control rules from the service that evaluates them.

Production authorization should use trusted identity information, explicit permission scopes, and server-side enforcement.

## 6. C++17 Polymorphism

C++ supports runtime polymorphism through inheritance and virtual functions.

### 6.1 Abstract Base Classes

The C++ implementation defines `GovernanceRule` as an abstract base class.

Its pure virtual method is:

`evaluate()`

Concrete policies override this method.

The implementation includes:

- `ApprovalRule`
- `StatusCheckRule`
- `ConversationRule`
- `BranchProtectionRule`
- `LinearHistoryRule`

Each rule evaluates a different governance condition.

The governance engine stores rule objects through `shared_ptr<const GovernanceRule>`.

This enables runtime dispatch through base-class pointers while maintaining shared ownership.

### 6.2 Virtual Functions and Dynamic Dispatch

When a virtual function is invoked through a base-class pointer or reference, C++ selects the overriding implementation belonging to the actual object.

The governance engine does not need to know the concrete type of each rule.

It iterates through the registered policies and calls `evaluate()`.

This is runtime polymorphism.

The `override` keyword verifies that a method actually overrides a virtual method in the base class.

The virtual destructor ensures that derived objects are correctly destroyed through base-class pointers.

### 6.3 Smart Pointers

The implementation uses `shared_ptr` to manage policy-object lifetime.

Smart pointers reduce manual memory-management errors.

Important C++ smart pointers include:

| Smart pointer | Ownership behavior |
|---|---|
| `unique_ptr` | Exclusive ownership |
| `shared_ptr` | Shared ownership |
| `weak_ptr` | Non-owning reference to shared ownership |

The governance engine uses shared ownership because multiple components may hold references to the same immutable policy.

Where shared ownership is unnecessary, `unique_ptr` is generally preferable.

### 6.4 STL Containers

The implementation uses:

- `vector` for commits, reviews, checks, and policies.
- `set` for unique reviewers and required check names.
- `map` for status-check lookup.
- `shared_ptr` for policy ownership.

These structures provide predictable and maintainable data management.

The approval calculation uses a set to prevent duplicate reviewer approvals from being counted multiple times.

### 6.5 Merge Eligibility

The governance engine combines multiple independent policy evaluations.

The result includes:

- Eligibility status
- Violation messages

A Pull Request is eligible only when all required governance rules pass.

The implementation distinguishes review approval from automated checks and branch-level enforcement.

A successful evaluation is not sufficient by itself if the target branch changes before merging.

The merge service verifies that the target branch still references the expected base commit.

This is a simplified optimistic concurrency check.

A production implementation must also validate commit ancestry, conflict resolution, branch permissions, and concurrent updates.

## 7. Java 17 Polymorphism

Java provides polymorphism through interfaces, abstract classes, inheritance, and method overriding.

### 7.1 Interfaces

An interface specifies operations that implementing classes must provide.

Java interfaces support multiple interface implementation.

The enterprise implementation uses a sealed `GovernanceRule` interface.

Its permitted implementations are explicitly declared.

This restricts the set of classes that can implement the governance contract.

Sealed interfaces are useful when a domain requires a controlled set of policy implementations.

### 7.2 Abstract Classes

Abstract classes can contain both abstract methods and implemented methods.

They are useful when related classes share behavior or state.

Unlike interfaces, a Java class can extend only one class.

It can implement multiple interfaces.

### 7.3 Records

Java 17 records provide a concise mechanism for immutable data carriers.

The implementation uses records for:

- `Commit`
- `Review`
- `StatusCheck`
- `Branch`
- `ProtectionPolicy`
- `PullRequest`
- `EvaluationResult`

Records automatically provide component accessors, equality, hashing, and string representation.

Compact constructors validate data during object creation.

Collection components are copied into immutable lists or sets where appropriate.

Records are particularly useful for domain values that should not change after construction.

### 7.4 Strategy-Based Governance

Each governance rule implements the same interface.

The governance service iterates over these policies without depending on individual implementations.

This is an example of the Open/Closed Principle.

The service can support additional compatible rules without rewriting its evaluation loop.

### 7.5 State Transitions

The `PullRequestLifecycle` class models explicit state transitions.

Supported operations include:

- Opening a draft or closed Pull Request.
- Closing an open Pull Request.
- Merging an open Pull Request.

Invalid transitions raise exceptions.

A state-transition service prevents arbitrary changes that violate lifecycle rules.

### 7.6 Enterprise Validation

The implementation uses custom exceptions to distinguish:

- Invalid domain data.
- Invalid governance operations.

It also uses immutable collections and defensive validation.

These mechanisms help prevent inconsistent enterprise application state.

## 8. PostgreSQL Polymorphism

Relational databases do not provide the same class inheritance and dynamic method dispatch mechanisms found in object-oriented languages.

Polymorphic behavior can nevertheless be modeled through relational structures and database functions.

### 8.1 Discriminator-Based Modeling

The notification example uses a common `notification_channels` table.

The `channel_type` column identifies the concrete channel category.

Specialized tables provide additional fields:

- `email_channels`
- `sms_channels`
- `webhook_channels`

The common channel table provides shared identity and activation state.

The specialized tables store channel-specific information.

This resembles a type hierarchy implemented through relational tables.

### 8.2 Foreign Keys and Integrity

Composite foreign keys ensure that specialized records reference the correct parent channel type.

For example, an email subtype cannot reference a parent record identified as an SMS channel through the declared constraints.

This reduces invalid subtype relationships.

The database schema also uses:

- Primary keys
- Foreign keys
- Unique constraints
- Check constraints
- Partial indexes
- Composite indexes

These mechanisms enforce data integrity and support query performance.

### 8.3 SQL Function-Based Dispatch

The `dispatch_notification()` function evaluates the channel discriminator.

A PostgreSQL `CASE` expression selects the appropriate validation branch.

The function performs channel-specific checks and updates delivery state.

This is database-level behavior selection based on a discriminator.

The function does not contact external email, SMS, or webhook services. It models validation and dispatch-state recording.

Real delivery should be performed through an external worker or service.

### 8.4 Repository Relationships

The repository schema models the following relationships:

`Repository → Branches → Commits → Pull Requests`

Pull Requests connect a source branch to a target branch.

They also reference proposed base and head commit identifiers.

The schema records individual commits associated with a Pull Request.

This distinguishes the proposed changes from the actual branch state.

### 8.5 Review and Approval Data

The review tables represent reviewer decisions.

The review state distinguishes:

- Approved
- Changes requested
- Commented
- Dismissed

Reviewer assignments identify eligible reviewers.

Approval counting excludes the Pull Request author and checks the review against the current head commit.

A review against an earlier head commit does not satisfy the current approval requirement.

This is the database representation of stale approval handling.

### 8.6 Status Checks

Automated checks are represented independently from human reviews.

Examples include:

- Unit tests
- Security scans
- Build validation

Each check references the commit it evaluated.

Only successful checks against the current head commit satisfy the required check conditions.

This prevents an earlier successful execution from incorrectly authorizing newer code.

### 8.7 Branch Protection

Branch protection policies store repository-level merge restrictions.

The example includes:

- Required approval count
- Required status checks
- Resolved-conversation requirements
- Linear-history requirements
- Direct-push restrictions
- Force-push restrictions
- Branch deletion restrictions
- Bypass configuration

The merge eligibility function evaluates applicable policy conditions.

Branch protection is separate from the review decision itself.

### 8.8 Transactional Merge

The merge procedure uses row-level locking.

It locks the Pull Request and target branch, recalculates eligibility, verifies authorization, and updates the target branch.

The procedure also checks whether the target branch still references the expected base commit.

If a concurrent update changes the branch, the operation fails.

This prevents a stale evaluation from automatically authorizing a merge.

The example uses a simplified generated commit identifier rather than implementing a real Git object graph.

## 9. Distinguishing the Polymorphism Mechanisms

| Mechanism | Main purpose | Main advantage | Important limitation |
|---|---|---|---|
| Inheritance | Share and specialize behavior | Reuse | Can create tight coupling |
| Overriding | Replace inherited behavior | Runtime specialization | Requires compatible method contracts |
| Abstract classes | Enforce implementation requirements | Common structure | Usually single inheritance in class hierarchies |
| Interfaces | Define behavioral contracts | Loose coupling | May require separate shared implementation |
| Duck typing | Accept compatible behavior | Flexibility | Runtime compatibility failures |
| Protocol | Describe structural contracts | Static structural checking | Type checking does not guarantee runtime correctness |
| Operator overloading | Customize operators | Natural domain expressions | Poor design can make behavior confusing |
| Strategy pattern | Replace algorithms | Extensibility | Adds additional objects and abstractions |
| Dependency injection | Supply interchangeable dependencies | Testability | Requires dependency management |
| Factory pattern | Centralize object creation | Controlled construction | Factories can become overly complex |

## 10. Relationship Between the Five Implementations

The five source files demonstrate different applications of the same underlying concept.

| Language | Main application | Polymorphic mechanism |
|---|---|---|
| Python | Employee compensation, payment, reporting, notification | ABC, Protocol, duck typing, overriding |
| JavaScript | Data retrieval, pricing, notification, access control | Dynamic dispatch, strategies, events |
| C++17 | Repository governance and merge eligibility | Virtual functions and abstract classes |
| Java 17 | Enterprise repository governance | Sealed interfaces, records, strategy policies |
| PostgreSQL | Repository workflow and notification channels | Discriminators, specialized tables, SQL functions |

The implementations are complementary rather than identical translations.

Python focuses on the range of polymorphism mechanisms available in a dynamically typed language.

JavaScript demonstrates asynchronous and event-driven extensibility.

C++ demonstrates explicit runtime dispatch and memory ownership.

Java demonstrates immutable enterprise domain models and controlled policy implementations.

PostgreSQL demonstrates how related concepts can be represented through relational structures and database-side dispatch.

## 11. Practical Design Principles

### 11.1 Program to an Interface

Depend on the required operation rather than a particular implementation.

A notification service should depend on a notification contract rather than directly depending on email delivery.

### 11.2 Prefer Composition When Appropriate

Inheritance represents an is-a relationship.

Composition represents a has-a relationship.

A notification service has a delivery channel. It does not need to inherit from an email or SMS class.

### 11.3 Follow the Substitution Principle

The Liskov Substitution Principle states that an object of a subtype should be usable wherever its parent type is expected without breaking the correctness of the program.

An implementation must preserve the behavioral expectations of its base contract.

A payment processor that silently accepts invalid amounts would violate the expected behavior of a validated payment interface.

### 11.4 Keep Responsibilities Separate

A single interface should represent a coherent responsibility.

A reporting interface should not also perform database administration, authentication, and notification delivery.

Small interfaces make substitution and testing easier.

### 11.5 Validate at System Boundaries

Polymorphism does not eliminate validation.

Validate:

- Object construction.
- Method arguments.
- Return values where required.
- External data.
- Authorization context.
- State transitions.
- Database relationships.

### 11.6 Avoid Excessive Inheritance

Deep inheritance hierarchies create dependencies between parent and child classes.

Changes to a parent class can affect multiple subclasses.

Composition and focused interfaces can reduce this problem.

### 11.7 Design for Failure

Different implementations may fail differently.

For example:

- A payment provider may reject a transaction.
- An email address may be invalid.
- A database connection may fail.
- A status check may remain pending.
- A review may become stale.
- A branch may change before merging.

Polymorphic interfaces should have clearly defined failure behavior.

## 12. Performance Considerations

Polymorphism introduces different performance characteristics depending on the language and implementation.

| Language | Dispatch mechanism | Performance consideration |
|---|---|---|
| Python | Dynamic attribute and method lookup | Runtime dispatch and object overhead |
| JavaScript | Prototype-based method lookup | Object shape and optimization behavior |
| C++17 | Virtual dispatch | Indirect function call and possible optimization constraints |
| Java 17 | Virtual/interface dispatch | JIT compilation and call-site optimization |
| PostgreSQL | SQL function and relational query execution | Query plans, indexes, joins, and locking |

Important considerations:

- Avoid repeatedly constructing expensive strategy objects.
- Reuse immutable policies where appropriate.
- Use efficient lookup structures.
- Avoid unnecessary database round trips.
- Index frequently evaluated foreign keys and status fields.
- Avoid overly broad policy evaluation.
- Measure actual workloads instead of assuming polymorphism is the main performance bottleneck.

In most enterprise applications, database access, network calls, serialization, and external service latency are more significant than the cost of a virtual method call.

## 13. Security Considerations

Polymorphic extensibility must not become unrestricted execution.

Important safeguards include:

- Restrict supported implementations.
- Validate user-controlled type identifiers.
- Avoid arbitrary class loading from untrusted input.
- Validate payment amounts and recipients.
- Apply authorization independently of object type.
- Protect sensitive configuration.
- Prevent unauthorized policy bypass.
- Verify review eligibility.
- Recalculate merge eligibility before merging.
- Use database transactions for critical state changes.
- Avoid executing external network requests inside database transactions.

A common interface does not automatically guarantee that an implementation is secure.

Security must be enforced independently at the relevant application and infrastructure boundaries.

## 14. Edge Cases Covered

| Area | Failure condition | Expected behavior |
|---|---|---|
| Python payroll | Invalid salary | Reject construction |
| Python payment | Negative amount | Raise validation error |
| Python duck typing | Missing method | Reject incompatible object |
| Python operator overloading | Invalid operand | Return `NotImplemented` |
| Python vector | Non-finite coordinate | Reject construction |
| JavaScript formatter | Missing `format()` | Throw `TypeError` |
| JavaScript notification | Invalid recipient | Reject delivery |
| JavaScript strategy | Invalid discount | Reject calculation |
| JavaScript retry | Repeated failure | Stop at configured limit |
| C++ governance | Insufficient approvals | Reject merge |
| C++ governance | Failed status check | Reject merge |
| C++ governance | Stale approval | Reject merge |
| Java governance | Invalid state transition | Throw domain exception |
| Java governance | Draft Pull Request | Reject merge |
| PostgreSQL | Invalid channel subtype | Reject foreign-key relationship |
| PostgreSQL | Unresolved conversation | Reject merge |
| PostgreSQL | Failed status check | Reject merge |
| PostgreSQL | Concurrent branch update | Roll back transaction |

## 15. Execution Requirements

| Deliverable | Runtime | External dependencies |
|---|---|---|
| Python | Python 3.10 or later | None |
| JavaScript | Node.js 18 or later | None |
| C++17 | C++17-compatible compiler | None |
| Java | Java 17 | None |
| PostgreSQL | PostgreSQL 14 or later | None |

The Python script creates temporary report files and removes them automatically.

The JavaScript implementation uses Node.js standard-library modules.

The C++ implementation uses standard C++17 libraries.

The Java implementation uses standard Java 17 features.

The PostgreSQL script creates a dedicated schema and its associated tables, functions, triggers, sample records, and reporting views.

The SQL script is transactional. It should be executed against a database where the schema can be created.

## 16. Complexity and Scalability

The primary complexity considerations are:

| Operation | Data structure | Expected complexity |
|---|---|---|
| Python list iteration | List | O(n) |
| Python dictionary lookup | Dictionary | O(1) average |
| Python set membership | Set | O(1) average |
| JavaScript strategy lookup | Map | O(1) average |
| C++ reviewer deduplication | Set | O(log n) per insertion |
| C++ required-check lookup | Map | O(log n) per lookup |
| Java reviewer deduplication | HashSet | O(1) average |
| Java policy iteration | List | O(p) |
| PostgreSQL indexed lookup | B-tree index | O(log n) typical |
| PostgreSQL aggregation | Relational execution | Depends on rows, indexes, and execution plan |

Here, `n` represents the number of relevant objects and `p` represents the number of registered policies.

For enterprise systems, the number of registered policies is generally small compared with the volume of repository, review, and status-check records.

Database indexing and efficient query design become increasingly important as the number of Pull Requests and associated events grows.

## 17. Key Terminology

| Term | Definition |
|---|---|
| Polymorphism | Ability to use a common operation with multiple implementations |
| Method overriding | Subclass replacement of an inherited method |
| Dynamic dispatch | Runtime selection of an implementation |
| Duck typing | Compatibility based on supported behavior |
| Abstract class | Class that defines a contract and may contain shared implementation |
| Interface | Contract describing supported operations |
| Protocol | Python structural typing contract |
| Virtual function | C++ function supporting runtime dispatch |
| Method Resolution Order | Python's inheritance method lookup order |
| Strategy pattern | Encapsulation of interchangeable algorithms |
| Dependency injection | Supplying an object's dependencies externally |
| Composition | Building functionality from collaborating objects |
| Liskov Substitution Principle | Requirement that subtypes preserve parent behavioral expectations |
| Discriminator | Field identifying a concrete subtype |
| State transition | Valid movement from one domain state to another |

## 18. Final Conceptual Distinction

Polymorphism is not simply the use of inheritance.

Inheritance is one mechanism through which polymorphism can be implemented.

Polymorphic behavior can also be achieved through duck typing, structural typing, interfaces, abstract classes, composition, and strategy objects.

The most important design consideration is the separation of an operation's contract from its concrete implementation.

A well-designed polymorphic system allows new implementations to be introduced without unnecessarily changing the components that use them.
