#!/usr/bin/env python3
"""Variable scope: executable examples from lexical scope to closure behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


def heading(title: str) -> None:
    print(f"\n{'=' * 12} {title} {'=' * 12}")


# Module-level names are accessible inside functions, but assignment normally
# creates a local binding unless global is declared.
application_name = "RepositoryScopeLab"
build_number = 12


def inspect_module_scope() -> tuple[str, int]:
    return application_name, build_number


def local_scope() -> tuple[int, int]:
    value = 20

    def calculate() -> int:
        value = 5
        return value

    inner_value = calculate()
    return value, inner_value


def modify_global() -> int:
    global build_number
    build_number += 1
    return build_number


def demonstrate_unbound_local() -> str:
    """Show why reading a name before its local assignment raises an error."""
    count = 10

    def invalid_operation() -> int:
        # Assignment makes count local throughout this function.
        # The read therefore occurs before the local binding exists.
        count += 1
        return count

    try:
        invalid_operation()
    except UnboundLocalError as exc:
        return f"{type(exc).__name__}: {exc}"

    raise AssertionError("Expected an UnboundLocalError")


def closure_counter(start: int = 0) -> Callable[[], int]:
    """Retain state in an enclosing function's scope."""
    value = start

    def increment() -> int:
        nonlocal value
        value += 1
        return value

    return increment


def closure_factory(initial: int) -> tuple[Callable[[], int], Callable[[int], None]]:
    value = initial

    def read() -> int:
        return value

    def write(new_value: int) -> None:
        nonlocal value
        value = new_value

    return read, write


def late_binding_example() -> list[Callable[[], int]]:
    # Closures created in this loop share the same variable named index.
    return [lambda: index for index in range(3)]


def early_binding_example() -> list[Callable[[], int]]:
    # A default argument captures the current value when each function is made.
    return [lambda index=index: index for index in range(3)]


def comprehension_scope() -> tuple[list[int], bool]:
    squares = [number * number for number in range(5)]
    # In Python 3, the comprehension variable does not leak into the outer scope.
    return squares, "number" in locals()


def exception_target_scope() -> bool:
    try:
        raise ValueError("review rejected")
    except ValueError as error:
        print("Caught:", error)
    # Python clears the exception target after the except block.
    return "error" in locals()


@dataclass
class RepositorySettings:
    repository: str
    protected_branch: str


def make_repository_checker(settings: RepositorySettings) -> Callable[[str], bool]:
    """The closure retains its own settings object."""
    def is_protected(branch: str) -> bool:
        return branch == settings.protected_branch

    return is_protected


def scoped_review(
    reviewer: str,
    changed_files: list[str],
    approved: bool,
) -> dict[str, object]:
    # Function parameters and review-specific variables are local bindings.
    decision = "APPROVED" if approved else "CHANGES_REQUESTED"
    normalized_files = sorted({path.strip() for path in changed_files if path.strip()})
    return {
        "reviewer": reviewer,
        "decision": decision,
        "files": normalized_files,
    }


def evaluate_merge(
    *,
    branch: str,
    approved_reviewers: set[str],
    required_reviewers: int,
    checks: dict[str, bool],
    required_checks: set[str],
    conversations_resolved: bool,
) -> tuple[bool, list[str]]:
    """Use local policy state to explain merge eligibility."""
    failures: list[str] = []

    if not branch:
        failures.append("Target branch is missing")

    if len(approved_reviewers) < required_reviewers:
        failures.append("Insufficient distinct approving reviewers")

    missing_checks = required_checks - checks.keys()
    failed_checks = {name for name in required_checks if checks.get(name) is False}

    if missing_checks:
        failures.append(f"Missing status checks: {sorted(missing_checks)}")

    if failed_checks:
        failures.append(f"Failed status checks: {sorted(failed_checks)}")

    if not conversations_resolved:
        failures.append("Review conversations remain unresolved")

    return not failures, failures


def demonstrate_shadowing() -> None:
    policy = "repository-default"

    def evaluate() -> str:
        policy = "pull-request-override"
        return policy

    print("Outer binding:", policy)
    print("Shadowed inner binding:", evaluate())
    print("Outer binding remains:", policy)


def demonstrate_mutation_vs_rebinding() -> tuple[list[str], list[str]]:
    files = ["src/api.py"]

    def mutate() -> None:
        # Mutation changes the object referenced by the outer binding.
        files.append("tests/test_api.py")

    mutate()

    def rebind() -> None:
        # This creates a separate local binding; it does not rebind outer files.
        files = ["temporary.py"]
        files.append("local-only.py")
        print("Local list:", files)

    rebind()
    return files, list(files)


def main() -> None:
    heading("Module and function scope")
    print("Module values:", inspect_module_scope())
    print("Outer and inner local values:", local_scope())
    print("Global modification:", modify_global())

    heading("Local binding errors")
    print(demonstrate_unbound_local())

    heading("Closures and nonlocal")
    counter = closure_counter(4)
    print("Counter:", counter(), counter(), counter())

    read_value, write_value = closure_factory(8)
    print("Captured value:", read_value())
    write_value(21)
    print("Updated enclosing binding:", read_value())

    heading("Loop closures")
    print("Late binding:", [function() for function in late_binding_example()])
    print("Early binding:", [function() for function in early_binding_example()])

    heading("Comprehension and exception scope")
    print("Squares and leaked loop variable:", comprehension_scope())
    print("Exception target survives:", exception_target_scope())

    heading("Name shadowing and object mutation")
    demonstrate_shadowing()
    original_files, copied_files = demonstrate_mutation_vs_rebinding()
    print("Original list after mutation:", original_files)
    print("Independent copy:", copied_files)

    heading("Closure-backed repository policy")
    settings = RepositorySettings("payments-service", "main")
    is_protected = make_repository_checker(settings)
    print("main protected:", is_protected("main"))
    print("feature/review protected:", is_protected("feature/review"))

    heading("Review workflow and merge policy")
    reviews = [
        scoped_review("reviewer-ada", ["src/api.py", "src/api.py"], True),
        scoped_review("reviewer-lin", ["tests/test_api.py"], True),
    ]
    print("Reviews:", reviews)

    eligible, failures = evaluate_merge(
        branch="main",
        approved_reviewers={
            review["reviewer"]
            for review in reviews
            if review["decision"] == "APPROVED"
        },
        required_reviewers=2,
        checks={"unit-tests": True, "security-scan": True},
        required_checks={"unit-tests", "security-scan"},
        conversations_resolved=True,
    )
    print("Merge eligible:", eligible)
    print("Policy failures:", failures)

    failed_eligible, failed_reasons = evaluate_merge(
        branch="main",
        approved_reviewers={"reviewer-ada"},
        required_reviewers=2,
        checks={"unit-tests": True, "security-scan": False},
        required_checks={"unit-tests", "security-scan", "build"},
        conversations_resolved=False,
    )
    print("Incomplete review eligible:", failed_eligible)
    print("Blocking conditions:", failed_reasons)


if __name__ == "__main__":
    main()
