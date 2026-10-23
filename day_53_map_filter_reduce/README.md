# `map()`, `filter()`, and `reduce()`

## Scope

`map()`, `filter()`, and `reduce()` are collection-processing operations with three distinct responsibilities:

- **Map** transforms every selected input element into a new representation.
- **Filter** selects elements that satisfy a predicate.
- **Reduce** combines multiple elements into one accumulated result.

A useful mental model is:

`collection → filter → map → reduce → result`

The order is not mandatory. A transformation may occur before filtering when the transformed value is the value needed by the predicate. The important distinction is that transformation, selection, and aggregation are different operations.

The five implementations use the same conceptual domain of structured business data while emphasizing different mechanisms available in each language.

## Conceptual distinction

| Operation | Input | Output | Typical purpose |
|---|---|---|---|
| `map()` | Many elements | Many elements | Transform each element |
| `filter()` | Many elements | Zero or more elements | Select qualifying elements |
| `reduce()` | Many elements | Usually one value | Aggregate or fold elements |

A mapping preserves the number of elements unless a separate operation changes the collection. Filtering can reduce the collection size. Reduction collapses a collection into an accumulated result.

For example, given values `[-4, -2, 1, 3, 5]`:

`map(x → 2x)` produces `[-8, -4, 2, 6, 10]`.

`filter(x → x > 0)` then produces `[2, 6, 10]`.

`reduce((total, x) → total + x, 0)` produces `18`.

The initial value `0` is important because it defines the result when the input collection is empty.

## Python implementation

The Python program defines reusable `map_items()`, `filter_items()`, and `reduce_items()` functions around the standard-library `map()`, `filter()`, and `functools.reduce()` operations.

The domain model uses an immutable `Employee` dataclass. Validation rejects invalid identifiers, empty names, missing departments, and negative salaries before processing begins.

The employee workflow separates the three operations:

- `filter()` selects active employees meeting the salary eligibility rule.
- `map()` calculates an eight-percent salary projection for every eligible employee.
- `reduce()` calculates the current and projected salary totals.

The program also demonstrates a composed pipeline and a generator-based pipeline. Generators are useful when input is large because they can provide values incrementally rather than requiring every intermediate value to exist as a list.

The explicit initial value supplied to `reduce()` makes an empty reduction safe. Without an initial value, Python's `reduce()` raises an exception for an empty iterable.

The Python implementation uses separate functions because validation, selection, transformation, and aggregation have different responsibilities. This also makes individual stages easier to test and debug.

## JavaScript implementation

The JavaScript program models an order-processing workflow using immutable `Order` objects.

`Array.prototype.filter()` selects paid orders whose amount meets the revenue threshold. `map()` converts those orders into reporting objects containing the original amount, processing fee, and calculated amount. `reduce()` aggregates those reporting objects into one report containing counts, totals, and regional amounts.

The implementation also uses an asynchronous boundary through `loadOrders()`. This represents a realistic point where collection data might arrive from an API, queue, or file without requiring an external dependency.

JavaScript's `reduce()` is particularly flexible because the accumulator does not have to be a number. In the example it is an object containing multiple aggregate values:

`{ orderCount, grossTotal, feeTotal, netTotal, regions }`

An explicit initial accumulator is supplied. This prevents an empty collection from causing the usual `reduce()` failure associated with missing initial state.

The program validates input before processing it and freezes individual order objects. This reduces accidental mutation during a pipeline where the same records may be consumed by several operations.

## C++ implementation

The C++17 program uses a repository-governance-style record model to show the same concepts through standard algorithms rather than JavaScript-style array methods.

`std::copy_if` performs the filtering role by selecting approved changes.

`std::transform` performs the mapping role by converting repository records into governance evaluations. Each evaluation records whether the change is merge eligible and, when it is not, identifies the failed condition.

`std::accumulate` performs the reduction role by aggregating changed-line counts for merge-eligible changes.

The C++ implementation deliberately separates these stages because the standard algorithms expose different semantics. This makes the governance rules explicit and allows each operation to be reasoned about independently.

The program also demonstrates that a reduction does not have to produce a scalar. An aggregation can construct a map from authors to their total changed lines. This illustrates the broader concept of a fold: an accumulator can have a structured state.

The implementation validates repository records before processing. Invalid identifiers, empty titles or authors, and negative line counts are rejected.

For `n` records, the primary processing operations are linear, giving approximately `O(n)` time. The author aggregation uses an `unordered_map`, providing expected constant-time insertion and lookup per record and `O(n)` expected total processing time.

## Java implementation

The Java 17 implementation uses records, enums, immutable collections, functional interfaces, and streams to model an enterprise order workflow.

The `Order` record validates its domain invariants at construction time. `OrderStatus` restricts status values to a fixed set.

The reusable generic methods:

- `map()` accept a `Function<T, R>`.
- `filter()` accept a `Predicate<T>`.
- `reduce()` accept an identity and a `BinaryOperator<T>`.

This gives the operations explicit type relationships rather than relying on untyped values.

The business workflow filters paid orders above the revenue threshold, maps them into `OrderProjection` records, and reduces their monetary amounts into a total. Department revenue is calculated with stream grouping and summation.

Java streams are lazy until a terminal operation is reached. Intermediate `filter()` and `map()` operations describe the pipeline, while operations such as `reduce()`, `collect()`, and `toList()` trigger processing.

Immutable records are appropriate for this example because collection pipelines should generally avoid modifying their source elements while they are being transformed or aggregated.

## PostgreSQL implementation

The PostgreSQL script represents collection processing through relational operations.

The database contains:

- `department`
- `customer`
- `sales_order`

Foreign keys enforce relationships between these entities, while `CHECK` constraints prevent negative amounts and blank names.

The `order_projection` view provides a reusable map-like projection. It derives service fees and fee-inclusive amounts from stored order values.

SQL filtering is expressed with `WHERE`. The revenue query selects paid orders whose amounts satisfy the business threshold.

SQL aggregation provides the reduction stage. `SUM`, `COUNT`, and `AVG` combine multiple rows into aggregate results.

A CTE named `eligible_orders` makes the filter stage explicit. A second CTE named `projected_orders` derives a mapped value before the final aggregation. This produces a direct relational representation of a filter-map-reduce pipeline:

`eligible_orders → projected_orders → aggregate`

The `eligible_revenue()` function encapsulates a reusable reduction and returns zero for an empty result through `COALESCE`.

The transaction section demonstrates database-level integrity enforcement. An invalid negative amount violates the `CHECK` constraint, and a savepoint provides a controlled transactional boundary.

The index on `(status, amount)` supports queries that repeatedly restrict orders by status and amount. The department index supports joins and grouping by department.

## Empty collections and identity values

Reduction is the operation where empty input requires the most careful design.

For addition, the identity is `0`:

`0 + x = x`

For multiplication, the identity is `1`:

`1 × x = x`

For concatenation, the identity is an empty sequence.

Using an identity value makes the reduction total over an empty collection. This is safer in production systems because an empty dataset is often a valid business condition rather than an exceptional programming error.

The identity must match the accumulator operation. Choosing an incorrect initial value changes the result.

## Composition and evaluation order

The operations become especially useful when composed.

A common pipeline is:

`input → filter → map → reduce`

The filter can reduce the number of elements processed by later stages. If mapping is computationally expensive, filtering first can therefore improve performance when the predicate does not depend on the mapped representation.

The reverse order can be correct when the filtering condition depends on a calculated value:

`input → map → filter → reduce`

The choice should follow data dependencies rather than a fixed rule.

For example, if eligibility depends on `salary * 1.08`, the salary projection must exist before that condition can be evaluated.

## Performance considerations

For a collection containing `n` elements, an ordinary map, filter, or reduction is generally `O(n)`.

A sequence of three independent passes is still `O(n)` asymptotically:

`O(n) + O(n) + O(n) = O(n)`

The constant cost can still matter for very large collections. Some runtimes can fuse operations, use lazy evaluation, or process elements without creating intermediate collections.

Python's generator pipeline is useful for this reason. Java streams can also evaluate intermediate operations lazily. JavaScript array methods normally create new arrays for `map()` and `filter()`, so large pipelines can require additional memory.

C++ standard algorithms can operate over iterator ranges and can be combined with data structures selected for the specific workload.

PostgreSQL performs the operations inside the database engine, where indexes, query planning, joins, aggregation strategies, and available memory influence the execution plan.

## Correctness and failure modes

A pipeline should distinguish invalid data from valid empty data.

Invalid data should normally be rejected through validation or constraints. Empty input should normally produce an identity result where the operation has a well-defined identity.

Typical failure conditions include:

- calling a reduction without handling an empty collection;
- applying a transformation to malformed records;
- using a filter predicate that does not represent the intended business rule;
- mutating source objects during a transformation;
- choosing an accumulator whose type does not represent all possible results;
- performing an expensive transformation before a selective filter;
- allowing floating-point arithmetic to represent monetary values without considering rounding requirements.

The examples use explicit validation and rounded monetary calculations where financial-style values are involved.

## Relationship between the three operations

`map()` answers:

**What should each element become?**

`filter()` answers:

**Which elements should remain?**

`reduce()` answers:

**How should the remaining elements be combined?**

They are complementary rather than interchangeable.

A mapping should not secretly remove elements. A filter should not unexpectedly transform their representation. A reduction should make its accumulator semantics clear.

Keeping those responsibilities separate produces pipelines that are easier to test, optimize, inspect, and change.

## Cross-language correspondence

| Concept | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Map | `map()` | `Array.map()` | `std::transform` | `Stream.map()` | Derived expressions / CTE |
| Filter | `filter()` | `Array.filter()` | `std::copy_if` | `Stream.filter()` | `WHERE` |
| Reduce | `functools.reduce()` | `Array.reduce()` | `std::accumulate` | `Stream.reduce()` | `SUM`, `COUNT`, `AVG`, aggregates |
| Empty reduction | Explicit initial value | Explicit initial value | Initial accumulator | Identity value | `COALESCE` |
| Validation | Exceptions | Type checks / exceptions | Exceptions | Record validation / exceptions | Constraints |
| Structured result | Dictionaries / dataclasses | Objects | Structs / maps | Records / maps | Rows / aggregates |

## Practical design boundary

These operations are most useful when each stage has one clear responsibility.

A robust pipeline can therefore be viewed as:

`validated input → selection policy → transformation → aggregation → validated result`

That structure is visible in all five implementations even though the languages provide different abstractions for expressing it.
