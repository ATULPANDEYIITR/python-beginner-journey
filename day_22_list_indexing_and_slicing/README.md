# List Indexing and Slicing

## Topic introduction

List indexing and slicing are fundamental sequence operations. They provide a precise way to retrieve individual elements, select ranges of elements, traverse data in different directions, modify portions of a collection, and build higher-level operations such as pagination, batching, rolling windows, sampling, and data extraction.

The three implementations in this study use different collection models:

- Python uses the built-in `list` type and provides direct indexing and the compact `start:stop:step` slicing syntax.
- JavaScript uses `Array`, where `slice()` provides range selection and `at()` provides convenient negative indexing.
- C++ uses `std::vector` and develops explicit indexing and slicing utilities because the language does not have Python's built-in slice operator.

The central idea is that a sequence contains ordered elements, and each element can be addressed by a position. A slice describes a region or traversal pattern over those positions.

---

## Fundamental concepts

### Sequence

A sequence is an ordered collection whose elements have positions. Python provides several important sequence types, including:

- `list`
- `tuple`
- `str`
- `range`

JavaScript arrays are ordered collections with numeric indexes.

C++ provides several sequence-oriented containers, with `std::vector` being particularly suitable for random-access indexing and contiguous ranges.

### Index

An index identifies the position of an element.

For a sequence containing:

`["A", "B", "C", "D"]`

the conventional zero-based indexes are:

| Index | Value |
|---:|---|
| 0 | A |
| 1 | B |
| 2 | C |
| 3 | D |

Zero-based indexing means the first element has index `0`, not `1`.

### Position versus value

An index identifies a position. The value is the object stored at that position.

For example, with `values = [10, 20, 30]`:

- `values[0]` means the value at position `0`.
- `values[2]` means the value at position `2`.
- `values.index(30)` in Python searches for the value `30` and returns its first matching position.

This distinction is important when a collection contains duplicate values.

---

## Python indexing

Python indexing uses square brackets.

For a list such as:

`numbers = [10, 20, 30, 40, 50]`

the expressions `numbers[0]`, `numbers[1]`, and `numbers[4]` retrieve individual elements.

The Python implementation demonstrates this progressively through direct access, loops, updates, validation, nested structures, and error handling.

### Positive indexes

Positive indexes count from the beginning:

- `0` means first element.
- `1` means second element.
- `2` means third element.
- `len(values) - 1` means last element.

### Negative indexes

Python supports negative indexes:

- `-1` means last element.
- `-2` means second-last element.
- `-3` means third-last element.

For a five-element list, the relationship is:

| Positive | Negative |
|---:|---:|
| 0 | -5 |
| 1 | -4 |
| 2 | -3 |
| 3 | -2 |
| 4 | -1 |

Negative indexing is especially useful when the desired element is relative to the end.

### Index errors

Ordinary Python indexing requires an existing position.

For example, accessing `values[100]` on a short list raises `IndexError`.

This differs from Python slicing, where boundaries outside the sequence are generally handled by normalization and do not produce an `IndexError`.

---

## Python slicing

The basic Python slice structure is:

`sequence[start:stop]`

The extended form is:

`sequence[start:stop:step]`

The three components have distinct roles:

- `start` identifies where traversal begins.
- `stop` identifies where traversal ends.
- `step` controls the distance and direction between selected positions.

The most important boundary rule is:

**The start boundary is included and the stop boundary is excluded.**

For:

`values[2:6]`

Python selects indexes `2`, `3`, `4`, and `5`.

It does not select index `6`.

This exclusive-stop design makes many calculations convenient because the number of elements in a simple forward slice is often `stop - start`.

---

## Omitted slice boundaries

Python allows boundaries to be omitted.

`values[:5]` means from the beginning through index `4`.

`values[5:]` means from index `5` through the end.

`values[:]` means the entire list.

The full slice is commonly used to create a shallow copy of a list.

---

## Negative slice boundaries

Negative values can be used as slice boundaries.

Examples include:

- `values[-5:]`
- `values[:-2]`
- `values[-7:-2]`

Negative boundaries are interpreted relative to the end of the sequence before the slice is applied.

This is useful for operations such as selecting recent records, the last few measurements, or excluding a suffix.

---

## Slice steps

The third component controls traversal:

`sequence[start:stop:step]`

Examples:

- `values[::2]` selects every second element.
- `values[1::2]` selects every second element starting from index `1`.
- `values[::3]` selects every third element.
- `values[2:15:4]` selects a bounded region with a step of four.

The step cannot be zero. Python raises `ValueError` when a zero step is used.

A positive step moves forward.

A negative step moves backward.

---

## Reverse slicing

`values[::-1]` is a common Python idiom for producing a reversed copy of a list.

A negative step can also be combined with explicit boundaries:

`values[8:2:-1]`

This starts at index `8` and moves toward index `2`, excluding the stop boundary.

Reverse slicing is useful for reverse chronological data, recent-first views, descending traversal, and sequence transformations.

---

## Slice objects

Python exposes the slice operation as a first-class `slice` object.

For example:

`slice(2, 10, 2)`

represents the same boundary information as:

`2:10:2`

The Python implementation uses slice objects to:

- store slicing rules;
- pass slicing behavior into functions;
- inspect `start`, `stop`, and `step`;
- normalize boundaries with `slice.indices()`;
- demonstrate how slicing can be implemented conceptually.

This becomes useful when slice behavior must be represented as data rather than written directly into an expression.

---

## Slice normalization

`slice.indices(length)` converts a slice into concrete boundaries appropriate for a sequence of a specified length.

This is important because Python must account for:

- omitted boundaries;
- negative boundaries;
- very large boundaries;
- positive steps;
- negative steps;
- empty sequences.

The custom `manual_slice()` implementation in the Python script uses normalization and `range()` to demonstrate the conceptual mechanics behind slice selection.

The native Python implementation should still be preferred in production because it is concise, optimized, and directly expresses the intended operation.

---

## Slice assignment

Python slicing is not limited to reading data.

A slice can appear on the left side of an assignment.

For example:

`values[2:5] = [20, 30, 40]`

replaces the selected region.

The replacement may contain a different number of elements when the step is `1`. Therefore slice assignment can:

- replace elements;
- insert elements;
- delete elements;
- change the length of the list.

An empty replacement deletes the selected region.

An empty slice such as `values[2:2]` can be used as an insertion point.

---

## Extended slice assignment

When a non-unit step is used in slice assignment, Python requires the replacement iterable to contain exactly as many elements as the selected positions.

For example:

`values[::2]`

might select five positions.

The replacement therefore must contain exactly five elements.

This restriction prevents ambiguous resizing of non-contiguous selections.

The Python program deliberately demonstrates the `ValueError` produced when the replacement length is incorrect.

---

## Indexing versus slicing

Indexing and slicing produce different types of results.

For:

`values = [10, 20, 30, 40]`

`values[2]` returns one element:

`30`

while:

`values[2:3]`

returns a list:

`[30]`

This distinction is fundamental.

Indexing asks:

> Which single element is located at this position?

Slicing asks:

> Which sequence of elements falls inside this positional range and traversal rule?

---

## Nested list indexing

A list can contain other lists.

For example:

`matrix = [[1, 2], [3, 4]]`

The expression `matrix[0]` retrieves the first row.

The expression `matrix[0][1]` retrieves the second value in that row.

The two indexes operate at different levels:

- first index selects a row;
- second index selects an element inside that row.

The Python implementation demonstrates nested list modification, nested slicing, table processing, and deeper structures.

---

## Nested slicing

Nested structures often require applying a slice at one level and then indexing or slicing at another.

For example:

`matrix[:2]`

selects the first two rows.

A comprehension such as:

`[row[1:3] for row in matrix]`

selects columns `1` and `2` from every row.

The built-in Python list type does not provide multidimensional indexing such as `matrix[0, 1]`. Nested lists require separate indexing operations.

---

## Shallow copies

A normal list slice creates a new outer list.

For example:

`copy = original[:]`

means `copy` and `original` are different list objects.

Changing an element in one outer list does not change the corresponding element in the other outer list when that element is an immutable object.

The distinction becomes important with nested mutable objects.

If:

`original = [[1, 2], [3, 4]]`

and:

`copy = original[:]`

then the outer list is copied but the nested lists are shared.

Consequently:

`copy[0][0] = 999`

also changes the nested list visible through `original`.

The Python implementation compares:

- aliasing;
- slicing;
- `list()`;
- `.copy()`;
- `deepcopy()`.

---

## Deep copying

A deep copy recursively copies nested structures.

Python's `copy.deepcopy()` is used in the study program when independent nested data is required.

Deep copying has a cost. It may require significantly more memory and processing than a shallow copy.

It is therefore a semantic decision rather than an operation that should automatically be used everywhere.

---

## Strings, tuples, and ranges

Indexing and slicing are not limited to lists.

Python strings support indexing and slicing:

`text[0]`

`text[-1]`

`text[1:5]`

`text[::-1]`

Strings are immutable, so their elements cannot be replaced through indexing.

Tuples also support indexing and slicing but are immutable.

`range` objects support indexing and slicing while retaining their range-oriented representation.

This demonstrates a major sequence principle:

**Different sequence types can share indexing and slicing concepts while having different mutation and storage behavior.**

---

## Iterables versus sequences

Not every iterable supports ordinary indexing and slicing.

A generator can be iterated but does not provide direct random-access indexing.

Therefore an expression such as:

`generator[2:5]`

does not work.

There are two common alternatives.

One is to materialize the generator into a list:

`list(generator)[2:5]`

This is simple but can consume substantial memory.

The other is to use `itertools.islice()`.

`islice()` can select a region lazily without first constructing a complete list.

This distinction is important when processing large or streaming datasets.

---

## Practical Python applications

The Python implementation demonstrates several practical uses of indexing and slicing.

### Recent records

`records[-5:]`

is useful when a system needs the latest five records stored in chronological order.

### Pagination

An API-style page can be represented by:

`records[start:start + page_size]`

This is a common model for offset-based pagination.

### Chunking

Repeated slices can divide data into fixed-size batches.

This is useful for:

- batch processing;
- uploads;
- database operations;
- message processing;
- model inference;
- file processing.

### Sliding windows

Overlapping slices can represent moving windows over time-series data.

A window of width three over:

`[10, 20, 30, 40, 50]`

produces:

- `[10, 20, 30]`
- `[20, 30, 40]`
- `[30, 40, 50]`

This pattern is common in analytics and signal processing.

### Rotation

List rotation can be implemented through two slices:

`values[position:] + values[:position]`

This is a useful demonstration of how simple slicing operations can build more complex algorithms.

### Fixed-width text

String slicing can extract fields from fixed-width records.

This technique appears in legacy data formats, structured text files, and certain data-import pipelines.

---

## JavaScript implementation

JavaScript uses `Array` rather than Python's `list`, but many sequence concepts remain similar.

The JavaScript program starts with basic array indexing and progresses through slicing, mutation, nested arrays, typed arrays, pagination, chunking, sliding windows, rotation, performance considerations, and a complete sales-processing example.

---

## JavaScript array indexing

Standard JavaScript array indexing uses:

`array[index]`

Indexes start at zero.

For:

`const values = [10, 20, 30]`

the expressions:

- `values[0]`
- `values[1]`
- `values[2]`

return the three elements.

An important difference from Python is the behavior of negative bracket indexes.

In JavaScript:

`values[-1]`

does not mean the last element.

Instead, it accesses a property named `"-1"` and normally produces `undefined` unless such a property has been explicitly assigned.

Modern JavaScript provides:

`values.at(-1)`

for convenient negative indexing.

---

## JavaScript out-of-range behavior

Accessing an unavailable array position through bracket notation generally returns `undefined`.

For example:

`values[100]`

returns `undefined`.

This differs from Python, where an invalid ordinary list index raises `IndexError`.

The difference matters when porting algorithms between Python and JavaScript.

---

## JavaScript slicing

JavaScript uses:

`array.slice(start, end)`

The start is included and the end is excluded.

For example:

`values.slice(2, 6)`

selects positions `2`, `3`, `4`, and `5`.

JavaScript's `slice()` accepts negative boundaries, making expressions such as:

`values.slice(-5)`

useful for selecting the final five elements.

---

## JavaScript does not have Python's built-in slice step

Python directly supports:

`values[start:stop:step]`

JavaScript's standard `Array.prototype.slice()` accepts only start and end boundaries.

There is no third step argument.

The JavaScript implementation demonstrates stride selection using `filter()` and index calculations, and also provides a `pythonLikeSlice()` helper that implements start, stop, and step behavior explicitly.

This distinction is important when translating algorithms between the two languages.

---

## JavaScript `slice()` versus `splice()`

These methods have very different semantics.

`slice()`:

- creates a new array;
- does not mutate the source array;
- selects a range.

`splice()`:

- changes the source array;
- can delete elements;
- can insert elements;
- can replace elements;
- returns deleted elements.

The JavaScript implementation deliberately demonstrates both operations because confusing them is a common programming error.

---

## JavaScript reversing

JavaScript's `reverse()` mutates the array.

Therefore:

`values.reverse()`

changes `values`.

To create a reversed copy:

`values.slice().reverse()`

This combines a non-mutating copy operation with an in-place reversal of that copy.

---

## JavaScript shallow copying

Common shallow-copy techniques include:

`array.slice()`

`[...array]`

`Array.from(array)`

These create a new outer array.

They do not recursively clone nested objects or arrays.

The JavaScript implementation demonstrates the difference between shallow copying and `structuredClone()` for nested data.

---

## Typed arrays

JavaScript provides typed arrays such as:

`Int32Array`

Typed arrays store fixed-width numeric values and have specialized behavior.

The implementation demonstrates:

- indexed access;
- negative access with `at()`;
- `slice()`;
- `subarray()`.

A particularly important distinction is that:

`typedArray.slice()`

creates a copy, while:

`typedArray.subarray()`

creates a view over the same underlying memory.

Changing the `subarray()` can therefore change the original typed array.

This is a memory-management concept that does not have a direct equivalent in ordinary JavaScript array slicing.

---

## Sparse arrays

JavaScript arrays can contain holes.

For example, an array can have an assigned element at index `0` and another at index `3` while positions `1` and `2` are absent.

A missing element and an explicitly assigned `undefined` value are not identical concepts.

The implementation uses `Object.hasOwn()` to distinguish an absent array property from a property that exists.

Sparse arrays require care because different array methods have different behavior around missing positions.

---

## Array-like objects

Some JavaScript objects have numeric properties and a `length` property but are not actual arrays.

`Array.from()` can convert many such structures into real arrays.

This is useful when working with collection-like values supplied by APIs or browser interfaces.

---

## Array destructuring

Destructuring provides another way to access positional data.

For:

`const [first, second, ...remaining] = values`

the first two positions are assigned to `first` and `second`, while the remaining values are collected into a new array.

Destructuring is not a replacement for slicing, but it is closely related because both express positional extraction.

---

## JavaScript practical applications

The JavaScript implementation includes:

- pagination;
- chunking;
- sliding windows;
- top-N selection;
- transaction filtering;
- feature extraction;
- table processing;
- fixed-width text parsing;
- array rotation;
- moving averages;
- typed-array memory views;
- nested data processing.

These examples demonstrate that indexing and slicing are not isolated syntax features. They are building blocks for larger data-processing operations.

---

## C++ implementation

C++ does not provide Python's `sequence[start:stop:step]` syntax.

The C++ case study therefore builds a slicing model around `std::vector`.

This approach exposes concepts that are often hidden by high-level language syntax:

- bounds checking;
- iterator ranges;
- ownership;
- copying;
- non-owning views;
- memory allocation;
- lifetime;
- complexity;
- validation.

The program uses C++17 and the standard library.

---

## `std::vector` indexing

A vector can be accessed with:

`values[index]`

or:

`values.at(index)`

The two operations differ in bounds checking.

`operator[]` does not perform a runtime bounds check.

An invalid index results in undefined behavior.

`at()` performs bounds checking and throws `std::out_of_range` when the index is invalid.

This is a major C++ reliability consideration.

---

## Negative indexing in C++

C++ vector indexing does not provide Python-style negative indexes.

The case-study program therefore implements `atNegativeAware()`.

The function translates a negative index by adding the vector length.

For example, for a five-element vector:

`-1`

becomes the final position.

The helper also validates the resulting position.

This demonstrates that language features such as negative indexing can be implemented explicitly when they are useful to an application.

---

## C++ slice representation

The case study defines:

`Slice`

with:

- optional start;
- optional stop;
- step.

This represents the conceptual structure of Python-style slicing without relying on language syntax that C++ does not provide.

The implementation then normalizes the slice and iterates over the selected positions.

---

## Slice normalization

A normalized slice contains concrete start, stop, and step values.

Normalization must handle:

- omitted start;
- omitted stop;
- negative boundaries;
- positive steps;
- negative steps;
- empty ranges;
- values outside the collection bounds;
- zero-step errors.

This is a useful example of how a high-level language operation can be decomposed into lower-level algorithmic rules.

---

## Iterator ranges

C++ commonly represents a selected portion of a vector through iterator pairs.

For example, conceptually:

`begin + start`

through:

`begin + stop`

represents a contiguous range.

Constructing a new vector from those iterators copies the selected elements.

This is one of the central C++ mechanisms for range-based processing.

---

## Copying versus viewing

A copied slice creates independent storage.

This provides:

- clear ownership;
- independence from later source changes;
- straightforward lifetime behavior.

The cost is memory and copying time.

A view can instead reference the original vector.

The `VectorWindow` class in the program demonstrates a simple non-owning window.

A non-owning view can avoid copying but introduces a lifetime requirement:

**The source collection must remain alive while the view is being used.**

This trade-off is important in high-performance applications.

---

## Pagination in C++

The `page()` function calculates:

`start = (pageNumber - 1) * pageSize`

and constructs a vector from the corresponding iterator range.

It validates page numbering and page size.

Requests beyond the end return an empty result rather than attempting an invalid iterator range.

This models a practical data-access operation.

---

## Chunking

The C++ `chunk()` function repeatedly constructs bounded ranges.

For example, a sequence of nine values with a chunk size of four produces:

- four elements;
- four elements;
- one element.

The final partial chunk is valid.

This pattern is useful for batch operations.

---

## Sliding windows

The `slidingWindows()` function produces overlapping ranges.

For a width of three:

`[10, 20, 30, 40, 50]`

becomes:

- `[10, 20, 30]`
- `[20, 30, 40]`
- `[30, 40, 50]`

Sliding windows are common in time-series processing, anomaly detection, rolling calculations, and local pattern analysis.

---

## Slice assignment in C++

C++ does not have Python's slice-assignment syntax.

The case study implements replacement using:

- normalized positions;
- `erase()`;
- `insert()`;
- direct assignment for extended slices.

For a normal contiguous range, replacing a range with a different number of elements requires resizing the vector appropriately.

For an extended slice, the selected positions must correspond one-to-one with replacement values.

This demonstrates the implementation complexity that high-level language syntax can conceal.

---

## Realistic C++ case study

The main case study models a sales analytics system.

Each `Sale` contains:

- transaction ID;
- amount;
- region.

`SalesRepository` provides operations for:

- retrieving all records;
- selecting recent records;
- selecting the highest-value transactions;
- filtering by region;
- calculating totals;
- calculating averages.

`AnalyticsPipeline` then provides:

- latest-record extraction;
- positional sampling;
- highest-value selection;
- batch generation.

The system uses vectors, sorting, filtering, accumulation, slicing-like ranges, validation, exceptions, and test assertions.

This makes the C++ implementation substantially different from a collection of isolated syntax demonstrations.

---

## Important distinctions

### Python list versus JavaScript array

| Concept | Python | JavaScript |
|---|---|---|
| Primary collection | `list` | `Array` |
| First index | `0` | `0` |
| Negative bracket index | Supported | Not supported |
| Negative convenience access | `values[-1]` | `values.at(-1)` |
| Slice method | `values[start:stop]` | `values.slice(start, end)` |
| Built-in slice step | Yes | No |
| Out-of-range ordinary index | `IndexError` | `undefined` |
| Slice mutation | Possible with assignment | Use `splice()` for mutation |
| Slice copy | New outer list | New array |
| Nested copy | Shallow by default | Shallow by default |

### Python list versus C++ vector

| Concept | Python | C++ |
|---|---|---|
| Indexing | `values[index]` | `values[index]` |
| Checked indexing | Raises `IndexError` | `values.at(index)` |
| Negative indexing | Built in | Must be implemented |
| Built-in slicing syntax | Yes | No |
| Range selection | Slice expression | Iterator range or custom view |
| Slice copy | New list | New vector |
| Non-owning view | Not the normal list-slice behavior | Can be explicitly designed |
| Mutation | Built into list operations | Explicit container operations |

---

## Edge cases

### Empty list

For an empty Python list:

- `values[:]` produces an empty list.
- `values[::-1]` produces an empty list.
- `values[0]` raises `IndexError`.

The JavaScript equivalent generally produces:

- `[]` for `slice()`;
- `undefined` for an unavailable index.

C++ `std::vector::at(0)` throws `std::out_of_range`.

### Single-element collections

Single-element sequences expose many boundary assumptions.

Operations such as:

`values[:3]`

and:

`values[-3:]`

remain valid in Python even when the requested range is larger than the collection.

### Very large slice boundaries

Python slice boundaries can exceed the sequence length without producing an ordinary indexing error.

For example:

`values[:100000]`

simply stops at the end.

This differs from ordinary indexing.

### Empty ranges

A valid slice can produce no elements.

For example:

`values[4:2]`

with a positive step is empty because traversal cannot move forward from the start to the stop.

Reverse slices follow the opposite directional rule.

### Zero step

A zero step is invalid.

Python raises `ValueError`.

The C++ and JavaScript custom slicing implementations explicitly reject a zero step.

---

## Common mistakes

### Confusing index with position

If a list has five elements, the first element is at index `0`, not index `1`.

### Forgetting that the stop boundary is exclusive

For:

`values[2:5]`

index `5` is not included.

### Assuming slices mutate the original

Python list slicing produces a new list.

JavaScript `slice()` also produces a new array.

C++ range construction into a new vector also creates independent storage.

Mutation requires a separate operation.

### Confusing `slice()` and `splice()` in JavaScript

`slice()` does not mutate the source.

`splice()` does.

### Assuming JavaScript `array[-1]` means the last element

Use:

`array.at(-1)`

for negative positional access.

### Assuming Python shallow copies are deep copies

A list slice copies the outer list but does not recursively clone nested mutable objects.

### Using unchecked C++ indexes with untrusted input

`operator[]` does not provide bounds checking.

Validate indexes before using them.

### Converting large generators to lists unnecessarily

`list(generator)` materializes all generated values.

For large streams, `itertools.islice()` can provide lazy selection.

### Ignoring allocation cost

A copied slice requires memory proportional to the number of selected elements.

This can matter significantly when processing large datasets.

---

## Performance considerations

For a Python list:

- indexed access is generally `O(1)`;
- selecting `k` elements through a slice is generally `O(k)`;
- the resulting slice requires storage for the selected references;
- inserting or deleting in the middle can require shifting elements.

For a JavaScript array:

- indexed access is generally constant-time for ordinary dense arrays;
- `slice()` requires copying the selected region;
- `splice()` can require shifting elements;
- repeated front operations such as `shift()` can be costly for large collections.

For a C++ `std::vector`:

- `operator[]` is constant-time;
- `at()` is constant-time apart from bounds checking;
- copying `k` elements is `O(k)`;
- insertion or deletion in the middle is generally `O(n)` because elements may need to move;
- sorting is typically `O(n log n)`;
- non-owning views can avoid copying when lifetime requirements are satisfied.

Complexity should be considered together with memory behavior. An operation that is computationally inexpensive can still create a large temporary allocation.

---

## Memory considerations

A list or array slice usually represents a new outer collection.

For nested data, the elements may still refer to shared objects.

This creates the shallow-copy behavior demonstrated in both the Python and JavaScript implementations.

C++ vectors have explicit ownership semantics. Copying a vector creates independent storage for its elements.

A C++ non-owning view, such as the `VectorWindow` case study, avoids the copy but does not own the selected data.

The source object must therefore outlive the view.

---

## Security and reliability considerations

Indexing and slicing become security-relevant when boundaries are controlled by external input.

Important practices include:

- validate indexes before accessing collections;
- distinguish signed and unsigned values in C++;
- check calculations such as `offset + limit` for overflow;
- avoid allocating unbounded slices based directly on external input;
- impose reasonable maximum page sizes;
- avoid dereferencing invalid C++ iterators;
- use checked access when invalid indexes must be handled safely;
- preserve lifetime guarantees for non-owning views;
- avoid accidental mutation when processing data that should remain unchanged.

For example, an API accepting `offset` and `limit` should validate both values before constructing a result.

---

## Implementation considerations

### When copying is appropriate

Copying is useful when:

- the selected data must outlive the original;
- independent mutation is required;
- ownership should be obvious;
- the selected collection is small enough that the allocation is acceptable.

### When a view is appropriate

A view is useful when:

- data should not be copied;
- processing is temporary;
- the source lifetime is controlled;
- read-only access is sufficient;
- performance or memory pressure makes copying undesirable.

### When direct indexing is appropriate

Direct indexing is appropriate when a precise position is known.

It is not appropriate when the requirement is actually a condition such as:

"return all values greater than 100."

That is filtering, not indexing.

---

## Testing considerations

The Python implementation uses `assert` statements to verify:

- first and last indexes;
- ordinary slices;
- negative slices;
- reverse slicing;
- empty collections.

The JavaScript implementation provides a custom `assert()` function and checks:

- ordinary indexing;
- negative access;
- standard slicing;
- reverse operations;
- custom step slicing.

The C++ program uses the standard `assert` facility to verify:

- slice boundaries;
- reverse slices;
- stride behavior;
- pagination;
- chunking.

Testing boundary conditions is especially important for indexing because off-by-one errors are common.

---

## Production design principles

A production implementation should make the intended behavior explicit.

If a function accepts an index:

- document whether negative indexes are accepted;
- define what happens when the index is invalid;
- validate external input.

If a function accepts a slice:

- define whether the stop boundary is exclusive;
- define whether negative indexes are supported;
- define whether a zero step is permitted;
- define whether the result is copied or viewed;
- define ownership and lifetime requirements when using views.

If a function implements pagination:

- define whether page numbering begins at zero or one;
- validate page size;
- impose reasonable limits;
- handle requests beyond the end consistently.

These decisions become part of the API contract.

---

## Conceptual relationship between indexing and slicing

Indexing and slicing can be understood as two levels of positional selection.

Indexing selects a single position:

`sequence[index]`

Slicing selects multiple positions according to a boundary and traversal rule:

`sequence[start:stop:step]`

Many larger operations can be constructed from these primitives.

Examples include:

- pagination;
- batching;
- recent-record extraction;
- sampling;
- rolling windows;
- rotation;
- top-N selection;
- fixed-width parsing;
- feature extraction;
- table processing.

This is why indexing and slicing are foundational concepts rather than isolated syntax rules.

---

## Language-specific implementation comparison

The Python implementation emphasizes the semantics of built-in slicing.

It demonstrates the full `start:stop:step` model, slice objects, slice assignment, negative indexing, sequence behavior, nested structures, shallow copying, and lazy alternatives.

The JavaScript implementation emphasizes how similar concepts are expressed through array methods and language-specific behavior.

It demonstrates `at()`, `slice()`, `splice()`, destructuring, filtering, typed arrays, `subarray()`, copying, sparse arrays, and application-level collection utilities.

The C++ implementation focuses on the lower-level mechanisms required to build these abstractions explicitly.

It demonstrates:

- `std::vector`;
- bounds checking;
- optional slice parameters;
- normalization;
- iterator ranges;
- copying;
- non-owning views;
- replacement;
- pagination;
- batching;
- sliding windows;
- performance;
- validation;
- ownership;
- lifetime considerations;
- a complete sales analytics system.

The three implementations therefore demonstrate the same conceptual domain through different programming models rather than simply duplicating syntax.

---

## C++ case study architecture

The C++ case study models a transaction analytics system.

### `Sale`

Represents one transaction with:

- `transactionId`;
- `amount`;
- `region`.

### `SalesRepository`

Encapsulates a collection of transactions and provides:

- complete record access;
- recent transaction extraction;
- top-value selection;
- region filtering;
- total calculation;
- average calculation.

### `AnalyticsPipeline`

Provides higher-level operations:

- recent records;
- positional sampling;
- highest-value records;
- fixed-size batches.

### `Slice`

Represents a generalized slicing rule:

- optional start;
- optional stop;
- step.

### `normalizeSlice()`

Converts flexible slice boundaries into concrete traversal information.

### `slice()`

Creates a new vector containing the selected elements.

### `VectorWindow`

Represents a non-owning selected region.

It avoids copying but requires the original vector to remain valid.

---

## Real-world relevance

Indexing and slicing appear throughout software systems.

### Data engineering

Large collections are divided into manageable batches and windows.

### APIs

Offset and limit pagination can be represented through range selection.

### Financial systems

Recent transactions, historical windows, top-value records, and rolling statistics depend on positional data selection.

### Monitoring

Recent logs and recent sensor readings are commonly selected using tail-oriented operations.

### Machine learning

Feature matrices and batches require controlled extraction of subsets of data.

### Web applications

JavaScript arrays frequently represent API results, table rows, search results, and application state.

### Systems programming

C++ applications often require explicit control over copying, memory, iterator validity, and views.

### Text processing

String indexing and substring extraction support parsing of structured or fixed-width records.

---

## Key rules

1. Sequence indexes normally begin at zero.
2. Python supports negative indexes directly.
3. JavaScript uses `at()` for convenient negative indexing.
4. C++ requires explicit handling for negative indexing.
5. Python slices use `start:stop:step`.
6. Slice starts are inclusive.
7. Slice stops are exclusive.
8. A positive step moves forward.
9. A negative step moves backward.
10. A zero step is invalid.
11. Python slices normally create new outer lists.
12. JavaScript `slice()` creates a new array.
13. JavaScript `splice()` mutates the source array.
14. C++ range copies create independent vectors.
15. C++ views can avoid copying but require careful lifetime management.
16. Slice assignment can change Python list length.
17. Extended Python slice assignment requires matching replacement lengths.
18. Nested slicing does not automatically perform multidimensional selection.
19. Indexing and slicing are positional operations.
20. Filtering is condition-based selection.
21. Large slices can consume significant memory.
22. Bounds validation is important when indexes originate from external input.
23. Off-by-one errors frequently occur at slice boundaries.
24. Performance depends on whether a selected region is copied or viewed.
25. Collection semantics should be documented when designing production APIs.
