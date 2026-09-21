/*
 * Practice: Conditions and Loops
 * ==============================
 *
 * Complete C++17 case study:
 * A rule-driven transaction monitoring engine.
 *
 * The program progressively demonstrates:
 * - Boolean expressions
 * - if / else if / else
 * - switch
 * - for loops
 * - while loops
 * - do-while loops
 * - break and continue
 * - nested loops
 * - vectors, maps, sets, and structures
 * - validation
 * - searching
 * - aggregation
 * - algorithmic complexity
 * - state-machine processing
 * - rule-based classification
 * - error handling
 * - edge cases
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic main.cpp -o conditions_loops
 */

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

// ---------------------------------------------------------------------------
// Output utilities
// ---------------------------------------------------------------------------

void section(const string& title) {
    cout << "\n" << string(78, '=') << '\n';
    cout << title << '\n';
    cout << string(78, '=') << '\n';
}

void subsection(const string& title) {
    cout << "\n--- " << title << " ---\n";
}

// ---------------------------------------------------------------------------
// Data model
// ---------------------------------------------------------------------------

struct Transaction {
    int id;
    string customer;
    double amount;
    bool countryMatches;
    bool knownDevice;
    int transactionsLastHour;
};

struct TransactionResult {
    int id;
    string customer;
    string classification;
    double amount;
};

enum class TransactionStatus {
    Normal,
    Review,
    HighRisk,
    ManualReview,
    Invalid
};

string statusToString(TransactionStatus status) {
    switch (status) {
        case TransactionStatus::Normal:
            return "normal";
        case TransactionStatus::Review:
            return "review";
        case TransactionStatus::HighRisk:
            return "high_risk";
        case TransactionStatus::ManualReview:
            return "manual_review";
        case TransactionStatus::Invalid:
            return "invalid";
    }

    return "unknown";
}

// ---------------------------------------------------------------------------
// 1. Boolean expressions
// ---------------------------------------------------------------------------

void demonstrateBooleanExpressions() {
    section("1. Boolean expressions");

    bool isAdult = true;
    bool hasIdentityDocument = true;

    bool canEnter = isAdult && hasIdentityDocument;
    bool requiresReview = !canEnter;

    cout << boolalpha;
    cout << "isAdult: " << isAdult << '\n';
    cout << "hasIdentityDocument: " << hasIdentityDocument << '\n';
    cout << "canEnter: " << canEnter << '\n';
    cout << "requiresReview: " << requiresReview << '\n';

    int age = 25;

    cout << "age >= 18: " << (age >= 18) << '\n';
    cout << "age == 25: " << (age == 25) << '\n';
    cout << "age != 30: " << (age != 30) << '\n';
}

// ---------------------------------------------------------------------------
// 2. if / else if / else
// ---------------------------------------------------------------------------

string classifyScore(double score) {
    if (!isfinite(score) || score < 0.0 || score > 100.0) {
        return "Invalid score";
    }

    if (score >= 90.0) {
        return "A";
    }

    if (score >= 80.0) {
        return "B";
    }

    if (score >= 70.0) {
        return "C";
    }

    if (score >= 60.0) {
        return "D";
    }

    return "F";
}

void demonstrateConditionals() {
    section("2. Conditional statements");

    vector<double> scores{95.0, 84.0, 72.0, 61.0, 43.0, -5.0, 101.0};

    for (double score : scores) {
        cout << "Score " << setw(5) << score
             << ": " << classifyScore(score) << '\n';
    }

    int age = 22;
    bool hasTicket = true;

    if (age >= 18) {
        if (hasTicket) {
            cout << "Admission permitted.\n";
        } else {
            cout << "Ticket required.\n";
        }
    } else {
        cout << "Visitor is under the required age.\n";
    }
}

// ---------------------------------------------------------------------------
// 3. switch
// ---------------------------------------------------------------------------

double calculateOperation(char operation, double first, double second) {
    switch (operation) {
        case '+':
            return first + second;

        case '-':
            return first - second;

        case '*':
            return first * second;

        case '/':
            if (second == 0.0) {
                throw invalid_argument("Division by zero is not allowed.");
            }
            return first / second;

        default:
            throw invalid_argument("Unknown operation.");
    }
}

void demonstrateSwitch() {
    section("3. switch statements");

    const vector<char> operations{'+', '-', '*', '/'};

    for (char operation : operations) {
        try {
            cout << "8 " << operation << " 4 = "
                 << calculateOperation(operation, 8.0, 4.0)
                 << '\n';
        } catch (const exception& error) {
            cout << "Error: " << error.what() << '\n';
        }
    }
}

// ---------------------------------------------------------------------------
// 4. for loops
// ---------------------------------------------------------------------------

void demonstrateForLoops() {
    section("4. for loops");

    cout << "Forward counting: ";

    for (int number = 1; number <= 5; ++number) {
        cout << number << ' ';
    }

    cout << "\nReverse counting: ";

    for (int number = 10; number >= 2; number -= 2) {
        cout << number << ' ';
    }

    cout << '\n';

    vector<string> topics{
        "conditions",
        "loops",
        "functions",
        "data structures"
    };

    for (size_t index = 0; index < topics.size(); ++index) {
        cout << index + 1 << ". " << topics[index] << '\n';
    }
}

// ---------------------------------------------------------------------------
// 5. while and do-while
// ---------------------------------------------------------------------------

void demonstrateWhileLoops() {
    section("5. while and do-while loops");

    int counter = 1;

    while (counter <= 5) {
        cout << "while counter = " << counter << '\n';
        ++counter;
    }

    int attempts = 0;

    do {
        cout << "do-while attempt = " << attempts + 1 << '\n';
        ++attempts;
    } while (attempts < 3);

    // A do-while executes at least once, even when its condition is initially
    // false. A while loop may execute zero times.
}

// ---------------------------------------------------------------------------
// 6. break and continue
// ---------------------------------------------------------------------------

void demonstrateBreakAndContinue() {
    section("6. break and continue");

    cout << "Odd numbers below 10: ";

    for (int number = 1; number <= 10; ++number) {
        if (number % 2 == 0) {
            continue;
        }

        cout << number << ' ';
    }

    cout << "\nSearching for 15: ";

    const vector<int> numbers{4, 7, 11, 15, 21};

    for (int number : numbers) {
        cout << number << ' ';

        if (number == 15) {
            break;
        }
    }

    cout << '\n';
}

// ---------------------------------------------------------------------------
// 7. Nested loops
// ---------------------------------------------------------------------------

void demonstrateNestedLoops() {
    section("7. Nested loops");

    for (int row = 1; row <= 3; ++row) {
        for (int column = 1; column <= 4; ++column) {
            cout << setw(4) << row * column;
        }

        cout << '\n';
    }

    // If both loops have n iterations, the nested body has O(n^2) time
    // complexity. Nested loops are not automatically bad, but their cost
    // should be understood.
}

// ---------------------------------------------------------------------------
// 8. Search algorithms
// ---------------------------------------------------------------------------

int linearSearch(const vector<int>& numbers, int target) {
    for (size_t index = 0; index < numbers.size(); ++index) {
        if (numbers[index] == target) {
            return static_cast<int>(index);
        }
    }

    return -1;
}

optional<pair<int, int>> findPairWithSum(
    const vector<int>& numbers,
    int target
) {
    // The unordered-set equivalent is common, but std::set is used here
    // because this program intentionally demonstrates a standard ordered
    // set. Lookup is O(log n), giving O(n log n) total time.
    set<int> seen;

    for (int number : numbers) {
        int required = target - number;

        if (seen.find(required) != seen.end()) {
            return make_pair(required, number);
        }

        seen.insert(number);
    }

    return nullopt;
}

void demonstrateSearching() {
    section("8. Searching");

    vector<int> numbers{3, 8, 12, 17, 21};

    cout << "Index of 12: "
         << linearSearch(numbers, 12) << '\n';

    cout << "Index of 100: "
         << linearSearch(numbers, 100) << '\n';

    auto pair = findPairWithSum(numbers, 29);

    if (pair.has_value()) {
        cout << "Pair adding to 29: "
             << pair->first << " + " << pair->second << '\n';
    } else {
        cout << "No pair adds to 29.\n";
    }
}

// ---------------------------------------------------------------------------
// 9. Aggregation
// ---------------------------------------------------------------------------

void demonstrateAggregation() {
    section("9. Filtering and aggregation");

    vector<double> transactions{
        1200.0,
        -300.0,
        450.0,
        -150.0,
        800.0,
        -50.0
    };

    double income = 0.0;
    double expenses = 0.0;

    for (double amount : transactions) {
        if (amount >= 0.0) {
            income += amount;
        } else {
            expenses += abs(amount);
        }
    }

    cout << fixed << setprecision(2);
    cout << "Income: " << income << '\n';
    cout << "Expenses: " << expenses << '\n';
    cout << "Balance: " << income - expenses << '\n';
}

// ---------------------------------------------------------------------------
// 10. Prime detection
// ---------------------------------------------------------------------------

bool isPrime(int number) {
    if (number < 2) {
        return false;
    }

    if (number == 2) {
        return true;
    }

    if (number % 2 == 0) {
        return false;
    }

    for (int divisor = 3;
         divisor <= number / divisor;
         divisor += 2) {
        if (number % divisor == 0) {
            return false;
        }
    }

    return true;
}

void demonstratePrimeDetection() {
    section("10. Prime number detection");

    for (int number = 1; number <= 50; ++number) {
        if (isPrime(number)) {
            cout << number << ' ';
        }
    }

    cout << '\n';

    // divisor <= number / divisor avoids computing sqrt repeatedly and also
    // avoids an unnecessary multiplication that could overflow for extreme
    // integer values.
}

// ---------------------------------------------------------------------------
// 11. Fibonacci
// ---------------------------------------------------------------------------

vector<unsigned long long> fibonacci(size_t count) {
    vector<unsigned long long> result;
    result.reserve(count);

    unsigned long long first = 0;
    unsigned long long second = 1;

    for (size_t index = 0; index < count; ++index) {
        result.push_back(first);

        // Unsigned overflow is well-defined modulo 2^N, but that does not
        // represent mathematical Fibonacci values after the type's limit.
        first = second;
        second = first + result.back();
    }

    return result;
}

void demonstrateFibonacci() {
    section("11. Fibonacci sequence");

    const auto values = fibonacci(15);

    for (auto value : values) {
        cout << value << ' ';
    }

    cout << '\n';
}

// ---------------------------------------------------------------------------
// 12. Matrix traversal
// ---------------------------------------------------------------------------

void demonstrateMatrixTraversal() {
    section("12. Matrix traversal");

    vector<vector<int>> matrix{
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    int total = 0;

    for (const auto& row : matrix) {
        for (int value : row) {
            total += value;
        }
    }

    for (const auto& row : matrix) {
        for (int value : row) {
            cout << setw(4) << value;
        }

        cout << '\n';
    }

    cout << "Total: " << total << '\n';
}

// ---------------------------------------------------------------------------
// 13. Transaction validation
// ---------------------------------------------------------------------------

bool isValidTransaction(const Transaction& transaction) {
    if (!isfinite(transaction.amount)) {
        return false;
    }

    if (transaction.amount <= 0.0) {
        return false;
    }

    if (transaction.transactionsLastHour < 0) {
        return false;
    }

    if (transaction.id <= 0) {
        return false;
    }

    return true;
}

// ---------------------------------------------------------------------------
// 14. Rule engine
// ---------------------------------------------------------------------------

TransactionStatus classifyTransaction(const Transaction& transaction) {
    if (!isValidTransaction(transaction)) {
        return TransactionStatus::Invalid;
    }

    if (transaction.amount >= 100000.0) {
        return TransactionStatus::ManualReview;
    }

    if (
        !transaction.countryMatches &&
        !transaction.knownDevice
    ) {
        return TransactionStatus::HighRisk;
    }

    if (transaction.transactionsLastHour > 20) {
        return TransactionStatus::HighRisk;
    }

    if (
        !transaction.countryMatches ||
        !transaction.knownDevice
    ) {
        return TransactionStatus::Review;
    }

    return TransactionStatus::Normal;
}

// ---------------------------------------------------------------------------
// 15. State-machine processing
// ---------------------------------------------------------------------------

enum class ProcessingState {
    Start,
    Validate,
    Classify,
    Store,
    Finish
};

string stateToString(ProcessingState state) {
    switch (state) {
        case ProcessingState::Start:
            return "START";
        case ProcessingState::Validate:
            return "VALIDATE";
        case ProcessingState::Classify:
            return "CLASSIFY";
        case ProcessingState::Store:
            return "STORE";
        case ProcessingState::Finish:
            return "FINISH";
    }

    return "UNKNOWN";
}

TransactionResult processTransaction(const Transaction& transaction) {
    ProcessingState state = ProcessingState::Start;
    TransactionStatus status = TransactionStatus::Invalid;

    while (state != ProcessingState::Finish) {
        switch (state) {
            case ProcessingState::Start:
                state = ProcessingState::Validate;
                break;

            case ProcessingState::Validate:
                if (!isValidTransaction(transaction)) {
                    status = TransactionStatus::Invalid;
                    state = ProcessingState::Finish;
                } else {
                    state = ProcessingState::Classify;
                }
                break;

            case ProcessingState::Classify:
                status = classifyTransaction(transaction);
                state = ProcessingState::Store;
                break;

            case ProcessingState::Store:
                // A production system would persist the result here.
                // This educational case study keeps storage in memory.
                state = ProcessingState::Finish;
                break;

            case ProcessingState::Finish:
                break;
        }
    }

    return {
        transaction.id,
        transaction.customer,
        statusToString(status),
        transaction.amount
    };
}

// ---------------------------------------------------------------------------
// 16. Full transaction processing
// ---------------------------------------------------------------------------

vector<TransactionResult> processTransactions(
    const vector<Transaction>& transactions
) {
    vector<TransactionResult> results;
    results.reserve(transactions.size());

    for (const auto& transaction : transactions) {
        results.push_back(processTransaction(transaction));
    }

    return results;
}

// ---------------------------------------------------------------------------
// 17. Reporting
// ---------------------------------------------------------------------------

void printReport(const vector<TransactionResult>& results) {
    subsection("Transaction report");

    map<string, int> counts;

    cout << left
         << setw(8) << "ID"
         << setw(15) << "Customer"
         << setw(18) << "Status"
         << right << setw(14) << "Amount"
         << '\n';

    cout << string(55, '-') << '\n';

    for (const auto& result : results) {
        cout << left
             << setw(8) << result.id
             << setw(15) << result.customer
             << setw(18) << result.classification
             << right << setw(14)
             << fixed << setprecision(2)
             << result.amount
             << '\n';

        ++counts[result.classification];
    }

    cout << "\nStatus counts:\n";

    for (const auto& [status, count] : counts) {
        cout << "  " << status << ": " << count << '\n';
    }
}

// ---------------------------------------------------------------------------
// 18. Retry mechanism
// ---------------------------------------------------------------------------

bool performRetries(
    int maximumAttempts,
    const vector<bool>& outcomes
) {
    if (maximumAttempts <= 0) {
        throw invalid_argument("maximumAttempts must be positive.");
    }

    for (int attempt = 1; attempt <= maximumAttempts; ++attempt) {
        bool successful =
            static_cast<size_t>(attempt - 1) < outcomes.size()
                ? outcomes[attempt - 1]
                : false;

        cout << "Attempt " << attempt << ": "
             << (successful ? "success" : "failure")
             << '\n';

        if (successful) {
            return true;
        }
    }

    return false;
}

// ---------------------------------------------------------------------------
// 19. Deterministic simulation
// ---------------------------------------------------------------------------

map<int, int> simulateDiceRolls(int numberOfRolls) {
    if (numberOfRolls < 0) {
        throw invalid_argument("numberOfRolls cannot be negative.");
    }

    mt19937 generator(42);
    uniform_int_distribution<int> distribution(1, 6);

    map<int, int> frequencies;

    for (int roll = 0; roll < numberOfRolls; ++roll) {
        int outcome = distribution(generator);
        ++frequencies[outcome];
    }

    return frequencies;
}

void demonstrateSimulation() {
    section("13. Loop-based simulation");

    const auto frequencies = simulateDiceRolls(1000);

    for (const auto& [face, count] : frequencies) {
        cout << "Face " << face << ": " << count << '\n';
    }
}

// ---------------------------------------------------------------------------
// 20. Edge-case handling
// ---------------------------------------------------------------------------

void demonstrateEdgeCases() {
    section("14. Edge cases");

    vector<int> empty;

    if (empty.empty()) {
        cout << "Empty vector detected before indexed access.\n";
    }

    const int zero = 0;

    if (zero == 0) {
        cout << "Division by zero condition detected before division.\n";
    }

    try {
        performRetries(0, {});
    } catch (const exception& error) {
        cout << "Retry validation: " << error.what() << '\n';
    }

    Transaction invalid{
        -1,
        "Unknown",
        -500.0,
        true,
        true,
        -2
    };

    cout << "Invalid transaction status: "
         << statusToString(classifyTransaction(invalid))
         << '\n';
}

// ---------------------------------------------------------------------------
// 21. Performance discussion through operation counting
// ---------------------------------------------------------------------------

long long countNestedOperations(int rows, int columns) {
    if (rows < 0 || columns < 0) {
        throw invalid_argument("Dimensions cannot be negative.");
    }

    long long operations = 0;

    for (int row = 0; row < rows; ++row) {
        for (int column = 0; column < columns; ++column) {
            ++operations;
        }
    }

    return operations;
}

void demonstrateComplexity() {
    section("15. Complexity and performance");

    cout << "10 x 10 operations: "
         << countNestedOperations(10, 10) << '\n';

    cout << "100 x 100 operations: "
         << countNestedOperations(100, 100) << '\n';

    cout << "1000 x 1000 operations: "
         << countNestedOperations(1000, 1000) << '\n';

    cout << "The operation count grows approximately as rows * columns.\n";
    cout << "For n rows and n columns, this is O(n^2).\n";
}

// ---------------------------------------------------------------------------
// 22. Main case study
// ---------------------------------------------------------------------------

void runTransactionCaseStudy() {
    section("16. Industry-style transaction monitoring case study");

    vector<Transaction> transactions{
        {1001, "Asha", 2500.0, true, true, 2},
        {1002, "Ravi", 15000.0, false, true, 4},
        {1003, "Mina", 300000.0, true, true, 1},
        {1004, "Kabir", 5000.0, false, false, 2},
        {1005, "Neha", 1000.0, true, true, 25},
        {1006, "Invalid", -50.0, true, true, 1}
    };

    const auto results = processTransactions(transactions);

    printReport(results);

    subsection("Retry demonstration");

    cout << "Final retry result: "
         << boolalpha
         << performRetries(4, {false, false, true})
         << '\n';
}

// ---------------------------------------------------------------------------
// 23. Main
// ---------------------------------------------------------------------------

int main() {
    try {
        demonstrateBooleanExpressions();
        demonstrateConditionals();
        demonstrateSwitch();
        demonstrateForLoops();
        demonstrateWhileLoops();
        demonstrateBreakAndContinue();
        demonstrateNestedLoops();
        demonstrateSearching();
        demonstrateAggregation();
        demonstratePrimeDetection();
        demonstrateFibonacci();
        demonstrateMatrixTraversal();
        demonstrateSimulation();
        demonstrateEdgeCases();
        demonstrateComplexity();
        runTransactionCaseStudy();

        section("Study checklist");

        const vector<string> checklist{
            "Can you write if, else if, and else conditions?",
            "Can you combine Boolean expressions with &&, ||, and !?",
            "Can you use switch when a value selects among discrete cases?",
            "Can you choose between for, while, and do-while?",
            "Can you explain the purpose of break and continue?",
            "Can you recognize the cost of nested loops?",
            "Can you search through a vector safely?",
            "Can you validate input before processing it?",
            "Can you use a set to reduce repeated search work?",
            "Can you describe O(n) and O(n^2) loop behavior?",
            "Can you design a state-driven processing loop?",
            "Can you identify edge cases before they become runtime errors?"
        };

        for (const auto& item : checklist) {
            cout << "[ ] " << item << '\n';
        }

        return 0;
    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
