#include <algorithm>
#include <chrono>
#include <cctype>
#include <exception>
#include <iomanip>
#include <iostream>
#include <optional>
#include <ranges>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

struct Product {
    string name;
    double price;
    int stock;
    string category;
};

struct ProductProjection {
    string name;
    double inventoryValue;
};

void printHeading(const string& title) {
    cout << "\n" << string(72, '=') << "\n";
    cout << title << "\n";
    cout << string(72, '=') << "\n";
}

template <typename T>
void printVector(const vector<T>& values) {
    cout << "[";
    for (size_t index = 0; index < values.size(); ++index) {
        if (index != 0) {
            cout << ", ";
        }
        cout << values[index];
    }
    cout << "]\n";
}

/*
 * C++ has no Python-style list-comprehension syntax.
 * A range pipeline expresses the same conceptual stages:
 * source -> filter -> transform -> materialize.
 *
 * The case study models product inventory analysis, where a business rule
 * selects eligible products and then projects them into derived values.
 */

vector<int> squareEvenNumbers(const vector<int>& numbers) {
    vector<int> result;

    // reserve() prevents repeated reallocations when the approximate output
    // size is known. The exact result may be smaller because of filtering.
    result.reserve(numbers.size());

    for (const int number : numbers) {
        if (number % 2 == 0) {
            result.push_back(number * number);
        }
    }

    return result;
}

vector<ProductProjection> buildInventoryProjection(
    const vector<Product>& products
) {
    vector<ProductProjection> result;

    for (const Product& product : products) {
        if (product.stock <= 0) {
            continue;
        }

        if (product.price <= 0.0) {
            continue;
        }

        if (product.category != "hardware") {
            continue;
        }

        result.push_back({
            product.name,
            product.price * product.stock
        });
    }

    return result;
}

vector<string> findEligibleProducts(const vector<Product>& products) {
    vector<string> names;

    for (const Product& product : products) {
        if (product.category == "hardware" && product.stock > 0) {
            names.push_back(product.name);
        }
    }

    return names;
}

vector<string> normalizeWords(const vector<string>& words) {
    vector<string> result;
    result.reserve(words.size());

    for (const string& word : words) {
        if (word.empty()) {
            continue;
        }

        string normalized;
        normalized.reserve(word.size());

        for (unsigned char character : word) {
            normalized.push_back(
                static_cast<char>(tolower(character))
            );
        }

        result.push_back(std::move(normalized));
    }

    return result;
}

vector<int> uniqueSquares(const vector<int>& values) {
    vector<int> result;
    unordered_set<int> seen;

    for (const int value : values) {
        const int square = value * value;

        // This is the C++ equivalent of retaining only distinct transformed
        // values rather than distinct source values.
        if (seen.insert(square).second) {
            result.push_back(square);
        }
    }

    return result;
}

optional<double> calculateAverage(const vector<int>& values) {
    if (values.empty()) {
        return nullopt;
    }

    long long total = 0;

    for (const int value : values) {
        total += value;
    }

    return static_cast<double>(total) / values.size();
}

void demonstrateRanges() {
    printHeading("C++20 ranges: lazy filtering and transformation");

    vector<int> numbers{1, 2, 3, 4, 5, 6, 7, 8};

    auto evenSquaresView =
        numbers
        | views::filter([](int number) {
            return number % 2 == 0;
        })
        | views::transform([](int number) {
            return number * number;
        });

    vector<int> materialized(
        evenSquaresView.begin(),
        evenSquaresView.end()
    );

    printVector(materialized);

    /*
     * A view is lazy. The transformation does not necessarily materialize
     * a second complete vector until the result is explicitly copied.
     * This is useful for large processing pipelines.
     */
}

void demonstrateCaseStudy() {
    printHeading("Inventory projection case study");

    const vector<Product> products{
        {"Keyboard", 79.99, 12, "hardware"},
        {"Mouse", 29.99, 0, "hardware"},
        {"Monitor", 249.50, 7, "hardware"},
        {"Notebook", 8.50, 25, "stationery"},
        {"Cable", 12.75, 18, "hardware"},
        {"Invalid device", -10.00, 4, "hardware"}
    };

    const vector<string> eligible = findEligibleProducts(products);

    cout << "Eligible hardware products:\n";
    for (const string& name : eligible) {
        cout << "  " << name << "\n";
    }

    const auto projections = buildInventoryProjection(products);

    cout << fixed << setprecision(2);
    cout << "Inventory projections:\n";

    for (const auto& projection : projections) {
        cout << "  " << projection.name
             << " = " << projection.inventoryValue << "\n";
    }
}

void demonstrateEdgeCases() {
    printHeading("Edge cases");

    const vector<int> empty;
    const auto emptySquares = squareEvenNumbers(empty);

    cout << "Empty input result size: "
         << emptySquares.size() << "\n";

    const vector<int> noMatches{1, 3, 5, 7};
    const auto noSquares = squareEvenNumbers(noMatches);

    cout << "No-match result size: "
         << noSquares.size() << "\n";

    const vector<int> duplicateInput{2, 2, 3, 3, 4};
    const auto distinct = uniqueSquares(duplicateInput);

    cout << "Distinct transformed values: ";
    printVector(distinct);

    const auto average = calculateAverage(empty);

    if (!average.has_value()) {
        cout << "Average correctly rejected for empty input.\n";
    }
}

void demonstrateValidation() {
    printHeading("Validation before transformation");

    const vector<Product> products{
        {"Valid", 50.0, 5, "hardware"},
        {"Zero stock", 50.0, 0, "hardware"},
        {"Negative price", -1.0, 5, "hardware"},
        {"Wrong category", 50.0, 5, "stationery"}
    };

    const auto result = buildInventoryProjection(products);

    cout << "Valid projection count: "
         << result.size() << "\n";

    /*
     * Validation occurs before the multiplication. Without validation,
     * negative prices or invalid stock could silently produce financially
     * misleading inventory values.
     */
}

void demonstratePerformance() {
    printHeading("Materialization and performance");

    constexpr int count = 500'000;

    vector<int> numbers;
    numbers.reserve(count);

    for (int index = 0; index < count; ++index) {
        numbers.push_back(index);
    }

    const auto start = chrono::steady_clock::now();

    const auto result = squareEvenNumbers(numbers);

    const auto finish = chrono::steady_clock::now();

    const chrono::duration<double, milli> elapsed = finish - start;

    cout << "Input size: " << numbers.size() << "\n";
    cout << "Output size: " << result.size() << "\n";
    cout << "Processing time: " << elapsed.count() << " ms\n";

    /*
     * The explicit vector owns its results. A ranges::view can reduce
     * intermediate allocations when downstream consumers can operate lazily.
     * Materialization is appropriate when the result must be stored,
     * iterated repeatedly, or passed across an ownership boundary.
     */
}

void demonstrateReadability() {
    printHeading("Readability and design trade-offs");

    const vector<string> words{
        "Python", "", "Comprehension", "C++", "Data"
    };

    const auto normalized = normalizeWords(words);

    cout << "Normalized words: ";
    printVector(normalized);

    /*
     * C++ offers powerful generic algorithms and ranges, but attempting to
     * compress complicated business rules into one expression can reduce
     * readability. Named functions are useful when validation or transformation
     * rules deserve independent tests and documentation.
     */
}

int main() {
    try {
        printHeading("List-Comprehension Concepts in a C++ Case Study");

        const vector<int> numbers{1, 2, 3, 4, 5, 6};

        cout << "Even squares: ";
        printVector(squareEvenNumbers(numbers));

        demonstrateRanges();
        demonstrateCaseStudy();
        demonstrateEdgeCases();
        demonstrateValidation();
        demonstratePerformance();
        demonstrateReadability();

        return 0;
    } catch (const exception& error) {
        cerr << "Unexpected failure: " << error.what() << '\n';
        return 1;
    }
}
