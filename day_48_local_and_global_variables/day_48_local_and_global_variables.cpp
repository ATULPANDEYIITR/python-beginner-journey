#include <iostream>
#include <iomanip>
#include <string>
#include <vector>
#include <stdexcept>
#include <numeric>
#include <algorithm>
#include <functional>

// Namespace-scope constants have static storage duration.
// Internal linkage prevents this configuration from colliding with
// same-named symbols in other translation units.
namespace {
    constexpr double TAX_RATE = 0.18;
    constexpr int MAX_RETRY_ATTEMPTS = 3;
    const std::string APPLICATION_NAME = "Warehouse Operations";
}

int processedTransactions = 0;

struct AuditRecord {
    std::string operation;
    int quantity;
    int stockAfter;
};

class Warehouse {
private:
    std::string name_;
    int capacity_;
    int stock_;
    std::vector<AuditRecord> audit_;

public:
    Warehouse(std::string name, int capacity, int initialStock = 0)
        : name_(std::move(name)),
          capacity_(capacity),
          stock_(initialStock) {
        if (capacity_ < 0 || initialStock < 0 || initialStock > capacity_) {
            throw std::invalid_argument("Invalid warehouse capacity or stock.");
        }
    }

    bool receive(int quantity) {
        if (quantity <= 0) {
            throw std::invalid_argument("Received quantity must be positive.");
        }
        if (quantity > capacity_ - stock_) {
            return false;
        }

        stock_ += quantity;
        audit_.push_back({"receive", quantity, stock_});
        ++processedTransactions;
        return true;
    }

    bool dispatch(int quantity) {
        if (quantity <= 0) {
            throw std::invalid_argument("Dispatch quantity must be positive.");
        }
        if (quantity > stock_) {
            return false;
        }

        stock_ -= quantity;
        audit_.push_back({"dispatch", quantity, stock_});
        ++processedTransactions;
        return true;
    }

    int stock() const {
        return stock_;
    }

    const std::string& name() const {
        return name_;
    }

    const std::vector<AuditRecord>& audit() const {
        return audit_;
    }
};

// The parameter quantity is local to each function call. The reference
// allows the caller to observe a value without copying the warehouse.
void printWarehouseStatus(const Warehouse& warehouse) {
    const std::string displayName = warehouse.name();
    const int availableStock = warehouse.stock();

    std::cout << displayName << ": " << availableStock << " units\n";
}

// Demonstrates a closure-like callable whose state is captured by value.
// Each returned function has its own independent copy of taxRate.
std::function<double(double)> makeTaxCalculator(double taxRate) {
    if (taxRate < 0.0 || taxRate > 1.0) {
        throw std::invalid_argument("Tax rate must be between zero and one.");
    }

    return [taxRate](double subtotal) {
        if (subtotal < 0.0) {
            throw std::invalid_argument("Subtotal cannot be negative.");
        }
        return subtotal * (1.0 + taxRate);
    };
}

int main() {
    std::cout << "=== " << APPLICATION_NAME << " ===\n";
    std::cout << "Configured tax rate: " << TAX_RATE << '\n';
    std::cout << "Maximum retry attempts: " << MAX_RETRY_ATTEMPTS << "\n\n";

    try {
        Warehouse lucknow("Lucknow Distribution Centre", 500, 120);
        Warehouse kanpur("Kanpur Distribution Centre", 300, 80);

        // Each object owns independent stock_ and audit_ state.
        lucknow.receive(40);
        lucknow.dispatch(25);
        kanpur.dispatch(10);

        printWarehouseStatus(lucknow);
        printWarehouseStatus(kanpur);

        const auto calculateTaxInclusivePrice = makeTaxCalculator(TAX_RATE);
        const double subtotal = 2500.0;
        const double invoiceTotal = calculateTaxInclusivePrice(subtotal);

        std::cout << std::fixed << std::setprecision(2)
                  << "Invoice total: ₹" << invoiceTotal << '\n';

        // Local variable: exists only within this block.
        {
            const int auditCount = static_cast<int>(lucknow.audit().size());
            std::cout << "Lucknow audit entries: " << auditCount << '\n';
        }

        // The name auditCount is not visible here because its block ended.
        std::cout << "Valid transactions: " << processedTransactions << '\n';

        // A lambda can capture a local value safely by value.
        const int requestedQuantity = 15;
        const auto canDispatch = [requestedQuantity](const Warehouse& warehouse) {
            return warehouse.stock() >= requestedQuantity;
        };

        std::cout << "Lucknow can dispatch 15 units: "
                  << std::boolalpha << canDispatch(lucknow) << '\n';

        // Do not return a reference or pointer to an ordinary local variable:
        // its lifetime ends when its function returns.
        std::vector<int> monthlyShipments{20, 35, 28, 42};
        const int totalShipments = std::accumulate(
            monthlyShipments.begin(), monthlyShipments.end(), 0
        );

        std::cout << "Monthly shipments: " << totalShipments << '\n';

        std::cout << "\nLucknow audit trail:\n";
        for (const AuditRecord& record : lucknow.audit()) {
            std::cout << record.operation
                      << ", quantity=" << record.quantity
                      << ", stock_after=" << record.stockAfter << '\n';
        }
    } catch (const std::exception& error) {
        std::cerr << "Operation failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
