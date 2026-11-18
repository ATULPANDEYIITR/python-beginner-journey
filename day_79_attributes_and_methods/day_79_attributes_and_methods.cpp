#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * ATTRIBUTES AND METHODS
 *
 * Repository-independent banking domain used to demonstrate
 * C++17 object-oriented programming.
 *
 * Concepts:
 * - Public, protected and private attributes
 * - Instance and static attributes
 * - Constructors and destructors
 * - Instance and static methods
 * - Const methods
 * - Encapsulation
 * - Inheritance
 * - Virtual methods
 * - Method overriding
 * - Runtime polymorphism
 * - Composition
 * - Exceptions
 * - RAII and ownership considerations
 */

enum class AccountStatus {
    Active,
    Frozen,
    Closed
};

enum class TransactionType {
    Deposit,
    Withdrawal,
    TransferIn,
    TransferOut
};


std::string toString(AccountStatus status) {
    switch (status) {
        case AccountStatus::Active:
            return "ACTIVE";
        case AccountStatus::Frozen:
            return "FROZEN";
        case AccountStatus::Closed:
            return "CLOSED";
    }

    throw std::logic_error("Unknown account status.");
}


std::string toString(TransactionType type) {
    switch (type) {
        case TransactionType::Deposit:
            return "DEPOSIT";
        case TransactionType::Withdrawal:
            return "WITHDRAWAL";
        case TransactionType::TransferIn:
            return "TRANSFER_IN";
        case TransactionType::TransferOut:
            return "TRANSFER_OUT";
    }

    throw std::logic_error("Unknown transaction type.");
}


class AccountException : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};


struct Transaction {
    std::uint64_t id;
    TransactionType type;
    std::int64_t amountPaise;
    std::int64_t balanceAfterPaise;
};


class BankAccount {
private:
    // Private instance attributes protect account state.
    std::string accountNumber_;
    std::string owner_;
    std::int64_t balancePaise_;
    AccountStatus status_;

    std::vector<Transaction> history_;
    std::uint64_t sequence_ = 0;

    static std::size_t accountCount_;

    void ensureActive() const {
        if (status_ != AccountStatus::Active) {
            throw AccountException("Account is not active.");
        }
    }

    void record(TransactionType type, std::int64_t amount) {
        history_.push_back({
            ++sequence_,
            type,
            amount,
            balancePaise_
        });
    }

protected:
    // Protected attribute can be accessed by derived classes.
    std::int64_t minimumBalancePaise_ = 0;

public:
    // Static attributes belong to the class.
    inline static std::string bankName =
        "National Digital Bank";

    explicit BankAccount(
        std::string accountNumber,
        std::string owner,
        std::int64_t initialBalancePaise = 0
    )
        : accountNumber_(std::move(accountNumber)),
          owner_(std::move(owner)),
          balancePaise_(initialBalancePaise),
          status_(AccountStatus::Active) {

        if (accountNumber_.empty() || owner_.empty()) {
            throw std::invalid_argument(
                "Account number and owner are required."
            );
        }

        if (initialBalancePaise < 0) {
            throw std::invalid_argument(
                "Initial balance cannot be negative."
            );
        }

        ++accountCount_;
    }

    virtual ~BankAccount() = default;

    // Prevent accidental copying of account identity and state.
    BankAccount(const BankAccount&) = delete;
    BankAccount& operator=(const BankAccount&) = delete;

    BankAccount(BankAccount&&) = default;
    BankAccount& operator=(BankAccount&&) = default;

    // Read-only accessors.
    const std::string& accountNumber() const {
        return accountNumber_;
    }

    const std::string& owner() const {
        return owner_;
    }

    std::int64_t balancePaise() const {
        return balancePaise_;
    }

    AccountStatus status() const {
        return status_;
    }

    const std::vector<Transaction>& history() const {
        return history_;
    }

    // Static method.
    static std::size_t accountCount() {
        return accountCount_;
    }

    static void changeBankName(const std::string& name) {
        if (name.empty()) {
            throw std::invalid_argument(
                "Bank name cannot be empty."
            );
        }

        bankName = name;
    }

    static std::int64_t parseRupees(const std::string& value) {
        if (value.empty()) {
            throw std::invalid_argument("Amount is empty.");
        }

        std::size_t position = 0;
        double amount;

        try {
            amount = std::stod(value, &position);
        } catch (...) {
            throw std::invalid_argument("Invalid monetary amount.");
        }

        if (position != value.size() ||
            !std::isfinite(amount) ||
            amount < 0) {
            throw std::invalid_argument("Invalid monetary amount.");
        }

        const double paise = amount * 100.0;
        const auto rounded = static_cast<std::int64_t>(
            std::llround(paise)
        );

        if (std::abs(paise - static_cast<double>(rounded)) > 1e-7) {
            throw std::invalid_argument(
                "Amounts support two decimal places."
            );
        }

        return rounded;
    }

    static std::string formatMoney(std::int64_t paise) {
        std::ostringstream output;

        output << "INR "
               << paise / 100
               << "."
               << std::setw(2)
               << std::setfill('0')
               << paise % 100;

        return output.str();
    }

    // Instance method.
    virtual void deposit(std::int64_t amountPaise) {
        ensureActive();

        if (amountPaise <= 0) {
            throw std::invalid_argument(
                "Deposit must be positive."
            );
        }

        if (balancePaise_ >
            INT64_MAX - amountPaise) {
            throw std::overflow_error(
                "Balance overflow."
            );
        }

        balancePaise_ += amountPaise;
        record(TransactionType::Deposit, amountPaise);
    }

    virtual void withdraw(std::int64_t amountPaise) {
        ensureActive();

        if (amountPaise <= 0) {
            throw std::invalid_argument(
                "Withdrawal must be positive."
            );
        }

        if (balancePaise_ - amountPaise <
            minimumBalancePaise_) {
            throw AccountException("Insufficient funds.");
        }

        balancePaise_ -= amountPaise;
        record(TransactionType::Withdrawal, amountPaise);
    }

    void freeze() {
        if (status_ == AccountStatus::Closed) {
            throw AccountException(
                "Closed account cannot be frozen."
            );
        }

        status_ = AccountStatus::Frozen;
    }

    void unfreeze() {
        if (status_ != AccountStatus::Frozen) {
            throw AccountException(
                "Account is not frozen."
            );
        }

        status_ = AccountStatus::Active;
    }

    void close() {
        if (balancePaise_ != 0) {
            throw AccountException(
                "Account balance must be zero."
            );
        }

        status_ = AccountStatus::Closed;
    }

    // Virtual method supports runtime polymorphism.
    virtual std::string accountType() const {
        return "STANDARD";
    }

    virtual void display() const {
        std::cout
            << accountType()
            << " | "
            << accountNumber_
            << " | "
            << owner_
            << " | "
            << formatMoney(balancePaise_)
            << " | "
            << toString(status_)
            << '\n';
    }

    void transferTo(
        BankAccount& destination,
        std::int64_t amountPaise
    ) {
        ensureActive();
        destination.ensureActive();

        if (&destination == this) {
            throw std::invalid_argument(
                "Self-transfer is prohibited."
            );
        }

        if (amountPaise <= 0) {
            throw std::invalid_argument(
                "Transfer must be positive."
            );
        }

        if (balancePaise_ - amountPaise <
            minimumBalancePaise_) {
            throw AccountException(
                "Insufficient transfer balance."
            );
        }

        if (destination.balancePaise_ >
            INT64_MAX - amountPaise) {
            throw std::overflow_error(
                "Destination balance overflow."
            );
        }

        // Validate both accounts before committing changes.
        const auto sourceBefore = balancePaise_;
        const auto destinationBefore =
            destination.balancePaise_;

        const auto sourceHistorySize = history_.size();
        const auto destinationHistorySize =
            destination.history_.size();

        try {
            balancePaise_ -= amountPaise;
            destination.balancePaise_ += amountPaise;

            record(TransactionType::TransferOut, amountPaise);
            destination.record(
                TransactionType::TransferIn,
                amountPaise
            );
        } catch (...) {
            balancePaise_ = sourceBefore;
            destination.balancePaise_ = destinationBefore;

            history_.resize(sourceHistorySize);
            destination.history_.resize(destinationHistorySize);

            throw;
        }
    }
};

std::size_t BankAccount::accountCount_ = 0;


// ---------------------------------------------------------
// INHERITANCE AND METHOD OVERRIDING
// ---------------------------------------------------------

class SavingsAccount final : public BankAccount {
private:
    unsigned int interestBasisPoints_;

public:
    SavingsAccount(
        std::string accountNumber,
        std::string owner,
        std::int64_t initialBalancePaise,
        unsigned int interestBasisPoints
    )
        : BankAccount(
            std::move(accountNumber),
            std::move(owner),
            initialBalancePaise
        ),
          interestBasisPoints_(interestBasisPoints) {

        if (interestBasisPoints_ > 10000) {
            throw std::invalid_argument(
                "Interest rate cannot exceed 100 percent."
            );
        }
    }

    std::int64_t calculateInterest() const {
        // Basis points avoid floating-point interest calculations.
        return balancePaise() * interestBasisPoints_ / 10000;
    }

    void applyInterest() {
        const auto interest = calculateInterest();

        if (interest > 0) {
            deposit(interest);
        }
    }

    std::string accountType() const override {
        return "SAVINGS";
    }

    void display() const override {
        BankAccount::display();

        std::cout
            << "Interest rate: "
            << interestBasisPoints_ / 100.0
            << "%\n";
    }
};


// ---------------------------------------------------------
// POLYMORPHIC PROCESSING
// ---------------------------------------------------------

void printAccount(const BankAccount& account) {
    account.display();
}


// ---------------------------------------------------------
// MAIN
// ---------------------------------------------------------

int main() {
    try {
        std::cout << "ATTRIBUTES AND METHODS\n";
        std::cout << "======================\n\n";

        BankAccount current(
            "ACC1001",
            "Rahul Sharma",
            BankAccount::parseRupees("50000.00")
        );

        SavingsAccount savings(
            "ACC1002",
            "Priya Verma",
            BankAccount::parseRupees("75000.00"),
            500
        );

        std::cout << "Instance attributes:\n";
        std::cout << current.accountNumber() << '\n';
        std::cout << current.owner() << '\n';
        std::cout << BankAccount::formatMoney(
            current.balancePaise()
        ) << "\n\n";

        std::cout << "Class attributes:\n";
        std::cout << BankAccount::bankName << '\n';
        std::cout << "Account count: "
                  << BankAccount::accountCount() << "\n\n";

        std::cout << "Instance methods:\n";

        current.deposit(
            BankAccount::parseRupees("5000.00")
        );

        current.withdraw(
            BankAccount::parseRupees("2000.00")
        );

        std::cout << BankAccount::formatMoney(
            current.balancePaise()
        ) << "\n\n";

        std::cout << "Static methods:\n";

        BankAccount::changeBankName(
            "Enterprise Banking Group"
        );

        std::cout << BankAccount::bankName << '\n';

        std::cout << "\nInheritance and polymorphism:\n";

        std::vector<const BankAccount*> accounts = {
            &current,
            &savings
        };

        for (const auto* account : accounts) {
            printAccount(*account);
        }

        std::cout << "\nSpecialized methods:\n";

        savings.applyInterest();

        std::cout << BankAccount::formatMoney(
            savings.balancePaise()
        ) << "\n\n";

        std::cout << "Account transfer:\n";

        current.transferTo(
            savings,
            BankAccount::parseRupees("3000.00")
        );

        std::cout << "Source: "
                  << BankAccount::formatMoney(
                      current.balancePaise()
                  ) << '\n';

        std::cout << "Destination: "
                  << BankAccount::formatMoney(
                      savings.balancePaise()
                  ) << "\n\n";

        std::cout << "Exception handling:\n";

        try {
            current.withdraw(
                BankAccount::parseRupees("1000000.00")
            );
        } catch (const AccountException& error) {
            std::cout << error.what() << '\n';
        }

        try {
            current.deposit(0);
        } catch (const std::invalid_argument& error) {
            std::cout << error.what() << '\n';
        }

        std::cout << "\nState management:\n";

        current.freeze();

        try {
            current.deposit(100);
        } catch (const AccountException& error) {
            std::cout << error.what() << '\n';
        }

        current.unfreeze();

        assert(current.balancePaise() ==
               BankAccount::parseRupees("50000.00"));

        assert(savings.balancePaise() ==
               BankAccount::parseRupees("81125.00"));

        assert(current.status() == AccountStatus::Active);

        assert(current.history().size() == 3);

        std::cout << "\nAll assertions passed.\n";

        std::cout << "\nTransaction history:\n";

        for (const auto& transaction : current.history()) {
            std::cout
                << transaction.id
                << " | "
                << toString(transaction.type)
                << " | "
                << BankAccount::formatMoney(
                    transaction.amountPaise
                )
                << " | "
                << BankAccount::formatMoney(
                    transaction.balanceAfterPaise
                )
                << '\n';
        }

    } catch (const std::exception& error) {
        std::cerr << "Application error: "
                  << error.what()
                  << '\n';

        return 1;
    }

    return 0;
}
