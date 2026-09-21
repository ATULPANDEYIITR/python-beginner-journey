/*
 * Introduction to Lists
 * ======================
 *
 * C++17 case study:
 * Inventory and order processing system using std::vector as the primary
 * list-like data structure.
 *
 * The program demonstrates:
 *
 * - std::vector as a dynamic contiguous list
 * - indexing and bounds-safe access
 * - iteration
 * - insertion and deletion
 * - searching
 * - sorting
 * - filtering
 * - aggregation
 * - nested vectors
 * - classes and structures
 * - validation
 * - exception handling
 * - binary search
 * - duplicate handling
 * - grouping
 * - performance considerations
 * - const correctness
 * - range-based loops
 * - algorithmic design
 *
 * Compile:
 *     g++ -std=c++17 -O2 -Wall -Wextra -pedantic lists.cpp -o lists
 *
 * Run:
 *     ./lists
 */

#include <algorithm>
#include <cmath>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;


// -----------------------------------------------------------------------------
// Utility functions
// -----------------------------------------------------------------------------

void printLine() {
    cout << string(78, '=') << '\n';
}

void section(const string& title) {
    cout << '\n';
    printLine();
    cout << title << '\n';
    printLine();
}

template <typename T>
void printVector(const vector<T>& values, const string& label) {
    cout << label << ": [";

    for (size_t index = 0; index < values.size(); ++index) {
        cout << values[index];

        if (index + 1 < values.size()) {
            cout << ", ";
        }
    }

    cout << "]\n";
}


// -----------------------------------------------------------------------------
// Basic vector demonstrations
// -----------------------------------------------------------------------------

void demonstrateBasicVectors() {
    section("1. Basic std::vector operations");

    vector<int> numbers = {10, 20, 30, 40};

    printVector(numbers, "Original");

    cout << "First element: " << numbers[0] << '\n';
    cout << "Last element: " << numbers.back() << '\n';
    cout << "Size: " << numbers.size() << '\n';
    cout << "Capacity: " << numbers.capacity() << '\n';

    numbers.push_back(50);

    printVector(numbers, "After push_back");

    numbers.pop_back();

    printVector(numbers, "After pop_back");

    numbers.insert(numbers.begin() + 1, 15);

    printVector(numbers, "After inserting 15");

    numbers.erase(numbers.begin() + 1);

    printVector(numbers, "After erasing index 1");
}


// -----------------------------------------------------------------------------
// Bounds-safe access
// -----------------------------------------------------------------------------

void demonstrateBoundsSafety() {
    section("2. Bounds-safe access");

    vector<int> values = {10, 20, 30};

    cout << "values.at(1): " << values.at(1) << '\n';

    try {
        cout << values.at(100) << '\n';
    } catch (const out_of_range& error) {
        cout << "Handled invalid index: " << error.what() << '\n';
    }

    /*
     * operator[] does not perform bounds checking.
     * at() performs a checked access and throws std::out_of_range when the
     * index is invalid.
     */
}


// -----------------------------------------------------------------------------
// Iteration
// -----------------------------------------------------------------------------

void demonstrateIteration() {
    section("3. Iteration");

    vector<string> languages = {
        "Python",
        "JavaScript",
        "C++",
        "Java"
    };

    cout << "Range-based iteration:\n";

    for (const string& language : languages) {
        cout << "  " << language << '\n';
    }

    cout << "Index-based iteration:\n";

    for (size_t index = 0; index < languages.size(); ++index) {
        cout << "  " << index << ": " << languages[index] << '\n';
    }
}


// -----------------------------------------------------------------------------
// Search
// -----------------------------------------------------------------------------

void demonstrateSearching() {
    section("4. Searching");

    vector<int> values = {10, 20, 30, 40, 50};

    auto iterator = find(values.begin(), values.end(), 30);

    if (iterator != values.end()) {
        cout << "30 found at index "
             << distance(values.begin(), iterator)
             << '\n';
    } else {
        cout << "30 not found\n";
    }

    iterator = find(values.begin(), values.end(), 99);

    if (iterator == values.end()) {
        cout << "99 was not found.\n";
    }
}


// -----------------------------------------------------------------------------
// Sorting
// -----------------------------------------------------------------------------

void demonstrateSorting() {
    section("5. Sorting");

    vector<int> values = {50, 10, 40, 20, 30};

    printVector(values, "Before sorting");

    sort(values.begin(), values.end());

    printVector(values, "Ascending");

    sort(values.begin(), values.end(), greater<int>());

    printVector(values, "Descending");
}


// -----------------------------------------------------------------------------
// Algorithms: min, max, sum, count
// -----------------------------------------------------------------------------

void demonstrateAlgorithms() {
    section("6. Standard algorithms");

    vector<int> values = {10, 20, 20, 30, 40};

    const int minimum = *min_element(values.begin(), values.end());
    const int maximum = *max_element(values.begin(), values.end());

    const int total = accumulate(
        values.begin(),
        values.end(),
        0
    );

    const auto twenties = count(
        values.begin(),
        values.end(),
        20
    );

    cout << "Minimum: " << minimum << '\n';
    cout << "Maximum: " << maximum << '\n';
    cout << "Total: " << total << '\n';
    cout << "Number of 20s: " << twenties << '\n';
}


// -----------------------------------------------------------------------------
// Filtering
// -----------------------------------------------------------------------------

vector<int> filterEvenNumbers(const vector<int>& values) {
    vector<int> result;

    for (const int value : values) {
        if (value % 2 == 0) {
            result.push_back(value);
        }
    }

    return result;
}

void demonstrateFiltering() {
    section("7. Filtering");

    const vector<int> values = {1, 2, 3, 4, 5, 6};

    const vector<int> evenValues = filterEvenNumbers(values);

    printVector(values, "Original");
    printVector(evenValues, "Even values");
}


// -----------------------------------------------------------------------------
// Nested vectors
// -----------------------------------------------------------------------------

void demonstrateNestedVectors() {
    section("8. Nested vectors");

    vector<vector<int>> matrix = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    cout << "Matrix:\n";

    for (const auto& row : matrix) {
        printVector(row, "  Row");
    }

    cout << "Element [1][2]: "
         << matrix.at(1).at(2)
         << '\n';
}


// -----------------------------------------------------------------------------
// Matrix validation
// -----------------------------------------------------------------------------

bool isRectangular(const vector<vector<int>>& matrix) {
    if (matrix.empty()) {
        return true;
    }

    const size_t expectedWidth = matrix.front().size();

    return all_of(
        matrix.begin(),
        matrix.end(),
        [expectedWidth](const vector<int>& row) {
            return row.size() == expectedWidth;
        }
    );
}

void demonstrateMatrixValidation() {
    section("9. Matrix validation");

    const vector<vector<int>> validMatrix = {
        {1, 2},
        {3, 4}
    };

    const vector<vector<int>> invalidMatrix = {
        {1, 2},
        {3}
    };

    cout << boolalpha;
    cout << "Valid matrix: "
         << isRectangular(validMatrix)
         << '\n';

    cout << "Invalid matrix: "
         << isRectangular(invalidMatrix)
         << '\n';
}


// -----------------------------------------------------------------------------
// Product model
// -----------------------------------------------------------------------------

struct Product {
    int id;
    string name;
    string category;
    double price;
    int quantity;

    double inventoryValue() const {
        return price * static_cast<double>(quantity);
    }
};


// -----------------------------------------------------------------------------
// Order model
// -----------------------------------------------------------------------------

struct Order {
    int id;
    int productId;
    int quantity;
};


// -----------------------------------------------------------------------------
// Inventory system
// -----------------------------------------------------------------------------

class InventorySystem {
private:
    vector<Product> products;
    vector<Order> orders;

public:
    void addProduct(const Product& product) {
        if (product.id <= 0) {
            throw invalid_argument("Product ID must be positive.");
        }

        if (product.name.empty()) {
            throw invalid_argument("Product name cannot be empty.");
        }

        if (product.price < 0.0) {
            throw invalid_argument("Product price cannot be negative.");
        }

        if (product.quantity < 0) {
            throw invalid_argument("Product quantity cannot be negative.");
        }

        const auto duplicate = findProduct(product.id);

        if (duplicate.has_value()) {
            throw invalid_argument("Product ID already exists.");
        }

        products.push_back(product);
    }

    optional<reference_wrapper<const Product>>
    findProduct(int productId) const {
        const auto iterator = find_if(
            products.begin(),
            products.end(),
            [productId](const Product& product) {
                return product.id == productId;
            }
        );

        if (iterator == products.end()) {
            return nullopt;
        }

        return cref(*iterator);
    }

    optional<reference_wrapper<Product>>
    findMutableProduct(int productId) {
        const auto iterator = find_if(
            products.begin(),
            products.end(),
            [productId](const Product& product) {
                return product.id == productId;
            }
        );

        if (iterator == products.end()) {
            return nullopt;
        }

        return ref(*iterator);
    }

    void placeOrder(int orderId, int productId, int quantity) {
        if (orderId <= 0) {
            throw invalid_argument("Order ID must be positive.");
        }

        if (quantity <= 0) {
            throw invalid_argument("Order quantity must be positive.");
        }

        const auto product = findMutableProduct(productId);

        if (!product.has_value()) {
            throw invalid_argument("Product does not exist.");
        }

        Product& selectedProduct = product->get();

        if (selectedProduct.quantity < quantity) {
            throw runtime_error(
                "Insufficient stock for product: " +
                selectedProduct.name
            );
        }

        selectedProduct.quantity -= quantity;

        orders.push_back({
            orderId,
            productId,
            quantity
        });
    }

    double totalInventoryValue() const {
        return accumulate(
            products.begin(),
            products.end(),
            0.0,
            [](double total, const Product& product) {
                return total + product.inventoryValue();
            }
        );
    }

    vector<Product> outOfStockProducts() const {
        vector<Product> result;

        copy_if(
            products.begin(),
            products.end(),
            back_inserter(result),
            [](const Product& product) {
                return product.quantity == 0;
            }
        );

        return result;
    }

    vector<Product> productsAbovePrice(double minimumPrice) const {
        vector<Product> result;

        copy_if(
            products.begin(),
            products.end(),
            back_inserter(result),
            [minimumPrice](const Product& product) {
                return product.price >= minimumPrice;
            }
        );

        return result;
    }

    map<string, double> inventoryValueByCategory() const {
        map<string, double> totals;

        for (const Product& product : products) {
            totals[product.category] += product.inventoryValue();
        }

        return totals;
    }

    vector<Product> productsSortedByValueDescending() const {
        vector<Product> result = products;

        sort(
            result.begin(),
            result.end(),
            [](const Product& first, const Product& second) {
                if (first.inventoryValue() != second.inventoryValue()) {
                    return first.inventoryValue() >
                           second.inventoryValue();
                }

                return first.name < second.name;
            }
        );

        return result;
    }

    const vector<Product>& getProducts() const {
        return products;
    }

    const vector<Order>& getOrders() const {
        return orders;
    }
};


// -----------------------------------------------------------------------------
// Printing domain records
// -----------------------------------------------------------------------------

void printProduct(const Product& product) {
    cout << left
         << setw(5) << product.id
         << setw(15) << product.name
         << setw(15) << product.category
         << setw(12) << fixed << setprecision(2) << product.price
         << setw(8) << product.quantity
         << setw(14) << product.inventoryValue()
         << '\n';
}

void printProductTable(const vector<Product>& products) {
    cout << left
         << setw(5) << "ID"
         << setw(15) << "Name"
         << setw(15) << "Category"
         << setw(12) << "Price"
         << setw(8) << "Qty"
         << setw(14) << "Value"
         << '\n';

    cout << string(69, '-') << '\n';

    for (const Product& product : products) {
        printProduct(product);
    }
}


// -----------------------------------------------------------------------------
// Binary search
// -----------------------------------------------------------------------------

int binarySearch(const vector<int>& values, int target) {
    int left = 0;
    int right = static_cast<int>(values.size()) - 1;

    while (left <= right) {
        const int middle = left + (right - left) / 2;

        if (values[middle] == target) {
            return middle;
        }

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

void demonstrateBinarySearch() {
    section("10. Binary search");

    const vector<int> values = {
        10, 20, 30, 40, 50, 60
    };

    cout << "Index of 40: "
         << binarySearch(values, 40)
         << '\n';

    cout << "Index of 99: "
         << binarySearch(values, 99)
         << '\n';

    /*
     * Binary search is O(log n), but it requires sorted data.
     * A linear search is O(n) and does not require sorting.
     */
}


// -----------------------------------------------------------------------------
// Deduplication while preserving sorted order
// -----------------------------------------------------------------------------

vector<int> uniqueSortedValues(vector<int> values) {
    sort(values.begin(), values.end());

    values.erase(
        unique(values.begin(), values.end()),
        values.end()
    );

    return values;
}

void demonstrateDeduplication() {
    section("11. Deduplication");

    const vector<int> values = {
        4, 2, 4, 7, 2, 9, 7, 1
    };

    printVector(values, "Original");

    const vector<int> uniqueValues =
        uniqueSortedValues(values);

    printVector(uniqueValues, "Unique sorted values");
}


// -----------------------------------------------------------------------------
// Chunking
// -----------------------------------------------------------------------------

vector<vector<int>> chunkVector(
    const vector<int>& values,
    size_t chunkSize
) {
    if (chunkSize == 0) {
        throw invalid_argument("Chunk size must be greater than zero.");
    }

    vector<vector<int>> chunks;

    for (size_t start = 0; start < values.size(); start += chunkSize) {
        const size_t end = min(
            start + chunkSize,
            values.size()
        );

        chunks.emplace_back(
            values.begin() + static_cast<ptrdiff_t>(start),
            values.begin() + static_cast<ptrdiff_t>(end)
        );
    }

    return chunks;
}

void demonstrateChunking() {
    section("12. Chunking");

    const vector<int> values = {
        1, 2, 3, 4, 5, 6, 7
    };

    const auto chunks = chunkVector(values, 3);

    for (size_t index = 0; index < chunks.size(); ++index) {
        printVector(
            chunks[index],
            "Chunk " + to_string(index + 1)
        );
    }
}


// -----------------------------------------------------------------------------
// Sales analysis
// -----------------------------------------------------------------------------

struct Sale {
    int id;
    string product;
    int quantity;
    double unitPrice;

    double total() const {
        return static_cast<double>(quantity) * unitPrice;
    }
};

double calculateSalesTotal(const vector<Sale>& sales) {
    return accumulate(
        sales.begin(),
        sales.end(),
        0.0,
        [](double total, const Sale& sale) {
            return total + sale.total();
        }
    );
}

optional<Sale> highestValueSale(const vector<Sale>& sales) {
    if (sales.empty()) {
        return nullopt;
    }

    return *max_element(
        sales.begin(),
        sales.end(),
        [](const Sale& first, const Sale& second) {
            return first.total() < second.total();
        }
    );
}

void demonstrateSalesAnalysis() {
    section("13. Sales analysis");

    const vector<Sale> sales = {
        {101, "Laptop", 2, 65000.0},
        {102, "Mouse", 10, 1200.0},
        {103, "Keyboard", 5, 2500.0},
        {104, "Monitor", 3, 18000.0}
    };

    cout << fixed << setprecision(2);

    for (const Sale& sale : sales) {
        cout << sale.product
             << " -> "
             << sale.total()
             << '\n';
    }

    cout << "Total sales: "
         << calculateSalesTotal(sales)
         << '\n';

    const auto largestSale = highestValueSale(sales);

    if (largestSale.has_value()) {
        cout << "Largest sale: "
             << largestSale->product
             << " -> "
             << largestSale->total()
             << '\n';
    }
}


// -----------------------------------------------------------------------------
// Inventory case study
// -----------------------------------------------------------------------------

void demonstrateInventorySystem() {
    section("14. Industry-style inventory case study");

    InventorySystem inventory;

    inventory.addProduct({
        1,
        "Laptop",
        "Technology",
        65000.0,
        3
    });

    inventory.addProduct({
        2,
        "Mouse",
        "Accessories",
        1200.0,
        10
    });

    inventory.addProduct({
        3,
        "Keyboard",
        "Accessories",
        2500.0,
        8
    });

    inventory.addProduct({
        4,
        "Monitor",
        "Technology",
        18000.0,
        2
    });

    inventory.addProduct({
        5,
        "Webcam",
        "Accessories",
        4000.0,
        0
    });

    cout << "Initial inventory:\n";
    printProductTable(inventory.getProducts());

    cout << "\nPlacing valid orders...\n";

    inventory.placeOrder(1001, 1, 1);
    inventory.placeOrder(1002, 2, 4);
    inventory.placeOrder(1003, 3, 2);

    cout << "Inventory after orders:\n";
    printProductTable(inventory.getProducts());

    cout << "\nTotal inventory value: "
         << inventory.totalInventoryValue()
         << '\n';

    cout << "\nOut-of-stock products:\n";

    const vector<Product> outOfStock =
        inventory.outOfStockProducts();

    for (const Product& product : outOfStock) {
        cout << "  " << product.name << '\n';
    }

    cout << "\nProducts priced at or above 10000:\n";

    const vector<Product> expensiveProducts =
        inventory.productsAbovePrice(10000.0);

    for (const Product& product : expensiveProducts) {
        cout << "  "
             << product.name
             << ": "
             << product.price
             << '\n';
    }

    cout << "\nInventory value by category:\n";

    const map<string, double> categoryTotals =
        inventory.inventoryValueByCategory();

    for (const auto& [category, total] : categoryTotals) {
        cout << "  "
             << category
             << ": "
             << total
             << '\n';
    }

    cout << "\nProducts sorted by inventory value:\n";

    const vector<Product> rankedProducts =
        inventory.productsSortedByValueDescending();

    printProductTable(rankedProducts);

    cout << "\nOrders processed: "
         << inventory.getOrders().size()
         << '\n';
}


// -----------------------------------------------------------------------------
// Failure conditions
// -----------------------------------------------------------------------------

void demonstrateFailureConditions() {
    section("15. Failure conditions");

    InventorySystem inventory;

    try {
        inventory.addProduct({
            -1,
            "Invalid Product",
            "Test",
            100.0,
            5
        });
    } catch (const exception& error) {
        cout << "Invalid product rejected: "
             << error.what()
             << '\n';
    }

    try {
        inventory.addProduct({
            1,
            "Valid Product",
            "Test",
            100.0,
            2
        });

        inventory.placeOrder(100, 1, 5);
    } catch (const exception& error) {
        cout << "Invalid order rejected: "
             << error.what()
             << '\n';
    }

    try {
        inventory.addProduct({
            1,
            "Duplicate Product",
            "Test",
            200.0,
            3
        });
    } catch (const exception& error) {
        cout << "Duplicate product rejected: "
             << error.what()
             << '\n';
    }
}


// -----------------------------------------------------------------------------
// Vector capacity demonstration
// -----------------------------------------------------------------------------

void demonstrateCapacity() {
    section("16. Size and capacity");

    vector<int> values;

    cout << "Initial size: "
         << values.size()
         << '\n';

    cout << "Initial capacity: "
         << values.capacity()
         << '\n';

    /*
     * reserve() requests enough storage for a known approximate workload.
     * It can reduce reallocations when many elements will be inserted.
     */

    values.reserve(1000);

    cout << "Capacity after reserve(1000): "
         << values.capacity()
         << '\n';

    for (int index = 0; index < 1000; ++index) {
        values.push_back(index);
    }

    cout << "Size after insertion: "
         << values.size()
         << '\n';

    cout << "Capacity after insertion: "
         << values.capacity()
         << '\n';
}


// -----------------------------------------------------------------------------
// Const correctness
// -----------------------------------------------------------------------------

double sumReadOnly(const vector<double>& values) {
    /*
     * const reference:
     * - avoids copying the vector
     * - promises not to modify it
     * - works efficiently for large vectors
     */
    return accumulate(
        values.begin(),
        values.end(),
        0.0
    );
}

void demonstrateConstCorrectness() {
    section("17. const correctness");

    const vector<double> values = {
        10.5,
        20.5,
        30.5
    };

    cout << "Read-only sum: "
         << sumReadOnly(values)
         << '\n';
}


// -----------------------------------------------------------------------------
// Practical assertions
// -----------------------------------------------------------------------------

void runTests() {
    section("18. Tests");

    const vector<int> values = {
        1, 2, 3, 4, 5
    };

    const vector<int> evens =
        filterEvenNumbers(values);

    if (evens != vector<int>{2, 4}) {
        throw runtime_error("Even-number test failed.");
    }

    if (binarySearch(
            vector<int>{10, 20, 30},
            20
        ) != 1) {
        throw runtime_error("Binary-search test failed.");
    }

    if (binarySearch(
            vector<int>{10, 20, 30},
            99
        ) != -1) {
        throw runtime_error(
            "Missing-value binary-search test failed."
        );
    }

    if (!isRectangular(
            vector<vector<int>>{{1, 2}, {3, 4}}
        )) {
        throw runtime_error(
            "Rectangular-matrix test failed."
        );
    }

    if (isRectangular(
            vector<vector<int>>{{1, 2}, {3}}
        )) {
        throw runtime_error(
            "Irregular-matrix test failed."
        );
    }

    const vector<int> uniqueValues =
        uniqueSortedValues(
            vector<int>{3, 1, 3, 2, 2}
        );

    if (uniqueValues != vector<int>{1, 2, 3}) {
        throw runtime_error(
            "Deduplication test failed."
        );
    }

    cout << "All tests passed.\n";
}


// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

int main() {
    try {
        demonstrateBasicVectors();
        demonstrateBoundsSafety();
        demonstrateIteration();
        demonstrateSearching();
        demonstrateSorting();
        demonstrateAlgorithms();
        demonstrateFiltering();
        demonstrateNestedVectors();
        demonstrateMatrixValidation();
        demonstrateBinarySearch();
        demonstrateDeduplication();
        demonstrateChunking();
        demonstrateSalesAnalysis();
        demonstrateInventorySystem();
        demonstrateFailureConditions();
        demonstrateCapacity();
        demonstrateConstCorrectness();
        runTests();

        section("19. Program completed");

        cout << "The case study demonstrated how a dynamic list-like "
             << "structure can support practical data processing, "
             << "validation, searching, sorting, aggregation, and "
             << "inventory operations.\n";

        return 0;
    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }
}
