#include <algorithm>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

class DomainError : public runtime_error {
public:
    explicit DomainError(const string& message)
        : runtime_error(message) {}
};

enum class ProductStatus {
    ACTIVE,
    DISCONTINUED
};

struct ProductInput {
    string id;
    string name;
    string category;
    double price;
};

class Product {
private:
    string id_;
    string name_;
    string category_;
    double price_;
    ProductStatus status_;

    // Shared state belongs to the class, not individual objects.
    static unordered_map<string, shared_ptr<Product>> registry_;
    static double minimum_price_;
    static uint64_t created_count_;

    Product(
        const ProductInput& input,
        ProductStatus status
    )
        : id_(input.id),
          name_(input.name),
          category_(input.category),
          price_(input.price),
          status_(status) {

        if (id_.empty() || name_.empty() || category_.empty()) {
            throw DomainError("Required product fields are missing.");
        }

        if (price_ < minimum_price_) {
            throw DomainError("Price is below the minimum.");
        }
    }

public:
    Product(const Product&) = delete;
    Product& operator=(const Product&) = delete;

    // Static factory method.
    static shared_ptr<Product> create(
        const ProductInput& input
    ) {
        if (registry_.count(input.id)) {
            throw DomainError("Duplicate product identifier.");
        }

        auto product = shared_ptr<Product>(
            new Product(input, ProductStatus::ACTIVE)
        );

        registry_.emplace(input.id, product);
        ++created_count_;

        return product;
    }

    // Alternative constructor implemented as a static method.
    static shared_ptr<Product> from_record(
        const vector<string>& fields
    ) {
        if (fields.size() != 4) {
            throw DomainError("Expected four input fields.");
        }

        size_t consumed = 0;
        double price;

        try {
            price = stod(fields[3], &consumed);
        } catch (...) {
            throw DomainError("Invalid numeric price.");
        }

        if (consumed != fields[3].size()) {
            throw DomainError("Price contains invalid characters.");
        }

        return create({
            fields[0],
            fields[1],
            fields[2],
            price
        });
    }

    // Class-level lookup.
    static shared_ptr<Product> find(const string& id) {
        auto iterator = registry_.find(id);

        if (iterator == registry_.end()) {
            return nullptr;
        }

        return iterator->second;
    }

    static size_t count() {
        return registry_.size();
    }

    static uint64_t created_count() {
        return created_count_;
    }

    static void set_minimum_price(double value) {
        if (value <= 0) {
            throw DomainError("Minimum price must be positive.");
        }

        minimum_price_ = value;
    }

    static double minimum_price() {
        return minimum_price_;
    }

    // Static aggregation does not require an object instance.
    static map<string, pair<size_t, double>> category_report() {
        map<string, pair<size_t, double>> report;

        for (const auto& entry : registry_) {
            const Product& product = *entry.second;

            if (product.status_ != ProductStatus::ACTIVE) {
                continue;
            }

            auto& aggregate = report[product.category_];

            ++aggregate.first;
            aggregate.second += product.price_;
        }

        return report;
    }

    static bool discontinue(const string& id) {
        auto product = find(id);

        if (!product) {
            return false;
        }

        product->status_ = ProductStatus::DISCONTINUED;
        return true;
    }

    // A static utility method.
    static double calculate_tax(
        double amount,
        double tax_rate
    ) {
        if (amount < 0 || tax_rate < 0 || tax_rate > 100) {
            throw DomainError("Invalid tax calculation inputs.");
        }

        return amount * tax_rate / 100.0;
    }

    // Instance method.
    void apply_discount(double percentage) {
        if (status_ != ProductStatus::ACTIVE) {
            throw DomainError("Cannot discount discontinued products.");
        }

        if (percentage < 0 || percentage > 50) {
            throw DomainError("Discount must be between 0 and 50.");
        }

        price_ *= (100.0 - percentage) / 100.0;
    }

    void display() const {
        cout << left
             << setw(10) << id_
             << setw(25) << name_
             << setw(18) << category_
             << fixed << setprecision(2)
             << price_
             << " Status: "
             << (status_ == ProductStatus::ACTIVE
                     ? "ACTIVE"
                     : "DISCONTINUED")
             << '\n';
    }

    static void clear() {
        registry_.clear();
        created_count_ = 0;
    }
};

// Static member definitions.
unordered_map<string, shared_ptr<Product>> Product::registry_;
double Product::minimum_price_ = 100.0;
uint64_t Product::created_count_ = 0;

// Specialized product type.
class SubscriptionProduct : public Product {
private:
    int duration_months_;

public:
    SubscriptionProduct(
        const ProductInput& input,
        int duration_months
    )
        : Product(input, ProductStatus::ACTIVE),
          duration_months_(duration_months) {

        if (duration_months_ < 1 || duration_months_ > 60) {
            throw DomainError("Invalid subscription duration.");
        }
    }

    static shared_ptr<SubscriptionProduct> create_subscription(
        const ProductInput& input,
        int months
    ) {
        if (Product::find(input.id)) {
            throw DomainError("Duplicate product identifier.");
        }

        auto product = shared_ptr<SubscriptionProduct>(
            new SubscriptionProduct(input, months)
        );

        Product::registry_.emplace(input.id, product);
        ++Product::created_count_;

        return product;
    }

    void display() const {
        Product::display();
        cout << "Subscription duration: "
             << duration_months_ << " months\n";
    }
};

int main() {
    try {
        Product::clear();

        cout << "1. Class-level configuration\n";

        Product::set_minimum_price(500);

        cout << "Minimum price: "
             << Product::minimum_price() << "\n\n";

        cout << "2. Static factory method\n";

        auto laptop = Product::create({
            "P101",
            "Business Laptop",
            "Electronics",
            75000
        });

        laptop->display();

        cout << "\n3. Alternative constructor\n";

        auto chair = Product::from_record({
            "P102",
            "Office Chair",
            "Furniture",
            "12500"
        });

        chair->display();

        cout << "\n4. Subclass factory\n";

        auto subscription =
            SubscriptionProduct::create_subscription(
                {
                    "S101",
                    "Security Platform",
                    "Software",
                    12000
                },
                12
            );

        subscription->display();

        cout << "\n5. Class-level lookup\n";

        auto result = Product::find("P101");

        if (result) {
            result->display();
        }

        cout << "\n6. Instance-level operation\n";

        laptop->apply_discount(10);
        laptop->display();

        cout << "\n7. Category aggregation\n";

        auto report = Product::category_report();

        for (const auto& entry : report) {
            cout << entry.first
                 << " | Count: " << entry.second.first
                 << " | Value: " << entry.second.second
                 << '\n';
        }

        cout << "\n8. Static utility method\n";

        cout << "Tax: "
             << Product::calculate_tax(75000, 18)
             << '\n';

        cout << "\n9. State transition\n";

        Product::discontinue("P102");

        cout << "Chair discontinued successfully.\n";

        cout << "\n10. Registry statistics\n";

        cout << "Current products: "
             << Product::count() << '\n';

        cout << "Created products: "
             << Product::created_count() << '\n';

        cout << "\n11. Failure handling\n";

        try {
            Product::create({
                "P103",
                "Invalid Product",
                "Testing",
                -500
            });
        } catch (const DomainError& error) {
            cout << "Rejected: " << error.what() << '\n';
        }

        try {
            Product::create({
                "P101",
                "Duplicate Laptop",
                "Electronics",
                80000
            });
        } catch (const DomainError& error) {
            cout << "Rejected: " << error.what() << '\n';
        }

    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
