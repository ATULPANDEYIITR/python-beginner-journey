#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum class AccountStatus {
    Active,
    Frozen,
    Closed
};

std::string statusName(AccountStatus status) {
    switch (status) {
        case AccountStatus::Active: return "ACTIVE";
        case AccountStatus::Frozen: return "FROZEN";
        case AccountStatus::Closed: return "CLOSED";
    }

    throw std::logic_error("Unknown account status.");
}

struct Transaction {
    int id;
    std::string type;
    double amount;
    double balanceAfter;
};

class Account {
private:
    static int nextId;
    static int totalAccounts;

    const int accountId;
    std::string owner;
    double balance;
    AccountStatus status;
    std::vector<Transaction> transactions;

protected:
    void ensureActive() const {
        if (status != AccountStatus::Active) {
            throw std::runtime_error("Account is not active.");
        }
    }

    void record(const std::string& type, double amount) {
        transactions.push_back({
            static_cast<int>(transactions.size()) + 1,
            type,
            amount,
            balance
        });
    }

    static double validateAmount(double amount) {
        if (!std::isfinite(amount) || amount <= 0) {
            throw std::invalid_argument(
                "Amount must be finite and positive."
            );
        }

        return std::round(amount * 100.0) / 100.0;
    }

public:
    Account(const std::string& ownerName, double openingBalance)
        : accountId(nextId++),
          owner(ownerName),
          balance(openingBalance),
          status(AccountStatus::Active) {

        if (owner.empty()) {
            throw std::invalid_argument("Owner cannot be empty.");
        }

        if (!std::isfinite(openingBalance) || openingBalance < 0) {
            throw std::invalid_argument("Invalid opening balance.");
        }

        ++totalAccounts;
    }

    virtual ~Account() = default;

    Account(const Account&) = delete;
    Account& operator=(const Account&) = delete;

    int getId() const {
        return accountId;
    }

    const std::string& getOwner() const {
        return owner;
    }

    double getBalance() const {
        return balance;
    }

    AccountStatus getStatus() const {
        return status;
    }

    const std::vector<Transaction>& getTransactions() const {
        return transactions;
    }

    static int getTotalAccounts() {
        return totalAccounts;
    }

    virtual double availableBalance() const = 0;

    virtual std::string accountType() const = 0;

    double deposit(double amount) {
        ensureActive();
        amount = validateAmount(amount);

        balance = std::round((balance + amount) * 100.0) / 100.0;
        record("DEPOSIT", amount);

        return balance;
    }

    double withdraw(double amount) {
        ensureActive();
        amount = validateAmount(amount);

        if (amount > availableBalance()) {
            throw std::runtime_error("Insufficient available balance.");
        }

        balance = std::round((balance - amount) * 100.0) / 100.0;
        record("WITHDRAWAL", amount);

        return balance;
    }

    void freeze() {
        ensureActive();
        status = AccountStatus::Frozen;
    }

    void unfreeze() {
        if (status != AccountStatus::Frozen) {
            throw std::runtime_error("Account is not frozen.");
        }

        status = AccountStatus::Active;
    }

    void close() {
        if (status == AccountStatus::Closed || balance != 0.0) {
            throw std::runtime_error(
                "Account must have zero balance before closing."
            );
        }

        status = AccountStatus::Closed;
    }

    void display() const {
        std::cout
            << std::left
            << std::setw(12) << accountType()
            << std::setw(8) << accountId
            << std::setw(20) << owner
            << std::setw(12) << std::fixed << std::setprecision(2)
            << balance
            << statusName(status)
            << '\n';
    }
};

int Account::nextId = 1000;
int Account::totalAccounts = 0;


class SavingsAccount final : public Account {
private:
    double minimumBalance;
    double interestRate;

public:
    SavingsAccount(
        const std::string& owner,
        double openingBalance,
        double minimum,
        double rate
    ) : Account(owner, openingBalance),
        minimumBalance(minimum),
        interestRate(rate) {

        if (!std::isfinite(minimum) || minimum < 0) {
            throw std::invalid_argument("Invalid minimum balance.");
        }

        if (!std::isfinite(rate) || rate < 0 || rate > 1) {
            throw std::invalid_argument("Invalid interest rate.");
        }
    }

    double availableBalance() const override {
        return std::max(0.0, getBalance() - minimumBalance);
    }

    std::string accountType() const override {
        return "SAVINGS";
    }

    double applyInterest() {
        ensureActive();

        const double interest =
            std::round(getBalance() * interestRate * 100.0) / 100.0;

        if (interest > 0) {
            deposit(interest);
        }

        return interest;
    }
};


class CurrentAccount final : public Account {
private:
    double overdraftLimit;

public:
    CurrentAccount(
        const std::string& owner,
        double openingBalance,
        double limit
    ) : Account(owner, openingBalance),
        overdraftLimit(limit) {

        if (!std::isfinite(limit) || limit < 0) {
            throw std::invalid_argument("Invalid overdraft limit.");
        }
    }

    double availableBalance() const override {
        return getBalance() + overdraftLimit;
    }

    std::string accountType() const override {
        return "CURRENT";
    }
};


class Bank {
private:
    std::string name;
    std::map<int, std::unique_ptr<Account>> accounts;

public:
    explicit Bank(std::string bankName)
        : name(std::move(bankName)) {

        if (name.empty()) {
            throw std::invalid_argument("Bank name is required.");
        }
    }

    void addAccount(std::unique_ptr<Account> account) {
        if (!account) {
            throw std::invalid_argument("Null account rejected.");
        }

        const int id = account->getId();

        auto result = accounts.emplace(id, std::move(account));

        if (!result.second) {
            throw std::runtime_error("Duplicate account.");
        }
    }

    Account& findAccount(int id) {
        auto it = accounts.find(id);

        if (it == accounts.end()) {
            throw std::out_of_range("Account not found.");
        }

        return *it->second;
    }

    void transfer(int sourceId, int destinationId, double amount) {
        if (sourceId == destinationId) {
            throw std::invalid_argument("Accounts must differ.");
        }

        Account& source = findAccount(sourceId);
        Account& destination = findAccount(destinationId);

        if (source.getStatus() != AccountStatus::Active ||
            destination.getStatus() != AccountStatus::Active) {
            throw std::runtime_error("Both accounts must be active.");
        }

        amount = Account::validateAmount(amount);

        if (amount > source.availableBalance()) {
            throw std::runtime_error("Insufficient funds.");
        }

        // Destination validation occurs before source modification.
        const double destinationBalance = destination.getBalance();

        try {
            source.withdraw(amount);
            destination.deposit(amount);
        } catch (...) {
            // Restore the source if destination processing fails.
            if (destination.getBalance() == destinationBalance) {
                source.deposit(amount);
            }
            throw;
        }
    }

    void displayAccounts() const {
        std::cout << "\nBank: " << name << "\n";

        std::cout
            << std::left
            << std::setw(12) << "TYPE"
            << std::setw(8) << "ID"
            << std::setw(20) << "OWNER"
            << std::setw(12) << "BALANCE"
            << "STATUS\n";

        for (const auto& entry : accounts) {
            entry.second->display();
        }
    }

    double totalBalance() const {
        double total = 0;

        for (const auto& entry : accounts) {
            total += entry.second->getBalance();
        }

        return std::round(total * 100.0) / 100.0;
    }
};


int main() {
    try {
        Bank bank("Enterprise Banking");

        auto savings = std::make_unique<SavingsAccount>(
            "Aarav Sharma", 25000, 1000, 0.05
        );

        auto current = std::make_unique<CurrentAccount>(
            "Meera Verma", 10000, 5000
        );

        const int savingsId = savings->getId();
        const int currentId = current->getId();

        SavingsAccount* savingsPointer = savings.get();

        bank.addAccount(std::move(savings));
        bank.addAccount(std::move(current));

        savingsPointer->deposit(5000);
        savingsPointer->applyInterest();

        bank.transfer(savingsId, currentId, 5000);

        // Runtime polymorphism through base-class references.
        std::vector<Account*> accountReferences = {
            savingsPointer,
            &bank.findAccount(currentId)
        };

        for (const Account* account : accountReferences) {
            std::cout
                << account->accountType()
                << " available: "
                << account->availableBalance()
                << '\n';
        }

        bank.displayAccounts();

        std::cout
            << "\nTotal accounts: "
            << Account::getTotalAccounts()
            << '\n';

        std::cout
            << "Total balance: "
            << bank.totalBalance()
            << '\n';

        try {
            bank.findAccount(savingsId).withdraw(100000);
        } catch (const std::exception& error) {
            std::cout << "Expected error: " << error.what() << '\n';
        }

        bank.findAccount(currentId).withdraw(15000);
        bank.findAccount(currentId).close();

        std::cout << "Account closure completed.\n";

    } catch (const std::exception& error) {
        std::cerr << "Application error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
