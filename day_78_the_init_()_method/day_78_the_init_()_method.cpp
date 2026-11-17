/*
 * THE __init__() METHOD
 *
 * C++17 does not use Python's __init__() method.
 * Object initialization is performed through constructors.
 *
 * Demonstrates:
 * - Default constructors
 * - Parameterized constructors
 * - Constructor initializer lists
 * - Delegating constructors
 * - Member initialization order
 * - const and reference members
 * - Constructor validation
 * - Inheritance and constructor chaining
 * - Composition
 * - Copy constructors
 * - Move constructors
 * - RAII
 * - Exception safety
 * - Object lifecycle
 */

#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// ==========================================================
// 1. BASIC CONSTRUCTOR
// ==========================================================

class Student {
private:
    std::string name_;
    int age_;

public:
    Student(const std::string& name, int age)
        : name_(name), age_(age) {

        if (name_.empty()) {
            throw std::invalid_argument("Student name is required.");
        }

        if (age_ < 0 || age_ > 120) {
            throw std::invalid_argument("Invalid student age.");
        }
    }

    void introduce() const {
        std::cout << name_ << ", age " << age_ << '\n';
    }

    const std::string& name() const {
        return name_;
    }

    int age() const {
        return age_;
    }
};

// ==========================================================
// 2. DEFAULT AND PARAMETERIZED CONSTRUCTORS
// ==========================================================

class Server {
private:
    std::string host_;
    int port_;
    bool secure_;

public:
    Server()
        : Server("localhost", 3000, false) {
    }

    Server(std::string host, int port, bool secure)
        : host_(std::move(host)),
          port_(port),
          secure_(secure) {

        if (host_.empty()) {
            throw std::invalid_argument("Host cannot be empty.");
        }

        if (port_ < 1 || port_ > 65535) {
            throw std::invalid_argument("Invalid port.");
        }
    }

    void display() const {
        std::cout
            << (secure_ ? "https://" : "http://")
            << host_ << ':' << port_ << '\n';
    }
};

// ==========================================================
// 3. MEMBER INITIALIZATION ORDER
// ==========================================================

class Measurement {
private:
    double value_;
    const std::string unit_;
    double converted_;

public:
    Measurement(double value, std::string unit)
        : value_(value),
          unit_(std::move(unit)),
          converted_(value_ * 1000.0) {

        if (!std::isfinite(value_) || unit_.empty()) {
            throw std::invalid_argument("Invalid measurement.");
        }
    }

    void display() const {
        std::cout << value_ << ' ' << unit_
                  << ", converted: " << converted_ << '\n';
    }
};

// ==========================================================
// 4. REFERENCE MEMBERS AND INITIALIZATION
// ==========================================================

class Logger {
private:
    std::ostream& output_;

public:
    explicit Logger(std::ostream& output)
        : output_(output) {
    }

    void log(const std::string& message) const {
        output_ << "[LOG] " << message << '\n';
    }
};

// ==========================================================
// 5. VALIDATED BANK ACCOUNT
// ==========================================================

enum class AccountStatus {
    Active,
    Suspended,
    Closed
};

class BankAccount {
private:
    std::string accountNumber_;
    std::string owner_;
    double balance_;
    AccountStatus status_;

public:
    BankAccount(
        std::string accountNumber,
        std::string owner,
        double initialBalance = 0.0
    )
        : accountNumber_(std::move(accountNumber)),
          owner_(std::move(owner)),
          balance_(initialBalance),
          status_(AccountStatus::Active) {

        if (accountNumber_.empty() || owner_.empty()) {
            throw std::invalid_argument("Account details are required.");
        }

        if (!std::isfinite(balance_) || balance_ < 0) {
            throw std::invalid_argument("Invalid initial balance.");
        }
    }

    void deposit(double amount) {
        if (status_ != AccountStatus::Active) {
            throw std::logic_error("Account is not active.");
        }

        if (!std::isfinite(amount) || amount <= 0) {
            throw std::invalid_argument("Invalid deposit.");
        }

        balance_ += amount;
    }

    void suspend() {
        if (status_ == AccountStatus::Closed) {
            throw std::logic_error("Closed account cannot be suspended.");
        }

        status_ = AccountStatus::Suspended;
    }

    double balance() const {
        return balance_;
    }

    AccountStatus status() const {
        return status_;
    }
};

// ==========================================================
// 6. INHERITANCE AND BASE CONSTRUCTOR INITIALIZATION
// ==========================================================

class Employee {
protected:
    std::string name_;
    std::string employeeId_;

public:
    Employee(std::string name, std::string employeeId)
        : name_(std::move(name)),
          employeeId_(std::move(employeeId)) {

        if (name_.empty() || employeeId_.empty()) {
            throw std::invalid_argument("Invalid employee details.");
        }
    }

    virtual ~Employee() = default;

    virtual void display() const {
        std::cout << name_ << " [" << employeeId_ << "]\n";
    }
};

class Manager : public Employee {
private:
    int teamSize_;

public:
    Manager(
        std::string name,
        std::string employeeId,
        int teamSize
    )
        : Employee(std::move(name), std::move(employeeId)),
          teamSize_(teamSize) {

        if (teamSize_ < 0) {
            throw std::invalid_argument("Invalid team size.");
        }
    }

    void display() const override {
        Employee::display();
        std::cout << "Team size: " << teamSize_ << '\n';
    }
};

// ==========================================================
// 7. COMPOSITION
// ==========================================================

class Address {
private:
    std::string city_;
    std::string country_;

public:
    Address(std::string city, std::string country)
        : city_(std::move(city)),
          country_(std::move(country)) {

        if (city_.empty() || country_.empty()) {
            throw std::invalid_argument("Address is incomplete.");
        }
    }

    void display() const {
        std::cout << city_ << ", " << country_ << '\n';
    }
};

class Organization {
private:
    std::string name_;
    Address address_;

public:
    Organization(std::string name, Address address)
        : name_(std::move(name)),
          address_(std::move(address)) {

        if (name_.empty()) {
            throw std::invalid_argument("Organization name is required.");
        }
    }

    void display() const {
        std::cout << name_ << '\n';
        address_.display();
    }
};

// ==========================================================
// 8. COPY AND MOVE CONSTRUCTORS
// ==========================================================

class Document {
private:
    std::string title_;
    std::vector<std::string> sections_;

public:
    Document(
        std::string title,
        std::vector<std::string> sections
    )
        : title_(std::move(title)),
          sections_(std::move(sections)) {

        if (title_.empty()) {
            throw std::invalid_argument("Document title is required.");
        }
    }

    // Copy constructor creates independent document storage.
    Document(const Document& other)
        : title_(other.title_),
          sections_(other.sections_) {
    }

    // Move constructor transfers resources.
    Document(Document&& other) noexcept
        : title_(std::move(other.title_)),
          sections_(std::move(other.sections_)) {
    }

    Document& operator=(const Document&) = default;
    Document& operator=(Document&&) noexcept = default;

    void addSection(std::string section) {
        if (section.empty()) {
            throw std::invalid_argument("Section cannot be empty.");
        }

        sections_.push_back(std::move(section));
    }

    std::size_t sectionCount() const {
        return sections_.size();
    }

    void display() const {
        std::cout << title_ << " | Sections: "
                  << sections_.size() << '\n';
    }
};

// ==========================================================
// 9. RAII AND RESOURCE MANAGEMENT
// ==========================================================

class Resource {
private:
    std::string name_;
    bool acquired_;

public:
    explicit Resource(std::string name)
        : name_(std::move(name)), acquired_(true) {

        if (name_.empty()) {
            throw std::invalid_argument("Resource name is required.");
        }

        std::cout << "Acquired: " << name_ << '\n';
    }

    ~Resource() {
        if (acquired_) {
            std::cout << "Released: " << name_ << '\n';
        }
    }

    Resource(const Resource&) = delete;
    Resource& operator=(const Resource&) = delete;
};

// ==========================================================
// 10. CONSTRUCTOR FAILURE AND OBJECT FACTORY
// ==========================================================

class Deployment {
private:
    std::string application_;
    std::string environment_;
    std::string version_;

    Deployment(
        std::string application,
        std::string environment,
        std::string version
    )
        : application_(std::move(application)),
          environment_(std::move(environment)),
          version_(std::move(version)) {
    }

public:
    static std::unique_ptr<Deployment> create(
        std::string application,
        std::string environment,
        std::string version
    ) {
        if (application.empty() || version.empty()) {
            throw std::invalid_argument("Deployment details are required.");
        }

        const std::vector<std::string> allowed = {
            "development", "testing", "production"
        };

        if (std::find(
            allowed.begin(),
            allowed.end(),
            environment
        ) == allowed.end()) {
            throw std::invalid_argument("Unsupported environment.");
        }

        return std::unique_ptr<Deployment>(
            new Deployment(
                std::move(application),
                std::move(environment),
                std::move(version)
            )
        );
    }

    void display() const {
        std::cout << application_ << " | "
                  << environment_ << " | "
                  << version_ << '\n';
    }
};

// ==========================================================
// 11. EXECUTABLE TESTS
// ==========================================================

int main() {
    try {
        std::cout << "\n1. Basic constructor\n";

        Student student("Atul", 25);
        student.introduce();

        std::cout << "\n2. Delegating constructor\n";

        Server defaultServer;
        Server productionServer("example.com", 443, true);

        defaultServer.display();
        productionServer.display();

        std::cout << "\n3. Member initialization list\n";

        Measurement measurement(5.5, "meters");
        measurement.display();

        std::cout << "\n4. Reference member\n";

        Logger logger(std::cout);
        logger.log("Application initialized.");

        std::cout << "\n5. Validated account\n";

        BankAccount account("ACC-1001", "Atul", 5000);
        account.deposit(1500);

        assert(account.balance() == 6500);
        std::cout << "Balance: " << account.balance() << '\n';

        std::cout << "\n6. Inheritance\n";

        Manager manager("Anita", "EMP-101", 8);
        manager.display();

        std::cout << "\n7. Composition\n";

        Organization organization(
            "Research Laboratory",
            Address("Lucknow", "India")
        );

        organization.display();

        std::cout << "\n8. Copy and move construction\n";

        Document original("Research Report", {"Introduction", "Methods"});

        Document copied(original);
        Document moved(std::move(copied));

        moved.addSection("Results");

        original.display();
        moved.display();

        assert(original.sectionCount() == 2);
        assert(moved.sectionCount() == 3);

        std::cout << "\n9. RAII\n";

        {
            Resource resource("Database Connection");
            logger.log("Resource is active.");
        }

        std::cout << "\n10. Validated factory\n";

        auto deployment = Deployment::create(
            "Risk Engine",
            "production",
            "2.1.0"
        );

        deployment->display();

        std::cout << "\n11. Invalid constructor inputs\n";

        int rejected = 0;

        try {
            Student invalid("", 20);
        } catch (const std::invalid_argument& error) {
            ++rejected;
            std::cout << error.what() << '\n';
        }

        try {
            BankAccount invalid("ACC-2", "User", -100);
        } catch (const std::invalid_argument& error) {
            ++rejected;
            std::cout << error.what() << '\n';
        }

        try {
            Server invalid("localhost", 70000, false);
        } catch (const std::invalid_argument& error) {
            ++rejected;
            std::cout << error.what() << '\n';
        }

        try {
            auto invalid = Deployment::create(
                "Risk Engine",
                "unknown",
                "1.0"
            );
        } catch (const std::invalid_argument& error) {
            ++rejected;
            std::cout << error.what() << '\n';
        }

        assert(rejected == 4);

        std::cout << "\nAll C++17 tests passed.\n";

    } catch (const std::exception& error) {
        std::cerr << "Execution failed: "
                  << error.what() << '\n';

        return 1;
    }

    return 0;
}
