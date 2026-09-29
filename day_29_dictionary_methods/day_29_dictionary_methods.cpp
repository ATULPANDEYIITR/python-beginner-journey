#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Dictionary Methods: C++ Industry-Style Case Study
 *
 * C++ does not have a built-in "dictionary" type named dictionary.
 * std::map and std::unordered_map provide dictionary-like key-value storage.
 *
 * This case study models an inventory and order-processing service. It
 * demonstrates:
 *
 *   - unordered_map for average O(1) key lookup
 *   - map for ordered key-value storage
 *   - nested containers
 *   - insertion and update operations
 *   - find(), contains(), erase(), at(), operator[]
 *   - validation and exceptions
 *   - aggregation and grouping
 *   - sorting derived data
 *   - command/dispatch maps
 *   - inventory transactions
 *   - edge cases
 *   - complexity and design trade-offs
 *
 * Compile:
 *   g++ -std=c++17 -O2 dictionary_methods.cpp -o dictionary_methods
 */

using namespace std;


// ============================================================================
// 1. DOMAIN MODEL
// ============================================================================

struct Product {
    string id;
    string name;
    double price;
    int quantity;
};

struct Order {
    string id;
    string customer;
    string category;
    double amount;
    string status;
};


// ============================================================================
// 2. VALIDATION UTILITIES
// ============================================================================

class ValidationError : public runtime_error {
public:
    explicit ValidationError(const string& message)
        : runtime_error(message) {}
};


void requireNonEmpty(const string& value, const string& fieldName) {
    if (value.empty()) {
        throw ValidationError(fieldName + " cannot be empty");
    }
}


void requireNonNegative(double value, const string& fieldName) {
    if (value < 0.0) {
        throw ValidationError(fieldName + " cannot be negative");
    }
}


void requirePositiveInteger(int value, const string& fieldName) {
    if (value <= 0) {
        throw ValidationError(fieldName + " must be positive");
    }
}


// ============================================================================
// 3. INVENTORY SERVICE
// ============================================================================

class InventoryService {
private:
    /*
     * unordered_map is appropriate when the main operation is lookup by a
     * product identifier and sorted iteration is not a requirement.
     *
     * Average complexity:
     *   find: O(1)
     *   insert: O(1)
     *   erase: O(1)
     *
     * Worst-case hash-table operations can degrade to O(n).
     */
    unordered_map<string, Product> products_;

public:
    void addProduct(
        const string& id,
        const string& name,
        double price,
        int quantity
    ) {
        requireNonEmpty(id, "Product ID");
        requireNonEmpty(name, "Product name");
        requireNonNegative(price, "Product price");

        if (quantity < 0) {
            throw ValidationError("Product quantity cannot be negative");
        }

        if (products_.contains(id)) {
            throw ValidationError(
                "Product already exists: " + id
            );
        }

        products_.emplace(
            id,
            Product{id, name, price, quantity}
        );
    }


    /*
     * at() is useful when a missing key should be considered an error.
     * It throws std::out_of_range instead of silently creating a value.
     */
    Product& requireProduct(const string& id) {
        return products_.at(id);
    }


    const Product& requireProduct(const string& id) const {
        return products_.at(id);
    }


    /*
     * operator[] has an important peculiarity:
     *
     *   products_[missingKey]
     *
     * inserts a default-constructed value when the key does not exist.
     *
     * This can be useful for counters, but dangerous when accidental
     * insertion is not intended. find()/contains()/at() are preferable
     * when read-only lookup is intended.
     */
    void demonstrateOperatorSubscript() {
        Product& generated = products_["TEMP"];

        generated.id = "TEMP";
        generated.name = "Temporary Product";
        generated.price = 0.0;
        generated.quantity = 0;

        products_.erase("TEMP");
    }


    void restock(const string& id, int quantity) {
        requirePositiveInteger(quantity, "Restock quantity");

        auto iterator = products_.find(id);

        if (iterator == products_.end()) {
            throw out_of_range(
                "Cannot restock unknown product: " + id
            );
        }

        iterator->second.quantity += quantity;
    }


    double sell(const string& id, int quantity) {
        requirePositiveInteger(quantity, "Sale quantity");

        auto iterator = products_.find(id);

        if (iterator == products_.end()) {
            throw out_of_range(
                "Unknown product: " + id
            );
        }

        Product& product = iterator->second;

        if (product.quantity < quantity) {
            throw runtime_error(
                "Insufficient stock for product: " + id
            );
        }

        product.quantity -= quantity;

        return product.price * quantity;
    }


    optional<Product> getProduct(const string& id) const {
        auto iterator = products_.find(id);

        if (iterator == products_.end()) {
            return nullopt;
        }

        return iterator->second;
    }


    vector<Product> lowStock(int threshold) const {
        if (threshold < 0) {
            throw ValidationError(
                "Low-stock threshold cannot be negative"
            );
        }

        vector<Product> result;

        for (const auto& [id, product] : products_) {
            if (product.quantity <= threshold) {
                result.push_back(product);
            }
        }

        return result;
    }


    double totalInventoryValue() const {
        double total = 0.0;

        for (const auto& [id, product] : products_) {
            total += product.price * product.quantity;
        }

        return total;
    }


    /*
     * Returning a vector rather than exposing the underlying unordered_map
     * keeps the internal data structure private and makes the class easier
     * to change later.
     */
    vector<Product> allProducts() const {
        vector<Product> result;

        result.reserve(products_.size());

        for (const auto& [id, product] : products_) {
            result.push_back(product);
        }

        return result;
    }


    size_t size() const {
        return products_.size();
    }
};


// ============================================================================
// 4. DISPLAY UTILITIES
// ============================================================================

void printProduct(const Product& product) {
    cout
        << left
        << setw(8) << product.id
        << setw(20) << product.name
        << setw(12) << fixed << setprecision(2) << product.price
        << setw(8) << product.quantity
        << '\n';
}


void printProducts(const vector<Product>& products) {
    cout
        << left
        << setw(8) << "ID"
        << setw(20) << "Name"
        << setw(12) << "Price"
        << setw(8) << "Qty"
        << '\n';

    cout << string(48, '-') << '\n';

    for (const Product& product : products) {
        printProduct(product);
    }
}


void printSection(const string& title) {
    cout << "\n" << string(78, '=') << '\n';
    cout << title << '\n';
    cout << string(78, '=') << '\n';
}


// ============================================================================
// 5. MAP FUNDAMENTALS
// ============================================================================

void demonstrateDictionaryStructures() {
    printSection("1. std::map and std::unordered_map");

    /*
     * std::map is an ordered associative container, typically implemented
     * as a balanced tree.
     *
     * Average and worst-case lookup/insert/erase:
     *   O(log n)
     *
     * Iteration occurs in sorted key order.
     */
    map<string, int> orderedScores{
        {"Atul", 92},
        {"Priya", 87},
        {"Ravi", 95},
        {"Neha", 81}
    };

    cout << "std::map iteration:\n";

    for (const auto& [name, score] : orderedScores) {
        cout << "  " << name << ": " << score << '\n';
    }


    /*
     * unordered_map uses hashing and does not provide sorted iteration.
     * Its average key lookup is O(1).
     */
    unordered_map<string, int> fastScores{
        {"Atul", 92},
        {"Priya", 87},
        {"Ravi", 95},
        {"Neha", 81}
    };

    cout << "\nstd::unordered_map lookup:\n";

    auto iterator = fastScores.find("Atul");

    if (iterator != fastScores.end()) {
        cout << "  Atul: " << iterator->second << '\n';
    }

    cout << "\nMap contains Ravi: "
         << (fastScores.contains("Ravi") ? "yes" : "no")
         << '\n';

    cout << "Map contains John: "
         << (fastScores.contains("John") ? "yes" : "no")
         << '\n';
}


// ============================================================================
// 6. COUNTING WITH A DICTIONARY
// ============================================================================

unordered_map<char, int> countCharacters(const string& text) {
    unordered_map<char, int> counts;

    for (char character : text) {
        ++counts[character];
    }

    return counts;
}


void demonstrateCounting() {
    printSection("2. Frequency Counting");

    const string text = "mississippi";

    auto counts = countCharacters(text);

    /*
     * operator[] is particularly convenient for counting:
     *
     * If the key does not exist, counts[character] creates it with the
     * value-initialized integer 0, then ++ increments it.
     */
    for (const auto& [character, count] : counts) {
        cout << "  " << character << ": " << count << '\n';
    }
}


// ============================================================================
// 7. GROUPING
// ============================================================================

unordered_map<string, vector<string>>
groupEmployeesByDepartment(
    const vector<pair<string, string>>& employees
) {
    unordered_map<string, vector<string>> groups;

    for (const auto& [department, employee] : employees) {
        groups[department].push_back(employee);
    }

    return groups;
}


void demonstrateGrouping() {
    printSection("3. Grouping with Nested Dictionary Structures");

    vector<pair<string, string>> employees{
        {"Engineering", "Atul"},
        {"Engineering", "Priya"},
        {"Finance", "Ravi"},
        {"Finance", "Neha"}
    };

    auto groups = groupEmployeesByDepartment(employees);

    for (const auto& [department, names] : groups) {
        cout << department << ":\n";

        for (const string& name : names) {
            cout << "  - " << name << '\n';
        }
    }
}


// ============================================================================
// 8. AGGREGATION
// ============================================================================

unordered_map<string, double>
calculateCategorySales(
    const vector<Order>& orders
) {
    unordered_map<string, double> totals;

    for (const Order& order : orders) {
        if (order.status != "completed") {
            continue;
        }

        totals[order.category] += order.amount;
    }

    return totals;
}


void demonstrateAggregation() {
    printSection("4. Dictionary-Based Aggregation");

    vector<Order> orders{
        {"O1001", "Atul", "Electronics", 75000.0, "completed"},
        {"O1002", "Priya", "Books", 2500.0, "completed"},
        {"O1003", "Ravi", "Electronics", 45000.0, "cancelled"},
        {"O1004", "Neha", "Books", 3500.0, "completed"}
    };

    auto categorySales = calculateCategorySales(orders);

    for (const auto& [category, amount] : categorySales) {
        cout << "  "
             << category
             << ": "
             << fixed
             << setprecision(2)
             << amount
             << '\n';
    }
}


// ============================================================================
// 9. SORTING DICTIONARY-DERIVED DATA
// ============================================================================

vector<pair<string, double>>
sortSalesDescending(
    const unordered_map<string, double>& sales
) {
    vector<pair<string, double>> entries(
        sales.begin(),
        sales.end()
    );

    sort(
        entries.begin(),
        entries.end(),
        [](const auto& left, const auto& right) {
            if (left.second != right.second) {
                return left.second > right.second;
            }

            return left.first < right.first;
        }
    );

    return entries;
}


void demonstrateSorting() {
    printSection("5. Sorting Dictionary Data");

    unordered_map<string, double> sales{
        {"Electronics", 120000.0},
        {"Books", 45000.0},
        {"Furniture", 80000.0}
    };

    auto sortedSales = sortSalesDescending(sales);

    for (const auto& [category, amount] : sortedSales) {
        cout
            << "  "
            << category
            << ": "
            << fixed
            << setprecision(2)
            << amount
            << '\n';
    }

    cout
        << "\nSorting n dictionary entries costs O(n log n), "
        << "because unordered_map itself does not maintain sorted order.\n";
}


// ============================================================================
// 10. DISPATCH TABLE
// ============================================================================

using Operation = function<double(double, double)>;


void demonstrateDispatchTable() {
    printSection("6. Dictionary-Based Function Dispatch");

    unordered_map<string, Operation> operations{
        {"+", [](double a, double b) {
            return a + b;
        }},
        {"-", [](double a, double b) {
            return a - b;
        }},
        {"*", [](double a, double b) {
            return a * b;
        }},
        {"/", [](double a, double b) {
            if (b == 0.0) {
                throw domain_error(
                    "Division by zero"
                );
            }

            return a / b;
        }}
    };

    const vector<string> operators{"+", "-", "*", "/"};

    for (const string& symbol : operators) {
        auto iterator = operations.find(symbol);

        if (iterator == operations.end()) {
            continue;
        }

        cout
            << "  10 "
            << symbol
            << " 5 = "
            << iterator->second(10.0, 5.0)
            << '\n';
    }

    try {
        operations.at("/")(
            10.0,
            0.0
        );
    } catch (const exception& error) {
        cout
            << "  Expected error: "
            << error.what()
            << '\n';
    }
}


// ============================================================================
// 11. INVENTORY CASE STUDY
// ============================================================================

void demonstrateInventory() {
    printSection("7. Complete Inventory Case Study");

    InventoryService inventory;

    inventory.addProduct(
        "P001",
        "Laptop",
        75000.0,
        10
    );

    inventory.addProduct(
        "P002",
        "Keyboard",
        2500.0,
        3
    );

    inventory.addProduct(
        "P003",
        "Monitor",
        18000.0,
        7
    );

    cout
        << "Initial inventory count: "
        << inventory.size()
        << '\n';

    inventory.restock("P002", 4);

    const double saleValue =
        inventory.sell("P001", 2);

    cout
        << "Sale value: "
        << fixed
        << setprecision(2)
        << saleValue
        << '\n';

    auto laptop =
        inventory.getProduct("P001");

    if (laptop.has_value()) {
        cout << "\nLaptop after sale:\n";
        printProduct(*laptop);
    }

    cout << "\nLow-stock products:\n";
    printProducts(inventory.lowStock(5));

    cout
        << "\nTotal inventory value: "
        << inventory.totalInventoryValue()
        << '\n';

    cout << "\nAll products:\n";
    printProducts(inventory.allProducts());
}


// ============================================================================
// 12. FAILURE CONDITIONS
// ============================================================================

void demonstrateFailureConditions() {
    printSection("8. Validation and Failure Conditions");

    InventoryService inventory;

    inventory.addProduct(
        "P001",
        "Laptop",
        75000.0,
        5
    );

    try {
        inventory.addProduct(
            "P001",
            "Duplicate Laptop",
            80000.0,
            1
        );
    } catch (const exception& error) {
        cout
            << "Duplicate product error: "
            << error.what()
            << '\n';
    }


    try {
        inventory.sell(
            "P001",
            100
        );
    } catch (const exception& error) {
        cout
            << "Insufficient stock error: "
            << error.what()
            << '\n';
    }


    try {
        inventory.restock(
            "UNKNOWN",
            5
        );
    } catch (const exception& error) {
        cout
            << "Unknown product error: "
            << error.what()
            << '\n';
    }


    try {
        inventory.sell(
            "P001",
            0
        );
    } catch (const exception& error) {
        cout
            << "Invalid quantity error: "
            << error.what()
            << '\n';
    }
}


// ============================================================================
// 13. MAP VERSUS UNORDERED_MAP
// ============================================================================

void demonstrateContainerTradeoffs() {
    printSection("9. std::map vs std::unordered_map");

    map<int, string> ordered{
        {30, "thirty"},
        {10, "ten"},
        {20, "twenty"}
    };

    unordered_map<int, string> unordered{
        {30, "thirty"},
        {10, "ten"},
        {20, "twenty"}
    };

    cout << "std::map preserves sorted key order:\n";

    for (const auto& [key, value] : ordered) {
        cout << "  " << key << " -> " << value << '\n';
    }

    cout << "\nstd::unordered_map does not promise sorted iteration:\n";

    for (const auto& [key, value] : unordered) {
        cout << "  " << key << " -> " << value << '\n';
    }

    cout << "\nUse std::map when ordered traversal and logarithmic "
         << "lookup are appropriate.\n";

    cout << "Use std::unordered_map when average constant-time key "
         << "lookup is more important than key ordering.\n";
}


// ============================================================================
// 14. NESTED MAPS
// ============================================================================

void demonstrateNestedMaps() {
    printSection("10. Nested Dictionary Structures");

    unordered_map<
        string,
        unordered_map<string, double>
    > departmentMetrics;

    departmentMetrics["Engineering"]["budget"] = 5000000.0;
    departmentMetrics["Engineering"]["employees"] = 40.0;
    departmentMetrics["Finance"]["budget"] = 1800000.0;
    departmentMetrics["Finance"]["employees"] = 12.0;

    for (const auto& [department, metrics] : departmentMetrics) {
        cout << department << ":\n";

        for (const auto& [metric, value] : metrics) {
            cout
                << "  "
                << metric
                << ": "
                << value
                << '\n';
        }
    }
}


// ============================================================================
// 15. OPTIONAL LOOKUP
// ============================================================================

optional<double>
findProductPrice(
    const unordered_map<string, Product>& products,
    const string& id
) {
    auto iterator = products.find(id);

    if (iterator == products.end()) {
        return nullopt;
    }

    return iterator->second.price;
}


void demonstrateOptionalLookup() {
    printSection("11. Non-Throwing Dictionary Lookup");

    unordered_map<string, Product> products;

    products.emplace(
        "P001",
        Product{
            "P001",
            "Laptop",
            75000.0,
            10
        }
    );

    auto existingPrice =
        findProductPrice(products, "P001");

    auto missingPrice =
        findProductPrice(products, "UNKNOWN");

    if (existingPrice.has_value()) {
        cout
            << "P001 price: "
            << *existingPrice
            << '\n';
    }

    if (!missingPrice.has_value()) {
        cout
            << "UNKNOWN product has no price.\n";
    }
}


// ============================================================================
// 16. EDGE CASE: OPERATOR[]
// ============================================================================

void demonstrateOperatorSubscriptSemantics() {
    printSection("12. operator[] and Accidental Insertion");

    unordered_map<string, int> counts;

    cout
        << "Initial size: "
        << counts.size()
        << '\n';

    /*
     * Reading with operator[] changes the dictionary when the key is absent.
     */
    int value = counts["missing"];

    cout
        << "Value returned for missing key: "
        << value
        << '\n';

    cout
        << "Size after operator[] lookup: "
        << counts.size()
        << '\n';

    /*
     * find() performs a lookup without insertion.
     */
    auto iterator = counts.find("another_missing");

    cout
        << "Size after find(): "
        << counts.size()
        << '\n';

    if (iterator == counts.end()) {
        cout
            << "find() correctly reported a missing key.\n";
    }
}


// ============================================================================
// 17. REALISTIC ORDER ANALYTICS
// ============================================================================

struct OrderAnalytics {
    size_t completedOrders = 0;
    double totalRevenue = 0.0;
    unordered_map<string, double> categoryRevenue;
    unordered_map<string, double> customerRevenue;
    optional<Order> largestOrder;
};


OrderAnalytics analyzeOrders(
    const vector<Order>& orders
) {
    OrderAnalytics analytics;

    for (const Order& order : orders) {
        if (order.status != "completed") {
            continue;
        }

        ++analytics.completedOrders;

        analytics.totalRevenue += order.amount;

        analytics.categoryRevenue[order.category]
            += order.amount;

        analytics.customerRevenue[order.customer]
            += order.amount;

        if (
            !analytics.largestOrder.has_value()
            || order.amount >
               analytics.largestOrder->amount
        ) {
            analytics.largestOrder = order;
        }
    }

    return analytics;
}


void demonstrateOrderAnalytics() {
    printSection("13. Industry-Style Order Analytics");

    vector<Order> orders{
        {
            "O1001",
            "Atul",
            "Electronics",
            75000.0,
            "completed"
        },
        {
            "O1002",
            "Priya",
            "Books",
            2500.0,
            "completed"
        },
        {
            "O1003",
            "Ravi",
            "Electronics",
            45000.0,
            "cancelled"
        },
        {
            "O1004",
            "Neha",
            "Books",
            3500.0,
            "completed"
        },
        {
            "O1005",
            "Atul",
            "Electronics",
            25000.0,
            "completed"
        }
    };

    OrderAnalytics analytics =
        analyzeOrders(orders);

    cout
        << "Completed orders: "
        << analytics.completedOrders
        << '\n';

    cout
        << "Total revenue: "
        << fixed
        << setprecision(2)
        << analytics.totalRevenue
        << '\n';

    cout << "\nRevenue by category:\n";

    for (const auto& [category, revenue] :
         analytics.categoryRevenue) {
        cout
            << "  "
            << category
            << ": "
            << revenue
            << '\n';
    }

    cout << "\nRevenue by customer:\n";

    for (const auto& [customer, revenue] :
         analytics.customerRevenue) {
        cout
            << "  "
            << customer
            << ": "
            << revenue
            << '\n';
    }

    if (analytics.largestOrder.has_value()) {
        cout
            << "\nLargest completed order: "
            << analytics.largestOrder->id
            << " for "
            << analytics.largestOrder->amount
            << '\n';
    }
}


// ============================================================================
// 18. PERFORMANCE AND HASHING
// ============================================================================

void demonstrateHashTableProperties() {
    printSection("14. Hash Table Properties");

    unordered_map<string, int> data;

    data.reserve(10000);

    for (int index = 0; index < 10000; ++index) {
        data.emplace(
            "key_" + to_string(index),
            index
        );
    }

    cout
        << "Element count: "
        << data.size()
        << '\n';

    cout
        << "Bucket count: "
        << data.bucket_count()
        << '\n';

    cout
        << "Load factor: "
        << data.load_factor()
        << '\n';

    cout
        << "Maximum load factor: "
        << data.max_load_factor()
        << '\n';

    /*
     * reserve() asks the implementation to allocate enough buckets for
     * approximately the requested number of elements, reducing repeated
     * rehashing when the expected size is known.
     */
}


// ============================================================================
// 19. SECURITY AND ROBUSTNESS
// ============================================================================

void demonstrateSecurityConsiderations() {
    printSection("15. Security and Robustness Considerations");

    /*
     * Dictionary-like containers are often populated from external input.
     * Never assume a key exists simply because normal input contains it.
     *
     * Validate:
     *   - key presence
     *   - value type/format
     *   - numeric ranges
     *   - authorization-sensitive fields
     *   - resource limits
     */

    unordered_map<string, string> externalInput{
        {"username", "atul"},
        {"role", "user"},
        {"debug", "true"}
    };

    const vector<string> allowedFields{
        "username",
        "role"
    };

    unordered_map<string, string> safeInput;

    for (const string& field : allowedFields) {
        auto iterator = externalInput.find(field);

        if (iterator != externalInput.end()) {
            safeInput.emplace(
                iterator->first,
                iterator->second
            );
        }
    }

    cout << "Allowlisted external fields:\n";

    for (const auto& [key, value] : safeInput) {
        cout
            << "  "
            << key
            << ": "
            << value
            << '\n';
    }

    /*
     * Sensitive values such as passwords, access tokens, and private keys
     * should not be written to ordinary application logs.
     */
}


// ============================================================================
// 20. TESTING
// ============================================================================

void runAssertions() {
    printSection("16. Behavioral Tests");

    InventoryService inventory;

    inventory.addProduct(
        "TEST",
        "Test Product",
        100.0,
        10
    );

    const double revenue =
        inventory.sell("TEST", 3);

    if (revenue != 300.0) {
        throw runtime_error(
            "Test failed: incorrect revenue"
        );
    }

    auto product =
        inventory.getProduct("TEST");

    if (!product.has_value()) {
        throw runtime_error(
            "Test failed: product missing"
        );
    }

    if (product->quantity != 7) {
        throw runtime_error(
            "Test failed: incorrect remaining quantity"
        );
    }

    if (!inventory.getProduct("MISSING").has_value()) {
        cout
            << "Missing-product lookup test passed.\n";
    }

    try {
        inventory.sell("TEST", 100);
        throw runtime_error(
            "Test failed: insufficient stock was accepted"
        );
    } catch (const runtime_error&) {
        cout
            << "Insufficient-stock test passed.\n";
    }

    cout
        << "All core inventory assertions passed.\n";
}


// ============================================================================
// 21. MAIN PROGRAM
// ============================================================================

int main() {
    try {
        demonstrateDictionaryStructures();
        demonstrateCounting();
        demonstrateGrouping();
        demonstrateAggregation();
        demonstrateSorting();
        demonstrateDispatchTable();
        demonstrateInventory();
        demonstrateFailureConditions();
        demonstrateContainerTradeoffs();
        demonstrateNestedMaps();
        demonstrateOptionalLookup();
        demonstrateOperatorSubscriptSemantics();
        demonstrateOrderAnalytics();
        demonstrateHashTableProperties();
        demonstrateSecurityConsiderations();
        runAssertions();

        printSection("17. Case Study Reference");

        cout
            << "Key concepts demonstrated:\n"
            << "  - std::map\n"
            << "  - std::unordered_map\n"
            << "  - find()\n"
            << "  - contains()\n"
            << "  - at()\n"
            << "  - operator[]\n"
            << "  - emplace()\n"
            << "  - erase()\n"
            << "  - nested associative structures\n"
            << "  - counting and aggregation\n"
            << "  - grouping\n"
            << "  - dispatch tables\n"
            << "  - validation\n"
            << "  - exception handling\n"
            << "  - optional lookup results\n"
            << "  - sorting derived data\n"
            << "  - hash-table capacity management\n"
            << "  - security-oriented input handling\n"
            << "  - behavioral testing\n";

        cout
            << "\nThe central design decision is not merely how to store "
            << "key-value pairs, but which associative container and "
            << "access operation best match the application's semantics.\n";

        return 0;
    }
    catch (const exception& error) {
        cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
