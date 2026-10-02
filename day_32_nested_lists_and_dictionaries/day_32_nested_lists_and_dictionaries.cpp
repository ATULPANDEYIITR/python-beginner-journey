#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Nested Lists and Dictionaries
 *
 * C++ does not have a built-in dictionary/list pair identical to Python.
 * std::vector provides ordered nested collections, while std::map and
 * std::unordered_map provide dictionary-like structures.
 *
 * Case study:
 * A warehouse inventory service stores products as structured records.
 * Each product has nested pricing information and a list of warehouse
 * quantities. The program builds indexes so repeated product and category
 * lookups do not require scanning the complete nested dataset.
 */

struct WarehouseStock {
    std::string city;
    int quantity;
};

struct Pricing {
    std::string currency;
    double amount;
};

struct Product {
    std::string sku;
    std::string name;
    std::string category;
    Pricing pricing;
    std::vector<WarehouseStock> warehouses;
};

class InventoryRepository {
private:
    std::vector<Product> products_;

    std::unordered_map<std::string, const Product*> bySku_;
    std::unordered_map<std::string, std::vector<const Product*>> byCategory_;

public:
    explicit InventoryRepository(std::vector<Product> products)
        : products_(std::move(products)) {
        buildIndexes();
    }

    void buildIndexes() {
        bySku_.clear();
        byCategory_.clear();

        for (const auto& product : products_) {
            if (product.sku.empty()) {
                throw std::invalid_argument("Product SKU cannot be empty.");
            }

            if (bySku_.contains(product.sku)) {
                throw std::invalid_argument(
                    "Duplicate SKU: " + product.sku
                );
            }

            if (product.pricing.amount < 0) {
                throw std::invalid_argument(
                    "Product price cannot be negative: " + product.sku
                );
            }

            for (const auto& warehouse : product.warehouses) {
                if (warehouse.city.empty()) {
                    throw std::invalid_argument(
                        "Warehouse city cannot be empty: " + product.sku
                    );
                }

                if (warehouse.quantity < 0) {
                    throw std::invalid_argument(
                        "Warehouse quantity cannot be negative: " + product.sku
                    );
                }
            }

            bySku_[product.sku] = &product;
            byCategory_[product.category].push_back(&product);
        }
    }

    std::optional<std::reference_wrapper<const Product>>
    findBySku(const std::string& sku) const {
        auto it = bySku_.find(sku);

        if (it == bySku_.end()) {
            return std::nullopt;
        }

        return std::cref(*it->second);
    }

    std::vector<std::reference_wrapper<const Product>>
    findByCategory(const std::string& category) const {
        std::vector<std::reference_wrapper<const Product>> result;

        auto it = byCategory_.find(category);
        if (it == byCategory_.end()) {
            return result;
        }

        for (const Product* product : it->second) {
            result.push_back(std::cref(*product));
        }

        return result;
    }

    std::map<std::string, int> stockByCity() const {
        std::map<std::string, int> totals;

        for (const auto& product : products_) {
            for (const auto& warehouse : product.warehouses) {
                totals[warehouse.city] += warehouse.quantity;
            }
        }

        return totals;
    }

    double inventoryValue() const {
        double value = 0.0;

        for (const auto& product : products_) {
            int stock = 0;

            for (const auto& warehouse : product.warehouses) {
                stock += warehouse.quantity;
            }

            value += stock * product.pricing.amount;
        }

        return value;
    }

    const std::vector<Product>& products() const {
        return products_;
    }
};

void printHeading(const std::string& title) {
    std::cout << "\n" << std::string(72, '=') << "\n";
    std::cout << title << "\n";
    std::cout << std::string(72, '=') << "\n";
}

void demonstrateNestedVectors() {
    printHeading("Nested vectors");

    std::vector<std::vector<int>> warehouseGrid = {
        {12, 8, 4},
        {20, 11, 9},
        {7, 15, 13}
    };

    std::cout << "Warehouse grid:\n";

    for (const auto& row : warehouseGrid) {
        for (int value : row) {
            std::cout << std::setw(4) << value;
        }
        std::cout << '\n';
    }

    int total = 0;

    for (const auto& row : warehouseGrid) {
        for (int quantity : row) {
            total += quantity;
        }
    }

    std::cout << "Total stock: " << total << '\n';

    // vector<vector<T>> permits rows of different lengths. Code that assumes
    // a rectangular matrix must validate each row before using fixed columns.
    warehouseGrid.push_back({5, 6});

    std::cout << "Rows after adding a variable-length row: "
              << warehouseGrid.size() << '\n';
}

void demonstrateNestedMaps() {
    printHeading("Nested maps");

    std::map<std::string, std::map<std::string, int>> regionalStock = {
        {
            "North",
            {
                {"Delhi", 120},
                {"Chandigarh", 80}
            }
        },
        {
            "South",
            {
                {"Bengaluru", 150},
                {"Chennai", 95}
            }
        }
    };

    regionalStock["North"]["Delhi"] += 25;
    regionalStock["South"]["Hyderabad"] = 70;

    for (const auto& [region, cities] : regionalStock) {
        std::cout << region << ":\n";

        for (const auto& [city, quantity] : cities) {
            std::cout << "  " << city << " -> " << quantity << '\n';
        }
    }
}

void demonstrateNestedMixedStructures() {
    printHeading("Maps containing vectors and structured records");

    std::map<std::string, std::vector<std::string>> teams = {
        {"Engineering", {"Anika", "Ravi", "Meera"}},
        {"Analytics", {"Kabir", "Neha"}}
    };

    teams["Engineering"].push_back("Sanjay");

    for (const auto& [department, members] : teams) {
        std::cout << department << ": ";

        for (std::size_t index = 0; index < members.size(); ++index) {
            if (index != 0) {
                std::cout << ", ";
            }
            std::cout << members[index];
        }

        std::cout << '\n';
    }
}

std::optional<int> safeMatrixValue(
    const std::vector<std::vector<int>>& matrix,
    std::size_t row,
    std::size_t column
) {
    if (row >= matrix.size()) {
        return std::nullopt;
    }

    if (column >= matrix[row].size()) {
        return std::nullopt;
    }

    return matrix[row][column];
}

void demonstrateValidationAndSafeAccess() {
    printHeading("Bounds validation for nested vectors");

    std::vector<std::vector<int>> matrix = {
        {10, 20, 30},
        {40, 50},
        {60, 70, 80, 90}
    };

    auto valid = safeMatrixValue(matrix, 2, 3);
    auto invalid = safeMatrixValue(matrix, 1, 3);

    std::cout << "Valid lookup: "
              << (valid ? std::to_string(*valid) : "missing")
              << '\n';

    std::cout << "Invalid lookup: "
              << (invalid ? std::to_string(*invalid) : "missing")
              << '\n';
}

void printProduct(const Product& product) {
    std::cout << product.sku << " | "
              << product.name << " | "
              << product.category << " | "
              << product.pricing.currency << ' '
              << std::fixed << std::setprecision(2)
              << product.pricing.amount << '\n';

    for (const auto& warehouse : product.warehouses) {
        std::cout << "    " << warehouse.city
                  << ": " << warehouse.quantity << '\n';
    }
}

void runInventoryCaseStudy() {
    printHeading("Inventory case study");

    std::vector<Product> products = {
        {
            "LAP-100",
            "Developer Laptop",
            "computing",
            {"INR", 95000.00},
            {
                {"Delhi", 12},
                {"Pune", 8}
            }
        },
        {
            "MON-200",
            "4K Monitor",
            "display",
            {"INR", 42000.00},
            {
                {"Delhi", 5},
                {"Pune", 11}
            }
        },
        {
            "LAP-300",
            "Engineering Laptop",
            "computing",
            {"INR", 125000.00},
            {
                {"Bengaluru", 7}
            }
        }
    };

    InventoryRepository repository(products);

    std::cout << "Product found by SKU:\n";

    auto product = repository.findBySku("LAP-100");

    if (product.has_value()) {
        printProduct(product->get());
    } else {
        std::cout << "SKU not found.\n";
    }

    std::cout << "\nComputing category:\n";

    for (const auto& reference : repository.findByCategory("computing")) {
        printProduct(reference.get());
    }

    std::cout << "\nStock by city:\n";

    for (const auto& [city, quantity] : repository.stockByCity()) {
        std::cout << "  " << city << ": " << quantity << '\n';
    }

    std::cout << "\nInventory value: INR "
              << std::fixed << std::setprecision(2)
              << repository.inventoryValue()
              << '\n';
}

void demonstrateFailureConditions() {
    printHeading("Failure conditions and validation");

    try {
        std::vector<Product> duplicateProducts = {
            {
                "DUP-1",
                "First",
                "test",
                {"INR", 100.0},
                {{"Delhi", 2}}
            },
            {
                "DUP-1",
                "Second",
                "test",
                {"INR", 200.0},
                {{"Pune", 3}}
            }
        };

        InventoryRepository invalidRepository(duplicateProducts);
        (void)invalidRepository;
    } catch (const std::invalid_argument& error) {
        std::cout << "Rejected duplicate record: "
                  << error.what() << '\n';
    }

    try {
        std::vector<Product> negativeStock = {
            {
                "BAD-1",
                "Invalid Product",
                "test",
                {"INR", 100.0},
                {{"Delhi", -4}}
            }
        };

        InventoryRepository invalidRepository(negativeStock);
        (void)invalidRepository;
    } catch (const std::invalid_argument& error) {
        std::cout << "Rejected invalid stock: "
                  << error.what() << '\n';
    }
}

void discussComplexity() {
    printHeading("Complexity characteristics");

    std::cout
        << "Nested vector traversal visits each contained element: O(n).\n"
        << "std::map lookup is O(log n) because it is tree-based.\n"
        << "std::unordered_map lookup is O(1) average and O(n) worst case.\n"
        << "Building SKU and category indexes is O(n) average with unordered_map.\n"
        << "Inventory aggregation scans each product and warehouse entry once.\n"
        << "Reference-based indexes avoid copying Product objects during lookup.\n";
}

int main() {
    try {
        demonstrateNestedVectors();
        demonstrateNestedMaps();
        demonstrateNestedMixedStructures();
        demonstrateValidationAndSafeAccess();
        runInventoryCaseStudy();
        demonstrateFailureConditions();
        discussComplexity();

        printHeading("Completed");
        std::cout
            << "Nested-list and dictionary case study completed successfully.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
