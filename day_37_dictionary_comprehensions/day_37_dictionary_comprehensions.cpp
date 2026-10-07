#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

void heading(const string& title) {
    cout << "\n" << string(72, '=') << "\n";
    cout << title << "\n";
    cout << string(72, '=') << "\n";
}

template <typename K, typename V>
void printMap(const map<K, V>& data) {
    cout << "{ ";
    for (const auto& [key, value] : data) {
        cout << key << ": " << value << " ";
    }
    cout << "}\n";
}

// C++ has no native dictionary-comprehension syntax.
// The closest idiom is constructing an associative container from
// a range with a transformation, often using explicit loops, algorithms,
// lambdas, or helper functions. This case study uses an operations
// analytics index to show why each mechanism is useful.

struct Transaction {
    string id;
    string customer;
    double amount;
    string status;
};

enum class RiskBand {
    Invalid,
    Low,
    Medium,
    High
};

string toString(RiskBand band) {
    switch (band) {
        case RiskBand::Invalid: return "invalid";
        case RiskBand::Low: return "low";
        case RiskBand::Medium: return "medium";
        case RiskBand::High: return "high";
    }

    throw logic_error("Unknown risk band");
}

RiskBand classifyAmount(double amount) {
    if (amount < 0) {
        return RiskBand::Invalid;
    }

    if (amount >= 50000) {
        return RiskBand::High;
    }

    if (amount >= 10000) {
        return RiskBand::Medium;
    }

    return RiskBand::Low;
}

// This helper captures the fundamental comprehension pattern:
// iterate over source entries, compute a key/value pair, optionally
// filter the input, then insert the result into the destination map.
template <typename Input, typename KeyFunction, typename ValueFunction,
          typename Predicate>
auto dictionaryTransform(
    const Input& source,
    KeyFunction keyFunction,
    ValueFunction valueFunction,
    Predicate predicate
) {
    using Element = typename Input::value_type;
    using Key = decay_t<invoke_result_t<KeyFunction, Element>>;
    using Value = decay_t<invoke_result_t<ValueFunction, Element>>;

    map<Key, Value> result;

    for (const auto& element : source) {
        if (predicate(element)) {
            result.emplace(
                keyFunction(element),
                valueFunction(element)
            );
        }
    }

    return result;
}

void basicTransformation() {
    heading("Basic dictionary-comprehension equivalent");

    vector<int> numbers{1, 2, 3, 4, 5};

    const auto squares = dictionaryTransform(
        numbers,
        [](int number) { return number; },
        [](int number) { return number * number; },
        [](int) { return true; }
    );

    printMap(squares);
}

void filteringAndTransformation() {
    heading("Filtering and transformation");

    vector<pair<string, int>> inventory{
        {"SSD", 8},
        {"RAM", 3},
        {"GPU", 2},
        {"CPU", 11},
        {"HDD", 0}
    };

    const auto lowStock = dictionaryTransform(
        inventory,
        [](const auto& item) { return item.first; },
        [](const auto& item) { return item.second; },
        [](const auto& item) {
            return item.second > 0 && item.second < 5;
        }
    );

    printMap(lowStock);
}

void transactionIndexing() {
    heading("Operational transaction index");

    vector<Transaction> transactions{
        {"TX1001", "Asha", 450, "completed"},
        {"TX1002", "Rahul", 17500, "completed"},
        {"TX1003", "Meera", 89000, "review"},
        {"TX1004", "Vikram", -250, "rejected"},
        {"TX1005", "Neha", 6200, "completed"}
    };

    // The transaction ID is a natural unique key. The resulting map
    // acts as an in-memory index for fast lookup by identifier.
    map<string, Transaction> index;

    for (const auto& transaction : transactions) {
        if (transaction.id.empty()) {
            throw invalid_argument("Transaction ID cannot be empty.");
        }

        if (!index.emplace(transaction.id, transaction).second) {
            throw invalid_argument(
                "Duplicate transaction ID: " + transaction.id
            );
        }
    }

    for (const auto& [id, transaction] : index) {
        cout << id << " -> "
             << transaction.customer << ", "
             << transaction.amount << ", "
             << transaction.status << "\n";
    }
}

void riskIndex() {
    heading("Derived risk classification");

    vector<Transaction> transactions{
        {"TX1001", "Asha", 450, "completed"},
        {"TX1002", "Rahul", 17500, "completed"},
        {"TX1003", "Meera", 89000, "review"},
        {"TX1004", "Vikram", -250, "rejected"}
    };

    map<string, RiskBand> riskByTransaction;

    for (const auto& transaction : transactions) {
        riskByTransaction[transaction.id] =
            classifyAmount(transaction.amount);
    }

    for (const auto& [id, band] : riskByTransaction) {
        cout << id << " -> " << toString(band) << "\n";
    }
}

void groupingWithDuplicateKeys() {
    heading("Grouping when keys are not unique");

    vector<pair<string, string>> employees{
        {"Asha", "Engineering"},
        {"Rahul", "Engineering"},
        {"Meera", "Finance"},
        {"Vikram", "Operations"}
    };

    // A direct dictionary-comprehension equivalent would overwrite
    // duplicate department keys. A multimap-like value structure is
    // required when the relationship is one-to-many.
    map<string, vector<string>> employeesByDepartment;

    for (const auto& [employee, department] : employees) {
        employeesByDepartment[department].push_back(employee);
    }

    for (const auto& [department, people] : employeesByDepartment) {
        cout << department << " -> ";
        for (const auto& person : people) {
            cout << person << " ";
        }
        cout << "\n";
    }
}

void aggregateTransactions() {
    heading("Aggregation into a derived dictionary");

    vector<Transaction> transactions{
        {"TX1", "Asha", 1200, "completed"},
        {"TX2", "Rahul", 800, "completed"},
        {"TX3", "Asha", 700, "completed"},
        {"TX4", "Meera", 2500, "completed"},
        {"TX5", "Rahul", 500, "completed"}
    };

    map<string, double> totals;

    for (const auto& transaction : transactions) {
        if (transaction.amount < 0) {
            throw invalid_argument(
                "Negative transaction cannot be aggregated."
            );
        }

        totals[transaction.customer] += transaction.amount;
    }

    const auto highValue = dictionaryTransform(
        totals,
        [](const auto& item) { return item.first; },
        [](const auto& item) { return item.second; },
        [](const auto& item) { return item.second >= 1500; }
    );

    printMap(highValue);
}

void parseAndTransform() {
    heading("Parsing records into a dictionary");

    vector<string> records{
        "101,Asha,Engineering,95000",
        "102,Rahul,Finance,72000",
        "103,Meera,Engineering,105000"
    };

    map<int, double> salaryByEmployee;

    for (const string& record : records) {
        stringstream stream(record);
        string idText;
        string name;
        string department;
        string salaryText;

        getline(stream, idText, ',');
        getline(stream, name, ',');
        getline(stream, department, ',');
        getline(stream, salaryText, ',');

        if (idText.empty() || name.empty() ||
            department.empty() || salaryText.empty()) {
            throw invalid_argument("Malformed employee record: " + record);
        }

        const int id = stoi(idText);
        const double salary = stod(salaryText);

        if (id <= 0 || salary < 0) {
            throw invalid_argument("Invalid employee data: " + record);
        }

        salaryByEmployee[id] = salary;
    }

    const auto seniorEmployees = dictionaryTransform(
        salaryByEmployee,
        [](const auto& item) { return item.first; },
        [](const auto& item) { return item.second; },
        [](const auto& item) { return item.second >= 90000; }
    );

    printMap(seniorEmployees);
}

void nestedTransformation() {
    heading("Nested dictionary transformation");

    map<string, map<string, int>> monthlySales{
        {
            "January",
            {{"North", 100}, {"South", 120}, {"West", 90}}
        },
        {
            "February",
            {{"North", 130}, {"South", 110}, {"West", 95}}
        }
    };

    map<string, map<string, int>> regionView;

    for (const auto& [month, regionalData] : monthlySales) {
        for (const auto& [region, amount] : regionalData) {
            regionView[region][month] = amount;
        }
    }

    for (const auto& [region, monthly] : regionView) {
        cout << region << ": ";
        for (const auto& [month, amount] : monthly) {
            cout << month << "=" << amount << " ";
        }
        cout << "\n";
    }
}

void performanceConsiderations() {
    heading("Performance characteristics");

    constexpr int count = 200000;

    vector<int> values;
    values.reserve(count);

    for (int i = 1; i <= count; ++i) {
        values.push_back(i);
    }

    const auto start = chrono::steady_clock::now();

    map<int, long long> squares;
    for (int value : values) {
        squares.emplace(value, 1LL * value * value);
    }

    const auto end = chrono::steady_clock::now();

    const double milliseconds =
        chrono::duration<double, milli>(end - start).count();

    cout << "Ordered map construction: "
         << fixed << setprecision(3)
         << milliseconds << " ms\n";

    cout << "Entries: " << squares.size() << "\n";

    /*
     * std::map provides O(log n) insertion and lookup.
     * std::unordered_map generally provides average O(1) lookup and
     * insertion, but does not preserve ordering and can suffer from
     * poor hash behavior. The correct container depends on the workload.
     */
}

void edgeCases() {
    heading("Edge cases");

    vector<pair<string, int>> duplicateKeys{
        {"status", 1},
        {"status", 2}
    };

    map<string, int> result;

    for (const auto& [key, value] : duplicateKeys) {
        // assignment intentionally gives last-write-wins semantics.
        result[key] = value;
    }

    printMap(result);

    vector<int> empty;

    const auto emptyResult = dictionaryTransform(
        empty,
        [](int value) { return value; },
        [](int value) { return value * value; },
        [](int) { return true; }
    );

    cout << "Empty source size: " << emptyResult.size() << "\n";
}

int main() {
    try {
        basicTransformation();
        filteringAndTransformation();
        transactionIndexing();
        riskIndex();
        groupingWithDuplicateKeys();
        aggregateTransactions();
        parseAndTransform();
        nestedTransformation();
        performanceConsiderations();
        edgeCases();
    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
