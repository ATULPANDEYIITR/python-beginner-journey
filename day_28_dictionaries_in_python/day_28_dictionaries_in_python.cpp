/*
 * DICTIONARIES IN C++: TECHNICAL CASE STUDY
 * ==========================================
 *
 * Scenario:
 * Build an in-memory inventory and order-management service using
 * std::unordered_map and related C++ standard-library containers.
 *
 * The case study demonstrates how dictionary-like data structures are used
 * in an industry-style application for:
 *
 * - Product lookup
 * - Customer lookup
 * - Inventory management
 * - Order processing
 * - Validation
 * - Aggregation
 * - Authorization
 * - Caching
 * - Graph representation
 * - Error handling
 * - Performance measurement
 * - Deterministic reporting
 *
 * Compile:
 *     g++ -std=c++17 -O2 dictionaries.cpp -o dictionaries
 *
 * Run:
 *     ./dictionaries
 */

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <queue>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;


// ============================================================================
// 1. BASIC DICTIONARY-LIKE STRUCTURES
// ============================================================================

void demonstrateBasicUnorderedMap() {
    cout << "\n=== 1. BASIC std::unordered_map ===\n";

    unordered_map<string, int> inventory{
        {"Laptop", 5},
        {"Keyboard", 12},
        {"Mouse", 20}
    };

    cout << "Laptop stock: " << inventory.at("Laptop") << '\n';

    // operator[] inserts a missing key with a default-constructed value.
    inventory["Monitor"] = 7;

    // Updating an existing key replaces its value.
    inventory["Laptop"] = 4;

    for (const auto& [product, quantity] : inventory) {
        cout << product << " -> " << quantity << '\n';
    }

    cout << "Number of products: " << inventory.size() << '\n';
}


// ============================================================================
// 2. FIND VS AT VS OPERATOR[]
// ============================================================================

void demonstrateLookupSemantics() {
    cout << "\n=== 2. LOOKUP SEMANTICS ===\n";

    unordered_map<string, int> stock{
        {"Laptop", 5}
    };

    auto iterator = stock.find("Keyboard");

    if (iterator == stock.end()) {
        cout << "Keyboard does not exist.\n";
    }

    try {
        cout << stock.at("Keyboard") << '\n';
    } catch (const out_of_range& error) {
        cout << "at() error: " << error.what() << '\n';
    }

    // operator[] would create "Keyboard" with value 0.
    cout << "Before [] size: " << stock.size() << '\n';
    int quantity = stock["Keyboard"];
    cout << "Created default value: " << quantity << '\n';
    cout << "After [] size: " << stock.size() << '\n';
}


// ============================================================================
// 3. DATA MODEL
// ============================================================================

struct Product {
    int id;
    string name;
    string category;
    double price;
    int stock;
    int reorderLevel;
};

struct Customer {
    int id;
    string name;
    string email;
    string role;
};

struct OrderLine {
    int productId;
    int quantity;
};

struct Order {
    int id;
    int customerId;
    vector<OrderLine> lines;
};


// ============================================================================
// 4. DOMAIN-SPECIFIC EXCEPTIONS
// ============================================================================

class InventoryError : public runtime_error {
public:
    explicit InventoryError(const string& message)
        : runtime_error(message) {}
};

class ValidationError : public runtime_error {
public:
    explicit ValidationError(const string& message)
        : runtime_error(message) {}
};

class AuthorizationError : public runtime_error {
public:
    explicit AuthorizationError(const string& message)
        : runtime_error(message) {}
};


// ============================================================================
// 5. INVENTORY SERVICE
// ============================================================================

class InventoryService {
private:
    unordered_map<int, Product> products;

public:
    void addProduct(Product product) {
        if (product.id <= 0) {
            throw ValidationError("Product ID must be positive.");
        }

        if (product.name.empty()) {
            throw ValidationError("Product name cannot be empty.");
        }

        if (product.price < 0.0) {
            throw ValidationError("Product price cannot be negative.");
        }

        if (product.stock < 0) {
            throw ValidationError("Product stock cannot be negative.");
        }

        if (products.contains(product.id)) {
            throw ValidationError(
                "Product ID already exists: " + to_string(product.id)
            );
        }

        products.emplace(product.id, move(product));
    }

    const Product& getProduct(int productId) const {
        auto iterator = products.find(productId);

        if (iterator == products.end()) {
            throw InventoryError(
                "Product not found: " + to_string(productId)
            );
        }

        return iterator->second;
    }

    Product& getProductMutable(int productId) {
        auto iterator = products.find(productId);

        if (iterator == products.end()) {
            throw InventoryError(
                "Product not found: " + to_string(productId)
            );
        }

        return iterator->second;
    }

    void increaseStock(int productId, int quantity) {
        if (quantity <= 0) {
            throw ValidationError("Increase quantity must be positive.");
        }

        Product& product = getProductMutable(productId);

        if (product.stock > numeric_limits<int>::max() - quantity) {
            throw InventoryError("Stock integer overflow.");
        }

        product.stock += quantity;
    }

    void decreaseStock(int productId, int quantity) {
        if (quantity <= 0) {
            throw ValidationError("Decrease quantity must be positive.");
        }

        Product& product = getProductMutable(productId);

        if (quantity > product.stock) {
            throw InventoryError(
                "Insufficient stock for product: " +
                to_string(productId)
            );
        }

        product.stock -= quantity;
    }

    vector<Product> lowStockProducts() const {
        vector<Product> result;

        for (const auto& [id, product] : products) {
            if (product.stock <= product.reorderLevel) {
                result.push_back(product);
            }
        }

        sort(
            result.begin(),
            result.end(),
            [](const Product& a, const Product& b) {
                return a.id < b.id;
            }
        );

        return result;
    }

    vector<Product> allProductsSorted() const {
        vector<Product> result;

        for (const auto& [id, product] : products) {
            result.push_back(product);
        }

        sort(
            result.begin(),
            result.end(),
            [](const Product& a, const Product& b) {
                return a.id < b.id;
            }
        );

        return result;
    }

    size_t size() const {
        return products.size();
    }
};


// ============================================================================
// 6. CUSTOMER SERVICE
// ============================================================================

class CustomerService {
private:
    unordered_map<int, Customer> customers;

public:
    void addCustomer(Customer customer) {
        if (customer.id <= 0) {
            throw ValidationError("Customer ID must be positive.");
        }

        if (customer.name.empty()) {
            throw ValidationError("Customer name cannot be empty.");
        }

        if (customer.email.find('@') == string::npos) {
            throw ValidationError("Customer email is invalid.");
        }

        if (customers.contains(customer.id)) {
            throw ValidationError(
                "Customer already exists: " +
                to_string(customer.id)
            );
        }

        customers.emplace(customer.id, move(customer));
    }

    const Customer& getCustomer(int customerId) const {
        auto iterator = customers.find(customerId);

        if (iterator == customers.end()) {
            throw ValidationError(
                "Customer not found: " +
                to_string(customerId)
            );
        }

        return iterator->second;
    }
};


// ============================================================================
// 7. ROLE-BASED ACCESS CONTROL
// ============================================================================

class AccessControl {
private:
    unordered_map<string, unordered_set<string>> permissions;

public:
    AccessControl() {
        permissions["admin"] = {
            "inventory.read",
            "inventory.write",
            "orders.create",
            "orders.cancel",
            "reports.read"
        };

        permissions["operator"] = {
            "inventory.read",
            "inventory.write",
            "orders.create",
            "reports.read"
        };

        permissions["viewer"] = {
            "inventory.read",
            "reports.read"
        };
    }

    bool authorized(
        const string& role,
        const string& permission
    ) const {
        auto roleIterator = permissions.find(role);

        if (roleIterator == permissions.end()) {
            return false;
        }

        return roleIterator->second.contains(permission);
    }

    void require(
        const Customer& customer,
        const string& permission
    ) const {
        if (!authorized(customer.role, permission)) {
            throw AuthorizationError(
                "Role '" + customer.role +
                "' lacks permission '" + permission + "'."
            );
        }
    }
};


// ============================================================================
// 8. ORDER SERVICE
// ============================================================================

class OrderService {
private:
    unordered_map<int, Order> orders;
    int nextOrderId = 1;

public:
    int createOrder(
        const Customer& customer,
        const vector<OrderLine>& lines,
        InventoryService& inventory,
        const AccessControl& accessControl
    ) {
        accessControl.require(customer, "orders.create");

        if (lines.empty()) {
            throw ValidationError("An order must contain at least one line.");
        }

        // Validate every line before modifying inventory.
        // This prevents a partially applied order when a later line fails.
        unordered_set<int> seenProducts;

        for (const OrderLine& line : lines) {
            if (line.quantity <= 0) {
                throw ValidationError(
                    "Order quantity must be positive."
                );
            }

            if (!seenProducts.insert(line.productId).second) {
                throw ValidationError(
                    "Duplicate product in one order: " +
                    to_string(line.productId)
                );
            }

            const Product& product = inventory.getProduct(line.productId);

            if (product.stock < line.quantity) {
                throw InventoryError(
                    "Insufficient stock for " + product.name
                );
            }
        }

        // All validation has succeeded, so inventory changes can begin.
        for (const OrderLine& line : lines) {
            inventory.decreaseStock(
                line.productId,
                line.quantity
            );
        }

        const int orderId = nextOrderId++;

        orders.emplace(
            orderId,
            Order{
                orderId,
                customer.id,
                lines
            }
        );

        return orderId;
    }

    const Order& getOrder(int orderId) const {
        auto iterator = orders.find(orderId);

        if (iterator == orders.end()) {
            throw ValidationError(
                "Order not found: " + to_string(orderId)
            );
        }

        return iterator->second;
    }

    size_t size() const {
        return orders.size();
    }
};


// ============================================================================
// 9. SALES AGGREGATION
// ============================================================================

struct SalesStatistics {
    unordered_map<int, double> revenueByProduct;
    unordered_map<string, double> revenueByCategory;
    unordered_map<int, int> quantityByProduct;
    double totalRevenue = 0.0;
};

SalesStatistics calculateSales(
    const vector<Order>& completedOrders,
    const InventoryService& inventory
) {
    SalesStatistics statistics;

    for (const Order& order : completedOrders) {
        for (const OrderLine& line : order.lines) {
            const Product& product =
                inventory.getProduct(line.productId);

            const double revenue =
                product.price * line.quantity;

            statistics.totalRevenue += revenue;

            statistics.revenueByProduct[product.id] += revenue;
            statistics.revenueByCategory[product.category] += revenue;
            statistics.quantityByProduct[product.id] += line.quantity;
        }
    }

    return statistics;
}


// ============================================================================
// 10. REPORTING
// ============================================================================

void printInventoryReport(
    const InventoryService& inventory
) {
    cout << "\n=== INVENTORY REPORT ===\n";

    for (const Product& product : inventory.allProductsSorted()) {
        cout
            << product.id << " | "
            << product.name << " | "
            << product.category << " | price="
            << fixed << setprecision(2)
            << product.price << " | stock="
            << product.stock << '\n';
    }
}

void printLowStockReport(
    const InventoryService& inventory
) {
    cout << "\n=== LOW STOCK REPORT ===\n";

    const auto products = inventory.lowStockProducts();

    if (products.empty()) {
        cout << "No products require replenishment.\n";
        return;
    }

    for (const Product& product : products) {
        cout
            << product.name
            << " stock=" << product.stock
            << " reorder-level=" << product.reorderLevel
            << '\n';
    }
}


// ============================================================================
// 11. DICTIONARY-BASED CACHE
// ============================================================================

class ProductCache {
private:
    unordered_map<int, Product> cache;

public:
    void put(const Product& product) {
        cache[product.id] = product;
    }

    optional<Product> get(int productId) const {
        auto iterator = cache.find(productId);

        if (iterator == cache.end()) {
            return nullopt;
        }

        return iterator->second;
    }

    void remove(int productId) {
        cache.erase(productId);
    }

    size_t size() const {
        return cache.size();
    }
};


// ============================================================================
// 12. GRAPH CASE STUDY
// ============================================================================

class NetworkGraph {
private:
    // An adjacency list is naturally represented as:
    // node -> (neighbor -> edge weight).
    unordered_map<string, unordered_map<string, int>> edges;

public:
    void addEdge(
        const string& from,
        const string& to,
        int weight
    ) {
        if (weight < 0) {
            throw ValidationError(
                "Dijkstra's algorithm requires non-negative weights."
            );
        }

        edges[from][to] = weight;

        // Ensure the destination appears even when it has no outgoing edge.
        if (!edges.contains(to)) {
            edges[to] = {};
        }
    }

    unordered_map<string, int> shortestPaths(
        const string& source
    ) const {
        if (!edges.contains(source)) {
            throw ValidationError("Unknown graph source.");
        }

        unordered_map<string, int> distance;

        for (const auto& [node, neighbors] : edges) {
            distance[node] = numeric_limits<int>::max();
        }

        distance[source] = 0;

        using QueueEntry = pair<int, string>;

        priority_queue<
            QueueEntry,
            vector<QueueEntry>,
            greater<QueueEntry>
        > queue;

        queue.push({0, source});

        while (!queue.empty()) {
            auto [currentDistance, current] = queue.top();
            queue.pop();

            if (currentDistance != distance[current]) {
                continue;
            }

            for (const auto& [neighbor, weight] : edges.at(current)) {
                if (
                    currentDistance >
                    numeric_limits<int>::max() - weight
                ) {
                    continue;
                }

                const int candidate =
                    currentDistance + weight;

                if (candidate < distance[neighbor]) {
                    distance[neighbor] = candidate;
                    queue.push({candidate, neighbor});
                }
            }
        }

        return distance;
    }
};


// ============================================================================
// 13. DICTIONARY-BASED DISPATCH
// ============================================================================

using Operation = function<double(double, double)>;

class Calculator {
private:
    unordered_map<string, Operation> operations;

public:
    Calculator() {
        operations["add"] = [](double a, double b) {
            return a + b;
        };

        operations["subtract"] = [](double a, double b) {
            return a - b;
        };

        operations["multiply"] = [](double a, double b) {
            return a * b;
        };

        operations["divide"] = [](double a, double b) {
            if (b == 0.0) {
                throw domain_error("Division by zero.");
            }

            return a / b;
        };
    }

    double execute(
        const string& operation,
        double a,
        double b
    ) const {
        auto iterator = operations.find(operation);

        if (iterator == operations.end()) {
            throw ValidationError(
                "Unknown operation: " + operation
            );
        }

        return iterator->second(a, b);
    }
};


// ============================================================================
// 14. PERFORMANCE BENCHMARK
// ============================================================================

void benchmarkLookup() {
    cout << "\n=== PERFORMANCE BENCHMARK ===\n";

    constexpr int elementCount = 500000;
    constexpr int repetitions = 500000;

    unordered_map<int, int> values;
    values.reserve(elementCount);

    for (int i = 0; i < elementCount; ++i) {
        values.emplace(i, i * 2);
    }

    volatile long long checksum = 0;

    const auto start = chrono::steady_clock::now();

    for (int i = 0; i < repetitions; ++i) {
        auto iterator = values.find(i % elementCount);

        if (iterator != values.end()) {
            checksum += iterator->second;
        }
    }

    const auto finish = chrono::steady_clock::now();

    const double milliseconds =
        chrono::duration<double, milli>(
            finish - start
        ).count();

    cout
        << "Elements: "
        << elementCount
        << '\n';

    cout
        << "Lookups: "
        << repetitions
        << '\n';

    cout
        << "Elapsed milliseconds: "
        << milliseconds
        << '\n';

    cout
        << "Checksum: "
        << checksum
        << '\n';

    cout
        << "Expected average-case unordered_map lookup: O(1).\n";

    cout
        << "Worst-case theoretical lookup can degrade toward O(n), "
        << "so hashing quality and implementation details matter.\n";
}


// ============================================================================
// 15. HASH TABLE CAPACITY
// ============================================================================

void demonstrateHashTableCapacity() {
    cout << "\n=== HASH TABLE CAPACITY ===\n";

    unordered_map<int, string> table;

    table.reserve(1000);

    cout << "Bucket count after reserve: "
         << table.bucket_count()
         << '\n';

    cout << "Load factor: "
         << table.load_factor()
         << '\n';

    cout << "Maximum load factor: "
         << table.max_load_factor()
         << '\n';

    // Lowering max_load_factor can reduce average collision pressure at
    // the cost of additional memory.
    table.max_load_factor(0.5f);

    cout << "Changed maximum load factor: "
         << table.max_load_factor()
         << '\n';
}


// ============================================================================
// 16. CUSTOM HASH FOR A COMPOSITE KEY
// ============================================================================

struct Coordinate {
    int x;
    int y;

    bool operator==(const Coordinate& other) const {
        return x == other.x && y == other.y;
    }
};

struct CoordinateHash {
    size_t operator()(const Coordinate& coordinate) const noexcept {
        const size_t first =
            hash<int>{}(coordinate.x);

        const size_t second =
            hash<int>{}(coordinate.y);

        // A common hash-combination technique.
        return first ^ (
            second +
            static_cast<size_t>(0x9e3779b9) +
            (first << 6) +
            (first >> 2)
        );
    }
};

void demonstrateCustomHash() {
    cout << "\n=== CUSTOM HASH ===\n";

    unordered_map<
        Coordinate,
        string,
        CoordinateHash
    > locations;

    locations[{10, 20}] = "Warehouse";
    locations[{30, 40}] = "Office";

    Coordinate query{10, 20};

    cout << "Coordinate lookup: "
         << locations.at(query)
         << '\n';
}


// ============================================================================
// 17. TRANSACTION VALIDATION
// ============================================================================

bool validateOrder(
    const Order& order,
    const InventoryService& inventory
) {
    if (order.id <= 0 || order.customerId <= 0) {
        return false;
    }

    if (order.lines.empty()) {
        return false;
    }

    unordered_set<int> seen;

    for (const OrderLine& line : order.lines) {
        if (line.quantity <= 0) {
            return false;
        }

        if (!seen.insert(line.productId).second) {
            return false;
        }

        try {
            const Product& product =
                inventory.getProduct(line.productId);

            if (line.quantity > product.stock) {
                return false;
            }
        } catch (const InventoryError&) {
            return false;
        }
    }

    return true;
}


// ============================================================================
// 18. MAIN INDUSTRY CASE STUDY
// ============================================================================

void runCaseStudy() {
    cout << "\n=== INDUSTRY CASE STUDY ===\n";

    InventoryService inventory;
    CustomerService customers;
    AccessControl accessControl;
    OrderService orders;

    inventory.addProduct({
        101,
        "Laptop",
        "Electronics",
        75000.0,
        10,
        3
    });

    inventory.addProduct({
        102,
        "Mouse",
        "Electronics",
        1200.0,
        25,
        5
    });

    inventory.addProduct({
        103,
        "Office Chair",
        "Furniture",
        8000.0,
        4,
        5
    });

    inventory.addProduct({
        104,
        "Keyboard",
        "Electronics",
        2500.0,
        15,
        4
    });

    customers.addCustomer({
        1,
        "Alice",
        "alice@example.com",
        "operator"
    });

    customers.addCustomer({
        2,
        "Bob",
        "bob@example.com",
        "viewer"
    });

    const Customer& alice = customers.getCustomer(1);
    const Customer& bob = customers.getCustomer(2);

    cout << "Customer Alice role: "
         << alice.role
         << '\n';

    cout << "Customer Bob role: "
         << bob.role
         << '\n';

    cout << "Alice can create orders: "
         << boolalpha
         << accessControl.authorized(
                alice.role,
                "orders.create"
            )
         << '\n';

    cout << "Bob can create orders: "
         << boolalpha
         << accessControl.authorized(
                bob.role,
                "orders.create"
            )
         << '\n';

    try {
        const int orderId = orders.createOrder(
            alice,
            {
                {101, 1},
                {102, 2}
            },
            inventory,
            accessControl
        );

        cout << "Created order: "
             << orderId
             << '\n';

        const Order& order = orders.getOrder(orderId);

        cout << "Order belongs to customer: "
             << order.customerId
             << '\n';

        cout << "Order is structurally valid: "
             << validateOrder(order, inventory)
             << '\n';

    } catch (const exception& error) {
        cout << "Order creation failed: "
             << error.what()
             << '\n';
    }

    try {
        orders.createOrder(
            bob,
            {
                {104, 1}
            },
            inventory,
            accessControl
        );
    } catch (const exception& error) {
        cout << "Expected authorization failure: "
             << error.what()
             << '\n';
    }

    printInventoryReport(inventory);
    printLowStockReport(inventory);

    // Demonstrate caching.
    ProductCache cache;

    for (const Product& product : inventory.allProductsSorted()) {
        cache.put(product);
    }

    cout << "\nCache size: "
         << cache.size()
         << '\n';

    auto cachedProduct = cache.get(101);

    if (cachedProduct.has_value()) {
        cout << "Cached product: "
             << cachedProduct->name
             << '\n';
    }

    // Reconstruct completed orders for analytics.
    vector<Order> completedOrders;

    if (orders.size() > 0) {
        completedOrders.push_back(
            orders.getOrder(1)
        );
    }

    SalesStatistics statistics =
        calculateSales(completedOrders, inventory);

    cout << "\n=== SALES REPORT ===\n";

    cout
        << "Total revenue: INR "
        << fixed
        << setprecision(2)
        << statistics.totalRevenue
        << '\n';

    cout << "Revenue by category:\n";

    vector<pair<string, double>> categories(
        statistics.revenueByCategory.begin(),
        statistics.revenueByCategory.end()
    );

    sort(
        categories.begin(),
        categories.end(),
        [](const auto& left, const auto& right) {
            return left.first < right.first;
        }
    );

    for (const auto& [category, revenue] : categories) {
        cout
            << category
            << " -> INR "
            << revenue
            << '\n';
    }
}


// ============================================================================
// 19. GRAPH CASE STUDY EXECUTION
// ============================================================================

void runGraphCaseStudy() {
    cout << "\n=== NETWORK GRAPH CASE STUDY ===\n";

    NetworkGraph network;

    network.addEdge("Warehouse", "Hub", 4);
    network.addEdge("Warehouse", "Airport", 2);
    network.addEdge("Airport", "Hub", 1);
    network.addEdge("Hub", "Store", 5);
    network.addEdge("Airport", "Store", 8);
    network.addEdge("Store", "Customer", 2);

    const auto distances =
        network.shortestPaths("Warehouse");

    vector<pair<string, int>> sortedDistances(
        distances.begin(),
        distances.end()
    );

    sort(
        sortedDistances.begin(),
        sortedDistances.end()
    );

    for (const auto& [node, distance] : sortedDistances) {
        cout << node << " -> ";

        if (distance == numeric_limits<int>::max()) {
            cout << "unreachable";
        } else {
            cout << distance;
        }

        cout << '\n';
    }
}


// ============================================================================
// 20. DISPATCH TABLE EXECUTION
// ============================================================================

void runCalculatorCaseStudy() {
    cout << "\n=== DISPATCH TABLE ===\n";

    Calculator calculator;

    cout << "10 + 5 = "
         << calculator.execute("add", 10, 5)
         << '\n';

    cout << "10 * 5 = "
         << calculator.execute("multiply", 10, 5)
         << '\n';

    try {
        calculator.execute("divide", 10, 0);
    } catch (const exception& error) {
        cout << "Expected calculator error: "
             << error.what()
             << '\n';
    }
}


// ============================================================================
// 21. FAILURE CONDITIONS
// ============================================================================

void demonstrateFailureConditions() {
    cout << "\n=== FAILURE CONDITIONS ===\n";

    InventoryService inventory;

    try {
        inventory.addProduct({
            -1,
            "Invalid",
            "Test",
            100.0,
            5,
            1
        });
    } catch (const ValidationError& error) {
        cout << "Invalid product rejected: "
             << error.what()
             << '\n';
    }

    inventory.addProduct({
        1,
        "Valid Product",
        "Test",
        100.0,
        1,
        1
    });

    try {
        inventory.decreaseStock(1, 2);
    } catch (const InventoryError& error) {
        cout << "Overselling rejected: "
             << error.what()
             << '\n';
    }

    try {
        inventory.getProduct(999);
    } catch (const InventoryError& error) {
        cout << "Missing product handled: "
             << error.what()
             << '\n';
    }
}


// ============================================================================
// 22. COMPLEXITY DISCUSSION
// ============================================================================

void printComplexityDiscussion() {
    cout << "\n=== COMPLEXITY ===\n";

    cout << "unordered_map find/insert/erase: "
         << "O(1) average, O(n) worst-case.\n";

    cout << "map find/insert/erase: "
         << "O(log n), because std::map is tree-based.\n";

    cout << "unordered_set membership: "
         << "O(1) average, O(n) worst-case.\n";

    cout << "vector linear search: "
         << "O(n).\n";

    cout << "Dijkstra with priority_queue and adjacency list: "
         << "approximately O((V + E) log V).\n";

    cout << "Sorting an unordered_map-derived report: "
         << "O(n log n).\n";
}


// ============================================================================
// 23. MAIN
// ============================================================================

int main() {
    try {
        cout << "DICTIONARIES / KEY-VALUE DATA STRUCTURES IN C++\n";
        cout << "================================================\n";

        demonstrateBasicUnorderedMap();
        demonstrateLookupSemantics();
        demonstrateHashTableCapacity();
        demonstrateCustomHash();

        runCaseStudy();
        runGraphCaseStudy();
        runCalculatorCaseStudy();
        demonstrateFailureConditions();
        benchmarkLookup();
        printComplexityDiscussion();

        cout << "\n=== PROGRAM COMPLETED SUCCESSFULLY ===\n";

        return 0;

    } catch (const exception& error) {
        cerr << "\nUnhandled error: "
             << error.what()
             << '\n';

        return 1;
    }
}
