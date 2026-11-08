# Creating Your Own Modules

## 1. Introduction

A software module is an independently organized unit of functionality that exposes a defined interface and hides its internal implementation.

Modules allow applications to separate responsibilities, reduce code duplication, control dependencies, and support independent testing and maintenance.

Creating a module involves more than moving code into another file. A properly designed module has:

- A clearly defined responsibility.
- A stable public interface.
- Encapsulated internal implementation.
- Explicit dependencies.
- Configuration and validation rules.
- A documented lifecycle.
- Controlled permissions.
- Defined error-handling behavior.
- Tests that verify its contract.

The five implementations in this repository demonstrate different approaches to designing, registering, managing, and executing reusable modules.

## 2. Fundamental Module Concepts

### 2.1 Module

A module is a logical unit containing related functionality.

Examples include:

| Module | Responsibility |
|---|---|
| Analytics | Numerical calculations and statistical operations |
| Reporting | Generation of structured reports |
| Authentication | Identity verification and access management |
| Notification | Email and application notifications |
| Database Access | Data retrieval and persistence |
| Configuration | Application configuration management |
| Logging | Application event recording |

Each module should have a focused responsibility rather than combining unrelated operations.

### 2.2 Modularity

Modularity is the organization of a software system into smaller components with explicit responsibilities and interfaces.

A modular application can be represented as:

Application
- Module Registry
- Analytics Module
- Reporting Module
- Configuration Module
- Notification Module
- Shared Interfaces

The application interacts with modules through their exposed contracts instead of depending directly on their internal implementation.

### 2.3 Encapsulation

Encapsulation restricts direct access to implementation details.

A module may expose:

- Public functions.
- Public classes.
- Interfaces.
- Configuration options.
- Documented data structures.

Internal variables, helper functions, and implementation-specific algorithms remain hidden.

This reduces accidental coupling and makes internal changes less likely to break dependent components.

### 2.4 Cohesion and Coupling

**Cohesion** measures how closely related the responsibilities inside a module are.

High cohesion means that a module concentrates on a clearly defined purpose.

**Coupling** describes the degree of dependency between modules.

Low coupling allows individual modules to change with fewer effects on other parts of the application.

A good modular design generally aims for high cohesion and controlled coupling.

## 3. Module Interfaces and Contracts

An interface specifies how another component can interact with a module.

A typical module contract contains:

| Contract element | Purpose |
|---|---|
| Initialization | Prepare internal state |
| Configuration | Receive operational settings |
| Execution | Perform the module's main responsibility |
| Validation | Reject invalid input |
| Output | Return structured results |
| Error handling | Communicate failure conditions |
| Shutdown | Release resources |

A module interface should specify input types, expected output, permitted operations, and possible errors.

### Public and private interfaces

A public interface is intended for use by other modules.

A private interface supports internal implementation.

The distinction is important because changing a public contract can affect dependent applications, whereas changing a private helper normally does not require dependent modules to change.

### Interface versioning

An interface should have its own version when independently evolving contracts are necessary.

For example:

| Interface | Version | Contract |
|---|---|---|
| calculate | 1.0.0 | Accept numerical values and return an aggregate |
| generate_report | 1.0.0 | Accept records and return a structured report |
| calculate | 2.0.0 | Revised input and output contract |

Module versioning and interface versioning are related but not identical.

A module may introduce internal improvements without changing its public interface.

## 4. Creating Modules in Python

Python supports several approaches to modular development.

### 4.1 Python files as modules

A Python file can be imported as a module.

The filename generally determines its import name.

For example, a file named `analytics.py` can expose functions and classes to other Python files through an import statement.

### 4.2 Packages

A package groups related modules in a directory.

A typical structure is:

project/
- main.py
- analytics/
  - __init__.py
  - calculations.py
  - statistics.py
  - validation.py
- reporting/
  - __init__.py
  - generators.py
  - formatting.py
- tests/
  - test_analytics.py
  - test_reporting.py

The `__init__.py` file supports package initialization and can define the package's public interface.

Modern Python also supports namespace packages without `__init__.py`.

### 4.3 Module imports

Python provides several import mechanisms:

| Mechanism | Purpose |
|---|---|
| `import module` | Import a module |
| `from module import function` | Import a specific object |
| `import package.module` | Import a nested module |
| `importlib` | Programmatic module loading |
| Relative imports | Import within a package |

Imports should be designed to avoid unnecessary circular dependencies.

### 4.4 Python implementation

The Python implementation defines a reusable module management architecture.

Its primary components are:

- `ModuleMetadata`: Describes module identity, version, ownership, permissions, and dependencies.
- `ModuleDependency`: Defines minimum compatible dependency versions.
- `ModuleInterface`: Defines the expected implementation contract.
- `ModuleRecord`: Maintains runtime state and execution statistics.
- `ModuleManager`: Coordinates registration, dependency validation, loading, activation, execution, and shutdown.

The calculation module implements numerical operations.

The reporting module demonstrates a separate responsibility.

The reporting module declares a dependency on the calculation module.

The manager validates this dependency before activation.

### 4.5 Dynamic imports

Python's `importlib.util` provides programmatic loading of source files.

The implementation includes a dynamic loading function that:

1. Resolves the requested file path.
2. Verifies that the file exists.
3. Constructs a module specification.
4. Creates a module object.
5. Executes the module.

Dynamic imports execute arbitrary Python code.

A file extension check and path validation do not make untrusted code safe.

Production systems should restrict module sources, validate ownership, review dependencies, and isolate untrusted execution.

## 5. Creating Modules in JavaScript

JavaScript provides native module support through ECMAScript modules.

### 5.1 ECMAScript modules

An ES module can export reusable functionality.

The principal mechanisms are:

| Mechanism | Purpose |
|---|---|
| `export` | Expose functionality |
| `export default` | Define a default export |
| `import` | Consume another module |
| Named imports | Import specific exports |
| Dynamic `import()` | Load modules at runtime |

For example, a module may export an analytics class while keeping its internal helper functions private.

### 5.2 Named and default exports

Named exports are useful when a module exposes multiple related functions or classes.

Default exports are useful when a module has one primary implementation.

A project should choose a consistent export strategy.

### 5.3 Module resolution

Node.js supports ES modules through `.mjs` files or package configuration specifying module type.

The implementation uses a `.mjs` runtime module loader.

It resolves a trusted local path and imports the module dynamically.

Dynamic imports are not a security sandbox.

### 5.4 Event-driven module management

The JavaScript implementation uses Node.js `EventEmitter`.

The registry emits lifecycle events such as:

- `module:registered`
- `module:activated`
- `module:failed`
- `module:disabled`
- `execution:started`
- `execution:completed`
- `execution:failed`

This separates module execution from operational monitoring.

For example, a monitoring component can listen for execution failures without modifying the analytics implementation.

### 5.5 Asynchronous execution

JavaScript modules frequently perform asynchronous operations.

The implementation uses `async` and `await` to support asynchronous initialization, execution, and shutdown.

Promises provide a mechanism for representing operations that complete in the future.

The registry also maintains execution identifiers, duration measurements, and result hashes.

## 6. Creating Modules in C++17

C++17 supports modular software organization through conventional source files, headers, namespaces, interfaces, and libraries.

An important distinction is that standardized C++ language modules were not introduced in C++17.

The implementation therefore uses conventional C++17 techniques rather than C++20 module declarations.

### 6.1 Header and implementation separation

A typical C++ module has:

- A header file containing public declarations.
- An implementation file containing definitions.
- A set of private helper functions.
- A defined namespace.

A typical project structure is:

project/
- include/
  - analytics.hpp
  - reporting.hpp
  - module_registry.hpp
- src/
  - analytics.cpp
  - reporting.cpp
  - module_registry.cpp
  - main.cpp
- tests/
  - module_tests.cpp

Header guards or `#pragma once` prevent repeated header inclusion.

### 6.2 Namespaces

Namespaces prevent naming collisions and group related functionality.

For example, `module_system` contains the module registry, metadata, interfaces, and lifecycle types.

### 6.3 Abstract interfaces

The C++ implementation defines an abstract `Module` interface.

Implementations must provide:

- `initialize()`
- `execute()`
- `shutdown()`

Concrete implementations use inheritance and polymorphism.

The registry stores implementations using `std::unique_ptr`.

This establishes clear ownership and prevents accidental copying of uniquely owned module instances.

### 6.4 STL data structures

The implementation uses:

| Structure | Purpose |
|---|---|
| `std::map` | Module lookup |
| `std::set` | Permission and dependency tracking |
| `std::vector` | Dependency ordering and input values |
| `std::unique_ptr` | Exclusive implementation ownership |
| `std::unique_ptr` with virtual destructors | Safe polymorphic destruction |
| STL algorithms | Minimum, maximum, and aggregation |

### 6.5 Dependency resolution

A depth-first search resolves dependencies.

Two sets distinguish visited nodes from nodes currently being explored.

Encountering a currently active node indicates a dependency cycle.

The resulting ordering ensures that dependencies are processed before dependent modules.

For a graph containing V modules and E dependency relationships, dependency resolution requires O(V + E) time.

## 7. Creating Modules in Java 17

Java provides packages, interfaces, classes, records, and the Java Platform Module System.

### 7.1 Packages

Packages group related classes and establish a namespace.

An enterprise project might use:

- `com.company.analytics`
- `com.company.reporting`
- `com.company.platform`
- `com.company.configuration`
- `com.company.security`

Packages help organize implementation responsibilities and control package-level access.

### 7.2 Interfaces

Java interfaces define contracts that independent implementations can satisfy.

The enterprise implementation defines `EnterpriseModule` with initialization, execution, and shutdown operations.

Concrete modules implement the interface independently.

### 7.3 Records

Java 17 records provide concise data-oriented types.

The implementation uses records for:

- `Version`
- `Dependency`
- `ModuleMetadata`
- `ModuleConfiguration`
- `AnalyticsRequest`
- `ModuleResult`
- `ExecutionAudit`

Records reduce boilerplate and make data structures easier to reason about.

Defensive copying is used for collection components.

### 7.4 Java Platform Module System

The Java Platform Module System, introduced in Java 9, provides explicit module declarations.

A JPMS module normally contains a `module-info.java` descriptor.

The descriptor can declare:

- `requires`: Modules on which the current module depends.
- `exports`: Packages exposed to other modules.
- `opens`: Packages available for reflective access.
- `uses`: Services consumed.
- `provides`: Service implementations supplied.

A single-file Java program cannot independently demonstrate a complete multi-file JPMS deployment.

The Java implementation therefore models enterprise module behavior using packages, interfaces, records, and service classes.

### 7.5 Asynchronous services

The Java implementation uses `CompletableFuture` for asynchronous execution.

It also uses `AtomicLong` for thread-safe execution counting and synchronized audit-log access.

These mechanisms support concurrent execution scenarios.

A production implementation must also define thread-safety requirements for each module's internal state.

## 8. Module Dependencies and Version Management

A dependency exists when one module requires another module's functionality.

Example:

Analytics Module
    |
    v
Reporting Module
    |
    v
Business Application

In this relationship, reporting depends on analytics.

A dependency declaration should specify:

- Required module.
- Minimum supported version.
- Required interface.
- Configuration expectations.
- Failure behavior.

### 8.1 Semantic versioning

The examples use three-part versions:

`MAJOR.MINOR.PATCH`

| Component | Meaning |
|---|---|
| MAJOR | Incompatible public interface changes |
| MINOR | Backward-compatible functionality |
| PATCH | Backward-compatible corrections |

The implementations compare numeric version components.

They demonstrate minimum-version compatibility rather than the full semantic-versioning range specification.

### 8.2 Dependency graphs

A dependency graph represents modules as vertices and dependency relationships as directed edges.

Example:

Analytics
  |
  v
Reporting
  |
  v
Application

The actual direction of an edge should be documented consistently.

A valid activation sequence must initialize dependencies before dependent modules.

### 8.3 Circular dependencies

A circular dependency occurs when a dependency chain eventually returns to an earlier module.

Example:

Module A -> Module B
Module B -> Module C
Module C -> Module A

Such a structure complicates initialization, testing, and lifecycle management.

The Python, JavaScript, C++, and Java implementations use graph traversal to identify circular dependencies.

The PostgreSQL implementation also prevents cycles when inserting dependency relationships.

## 9. Module Lifecycle Management

A module has a lifecycle that describes its operational condition.

The implementations use the following conceptual states:

| State | Meaning |
|---|---|
| Registered | Module metadata and implementation are known |
| Initialized | Configuration and internal resources are prepared |
| Active | Module is available for execution |
| Failed | An initialization or operational failure occurred |
| Disabled | Module is unavailable for execution |

Typical lifecycle:

Registered
    |
    v
Initialized
    |
    v
Active
    |
    +----> Failed
    |
    +----> Disabled

A disabled module should not execute.

A module should not be shut down while active dependents still require it.

The implementations include lifecycle checks and dependency-aware deactivation.

The database additionally enforces permitted state transitions through a trigger.

## 10. Configuration Management

Modules frequently require configuration values.

Examples include:

- Numerical precision.
- Maximum input size.
- Connection settings.
- Report formats.
- Logging levels.
- Feature flags.

Configuration should be validated during initialization.

The examples demonstrate configuration objects or dictionaries rather than hardcoding every operational setting inside a module.

Sensitive configuration values such as database passwords, access tokens, and encryption keys should be stored in an appropriate secret-management system rather than committed to source code.

Configuration changes should be versioned and audited when they affect operational behavior.

## 11. Permission Management and Security

A module should receive only the permissions necessary for its responsibility.

This follows the principle of least privilege.

The implementations define capabilities such as:

| Permission | Intended operation |
|---|---|
| `read_data` | Access authorized records |
| `write_data` | Modify permitted records |
| `calculate` | Execute numerical operations |
| `export_data` | Produce authorized exports |
| `manage_configuration` | Change module configuration |

Registration validates declared permissions.

Execution validates caller permissions against module requirements.

A production authorization system should distinguish between:

- Permissions requested by a module.
- Permissions approved by an administrator.
- Permissions assigned to a caller.
- Permissions actually enforced by the underlying resource.

A registry-level permission check alone does not provide operating-system or process-level isolation.

## 12. PostgreSQL Module Management

The SQL implementation provides a relational representation of the module architecture.

### 12.1 Database entities

| Table | Responsibility |
|---|---|
| `modules` | Module identity, version, owner, and lifecycle |
| `module_interfaces` | Public interface contracts |
| `permissions` | Available capabilities |
| `module_permissions` | Permission assignments |
| `module_dependencies` | Dependency relationships |
| `module_configurations` | Versioned configuration records |
| `module_executions` | Execution history and results |
| `module_audit_log` | Lifecycle and administrative events |

### 12.2 Referential integrity

Primary keys identify individual records.

Foreign keys connect dependencies, permissions, interfaces, configurations, executions, and audit entries to their owning modules.

Unique constraints prevent duplicate module names, interface names within a module, and duplicate dependency relationships.

Check constraints validate names, versions, configuration formats, and execution states.

### 12.3 Recursive queries

Recursive common table expressions support hierarchical dependency analysis.

The dependency hierarchy query traverses dependency relationships and records their depth.

The cycle-prevention trigger rejects relationships that would create circular dependencies.

### 12.4 Lifecycle procedures

The `activate_module` procedure:

1. Locks the target module.
2. Checks whether it exists.
3. Verifies that it is enabled.
4. Validates dependency states.
5. Checks dependency versions.
6. Initializes the module when required.
7. Activates the module.
8. Records an audit event.

The procedure runs within the caller's transaction.

### 12.5 Execution tracking

Each execution has a UUID, requesting identity, input payload, output payload, status, timestamps, and optional failure information.

The execution functions prevent an already finalized execution from being completed again.

The reporting views aggregate successful executions, failures, and execution duration.

### 12.6 Indexing

Indexes support frequently used access patterns:

- Module lifecycle and enabled status.
- Module ownership.
- Dependency lookups.
- Configuration retrieval.
- Execution history by module and date.
- Failed execution investigation.
- Audit history.

Indexes improve relevant reads but introduce additional storage and write-maintenance costs.

## 13. Error Handling and Failure Management

A reusable module should fail predictably.

The implementations cover several failure conditions:

| Failure | Expected handling |
|---|---|
| Duplicate registration | Reject registration |
| Invalid module metadata | Reject registration |
| Missing dependency | Prevent activation |
| Incompatible version | Prevent activation |
| Circular dependency | Reject dependency resolution |
| Invalid configuration | Reject initialization |
| Invalid input | Reject execution |
| Missing permission | Reject execution |
| Initialization exception | Mark module as failed |
| Execution exception | Record error information |
| Active dependent exists | Prevent shutdown |

Failures should include sufficient diagnostic information without exposing passwords, tokens, or other sensitive information.

A production implementation should also define retry policies, timeout handling, resource cleanup, and recovery procedures.

## 14. Testing Your Own Modules

Module testing should cover both implementation behavior and contract compatibility.

### Unit testing

Tests verify individual module operations.

Examples:

- Sum numerical values.
- Calculate averages.
- Reject empty inputs.
- Reject unsupported operations.
- Validate configuration values.

### Integration testing

Integration tests verify relationships between modules.

Examples:

- Reporting requires analytics.
- An incompatible dependency prevents activation.
- A disabled dependency prevents dependent activation.
- Module shutdown respects dependency relationships.

### Contract testing

Contract tests verify that a module conforms to its published interface.

They should check input requirements, output structure, error behavior, and version compatibility.

### Failure testing

Failure testing examines behavior when dependencies are missing, initialization fails, permissions are insufficient, or execution produces an exception.

The Python, C++, and Java examples include executable assertions or validation tests. The JavaScript implementation demonstrates expected permission and execution failures.

The SQL implementation demonstrates database constraints, lifecycle enforcement, dependency validation, and execution failure recording.

## 15. Performance and Scalability

Modular design introduces additional management and dependency-resolution costs.

| Operation | Typical complexity |
|---|---|
| Python dictionary module lookup | Average O(1) |
| JavaScript Map lookup | Average O(1) |
| C++ ordered map lookup | O(log V) |
| Java HashMap lookup | Average O(1) |
| Dependency graph traversal | O(V + E) |
| Permission set membership | Average O(1) |
| Module inventory | O(V) |
| Execution history retrieval | Depends on indexing and result size |

Here, V represents modules and E represents dependency relationships.

For large module platforms, useful optimizations include:

- Caching validated dependency orders.
- Avoiding unnecessary repeated initialization.
- Limiting execution payload sizes.
- Using bounded asynchronous execution.
- Separating module metadata from runtime state.
- Indexing frequently queried database fields.
- Applying connection pooling where database modules are involved.

Caches must be invalidated when module versions, dependencies, or lifecycle states change.

## 16. Implementation Comparison

| Dimension | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Primary approach | Module manager | Event-driven registry | Polymorphic interfaces | Enterprise service architecture | Relational module catalog |
| Encapsulation | Classes and conventions | Classes and private fields | Classes and namespaces | Packages and private members | Schemas and constraints |
| Dependencies | Dependency objects | Dependency graph | DFS traversal | DFS traversal | Foreign keys and recursive queries |
| Lifecycle | Enum-based states | Event-driven states | Enum-based states | Enum-based states | Enum and trigger |
| Execution | Direct calls | Async functions | Virtual methods | CompletableFuture | Execution records |
| Permissions | Capability sets | Permission sets | Permission sets | Permission enums | Permission relations |
| Versioning | Semantic version comparison | Semantic version comparison | Structured version type | Comparable record | Version columns |

## 17. Design Decisions and Limitations

### 17.1 Single-file implementations

The source files are deliberately self-contained for direct execution.

Real projects should separate interfaces, implementations, tests, configuration, and documentation into appropriate files and packages.

The Java implementation demonstrates enterprise module management but does not replace a complete multi-file JPMS deployment.

The C++ implementation uses C++17-compatible namespace and interface techniques rather than C++20 language modules.

### 17.2 Dependency compatibility

The examples implement minimum-version checks.

A production package manager may require richer version constraints, including compatible ranges, prerelease versions, optional dependencies, and conflict resolution.

### 17.3 Runtime isolation

Dynamic imports do not isolate untrusted code.

Modules that execute third-party or externally supplied code require stronger isolation, such as separate processes, containers, restricted operating-system permissions, and resource limits.

### 17.4 Database and application consistency

The PostgreSQL implementation stores module metadata and lifecycle information.

It does not automatically execute the corresponding Python, JavaScript, C++, or Java implementations.

A production deployment needs an application service that coordinates database transactions with actual module initialization and execution.

Distributed lifecycle operations require careful handling of partial failures and retries.

### 17.5 Concurrency

Concurrent execution introduces shared-state concerns.

Module implementations should define whether they are thread-safe, whether initialization can occur concurrently, and whether shutdown must wait for active executions.

The JavaScript and Java implementations provide asynchronous execution examples, but production concurrency limits and cancellation policies must be explicitly designed.

## 18. Practical Module Development Workflow

A disciplined module development process follows this sequence:

1. Identify a cohesive responsibility.
2. Define the public interface.
3. Determine private implementation details.
4. Define input and output contracts.
5. Identify dependencies.
6. Establish compatible versions.
7. Define required permissions.
8. Implement initialization and shutdown.
9. Validate configuration and inputs.
10. Implement error handling.
11. Write unit and integration tests.
12. Register the module.
13. Validate dependency compatibility.
14. Activate the module.
15. Monitor execution and failures.
16. Document interface changes.

This process produces modules that can be independently understood, tested, maintained, and reused.
