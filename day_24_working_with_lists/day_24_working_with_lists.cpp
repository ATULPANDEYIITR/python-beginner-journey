#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// ---------------------------------------------------------------------------
// Working with Lists in C++
// ---------------------------------------------------------------------------
//
// C++ does not have a standard container literally called "List" that behaves
// like Python's list or JavaScript's Array. The standard library provides
// several sequence containers:
//
//   vector   -> dynamic contiguous array; usually the closest general-purpose
//               equivalent to a Python list or JavaScript Array.
//   list     -> doubly linked list; efficient insertion/removal with an
//               iterator, but poor random access and less cache-friendly.
//   deque    -> double-ended queue; efficient insertion/removal at both ends.
//
// This case study models a warehouse inventory system. It progressively uses
// vector, algorithms, sorting, searching, validation, queue behavior,
// nested vectors, and performance-aware design.
//
// Compile with:
//   g++ -std=c++17 -O2 working_with_lists.cpp -o working_with_lists
// ---------------------------------------------------------------------------

template <typename T>
void printVector(const vector<T>& values, const string& label) {
    cout << label << ": [";

    for (size_t index = 0; index < values.size(); ++index) {
        if (index > 0) {
            cout << ", ";
        }

        cout << values[index];
    }

    cout << "]\n";
}

template <typename T>
void printNestedVector(
    const vector<vector<T>>& matrix,
    const string& label
) {
    cout << label << ":\n";

    for (const auto& row : matrix) {
        cout << "  [";

        for (size_t index = 0; index < row.size(); ++index) {
            if (index > 0) {
                cout << ", ";
            }

            cout << row[index];
        }

        cout << "]\n";
    }
}

void section(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

// ---------------------------------------------------------------------------
// Fundamental vector demonstrations
// ---------------------------------------------------------------------------

void demonstrateVectorFundamentals() {
    section("1. Fundamental vector operations");

    vector<int> numbers{10, 20, 30, 40};

    printVector(numbers, "Initial vector");

    cout << "First element: " << numbers.front() << "\n";
    cout << "Last element: " << numbers.back() << "\n";
    cout << "Size: " << numbers.size() << "\n";
    cout << "Capacity: " << numbers.capacity() << "\n";

    numbers.push_back(50);
    printVector(numbers, "After push_back");

    numbers.insert(numbers.begin() + 1, 15);
    printVector(numbers, "After insertion");

    numbers.erase(numbers.begin() + 1);
    printVector(numbers, "After erase");

    // at() performs bounds checking and throws std::out_of_range for an
    // invalid index. operator[] does not perform bounds checking.
    try {
        cout << "Checked access: " << numbers.at(100) << "\n";
    } catch (const out_of_range& error) {
        cout << "Invalid access handled: " << error.what() << "\n";
    }
}

// ---------------------------------------------------------------------------
// Copying and references
// ---------------------------------------------------------------------------

void demonstrateCopyAndReference() {
    section("2. Copying versus referencing");

    vector<int> original{1, 2, 3};

    // Copy creates an independent vector.
    vector<int> copied = original;
    copied.push_back(4);

    printVector(original, "Original after copied mutation");
    printVector(copied, "Copied vector");

    // A reference is another name for the same vector.
    vector<int>& reference = original;
    reference.push_back(99);

    printVector(original, "Original after reference mutation");

    // const reference avoids copying while preventing modification through
    // that reference.
    const vector<int>& readOnlyReference = original;
    cout << "Read-only reference size: "
         << readOnlyReference.size() << "\n";
}

// ---------------------------------------------------------------------------
// Iteration
// ---------------------------------------------------------------------------

void demonstrateIteration() {
    section("3. Iteration");

    vector<string> names{"Alice", "Bob", "Charlie"};

    cout << "Range-based for:\n";

    for (const string& name : names) {
        cout << "  " << name << "\n";
    }

    cout << "Index-based iteration:\n";

    for (size_t index = 0; index < names.size(); ++index) {
        cout << "  " << index << ": " << names[index] << "\n";
    }

    // Iterators are objects used to traverse containers.
    cout << "Iterator traversal:\n";

    for (auto iterator = names.begin(); iterator != names.end(); ++iterator) {
        cout << "  " << *iterator << "\n";
    }
}

// ---------------------------------------------------------------------------
// Standard algorithms
// ---------------------------------------------------------------------------

void demonstrateAlgorithms() {
    section("4. Standard algorithms");

    vector<int> values{7, 2, 9, 2, 5, 10};

    printVector(values, "Original");

    sort(values.begin(), values.end());
    printVector(values, "Sorted ascending");

    sort(values.rbegin(), values.rend());
    printVector(values, "Sorted descending");

    auto iterator = find(values.begin(), values.end(), 5);

    if (iterator != values.end()) {
        cout << "Found 5 at index "
             << distance(values.begin(), iterator)
             << "\n";
    }

    const int occurrences = static_cast<int>(
        count(values.begin(), values.end(), 2)
    );

    cout << "Occurrences of 2: " << occurrences << "\n";

    const bool containsTen =
        find(values.begin(), values.end(), 10) != values.end();

    cout << "Contains 10: " << boolalpha << containsTen << "\n";
}

// ---------------------------------------------------------------------------
// Transform and filtering
// ---------------------------------------------------------------------------

void demonstrateTransformAndFilter() {
    section("5. Transforming and filtering vectors");

    vector<int> values{1, 2, 3, 4, 5, 6};

    vector<int> squares;
    squares.reserve(values.size());

    transform(
        values.begin(),
        values.end(),
        back_inserter(squares),
        [](int value) {
            return value * value;
        }
    );

    printVector(squares, "Squares");

    vector<int> evenValues = values;

    // remove_if does not physically shorten the vector. erase removes the
    // unwanted suffix after remove_if moves retained values forward.
    evenValues.erase(
        remove_if(
            evenValues.begin(),
            evenValues.end(),
            [](int value) {
                return value % 2 != 0;
            }
        ),
        evenValues.end()
    );

    printVector(evenValues, "Even values");
}

// ---------------------------------------------------------------------------
// Nested vectors and matrices
// ---------------------------------------------------------------------------

void demonstrateNestedVectors() {
    section("6. Nested vectors");

    vector<vector<int>> matrix{
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    printNestedVector(matrix, "Matrix");

    cout << "Middle value: " << matrix.at(1).at(1) << "\n";

    // Each initializer-list row is a separate vector.
    matrix[0][0] = 99;

    printNestedVector(matrix, "Modified matrix");

    // Transpose the matrix.
    vector<vector<int>> transposed(
        matrix[0].size(),
        vector<int>(matrix.size())
    );

    for (size_t row = 0; row < matrix.size(); ++row) {
        for (size_t column = 0; column < matrix[row].size(); ++column) {
            transposed[column][row] = matrix[row][column];
        }
    }

    printNestedVector(transposed, "Transpose");
}

// ---------------------------------------------------------------------------
// Stack and queue behavior
// ---------------------------------------------------------------------------

void demonstrateStackAndQueue() {
    section("7. Stack and queue behavior");

    vector<string> stack;

    stack.push_back("task A");
    stack.push_back("task B");
    stack.push_back("task C");

    printVector(stack, "Stack");

    cout << "Popped: " << stack.back() << "\n";
    stack.pop_back();

    printVector(stack, "Stack after pop");

    // std::queue is normally preferable to repeatedly erasing the first
    // element of a vector. Vector erase at the front shifts remaining items.
    queue<string> customerQueue;

    customerQueue.push("customer 1");
    customerQueue.push("customer 2");
    customerQueue.push("customer 3");

    cout << "Dequeued: " << customerQueue.front() << "\n";
    customerQueue.pop();

    cout << "Queue size: " << customerQueue.size() << "\n";
}

// ---------------------------------------------------------------------------
// Binary search
// ---------------------------------------------------------------------------

optional<size_t> binarySearch(
    const vector<int>& values,
    int target
) {
    size_t left = 0;
    size_t right = values.size();

    while (left < right) {
        const size_t middle = left + (right - left) / 2;

        if (values[middle] == target) {
            return middle;
        }

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return nullopt;
}

void demonstrateBinarySearch() {
    section("8. Binary search");

    const vector<int> sortedValues{
        3, 7, 12, 18, 24, 31, 42
    };

    const auto found = binarySearch(sortedValues, 24);
    const auto missing = binarySearch(sortedValues, 100);

    if (found.has_value()) {
        cout << "24 found at index " << found.value() << "\n";
    }

    if (!missing.has_value()) {
        cout << "100 was not found\n";
    }

    // lower_bound is the standard-library form of a binary-search boundary.
    const auto position = lower_bound(
        sortedValues.begin(),
        sortedValues.end(),
        20
    );

    cout << "Insertion position for 20: "
         << distance(sortedValues.begin(), position)
         << "\n";
}

// ---------------------------------------------------------------------------
// Two-pointer algorithm
// ---------------------------------------------------------------------------

optional<pair<int, int>> findPairWithSum(
    const vector<int>& sortedValues,
    int target
) {
    if (sortedValues.size() < 2) {
        return nullopt;
    }

    size_t left = 0;
    size_t right = sortedValues.size() - 1;

    while (left < right) {
        const int sum = sortedValues[left] + sortedValues[right];

        if (sum == target) {
            return make_pair(
                sortedValues[left],
                sortedValues[right]
            );
        }

        if (sum < target) {
            ++left;
        } else {
            --right;
        }
    }

    return nullopt;
}

void demonstrateTwoPointers() {
    section("9. Two-pointer search");

    const vector<int> values{
        1, 3, 4, 6, 8, 11, 15
    };

    const auto result = findPairWithSum(values, 14);

    if (result.has_value()) {
        cout << "Pair: "
             << result->first
             << " + "
             << result->second
             << " = 14\n";
    } else {
        cout << "No pair found\n";
    }
}

// ---------------------------------------------------------------------------
// Frequency analysis
// ---------------------------------------------------------------------------

void demonstrateFrequencyAnalysis() {
    section("10. Frequency analysis");

    const vector<string> values{
        "apple",
        "banana",
        "apple",
        "orange",
        "banana",
        "apple"
    };

    unordered_map<string, int> frequencies;

    for (const string& value : values) {
        ++frequencies[value];
    }

    for (const auto& [value, countValue] : frequencies) {
        cout << value << ": " << countValue << "\n";
    }
}

// ---------------------------------------------------------------------------
// Remove duplicates while preserving first occurrence
// ---------------------------------------------------------------------------

template <typename T>
vector<T> uniquePreservingOrder(const vector<T>& values) {
    unordered_set<T> seen;
    vector<T> result;

    result.reserve(values.size());

    for (const T& value : values) {
        if (seen.insert(value).second) {
            result.push_back(value);
        }
    }

    return result;
}

void demonstrateUniqueValues() {
    section("11. Duplicate removal");

    const vector<int> values{
        4, 2, 4, 1, 2, 3, 1
    };

    const vector<int> uniqueValues =
        uniquePreservingOrder(values);

    printVector(values, "Original");
    printVector(uniqueValues, "Unique preserving first occurrence");
}

// ---------------------------------------------------------------------------
// Data model for the inventory case study
// ---------------------------------------------------------------------------

struct InventoryItem {
    string sku;
    string name;
    int quantity;
    double price;
};

ostream& operator<<(ostream& output, const InventoryItem& item) {
    output << "{sku=" << item.sku
           << ", name=" << item.name
           << ", quantity=" << item.quantity
           << ", price=" << fixed << setprecision(2)
           << item.price
           << "}";

    return output;
}

void printInventory(
    const vector<InventoryItem>& inventory,
    const string& label
) {
    cout << label << ":\n";

    for (const InventoryItem& item : inventory) {
        cout << "  " << item << "\n";
    }
}

// ---------------------------------------------------------------------------
// Inventory manager
// ---------------------------------------------------------------------------

class InventoryManager {
private:
    vector<InventoryItem> items;

    static void validateItem(const InventoryItem& item) {
        if (item.sku.empty()) {
            throw invalid_argument("SKU cannot be empty");
        }

        if (item.name.empty()) {
            throw invalid_argument("Name cannot be empty");
        }

        if (item.quantity < 0) {
            throw invalid_argument("Quantity cannot be negative");
        }

        if (
            !numeric_limits<double>::is_iec559 ||
            !isfinite(item.price) ||
            item.price < 0.0
        ) {
            throw invalid_argument("Price must be finite and non-negative");
        }
    }

public:
    void addItem(const InventoryItem& item) {
        validateItem(item);

        const auto existing = findBySku(item.sku);

        if (existing != nullptr) {
            throw invalid_argument(
                "Duplicate SKU: " + item.sku
            );
        }

        items.push_back(item);
    }

    InventoryItem* findBySku(const string& sku) {
        for (InventoryItem& item : items) {
            if (item.sku == sku) {
                return &item;
            }
        }

        return nullptr;
    }

    const InventoryItem* findBySku(const string& sku) const {
        for (const InventoryItem& item : items) {
            if (item.sku == sku) {
                return &item;
            }
        }

        return nullptr;
    }

    void adjustStock(
        const string& sku,
        int adjustment
    ) {
        InventoryItem* item = findBySku(sku);

        if (item == nullptr) {
            throw out_of_range("SKU not found: " + sku);
        }

        if (adjustment < 0 &&
            item->quantity < -adjustment) {
            throw invalid_argument(
                "Stock quantity cannot become negative"
            );
        }

        if (adjustment > 0 &&
            item->quantity >
                numeric_limits<int>::max() - adjustment) {
            throw overflow_error(
                "Stock quantity would overflow int"
            );
        }

        item->quantity += adjustment;
    }

    double totalValue() const {
        return accumulate(
            items.begin(),
            items.end(),
            0.0,
            [](double total, const InventoryItem& item) {
                return total +
                    static_cast<double>(item.quantity) *
                    item.price;
            }
        );
    }

    vector<InventoryItem> expensiveFirst() const {
        // Return a copy so that presenting a sorted view does not reorder the
        // primary inventory vector.
        vector<InventoryItem> result = items;

        sort(
            result.begin(),
            result.end(),
            [](const InventoryItem& left,
               const InventoryItem& right) {
                if (left.price != right.price) {
                    return left.price > right.price;
                }

                return left.sku < right.sku;
            }
        );

        return result;
    }

    const vector<InventoryItem>& getItems() const {
        return items;
    }
};

// ---------------------------------------------------------------------------
// Inventory case study
// ---------------------------------------------------------------------------

void demonstrateInventoryCaseStudy() {
    section("12. Industry-style inventory case study");

    InventoryManager manager;

    manager.addItem({
        "LAP-001",
        "Laptop",
        8,
        75000.0
    });

    manager.addItem({
        "PHN-002",
        "Phone",
        15,
        42000.0
    });

    manager.addItem({
        "MON-003",
        "Monitor",
        12,
        18000.0
    });

    printInventory(
        manager.getItems(),
        "Initial inventory"
    );

    cout << "Total inventory value: "
         << fixed << setprecision(2)
         << manager.totalValue()
         << "\n";

    manager.adjustStock("PHN-002", -3);

    printInventory(
        manager.getItems(),
        "After phone stock adjustment"
    );

    const InventoryItem* phone =
        manager.findBySku("PHN-002");

    if (phone != nullptr) {
        cout << "Found item: " << *phone << "\n";
    }

    const vector<InventoryItem> sortedView =
        manager.expensiveFirst();

    printInventory(
        sortedView,
        "Expensive-first view"
    );

    // Duplicate SKU validation.
    try {
        manager.addItem({
            "PHN-002",
            "Duplicate Phone",
            1,
            100.0
        });
    } catch (const exception& error) {
        cout << "Duplicate rejected: "
             << error.what()
             << "\n";
    }

    // Negative-stock validation.
    try {
        manager.adjustStock("PHN-002", -100);
    } catch (const exception& error) {
        cout << "Invalid stock adjustment rejected: "
             << error.what()
             << "\n";
    }

    // Missing SKU validation.
    try {
        manager.adjustStock("UNKNOWN", 1);
    } catch (const exception& error) {
        cout << "Missing SKU rejected: "
             << error.what()
             << "\n";
    }
}

// ---------------------------------------------------------------------------
// Merging sorted vectors
// ---------------------------------------------------------------------------

vector<int> mergeSortedVectors(
    const vector<int>& left,
    const vector<int>& right
) {
    vector<int> result;

    result.reserve(left.size() + right.size());

    size_t leftIndex = 0;
    size_t rightIndex = 0;

    while (
        leftIndex < left.size() &&
        rightIndex < right.size()
    ) {
        if (left[leftIndex] <= right[rightIndex]) {
            result.push_back(left[leftIndex]);
            ++leftIndex;
        } else {
            result.push_back(right[rightIndex]);
            ++rightIndex;
        }
    }

    result.insert(
        result.end(),
        left.begin() + static_cast<ptrdiff_t>(leftIndex),
        left.end()
    );

    result.insert(
        result.end(),
        right.begin() + static_cast<ptrdiff_t>(rightIndex),
        right.end()
    );

    return result;
}

void demonstrateMerge() {
    section("13. Merging sorted vectors");

    const vector<int> left{1, 4, 7, 10};
    const vector<int> right{2, 3, 8, 11};

    const vector<int> merged =
        mergeSortedVectors(left, right);

    printVector(left, "Left");
    printVector(right, "Right");
    printVector(merged, "Merged");
}

// ---------------------------------------------------------------------------
// Rotate a vector
// ---------------------------------------------------------------------------

template <typename T>
void rotateRight(vector<T>& values, size_t positions) {
    if (values.empty()) {
        return;
    }

    positions %= values.size();

    // std::rotate uses linear-time element rearrangement.
    rotate(
        values.rbegin(),
        values.rbegin() + static_cast<ptrdiff_t>(positions),
        values.rend()
    );
}

void demonstrateRotation() {
    section("14. Vector rotation");

    vector<int> values{1, 2, 3, 4, 5};

    rotateRight(values, 2);

    printVector(values, "Rotated right by two");
}

// ---------------------------------------------------------------------------
// Chunking
// ---------------------------------------------------------------------------

template <typename T>
vector<vector<T>> chunkVector(
    const vector<T>& values,
    size_t chunkSize
) {
    if (chunkSize == 0) {
        throw invalid_argument(
            "Chunk size must be greater than zero"
        );
    }

    vector<vector<T>> result;

    for (
        size_t start = 0;
        start < values.size();
        start += chunkSize
    ) {
        const size_t end =
            min(start + chunkSize, values.size());

        result.emplace_back(
            values.begin() + static_cast<ptrdiff_t>(start),
            values.begin() + static_cast<ptrdiff_t>(end)
        );
    }

    return result;
}

void demonstrateChunking() {
    section("15. Chunking");

    const vector<int> values{
        1, 2, 3, 4, 5, 6, 7
    };

    const auto chunks = chunkVector(values, 3);

    for (size_t index = 0; index < chunks.size(); ++index) {
        printVector(
            chunks[index],
            "Chunk " + to_string(index + 1)
        );
    }

    try {
        chunkVector(values, 0);
    } catch (const exception& error) {
        cout << "Invalid chunk size rejected: "
             << error.what()
             << "\n";
    }
}

// ---------------------------------------------------------------------------
// Performance demonstration
// ---------------------------------------------------------------------------

void demonstratePerformance() {
    section("16. Performance and capacity");

    constexpr size_t elementCount = 200000;

    vector<int> withoutReserve;

    const auto startWithoutReserve =
        chrono::steady_clock::now();

    for (size_t index = 0; index < elementCount; ++index) {
        withoutReserve.push_back(
            static_cast<int>(index)
        );
    }

    const auto endWithoutReserve =
        chrono::steady_clock::now();

    vector<int> withReserve;
    withReserve.reserve(elementCount);

    const auto startWithReserve =
        chrono::steady_clock::now();

    for (size_t index = 0; index < elementCount; ++index) {
        withReserve.push_back(
            static_cast<int>(index)
        );
    }

    const auto endWithReserve =
        chrono::steady_clock::now();

    const auto withoutReserveMicroseconds =
        chrono::duration_cast<chrono::microseconds>(
            endWithoutReserve - startWithoutReserve
        ).count();

    const auto withReserveMicroseconds =
        chrono::duration_cast<chrono::microseconds>(
            endWithReserve - startWithReserve
        ).count();

    cout << "Without reserve: "
         << withoutReserveMicroseconds
         << " microseconds\n";

    cout << "With reserve: "
         << withReserveMicroseconds
         << " microseconds\n";

    cout << "Final capacity without reserve: "
         << withoutReserve.capacity()
         << "\n";

    cout << "Final capacity with reserve: "
         << withReserve.capacity()
         << "\n";

    cout << "reserve() can reduce reallocations when the required "
            "size is known or can be estimated.\n";
}

// ---------------------------------------------------------------------------
// List versus vector demonstration
// ---------------------------------------------------------------------------

void demonstrateContainerChoice() {
    section("17. Choosing the appropriate sequence container");

    cout << "vector:\n";
    cout << "  - contiguous storage\n";
    cout << "  - O(1) random access\n";
    cout << "  - amortized O(1) append\n";
    cout << "  - excellent cache locality\n";
    cout << "  - insertion in the middle can be O(n)\n\n";

    cout << "list:\n";
    cout << "  - doubly linked nodes\n";
    cout << "  - no O(1) random indexing\n";
    cout << "  - insertion/removal at a known iterator is O(1)\n";
    cout << "  - additional node and pointer overhead\n\n";

    cout << "deque:\n";
    cout << "  - efficient insertion/removal at both ends\n";
    cout << "  - random access supported\n";
    cout << "  - storage is not one contiguous array\n";
}

// ---------------------------------------------------------------------------
// Lightweight tests
// ---------------------------------------------------------------------------

void demonstrateTests() {
    section("18. Lightweight tests");

    const vector<int> input{4, 2, 4, 1, 2, 3, 1};
    const vector<int> expected{4, 2, 1, 3};

    const vector<int> actual =
        uniquePreservingOrder(input);

    assert(actual == expected);

    const vector<int> sortedLeft{1, 4, 7};
    const vector<int> sortedRight{2, 3, 8};

    const vector<int> merged =
        mergeSortedVectors(
            sortedLeft,
            sortedRight
        );

    assert(
        merged ==
        vector<int>({1, 2, 3, 4, 7, 8})
    );

    assert(
        binarySearch(
            vector<int>({1, 3, 5, 7}),
            5
        ).has_value()
    );

    assert(
        !binarySearch(
            vector<int>({1, 3, 5, 7}),
            6
        ).has_value()
    );

    cout << "All assertions passed.\n";
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main() {
    try {
        demonstrateVectorFundamentals();
        demonstrateCopyAndReference();
        demonstrateIteration();
        demonstrateAlgorithms();
        demonstrateTransformAndFilter();
        demonstrateNestedVectors();
        demonstrateStackAndQueue();
        demonstrateBinarySearch();
        demonstrateTwoPointers();
        demonstrateFrequencyAnalysis();
        demonstrateUniqueValues();
        demonstrateInventoryCaseStudy();
        demonstrateMerge();
        demonstrateRotation();
        demonstrateChunking();
        demonstratePerformance();
        demonstrateContainerChoice();
        demonstrateTests();

        section("Study program completed");
        cout << "All C++ list and vector case-study demonstrations "
                "completed successfully.\n";

        return 0;
    } catch (const exception& error) {
        cerr << "Unhandled error: "
             << error.what()
             << "\n";

        return 1;
    }
}
