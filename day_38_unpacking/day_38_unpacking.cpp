#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

/*
 * C++ case study: structured operational-record processing.
 *
 * C++ does not have Python's assignment-unpacking syntax. Structured binding
 * declarations provide the closest language-level mechanism for decomposing
 * tuples, pairs, arrays, and suitable user-defined objects into named
 * variables.
 *
 * The program models a small operations ingestion service. It validates
 * records, decomposes them with structured bindings, aggregates accepted
 * transactions, and reports malformed data.
 */

struct Transaction {
    std::string id;
    std::string region;
    double amount;
    std::string status;

    // Structured bindings can access public aggregate members when the type
    // satisfies the language requirements for structured binding.
};

struct ProcessingResult {
    std::map<std::string, double> totals;
    std::vector<std::string> rejectedIds;
};

std::vector<std::string> splitCsv(const std::string& line) {
    std::vector<std::string> fields;
    std::stringstream stream(line);
    std::string field;

    while (std::getline(stream, field, ',')) {
        fields.push_back(field);
    }

    return fields;
}

std::string trim(const std::string& value) {
    const auto first = value.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) {
        return "";
    }

    const auto last = value.find_last_not_of(" \t\r\n");
    return value.substr(first, last - first + 1);
}

std::optional<Transaction> parseTransaction(
    const std::string& line,
    std::string& error
) {
    const auto fields = splitCsv(line);

    if (fields.size() != 4) {
        error = "expected exactly four fields";
        return std::nullopt;
    }

    const auto& id = fields[0];
    const auto& region = fields[1];
    const auto& amountText = fields[2];
    const auto& status = fields[3];

    if (id.empty()) {
        error = "transaction id is empty";
        return std::nullopt;
    }

    if (region.empty()) {
        error = "region is empty";
        return std::nullopt;
    }

    double amount = 0.0;

    try {
        std::size_t consumed = 0;
        amount = std::stod(amountText, &consumed);

        if (consumed != amountText.size()) {
            error = "amount contains invalid characters";
            return std::nullopt;
        }
    } catch (const std::exception&) {
        error = "amount is not numeric";
        return std::nullopt;
    }

    if (amount < 0.0) {
        error = "amount cannot be negative";
        return std::nullopt;
    }

    if (
        status != "completed" &&
        status != "pending" &&
        status != "cancelled"
    ) {
        error = "unsupported transaction status";
        return std::nullopt;
    }

    return Transaction{
        id,
        region,
        amount,
        status
    };
}

ProcessingResult processTransactions(
    const std::vector<Transaction>& transactions
) {
    ProcessingResult result;

    for (const auto& transaction : transactions) {
        // Structured binding decomposes the aggregate into references.
        // References avoid copying strings and preserve the original record.
        const auto& [id, region, amount, status] = transaction;

        if (id.empty() || region.empty()) {
            result.rejectedIds.push_back(id);
            continue;
        }

        if (amount < 0.0) {
            result.rejectedIds.push_back(id);
            continue;
        }

        if (status == "completed") {
            result.totals[region] += amount;
        } else if (
            status != "pending" &&
            status != "cancelled"
        ) {
            result.rejectedIds.push_back(id);
        }
    }

    return result;
}

void demonstratePairAndTupleBindings() {
    std::cout << "\n=== Pair and tuple structured bindings ===\n";

    std::pair<std::string, int> serviceStatus{
        "operations-api",
        200
    };

    const auto& [serviceName, statusCode] = serviceStatus;

    std::cout
        << serviceName
        << " returned "
        << statusCode
        << '\n';

    auto metrics = std::make_tuple(
        "latency",
        84.5,
        true
    );

    const auto& [metricName, metricValue, healthy] = metrics;

    std::cout
        << metricName
        << "="
        << metricValue
        << ", healthy="
        << std::boolalpha
        << healthy
        << '\n';
}

void demonstrateArrayBindings() {
    std::cout << "\n=== Array structured bindings ===\n";

    int coordinates[] = {28, 77, 2090};

    const auto& [latitudePart, longitudePart, precisionPart] =
        coordinates;

    std::cout
        << "parts="
        << latitudePart
        << ", "
        << longitudePart
        << ", "
        << precisionPart
        << '\n';
}

void demonstrateTransactionalRecords() {
    std::cout << "\n=== Transaction processing ===\n";

    std::vector<Transaction> transactions{
        {"TX001", "North", 12500.0, "completed"},
        {"TX002", "North", 3000.0, "pending"},
        {"TX003", "South", 8900.0, "completed"},
        {"TX004", "North", 1500.0, "cancelled"},
        {"TX005", "South", 2100.0, "completed"}
    };

    const auto result = processTransactions(transactions);

    std::cout << std::fixed << std::setprecision(2);

    for (const auto& [region, total] : result.totals) {
        std::cout
            << region
            << ": "
            << total
            << '\n';
    }

    std::cout << "Rejected records: ";

    if (result.rejectedIds.empty()) {
        std::cout << "none\n";
    } else {
        for (const auto& id : result.rejectedIds) {
            std::cout << id << ' ';
        }
        std::cout << '\n';
    }
}

void demonstrateParsingAndFailureHandling() {
    std::cout << "\n=== Parsing and failure handling ===\n";

    const std::vector<std::string> lines{
        "TX101,West,7200.50,completed",
        "TX102,East,1800.00,pending",
        "TX103,North,-20.00,completed",
        "TX104,South,not-a-number,completed",
        "TX105,Central,900.00,unknown"
    };

    for (const auto& line : lines) {
        std::string error;

        const auto transaction = parseTransaction(line, error);

        if (!transaction) {
            std::cout
                << "Rejected: "
                << line
                << " -> "
                << error
                << '\n';
            continue;
        }

        const auto& [id, region, amount, status] = *transaction;

        std::cout
            << "Accepted: "
            << id
            << " / "
            << region
            << " / "
            << amount
            << " / "
            << status
            << '\n';
    }
}

void demonstrateCopyVersusReference() {
    std::cout << "\n=== Binding references versus copies ===\n";

    std::pair<std::string, int> record{
        "warehouse",
        42
    };

    auto [copyName, copyValue] = record;

    const auto& [referenceName, referenceValue] = record;

    copyName = "modified-copy";

    std::cout
        << "Original after copy modification: "
        << record.first
        << '\n';

    std::cout
        << "Reference observes original: "
        << referenceName
        << " / "
        << referenceValue
        << '\n';
}

void demonstrateAlgorithmicTradeoff() {
    std::cout << "\n=== Algorithmic trade-off ===\n";

    std::vector<Transaction> transactions{
        {"A", "North", 100.0, "completed"},
        {"B", "South", 200.0, "completed"},
        {"C", "North", 300.0, "completed"},
        {"D", "South", 50.0, "cancelled"}
    };

    /*
     * The aggregation uses std::map. Each insertion/update is O(log R),
     * where R is the number of distinct regions. Traversing all transactions
     * remains O(N), so the complete aggregation is O(N log R).
     *
     * An unordered_map could provide expected O(1) aggregation, but a map
     * provides deterministic sorted output and predictable tree semantics.
     */
    const auto result = processTransactions(transactions);

    for (const auto& [region, total] : result.totals) {
        std::cout
            << region
            << " => "
            << total
            << '\n';
    }
}

int main() {
    try {
        demonstratePairAndTupleBindings();
        demonstrateArrayBindings();
        demonstrateTransactionalRecords();
        demonstrateParsingAndFailureHandling();
        demonstrateCopyVersusReference();
        demonstrateAlgorithmicTradeoff();

        std::cout << "\nCase study completed successfully.\n";
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal processing error: "
            << error.what()
            << '\n';

        return 1;
    }

    return 0;
}
