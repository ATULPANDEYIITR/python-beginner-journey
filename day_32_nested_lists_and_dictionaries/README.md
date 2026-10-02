# Nested Lists and Dictionaries

## Scope

Nested lists and dictionaries are hierarchical data structures in which one collection contains other collections. They are useful when data naturally has multiple levels: a matrix contains rows, an order contains line items, a customer contains an address object, and an inventory product contains warehouse-level quantities.

The three implementations approach the same subject from different technical perspectives:

- The Python program emphasizes expressive nested `list` and `dict` operations, recursive traversal, validation, transformation, serialization, grouping, copying, and indexing.
- The JavaScript program focuses on `Array`, object, `Map`, optional chaining, nullish coalescing, recursive traversal, reference behavior, JSON serialization, and asynchronous processing.
- The C++ program models a typed inventory repository using `std::vector`, `std::map`, `std::unordered_map`, structures, references, validation, and lookup indexes.

The central distinction is between an **ordered collection** and a **keyed collection**. A list or array is normally used when position and ordering matter. A dictionary-like structure is used when values are identified by keys.

## Core Data Model

A nested structure can be visualized as a tree:

    Application
    ├── configuration
    │   ├── database
    │   │   ├── host
    │   │   └── port
    │   └── features
    │       ├── stock
    │       └── pricing
    └── products
        ├── product
        │   ├── pricing
        │   └── warehouses
        │       ├── warehouse
        │       └── warehouse
        └── product

The leaves of this tree contain scalar values such as strings, integers, floating-point numbers, and booleans. Intermediate nodes contain lists, arrays, dictionaries, objects, maps, or combinations of those structures.

This hierarchy matters because accessing a value requires following the structure that leads to it. For example, a product price can conceptually be represented as `product -> pricing -> amount`, while a warehouse quantity may be represented as `product -> warehouses -> warehouse -> quantity`.

## Nested Lists

A nested list is a list whose elements are themselves lists.

Python expresses a two-dimensional collection naturally as `[[10, 20], [30, 40]]`. The outer list contains rows, and each row contains values.

JavaScript uses the same conceptual model with arrays such as `[[10, 20], [30, 40]]`.

C++ commonly uses `std::vector<std::vector<int>>`. Unlike a mathematical matrix, a nested vector does not automatically require every row to have the same number of elements. A row may contain two values while another contains four. Code that requires a rectangular structure must explicitly validate row lengths.

Nested lists are appropriate when:

- order matters;
- position has meaning;
- duplicate values are allowed;
- the number of elements can vary;
- each element belongs to the same broad collection.

A matrix, sequence of batches, list of orders, and list of warehouse records are all examples where nesting provides useful structure.

## Nested Dictionaries

A nested dictionary stores a dictionary as the value associated with another dictionary key.

In Python:

`employee["department"]["name"]`

means that `department` must first be retrieved from `employee`, after which `name` is retrieved from the resulting dictionary.

JavaScript objects support the same property hierarchy:

`employee.department.name`

C++ does not have one universal dictionary type. The C++ implementation uses `std::map` and `std::unordered_map` for keyed collections and uses structures for strongly typed records.

Nested dictionaries are useful when the keys describe the meaning of the values. For example, a configuration can use `database.host` and `database.port`, while an inventory record can use `pricing.currency` and `pricing.amount`.

The key is part of the data model. Unlike a list index, a dictionary key communicates what a value represents.

## Mixed Nesting

Real data is rarely only a list or only a dictionary.

An order can contain:

- an order identifier;
- a customer dictionary;
- an items list;
- dictionaries representing individual items;
- nested numeric and textual values inside those item dictionaries.

This produces structures such as:

`orders -> order -> customer -> city`

and

`orders -> order -> items -> item -> quantity`.

The Python and JavaScript programs deliberately use this pattern because it represents common API responses, configuration documents, operational records, and JSON data.

## Python Implementation

The Python implementation starts with a matrix represented by a list of lists. It demonstrates indexing, iteration, flattening, mutation, shallow copying, and `deepcopy`.

The distinction between shallow and deep copies is important for nested structures. `list.copy()` duplicates only the outer list. The inner lists remain shared. A mutation to an inner list can therefore appear in both structures.

`copy.deepcopy()` recursively copies the nested containers so that subsequent nested mutations do not affect the original object.

The Python dictionary examples then build an employee record containing nested department, contact, and skill dictionaries. The implementation accesses and updates values at multiple levels rather than treating the dictionary as a flat collection.

The `safe_nested_access()` function demonstrates explicit structural traversal. It checks that every intermediate value is a dictionary before using the next key. The companion `get_nested_value()` function returns a default when the requested path does not exist.

This distinction is useful in production code. A missing required field and an optional missing field should not necessarily have identical behavior.

### Recursive Traversal

`recursive_walk()` treats nested lists and dictionaries as a tree. Dictionaries contribute keys to the path, while lists contribute integer indexes.

For example, a path may look conceptually like:

`("profile", "addresses", 1, "city")`

The function yields leaf values only. This allows the same traversal mechanism to inspect structures whose depth is not known beforehand.

Recursive traversal is useful for:

- configuration inspection;
- validation;
- auditing;
- data transformation;
- searching deeply nested documents;
- discovering unexpected values.

Its cost is proportional to the number of nodes visited. Very deeply nested input can also encounter Python's recursion-depth limitations, so iterative traversal may be preferable for hostile or extremely deep input.

### Validation

The Python `validate_customer()` function validates both types and structural relationships.

It checks that:

- the top-level value is a dictionary;
- required fields exist;
- identifiers have the expected type;
- an address is a dictionary;
- address fields have expected types;
- orders are represented by a list;
- individual orders are dictionaries;
- order items are lists.

Structural validation is more important than simply checking whether a top-level object exists. A value such as `{"orders": "three"}` has an `orders` key but still violates the expected data model.

### Transformation and Grouping

The Python program calculates order totals from nested item records and then aggregates those totals by city.

The `defaultdict` grouping structure demonstrates a common pattern:

`region -> category -> amounts`

The program later transforms those amounts into counts, totals, and averages.

This separates the storage model from the reporting model. Source records remain detailed and hierarchical, while a derived report can contain only the metrics needed by consumers.

### Flattening

`flatten_dictionary()` converts nested dictionary paths into dotted keys such as:

`server.http.port`

This can be useful for configuration reporting and systems that require flat key-value representations.

Lists are intentionally kept as values rather than automatically converted into dotted numeric paths. A list represents an ordered collection, and flattening its indexes can change the intended semantic distinction between collection data and dictionary hierarchy.

### Serialization

The Python implementation serializes nested data with `json.dumps()` and restores it with `json.loads()`.

JSON naturally represents:

- Python dictionaries as JSON objects;
- Python lists as JSON arrays;
- strings as strings;
- numbers as JSON numbers;
- booleans as JSON booleans;
- `None` as JSON `null`.

Serialization provides a boundary between an in-memory nested data structure and a persistent or transferable representation.

The example writes a temporary JSON file and removes it after the round trip, so execution does not leave an unnecessary artifact.

### Inventory Index

The `InventoryIndex` dataclass demonstrates a more advanced design. Products remain stored as nested records, but two indexes are created:

- `by_sku` maps a unique SKU to its product.
- `by_category` maps a category to a list of products.

This avoids repeatedly scanning every product when the application frequently performs SKU or category lookups.

The source structure is therefore optimized for readability and completeness, while the derived indexes are optimized for access patterns.

## JavaScript Implementation

The JavaScript implementation uses arrays for ordered nested collections and objects for dictionary-like records.

The nested-array section also demonstrates a subtle reference issue. Creating rows with `Array.from({ length: 3 }, () => Array(3).fill(0))` gives every row its own array.

Using a shared nested array reference would cause a mutation in one row to unexpectedly appear in other rows.

### Optional Chaining

JavaScript optional chaining provides concise safe navigation:

`configuration.application?.cache?.host`

If an intermediate property is `undefined` or `null`, evaluation stops instead of throwing a `TypeError`.

The program combines this with nullish coalescing:

`value ?? defaultValue`

This supplies a fallback only when the left side is `null` or `undefined`. It does not replace valid values such as `0` or `false`.

### Generic Path Access

`getByPath()` accepts a root object and a path array containing both object keys and array indexes.

A path such as:

`["profile", "addresses", 0, "city"]`

can therefore navigate through an object, an array, another object, and finally a scalar value.

This approach is useful when the path is supplied dynamically rather than being known at programming time.

### Recursive Traversal

`walkNestedValue()` recursively processes arrays and objects. It treats arrays as indexed collections and objects as keyed collections.

The callback receives the complete path and leaf value. This is useful when a JavaScript application needs to inspect unknown nested JSON rather than hard-code a particular hierarchy.

### Validation

`validateOrder()` demonstrates structural validation without relying on an external validation package.

The function checks:

- whether the order is an object;
- whether the identifier is a non-empty string;
- whether the customer is an object;
- whether the customer name has the expected type;
- whether items are an array;
- whether each item has valid SKU, quantity, and price values.

The validation deliberately distinguishes structural errors from business-value errors. A quantity of `-2` has the correct general numeric type but violates the rule that a quantity must be positive.

### Map for Dynamic Grouping

The grouping implementation uses nested `Map` objects rather than ordinary objects.

The structure is:

`region -> category -> amounts`

`Map` is useful when keys are dynamic and when explicit map operations such as `has()`, `get()`, and `set()` make the grouping logic clearer.

The final reporting structure is converted to ordinary objects for easier output.

### Reference Semantics

JavaScript objects and arrays are reference values. A shallow object spread such as `{ ...original }` copies only the outer object.

Nested arrays remain shared.

The example contrasts this behavior with `structuredClone()`, which recursively copies supported structured data.

Deep copying should not be used automatically. It can be expensive for large structures, and some JavaScript values are not supported by `structuredClone()`. A deliberate data model is often preferable to copying a large object graph repeatedly.

### Asynchronous Nested Processing

The JavaScript program also processes nested batches asynchronously with `Promise.all()`.

Each batch contains its own list of records. A promise calculates the total for that batch, and `Promise.all()` waits for all batch operations.

This is specifically relevant to nested application data because real JavaScript systems frequently receive or process hierarchical records through asynchronous I/O.

## C++ Case Study

The C++ implementation models a warehouse inventory repository.

Each `Product` contains:

- an SKU;
- a name;
- a category;
- a nested `Pricing` structure;
- a vector of `WarehouseStock` records.

A product therefore has a hierarchy similar to:

`product -> pricing -> amount`

and:

`product -> warehouses -> warehouse -> quantity`.

The case study uses typed structures instead of a dynamically typed dictionary. This makes the expected shape explicit at compile time.

### Data Structures

`std::vector<Product>` stores the primary product collection.

`std::vector<WarehouseStock>` stores the variable number of warehouse records belonging to each product.

`std::map` is used for ordered keyed aggregation where predictable key ordering is useful.

`std::unordered_map` is used for SKU and category indexes where average constant-time lookup is valuable.

This separation demonstrates an important design principle: one representation does not need to satisfy every access pattern.

### Validation

The repository validates the nested data when indexes are constructed.

It rejects:

- empty SKUs;
- duplicate SKUs;
- negative product prices;
- empty warehouse cities;
- negative warehouse quantities.

Rejecting invalid data while building the repository prevents later code from operating on an inconsistent index.

Exceptions communicate invalid construction to the caller, while `main()` catches standard exceptions and reports the failure without allowing an unhandled exception to terminate the program unexpectedly.

### SKU Index

The SKU index maps:

`SKU -> Product`

The SKU is unique, so duplicate detection is performed before the index is accepted.

A lookup therefore does not need to scan every product.

The index stores pointers to products already owned by the repository rather than copying every complete `Product`. This reduces copying overhead.

The repository owns the `products_` vector for the lifetime of the indexes, so those pointers remain valid as long as the owning vector is not modified in a way that invalidates them. The implementation does not append to the vector after index construction, which keeps this ownership relationship stable.

### Category Index

The category index maps:

`category -> vector of Product pointers`

A category can contain multiple products, so a single value is insufficient.

The resulting structure allows the application to retrieve all computing products without scanning unrelated display products during each query.

### Warehouse Aggregation

`stockByCity()` traverses every product and every warehouse record and accumulates quantities in a map.

This is a direct example of a nested collection reduction:

`products -> warehouses -> quantity`

The algorithm must inspect every warehouse entry because each entry contributes to the final city totals.

### Inventory Value

`inventoryValue()` calculates total inventory value by summing:

`warehouse quantity × product price`

for every warehouse associated with every product.

The calculation illustrates why hierarchical data often requires traversal across multiple levels rather than a single lookup.

## Relationship Between Lists and Dictionaries

The two structures solve different problems.

| Property | List / Array | Dictionary / Map |
|---|---|---|
| Primary access | Position or iteration | Key |
| Ordering | Usually meaningful | Depends on implementation |
| Duplicate values | Normally allowed | Keys are unique |
| Typical use | Items, rows, batches | Attributes, indexes, named values |
| Nested use | List of records | Record containing attributes |
| Lookup pattern | Usually O(n) scan | O(1) average for hash maps, O(log n) for balanced trees |

A realistic data model frequently combines them rather than choosing one universally.

An order is naturally a dictionary-like record because `customer`, `id`, and `items` have named meanings. `items` is naturally a list because an order can contain many line items in an ordered collection.

## Common Structural Mistakes

### Confusing an Index With a Key

`items[0]` means the first element of an ordered collection.

`customer["name"]` means the value associated with the key `name`.

Treating these as interchangeable leads to incorrect traversal logic.

### Assuming Uniform Nesting

Not every nested structure has the same depth.

A configuration may contain:

`database -> host`

while another branch contains:

`database -> replicas -> replica -> host`.

Traversal code should be designed around the actual data model rather than assuming every branch has identical depth.

### Mutating Shared Nested Containers

Nested containers are frequently referenced rather than copied.

In Python, a shallow copy retains references to nested lists and dictionaries. In JavaScript, object spread and array spread are also shallow operations.

Unintended sharing can cause changes made through one variable to appear in another.

### Assuming Rectangular Matrices

A nested list or vector does not automatically guarantee equal row lengths.

Code accessing `matrix[row][column]` should validate both the row and column when the structure may be irregular.

The C++ program explicitly demonstrates safe nested-vector access through bounds checks.

### Using Exceptions as Normal Lookup Flow

Exceptions are useful for malformed required structures and invalid construction, but optional data should often be handled with explicit defaults or optional values.

The Python program separates required-path access from default-returning access. The C++ program uses `std::optional` for a missing SKU lookup.

## Performance Considerations

Access complexity depends on both the container and the operation.

For a nested list, accessing an element by known index is generally constant time for the individual list operation. Finding an arbitrary value by its content requires a scan.

Traversing an entire nested structure is proportional to the number of contained elements. If there are `n` total nodes, a complete traversal is approximately `O(n)`.

Python dictionaries provide average constant-time key lookup. JavaScript `Map` provides efficient keyed access. C++ `std::unordered_map` provides average constant-time lookup, while `std::map` provides logarithmic lookup.

Building an index has an upfront cost. It is useful when the same lookup is performed repeatedly. For a one-time operation, a full scan may be simpler and can avoid maintaining additional structures.

Deep copying also has a cost proportional to the amount of nested data being copied. For large structures, selective copying or immutable design can be preferable.

## Validation and Data Integrity

Nested structures should be validated at boundaries where untrusted or external data enters an application.

Useful validation checks include:

- expected container type;
- required keys;
- allowed value types;
- numeric ranges;
- non-empty identifiers;
- uniqueness constraints;
- valid relationships between nested fields.

Validation should be specific to the data model. A generic test such as "the object exists" is insufficient when the application requires `items` to be a list containing objects with positive integer quantities.

Malformed nested input should not silently produce partially correct reports.

## Serialization and JSON

JSON is particularly compatible with nested lists and dictionaries because its object and array structures map naturally to hierarchical application data.

A typical JSON representation may contain an object with an array:

`{"products": [{"sku": "LAP-100", "warehouses": [{"city": "Delhi", "quantity": 12}]}]}`

The Python implementation uses `json.dumps()` and `json.loads()`. The JavaScript implementation uses `JSON.stringify()` and `JSON.parse()`.

Serialization creates a data boundary. Application code should validate deserialized data before assuming that required nested fields exist or have the expected types.

## Practical Design Principles

Keep nesting aligned with domain relationships. A warehouse quantity belongs inside a warehouse record because the city and quantity describe one warehouse location.

Use a list when multiple values form a collection. Use a dictionary or map when a key identifies the meaning of a value.

Avoid unnecessary nesting. A deeply nested structure can make validation, access, debugging, and transformation harder.

Preserve the source structure when it represents the domain clearly, then build derived indexes or reporting structures for specific access patterns.

When the data shape is externally supplied, validate it before performing deep access.

When a structure is frequently searched by a unique identifier, consider maintaining an index instead of repeatedly scanning the complete nested collection.

When copying nested data, explicitly decide whether shared references are desirable. Shallow and deep copying have different semantics and different performance costs.

## Debugging Nested Structures

Debugging becomes easier when the structure is inspected at the same level at which the application reasons about it.

For dictionaries and objects, inspect the keys and intermediate values before accessing deeper fields.

For lists and arrays, inspect length and element types before assuming an index exists.

Recursive structures benefit from path-aware diagnostics. The Python and JavaScript traversal functions produce paths such as `profile.addresses.0.city`, which identifies not only the invalid value but also its location within the hierarchy.

For production systems, error messages should identify the affected field or record without exposing sensitive values.

## Security and Reliability

Nested structures frequently originate from APIs, configuration files, uploaded JSON, and other external inputs. Their contents must therefore be treated as untrusted until validated.

Do not assume that a key exists merely because a normal record contains it.

Do not trust numeric fields to be numeric. External JSON can contain strings, null values, negative numbers, or unexpected objects.

Do not recursively process arbitrarily deep untrusted structures without considering resource limits. Deep recursion can consume stack space, while very large nested collections can consume significant memory and processing time.

When serialized data is loaded from an external source, parse it using the intended data format and validate the resulting structure before using it in business logic.

The central reliability principle is that the shape of nested data is part of the application's contract. Correctly handling that shape is as important as handling the individual values stored within it.
