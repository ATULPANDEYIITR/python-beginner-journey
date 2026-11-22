#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * STATIC METHODS IN C++17
 *
 * Scenario: Enterprise financial transaction and account management.
 *
 * Concepts:
 * - Static member functions.
 * - Static data members.
 * - Object-independent operations.
 * - Static factory methods.
 * - Shared state.
 * - Static validation and policy functions.
 * - Caching.
 * - Access control.
 * - State transitions.
 * - Exception handling.
 *
 * Compile:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic static_methods.cpp -o static_methods
 */

namespace enterprise {

// ============================================================
// 1. STATIC UTILITY METHODS
// ============================================================

class NumericUtilities {
public:
    static double add(double a, double b) {
        validate(a, b);
        return a + b;
    }

    static double subtract(double a, double b) {
        validate(a, b);
        return a - b;
    }

    static double multiply(double a, double b) {
        validate(a, b);
        return a * b;
    }

    static double divide(double a, double b) {
        validate(a, b);

        if (b == 0.0) {
            throw std::domain_error("Division by zero.");
        }

        return a / b;
    }

    static double percentage(double part, double total) {
        validate(part, total);

        if (total == 0.0) {
            throw std::domain_error("Total cannot be zero.");
        }

        return (part / total) * 100.0;
    }

private:
    static void validate(double a, double b) {
        if (!std::isfinite(a) || !std::isfinite(b)) {
            throw std::invalid_argument("Inputs must be finite.");
        }
    }
};

// ============================================================
// 2. DOMAIN TYPES
// ============================================================

enum class TransactionType {
    CREDIT,
    DEBIT
};

enum class TransactionStatus {
    PENDING,
    COMPLETED,
    REJECTED
};

struct Transaction {
    std::string id;
    TransactionType type;
    double amount;
    TransactionStatus status;
};

struct AccountSnapshot {
    int accountId;
    std::string owner;
    double balance;
};

// ============================================================
// 3. STATIC BUSINESS VALIDATION
// ============================================================

class TransactionRules {
public:
    static bool validAmount(double amount) {
        return std::isfinite(amount) && amount > 0.0;
    }

    static bool validAccountId(int accountId) {
        return accountId > 0;
    }

    static bool canDebit(double balance, double amount) {
        return std::isfinite(balance)
            && balance >= 0.0
            && validAmount(amount)
            && amount <= balance;
    }

    static std::optional<std::string> validate(
        const Transaction& transaction
    ) {
        if (transaction.id.empty()) {
            return "Transaction ID is required.";
        }

        if (!validAmount(transaction.amount)) {
            return "Transaction amount must be positive and finite.";
        }

        if (transaction.status != TransactionStatus::PENDING) {
            return "Only pending transactions can be processed.";
        }

        return std::nullopt;
    }
};

// ============================================================
// 4. ACCOUNT DOMAIN MODEL
// ============================================================

class BankAccount {
private:
    int accountId_;
    std::string owner_;
    double balance_;

    // Static data is shared by all account objects.
    inline static std::uint64_t totalAccounts_ = 0;

    inline static std::set<std::string> processedIds_;

public:
    BankAccount(
        int accountId,
        std::string owner,
        double initialBalance
    )
        : accountId_(accountId),
          owner_(std::move(owner)),
          balance_(initialBalance) {

        if (!TransactionRules::validAccountId(accountId_)) {
            throw std::invalid_argument("Invalid account ID.");
        }

        if (owner_.empty()) {
            throw std::invalid_argument("Owner is required.");
        }

        if (!std::isfinite(balance_) || balance_ < 0.0) {
            throw std::invalid_argument("Invalid opening balance.");
        }

        ++totalAccounts_;
    }

    // Instance method: uses the current object's state.
    double getBalance() const {
        return balance_;
    }

    int getAccountId() const {
        return accountId_;
    }

    // Static method: does not access a particular account object.
    static std::uint64_t totalAccounts() {
        return totalAccounts_;
    }

    static bool validOwner(const std::string& owner) {
        return !owner.empty() && owner.size() <= 100;
    }

    // Static factory method.
    static BankAccount create(
        int accountId,
        const std::string& owner,
        double openingBalance
    ) {
        if (!validOwner(owner)) {
            throw std::invalid_argument("Invalid account owner.");
        }

        return BankAccount(accountId, owner, openingBalance);
    }

    // A transaction is validated before account state is changed.
    Transaction process(Transaction transaction) {
        const auto validation = TransactionRules::validate(transaction);

        if (validation.has_value()) {
            transaction.status = TransactionStatus::REJECTED;
            throw std::invalid_argument(validation.value());
        }

        if (processedIds_.count(transaction.id) != 0) {
            transaction.status = TransactionStatus::REJECTED;
            throw std::logic_error("Duplicate transaction.");
        }

        if (transaction.type == TransactionType::DEBIT) {
            if (!TransactionRules::canDebit(balance_, transaction.amount)) {
                transaction.status = TransactionStatus::REJECTED;
                throw std::runtime_error("Insufficient funds.");
            }
        }

        // Commit state only after all validations succeed.
        const double previousBalance = balance_;

        try {
            processedIds_.insert(transaction.id);

            if (transaction.type == TransactionType::CREDIT) {
                balance_ += transaction.amount;
            } else {
                balance_ -= transaction.amount;
            }

            if (!std::isfinite(balance_)) {
                balance_ = previousBalance;
                processedIds_.erase(transaction.id);
                throw std::overflow_error("Balance overflow.");
            }
        } catch (...) {
            balance_ = previousBalance;
            processedIds_.erase(transaction.id);
            throw;
        }

        transaction.status = TransactionStatus::COMPLETED;

        return transaction;
    }

    AccountSnapshot snapshot() const {
        return {
            accountId_,
            owner_,
            balance_
        };
    }
};

// ============================================================
// 5. STATIC POLICY EVALUATION ENGINE
// ============================================================

enum class Role {
    READER,
    ANALYST,
    ADMINISTRATOR
};

enum class Operation {
    READ,
    ANALYZE,
    WRITE,
    DELETE
};

class AccessControl {
public:
    static bool permitted(Role role, Operation operation) {
        switch (role) {
            case Role::READER:
                return operation == Operation::READ;

            case Role::ANALYST:
                return operation == Operation::READ
                    || operation == Operation::ANALYZE;

            case Role::ADMINISTRATOR:
                return true;
        }

        return false;
    }
};

// ============================================================
// 6. STATIC ANALYTICS
// ============================================================

struct Statistics {
    std::size_t count;
    double minimum;
    double maximum;
    double mean;
    double median;
};

class AnalyticsEngine {
public:
    static Statistics calculate(std::vector<double> values) {
        if (values.empty()) {
            throw std::invalid_argument("Dataset cannot be empty.");
        }

        for (double value : values) {
            if (!std::isfinite(value)) {
                throw std::invalid_argument(
                    "Dataset contains a non-finite value."
                );
            }
        }

        std::sort(values.begin(), values.end());

        const std::size_t count = values.size();

        const double sum = std::accumulate(
            values.begin(),
            values.end(),
            0.0
        );

        const double median = count % 2 == 0
            ? (
                values[count / 2 - 1]
                + values[count / 2]
              ) / 2.0
            : values[count / 2];

        return {
            count,
            values.front(),
            values.back(),
            sum / static_cast<double>(count),
            median
        };
    }
};

// ============================================================
// 7. STATIC CACHING
// ============================================================

class FactorialService {
private:
    inline static std::unordered_map<unsigned int, std::uint64_t> cache_{
        {0, 1},
        {1, 1}
    };

public:
    static std::uint64_t calculate(unsigned int number) {
        if (number > 20) {
            throw std::out_of_range(
                "Factorial exceeds uint64_t capacity."
            );
        }

        const auto existing = cache_.find(number);

        if (existing != cache_.end()) {
            return existing->second;
        }

        std::uint64_t result = 1;

        for (unsigned int i = 2; i <= number; ++i) {
            result *= i;
        }

        cache_[number] = result;

        return result;
    }

    static std::size_t cacheSize() {
        return cache_.size();
    }
};

// ============================================================
// 8. STATIC CONFIGURATION VALIDATION
// ============================================================

struct ApplicationConfiguration {
    std::string application;
    std::string environment;
    unsigned int port;
};

class ConfigurationValidator {
public:
    static bool valid(
        const ApplicationConfiguration& config
    ) {
        const bool validEnvironment =
            config.environment == "development"
            || config.environment == "testing"
            || config.environment == "production";

        return !config.application.empty()
            && validEnvironment
            && config.port >= 1
            && config.port <= 65535;
    }
};

// ============================================================
// 9. STATIC METHOD TESTING
// ============================================================

void runTests() {
    using namespace enterprise;

    if (NumericUtilities::add(10, 20) != 30) {
        throw std::runtime_error("Addition test failed.");
    }

    if (NumericUtilities::divide(100, 5) != 20) {
        throw std::runtime_error("Division test failed.");
    }

    try {
        NumericUtilities::divide(10, 0);
        throw std::runtime_error("Division validation failed.");
    } catch (const std::domain_error&) {
        // Expected behavior.
    }

    if (!TransactionRules::validAmount(100)) {
        throw std::runtime_error("Amount validation failed.");
    }

    if (TransactionRules::validAmount(-10)) {
        throw std::runtime_error("Negative amount accepted.");
    }

    if (!AccessControl::permitted(
        Role::ADMINISTRATOR,
        Operation::DELETE
    )) {
        throw std::runtime_error("Authorization test failed.");
    }

    if (AccessControl::permitted(
        Role::READER,
        Operation::DELETE
    )) {
        throw std::runtime_error("Unauthorized access permitted.");
    }

    if (FactorialService::calculate(5) != 120) {
        throw std::runtime_error("Factorial test failed.");
    }

    const auto statistics = AnalyticsEngine::calculate({
        10, 20, 30, 40
    });

    if (statistics.mean != 25.0 || statistics.median != 25.0) {
        throw std::runtime_error("Analytics test failed.");
    }

    auto account = BankAccount::create(
        900,
        "Research Division",
        10000
    );

    auto transaction = account.process({
        "TX-001",
        TransactionType::DEBIT,
        2500,
        TransactionStatus::PENDING
    });

    if (transaction.status != TransactionStatus::COMPLETED) {
        throw std::runtime_error("Transaction test failed.");
    }

    if (account.getBalance() != 7500) {
        throw std::runtime_error("Balance test failed.");
    }

    std::cout << "All C++17 static method tests passed.\n";
}

// ============================================================
// 10. APPLICATION ENTRY POINT
// ============================================================

int main() {
    try {
        using namespace enterprise;

        std::cout << std::fixed << std::setprecision(2);

        std::cout << "STATIC METHODS IN C++17\n";
        std::cout << "======================\n";

        std::cout << "\n1. Static mathematical operations\n";

        std::cout << "Addition: "
                  << NumericUtilities::add(100, 250)
                  << '\n';

        std::cout << "Percentage: "
                  << NumericUtilities::percentage(25, 200)
                  << "%\n";

        std::cout << "\n2. Static factory method\n";

        BankAccount account = BankAccount::create(
            1001,
            "Enterprise Research",
            100000
        );

        std::cout << "Account ID: "
                  << account.getAccountId()
                  << '\n';

        std::cout << "Opening balance: "
                  << account.getBalance()
                  << '\n';

        std::cout << "\n3. Transaction processing\n";

        const Transaction credit = account.process({
            "TX-1001",
            TransactionType::CREDIT,
            25000,
            TransactionStatus::PENDING
        });

        std::cout << "Transaction: "
                  << credit.id
                  << '\n';

        std::cout << "New balance: "
                  << account.getBalance()
                  << '\n';

        std::cout << "\n4. Static access control\n";

        std::cout << "Analyst can analyze: "
                  << std::boolalpha
                  << AccessControl::permitted(
                      Role::ANALYST,
                      Operation::ANALYZE
                  )
                  << '\n';

        std::cout << "Reader can delete: "
                  << AccessControl::permitted(
                      Role::READER,
                      Operation::DELETE
                  )
                  << '\n';

        std::cout << "\n5. Static analytics\n";

        const Statistics statistics =
            AnalyticsEngine::calculate({
                1200, 1500, 1800, 2100, 2400
            });

        std::cout << "Mean: "
                  << statistics.mean
                  << '\n';

        std::cout << "Median: "
                  << statistics.median
                  << '\n';

        std::cout << "\n6. Static caching\n";

        std::cout << "Factorial 10: "
                  << FactorialService::calculate(10)
                  << '\n';

        std::cout << "Cache entries: "
                  << FactorialService::cacheSize()
                  << '\n';

        std::cout << "\n7. Shared class-level state\n";

        std::cout << "Total accounts created: "
                  << BankAccount::totalAccounts()
                  << '\n';

        std::cout << "\n8. Configuration validation\n";

        ApplicationConfiguration config{
            "FinancialService",
            "production",
            8080
        };

        std::cout << "Configuration valid: "
                  << ConfigurationValidator::valid(config)
                  << '\n';

        std::cout << "\n9. Automated tests\n";

        runTests();

        return 0;

    } catch (const std::exception& exception) {
        std::cerr << "Application error: "
                  << exception.what()
                  << '\n';

        return 1;
    }
}
