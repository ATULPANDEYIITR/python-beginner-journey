# Python Inheritance: Object-Oriented Programming and Enterprise Payroll

## 1. Introduction

Inheritance is an object-oriented programming mechanism that allows a class to acquire attributes and methods from another class.

It establishes relationships between general classes and specialized classes.

In Python, inheritance supports:

- Code reuse.
- Method overriding.
- Runtime polymorphism.
- Hierarchical domain modeling.
- Abstract interfaces.
- Multiple inheritance.
- Cooperative method execution.
- Extensible application architecture.

The implementations use an employee payroll system to demonstrate inheritance across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The central domain relationship is:

Employee
|
+-- PermanentEmployee
|   |
|   +-- SeniorEmployee
|       |
|       +-- DepartmentManager
|
+-- ContractEmployee
|
+-- InternEmployee

A specialized employee inherits the common employee identity, department, and employment status while implementing its own salary calculation.

## 2. Fundamental Concepts of Python Inheritance

### 2.1 Parent and child classes

A parent class, also called a base or superclass, defines common attributes and behavior.

A child class, also called a derived class or subclass, inherits that behavior.

Python uses the following syntax:

`class Child(Parent):`

The child receives accessible methods and attributes from the parent.

The `Employee` class provides common employee information, validation, status management, and an abstract salary-calculation contract.

The specialized employee classes inherit these responsibilities rather than implementing them repeatedly.

### 2.2 Single inheritance

Single inheritance occurs when one child class inherits from one parent class.

Example relationship:

`Employee → PermanentEmployee`

`PermanentEmployee` inherits the employee identity, department, and employment status.

It introduces:

- Monthly salary.
- Annual bonus.
- Permanent employment salary calculation.

The monthly salary is combined with one-twelfth of the annual bonus to calculate monthly gross compensation.

### 2.3 Multilevel inheritance

Multilevel inheritance establishes a chain of inheritance.

Example:

`Employee → PermanentEmployee → SeniorEmployee`

`SeniorEmployee` inherits the functionality of both `PermanentEmployee` and `Employee`.

It introduces a leadership allowance.

The implementation uses `super()` to reuse the parent salary calculation before applying the additional allowance.

This avoids unnecessarily duplicating the permanent employee calculation.

### 2.4 Hierarchical inheritance

Hierarchical inheritance occurs when multiple child classes inherit from the same parent.

Example:

- Employee → PermanentEmployee
- Employee → ContractEmployee
- Employee → InternEmployee

All three classes share employee identity and employment status.

Their compensation rules differ:

| Employee type | Compensation mechanism |
|---|---|
| Permanent | Monthly salary and annual bonus |
| Contract | Hourly rate multiplied by hours |
| Intern | Fixed monthly stipend |

This structure provides a common employee interface without requiring identical implementations.

### 2.5 Multiple inheritance

Python allows a class to inherit from multiple parent classes.

Example:

`class TaxablePermanentEmployee(TaxableMixin, AuditableMixin, PermanentEmployee):`

This combines:

- Permanent employee compensation.
- Tax calculation.
- Audit functionality.

The mixins provide reusable behavior without requiring every employee class to inherit from a large common utility class.

Python supports multiple inheritance directly, unlike Java's restriction to one direct superclass.

### 2.6 Hybrid inheritance

Hybrid inheritance combines multiple inheritance patterns.

The `DepartmentManager` class combines:

- Multilevel inheritance through `SeniorEmployee`.
- Multiple inheritance through `TaxableMixin` and `AuditableMixin`.

It receives employee information, permanent compensation, senior-level allowances, taxation behavior, and audit functionality.

Hybrid inheritance is useful when domain objects require several independent capabilities.

Complex inheritance hierarchies should remain small because they increase method-resolution complexity.

## 3. Method Overriding and Polymorphism

### 3.1 Method overriding

Method overriding occurs when a child class provides its own implementation of an inherited method.

The central method in the payroll model is:

`calculate_salary()`

Its implementation differs across employee types.

| Class | Salary calculation |
|---|---|
| PermanentEmployee | Monthly salary + annual bonus / 12 |
| SeniorEmployee | Permanent salary + leadership allowance |
| ContractEmployee | Hourly rate × monthly hours |
| InternEmployee | Monthly stipend |
| DepartmentManager | Senior salary + management bonus |

The method name remains consistent while the calculation changes according to the actual object.

### 3.2 Runtime polymorphism

Polymorphism allows different object types to be accessed through a common interface.

The Python payroll system stores different employee subclasses in one list.

Calling `calculate_salary()` on each employee invokes the implementation belonging to its actual class.

This is called dynamic dispatch.

It eliminates the need for extensive conditional statements based on employee type.

### 3.3 Abstract classes

The `Employee` class inherits from `ABC`.

Its salary method uses the `@abstractmethod` decorator.

An abstract class defines a contract that concrete subclasses must implement.

Python prevents direct instantiation of an abstract class when required abstract methods remain unimplemented.

Abstract classes are useful when all subclasses must provide a common operation.

### 3.4 super()

The `super()` function provides access to the next implementation in the method-resolution order.

It is particularly important for:

- Reusing parent constructors.
- Extending existing methods.
- Cooperative multiple inheritance.
- Maintaining consistent initialization.

In the senior employee implementation, `super().calculate_salary()` reuses the permanent employee calculation.

The child class then adds its own allowance.

`super()` does not simply mean calling the immediate parent by name. In multiple inheritance, it follows the method-resolution order.

## 4. Advanced Python Inheritance

### 4.1 Method Resolution Order

Python uses Method Resolution Order (MRO) to determine which method implementation should execute when multiple inheritance is involved.

Python uses the C3 linearization algorithm to calculate the order.

The order can be inspected through:

- `ClassName.__mro__`
- `ClassName.mro()`

For the manager hierarchy, the MRO identifies the sequence in which Python searches for methods.

The sequence also determines how cooperative `super()` calls move through the hierarchy.

MRO prevents inconsistent method lookup orders while preserving the inheritance relationships.

### 4.2 Mixins

A mixin provides a focused capability that can be reused by multiple classes.

The implementations contain:

| Mixin | Responsibility |
|---|---|
| TaxableMixin | Tax and net salary calculations |
| AuditableMixin | Audit information and class hierarchy inspection |

Mixins should generally avoid maintaining complex independent state.

They work best when their methods operate on clearly defined attributes or methods provided by the consuming class.

### 4.3 Encapsulation

Inheritance and encapsulation solve different problems.

Inheritance establishes class relationships.

Encapsulation controls access to internal state.

The Python implementation uses `_active` to indicate an internal attribute and exposes a property for reading employee status.

The underscore is a Python convention, not strict access enforcement.

Properties allow validation and controlled state changes without exposing internal implementation details.

### 4.4 Composition versus inheritance

Composition combines independent objects instead of creating another inheritance relationship.

The `PayrollSystem` contains a `PayrollPolicy` object.

The policy calculates net compensation independently of employee subclasses.

This separation prevents payroll rules from becoming tightly coupled to the employee inheritance hierarchy.

Use inheritance for genuine specialization.

Use composition when an object needs another object's functionality without being a specialized version of that object.

## 5. Python Implementation Architecture

The Python script is organized around six components.

| Component | Responsibility |
|---|---|
| Employee | Abstract employee contract |
| PermanentEmployee | Permanent compensation |
| SeniorEmployee | Senior compensation |
| ContractEmployee | Hourly compensation |
| InternEmployee | Stipend calculation |
| TaxablePermanentEmployee | Multiple inheritance |
| DepartmentManager | Hybrid inheritance |
| PayrollPolicy | Deduction calculation |
| PayrollSystem | Registration and payroll processing |

The implementation also defines:

- `EmploymentType` for employment categories.
- `PayrollError` for payroll-related failures.
- `ValidationError` for invalid employee information.
- `EmployeeNotFoundError` for missing employee records.

Dataclasses reduce repetitive initialization code while retaining class-based inheritance.

Type annotations improve readability and help static analysis.

Assertions verify important salary calculations, abstract-class restrictions, and inheritance relationships.

## 6. JavaScript Inheritance

JavaScript supports inheritance through prototypes and ES6 classes.

Its class syntax resembles Python, but its underlying inheritance mechanism is different.

### 6.1 extends

JavaScript uses `extends` to establish a subclass relationship.

The payroll implementation uses:

`class SeniorEmployee extends PermanentEmployee`

The subclass inherits accessible methods and properties from the parent.

### 6.2 super

The `super()` constructor call initializes the parent class.

A subclass must call `super()` before accessing `this` in its constructor.

The `super.method()` syntax allows an overridden method to reuse parent behavior.

### 6.3 Prototype chain

JavaScript objects inherit through prototype relationships.

The `instanceof` operator checks whether a constructor's prototype occurs in an object's prototype chain.

The demonstration tests whether senior employees belong to:

- SeniorEmployee.
- PermanentEmployee.
- Employee.

### 6.4 Private fields

JavaScript supports private class fields through the `#` prefix.

The employee's active status uses a private field.

Unlike ordinary underscore-prefixed properties, private fields cannot be accessed directly from outside their declaring class.

### 6.5 Mixins

JavaScript does not support multiple direct class inheritance.

A class can extend only one class.

Mixins provide an alternative by returning a new subclass that adds functionality to an existing class.

The implementation uses functional mixins for taxation and auditing.

### 6.6 Event-driven processing

The JavaScript payroll service extends `EventTarget`.

It publishes events when employees are registered and payroll processing completes.

This separates payroll operations from listeners that need to respond to those operations.

`Promise.all()` processes independent employee calculations concurrently.

If one payroll calculation fails, the aggregate operation rejects.

A production system requiring independent failure reporting would process employees with individual error handling rather than relying exclusively on one aggregate promise.

## 7. C++17 Inheritance

C++ implements inheritance through explicit base-class relationships and virtual dispatch.

The C++ implementation provides a payroll engine with memory ownership and runtime polymorphism.

### 7.1 Base classes

The `Employee` class provides shared employee information.

It declares a pure virtual salary method:

`virtual double calculateSalary() const = 0;`

A class containing a pure virtual function is abstract.

It cannot be instantiated directly.

### 7.2 Virtual functions

Virtual functions support runtime polymorphism.

A base-class pointer or reference can refer to different derived employee objects.

The program calls the appropriate overridden method at runtime.

The `override` keyword allows the compiler to verify that a derived method correctly overrides a virtual base method.

### 7.3 Virtual destructors

A polymorphic base class should generally have a virtual destructor.

The payroll implementation declares:

`virtual ~Employee() = default;`

This ensures that derived-class destructors are invoked correctly when objects are destroyed through base-class pointers.

### 7.4 Multiple inheritance

C++ supports multiple inheritance through multiple base classes.

The `TaxablePermanentEmployee` class inherits from:

- `PermanentEmployee`
- `Taxable`

The `Taxable` class acts as an interface-style abstract base class.

This separates the taxation contract from permanent employment compensation.

### 7.5 Smart pointers

The payroll engine stores employee objects through `std::unique_ptr`.

This provides automatic resource management.

The engine has exclusive ownership of its registered employee objects.

The auxiliary employee index stores non-owning pointers into objects owned by the smart pointers.

Those pointers remain valid because the pointed-to heap objects are not relocated when the vector of smart pointers grows.

### 7.6 Performance considerations

| Operation | Expected complexity |
|---|---|
| Employee registration | Average O(1) lookup plus amortized vector insertion |
| Employee lookup | Average O(1) |
| Payroll processing | O(n) |
| Department aggregation | Average O(n) |
| Salary calculation | O(1) |

The unordered map provides efficient lookup, while the vector provides efficient sequential payroll processing.

## 8. Java 17 Inheritance

Java supports single class inheritance and multiple interface implementation.

Its inheritance system is designed around explicit type contracts and controlled class relationships.

### 8.1 Abstract classes

The abstract `Employee` class defines shared employee information and the salary calculation contract.

Concrete employee classes must implement the abstract method.

The `final` access modifiers on selected methods prevent subclasses from changing identity and status-management operations.

### 8.2 Interfaces

The Java implementation defines two interfaces:

- `Taxable`
- `Auditable`

Interfaces allow unrelated classes to share behavioral contracts.

`TaxablePermanentEmployee` extends `PermanentEmployee` while implementing both interfaces.

This is Java's approach to combining class inheritance and multiple behavioral contracts.

### 8.3 Default methods

The `Taxable` interface contains a default implementation of `calculateNetSalary()`.

It uses the interface's tax calculation contract and gross salary method.

Default methods allow interfaces to provide reusable behavior without requiring every implementing class to duplicate the implementation.

### 8.4 Records

Java 17 records represent immutable data carriers.

The implementation uses:

- `PayrollResult`
- `DepartmentReport`

Records automatically provide constructors, accessors, equality, hash codes, and string representations.

They are appropriate for payroll results that should not be modified after creation.

### 8.5 Generics

The payroll service contains a generic method:

`<T extends Employee> List<T> findByType(Class<T> employeeClass)`

The upper bound ensures that the requested type belongs to the employee hierarchy.

The method returns only matching employee objects.

### 8.6 Streams

Java streams support collection processing and aggregation.

The payroll service uses streams for:

- Filtering inactive employees.
- Calculating payroll.
- Sorting payroll results.
- Grouping employees by department.
- Calculating department totals.

The `toList()` operation returns an unmodifiable list in Java 17.

### 8.7 Enterprise validation

The implementation separates business operations into:

- Domain classes.
- Behavioral interfaces.
- Payroll policy.
- Payroll service.
- Result records.
- Custom exceptions.

This structure helps isolate responsibilities and makes individual components easier to test.

## 9. PostgreSQL: Relational Representation of Inheritance

Relational databases do not automatically implement Python class inheritance.

The SQL implementation uses a table-per-type model.

This represents a general employee entity in one table and specialized attributes in related tables.

### 9.1 Table-per-type structure

| Relational table | Purpose |
|---|---|
| employees | Shared employee information |
| permanent_employees | Permanent compensation |
| senior_employees | Leadership allowance |
| contract_employees | Hourly compensation |
| intern_employees | Internship stipend |

The primary key of each subtype table also references its parent employee.

This creates a one-to-one relationship between the base record and its specialized record.

### 9.2 Primary and foreign keys

The employee identifier is the primary key in the base table.

Each subtype table uses the same identifier as both its primary key and foreign key.

This prevents subtype records from referring to nonexistent employees.

The foreign key also supports cascading deletion.

### 9.3 Integrity enforcement

The database uses:

- Primary-key constraints.
- Foreign-key constraints.
- Unique constraints.
- Check constraints.
- Deferred constraint triggers.

The subtype-integrity triggers verify that the employment category matches the subtype table.

They also prevent an employee from belonging to multiple primary employment subtypes.

Senior employees must have a permanent employee record.

A deferred constraint trigger allows related base and subtype records to be inserted within the same transaction.

### 9.4 Salary calculation

The `calculate_employee_salary()` function retrieves the employee's employment type and calculates compensation using the corresponding subtype data.

Permanent employees may also have a senior-level allowance.

Contract employees use hourly rates and recorded monthly hours.

Interns receive a fixed stipend.

The function raises an exception if the employee does not exist or the required subtype information is incomplete.

### 9.5 Payroll processing

The `process_employee_payroll()` function performs several operations:

1. Locks the employee record.
2. Verifies employee existence.
3. Checks active employment status.
4. Retrieves the active payroll policy.
5. Calculates gross compensation.
6. Calculates deductions.
7. Calculates net compensation.
8. Inserts a payroll record.
9. Returns the generated payroll identifier.

The row lock helps prevent conflicting processing operations on the same employee.

The function operates within the caller's transaction.

### 9.6 Views and reporting

The `employee_salary_details` view presents employee information with calculated compensation.

The `payroll_eligibility` view determines whether an employee has a valid subtype record and active status.

CTEs support department-level reporting.

Indexes improve access to employee departments, employment status, and payroll history.

## 10. Important Differences Between Inheritance Implementations

| Feature | Python | JavaScript | C++17 | Java 17 |
|---|---|---|---|---|
| Class inheritance | Multiple | Single | Multiple | Single |
| Abstract classes | ABC | No native abstract class enforcement | Pure virtual classes | Native |
| Interfaces | Abstract classes and protocols | Convention and mixins | Abstract base classes | Native |
| Method overriding | Supported | Supported | Virtual functions | Supported |
| Runtime polymorphism | Dynamic dispatch | Prototype-based dispatch | Virtual dispatch | Dynamic dispatch |
| Multiple inheritance | Supported | Mixins as alternative | Supported | Multiple interfaces |
| Constructor delegation | super() | super() | Base initializers | super() |
| Method resolution | C3 MRO | Prototype chain | Base-class lookup rules | Class and interface rules |

The same business domain can be implemented using different inheritance mechanisms.

The language-specific implementation determines how method dispatch, type checking, memory management, and interface enforcement operate.

## 11. Inheritance Versus Composition

Inheritance and composition should not be treated as interchangeable design techniques.

| Aspect | Inheritance | Composition |
|---|---|---|
| Relationship | Is-a | Has-a |
| Main purpose | Specialization | Combining capabilities |
| Reuse mechanism | Base-class behavior | Collaborating objects |
| Coupling | Often stronger | Usually more flexible |
| Example | SeniorEmployee is an Employee | PayrollSystem has a PayrollPolicy |

The payroll implementations use inheritance for employee specialization and composition for payroll policies.

This avoids creating unnecessary subclasses for every possible payroll deduction or policy variation.

## 12. Validation and Failure Handling

The implementations account for common domain errors.

| Failure condition | Handling |
|---|---|
| Invalid employee ID | Validation exception |
| Empty employee name | Input rejection |
| Negative compensation | Validation exception |
| Excessive working hours | Range validation |
| Duplicate employee ID | Registration rejection |
| Missing employee | Lookup exception |
| Abstract class instantiation | Runtime or compile-time restriction |
| Invalid tax rate | Policy validation |
| Inactive employee | Payroll processing exclusion |
| Missing subtype record | Database exception |
| Incompatible employment subtype | Database constraint trigger |

Financial calculations use finite, non-negative input validation.

The examples use floating-point arithmetic in the programming-language implementations for clarity.

Production financial systems should use decimal arithmetic or integer minor currency units to avoid binary floating-point rounding errors.

The PostgreSQL implementation uses `NUMERIC` for monetary values.

## 13. Security and Production Considerations

Inheritance does not automatically provide application security.

A production payroll system also requires:

- Authentication.
- Role-based authorization.
- Restricted employee record access.
- Protected salary information.
- Auditable payroll modifications.
- Transaction management.
- Secure database connections.
- Parameterized database queries.
- Input validation.
- Controlled administrative privileges.
- Separation of duties.
- Reliable backup and recovery.

Private attributes and protected methods improve encapsulation, but they do not replace authentication or authorization.

Database functions and triggers enforce business consistency but do not replace application-level access controls.

The sample SQL schema demonstrates integrity mechanisms rather than a complete payroll security architecture.

For real payroll processing, the application must also handle statutory deductions, currency precision, tax jurisdiction, payroll periods, reversals, and legally required reporting.

## 14. Performance and Design Trade-offs

| Design decision | Benefit | Trade-off |
|---|---|---|
| Abstract base class | Consistent contracts | More structural constraints |
| Multiple inheritance | Reusable independent behavior | Complex method resolution |
| Mixins | Small reusable capabilities | Requires careful method naming |
| Composition | Flexible policy changes | Additional object coordination |
| Runtime polymorphism | Extensible processing | Dispatch overhead |
| Table-per-type mapping | Normalized relational structure | Additional joins |
| Smart pointers | Automatic C++ memory management | Ownership rules must be clear |
| Java records | Immutable result objects | Limited to data-carrier use cases |

A deep inheritance hierarchy should not be created simply to avoid repeating a small amount of code.

Inheritance should represent genuine specialization and stable behavioral contracts.

Composition is generally preferable when behavior changes independently of the object's identity.

## 15. Execution Instructions

### Python

Save the first implementation as `inheritance_payroll.py`.

Run it using:

`python inheritance_payroll.py`

The script uses Python standard-library modules and requires no external packages.

### JavaScript

Save the second implementation as `inheritance_payroll.js`.

Run it using:

`node inheritance_payroll.js`

The implementation uses Node.js built-in capabilities.

### C++17

Save the third implementation as `inheritance_payroll.cpp`.

Compile using:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic inheritance_payroll.cpp -o inheritance_payroll`

Run using:

`./inheritance_payroll`

### Java 17

Save the fourth implementation as `Main.java`.

Compile using:

`javac Main.java`

Run using:

`java Main`

### PostgreSQL

Save the fifth implementation as `inheritance_payroll.sql`.

Execute using:

`psql -U postgres -d your_database -f inheritance_payroll.sql`

The script creates a dedicated `payroll` schema and its related database objects.

It uses a transaction so that the main schema setup and sample payroll workflow can be committed together.

## 16. Learning Outcomes

The five implementations demonstrate how inheritance supports specialization, reuse, polymorphism, and behavioral contracts.

The most important distinctions are:

- Single inheritance establishes one direct parent relationship.
- Multilevel inheritance creates a chain of specialized classes.
- Hierarchical inheritance creates several subclasses from one parent.
- Multiple inheritance combines capabilities from several parent classes.
- Hybrid inheritance combines multiple inheritance structures.
- Abstract classes establish required behavioral contracts.
- Method overriding changes inherited behavior.
- Polymorphism enables common operations across different object types.
- MRO determines method lookup order in Python.
- Mixins provide reusable functionality.
- Composition combines independent objects without creating additional inheritance relationships.
- Relational table-per-type mapping represents object specialization through primary-key and foreign-key relationships.

The employee payroll domain provides a consistent basis for comparing the mechanisms and engineering trade-offs across all five implementations.
