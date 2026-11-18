# Attributes and Methods in Object-Oriented Programming

## 1. Introduction

Attributes and methods are the two fundamental building blocks of objects in object-oriented programming (OOP).

An object combines data with operations that work on that data.

- **Attributes** describe the properties and state of an object.
- **Methods** define the operations and behaviour of an object.

A banking application provides a practical model. A bank account has an account number, owner, balance, and status. It also supports operations such as depositing money, withdrawing money, transferring funds, freezing an account, and calculating interest.

The implementations use this domain to demonstrate how different programming languages represent attributes and methods.

## 2. Object, Class, Attributes, and Methods

### Class

A class defines the structure and behaviour shared by objects of a particular type.

For example, `BankAccount` defines the attributes and operations that a bank account should support.

### Object

An object is an instance of a class.

Two objects created from the same class can have different attribute values.

| Object | Account number | Owner | Balance |
|---|---|---|---:|
| Account 1 | ACC1001 | Rahul Sharma | 50,000 |
| Account 2 | ACC1002 | Priya Verma | 75,000 |

Both objects use the same class definition but maintain independent instance state.

### Attributes

Attributes store information associated with an object or class.

Consider the following classification:

| Attribute category | Meaning | Example |
|---|---|---|
| Instance attribute | Belongs to an individual object | `balance` |
| Class attribute | Shared at class level | `bankName` |
| Public attribute | Accessible through the public interface | `accountNumber` |
| Protected attribute | Intended for the class and derived classes | `minimumBalance` |
| Private attribute | Restricted through language-level access mechanisms | `__balance` |
| Constant attribute | Cannot be reassigned through the applicable language mechanism | `final` or `const` |
| Computed attribute | Obtained through a calculation or accessor | `availableBalance` |

An instance attribute belongs to an individual object. Changing one account's balance should not change another account's balance.

A class attribute represents information associated with the class itself. The bank name and account counter are examples.

### Methods

Methods represent operations associated with an object or class.

| Method category | Purpose | Example |
|---|---|---|
| Instance method | Operates on object state | `deposit()` |
| Class method | Operates at class level | `create_account()` |
| Static method | Performs an operation without requiring object state | `format_currency()` |
| Getter | Retrieves an attribute | `balance()` |
| Setter | Controls attribute modification | `set_interest_rate()` |
| Constructor | Initializes a new object | `__init__()` |
| Destructor | Handles object destruction or cleanup where applicable | `~BankAccount()` |
| Abstract method | Defines behaviour implemented by subclasses | `calculate_interest()` |
| Overridden method | Replaces inherited behaviour | `accountType()` |

## 3. Relationship Between Attributes and Methods

Attributes and methods are related through encapsulation.

An object's methods operate on its attributes while controlling how its internal state changes.

The relationship can be represented as:

    CLASS: BankAccount
    |
    +-- ATTRIBUTES
    |   |
    |   +-- account_number
    |   +-- owner
    |   +-- balance
    |   +-- status
    |   +-- transaction_history
    |
    +-- METHODS
        |
        +-- deposit()
        +-- withdraw()
        +-- transfer_to()
        +-- freeze()
        +-- unfreeze()
        +-- close()

For example, `deposit()` increases the balance after validating the transaction amount and account status.

The balance is not modified arbitrarily through an external operation. The method controls the state transition.

This separation improves data integrity and makes business rules easier to maintain.

## 4. Encapsulation and Access Control

Encapsulation combines data and behaviour while restricting uncontrolled access to internal state.

Consider an account balance.

An unsafe implementation would allow unrestricted assignment:

    account.balance = -50000

A controlled implementation exposes a read-only balance and requires changes to pass through validated methods.

The Python implementation uses:

- `__balance` for name-mangled private storage.
- `@property` for controlled attribute access.
- `deposit()` for increasing the balance.
- `withdraw()` for decreasing the balance.

The JavaScript implementation uses ECMAScript private fields such as `#balance`.

The C++ implementation uses `private`, `protected`, and `public` access specifiers.

The Java implementation uses private fields, public accessors, and synchronized methods.

PostgreSQL uses table constraints, triggers, and stored functions to enforce data integrity.

**Important distinction:** Access modifiers do not provide identical security guarantees across languages. Python name mangling is not equivalent to Java private access or C++ access control. Database permissions and application authorization are separate security boundaries.

## 5. Instance Attributes and Class Attributes

### Instance attributes

Each object maintains its own values.

For example:

- Rahul's account has a balance of INR 50,000.
- Priya's account has a balance of INR 75,000.

Modifying Rahul's balance does not automatically modify Priya's balance.

### Class attributes

Class attributes represent information shared at class level.

Examples include:

- Bank name.
- Default minimum balance.
- Account creation counter.
- Default transaction configuration.

The Python implementation uses `ClassVar`.

The JavaScript implementation uses `static` class fields.

The C++ implementation uses static data members and inline static variables.

The Java implementation uses static fields.

The PostgreSQL implementation represents shared configuration through the `bank_configuration` table.

A database configuration row is not literally a programming-language class attribute. It provides an equivalent shared configuration mechanism in a relational environment.

## 6. Instance Methods, Class Methods, and Static Methods

### Instance methods

Instance methods operate on a particular object's state.

Examples:

- `deposit()`
- `withdraw()`
- `transferTo()`
- `freeze()`

They require access to the relevant account object.

### Class methods

Class methods operate at class level rather than requiring an already existing instance.

The Python implementation demonstrates:

- `change_bank_name()`
- `create_account()`

A class method receives the class itself through `cls`. It can therefore construct objects or modify class-level configuration.

### Static methods

Static methods perform operations associated with a class but do not automatically receive an instance or class reference.

Examples:

- Amount validation.
- Currency formatting.
- Monetary value conversion.

The distinction is important:

| Property | Instance method | Class method | Static method |
|---|---|---|---|
| Associated with | Object | Class | Class namespace |
| Automatic instance access | Yes | No | No |
| Automatic class access | Through instance/class | Yes | No |
| Typical use | Business operations | Class-level operations | Independent utility operations |

Java and C++ provide static methods but do not have Python's exact class-method binding mechanism.

JavaScript also provides static methods.

## 7. Constructors and Object Initialization

A constructor establishes the initial state of an object.

The implementations initialize:

- Account identity.
- Account owner.
- Initial balance.
- Account status.
- Transaction history.
- Account-specific policy.

Validation during construction prevents invalid objects from entering the application.

Examples of rejected initialization conditions include:

- Missing account number.
- Empty owner name.
- Negative initial balance.
- Invalid interest rate.
- Invalid monetary precision.

Java uses constructors with explicit types. Python uses `__init__()`. JavaScript uses `constructor()`. C++ uses member initialization lists.

PostgreSQL performs initialization through the `create_account()` stored procedure and table constraints.

## 8. Getters, Setters, and Properties

A getter retrieves an attribute without exposing the underlying storage mechanism.

A setter provides controlled modification.

Python properties provide attribute-like access while executing validation or computation.

Java commonly uses accessor methods.

C++ commonly uses explicit getter and setter methods.

JavaScript uses `get` and `set` accessors.

A read-only balance is appropriate when all balance changes must pass through financial operations.

Not every attribute needs a setter. Exposing unnecessary modification methods increases the number of possible invalid states.

## 9. Inheritance and Method Overriding

Inheritance allows one class to reuse and extend another class.

The implementations define two account types:

- `BankAccount`
- `SavingsAccount`

The savings account inherits common account functionality.

It introduces a specialized interest-rate attribute and interest-related methods.

    BankAccount
    |
    +-- accountNumber
    +-- owner
    +-- balance
    +-- status
    +-- deposit()
    +-- withdraw()
    +-- freeze()
    |
    +-- SavingsAccount
        |
        +-- interestRate
        +-- calculateInterest()
        +-- applyInterest()

Method overriding allows a derived class to provide specialized behaviour for an inherited method.

For example, `accountType()` returns `STANDARD` for the base account and `SAVINGS` for the specialized account.

Overriding should preserve the expected contract of the parent method.

Inheritance is useful when a genuine subtype relationship exists. Composition is preferable when an object merely uses another object's services.

## 10. Polymorphism and Interfaces

Polymorphism allows different object types to be accessed through a common interface.

The banking example processes standard and savings accounts through a common account abstraction.

A caller can request an account's display behaviour without needing to know its concrete implementation.

Java additionally demonstrates the `InterestBearing` interface.

The interface establishes a contract:

- `calculateInterest()`
- `applyInterest()`

A class implementing this interface must provide the corresponding behaviour.

C++ uses virtual methods and method overriding to support runtime polymorphism.

Python supports polymorphism through its dynamic object model.

JavaScript uses its object and prototype system.

## 11. Composition and State Management

Composition represents relationships in which an object contains or manages other objects.

A bank account contains transaction history.

A transaction records:

- Transaction identifier.
- Transaction type.
- Amount.
- Resulting balance.
- Timestamp.

This design separates account state from transaction records.

The account also maintains a status.

| Status | Meaning | Permitted financial operations |
|---|---|---|
| ACTIVE | Account can perform transactions | Deposit, withdrawal, transfer |
| FROZEN | Account temporarily restricted | No financial transactions |
| CLOSED | Account permanently closed | No further transactions |

The state transition rules prevent invalid operations.

Examples:

- A frozen account cannot perform deposits.
- A closed account cannot be reactivated.
- An account cannot be closed with a nonzero balance.
- An active account can be frozen.
- A frozen account can be reactivated.

The implementations use enumerations to represent valid states rather than unrestricted strings.

## 12. Validation and Exception Handling

Methods should validate their inputs before modifying object state.

The banking examples enforce the following rules:

| Validation | Rule |
|---|---|
| Account identity | Must not be empty |
| Owner | Must not be empty |
| Initial balance | Must not be negative |
| Deposit | Must be positive |
| Withdrawal | Must be positive |
| Transfer | Must be positive |
| Monetary precision | Maximum two decimal places |
| Interest rate | Between 0 and 100 percent |
| Account status | Must permit the requested operation |
| Transfer destination | Must be a different valid account |
| Account balance | Must satisfy the minimum balance policy |

Custom exceptions communicate domain-specific failures.

Examples include:

- `InvalidAmountError`
- `InsufficientFundsError`
- `AccountUnavailableError`
- `ValidationException`
- `StateTransitionException`

An important implementation principle is to validate all transaction conditions before changing financial state.

## 13. Transaction Processing and Concurrency

A transfer affects two account objects.

A valid transfer must:

1. Identify the source account.
2. Identify the destination account.
3. Validate both accounts.
4. Validate the transfer amount.
5. Verify sufficient source funds.
6. Update the source balance.
7. Update the destination balance.
8. Record both transaction entries.

The Python implementation demonstrates exception-based rollback for an in-memory operation.

The JavaScript implementation uses asynchronous execution and ordered account locks within a single process.

The C++ implementation demonstrates exception handling and restoration of previous state.

The Java implementation uses synchronized methods and stable lock ordering.

The PostgreSQL implementation uses row-level locks with `SELECT ... FOR UPDATE`.

These approaches are not interchangeable.

In-memory locks coordinate objects within a process. They do not coordinate independent application instances.

A production financial system should use database transactions, durable records, concurrency controls, appropriate isolation, and idempotency mechanisms.

## 14. Language-Specific Implementation Decisions

### Python

The Python implementation focuses on readable object modelling.

| Feature | Implementation |
|---|---|
| Instance attributes | Object attributes |
| Class attributes | `ClassVar` |
| Private attributes | Name-mangled attributes |
| Properties | `@property` |
| Instance methods | `deposit()`, `withdraw()` |
| Class methods | `create_account()` |
| Static methods | `format_currency()` |
| Inheritance | `SavingsAccount` |
| Special methods | `__str__()`, `__repr__()` |
| Immutable data | Frozen `Transaction` dataclass |

The implementation uses `Decimal` rather than binary floating-point arithmetic for financial values.

### JavaScript

The JavaScript implementation focuses on event-driven behaviour.

| Feature | Implementation |
|---|---|
| Instance attributes | Object properties |
| Class attributes | Static fields |
| Private attributes | `#balance`, `#status` |
| Instance methods | Class methods |
| Static methods | Static class functions |
| Inheritance | `extends` |
| Events | `EventEmitter` |
| Asynchronous operations | `async` and `await` |
| Collections | `Map` |
| Immutable snapshots | `Object.freeze()` |

Integer cents are used to avoid common floating-point precision errors.

The asynchronous transfer mechanism uses ordered locking to coordinate operations on account objects within one JavaScript process.

### C++17

The C++ implementation emphasizes explicit access control and runtime polymorphism.

| Feature | Implementation |
|---|---|
| Public attributes and methods | `public` |
| Protected attributes | `protected` |
| Private attributes | `private` |
| Class-level attributes | Static members |
| Instance methods | Member functions |
| Read-only methods | `const` methods |
| Inheritance | `SavingsAccount` |
| Overriding | `override` |
| Runtime polymorphism | Virtual functions |
| Collections | `std::vector` |
| Exceptions | Standard and custom exceptions |

The implementation uses integer paise for monetary storage.

Copying account objects is prohibited to prevent accidental duplication of account identity and state.

### Java 17

The Java implementation emphasizes enterprise-oriented domain modelling.

| Feature | Implementation |
|---|---|
| Instance attributes | Private fields |
| Class attributes | Static fields |
| Immutable attributes | `final` fields |
| Immutable data | Records |
| Behaviour contract | Interface |
| Inheritance | `extends` |
| Method overriding | `@Override` |
| Collection management | Collections framework |
| Optional retrieval | `Optional` |
| Generic repository | `AccountRepository<T>` |
| Concurrency | Synchronized methods |
| Domain validation | Custom exceptions |
| Policy management | `AccountPolicy` |

The `Transaction` and `AccountSnapshot` records provide concise immutable data structures.

### PostgreSQL

PostgreSQL represents attributes and methods using relational database structures and routines.

| Object-oriented concept | PostgreSQL implementation |
|---|---|
| Object attributes | Table columns |
| Object identity | Primary key |
| Class-level configuration | Configuration table |
| Object specialization | Account type reference table |
| Instance operations | Parameterized functions |
| Class-level utility operations | Database routines |
| Constructors | Account creation procedure |
| Encapsulation | Controlled routines and privileges |
| Validation | Constraints and triggers |
| State transitions | Status-management function |
| Composition | Foreign-key relationships |
| Object collection | Relational tables |
| Reporting | Views and aggregate queries |

PostgreSQL is a relational database, not a conventional class-based object-oriented language. Its routines and relational structures provide database-level equivalents for many of the concepts.

## 15. Database Attributes and Methods

The SQL implementation uses the `oop_demo` schema.

Its main entities are:

    bank_configuration
          |
          +-- Shared configuration

    account_types
          |
          +-- STANDARD
          +-- SAVINGS

    bank_accounts
          |
          +-- Account attributes
          +-- Account status
          +-- Balance
          |
          +-- account_transactions
                  |
                  +-- Transaction identity
                  +-- Transaction type
                  +-- Transaction amount
                  +-- Balance after transaction

Database methods are implemented through functions and procedures.

Important routines include:

| Routine | Responsibility |
|---|---|
| `deposit_amount()` | Deposit validation and balance update |
| `withdraw_amount()` | Withdrawal validation and balance update |
| `transfer_amount()` | Atomic account transfer |
| `change_account_status()` | Account state transition |
| `calculate_interest()` | Savings interest calculation |
| `apply_interest()` | Interest application |
| `create_account()` | Account initialization |

The implementation also uses:

- Primary keys for entity identity.
- Foreign keys for relationships.
- Unique constraints for account numbers.
- Check constraints for valid monetary values.
- Triggers for attribute validation.
- Triggers for transaction immutability.
- Indexes for frequently accessed records.
- Views for account and transaction reporting.
- CTEs and window functions for analytical queries.

## 16. Practical Differences Between Attributes and Methods

Attributes and methods serve different purposes.

| Dimension | Attributes | Methods |
|---|---|---|
| Primary responsibility | Store information | Perform operations |
| Represents | State | Behaviour |
| Typical examples | Balance, owner, status | Deposit, withdraw |
| Changes through | Assignment or controlled setters | Method execution |
| Validation | Attribute constraints | Input and business-rule validation |
| Main concern | Data integrity | Behaviour correctness |
| Security concern | Unauthorized data access | Unauthorized operations |

An attribute can describe an object's current state, while a method can validate and change that state.

For example, `balance` represents the current financial position, while `withdraw()` enforces the conditions under which that balance may decrease.

## 17. Performance and Security Considerations

### Performance

- Use efficient collection structures for frequent lookups.
- Avoid repeatedly copying large transaction histories.
- Use indexes for database lookup and reporting operations.
- Keep frequently accessed attributes readily available.
- Use immutable data objects where appropriate.
- Avoid unnecessary object creation.
- Use appropriate locking only where shared mutable state requires it.
- Prefer database-side aggregation for large datasets.

The transaction-history implementation uses append-oriented collections. For large financial workloads, a database-backed history with pagination is preferable to loading every transaction into memory.

### Security

- Restrict direct access to sensitive attributes.
- Validate all external inputs.
- Apply authorization before sensitive methods execute.
- Avoid exposing account credentials or confidential identifiers.
- Use parameterized database operations.
- Restrict database routine execution through role-based privileges.
- Preserve financial transaction history.
- Enforce transactional integrity.
- Use audit records for important state changes.

Private attributes improve encapsulation, but they do not independently provide authentication, authorization, encryption, or protection against privileged access.

## 18. Edge Cases and Limitations

The implementations deliberately demonstrate several failure conditions.

| Scenario | Expected behaviour |
|---|---|
| Empty account number | Reject initialization |
| Negative opening balance | Reject initialization |
| Negative deposit | Reject transaction |
| Zero withdrawal | Reject transaction |
| Excessive withdrawal | Reject for insufficient funds |
| Invalid interest rate | Reject initialization |
| Transfer to the same account | Reject transfer |
| Frozen account transaction | Reject operation |
| Closing an account with funds | Reject closure |
| Duplicate account registration | Reject duplicate identity |
| Excessive monetary precision | Reject monetary value |
| Missing destination account | Reject transfer |

The implementations are educational domain models rather than complete banking platforms.

They do not provide distributed transaction coordination, payment-network integration, regulatory compliance, production authentication, external fraud detection, or a complete audit and reconciliation architecture.

The JavaScript, Python, C++, and Java examples maintain their operational state in memory. PostgreSQL provides persistent relational storage, but production deployment would also require carefully configured database roles and transaction permissions.

## 19. Execution and Verification

| File | Runtime or execution environment |
|---|---|
| Python | Python 3.10 or later |
| JavaScript | Node.js 18 or later |
| C++17 | C++ compiler with C++17 support |
| Java | Java 17 |
| PostgreSQL | PostgreSQL 15 or later |

The Python script can be executed directly.

The JavaScript implementation uses Node.js built-in modules and does not require npm dependencies.

The C++ implementation requires the C++17 language standard.

The Java implementation uses Java 17 language features, including records.

The SQL implementation creates its schema, domain tables, functions, procedures, triggers, indexes, sample data, and reporting queries. It uses PostgreSQL's `gen_random_uuid()` function.

The Python, JavaScript, C++, and Java programs include executable assertions or validation checks to verify the expected account balances, transaction history, and state transitions.

The six implementations demonstrate how attributes represent object state and how methods control object behaviour across procedural, class-based, event-driven, compiled, enterprise, and relational database environments.
