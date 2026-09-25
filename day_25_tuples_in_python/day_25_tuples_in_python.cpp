/*
 * TUPLE CONCEPTS IN C++17
 * =======================
 *
 * C++ provides std::tuple as a heterogeneous, fixed-size value type.
 * This case study builds a transaction-processing system around tuples.
 *
 * The program demonstrates:
 *   - std::tuple construction
 *   - std::get
 *   - std::tie
 *   - structured bindings
 *   - tuple concatenation
 *   - tuple comparison
 *   - tuple-like custom types
 *   - std::apply
 *   - tuple transformations
 *   - validation
 *   - exceptions
 *   - sorting
 *   - aggregation
 *   - graph-style records
 *   - compile-time tuple properties
 *   - performance and design trade-offs
 *
 * Compile:
 *   g++ -std=c++17 -O2 tuples_case_study.cpp -o tuples_case_study
 *
 * Run:
 *   ./tuples_case_study
 */

#include <algorithm>
#include <cmath>
#include <exception>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <tuple>
#include <type_traits>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;


// ============================================================================
// 1. OUTPUT UTILITIES
// ============================================================================

void section(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}


// ============================================================================
// 2. BASIC TUPLES
// ============================================================================

void basicTupleExamples() {
    section("1. Basic std::tuple Examples");

    tuple<int, int> coordinates{10, 20};
    tuple<string, int, double, bool> mixed{
        "Atul",
        30,
        88.5,
        true
    };

    cout << "Coordinates: "
         << get<0>(coordinates) << ", "
         << get<1>(coordinates) << "\n";

    cout << "Name: " << get<0>(mixed) << "\n";
    cout << "Age: " << get<1>(mixed) << "\n";
    cout << "Score: " << get<2>(mixed) << "\n";
    cout << "Active: " << boolalpha << get<3>(mixed) << "\n";

    // std::get uses a compile-time index. Invalid indexes are compilation
    // errors rather than runtime index errors.
}


// ============================================================================
// 3. TYPE-BASED ACCESS
// ============================================================================

void typeBasedAccess() {
    section("2. Type-Based Tuple Access");

    tuple<string, int, double> record{
        "Python",
        3,
        3.13
    };

    cout << "String: " << get<string>(record) << "\n";
    cout << "Integer: " << get<int>(record) << "\n";
    cout << "Double: " << get<double>(record) << "\n";

    // Type-based get requires the requested type to occur exactly once.
}


// ============================================================================
// 4. STRUCTURED BINDINGS
// ============================================================================

void structuredBindings() {
    section("3. Structured Bindings");

    tuple<string, int, string> person{
        "Atul",
        30,
        "India"
    };

    auto [name, age, country] = person;

    cout << name << ", " << age << ", " << country << "\n";

    // Structured bindings improve readability when the tuple has a known
    // semantic structure.
    auto [x, y] = tuple<double, double>{3.0, 4.0};

    cout << "x=" << x << ", y=" << y << "\n";
}


// ============================================================================
// 5. std::tie
// ============================================================================

pair<int, int> divideWithRemainder(int dividend, int divisor) {
    if (divisor == 0) {
        throw invalid_argument("divisor cannot be zero");
    }

    return {
        dividend / divisor,
        dividend % divisor
    };
}


void tieExample() {
    section("4. std::tie and Multiple Return Values");

    int quotient = 0;
    int remainder = 0;

    tie(quotient, remainder) = divideWithRemainder(17, 5);

    cout << "Quotient: " << quotient << "\n";
    cout << "Remainder: " << remainder << "\n";

    // std::ignore discards an unwanted tuple component.
    int ignored = 0;
    tie(ignored, remainder) = divideWithRemainder(20, 6);

    cout << "Remainder after second division: "
         << remainder << "\n";
}


// ============================================================================
// 6. TUPLE CONCATENATION
// ============================================================================

void tupleConcatenation() {
    section("5. Tuple Concatenation");

    auto first = make_tuple(1, string("Python"));
    auto second = make_tuple(2026, 3.13);

    auto combined = tuple_cat(first, second);

    cout << get<0>(combined) << "\n";
    cout << get<1>(combined) << "\n";
    cout << get<2>(combined) << "\n";
    cout << get<3>(combined) << "\n";
}


// ============================================================================
// 7. TUPLE COMPARISON
// ============================================================================

void tupleComparison() {
    section("6. Tuple Comparison");

    auto first = make_tuple(1, 2);
    auto second = make_tuple(1, 3);
    auto third = make_tuple(1, 2);

    cout << boolalpha;
    cout << "first == third: " << (first == third) << "\n";
    cout << "first < second: " << (first < second) << "\n";

    // std::tuple comparison is lexicographical: earlier elements are
    // considered before later elements.
}


// ============================================================================
// 8. TUPLE ALGORITHM SUPPORT
// ============================================================================

template <typename Tuple, typename Function, size_t... Indices>
void forEachTupleImpl(
    Tuple&& tupleValue,
    Function&& function,
    index_sequence<Indices...>
) {
    (function(get<Indices>(forward<Tuple>(tupleValue))), ...);
}


template <typename Tuple, typename Function>
void forEachTuple(Tuple&& tupleValue, Function&& function) {
    constexpr size_t tupleSize =
        tuple_size_v<remove_reference_t<Tuple>>;

    forEachTupleImpl(
        forward<Tuple>(tupleValue),
        forward<Function>(function),
        make_index_sequence<tupleSize>{}
    );
}


void tupleIteration() {
    section("7. Iterating Over Tuple Elements");

    auto values = make_tuple(10, 20.5, string("Python"));

    // std::tuple does not provide begin()/end() like std::vector.
    // A helper based on index_sequence can visit each compile-time element.
    forEachTuple(values, [](const auto& value) {
        cout << value << "\n";
    });
}


// ============================================================================
// 9. std::apply
// ============================================================================

void applyExample() {
    section("8. std::apply");

    auto person = make_tuple(
        string("Atul"),
        30,
        string("Engineering")
    );

    apply(
        [](const string& name, int age, const string& department) {
            cout << "Name: " << name << "\n";
            cout << "Age: " << age << "\n";
            cout << "Department: " << department << "\n";
        },
        person
    );
}


// ============================================================================
// 10. VALIDATED DOMAIN RECORD
// ============================================================================

using Coordinate = tuple<double, double>;


Coordinate validateCoordinate(double x, double y) {
    if (!isfinite(x) || !isfinite(y)) {
        throw invalid_argument(
            "coordinate values must be finite"
        );
    }

    return {x, y};
}


double distanceFromOrigin(const Coordinate& coordinate) {
    const auto [x, y] = coordinate;
    return sqrt(x * x + y * y);
}


void coordinateExample() {
    section("9. Validated Coordinate Type");

    Coordinate point = validateCoordinate(3.0, 4.0);

    cout << "x=" << get<0>(point) << "\n";
    cout << "y=" << get<1>(point) << "\n";
    cout << "Distance="
         << distanceFromOrigin(point)
         << "\n";

    try {
        validateCoordinate(
            numeric_limits<double>::infinity(),
            10.0
        );
    } catch (const invalid_argument& error) {
        cout << "Validation error: "
             << error.what()
             << "\n";
    }
}


// ============================================================================
// 11. TRANSACTION MODEL
// ============================================================================

using Transaction =
    tuple<string, string, double, string>;


Transaction makeTransaction(
    const string& transactionId,
    const string& accountId,
    double amount,
    const string& currency
) {
    if (transactionId.empty()) {
        throw invalid_argument("transaction ID cannot be empty");
    }

    if (accountId.empty()) {
        throw invalid_argument("account ID cannot be empty");
    }

    if (!isfinite(amount)) {
        throw invalid_argument("amount must be finite");
    }

    if (currency.empty()) {
        throw invalid_argument("currency cannot be empty");
    }

    return {
        transactionId,
        accountId,
        amount,
        currency
    };
}


void printTransaction(const Transaction& transaction) {
    const auto [
        transactionId,
        accountId,
        amount,
        currency
    ] = transaction;

    cout << fixed << setprecision(2)
         << transactionId
         << " | "
         << accountId
         << " | "
         << amount
         << " "
         << currency
         << "\n";
}


// ============================================================================
// 12. TRANSACTION PROCESSOR
// ============================================================================

class TransactionProcessor {
private:
    vector<Transaction> transactions;

public:
    void add(Transaction transaction) {
        // Validation happens before storing the transaction.
        const auto& id = get<0>(transaction);
        const auto& account = get<1>(transaction);
        double amount = get<2>(transaction);
        const auto& currency = get<3>(transaction);

        if (id.empty()) {
            throw invalid_argument("transaction ID is empty");
        }

        if (account.empty()) {
            throw invalid_argument("account ID is empty");
        }

        if (!isfinite(amount)) {
            throw invalid_argument("transaction amount is not finite");
        }

        if (currency.empty()) {
            throw invalid_argument("currency is empty");
        }

        transactions.push_back(move(transaction));
    }

    const vector<Transaction>& getAll() const {
        return transactions;
    }

    unordered_map<string, double> totalsByAccount() const {
        unordered_map<string, double> totals;

        for (const auto& transaction : transactions) {
            const string& account = get<1>(transaction);
            const double amount = get<2>(transaction);

            totals[account] += amount;
        }

        return totals;
    }

    optional<Transaction> findById(
        const string& transactionId
    ) const {
        for (const auto& transaction : transactions) {
            if (get<0>(transaction) == transactionId) {
                return transaction;
            }
        }

        return nullopt;
    }
};


// ============================================================================
// 13. TRANSACTION CASE STUDY
// ============================================================================

void transactionCaseStudy() {
    section("10. Industry-Style Transaction Processing Case Study");

    TransactionProcessor processor;

    processor.add(
        makeTransaction(
            "TX001",
            "ACC100",
            1500.00,
            "INR"
        )
    );

    processor.add(
        makeTransaction(
            "TX002",
            "ACC101",
            -250.00,
            "INR"
        )
    );

    processor.add(
        makeTransaction(
            "TX003",
            "ACC100",
            750.00,
            "INR"
        )
    );

    cout << "\nTransactions:\n";

    for (const auto& transaction : processor.getAll()) {
        printTransaction(transaction);
    }

    cout << "\nAccount totals:\n";

    const auto totals = processor.totalsByAccount();

    for (const auto& [account, total] : totals) {
        cout << account
             << " -> "
             << fixed
             << setprecision(2)
             << total
             << "\n";
    }

    cout << "\nLookup:\n";

    const auto found = processor.findById("TX002");

    if (found.has_value()) {
        printTransaction(found.value());
    } else {
        cout << "Transaction not found\n";
    }

    const auto missing = processor.findById("TX999");

    if (!missing.has_value()) {
        cout << "TX999 not found, handled safely\n";
    }
}


// ============================================================================
// 14. SORTING TUPLES
// ============================================================================

void sortingTransactions() {
    section("11. Sorting Tuple Records");

    vector<Transaction> transactions{
        makeTransaction("TX001", "ACC100", 1500, "INR"),
        makeTransaction("TX002", "ACC101", 250, "INR"),
        makeTransaction("TX003", "ACC100", 750, "INR"),
        makeTransaction("TX004", "ACC102", 2200, "INR")
    };

    // Sort by amount descending.
    sort(
        transactions.begin(),
        transactions.end(),
        [](const Transaction& left, const Transaction& right) {
            return get<2>(left) > get<2>(right);
        }
    );

    for (const auto& transaction : transactions) {
        printTransaction(transaction);
    }
}


// ============================================================================
// 15. GRAPH EDGES
// ============================================================================

using Edge = tuple<string, string, int>;


void graphExample() {
    section("12. Tuple-Based Graph Edges");

    vector<Edge> edges{
        {"A", "B", 4},
        {"A", "C", 2},
        {"C", "D", 1},
        {"B", "D", 5}
    };

    map<string, vector<pair<string, int>>> adjacency;

    for (const auto& [source, destination, weight] : edges) {
        adjacency[source].push_back({destination, weight});
    }

    for (const auto& [source, neighbors] : adjacency) {
        cout << source << ":\n";

        for (const auto& [destination, weight] : neighbors) {
            cout << "  -> "
                 << destination
                 << " weight="
                 << weight
                 << "\n";
        }
    }
}


// ============================================================================
// 16. PRIORITY QUEUE
// ============================================================================

using PriorityTask = tuple<int, string>;


void priorityQueueExample() {
    section("13. Tuple-Based Priority Queue");

    // For std::priority_queue, tuples are compared lexicographically.
    priority_queue<
        PriorityTask,
        vector<PriorityTask>,
        greater<PriorityTask>
    > tasks;

    tasks.push({2, "Write report"});
    tasks.push({1, "Fix production bug"});
    tasks.push({3, "Review documentation"});

    while (!tasks.empty()) {
        auto [priority, task] = tasks.top();
        tasks.pop();

        cout << "priority="
             << priority
             << ": "
             << task
             << "\n";
    }
}


// ============================================================================
// 17. COMPILE-TIME PROPERTIES
// ============================================================================

void compileTimeProperties() {
    section("14. Compile-Time Tuple Properties");

    using Example = tuple<string, int, double>;

    constexpr size_t numberOfElements =
        tuple_size_v<Example>;

    cout << "Tuple size: "
         << numberOfElements
         << "\n";

    static_assert(
        tuple_size_v<Example> == 3,
        "Example must contain three elements"
    );

    static_assert(
        is_same_v<
            tuple_element_t<1, Example>,
            int
        >,
        "Second element must be int"
    );
}


// ============================================================================
// 18. TUPLE TRANSFORMATION WITH std::apply
// ============================================================================

template <typename Tuple>
double sumNumericTuple(const Tuple& values) {
    double total = 0.0;

    apply(
        [&total](const auto&... elements) {
            (
                [&total](const auto& element) {
                    using ElementType =
                        decay_t<decltype(element)>;

                    if constexpr (
                        is_arithmetic_v<ElementType>
                    ) {
                        total += static_cast<double>(element);
                    }
                }(elements),
                ...
            );
        },
        values
    );

    return total;
}


void tupleTransformation() {
    section("15. Generic Tuple Processing");

    auto values = make_tuple(
        10,
        20.5,
        string("ignored"),
        30
    );

    cout << "Numeric total: "
         << sumNumericTuple(values)
         << "\n";
}


// ============================================================================
// 19. ERROR CONDITIONS
// ============================================================================

void errorConditions() {
    section("16. Error Conditions and Constraints");

    try {
        makeTransaction(
            "",
            "ACC100",
            100,
            "INR"
        );
    } catch (const invalid_argument& error) {
        cout << "Expected validation error: "
             << error.what()
             << "\n";
    }

    try {
        makeTransaction(
            "TX100",
            "ACC100",
            numeric_limits<double>::quiet_NaN(),
            "INR"
        );
    } catch (const invalid_argument& error) {
        cout << "Expected numeric error: "
             << error.what()
             << "\n";
    }

    // std::get with a compile-time invalid index cannot be demonstrated as a
    // runtime exception because the invalid access is rejected at compile time.
}


// ============================================================================
// 20. TUPLE VERSUS STRUCT
// ============================================================================

struct NamedTransaction {
    string transactionId;
    string accountId;
    double amount;
    string currency;
};


void tupleVersusStruct() {
    section("17. Tuple Versus Named Struct");

    Transaction tupleTransaction{
        "TX500",
        "ACC500",
        5000,
        "INR"
    };

    NamedTransaction namedTransaction{
        "TX500",
        "ACC500",
        5000,
        "INR"
    };

    cout << "Tuple transaction ID: "
         << get<0>(tupleTransaction)
         << "\n";

    cout << "Struct transaction ID: "
         << namedTransaction.transactionId
         << "\n";

    // Tuple:
    //   - compact
    //   - useful for temporary structured values
    //   - strongly typed by position
    //
    // Struct:
    //   - gives fields domain-specific names
    //   - often clearer for long-lived business entities
    //   - easier to evolve without relying on field positions
}


// ============================================================================
// 21. EDGE CASES
// ============================================================================

void edgeCases() {
    section("18. Edge Cases");

    tuple<> empty;

    cout << "Empty tuple size: "
         << tuple_size_v<decltype(empty)>
         << "\n";

    auto single = make_tuple(42);

    cout << "Single tuple value: "
         << get<0>(single)
         << "\n";

    // Duplicate types are valid, but type-based get becomes ambiguous.
    tuple<int, int> duplicateTypes{10, 20};

    cout << "Duplicate-type tuple: "
         << get<0>(duplicateTypes)
         << ", "
         << get<1>(duplicateTypes)
         << "\n";

    // The correct way to access duplicate types is by index.
}


// ============================================================================
// 22. COMPLEXITY DISCUSSION
// ============================================================================

void complexityDiscussion() {
    section("19. Complexity and Design Considerations");

    cout << "Tuple element access by index is compile-time indexed.\n";
    cout << "Tuple construction is fixed-size with statically known types.\n";
    cout << "Linear search through vector<Transaction> is O(n).\n";
    cout << "unordered_map account aggregation is expected O(n) overall.\n";
    cout << "Sorting n transactions is O(n log n).\n";
    cout << "Priority queue insertion/removal is O(log n).\n";
}


// ============================================================================
// 23. SELF-TESTS
// ============================================================================

void runTests() {
    section("20. Self-Tests");

    auto values = make_tuple(10, 20, 30);

    if (get<0>(values) != 10) {
        throw runtime_error("Tuple indexing test failed");
    }

    if (get<2>(values) != 30) {
        throw runtime_error("Tuple last element test failed");
    }

    auto [a, b, c] = values;

    if (a != 10 || b != 20 || c != 30) {
        throw runtime_error(
            "Structured binding test failed"
        );
    }

    auto combined = tuple_cat(
        make_tuple(1),
        make_tuple(2, 3)
    );

    if (combined != make_tuple(1, 2, 3)) {
        throw runtime_error(
            "tuple_cat test failed"
        );
    }

    auto coordinate = validateCoordinate(3, 4);

    if (distanceFromOrigin(coordinate) != 5) {
        throw runtime_error(
            "Coordinate calculation failed"
        );
    }

    TransactionProcessor processor;

    processor.add(
        makeTransaction(
            "T1",
            "A",
            100,
            "INR"
        )
    );

    processor.add(
        makeTransaction(
            "T2",
            "A",
            -25,
            "INR"
        )
    );

    const auto totals = processor.totalsByAccount();

    if (totals.at("A") != 75) {
        throw runtime_error(
            "Transaction aggregation failed"
        );
    }

    cout << "All self-tests passed.\n";
}


// ============================================================================
// 24. MAIN
// ============================================================================

int main() {
    try {
        basicTupleExamples();
        typeBasedAccess();
        structuredBindings();
        tieExample();
        tupleConcatenation();
        tupleComparison();
        tupleIteration();
        applyExample();
        coordinateExample();
        transactionCaseStudy();
        sortingTransactions();
        graphExample();
        priorityQueueExample();
        compileTimeProperties();
        tupleTransformation();
        errorConditions();
        tupleVersusStruct();
        edgeCases();
        complexityDiscussion();
        runTests();

        cout << "\nProgram completed successfully.\n";
        return 0;
    }
    catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << "\n";

        return 1;
    }
}
