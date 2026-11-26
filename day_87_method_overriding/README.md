# Method Overriding: Object-Oriented Programming and Runtime Polymorphism

## 1. Introduction

Method overriding is an object-oriented programming mechanism in which a subclass provides its own implementation of an inherited method while preserving the method's compatible signature and contractual behavior.

The overridden method replaces the inherited implementation when the method is invoked on an instance of the subclass through runtime polymorphism.

Method overriding supports specialization without requiring calling code to know the exact implementation class.

For example, an enterprise application may define a common payment-processing operation. Credit card, bank transfer, and digital wallet processors can implement the same operation differently while exposing a common interface.

The central relationship is:

Base class method
    |
    +-- Subclass A: overridden implementation
    |
    +-- Subclass B: overridden implementation
    |
    +-- Subclass C: overridden implementation

The calling code uses the common abstraction. Runtime dispatch selects the implementation associated with the actual object.

## 2. Fundamental Concepts

### 2.1 Parent class

A parent class, also called a superclass or base class, defines methods that subclasses can inherit.

A parent method establishes a shared operation and, where applicable, a behavioral contract.

Example:

- `PaymentProcessor` defines payment-processing behavior.
- `NotificationService` defines notification-delivery behavior.
- `ShippingPolicy` defines shipping-cost calculation.

A parent method may be concrete or abstract.

A concrete method provides an implementation that subclasses can inherit or override.

An abstract method defines an operation that concrete subclasses must implement.

### 2.2 Child class

A child class, also called a subclass or derived class, inherits accessible behavior from another class.

It may:

- Reuse inherited methods.
- Introduce new methods.
- Override inherited instance methods.
- Extend inherited behavior.
- Define additional state.

A subclass should preserve the behavioral expectations of its parent abstraction.

### 2.3 Method signature

A method signature identifies the method and its parameters according to the rules of the programming language.

The precise definition differs between languages.

| Language | Important signature considerations |
|---|---|
| Python | Method name and parameter behavior; runtime typing |
| JavaScript | Method name and argument behavior; dynamic runtime |
| C++ | Function name, parameter types, qualifiers and overload resolution |
| Java | Method name and parameter types; return type compatibility |

An overriding method must satisfy the language-specific overriding rules.

### 2.4 Runtime polymorphism

Runtime polymorphism allows an object to be accessed through a parent abstraction while its actual implementation is selected according to its runtime type.

For example:

- A variable refers to a `PaymentProcessor`.
- The actual object is a `CreditCardProcessor`.
- The credit card implementation executes when the overridden method is invoked.

This is different from merely calling a method that belongs to a particular subclass.

### 2.5 The `super` mechanism

`super` provides access to inherited behavior in supported contexts.

It is particularly useful when a subclass needs to extend an existing implementation instead of completely replacing it.

For example, a cashback processor can:

1. Invoke the inherited wallet-fee calculation.
2. Calculate a cashback adjustment.
3. Return the modified result.

Python, Java, and JavaScript support `super` with language-specific semantics.

C++ uses qualified base-class calls such as `BaseClass::method()`.

## 3. Method Overriding Versus Related Concepts

These concepts must remain distinct.

| Concept | Meaning |
|---|---|
| Method overriding | A subclass provides a compatible implementation of an inherited method |
| Method overloading | Multiple methods share a name but accept different parameter lists |
| Method hiding | A subclass declaration hides a parent declaration without necessarily participating in runtime overriding |
| Method inheritance | A subclass receives accessible behavior from a parent class |
| Method abstraction | A contract specifies behavior without necessarily providing an implementation |
| Dynamic dispatch | Runtime selection of an appropriate overridden implementation |
| Static dispatch | Implementation selection determined without runtime virtual dispatch |

### Overriding and overloading

Overriding changes inherited behavior.

Overloading provides multiple methods with different parameter signatures.

For example:

- `calculateFee(double amount)` can be overridden in a subclass.
- `calculateFee(double amount, String currency)` can represent an overloaded method.

The mechanisms solve different problems.

### Overriding and method hiding

Method hiding is especially important in Java and C++.

In Java, static methods are hidden rather than overridden.

In C++, a derived declaration can hide base-class overloads even when the functions are not virtual.

In JavaScript, subclass methods with the same name replace the inherited property during normal property lookup, but this does not establish the same formal virtual-method contract found in Java or C++.

## 4. Python Implementation

File: `method_overriding.py`

### 4.1 Implementation architecture

The Python implementation models an enterprise payment gateway.

The class hierarchy is:

`PaymentProcessor`
- `CreditCardProcessor`
- `BankTransferProcessor`
- `DigitalWalletProcessor`
  - `CashbackWalletProcessor`

`PaymentProcessor` is an abstract base class.

It defines two abstract operations:

- `calculate_fee()`
- `process_payment()`

It also implements shared validation and transaction-summary functionality.

Concrete processors override the abstract operations.

### 4.2 Abstract methods

The `ABC` base class and `@abstractmethod` decorator define methods that concrete subclasses must implement.

An abstract class cannot be instantiated until its abstract methods have implementations.

This creates an explicit implementation requirement.

### 4.3 Inherited concrete methods

The payment processors inherit common validation behavior.

This avoids repeating duplicate transaction checks across every implementation.

A subclass can reuse this functionality without overriding it.

### 4.4 Multilevel overriding

`CashbackWalletProcessor` inherits from `DigitalWalletProcessor`.

It overrides `calculate_fee()` and `process_payment()`.

The fee calculation calls the inherited implementation through `super()` and applies a cashback adjustment.

This demonstrates multilevel inheritance and extension of existing behavior.

### 4.5 Dynamic dispatch

The `PaymentGateway` stores processor instances using a dictionary.

The gateway does not need separate payment-processing logic for every provider.

Calling:

- `gateway.execute("credit_card", payment)`
- `gateway.execute("bank_transfer", payment)`
- `gateway.execute("digital_wallet", payment)`

causes the corresponding subclass implementation to execute.

The processor object's runtime class determines the implementation.

### 4.6 Validation and failure handling

The implementation covers:

- Empty transaction identifiers.
- Nonpositive payment amounts.
- Duplicate transactions.
- Unregistered payment providers.
- Invalid fee calculations.

Assertions verify expected behavior.

The duplicate-transaction test demonstrates how an inherited validation method can protect overridden processing operations.

## 5. JavaScript Implementation

File: `method_overriding.js`

### 5.1 Implementation architecture

The JavaScript implementation uses an event-driven order-fulfillment system.

Its hierarchy is:

`ShippingPolicy`
- `StandardShipping`
  - `SubscriptionShipping`
- `ExpressShipping`
- `InternationalShipping`

Each policy calculates shipping costs differently.

The `FulfillmentService` receives a policy identifier and retrieves the corresponding object from a registry.

It then calls the overridden `calculateCost()` method.

### 5.2 Prototype-based method lookup

JavaScript uses prototype-based inheritance.

A class declaration provides a convenient syntax for defining constructors and prototype methods.

When an object does not contain a particular property, JavaScript searches its prototype chain.

A subclass can provide a method with the same name as an inherited method.

The subclass implementation takes precedence during normal property lookup.

### 5.3 Extending inherited behavior

`SubscriptionShipping` overrides `calculateCost()`.

It invokes the parent implementation using:

`super.calculateCost(order)`

It then applies a subscription discount.

This illustrates behavioral extension instead of duplicating the complete parent calculation.

### 5.4 Event-driven execution

The fulfillment service extends Node.js `EventEmitter`.

It emits events for:

- Validated orders.
- Shipped orders.
- Rejected orders.

The event listeners operate independently of the individual shipping-policy implementations.

This separates policy calculation from operational monitoring.

### 5.5 Asynchronous execution

The fulfillment operation is asynchronous.

The implementation uses `async`, `await`, and Promise-based execution.

This represents the structure of an application that may interact with external shipping services.

### 5.6 State management

The order follows controlled state transitions:

`CREATED → VALIDATED → SHIPPED`

A rejected order follows:

`CREATED → REJECTED`

or:

`VALIDATED → REJECTED`

Invalid transitions are rejected.

The service also tracks processed order identifiers through a `Set`.

This prevents duplicate processing within the running application instance.

### 5.7 Security and operational considerations

The implementation includes:

- Private registry storage.
- Runtime type validation.
- Input validation.
- Duplicate-order prevention.
- Policy-result validation.
- Explicit error codes.
- Controlled state transitions.

An in-memory set does not provide distributed duplicate protection. Production applications should use persistent idempotency records and appropriate transaction controls.

## 6. C++17 Implementation

File: `method_overriding.cpp`

### 6.1 Implementation architecture

The C++ program implements a repository-governance and merge-eligibility engine.

Its domain includes:

- Branches.
- Pull Requests.
- Commits.
- Reviews.
- Status checks.
- Review conversations.
- Governance policies.
- Merge decisions.

This example uses polymorphic governance concepts and explicit state management to illustrate how method-oriented object models can support enterprise workflows.

### 6.2 Domain modeling

The implementation defines strongly typed enumerations for:

- Review status.
- Pull Request state.

The `Branch` class represents branch-level restrictions.

The `PullRequest` class manages proposed changes and review-related state.

The `GovernancePolicy` class defines repository-level requirements.

The `MergeEligibilityEngine` evaluates whether a proposed change satisfies those requirements.

### 6.3 Review decisions

The implementation distinguishes valid approvals from other review records.

An approval is counted only when:

- The reviewer is eligible.
- The reviewer is not the author.
- The review has not become stale.
- The review has not been dismissed.
- The review status is approved.

The use of a `set` prevents duplicate reviewer identities from increasing the approval count.

### 6.4 Status checks

Required status checks are evaluated independently.

The example requires:

- Build.
- Unit tests.
- Security scan.

A missing or unsuccessful required check blocks merging.

### 6.5 Branch restrictions

Protected branches can restrict:

- Direct pushes.
- Force pushes.
- Branch deletion.

The merge-eligibility engine also considers linear-history requirements.

These restrictions are separate from code-review decisions.

### 6.6 Merge eligibility

The engine checks:

1. Pull Request state.
2. Draft status.
3. Existence of commits.
4. Merge conflicts.
5. Base-branch synchronization.
6. Valid approvals.
7. Required status checks.
8. Conversation resolution.
9. Protected-branch requirements.

The engine returns a structured result containing eligibility and violations.

The merge operation executes only when the evaluation succeeds.

### 6.7 Performance considerations

The implementation uses:

- `unordered_map` for average constant-time keyed lookup.
- `set` for unique reviewer identities.
- `vector` for ordered commits, checks, and reviews.
- STL algorithms for searches and filtering.

For a Pull Request containing C commits, R reviews, S status checks, and V conversations, individual linear scans have costs proportional to the corresponding collection sizes.

A production implementation could maintain indexed state and incremental eligibility calculations for frequently updated Pull Requests.

## 7. Java 17 Implementation

File: `Main.java`

### 7.1 Implementation architecture

The Java implementation models an enterprise notification platform.

Its class hierarchy is:

`NotificationService`
- `EmailService`
  - `PriorityEmailService`
- `SmsService`
- `PushService`

The architecture separates notification delivery from request validation, service registration, audit recording, and coordination.

### 7.2 Abstract classes and interfaces

`NotificationService` is an abstract class.

It provides shared validation and receipt-generation behavior.

It also declares an abstract `send()` method.

`DeliveryPolicy` defines a common contract for cost calculation, validation, and service description.

This demonstrates the use of inheritance and interface-based abstraction together.

### 7.3 Method overriding

Each concrete service overrides:

- `calculateCost()`
- `send()`

The implementations reflect their different delivery mechanisms.

Email has a fixed cost.

SMS cost depends on the number of message units.

Push notifications have no delivery charge in this example.

Priority email extends the inherited email implementation and modifies the delivery description and cost.

### 7.4 Java 17 records

`NotificationRequest` and `DeliveryReceipt` are records.

Records provide concise immutable data carriers.

The compact constructor of `NotificationRequest` performs input validation.

This prevents invalid notification requests from being created through the normal constructor.

### 7.5 Enterprise service registry

`ServiceRegistry` associates notification channels with service implementations.

The coordinator retrieves an implementation through the registry rather than constructing concrete classes throughout the application.

This supports dependency management and reduces coupling.

### 7.6 Runtime polymorphism

The registry stores instances using the parent type `NotificationService`.

When the coordinator calls `service.send(request)`, Java selects the concrete overridden method according to the actual object.

This is runtime method dispatch.

### 7.7 Audit and reporting

`NotificationAudit` maintains delivery receipts.

The reporting method uses Java streams to group successful deliveries by channel.

This separates operational reporting from the implementation of notification delivery.

### 7.8 Failure handling

The implementation handles:

- Invalid email addresses.
- Invalid mobile numbers.
- Invalid device identifiers.
- Oversized notification messages.
- Duplicate notification identifiers.
- Missing service registrations.
- Invalid calculated costs.

A production implementation would also need delivery retries, external-provider response handling, persistent idempotency, and transactional audit storage.

## 8. PostgreSQL Implementation

File: `method_overriding.sql`

### 8.1 Database architecture

The SQL implementation models method definitions, class hierarchies, override relationships, and runtime invocation records.

The relational model contains:

| Table | Responsibility |
|---|---|
| `class_definitions` | Stores classes and parent relationships |
| `method_definitions` | Stores method declarations |
| `method_overrides` | Records overriding relationships |
| `method_contracts` | Stores method parameter and return contracts |
| `object_instances` | Records runtime objects |
| `method_invocations` | Stores dispatch and execution history |

### 8.2 Class hierarchy

The sample hierarchy is:

`NotificationService`
- `EmailService`
  - `PriorityEmailService`
- `SmsService`

The `parent_class_id` foreign key represents inheritance relationships.

A recursive common table expression retrieves the hierarchy and its depth.

A validation trigger prevents direct circular inheritance.

### 8.3 Method declarations

Each method record includes:

- Declaring class.
- Method name.
- Method signature.
- Method kind.
- Return type.
- Access level.
- Abstract status.
- Final status.
- Static status.

The model distinguishes instance methods from static methods.

This matters because static methods do not participate in ordinary instance-method overriding.

### 8.4 Override relationships

The `method_overrides` table links an inherited declaration to its overriding implementation.

The validation trigger checks:

- Method names.
- Signatures.
- Return types.
- Method kinds.
- Final-method restrictions.
- Static-method restrictions.
- Private-method restrictions.
- Class inheritance relationships.
- Access-level compatibility.

The model uses strict return-type equality as a simplified contract rule. Java and C++ permit certain covariant reference return types that require more advanced validation.

### 8.5 Contract compatibility

`method_contracts` stores parameter information separately from method declarations.

The contract-validation trigger checks parameter count, parameter signatures, and return types.

This provides a database-level representation of method compatibility.

### 8.6 Runtime dispatch

The `resolve_method()` function receives:

- A runtime object identifier.
- A requested parent method identifier.

It traverses the object's class hierarchy.

It searches from the runtime class towards the parent classes.

The nearest matching method implementation is returned.

For example:

A request through `NotificationService.send()` on an `EmailService` instance resolves to `EmailService.send()`.

The same request on a `PriorityEmailService` instance resolves to `PriorityEmailService.send()`.

This is a relational simulation of runtime dispatch.

It does not execute programming-language method bodies.

### 8.7 Invocation audit

`record_method_invocation()` records:

- Runtime object.
- Requested method.
- Resolved implementation.
- Invocation status.
- Execution result.
- Execution timestamp.

The reporting view combines these records with class and method metadata.

### 8.8 Reporting and evaluation

The SQL script includes:

- Recursive hierarchy retrieval.
- Overridden-method retrieval.
- Runtime dispatch reporting.
- Invocation aggregation.
- Contract compatibility evaluation.
- Failure auditing.
- Inheritance-depth reporting.

Indexes support common lookups by parent class, method name, runtime object, resolved method, and execution status.

### 8.9 Database integrity and security

Foreign keys protect referential integrity.

Check constraints reject invalid metadata states.

Triggers enforce cross-record rules that cannot be expressed through ordinary row-level constraints.

In production, database permissions should restrict changes to class and method metadata.

Invocation records should not contain passwords, tokens, or unnecessary personal information.

Concurrent hierarchy modifications require appropriate transaction and locking strategies.

## 9. Language Comparison

| Feature | Python | JavaScript | C++17 | Java 17 |
|---|---|---|---|---|
| Inheritance | Class inheritance | Prototype-based inheritance | Class inheritance | Class inheritance |
| Runtime overriding | Yes | Runtime property lookup | Virtual functions | Instance methods |
| Explicit override indicator | No mandatory keyword | No mandatory keyword | `override` | `@Override` |
| Abstract methods | `@abstractmethod` | Explicit application contract | Pure virtual functions | Abstract methods |
| Parent implementation | `super()` | `super` | `Base::method()` | `super` |
| Static method overriding | Not ordinary instance overriding | Static class methods use class inheritance semantics | Static methods are hidden | Static methods are hidden |
| Multiple inheritance | Supported for classes | Prototype-chain inheritance | Multiple base classes | Single class inheritance |
| Runtime dispatch | Dynamic | Dynamic | Virtual dispatch | Dynamic for overridable instance methods |

## 10. Important Rules and Restrictions

### 10.1 Java

Java supports overriding instance methods.

The `@Override` annotation allows the compiler to verify that a method actually overrides an inherited method.

Important restrictions include:

- Final methods cannot be overridden.
- Private methods are not inherited for overriding.
- Static methods are hidden rather than overridden.
- Constructors cannot be overridden.
- A method cannot reduce inherited access privileges.
- Overridden methods cannot introduce broader checked-exception requirements than the inherited method permits.
- Compatible covariant reference return types are allowed.

### 10.2 C++

C++ requires virtual dispatch for ordinary runtime overriding through a base-class reference or pointer.

Important mechanisms include:

- `virtual` functions.
- `override` specifiers.
- Pure virtual functions.
- Virtual destructors.
- Qualified base-class calls.

The `override` specifier allows the compiler to detect an invalid intended override.

Without virtual dispatch, a derived declaration may hide a base-class method without producing runtime polymorphism.

### 10.3 Python

Python uses dynamic method lookup.

A subclass method with the same name normally takes precedence over the inherited method.

Python does not require an override keyword.

Abstract base classes can enforce the implementation of abstract operations.

The `super()` mechanism supports cooperative inheritance and method resolution order.

### 10.4 JavaScript

JavaScript resolves methods through its prototype chain.

Subclass methods take precedence over inherited methods of the same name.

The `super` keyword can invoke inherited methods.

Private fields, property descriptors, and class methods have their own access and inheritance rules.

JavaScript does not provide a built-in compiler-enforced override annotation equivalent to Java's `@Override`.

## 11. Method Overriding and Design Quality

Method overriding is useful when subclasses represent valid specializations of a common abstraction.

It should preserve the expectations established by the parent class.

### Behavioral compatibility

A subclass should not unexpectedly weaken important parent guarantees.

For example, if a parent payment processor guarantees that duplicate transactions are rejected, an overriding implementation should preserve that guarantee.

### Liskov Substitution Principle

The Liskov Substitution Principle states that objects of a subtype should be usable wherever objects of the parent type are expected without violating the expected behavior.

Method overriding is one mechanism through which this principle is implemented.

A subclass that changes the meaning of a method incompatibly can create serious design problems even when the language accepts the override.

### Encapsulation

Common behavior should remain in the parent class when it is genuinely shared.

Subclass-specific behavior should remain in the overriding implementation.

This avoids unnecessary duplication.

### Composition versus inheritance

Method overriding is not the only mechanism for varying behavior.

Composition can be preferable when behavior changes independently of the object's class hierarchy.

For example, a shipping service can receive a separate shipping-policy object rather than creating a large hierarchy of specialized order classes.

## 12. Performance Considerations

Runtime method dispatch introduces implementation-dependent lookup or dispatch costs.

| Language | Consideration |
|---|---|
| Python | Dynamic attribute and method lookup can add runtime overhead |
| JavaScript | Prototype lookup and object-shape changes can affect optimization |
| C++ | Virtual calls can inhibit some inlining opportunities |
| Java | Virtual dispatch may be optimized through runtime profiling and devirtualization |

These costs are usually small compared with database access, network operations, and external service calls.

The choice of abstraction should primarily reflect correctness, maintainability, and system requirements.

## 13. Security Considerations

Method overriding can affect security-sensitive behavior when subclasses modify inherited operations.

Important controls include:

- Validate inputs in the common contract or an appropriate shared boundary.
- Preserve authorization requirements in overridden methods.
- Avoid allowing subclasses to bypass audit operations.
- Keep sensitive methods private or otherwise appropriately restricted.
- Avoid trusting user-controlled class or method identifiers.
- Validate extension implementations before registration.
- Preserve transaction and idempotency guarantees.
- Record relevant failures without exposing confidential information.

An override should not silently bypass security controls established by the parent implementation.

## 14. Testing Strategy

The implementations illustrate several testing dimensions.

| Test category | Example |
|---|---|
| Basic overriding | Subclass returns its specialized calculation |
| Inherited behavior | Subclass reuses a parent method |
| Extended behavior | Subclass calls `super` and modifies the result |
| Runtime dispatch | Parent reference invokes subclass implementation |
| Validation | Invalid method inputs are rejected |
| State management | Invalid state transitions fail |
| Duplicate prevention | Repeated identifiers are rejected |
| Contract compatibility | Invalid override metadata is rejected |
| Failure handling | Exceptions are handled at service boundaries |
| Multilevel inheritance | Most-specific implementation is selected |

Useful testing practices include:

- Test every concrete implementation.
- Test the parent contract independently.
- Verify that inherited behavior remains available.
- Test invalid overrides.
- Test boundary values.
- Test multilevel inheritance.
- Test polymorphic invocation through parent abstractions.
- Test security-sensitive inherited behavior.

## 15. Practical Applications

Method overriding is frequently used in:

- Payment gateways.
- Notification platforms.
- Shipping and logistics systems.
- Authentication providers.
- Database adapters.
- File-processing frameworks.
- Reporting engines.
- Enterprise integration services.
- Tax calculation systems.
- Workflow engines.

A payment platform can expose a shared payment-processing interface while allowing individual payment providers to implement their own transaction mechanisms.

A notification platform can use the same delivery operation for email, SMS, and push notifications.

A logistics application can apply specialized delivery calculations while retaining a common shipping-policy contract.

In each case, the calling application depends on the abstraction rather than the internal implementation.

## 16. Implementation Coverage

| Deliverable | Main implementation | Key concepts |
|---|---|---|
| Python | Payment gateway | Abstract base classes, overriding, `super()`, runtime polymorphism |
| JavaScript | Order fulfillment | Prototype inheritance, policy objects, asynchronous processing, events |
| C++17 | Repository-governance engine | Strong domain types, state management, policy evaluation |
| Java 17 | Enterprise notification platform | Abstract classes, interfaces, records, overriding, service registry |
| PostgreSQL | Method registry and dispatch audit | Class metadata, override relationships, recursive queries, triggers, runtime resolution |

The implementations use different domain models to demonstrate that method overriding is a reusable object-oriented mechanism rather than a feature restricted to one particular application category.
