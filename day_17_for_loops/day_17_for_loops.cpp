/*
 * for_loops_case_study.cpp
 *
 * C++17 case study: a transaction-processing and risk-monitoring engine
 * built around controlled iteration.
 *
 * Compile:
 *     g++ -std=c++17 -O2 -Wall -Wextra -pedantic for_loops_case_study.cpp -o risk_engine
 *
 * Run:
 *     ./risk_engine
 *
 * The program demonstrates how for loops participate in:
 * - input validation
 * - collection traversal
 * - aggregation
 * - filtering
 * - searching
 * - sorting
 * - matrix calculations
 * - graph traversal
 * - risk-rule evaluation
 * - batch processing
 * - complexity analysis
 * - exception handling
 */

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

// -----------------------------------------------------------------------------
// Domain model
// -----------------------------------------------------------------------------

struct Transaction {
    string id;
    string customerId;
    double amount{};
    string status;
    string country;
};

struct CustomerProfile {
    string customerId;
    double dailyLimit{};
    set<string> allowedCountries;
};

struct RiskResult {
    string transactionId;
    int riskScore{};
    vector<string> reasons;
    bool blocked{};
};

// -----------------------------------------------------------------------------
// Utility output
// -----------------------------------------------------------------------------

void printLine(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

// -----------------------------------------------------------------------------
// Basic loop demonstrations
// -----------------------------------------------------------------------------

void basicLoopExamples() {
    printLine("1. Basic for loops");

    // Traditional C++ for loop:
    // initialization; condition; update.
    for (int number = 0; number < 5; ++number) {
        cout << number << ' ';
    }
    cout << '\n';

    // Reverse iteration with a signed integer avoids unsigned underflow.
    for (int number = 10; number >= 0; number -= 2) {
        cout << number << ' ';
    }
    cout << '\n';

    // Range-based for is usually preferable when only values are needed.
    vector<string> technologies{"Python", "JavaScript", "C++"};

    for (const string& technology : technologies) {
        cout << technology << '\n';
    }
}

// -----------------------------------------------------------------------------
// Aggregation
// -----------------------------------------------------------------------------

double calculateTotal(const vector<Transaction>& transactions) {
    double total = 0.0;

    for (const Transaction& transaction : transactions) {
        if (transaction.amount < 0.0) {
            throw invalid_argument(
                "transaction amount cannot be negative: " + transaction.id
            );
        }

        if (transaction.status == "SUCCESS") {
            total += transaction.amount;
        }
    }

    return total;
}

// -----------------------------------------------------------------------------
// Validation
// -----------------------------------------------------------------------------

void validateTransactions(const vector<Transaction>& transactions) {
    for (size_t index = 0; index < transactions.size(); ++index) {
        const Transaction& transaction = transactions[index];

        if (transaction.id.empty()) {
            throw invalid_argument(
                "transaction at index " + to_string(index) +
                " has an empty ID"
            );
        }

        if (transaction.customerId.empty()) {
            throw invalid_argument(
                "transaction " + transaction.id +
                " has an empty customer ID"
            );
        }

        if (!isfinite(transaction.amount) || transaction.amount < 0.0) {
            throw invalid_argument(
                "transaction " + transaction.id +
                " has an invalid amount"
            );
        }

        if (
            transaction.status != "SUCCESS" &&
            transaction.status != "FAILED"
        ) {
            throw invalid_argument(
                "transaction " + transaction.id +
                " has an unknown status"
            );
        }
    }
}

// -----------------------------------------------------------------------------
// Search
// -----------------------------------------------------------------------------

const Transaction* findTransaction(
    const vector<Transaction>& transactions,
    const string& transactionId
) {
    for (const Transaction& transaction : transactions) {
        if (transaction.id == transactionId) {
            return &transaction;
        }
    }

    return nullptr;
}

// -----------------------------------------------------------------------------
// Frequency analysis
// -----------------------------------------------------------------------------

unordered_map<string, int> countTransactionsByCountry(
    const vector<Transaction>& transactions
) {
    unordered_map<string, int> counts;

    for (const Transaction& transaction : transactions) {
        ++counts[transaction.country];
    }

    return counts;
}

// -----------------------------------------------------------------------------
// Risk engine
// -----------------------------------------------------------------------------

RiskResult evaluateRisk(
    const Transaction& transaction,
    const CustomerProfile& profile,
    double customerDailyVolume
) {
    RiskResult result;
    result.transactionId = transaction.id;
    result.riskScore = 0;
    result.blocked = false;

    // Rule 1: large transactions receive more risk points.
    if (transaction.amount >= 100000.0) {
        result.riskScore += 50;
        result.reasons.push_back("very large transaction");
    } else if (transaction.amount >= 50000.0) {
        result.riskScore += 30;
        result.reasons.push_back("large transaction");
    } else if (transaction.amount >= 10000.0) {
        result.riskScore += 10;
        result.reasons.push_back("elevated transaction amount");
    }

    // Rule 2: exceeding a customer's daily limit is a separate signal.
    if (customerDailyVolume + transaction.amount > profile.dailyLimit) {
        result.riskScore += 40;
        result.reasons.push_back("daily limit exceeded");
    }

    // Rule 3: country validation.
    if (!profile.allowedCountries.empty()) {
        if (profile.allowedCountries.find(transaction.country) ==
            profile.allowedCountries.end()) {
            result.riskScore += 35;
            result.reasons.push_back("country not allowed");
        }
    }

    // A high score results in a block according to this fictional policy.
    result.blocked = result.riskScore >= 70;

    return result;
}

// -----------------------------------------------------------------------------
// Customer volume aggregation
// -----------------------------------------------------------------------------

unordered_map<string, double> calculateCustomerVolumes(
    const vector<Transaction>& transactions
) {
    unordered_map<string, double> volumes;

    for (const Transaction& transaction : transactions) {
        if (transaction.status == "SUCCESS") {
            volumes[transaction.customerId] += transaction.amount;
        }
    }

    return volumes;
}

// -----------------------------------------------------------------------------
// Risk analysis
// -----------------------------------------------------------------------------

vector<RiskResult> analyzeTransactions(
    const vector<Transaction>& transactions,
    const unordered_map<string, CustomerProfile>& profiles
) {
    vector<RiskResult> results;

    // First pass establishes historical successful volume.
    unordered_map<string, double> customerVolumes =
        calculateCustomerVolumes(transactions);

    // Second pass evaluates every transaction independently.
    for (const Transaction& transaction : transactions) {
        auto profileIterator = profiles.find(transaction.customerId);

        if (profileIterator == profiles.end()) {
            RiskResult missingProfile;
            missingProfile.transactionId = transaction.id;
            missingProfile.riskScore = 100;
            missingProfile.blocked = true;
            missingProfile.reasons.push_back("customer profile missing");
            results.push_back(missingProfile);
            continue;
        }

        const CustomerProfile& profile = profileIterator->second;

        // Remove the current transaction from historical volume when it was
        // already included in the aggregate. This prevents the transaction
        // from being counted twice in the daily-limit decision.
        double previousVolume = customerVolumes[transaction.customerId];

        if (transaction.status == "SUCCESS") {
            previousVolume -= transaction.amount;
        }

        results.push_back(
            evaluateRisk(transaction, profile, previousVolume)
        );
    }

    return results;
}

// -----------------------------------------------------------------------------
// Matrix-based exposure calculation
// -----------------------------------------------------------------------------

vector<vector<double>> multiplyMatrices(
    const vector<vector<double>>& left,
    const vector<vector<double>>& right
) {
    if (left.empty() || right.empty()) {
        return {};
    }

    const size_t leftColumns = left[0].size();
    const size_t rightColumns = right[0].size();

    if (leftColumns != right.size()) {
        throw invalid_argument("incompatible matrix dimensions");
    }

    for (const auto& row : left) {
        if (row.size() != leftColumns) {
            throw invalid_argument("left matrix is not rectangular");
        }
    }

    for (const auto& row : right) {
        if (row.size() != rightColumns) {
            throw invalid_argument("right matrix is not rectangular");
        }
    }

    vector<vector<double>> result(
        left.size(),
        vector<double>(rightColumns, 0.0)
    );

    // Three nested loops produce the standard O(n^3) matrix multiplication
    // pattern for square matrices.
    for (size_t i = 0; i < left.size(); ++i) {
        for (size_t k = 0; k < leftColumns; ++k) {
            for (size_t j = 0; j < rightColumns; ++j) {
                result[i][j] += left[i][k] * right[k][j];
            }
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// Graph traversal
// -----------------------------------------------------------------------------

vector<string> breadthFirstSearch(
    const unordered_map<string, vector<string>>& graph,
    const string& start
) {
    if (!graph.contains(start)) {
        throw invalid_argument("start node does not exist");
    }

    queue<string> pending;
    unordered_set<string> visited;
    vector<string> traversal;

    pending.push(start);
    visited.insert(start);

    while (!pending.empty()) {
        string current = pending.front();
        pending.pop();

        traversal.push_back(current);

        auto iterator = graph.find(current);

        if (iterator == graph.end()) {
            continue;
        }

        // The for loop explores every outgoing edge of the current node.
        for (const string& neighbor : iterator->second) {
            if (!visited.contains(neighbor)) {
                visited.insert(neighbor);
                pending.push(neighbor);
            }
        }
    }

    return traversal;
}

// -----------------------------------------------------------------------------
// Batch processing
// -----------------------------------------------------------------------------

template <typename T, typename Processor>
void processInBatches(
    const vector<T>& values,
    size_t batchSize,
    Processor processor
) {
    if (batchSize == 0) {
        throw invalid_argument("batch size must be greater than zero");
    }

    for (size_t start = 0; start < values.size(); start += batchSize) {
        const size_t end = min(start + batchSize, values.size());

        // A batch is processed before moving to the next range.
        processor(values, start, end);
    }
}

// -----------------------------------------------------------------------------
// Report generation
// -----------------------------------------------------------------------------

void printRiskReport(
    const vector<RiskResult>& results
) {
    printLine("Risk report");

    cout << left
         << setw(12) << "Transaction"
         << setw(10) << "Score"
         << setw(10) << "Blocked"
         << "Reasons\n";

    cout << string(78, '-') << '\n';

    for (const RiskResult& result : results) {
        cout << left
             << setw(12) << result.transactionId
             << setw(10) << result.riskScore
             << setw(10) << (result.blocked ? "YES" : "NO");

        for (size_t index = 0; index < result.reasons.size(); ++index) {
            if (index > 0) {
                cout << ", ";
            }
            cout << result.reasons[index];
        }

        cout << '\n';
    }
}

// -----------------------------------------------------------------------------
// Edge-case demonstrations
// -----------------------------------------------------------------------------

void edgeCaseExamples() {
    printLine("Edge cases");

    vector<int> empty;

    // Range-based for over an empty container performs zero iterations.
    for (int value : empty) {
        cout << value << '\n';
    }

    cout << "empty container processed safely\n";

    // Avoid unsigned reverse-loop mistakes such as:
    // for (size_t i = values.size() - 1; i >= 0; --i)
    // because size_t cannot become negative.
    vector<int> values{10, 20, 30};

    for (int index = static_cast<int>(values.size()) - 1;
         index >= 0;
         --index) {
        cout << values[static_cast<size_t>(index)] << ' ';
    }

    cout << '\n';
}

// -----------------------------------------------------------------------------
// Demonstration of break and continue
// -----------------------------------------------------------------------------

void controlFlowExamples() {
    printLine("break and continue");

    for (int number = 1; number <= 10; ++number) {
        if (number % 2 == 0) {
            continue;
        }

        if (number > 7) {
            break;
        }

        cout << number << ' ';
    }

    cout << '\n';
}

// -----------------------------------------------------------------------------
// Complete case study
// -----------------------------------------------------------------------------

void runCaseStudy() {
    printLine("Industry-style transaction risk case study");

    vector<Transaction> transactions{
        {"TX001", "C001", 1200.0, "SUCCESS", "IN"},
        {"TX002", "C001", 8500.0, "SUCCESS", "IN"},
        {"TX003", "C002", 65000.0, "SUCCESS", "US"},
        {"TX004", "C002", 20000.0, "SUCCESS", "IN"},
        {"TX005", "C003", 125000.0, "SUCCESS", "SG"},
        {"TX006", "C003", 3000.0, "FAILED", "IN"},
        {"TX007", "C001", 4500.0, "SUCCESS", "IN"}
    };

    unordered_map<string, CustomerProfile> profiles{
        {
            "C001",
            {"C001", 20000.0, {"IN"}}
        },
        {
            "C002",
            {"C002", 70000.0, {"IN", "US"}}
        },
        {
            "C003",
            {"C003", 100000.0, {"IN"}}
        }
    };

    try {
        validateTransactions(transactions);
    } catch (const exception& error) {
        cerr << "validation failure: " << error.what() << '\n';
        return;
    }

    cout << fixed << setprecision(2);

    double successfulTotal = calculateTotal(transactions);
    cout << "successful transaction volume: "
         << successfulTotal << '\n';

    const Transaction* transaction =
        findTransaction(transactions, "TX003");

    if (transaction != nullptr) {
        cout << "found TX003 for customer "
             << transaction->customerId << '\n';
    }

    auto countryCounts =
        countTransactionsByCountry(transactions);

    cout << "\ntransactions by country:\n";

    for (const auto& [country, count] : countryCounts) {
        cout << "  " << country << ": " << count << '\n';
    }

    vector<RiskResult> results =
        analyzeTransactions(transactions, profiles);

    printRiskReport(results);

    // Demonstrate batch processing. Real systems can use this pattern to
    // control memory consumption and interact with APIs or databases in
    // bounded groups.
    printLine("Batch processing");

    processInBatches<Transaction>(
        transactions,
        3,
        [](const vector<Transaction>& batch, size_t start, size_t end) {
            cout << "processing records [" << start
                 << ", " << end << ")\n";

            double batchTotal = 0.0;

            for (size_t index = start; index < end; ++index) {
                if (batch[index].status == "SUCCESS") {
                    batchTotal += batch[index].amount;
                }
            }

            cout << "batch successful volume: "
                 << batchTotal << '\n';
        }
    );

    // Matrix calculations could represent exposure transformations,
    // portfolio weights, or other numerical processing.
    printLine("Exposure matrix calculation");

    vector<vector<double>> exposure{
        {1.0, 2.0},
        {3.0, 4.0}
    };

    vector<vector<double>> weights{
        {0.5, 0.2},
        {0.1, 0.7}
    };

    vector<vector<double>> transformed =
        multiplyMatrices(exposure, weights);

    for (const auto& row : transformed) {
        for (double value : row) {
            cout << setw(8) << value;
        }
        cout << '\n';
    }

    // A graph can model relationships between services, accounts, or
    // infrastructure components.
    printLine("Relationship graph traversal");

    unordered_map<string, vector<string>> graph{
        {"Gateway", {"Auth", "Risk"}},
        {"Auth", {"Database"}},
        {"Risk", {"Database", "Alerting"}},
        {"Database", {}},
        {"Alerting", {}}
    };

    vector<string> traversal =
        breadthFirstSearch(graph, "Gateway");

    for (const string& node : traversal) {
        cout << node << ' ';
    }

    cout << '\n';
}

// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

int main() {
    try {
        basicLoopExamples();
        controlFlowExamples();
        edgeCaseExamples();
        runCaseStudy();
    } catch (const exception& error) {
        cerr << "\nFatal error: " << error.what() << '\n';
        return 1;
    }

    cout << "\nProgram completed successfully.\n";
    return 0;
}
