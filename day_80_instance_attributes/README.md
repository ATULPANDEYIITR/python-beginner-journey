# Instance Attributes: Object State and Data Management

## 1. Introduction

Instance attributes are properties that belong to individual objects created from a class. They represent the state of a particular object and allow multiple objects of the same class to maintain independent values.

For example, two network devices may be created from the same `Device` class. Both devices have a name, manufacturer, temperature, status, and configuration. Their values are independent because each object maintains its own instance attributes.

Instance attributes are fundamental to object-oriented programming, domain modeling, state management, and enterprise application development.

The five implementations use a network equipment management scenario to demonstrate object-specific state, attribute modification, validation, persistence, and independent object behavior.

## 2. Instance Attributes and Class Attributes

An instance attribute belongs to one object. A class attribute belongs to the class and is shared through the class-level definition.

| Property | Instance attribute | Class attribute |
|---|---|---|
| Ownership | Individual object | Class |
| Storage | Object-specific storage | Class-level storage |
| Values | Can differ between objects | Shared by default |
| Modification | Changes an individual object's state | Can affect shared class-level behavior |
| Lifetime | Associated with the object | Associated with the class |
| Typical purpose | Name, temperature, status | Category, shared configuration |

Consider two objects:

- Router: temperature = 42.5
- Firewall: temperature = 78.0

Both objects have the same attribute structure but different instance values.

A shared category such as `NETWORK_EQUIPMENT` can be represented as a class attribute.

### Attribute shadowing

In Python, an instance can define an attribute with the same name as a class attribute.

When this happens, normal attribute lookup finds the instance-specific value first.

For example, assigning `router.category` creates an instance attribute that shadows the class attribute. The class attribute remains unchanged.

JavaScript uses a related mechanism through its prototype chain. An own property takes precedence over an inherited property.

C++ and Java use different mechanisms. Static members belong to the class, while non-static data members belong to each object.

## 3. Object State and Instance Independence

An object consists of an identity, state, and behavior.

The identity distinguishes one object from another. Its state is represented by its instance attributes. Its behavior is implemented through methods.

The relationship is:

**Class → Object creation → Instance attributes → State modification → Object behavior**

The implementations use these device properties:

| Attribute | Data type | Purpose |
|---|---|---|
| `id` | String | Unique device identity |
| `name` | String | Device name |
| `manufacturer` | String | Device manufacturer |
| `temperature` | Numeric | Current operating temperature |
| `status` | Enumeration | Operational condition |
| `configuration` | Object or dictionary | Device-specific configuration |
| `tags` | Collection | Instance classification |
| `createdAt` | Date/time | Object creation information |
| `revision` | Integer | Number of successful modifications |

Every device receives its own values.

Changing the router's temperature does not change the firewall's temperature. Changing the router's configuration does not modify the firewall's configuration.

This independence is essential when modeling multiple employees, customers, transactions, devices, accounts, or other entities using the same class.

## 4. Python Implementation

The Python implementation uses classes, dataclasses, dictionaries, lists, enumerations, and exception handling.

### 4.1 Dataclasses

The `@dataclass` decorator automatically provides useful object functionality, including initialization and representation methods.

The `Device` dataclass defines instance attributes directly through its annotated fields.

`default_factory` is used for mutable attributes such as dictionaries and lists.

This is important because mutable default objects should not be unintentionally shared between instances.

Each device receives its own configuration dictionary and tags list.

### 4.2 Instance dictionary

Python normally stores an object's instance attributes in its `__dict__` when the class uses the standard instance dictionary.

The expression `vars(device)` exposes this dictionary.

It provides a practical way to inspect object-specific state.

Class variables annotated with `ClassVar` are excluded from dataclass instance fields.

### 4.3 Dynamic attributes

Python permits adding attributes to an existing object when its class allows dynamic instance dictionaries.

For example, a location attribute can be assigned to a router without adding that attribute to every device.

This flexibility is useful for exploratory programming but can create inconsistent object structures.

Production applications should generally use controlled schemas, validation, and explicit attribute-management methods.

### 4.4 Controlled updates

The `update_attribute()` method restricts modifications to approved attributes.

It validates:

- Temperature boundaries.
- Device status values.
- Configuration types.
- Tag collection structure.
- Required text fields.

Invalid modifications raise `ValidationError`.

### 4.5 Serialization

The registry converts object state into JSON records.

The JSON representation contains instance-specific information rather than relying on class-level attributes.

Loading reconstructs individual `Device` objects and restores their values.

Serialization requires special handling for enumerations and date/time objects because they are not directly JSON-compatible.

### 4.6 Registry operations

The `DeviceRegistry` class uses a dictionary indexed by device ID.

Its main operations are:

- Registering devices.
- Retrieving devices.
- Updating attributes.
- Identifying overheating devices.
- Producing reports.
- Saving and restoring object state.

Dictionary-based lookup has average-case O(1) complexity.

Filtering all devices requires O(n) time, where n is the number of registered objects.

## 5. JavaScript Implementation

JavaScript provides object-specific properties and prototype-based inheritance.

### 5.1 Own properties

Properties assigned through `this` inside a constructor become own properties of the constructed object.

For example, `this.temperature` belongs to that particular device.

The following concepts are important:

| Mechanism | Meaning |
|---|---|
| Own property | Property directly stored on an object |
| Prototype property | Property inherited through the prototype chain |
| Static property | Property associated with the class |
| `Object.keys()` | Lists enumerable own string properties |
| `Object.hasOwn()` | Checks direct ownership of a property |
| `Object.getPrototypeOf()` | Returns an object's prototype |

The implementation uses `Object.keys()` and `Object.hasOwn()` to distinguish instance properties from inherited properties.

### 5.2 Prototype lookup

JavaScript checks an object's own properties before checking its prototype chain.

If an object defines a property with the same name as an inherited property, the own property takes precedence.

This behavior is called property shadowing.

### 5.3 Maps and object registries

The `DeviceRegistry` uses a `Map` to associate device IDs with objects.

A Map provides efficient key-based retrieval and avoids treating arbitrary device IDs as ordinary object property names.

### 5.4 Event-driven updates

The implementation extends Node.js `EventEmitter`.

It publishes events when devices are registered or updated.

Events contain:

- Device identity.
- Previous revision.
- Current revision.
- Event timestamp.

This separates state modification from notification logic.

It is useful in monitoring systems where several components must react to object changes.

### 5.5 Asynchronous persistence

The implementation uses Node.js asynchronous file operations.

The registry writes to a temporary file before renaming it to the destination.

This reduces the risk of exposing a partially written report when the filesystem supports atomic rename operations.

It does not provide a complete multi-process transaction or guarantee crash durability.

## 6. C++17 Implementation

The C++ implementation models instance attributes using non-static data members.

### 6.1 Object storage

Each `Device` object contains its own:

- Identification fields.
- Temperature.
- Status.
- Configuration.
- Tags.
- Revision counter.

The `category` property is declared as a static class member.

This provides a direct distinction between object-specific storage and shared class-level storage.

### 6.2 Encapsulation

The device attributes are private.

External code cannot modify them directly.

Public getter and setter methods provide controlled access.

This protects the internal object state from invalid modifications.

### 6.3 Configuration structure

The `Configuration` structure groups related instance attributes.

It contains an IP address and port count.

Its constructor validates both values before accepting the configuration.

This demonstrates composition: a device owns a configuration object as part of its state.

### 6.4 Local category override

The implementation contains a separate `localCategory` instance attribute.

It allows one device to override the shared category without modifying the static class attribute.

This demonstrates the difference between shared state and object-specific overrides.

### 6.5 Registry and collections

The registry uses `std::map` to store devices by ID.

The ordered map provides O(log n) lookup and insertion.

The implementation also uses:

- `std::vector` for tags and filtered results.
- `std::find` for duplicate tag detection.
- Structured bindings for collection traversal.
- Exceptions for validation and operational failures.

The report writer uses standard file streams and checks write failures.

## 7. Java 17 Implementation

The Java implementation uses an enterprise-oriented model with explicit domain types, immutable identity, policy evaluation, and controlled state transitions.

### 7.1 Instance fields and static fields

Non-static fields belong to individual objects.

The `Device` class contains private instance fields for device identity, name, temperature, status, configuration, and tags.

The static `CATEGORY` field is shared at the class level.

The `id` and `createdAt` fields are final, preventing their reassignment after construction.

### 7.2 Records

Java 17 records provide compact immutable data structures.

The `DeviceConfiguration` record models a validated device configuration.

The `DeviceSnapshot` record represents a read-only representation of device state.

A snapshot is useful when reporting or transferring information without exposing the mutable device object itself.

### 7.3 Encapsulation

The implementation uses private fields and public methods.

Modifications are performed through methods such as:

- `updateTemperature()`
- `updateName()`
- `updateStatus()`
- `updateConfiguration()`
- `addTag()`

Each method validates the proposed value before modifying the object.

### 7.4 Enterprise policies

The `DevicePolicy` interface defines registration and update eligibility.

`EnterpriseDevicePolicy` checks whether the device manufacturer is approved.

The registry applies these rules before accepting a device.

This separates domain behavior from organizational policy.

### 7.5 Streams and immutable collections

Java streams support filtering and aggregation.

The implementation uses streams to identify overheating devices and count device statuses.

`List.copyOf()` creates an unmodifiable copy of a collection.

This prevents consumers of snapshots from modifying the registry's underlying tag collection.

The snapshot is a read-only representation, not a fully immutable copy of every possible object referenced by the original instance.

## 8. PostgreSQL Implementation

The PostgreSQL implementation represents instance attributes through relational tables.

It distinguishes device models, attribute definitions, individual device instances, and instance-specific attribute values.

### 8.1 Relational structure

The database follows this relationship:

    Organizations
         |
         v
    Device Instances
         |
         +----------> Device Models
         |                 |
         |                 v
         |          Attribute Definitions
         |                 |
         v                 v
    Instance Attribute Values
         |
         v
    Attribute Audit History

A device model describes a common type of equipment.

A device instance represents an individual physical or logical device.

An attribute definition describes an available attribute.

An instance attribute value stores the value assigned to one particular instance.

### 8.2 Attribute definitions

The `attribute_definitions` table defines:

- Attribute name.
- Data type.
- Required status.
- Mutability.
- Default value.

This separates the definition of a property from its actual value.

For example, `firmware_version` can be defined once for a router model but have different values for individual router instances.

### 8.3 Instance-specific values

The `instance_attribute_values` table uses a composite unique constraint on:

`(instance_id, attribute_id)`

This ensures that an instance has no more than one current value for a particular attribute.

The JSONB data type allows flexible storage while retaining a relational structure.

### 8.4 Data integrity

The implementation uses:

- Primary keys for entity identity.
- Foreign keys for relationship integrity.
- Unique constraints for duplicate prevention.
- Check constraints for valid temperature and revision values.
- Enumeration types for operational status.
- Triggers for attribute validation and revision management.

The attribute-validation trigger ensures that a value matches its declared data type and that the attribute definition belongs to the device's model.

### 8.5 Audit history

The `attribute_audit` table stores previous and new values for custom attribute changes.

It records:

- Instance ID.
- Attribute ID.
- Previous value.
- New value.
- User identifier.
- Modification timestamp.

This supports traceability and change analysis.

The audit table records changes made through its associated trigger. It is not a complete audit of every possible database modification or administrator action.

### 8.6 Transaction handling

The attribute update function locks the affected device instance using `FOR UPDATE`.

This prevents concurrent transactions from modifying the same instance's associated attribute state without coordinating through the row lock.

The transaction commits the update and its audit record together.

If validation fails, PostgreSQL raises an exception and the transaction can be rolled back.

### 8.7 JSONB and indexes

JSONB is appropriate for flexible configuration attributes.

The implementation uses GIN indexes for configuration searches and tags.

B-tree indexes support common filtering and joins.

A partial temperature index targets overheating devices instead of indexing every temperature value.

Index usefulness should be verified against actual query plans and data volume.

## 9. Important Technical Distinctions

| Concept | Meaning | Example |
|---|---|---|
| Instance attribute | State belonging to one object | Router temperature |
| Class attribute | State associated with a class | Shared equipment category |
| Static attribute | Class-level field in Java or C++ | `CATEGORY` |
| Dynamic attribute | Property added at runtime | Python location property |
| Own property | Direct JavaScript object property | `router.temperature` |
| Prototype property | Inherited JavaScript property | Shared prototype behavior |
| Encapsulation | Controlled access to internal state | Private Java and C++ fields |
| Composition | One object contains another object | Device configuration |
| Serialization | Converting state into a transferable representation | JSON |
| Persistence | Storing state beyond an object's lifetime | PostgreSQL |
| Audit trail | Recording changes to state | Attribute audit table |

## 10. Validation and Failure Conditions

The implementations address common problems associated with instance attributes.

| Failure condition | Control |
|---|---|
| Empty device identity | Required-field validation |
| Duplicate device ID | Registry and database uniqueness checks |
| Invalid temperature | Numeric range validation |
| Invalid status | Enumeration validation |
| Invalid configuration | Type and structure validation |
| Shared mutable data | Independent collection creation |
| Unauthorized attribute changes | Controlled update methods |
| Missing object | Explicit lookup exception |
| Invalid attribute type | Database trigger |
| Immutable custom attribute modification | Attribute mutability enforcement |
| File access failure | Exception handling |
| Concurrent database updates | Row-level locking |

A successful update must preserve object consistency.

Validation should occur before changing the object's state. The JavaScript implementation validates the entire update patch before applying its fields.

## 11. Practical Applications

Instance attributes are used extensively in software systems.

| Application | Instance attributes |
|---|---|
| Banking | Account number, balance, account status |
| Healthcare | Patient identifier, observations, appointment status |
| E-commerce | Product identifier, inventory, price |
| Cybersecurity | Device address, risk score, security status |
| Human resources | Employee ID, designation, department |
| Cloud computing | Instance ID, memory allocation, runtime status |
| Logistics | Vehicle ID, location, fuel level |
| Financial systems | Transaction ID, amount, transaction state |

The network equipment example demonstrates how an application can manage many objects while preserving independent state and applying common validation rules.

## 12. Performance Considerations

The main performance characteristics depend on the language and data structure.

| Operation | Implementation | Typical complexity |
|---|---|---|
| Direct Python attribute access | Object attribute lookup | Average O(1) |
| Python registry lookup | Dictionary | Average O(1) |
| JavaScript registry lookup | Map | Average sublinear, typically O(1) |
| C++ ordered registry lookup | `std::map` | O(log n) |
| Java registry lookup | HashMap | Average O(1) |
| PostgreSQL instance lookup | Indexed query | Depends on query plan and selectivity |
| Full registry monitoring | Collection scan | O(n) |
| Attribute report generation | Collection traversal | O(n) relative to returned records |

Additional considerations:

- Excessive instance attributes increase memory usage.
- Large nested configurations increase copying and serialization costs.
- Frequent audit writes increase database storage and write activity.
- Unnecessary database indexes increase maintenance overhead.
- Snapshot creation can consume significant memory for large collections.
- High-concurrency updates require appropriate transaction isolation and locking strategies.

## 13. Security and Production Considerations

Instance attributes often contain operational or sensitive information.

Production systems should apply:

- Authentication and authorization before attribute modifications.
- Validation at application and database boundaries.
- Parameterized SQL statements.
- Restricted database permissions.
- Audit retention and access policies.
- Protection against accidental exposure of internal attributes.
- Safe serialization and deserialization.
- Controlled file permissions.
- Concurrency controls for shared persistent state.
- Monitoring of invalid updates and repeated failures.

The demonstration programs provide basic validation and state management. They do not implement a complete authentication system, encrypted storage, distributed synchronization, or a production authorization framework.

## 14. Implementation Comparison

| Feature | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Instance storage | Object dictionary | Own properties | Non-static fields | Non-static fields | Relational rows |
| Shared state | Class variables | Static/prototype properties | Static members | Static fields | Model records |
| Dynamic properties | Supported | Supported | Not directly supported for ordinary class objects | Not directly supported | Flexible JSONB attributes |
| Validation | Methods and exceptions | Constructor and update validation | Setters and exceptions | Methods and domain policies | Constraints and triggers |
| Collections | Dictionary | Map and Set | STL containers | Collections | Relational tables |
| Persistence | JSON | Asynchronous JSON | CSV | CSV | Relational storage |
| Audit | Application-level reporting | Event notifications | Report generation | Snapshot reporting | Audit triggers |

## 15. Execution

The implementations are independent and use standard language capabilities.

| File | Runtime |
|---|---|
| `instance_attributes.py` | Python 3.10+ |
| `instance_attributes.js` | Node.js 18+ |
| `instance_attributes.cpp` | C++17 compiler |
| `InstanceAttributes.java` | Java 17 |
| `instance_attributes.sql` | PostgreSQL 14+ |

The SQL script creates its own `instance_lab` schema and inserts demonstration records. It should be executed using a database account with permission to create schemas, types, tables, functions, and triggers.

The Python and JavaScript programs create JSON reports. The C++17 and Java programs create CSV reports in their current working directories.

The examples demonstrate that instance attributes provide the object-specific state required to represent independent entities, while class-level attributes provide shared definitions and behavior.
