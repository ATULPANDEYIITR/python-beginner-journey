#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

class ValidationError : public runtime_error {
public:
    explicit ValidationError(const string& message)
        : runtime_error(message) {}
};

// 1. Encapsulated property using getter and setter
class Temperature {
private:
    double celsius_;

public:
    explicit Temperature(double value) {
        setCelsius(value);
    }

    double getCelsius() const {
        return celsius_;
    }

    void setCelsius(double value) {
        if (!isfinite(value) || value < -273.15 || value > 1000) {
            throw ValidationError("Invalid Celsius temperature.");
        }
        celsius_ = value;
    }

    double getFahrenheit() const {
        return celsius_ * 9.0 / 5.0 + 32.0;
    }

    void setFahrenheit(double value) {
        if (!isfinite(value)) {
            throw ValidationError("Invalid Fahrenheit temperature.");
        }
        setCelsius((value - 32.0) * 5.0 / 9.0);
    }
};

// 2. Read-only property
class Employee {
private:
    const int employeeId_;
    string name_;

public:
    Employee(int id, string name)
        : employeeId_(id), name_(move(name)) {
        if (id <= 0 || name_.empty()) {
            throw ValidationError("Invalid employee.");
        }
    }

    int getEmployeeId() const {
        return employeeId_;
    }

    const string& getName() const {
        return name_;
    }
};

// 3. Computed properties
class Rectangle {
private:
    double width_;
    double height_;

public:
    Rectangle(double width, double height)
        : width_(0), height_(0) {
        setWidth(width);
        setHeight(height);
    }

    void setWidth(double value) {
        if (!isfinite(value) || value <= 0) {
            throw ValidationError("Width must be positive.");
        }
        width_ = value;
    }

    void setHeight(double value) {
        if (!isfinite(value) || value <= 0) {
            throw ValidationError("Height must be positive.");
        }
        height_ = value;
    }

    double getWidth() const {
        return width_;
    }

    double getHeight() const {
        return height_;
    }

    double getArea() const {
        return width_ * height_;
    }

    double getPerimeter() const {
        return 2 * (width_ + height_);
    }
};

// 4. Inventory with cached computed property
class Inventory {
private:
    map<string, int> quantities_;
    long long cachedTotal_ = 0;
    bool dirty_ = true;
    size_t calculationCount_ = 0;

public:
    void setQuantity(const string& product, int quantity) {
        if (product.empty() || quantity < 0) {
            throw ValidationError("Invalid inventory entry.");
        }

        quantities_[product] = quantity;
        dirty_ = true;
    }

    long long getTotalUnits() {
        if (dirty_) {
            cachedTotal_ = 0;

            for (const auto& entry : quantities_) {
                cachedTotal_ += entry.second;
            }

            dirty_ = false;
            ++calculationCount_;
        }

        return cachedTotal_;
    }

    size_t getCalculationCount() const {
        return calculationCount_;
    }
};

// 5. Financial account with controlled state
class BankAccount {
private:
    string accountNumber_;
    double balance_;

public:
    BankAccount(string accountNumber, double openingBalance)
        : accountNumber_(move(accountNumber)), balance_(0) {
        if (accountNumber_.size() < 6 ||
            accountNumber_.size() > 20 ||
            !all_of(accountNumber_.begin(), accountNumber_.end(),
                [](unsigned char c) {
                    return isalnum(c);
                })) {
            throw ValidationError("Invalid account number.");
        }

        setBalance(openingBalance);
    }

    double getBalance() const {
        return balance_;
    }

    void setBalance(double value) {
        if (!isfinite(value) || value < 0) {
            throw ValidationError("Balance cannot be negative.");
        }
        balance_ = value;
    }

    void deposit(double amount) {
        if (!isfinite(amount) || amount <= 0 ||
            balance_ > 1e15 - amount) {
            throw ValidationError("Invalid deposit.");
        }

        balance_ += amount;
    }

    void withdraw(double amount) {
        if (!isfinite(amount) || amount <= 0) {
            throw ValidationError("Invalid withdrawal.");
        }

        if (amount > balance_) {
            throw ValidationError("Insufficient funds.");
        }

        balance_ -= amount;
    }
};

// 6. Property-style pricing model
class Product {
protected:
    string name_;
    double price_;

public:
    Product(string name, double price)
        : name_(move(name)), price_(0) {
        if (name_.empty()) {
            throw ValidationError("Product name cannot be empty.");
        }
        setPrice(price);
    }

    void setPrice(double value) {
        if (!isfinite(value) || value < 0) {
            throw ValidationError("Invalid price.");
        }
        price_ = value;
    }

    double getPrice() const {
        return price_;
    }

    virtual double getFinalPrice() const {
        return price_;
    }

    virtual ~Product() = default;
};

class DiscountedProduct : public Product {
private:
    double discount_;

public:
    DiscountedProduct(string name, double price, double discount)
        : Product(move(name), price), discount_(0) {
        setDiscount(discount);
    }

    void setDiscount(double value) {
        if (!isfinite(value) || value < 0 || value > 100) {
            throw ValidationError("Invalid discount.");
        }
        discount_ = value;
    }

    double getDiscount() const {
        return discount_;
    }

    double getFinalPrice() const override {
        return price_ * (1.0 - discount_ / 100.0);
    }
};

// 7. Property-oriented employee configuration
enum class EmploymentStatus {
    Active,
    Suspended,
    Terminated
};

class EmployeeRecord {
private:
    string name_;
    double salary_;
    EmploymentStatus status_;

public:
    EmployeeRecord(string name, double salary)
        : name_(move(name)), salary_(0),
          status_(EmploymentStatus::Active) {
        setSalary(salary);
        if (name_.empty()) {
            throw ValidationError("Name cannot be empty.");
        }
    }

    double getSalary() const {
        return salary_;
    }

    void setSalary(double value) {
        if (!isfinite(value) || value < 0 || value > 1e9) {
            throw ValidationError("Invalid salary.");
        }
        salary_ = value;
    }

    EmploymentStatus getStatus() const {
        return status_;
    }

    void setStatus(EmploymentStatus status) {
        if (status_ == EmploymentStatus::Terminated &&
            status != EmploymentStatus::Terminated) {
            throw ValidationError("Terminated employees cannot be reactivated.");
        }
        status_ = status;
    }
};

void demonstrate() {
    cout << fixed << setprecision(2);

    Temperature temperature(25);
    cout << "Celsius: " << temperature.getCelsius() << '\n';
    cout << "Fahrenheit: " << temperature.getFahrenheit() << '\n';

    temperature.setFahrenheit(32);
    cout << "Updated Celsius: " << temperature.getCelsius() << '\n';

    Employee employee(101, "Asha");
    cout << "Employee ID: " << employee.getEmployeeId() << '\n';

    Rectangle rectangle(10, 5);
    cout << "Area: " << rectangle.getArea() << '\n';
    cout << "Perimeter: " << rectangle.getPerimeter() << '\n';

    Inventory inventory;
    inventory.setQuantity("Laptop", 10);
    inventory.setQuantity("Keyboard", 20);

    cout << "Inventory units: " << inventory.getTotalUnits() << '\n';
    cout << "Cached inventory units: " << inventory.getTotalUnits() << '\n';
    cout << "Calculations: " << inventory.getCalculationCount() << '\n';

    inventory.setQuantity("Mouse", 15);
    cout << "Updated inventory: " << inventory.getTotalUnits() << '\n';

    BankAccount account("BANK1234", 5000);
    account.deposit(1000);
    account.withdraw(1500);
    cout << "Account balance: " << account.getBalance() << '\n';

    DiscountedProduct product("Laptop", 1000, 15);
    cout << "Original price: " << product.getPrice() << '\n';
    cout << "Final price: " << product.getFinalPrice() << '\n';

    EmployeeRecord record("Asha", 75000);
    record.setSalary(80000);
    cout << "Updated salary: " << record.getSalary() << '\n';
}

int main() {
    try {
        demonstrate();

        cout << "\nValidation tests:\n";

        try {
            Temperature invalid(-300);
        } catch (const ValidationError& error) {
            cout << "Temperature rejected: " << error.what() << '\n';
        }

        try {
            BankAccount account("BANK1234", 100);
            account.withdraw(200);
        } catch (const ValidationError& error) {
            cout << "Transaction rejected: " << error.what() << '\n';
        }

        try {
            Rectangle invalid(0, 5);
        } catch (const ValidationError& error) {
            cout << "Rectangle rejected: " << error.what() << '\n';
        }

    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
