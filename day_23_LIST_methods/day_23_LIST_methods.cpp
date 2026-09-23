/*
    LIST-LIKE DATA STRUCTURES
    ==========================

    C++ does not have Python's built-in list type or the exact same list
    methods. The closest general-purpose sequence container is std::vector.

    This program presents a realistic inventory-management case study while
    demonstrating concepts corresponding to common list operations:

        append()  -> vector::push_back()
        extend()  -> insert() with a range
        insert()  -> vector::insert()
        remove()  -> erase()
        pop()     -> pop_back()
        clear()   -> clear()
        index()   -> find / iterator distance
        count()   -> count / count_if
        sort()    -> std::sort()
        reverse() -> std::reverse()
        copy()    -> vector copy construction / assignment

    The implementation progresses from basic vector operations to a complete
    inventory system with:

        - Product records
        - Input validation
        - Inventory insertion and deletion
        - Searching
        - Filtering
        - Sorting
        - Aggregation
        - Stock updates
        - Transaction processing
        - Error handling
        - Reporting
        - Complexity considerations

    Compile with:

        g++ -std=c++17 -O2 main.cpp -o list_case_study

    The program uses only the C++ standard library.
*/

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;


// ---------------------------------------------------------------------------
// Utility functions
// ---------------------------------------------------------------------------

void section(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

template <typename T>
void printVector(const vector<T>& values, const string& label) {
    cout << label << ": [";

    for (size_t i = 0; i < values.size(); ++i) {
        cout << values[i];

        if (i + 1 < values.size()) {
            cout << ", ";
        }
    }

    cout << "]\n";
}


// ---------------------------------------------------------------------------
// Product model
// ---------------------------------------------------------------------------

struct Product {
    string sku;
    string name;
    string category;
    double price;
    int stock;
};


// ---------------------------------------------------------------------------
// Inventory class
// ---------------------------------------------------------------------------

class Inventory {
private:
    vector<Product> products;

    static bool validPrice(double price) {
        return price >= 0.0 && price <= 1'000'000.0;
    }

    static bool validStock(int stock) {
        return stock >= 0 && stock <= 1'000'000;
    }

public:
    // Add one product.
    void addProduct(const Product& product) {
        if (product.sku.empty()) {
            throw invalid_argument("SKU cannot be empty.");
        }

        if (product.name.empty()) {
            throw invalid_argument("Product name cannot be empty.");
        }

        if (!validPrice(product.price)) {
            throw invalid_argument("Product price is outside the valid range.");
        }

        if (!validStock(product.stock)) {
            throw invalid_argument("Product stock is outside the valid range.");
        }

        if (findBySku(product.sku).has_value()) {
            throw invalid_argument("A product with this SKU already exists.");
        }

        products.push_back(product);
    }

    // Insert at a specific position.
    void insertProduct(size_t position, const Product& product) {
        if (position > products.size()) {
            throw out_of_range("Insertion position is outside the vector.");
        }

        if (findBySku(product.sku).has_value()) {
            throw invalid_argument("A product with this SKU already exists.");
        }

        products.insert(products.begin() + static_cast<ptrdiff_t>(position), product);
    }

    // Find a product by SKU.
    optional<Product> findBySku(const string& sku) const {
        auto iterator = find_if(
            products.begin(),
            products.end(),
            [&](const Product& product) {
                return product.sku == sku;
            }
        );

        if (iterator == products.end()) {
            return nullopt;
        }

        return *iterator;
    }

    // Return the index of a product.
    optional<size_t> indexOf(const string& sku) const {
        auto iterator = find_if(
            products.begin(),
            products.end(),
            [&](const Product& product) {
                return product.sku == sku;
            }
        );

        if (iterator == products.end()) {
            return nullopt;
        }

        return static_cast<size_t>(
            distance(products.begin(), iterator)
        );
    }

    // Remove by SKU.
    bool removeBySku(const string& sku) {
        auto iterator = find_if(
            products.begin(),
            products.end(),
            [&](const Product& product) {
                return product.sku == sku;
            }
        );

        if (iterator == products.end()) {
            return false;
        }

        products.erase(iterator);
        return true;
    }

    // Remove and return the last product.
    optional<Product> popBack() {
        if (products.empty()) {
            return nullopt;
        }

        Product product = products.back();
        products.pop_back();
        return product;
    }

    // Remove everything.
    void clear() {
        products.clear();
    }

    // Extend the vector using another vector.
    void extend(const vector<Product>& additionalProducts) {
        for (const auto& product : additionalProducts) {
            addProduct(product);
        }
    }

    // Update stock safely.
    bool updateStock(const string& sku, int change) {
        auto iterator = find_if(
            products.begin(),
            products.end(),
            [&](Product& product) {
                return product.sku == sku;
            }
        );

        if (iterator == products.end()) {
            return false;
        }

        long long newStock =
            static_cast<long long>(iterator->stock) + change;

        if (newStock < 0 || newStock > 1'000'000) {
            return false;
        }

        iterator->stock = static_cast<int>(newStock);
        return true;
    }

    // Return all low-stock products.
    vector<Product> lowStock(int threshold) const {
        vector<Product> result;

        copy_if(
            products.begin(),
            products.end(),
            back_inserter(result),
            [threshold](const Product& product) {
                return product.stock > 0 &&
                       product.stock <= threshold;
            }
        );

        return result;
    }

    // Return all products in a category.
    vector<Product> byCategory(const string& category) const {
        vector<Product> result;

        copy_if(
            products.begin(),
            products.end(),
            back_inserter(result),
            [&](const Product& product) {
                return product.category == category;
            }
        );

        return result;
    }

    // Sort products by price descending.
    void sortByPriceDescending() {
        sort(
            products.begin(),
            products.end(),
            [](const Product& left, const Product& right) {
                return left.price > right.price;
            }
        );
    }

    // Sort products by stock ascending.
    void sortByStockAscending() {
        sort(
            products.begin(),
            products.end(),
            [](const Product& left, const Product& right) {
                if (left.stock != right.stock) {
                    return left.stock < right.stock;
                }

                return left.name < right.name;
            }
        );
    }

    // Reverse the sequence.
    void reverseOrder() {
        reverse(products.begin(), products.end());
    }

    // Count products matching a predicate.
    template <typename Predicate>
    size_t countIf(Predicate predicate) const {
        return static_cast<size_t>(
            count_if(products.begin(), products.end(), predicate)
        );
    }

    // Total inventory value.
    double totalValue() const {
        return accumulate(
            products.begin(),
            products.end(),
            0.0,
            [](double total, const Product& product) {
                return total +
                       product.price * product.stock;
            }
        );
    }

    // Read-only access when reporting is needed.
    const vector<Product>& data() const {
        return products;
    }

    bool empty() const {
        return products.empty();
    }

    size_t size() const {
        return products.size();
    }
};


// ---------------------------------------------------------------------------
// Output functions
// ---------------------------------------------------------------------------

void printProduct(const Product& product) {
    cout << left
         << setw(8) << product.sku
         << setw(20) << product.name
         << setw(16) << product.category
         << right << setw(10) << fixed << setprecision(2)
         << product.price
         << setw(8) << product.stock
         << '\n';
}

void printProducts(
    const vector<Product>& products,
    const string& title
) {
    cout << "\n" << title << "\n";

    cout << left
         << setw(8) << "SKU"
         << setw(20) << "Name"
         << setw(16) << "Category"
         << right
         << setw(10) << "Price"
         << setw(8) << "Stock"
         << '\n';

    cout << string(62, '-') << '\n';

    for (const auto& product : products) {
        printProduct(product);
    }
}


// ---------------------------------------------------------------------------
// Basic vector demonstration
// ---------------------------------------------------------------------------

void basicVectorOperations() {
    section("1. Basic Vector Operations");

    vector<int> numbers;

    // Equivalent to Python list.append().
    numbers.push_back(10);
    numbers.push_back(20);
    numbers.push_back(30);

    printVector(numbers, "After push_back");

    // Equivalent to Python list.extend().
    vector<int> additional{40, 50, 60};

    numbers.insert(
        numbers.end(),
        additional.begin(),
        additional.end()
    );

    printVector(numbers, "After range insert");

    // Equivalent to Python list.insert().
    numbers.insert(
        numbers.begin() + 2,
        25
    );

    printVector(numbers, "After inserting 25 at index 2");

    // Equivalent to Python list.pop().
    int removed = numbers.back();
    numbers.pop_back();

    cout << "Popped value: " << removed << '\n';
    printVector(numbers, "After pop_back");

    // Equivalent to Python list.reverse().
    reverse(numbers.begin(), numbers.end());

    printVector(numbers, "After reverse");

    // Equivalent to Python list.sort().
    sort(numbers.begin(), numbers.end());

    printVector(numbers, "After sort");

    // Equivalent to Python list.copy().
    vector<int> copied = numbers;

    copied.push_back(999);

    printVector(numbers, "Original");
    printVector(copied, "Copy");
}


// ---------------------------------------------------------------------------
// Search and count demonstration
// ---------------------------------------------------------------------------

void searchAndCount() {
    section("2. Search and Count");

    vector<string> languages{
        "Python",
        "C++",
        "Python",
        "JavaScript",
        "Python"
    };

    auto iterator = find(
        languages.begin(),
        languages.end(),
        "Python"
    );

    if (iterator != languages.end()) {
        size_t index = static_cast<size_t>(
            distance(languages.begin(), iterator)
        );

        cout << "First Python index: " << index << '\n';
    }

    size_t pythonCount = static_cast<size_t>(
        count(
            languages.begin(),
            languages.end(),
            "Python"
        )
    );

    cout << "Python count: " << pythonCount << '\n';

    bool containsRust =
        find(
            languages.begin(),
            languages.end(),
            "Rust"
        ) != languages.end();

    cout << boolalpha;
    cout << "Contains Rust: " << containsRust << '\n';
}


// ---------------------------------------------------------------------------
// Inventory initialization
// ---------------------------------------------------------------------------

Inventory buildInventory() {
    Inventory inventory;

    inventory.addProduct({
        "KB001",
        "Keyboard",
        "Peripherals",
        2500.00,
        12
    });

    inventory.addProduct({
        "MS001",
        "Mouse",
        "Peripherals",
        1200.00,
        4
    });

    inventory.addProduct({
        "MN001",
        "Monitor",
        "Displays",
        18000.00,
        0
    });

    inventory.addProduct({
        "HD001",
        "Hard Drive",
        "Storage",
        6500.00,
        7
    });

    inventory.addProduct({
        "LP001",
        "Laptop",
        "Computers",
        75000.00,
        3
    });

    return inventory;
}


// ---------------------------------------------------------------------------
// Inventory case study
// ---------------------------------------------------------------------------

void inventoryCaseStudy() {
    section("3. Industry-Style Inventory Case Study");

    Inventory inventory = buildInventory();

    printProducts(
        inventory.data(),
        "Initial Inventory"
    );

    cout << "\nInventory size: "
         << inventory.size()
         << '\n';

    cout << "Inventory value: "
         << fixed << setprecision(2)
         << inventory.totalValue()
         << '\n';

    // Searching by SKU.
    auto found = inventory.findBySku("MS001");

    if (found.has_value()) {
        cout << "\nFound product:\n";
        printProduct(*found);
    }

    // Finding the position.
    auto position = inventory.indexOf("HD001");

    if (position.has_value()) {
        cout << "HD001 index: " << *position << '\n';
    }

    // Low-stock filtering.
    auto lowStockProducts = inventory.lowStock(5);

    printProducts(
        lowStockProducts,
        "Low-Stock Products"
    );

    // Category filtering.
    auto peripherals = inventory.byCategory("Peripherals");

    printProducts(
        peripherals,
        "Peripheral Products"
    );

    // Sorting.
    inventory.sortByPriceDescending();

    printProducts(
        inventory.data(),
        "Sorted by Price Descending"
    );

    // Updating stock.
    bool stockUpdated =
        inventory.updateStock("MS001", 10);

    cout << "\nStock update successful: "
         << boolalpha
         << stockUpdated
         << '\n';

    // Invalid stock operation is rejected.
    bool invalidUpdate =
        inventory.updateStock("MS001", -1000);

    cout << "Invalid stock update accepted: "
         << invalidUpdate
         << '\n';

    // Add another batch of products.
    vector<Product> additionalProducts{
        {
            "CAM001",
            "Webcam",
            "Peripherals",
            4500.00,
            6
        },
        {
            "SSD001",
            "SSD",
            "Storage",
            8500.00,
            9
        }
    };

    inventory.extend(additionalProducts);

    printProducts(
        inventory.data(),
        "After Extending Inventory"
    );

    // Remove a product.
    bool removed =
        inventory.removeBySku("MN001");

    cout << "\nMonitor removed: "
         << boolalpha
         << removed
         << '\n';

    // Demonstrate insertion.
    inventory.insertProduct(
        0,
        {
            "UPS001",
            "UPS",
            "Power",
            9000.00,
            5
        }
    );

    printProducts(
        inventory.data(),
        "After Insertion"
    );

    // Count products according to a condition.
    size_t zeroStockCount =
        inventory.countIf(
            [](const Product& product) {
                return product.stock == 0;
            }
        );

    cout << "\nOut-of-stock product count: "
         << zeroStockCount
         << '\n';

    // Reverse ordering.
    inventory.reverseOrder();

    printProducts(
        inventory.data(),
        "After Reverse"
    );
}


// ---------------------------------------------------------------------------
// Validation demonstration
// ---------------------------------------------------------------------------

void validationCase() {
    section("4. Validation and Failure Handling");

    Inventory inventory;

    try {
        inventory.addProduct({
            "",
            "Invalid Product",
            "Test",
            100.00,
            10
        });
    }
    catch (const invalid_argument& error) {
        cout << "Validation error: "
             << error.what()
             << '\n';
    }

    try {
        inventory.addProduct({
            "BAD001",
            "Bad Stock",
            "Test",
            100.00,
            -5
        });
    }
    catch (const invalid_argument& error) {
        cout << "Validation error: "
             << error.what()
             << '\n';
    }

    inventory.addProduct({
        "GOOD001",
        "Valid Product",
        "Test",
        100.00,
        10
    });

    try {
        inventory.addProduct({
            "GOOD001",
            "Duplicate Product",
            "Test",
            200.00,
            5
        });
    }
    catch (const invalid_argument& error) {
        cout << "Duplicate error: "
             << error.what()
             << '\n';
    }

    try {
        inventory.insertProduct(
            100,
            {
                "BAD002",
                "Bad Position",
                "Test",
                200.00,
                5
            }
        );
    }
    catch (const out_of_range& error) {
        cout << "Position error: "
             << error.what()
             << '\n';
    }
}


// ---------------------------------------------------------------------------
// Copy semantics demonstration
// ---------------------------------------------------------------------------

void copyCase() {
    section("5. Copy Semantics");

    Inventory original = buildInventory();

    // vector and Inventory use value semantics here. Copying produces a
    // separate collection of Product objects.
    Inventory copied = original;

    copied.updateStock("KB001", -5);

    auto originalKeyboard = original.findBySku("KB001");
    auto copiedKeyboard = copied.findBySku("KB001");

    if (originalKeyboard.has_value() &&
        copiedKeyboard.has_value()) {

        cout << "Original keyboard stock: "
             << originalKeyboard->stock
             << '\n';

        cout << "Copied keyboard stock: "
             << copiedKeyboard->stock
             << '\n';
    }
}


// ---------------------------------------------------------------------------
// Algorithmic complexity discussion
// ---------------------------------------------------------------------------

void complexityCase() {
    section("6. Complexity Characteristics");

    cout << "vector indexing: O(1)\n";
    cout << "push_back: O(1) amortized\n";
    cout << "pop_back: O(1)\n";
    cout << "search with find: O(n)\n";
    cout << "count: O(n)\n";
    cout << "insert in middle: O(n)\n";
    cout << "erase in middle: O(n)\n";
    cout << "sort: O(n log n) typical\n";
    cout << "reverse: O(n)\n";
    cout << "copying vector: O(n)\n";

    cout << "\nThe vector is contiguous in memory, which generally gives good "
            "cache locality and fast indexed access.\n";

    cout << "Frequent insertion/removal at the front can be expensive because "
            "remaining elements must be shifted.\n";

    cout << "For a queue with frequent front removal, std::deque may be a "
            "better container.\n";
}


// ---------------------------------------------------------------------------
// Transaction processing
// ---------------------------------------------------------------------------

struct Transaction {
    string sku;
    int quantity;
    bool purchase;
};

void processTransactions(
    Inventory& inventory,
    const vector<Transaction>& transactions
) {
    section("7. Transaction Processing");

    for (const auto& transaction : transactions) {
        int change =
            transaction.purchase
                ? transaction.quantity
                : -transaction.quantity;

        bool success =
            inventory.updateStock(
                transaction.sku,
                change
            );

        cout << "Transaction for "
             << transaction.sku
             << " quantity="
             << transaction.quantity
             << " type="
             << (transaction.purchase ? "purchase" : "sale")
             << " accepted="
             << boolalpha
             << success
             << '\n';
    }
}


// ---------------------------------------------------------------------------
// Report generation
// ---------------------------------------------------------------------------

void generateReport(const Inventory& inventory) {
    section("8. Final Inventory Report");

    printProducts(
        inventory.data(),
        "Final Inventory"
    );

    const auto& data = inventory.data();

    if (data.empty()) {
        cout << "Inventory is empty.\n";
        return;
    }

    auto highestValue = max_element(
        data.begin(),
        data.end(),
        [](const Product& left, const Product& right) {
            return left.price * left.stock <
                   right.price * right.stock;
        }
    );

    cout << "\nHighest inventory-value product: "
         << highestValue->name
         << '\n';

    cout << "Inventory value: "
         << fixed
         << setprecision(2)
         << inventory.totalValue()
         << '\n';
}


// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main() {
    try {
        basicVectorOperations();
        searchAndCount();
        inventoryCaseStudy();
        validationCase();
        copyCase();
        complexityCase();

        Inventory transactionalInventory =
            buildInventory();

        vector<Transaction> transactions{
            {"KB001", 5, false},
            {"MS001", 20, true},
            {"HD001", 2, false},
            {"LP001", 1, false},
            {"MN001", 1, false}
        };

        processTransactions(
            transactionalInventory,
            transactions
        );

        generateReport(
            transactionalInventory
        );

        section("9. Empty Container Edge Case");

        Inventory emptyInventory;

        cout << "Empty inventory: "
             << boolalpha
             << emptyInventory.empty()
             << '\n';

        auto popped = emptyInventory.popBack();

        cout << "popBack() returned a value: "
             << popped.has_value()
             << '\n';

        emptyInventory.clear();

        cout << "clear() on empty inventory completed.\n";

        section("10. Program Completed");

        cout << "The C++ case study completed successfully.\n";
        cout << "The implementation demonstrates list-like sequence "
                "operations through std::vector and standard algorithms.\n";
    }
    catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }

    return 0;
}
