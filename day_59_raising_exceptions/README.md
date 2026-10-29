# Raising Exceptions

## Scope

This project models exception raising as an explicit control-flow mechanism for detecting invalid state, rejecting unsafe input, translating low-level failures into domain failures, and preserving useful failure information across application layers.

The five implementations use the same broad progression while keeping their engineering approaches distinct:

| Implementation | Primary focus |
|---|---|
| Python | Domain exceptions, validation, exception chaining, cleanup, and assertions |
| JavaScript | Error subclasses, asynchronous propagation, `cause`, and runtime validation |
| C++17 | Exception hierarchies, RAII cleanup, standard exceptions, and translation |
| Java 17 | Checked exceptions, domain modeling, try-with-resources, and service boundaries |
| PostgreSQL | `RAISE EXCEPTION`, SQLSTATE, PL/pgSQL exception handling, constraints, triggers, and transactional rollback |

The central distinction is between detecting a failure and raising an exception. A condition is detected by application logic or infrastructure. Raising an exception transfers control to an appropriate handler and prevents the current operation from silently continuing with invalid state.

## Core Exception Model

The implementations distinguish several failure categories:

- Validation failures indicate invalid input or domain state.
- Configuration failures indicate missing or unusable application configuration.
- Storage failures represent persistence or filesystem problems.
- Built-in exceptions represent failures already covered by the runtime, such as division by zero or invalid numeric conversion.
- Chained exceptions preserve the lower-level cause while exposing a higher-level domain meaning.

A useful flow is:

    Input
      |
      v
    Validation
      |
      +---- invalid ----> raise exception
      |
      v
    Domain operation
      |
      +---- failure ----> translate or propagate
      |
      v
    Persistence
      |
      +---- infrastructure failure ----> domain exception
      |
      v
    Success

An exception should be raised at the point where the program has enough information to describe the failure accurately. Handling should occur at a boundary that can make a meaningful decision about recovery, reporting, retrying, or termination.

## Python Implementation

The Python program uses custom exception classes derived from `Exception`:

- `ApplicationError` provides the common application-level type.
- `ValidationError` represents invalid user input.
- `ConfigurationError` represents missing configuration.
- `StorageError` represents filesystem persistence failures.

`validate_user()` raises `ValidationError` before a user reaches persistence. This keeps invalid state outside the repository layer.

The repository catches `OSError` and raises `StorageError` with `raise ... from exc`. The resulting exception chain preserves the operating-system failure as `__cause__` while giving callers a stable domain-level exception.

`parse_integer()` demonstrates exception translation. A `ValueError` produced by `int()` becomes a `ValidationError`, but the original exception remains available through exception chaining.

The script also demonstrates:

- explicit `raise`
- selective `except`
- bare `raise` for propagation
- `raise ... from`
- `finally`
- context-manager cleanup
- assertions for executable validation
- dataclasses for domain values
- enums for severity classification
- filesystem failure handling

The implementation intentionally does not catch every exception indiscriminately. Unexpected programming errors should not be converted into ordinary validation failures because doing so can hide defects.

## JavaScript Implementation

The JavaScript program defines `ApplicationError` and specialized subclasses for validation, configuration, and storage failures.

JavaScript's `Error` supports a `cause` option. The repository uses this capability when converting a filesystem error into a `StorageError`:

    low-level filesystem error
              |
              v
        StorageError
              |
              +--> cause

This preserves the original infrastructure error while allowing application code to reason about a stable domain type.

The implementation also uses asynchronous exception propagation. `UserRepository.save()` returns a Promise, and `processUser()` uses `await`. An exception raised inside the asynchronous operation becomes a rejected Promise and is handled by `try`/`catch` around `await`.

The JavaScript version demonstrates:

- custom `Error` subclasses
- explicit `throw`
- `try`/`catch`
- `cause`
- Promise rejection through asynchronous `throw`
- optional chaining while inspecting causes
- runtime type validation
- explicit process-level handling for unhandled failures

The file avoids external npm packages and uses Node.js built-in filesystem APIs.

## C++17 Implementation

The C++ program models application failures using an exception hierarchy derived from `std::runtime_error`.

`ApplicationError` provides the domain boundary. `ValidationError`, `ConfigurationError`, and `StorageError` specialize the hierarchy so callers can catch a specific category or the common application type.

The repository uses `std::ofstream` and raises `StorageError` when opening or writing fails.

The C++ implementation also demonstrates an important language-specific behavior: stack unwinding.

`ResourceGuard` has a destructor that executes automatically when an exception leaves its scope. This is the basis of RAII. Cleanup is therefore tied to object lifetime rather than a separate `finally` construct.

The implementation uses standard exceptions for arithmetic failures:

- `std::domain_error` is used when division by zero is detected.
- `std::invalid_argument` and `std::out_of_range` from `std::stoi` are translated into `ValidationError`.

This separation gives callers both standard-library compatibility and application-specific failure categories.

## Java 17 Implementation

The Java implementation uses checked domain exceptions:

- `ApplicationException`
- `ValidationException`
- `ConfigurationException`
- `StorageException`

Methods that can raise checked application failures explicitly declare them with `throws`. This makes part of the failure contract visible at compile time.

The `User` record provides an immutable domain representation. `UserRepository` is an interface, while `FileUserRepository` implements persistence. This separates domain processing from the concrete storage mechanism.

`processUser()` first validates the user and then invokes the repository. It declares the checked failures that callers must handle.

The Java implementation also demonstrates exception translation. `IOException` from filesystem operations is wrapped in `StorageException` while preserving the original exception as the cause.

Try-with-resources provides deterministic cleanup for the writer. If an exception occurs while the resource is open, Java closes the resource before control reaches the catch block.

The program demonstrates multi-catch handling where several exception types share the same recovery path.

## PostgreSQL Implementation

The PostgreSQL implementation treats exceptions as part of database workflow control.

The schema contains:

- `users`
- `application_errors`
- `user_operations`

The tables distinguish the business object, recorded failure, and operation state rather than storing all information in a single error table.

The `severity` enum provides explicit classification.

Database constraints reject invalid state before it can be committed. Examples include:

- non-empty user names
- basic email structure
- valid operation states
- completion timestamps for completed operations
- failure references for failed operations

The `parse_positive_integer()` function demonstrates explicit PL/pgSQL exception handling. A failed cast is caught and converted into an application-specific database exception with an appropriate SQLSTATE.

The `create_user()` function handles `unique_violation` and raises a clearer application-level error.

The `record_failure()` procedure records the error and transitions the operation to `failed`. The trigger then prevents invalid state transitions such as reopening a successful operation.

The transaction demonstration shows that an exception causes the current transaction to be rolled back when it is not handled within that transaction.

## Raising Versus Handling

Raising and handling are different responsibilities.

Raising answers:

> What condition makes the current operation invalid?

Handling answers:

> What can this layer meaningfully do about that failure?

A low-level storage component should generally not decide whether a user-facing request succeeds. It should expose a meaningful failure. A higher-level service can then decide whether to retry, report, compensate, or terminate.

A useful layering model is:

    Validation layer
          |
          | raises ValidationError
          v
    Domain service
          |
          | propagates or translates
          v
    Storage layer
          |
          | raises StorageError
          v
    Application boundary
          |
          +---- report
          +---- retry
          +---- reject
          +---- terminate

Catching an exception only to immediately raise the same exception without adding context is usually unnecessary. Python's bare `raise`, Java's exception propagation, JavaScript's natural Promise propagation, and C++'s absence of a matching handler already preserve the failure.

## Exception Translation

Exception translation is appropriate when an abstraction boundary needs a domain-specific vocabulary.

For example:

    File access failure
          |
          v
    IOException / OSError / filesystem error
          |
          v
    StorageException / StorageError
          |
          v
    Application boundary

The translated exception should preserve the original cause where the language supports it.

This prevents infrastructure-specific details from leaking through every application layer while keeping diagnostic information available.

## Validation and Failure Timing

Validation should occur before expensive or irreversible operations.

For a user creation workflow:

1. Validate the identifier.
2. Validate the name.
3. Validate the email.
4. Construct the domain object.
5. Persist the object.
6. Report persistence failure separately from validation failure.

This creates clearer failure semantics than allowing malformed data to reach persistence and fail through an unrelated database or filesystem error.

Validation does not eliminate the need for lower-level checks. Database constraints, filesystem checks, and concurrency controls remain necessary because application state can change between validation and persistence.

## Exception Chaining

Exception chaining preserves causality.

A useful chain is:

    ValidationError
        caused by
    ValueError

or:

    StorageError
        caused by
    OSError

The higher-level exception provides stable application semantics. The cause provides diagnostic detail.

Without chaining, translating an exception can erase information that is valuable during debugging and incident analysis.

## State and Failure Handling

The PostgreSQL workflow explicitly separates operation states:

| State | Meaning |
|---|---|
| `started` | Operation is currently active |
| `succeeded` | Operation completed successfully |
| `failed` | Operation ended because of a recorded failure |

The trigger prevents invalid transitions such as:

    succeeded -> started
    failed -> started

A failed operation must reference an error record. A successful operation cannot reference a failure.

This illustrates an important principle: exception handling is not only about messages. In stateful systems, failure handling must also preserve valid state.

## Edge Cases

The implementations cover several failure conditions:

- zero or negative identifiers
- blank names
- malformed email values
- invalid numeric input
- division by zero
- missing configuration
- filesystem open failures
- filesystem write failures
- duplicate database values
- invalid database casts
- invalid operation state transitions
- unhandled top-level failures
- cleanup after exceptions
- preservation of original failure causes

An exception should not be raised merely because an unusual input exists. It should represent a condition under which the current operation cannot safely continue.

## Performance Considerations

Raising an exception is generally more expensive than ordinary conditional branching because the runtime must construct exception state and unwind control flow.

Exceptions should therefore represent exceptional control flow rather than routine expected outcomes.

For frequently occurring validation checks, direct validation before entering expensive operations is preferable. Once a failure is genuinely exceptional, raising an exception gives the caller a clean path through multiple abstraction layers.

The database implementation uses indexes on error timestamps and user references because those fields support operational reporting and failure lookup. It does not index every column because unnecessary indexes increase storage and write costs.

## Security Considerations

Exception messages should not expose secrets.

Potentially sensitive values such as:

- passwords
- access tokens
- connection credentials
- session identifiers
- private keys

should not be inserted into exception messages or logs.

The examples use controlled values and avoid credentials.

Exception handling should also avoid broad catches that silently suppress security-relevant failures. A permission failure, authentication failure, or integrity violation may require different treatment from ordinary validation.

Database exceptions should be recorded with enough context to diagnose the operation while avoiding sensitive payloads.

## Failure-Handling Design Rules

A robust exception design follows several rules:

- Raise when the current operation cannot safely continue.
- Use specific exception types for distinct failure categories.
- Preserve the original cause when translating failures.
- Catch exceptions at a layer capable of making a meaningful decision.
- Do not silently suppress unexpected failures.
- Do not use exceptions as routine loop control.
- Validate before irreversible operations.
- Keep error messages useful but free of secrets.
- Maintain valid state when an operation fails.
- Use database constraints for rules that must hold regardless of application behavior.
- Ensure cleanup occurs during failure paths.
- Keep exception hierarchies small and meaningful.

## Practical Relationship Between the Implementations

The implementations intentionally approach the same subject differently.

Python emphasizes concise exception hierarchies, chaining, context-managed cleanup, and assertions.

JavaScript emphasizes dynamic validation, `Error` subclasses, asynchronous propagation, and Promise-based failure handling.

C++17 emphasizes typed standard exceptions, deterministic destruction, RAII, and stack unwinding.

Java 17 emphasizes explicit checked failure contracts, immutable records, repository interfaces, exception translation, and try-with-resources.

PostgreSQL moves exception handling into the database boundary, combining explicit `RAISE EXCEPTION` statements with SQLSTATE values, constraints, triggers, stored routines, and transactions.

The common model is:

    Detect invalid condition
            |
            v
    Raise typed failure
            |
            v
    Propagate through layers
            |
            v
    Handle at an appropriate boundary
            |
            v
    Preserve valid state
            |
            v
    Report, recover, retry, or terminate

This model keeps failure behavior explicit while allowing each implementation environment to use its native exception mechanisms.
