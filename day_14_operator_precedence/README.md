# Operator precedence in Python

## Introduction

Operator precedence defines the priority Python gives to different operators when several operators appear in the same expression. It determines how an expression is grouped before Python evaluates it.

For example, the expression `2 + 3 * 4` produces `14` because multiplication has higher precedence than addition. Python effectively groups it as `2 + (3 * 4)`.

Parentheses can explicitly change that grouping:

`(2 + 3) * 4`

produces `20`.

Operator precedence is closely related to, but different from, associativity. Precedence answers which operator binds more strongly. Associativity determines how operators at the same precedence level are grouped.

The Python script accompanying this README develops these concepts through executable examples, assertions, AST inspection, bytecode inspection, custom operator implementations, short-circuit evaluation, and a small precedence-aware expression parser.

## Fundamental terminology

### Operator

An operator is syntax that performs or requests an operation.

Examples include:

- `+`
- `-`
- `*`
- `/`
- `//`
- `%`
- `**`
- `==`
- `<`
- `and`
- `or`
- `not`
- `&`
- `|`
- `^`
- `<<`
- `>>`

Operators can be unary, binary, or part of specialized language constructs.

A unary operator acts on one operand:

`-value`

A binary operator works with two operands:

`left + right`

### Operand

An operand is a value on which an operator acts.

In:

`10 + 5`

`10` and `5` are operands, while `+` is the operator.

### Expression

An expression is a syntactic construct that produces a value.

Examples include:

`2 + 3`

`name.upper()`

`x > 10`

`"adult" if age >= 18 else "minor"`

Expressions can be nested inside larger expressions.

### Precedence

Precedence determines which operators bind more strongly when explicit parentheses are absent.

For example:

`2 + 3 * 4`

is grouped as:

`2 + (3 * 4)`

because `*` has higher precedence than `+`.

### Associativity

Associativity determines grouping when operators have the same precedence.

For example:

`10 - 5 - 2`

is grouped from left to right:

`(10 - 5) - 2`

Exponentiation is a notable exception:

`2 ** 3 ** 2`

is grouped from right to left:

`2 ** (3 ** 2)`

## Python operator precedence

A useful high-level ordering, from stronger to weaker binding, is:

| Relative level | Operators or constructs |
|---|---|
| Highest | Parenthesized expressions, function calls, indexing, attribute access |
| | `await` |
| | `**` |
| | Unary `+`, unary `-`, `~` |
| | `*`, `@`, `/`, `//`, `%` |
| | `+`, `-` |
| | `<<`, `>>` |
| | `&` |
| | `^` |
| | `\|` |
| | Comparisons, `in`, `not in`, `is`, `is not` |
| | `not` |
| | `and` |
| | `or` |
| | Conditional expression `if ... else` |
| | `lambda` |
| Lowest | Assignment expression `:=` |

This is a practical study reference rather than a replacement for Python's complete grammar. Some syntax, especially comprehensions, unpacking, assignment statements, and special constructs, has its own grammatical rules.

## Parentheses

Parentheses explicitly control grouping.

Without parentheses:

`2 + 3 * 4`

Python evaluates the multiplication first.

With parentheses:

`(2 + 3) * 4`

the addition is performed first.

Parentheses therefore have two important roles:

1. They can change the meaning of an expression.
2. They can document intended grouping even when they do not change the result.

For example:

`3 + 4 * 2 ** 3 - 5`

can be written conceptually as:

`3 + (4 * (2 ** 3)) - 5`

The additional parentheses do not change the result. They expose the structure selected by Python's precedence rules.

## Function calls, indexing, and attribute access

Function calls, indexing, and attribute access bind very strongly.

For example:

`numbers[1] + 5`

means that `numbers[1]` is evaluated before addition.

Likewise:

`text.upper()[0]`

first accesses the `upper` attribute, calls the method, and then indexes the returned string.

Expressions inside the call, index, or attribute operation are still governed by ordinary expression rules.

For example:

`numbers[1 + 1]`

evaluates `1 + 1` to obtain the index.

## Exponentiation

Exponentiation uses `**`.

Examples include:

`2 ** 3`

and:

`2 ** 3 * 4`

The second expression is grouped as:

`(2 ** 3) * 4`

because exponentiation has higher precedence than multiplication.

Exponentiation is also right-associative:

`2 ** 3 ** 2`

means:

`2 ** (3 ** 2)`

and therefore evaluates to `512`.

It does not mean:

`(2 ** 3) ** 2`

which evaluates to `64`.

This is one of the most important associativity exceptions in Python arithmetic.

## Unary operators and exponentiation

Python has a subtle relationship between unary operators and exponentiation.

The expression:

`-2 ** 2`

is interpreted as:

`-(2 ** 2)`

and therefore produces `-4`.

The expression:

`(-2) ** 2`

explicitly makes `-2` the base and produces `4`.

This distinction is important whenever a negative value is intended to be the base of a power operation.

Using parentheses is the clearest approach when the negative number itself is the intended base.

## Multiplicative operators

The multiplicative group includes:

- `*`
- `@`
- `/`
- `//`
- `%`

They share the same precedence level.

When operators at the same level occur together, their grouping is normally left to right.

For example:

`100 / 10 * 2`

means:

`(100 / 10) * 2`

It does not mean:

`100 / (10 * 2)`

The same principle applies to combinations of multiplication, division, floor division, modulo, and matrix multiplication.

### Floor division

`//` performs floor division.

For positive values:

`7 // 3`

produces `2`.

For negative values, floor division moves toward negative infinity rather than simply truncating toward zero.

For example:

`-7 // 3`

produces `-3`.

### Modulo

`%` computes the remainder according to Python's floor-division relationship.

For example:

`7 % 3`

produces `1`.

For negative operands, the result follows Python's mathematical relationship between floor division and modulo, so understanding `//` and `%` together is important.

## Addition and subtraction

Addition and subtraction have the same precedence and associate from left to right.

Therefore:

`20 - 5 + 2`

means:

`(20 - 5) + 2`

not:

`20 - (5 + 2)`

This is a general principle for operators that share a precedence level.

## Shift operators

Python provides:

- `<<`
- `>>`

Shift operators have lower precedence than addition and subtraction.

Therefore:

`1 << 2 + 1`

means:

`1 << (2 + 1)`

rather than:

`(1 << 2) + 1`

This distinction is particularly relevant in low-level programming and bit manipulation.

## Bitwise operators

Python's main binary bitwise operators are:

- `&`
- `^`
- `|`

Their precedence is ordered:

`&` before `^` before `|`.

Therefore:

`1 | 2 ^ 3 & 4`

is grouped according to that hierarchy.

Bitwise operators should not be confused with the Boolean operators:

- `and`
- `or`
- `not`

Although the concepts may appear related in informal discussion, they have different semantics, precedence, and evaluation behavior.

## Comparison operators

Comparison operators include:

- `<`
- `<=`
- `>`
- `>=`
- `==`
- `!=`
- `in`
- `not in`
- `is`
- `is not`

Comparisons generally produce Boolean results.

Arithmetic operations have higher precedence than comparisons.

Therefore:

`5 + 2 > 6`

means:

`(5 + 2) > 6`

not an operation in which the comparison is performed before the addition.

## Chained comparisons

Python supports comparison chains such as:

`0 <= score <= 100`

This is a particularly useful feature for range checks.

It expresses the logical relationship:

`score >= 0 and score <= 100`

while evaluating the middle operand only once.

Comparison chains can also mix comparison operators:

`10 < value == 50`

A chained comparison should not be interpreted as a sequence of ordinary binary operations such as:

`(10 < value) == 50`

Python treats the chain as a comparison structure with multiple comparisons.

## Membership operators

The membership operators are:

- `in`
- `not in`

Examples include:

`"banana" in items`

and:

`"pear" not in items`

Membership comparisons belong to the comparison portion of the precedence hierarchy.

Therefore:

`role in allowed and active`

is grouped as:

`(role in allowed) and active`

## Identity operators

The identity operators are:

- `is`
- `is not`

Identity and equality are different concepts.

`==` tests whether two objects are equal in value.

`is` tests whether two references identify the same object.

For example, two separately created lists can satisfy:

`list_a == list_b`

while:

`list_a is list_b`

is false.

For `None`, the conventional identity checks are:

`value is None`

and:

`value is not None`

Using `is` for `None` makes the intended identity test explicit.

## The `not` operator

`not` performs logical negation.

Examples include:

`not True`

and:

`not value`

Comparison operators have higher precedence than `not`.

Therefore:

`not value == expected`

is grouped as:

`not (value == expected)`

The expression:

`value != expected`

is often clearer when the intent is simply inequality.

Similarly:

`not value is None`

is grouped as:

`not (value is None)`

although `value is None` or `value is not None` is normally clearer depending on the intended condition.

## The `and` operator

`and` has lower precedence than comparisons and `not`, but higher precedence than `or`.

One important Python-specific property is that `and` does not necessarily return `True` or `False`.

It returns one of its operands.

For example:

`"hello" and 123`

returns `123`.

An empty string is falsy:

`"" and 123`

returns `""` without evaluating the right operand.

The general behavior is:

- If the left operand is falsy, return it.
- Otherwise evaluate and return the right operand.

## The `or` operator

`or` also returns operands rather than necessarily producing a Boolean object.

For example:

`"value" or "fallback"`

returns `"value"`.

But:

`"" or "fallback"`

returns `"fallback"`.

The general behavior is:

- If the left operand is truthy, return it.
- Otherwise evaluate and return the right operand.

This makes `or` useful for fallback expressions.

## `and` before `or`

`and` has higher precedence than `or`.

Therefore:

`A or B and C`

means:

`A or (B and C)`

It does not mean:

`(A or B) and C`

Parentheses should be used when a different grouping is intended.

This is especially important in business rules, authorization logic, filtering conditions, and validation code.

## Short-circuit evaluation

Precedence determines grouping, but it does not determine whether every operand is evaluated.

Python's Boolean operators short-circuit.

For:

`A and B`

Python does not evaluate `B` if `A` is falsy.

For:

`A or B`

Python does not evaluate `B` if `A` is truthy.

This affects both performance and correctness.

For example:

`value is not None and value.process()`

does not attempt to call `process()` when `value` is `None`.

Short-circuiting can also avoid expensive computations:

`cheap_condition and expensive_check()`

If `cheap_condition` is false, `expensive_check()` is not called.

Side effects inside Boolean expressions require care because the right-hand side may never execute.

## Conditional expressions

Python supports conditional expressions with this structure:

`value_if_true if condition else value_if_false`

For example:

`"adult" if age >= 18 else "minor"`

The condition is evaluated first, and only the selected value expression is evaluated.

Most arithmetic and comparison operations bind more strongly than the conditional expression.

For example:

`10 + 5 if condition else 20`

selects between the result of `10 + 5` and `20`.

Conditional expressions are useful for concise value selection. Excessive nesting can make them difficult to read.

## Lambda expressions

A lambda expression has the form:

`lambda parameters: expression`

For example:

`lambda x: x * x`

creates a function that returns the square of its argument.

Lambda expressions have very low precedence.

Their bodies are expressions, so the operators inside the body continue to follow normal precedence rules.

For example:

`lambda x: x + 2 * 3`

evaluates the multiplication before the addition when the lambda is called.

## Assignment expressions

The assignment expression operator is:

`:=`

It assigns a value while also producing that value as part of an expression.

For example:

`(length := len("Python")) > 3`

assigns the length and then uses it in the comparison.

Assignment expressions have very low precedence and often require parentheses for clarity or because the surrounding syntax requires explicit grouping.

They are different from ordinary assignment statements such as:

`length = len("Python")`

The ordinary assignment statement is not simply another binary operator in the precedence hierarchy.

## `and` and `or` return operands

This behavior deserves special attention because it can create useful patterns and subtle bugs.

For example:

`value = user_value or default_value`

uses the default whenever `user_value` is falsy.

That means all of these values can trigger the fallback:

- `0`
- `False`
- `""`
- `[]`
- `{}`
- `None`

If `0` is a legitimate value and should not trigger the fallback, an explicit `None` test is safer:

`value = user_value if user_value is not None else default_value`

## Operator precedence and types

Precedence determines grouping, but it does not determine the runtime meaning of an operator for every type.

For example:

`5 + 3`

performs numeric addition.

`"5" + "3"`

performs string concatenation.

`[5] + [3]`

concatenates lists.

The syntax is similar, but Python's object model determines the operation implemented by the operands.

This distinction becomes especially important with operator overloading.

## Operator overloading

Classes can define special methods that implement operators.

Examples include:

- `__add__`
- `__sub__`
- `__mul__`
- `__truediv__`
- `__pow__`
- `__lt__`
- `__eq__`
- `__and__`
- `__or__`
- `__xor__`
- `__matmul__`

For example, a custom class can implement `__add__` so that:

`left + right`

performs a domain-specific operation.

The important distinction is that custom methods do not change Python's precedence rules.

For:

`left + right * third`

Python still groups the expression as:

`left + (right * third)`

The custom class determines what `+` and `*` do after Python has established the expression's structure.

## Matrix multiplication

Python provides `@` for matrix multiplication.

It belongs to the multiplicative operator group.

This means it has the same precedence level as:

- `*`
- `/`
- `//`
- `%`

Libraries such as numerical computing libraries commonly give `@` meaningful matrix semantics, but the language-level precedence remains fixed.

## Comprehensions

Expressions inside list, set, and dictionary comprehensions follow normal precedence rules.

For example:

`[number ** 2 for number in numbers]`

uses exponentiation inside the element expression.

Similarly:

`[number for number in numbers if number % 2 == 0]`

contains:

`number % 2 == 0`

where modulo has higher precedence than equality comparison.

Comprehensions also have their own grammatical structure, so their syntax should not be reduced to a simple operator-precedence table.

## Generator expressions

Generator expressions use ordinary expression precedence while changing the evaluation strategy.

For example:

`(number ** 2 for number in numbers)`

produces values lazily.

The exponentiation expression is still evaluated according to ordinary precedence rules.

The major distinction is when the values are produced, not how `**` is grouped.

## F-strings

Expressions inside f-string replacement fields use ordinary Python expression rules.

For example:

`f"{x + y * 2}"`

performs multiplication before addition.

The surrounding string syntax does not change operator precedence inside the expression.

## Evaluation order versus precedence

These concepts should not be confused.

Precedence determines how an expression is grouped.

Evaluation rules determine which parts are evaluated and when.

Short-circuiting is a clear example.

In:

`False and expensive_operation()`

the expression is grouped correctly according to precedence, but `expensive_operation()` is never evaluated because the left side already determines the result.

This distinction is important when expressions contain function calls, exceptions, mutation, logging, I/O, or other side effects.

## Side effects

Consider an expression such as:

`record("A", 1) + record("B", 2) * record("C", 3)`

Precedence determines the multiplication grouping:

`record("A", 1) + (record("B", 2) * record("C", 3))`

The calls themselves can still have observable effects.

Complex expressions with important side effects can be difficult to understand. Splitting them into named intermediate variables often improves debugging and maintenance.

## Augmented assignment

Python provides augmented assignment operators such as:

- `+=`
- `-=`
- `*=`
- `/=`
- `//=`
- `%=`
- `**=`
- `@=`
- `&=`
- `|=`
- `^=`

For example:

`x *= 2 + 3`

uses the expression `2 + 3` on the right-hand side.

Augmented assignment is statement-level syntax and should not be treated as an ordinary binary expression with the same precedence behavior as `*`.

For mutable objects, an in-place operation may mutate the existing object. For immutable objects, a new object may be produced.

## Tuple construction and commas

The comma has syntactic significance that differs from ordinary operators.

For example:

`1 + 2, 3 * 4`

produces:

`(3, 12)`

The arithmetic expressions on each side are evaluated according to their normal precedence.

The comma is constructing the tuple structure rather than acting like an arithmetic operator.

## Unpacking

Python supports iterable unpacking:

`[0, *values, 4]`

and dictionary unpacking:

`{**base_config, **override_config}`

The `*` and `**` symbols have different meanings depending on syntactic context.

In:

`2 ** 3`

`**` is exponentiation.

In:

`{**dictionary}`

`**` is dictionary unpacking.

In:

`[1, *values]`

`*` is iterable unpacking.

This illustrates why precedence tables cannot be interpreted as a universal description of every use of a symbol. Grammar context matters.

## Abstract syntax trees

Python's `ast` module can reveal how an expression is parsed.

For example:

`3 + 4 * 2 ** 3 - 5`

can be converted into an abstract syntax tree.

The tree exposes the nesting of operations. Exponentiation occurs beneath multiplication, which occurs beneath the addition/subtraction structure.

This provides a direct representation of the fact that precedence affects the parsed structure.

AST inspection is particularly useful when an expression is syntactically valid but its grouping is unclear.

## Bytecode inspection

The `dis` module can show CPython bytecode for a function.

This can help investigate implementation behavior, but bytecode should not be treated as the definition of Python's precedence rules.

Bytecode can change between Python versions and implementations.

For understanding syntax and grouping, the language grammar and AST are more appropriate.

## Constant folding

Python implementations can optimize constant expressions during compilation.

For example:

`3 + 4 * 2`

contains only constants, so CPython may evaluate the result during compilation rather than repeatedly calculating it at runtime.

This is called constant folding.

The optimization does not define precedence. Precedence determines the expression's meaning first, and compiler optimizations can then operate on the resulting structure.

## A small precedence-aware parser

The Python script implements a restricted recursive-descent arithmetic parser.

Its grammar is conceptually:

`expression := term ((+ | -) term)*`

`term := factor ((* | /) factor)*`

`factor := integer | '(' expression ')'`

The important design feature is the separation between `expression`, `term`, and `factor`.

Addition and subtraction are handled at the expression level.

Multiplication and division are handled at the term level.

Numbers and parenthesized expressions are handled at the factor level.

Because the grammar is layered, multiplication and division naturally bind more strongly than addition and subtraction.

This demonstrates that operator precedence is fundamentally a parsing concept.

## Associativity in parser design

A parser must represent both precedence and associativity.

For operators such as:

`100 / 10 / 2`

left associativity produces:

`(100 / 10) / 2`

Exponentiation requires right associativity:

`2 ** 3 ** 2`

becomes:

`2 ** (3 ** 2)`

A parser that treats exponentiation as ordinary left-associative repetition would produce the wrong result.

Recursive-descent parsers, Pratt parsers, precedence-climbing parsers, and shunting-yard parsers can all represent precedence and associativity, although they do so differently.

## Shunting-yard parsing

The shunting-yard algorithm is a classical expression-parsing technique.

It typically maintains an output sequence and an operator stack.

Operators are associated with properties such as:

- precedence
- associativity
- arity

A simplified arithmetic hierarchy might be:

| Operator | Precedence | Associativity |
|---|---:|---|
| `**` | High | Right |
| `*` | Medium | Left |
| `/` | Medium | Left |
| `+` | Low | Left |
| `-` | Low | Left |

This is only an educational subset of Python's grammar. Python itself supports a much larger expression language.

## Pratt parsing

Pratt parsing is an expression-parsing strategy based on binding power.

Different tokens can have different binding strengths.

This approach can handle:

- prefix operators
- infix operators
- postfix operators
- precedence
- associativity

It is useful when implementing languages with rich expression syntax.

## Precedence climbing

Precedence climbing is another technique for parsing expressions.

The parser examines an operator's precedence and determines whether the operator should be consumed at the current parsing level.

Associativity changes how the right-hand side is parsed.

This gives a compact approach to implementing arithmetic grammars.

## Real-world financial calculation

The script demonstrates expressions such as:

`principal * (1 + annual_rate) ** years`

The parentheses around `1 + annual_rate` establish the intended mathematical grouping.

Exponentiation then applies the number of periods.

Multiplication by the principal occurs after the power operation.

Complex financial formulas are often clearer and safer when divided into named intermediate values rather than compressed into one expression.

## Validation and range checks

Python's chained comparisons are particularly useful for validation.

For example:

`0 <= percentage <= 100`

expresses an inclusive range directly.

The equivalent Boolean expression is:

`percentage >= 0 and percentage <= 100`

The chained form is concise and accurately reflects the mathematical notation.

## Common mistakes

### Reading every expression strictly left to right

Python does not evaluate a mixed expression simply from left to right.

For example:

`2 + 3 * 4`

is not `(2 + 3) * 4`.

### Forgetting exponentiation associativity

`2 ** 3 ** 2`

is:

`2 ** (3 ** 2)`

not:

`(2 ** 3) ** 2`.

### Misreading negative powers

`-2 ** 2`

is `-4`.

`(-2) ** 2`

is `4`.

### Treating multiplication as having priority over division

`100 / 10 * 2`

is:

`(100 / 10) * 2`

Multiplication and division have equal precedence.

### Treating addition as having priority over subtraction

`20 - 5 + 2`

is:

`(20 - 5) + 2`.

### Confusing `and` with `&`

`and` is a short-circuit Boolean operator.

`&` is bitwise AND.

They have different semantics and precedence.

### Confusing `or` with a Boolean conversion

`or` returns one of its operands.

For example:

`0 or 10`

returns `10`.

It is not simply an operation that always returns a Boolean.

### Using `is` for ordinary equality

Use:

`a == b`

for value equality.

Use:

`a is b`

for object identity.

### Assuming `or` fallback is safe for every value

This pattern:

`value or default`

treats all falsy values as missing.

If `0`, `False`, or an empty string is meaningful, an explicit condition may be required.

### Relying on obscure precedence rules

An expression can be technically correct while being difficult for humans to read.

Parentheses or intermediate variables are appropriate when they make intent clearer.

## Edge cases

### Floating-point equality

Precedence does not solve floating-point representation issues.

For example:

`0.1 + 0.2 == 0.3`

may be false because binary floating-point representation cannot represent many decimal fractions exactly.

When approximate equality is intended, `math.isclose()` can be appropriate.

### Division by zero

An expression can be grouped correctly and still fail at runtime.

Division by zero raises `ZeroDivisionError`.

### Incompatible types

`"10" + 5`

is unambiguously grouped but invalid because Python does not automatically combine string concatenation and integer addition.

Precedence determines grouping, not type compatibility.

### NaN

`float("nan")` has unusual comparison behavior.

NaN is not equal to itself:

`nan == nan`

is false.

This is a numerical semantics issue rather than a precedence issue.

### Custom objects

Custom classes can redefine operators.

Their methods can make an expression behave differently from ordinary numeric arithmetic, but the class cannot redefine Python's precedence rules.

## Security considerations

Operator precedence is not a security boundary.

A major security concern arises when arbitrary expressions supplied by users are passed to `eval()`.

`eval()` can execute Python expressions and should not be treated as a safe calculator for untrusted input.

A production expression evaluator should define the permitted language explicitly.

Possible architectural approaches include:

- a restricted grammar
- an AST-based validator with a strict allowlist
- explicit operator dispatch
- a purpose-built expression parser

The script demonstrates operator dispatch using the standard `operator` module rather than dynamically executing arbitrary source.

A safe expression evaluator must control more than operators. It must also control literals, names, function calls, attributes, indexing, comprehensions, imports, and other potentially executable constructs.

## Performance considerations

Operator precedence itself normally has negligible runtime cost.

Performance is more likely to depend on:

- algorithmic complexity
- repeated calculations
- object creation
- overloaded operator implementations
- function calls
- I/O
- numerical computation
- short-circuiting
- data structures

Short-circuiting can avoid unnecessary computation.

For example:

`cheap_condition and expensive_check()`

does not call `expensive_check()` when the first condition is false.

This can be useful, but correctness should remain the primary consideration.

Micro-optimizing parentheses or relying on obscure expression rearrangements is generally inappropriate when it harms readability.

## Debugging precedence problems

When an expression produces an unexpected result:

1. Identify every operator.
2. Determine the relevant precedence level.
3. Check associativity for equal-precedence operators.
4. Add explicit parentheses to represent the expected grouping.
5. Print intermediate values.
6. Break the expression into named variables.
7. Test boundary conditions.
8. Inspect the AST if the parse structure is unclear.
9. Check for short-circuit behavior.
10. Check whether custom operator methods are involved.

For example, an expression such as:

`a + b * c ** 2`

can be decomposed into:

`power = c ** 2`

`product = b * power`

`result = a + product`

This makes each stage directly observable.

## Readability and maintainability

Precedence knowledge should not become an excuse to write cryptic expressions.

A concise expression is useful when its meaning is obvious.

Parentheses are especially useful when:

- multiple Boolean operators are mixed
- bitwise and comparison operators are combined
- exponentiation and unary operators interact
- a mathematical formula has an important grouping
- a business rule needs to be audited
- a future maintainer may misunderstand the grouping

Named intermediate variables are often even better for complicated business logic.

For example, a complex authorization condition can be decomposed into:

- whether an account exists
- whether the account is verified
- whether the user is an administrator or owner
- whether the account satisfies the required policy

This communicates intent more clearly than a single large Boolean expression.

## Testing precedence-sensitive code

Tests should cover more than the normal successful case.

Useful categories include:

- lower boundary values
- upper boundary values
- empty values
- `None`
- falsy values
- truthy values
- zero
- negative values
- incompatible types
- exception-producing values
- combinations of Boolean conditions
- chained comparison boundaries
- overloaded operators

The script contains executable assertions for fundamental precedence rules and a set of practice expressions.

Assertions are useful because they convert language rules into executable expectations.

## Production implementation considerations

For ordinary Python application code, understanding precedence is primarily a correctness and readability requirement.

For an expression parser, precedence becomes an implementation concern.

A parser must determine:

- tokenization
- grammar
- precedence
- associativity
- unary operators
- binary operators
- parentheses
- function calls
- identifiers
- literals
- error handling
- evaluation semantics

A production expression language should define these rules explicitly.

Ambiguous or undocumented precedence rules can cause inconsistent interpretation, difficult debugging, and security problems.

## Important distinctions

| Concept | Meaning |
|---|---|
| Precedence | Determines which operators bind more strongly |
| Associativity | Determines grouping direction for equal-precedence operators |
| Evaluation order | Determines when subexpressions are actually evaluated |
| Short-circuiting | Allows `and` or `or` to skip later operands |
| Equality | Compares values with `==` |
| Identity | Compares object identity with `is` |
| Boolean AND | `and`, short-circuiting and operand-returning |
| Bitwise AND | `&`, bit-level operation |
| Assignment | `=` statement syntax |
| Assignment expression | `:=`, assignment that also produces a value |
| Operator overloading | Classes define behavior for operators through special methods |

These concepts interact, but they should not be treated as interchangeable.

## Core rules demonstrated by the script

The executable study file establishes the following important rules:

- Parentheses explicitly control grouping.
- Function calls, indexing, and attribute access bind strongly.
- Exponentiation has high precedence.
- Exponentiation is right-associative.
- Unary `+`, `-`, and `~` have their own precedence relationship with power.
- Multiplicative operators bind more strongly than additive operators.
- Multiplication and division have equal precedence.
- Addition and subtraction have equal precedence.
- Shift operators have lower precedence than addition and subtraction.
- Bitwise `&` binds more strongly than `^`.
- Bitwise `^` binds more strongly than `|`.
- Comparisons occur below arithmetic and bitwise operators.
- Python supports chained comparisons.
- `not` binds more strongly than `and`.
- `and` binds more strongly than `or`.
- `and` and `or` short-circuit.
- `and` and `or` return operands rather than necessarily returning `bool`.
- Conditional expressions have low precedence.
- Lambda expressions have very low precedence.
- Assignment expressions have very low precedence.
- `is` checks identity.
- `==` checks equality.
- Operator overloading changes operation behavior, not precedence.
- Precedence determines grouping before runtime operation behavior is applied.
- Short-circuiting can prevent an otherwise valid subexpression from being evaluated.
- Parentheses can improve readability even when they do not change the result.
- Complex expressions can be made safer to understand by decomposing them into intermediate values.

## Practical expression patterns

### Arithmetic

`total = price * quantity + shipping`

Multiplication occurs before addition.

### Grouped arithmetic

`total = (price + shipping) * tax_rate`

Parentheses make the intended order explicit.

### Range validation

`0 <= score <= 100`

This uses Python's chained comparison feature.

### Boolean authorization

`has_account and is_verified and (is_admin or is_owner)`

The parentheses clearly express the intended grouping of the alternatives.

### Safe conditional value selection

`status = "adult" if age >= 18 else "minor"`

The conditional expression chooses one value based on the condition.

### Explicit fallback

`value = user_value if user_value is not None else default_value`

This avoids treating every falsy value as missing.

### Short-circuit guard

`value is not None and value.process()`

The method call occurs only when the value is not `None`.

## The role of grammar

Operator precedence is fundamentally a grammar concept.

A programming language must determine how source text becomes a structured representation.

For example:

`2 + 3 * 4`

cannot be evaluated correctly without first deciding whether its structure is:

`(2 + 3) * 4`

or:

`2 + (3 * 4)`.

Python's grammar establishes the second structure.

The AST then represents that structure explicitly.

An interpreter or compiler can use the resulting structure for later execution or compilation.

This is why precedence matters beyond arithmetic. It affects the structure and meaning of programs.

## Relationship to language implementation

Different parsing strategies can encode precedence.

Common approaches include:

- layered recursive-descent grammar rules
- Pratt parsing
- precedence climbing
- shunting-yard parsing
- parser-generator precedence declarations

The script includes a small recursive-descent calculator to demonstrate how grammar structure itself can enforce precedence.

The parser is intentionally restricted. It is not a complete Python expression parser.

A complete Python parser must handle many additional constructs, including function calls, comprehensions, lambdas, conditional expressions, assignment expressions, attribute access, subscriptions, unpacking, Boolean operators, comparisons, and many forms of literals and syntax.

## Scope of the executable study

The Python script covers:

- basic precedence
- parentheses
- function calls
- indexing
- attribute access
- exponentiation
- exponentiation associativity
- unary operators
- multiplication and division
- floor division
- modulo
- addition and subtraction
- shifts
- bitwise operators
- comparisons
- chained comparisons
- membership
- identity
- `not`
- `and`
- `or`
- short-circuit evaluation
- conditional expressions
- lambda expressions
- assignment expressions
- strings and overloaded operators
- collection expressions
- comprehensions
- generator expressions
- f-strings
- custom operator overloading
- matrix multiplication
- AST inspection
- bytecode inspection
- constant folding
- side effects
- parser design
- recursive-descent parsing
- shunting-yard concepts
- Pratt parsing concepts
- precedence climbing
- validation
- financial calculations
- debugging
- testing
- performance considerations
- security considerations
- common mistakes
- edge cases
- production-oriented readability

The examples are executable and include assertions so that several fundamental rules are verified programmatically.
