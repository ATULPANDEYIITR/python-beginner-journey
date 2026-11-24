#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

/*
 * C++17 INHERITANCE
 *
 * Repository-independent employee payroll engine.
 *
 * Demonstrates:
 * - Base classes
 * - Derived classes
 * - Public inheritance
 * - Multilevel inheritance
 * - Hierarchical inheritance
 * - Multiple inheritance
 * - Virtual functions
 * - Pure virtual functions
 * - Function overriding
 * - Runtime polymorphism
 * - Virtual destructors
 * - Abstract classes
 * - Interface-style inheritance
 * - Composition
 * - Smart pointers
 * - Exception safety
 */

enum class EmploymentType {
    Permanent,
    Contract,
    Intern
};

class PayrollError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class ValidationError : public PayrollError {
public:
    using PayrollError::PayrollError;
};

class Employee {
private:
    int id_;
    std::string name_;
    std::string department_;
    bool active_ = true;

protected:
    static void validateMoney(double amount) {
        if (!std::isfinite(amount) || amount < 0) {
            throw ValidationError(
                "Money must be finite and non-negative."
            );
        }
    }

public:
    Employee(
        int id,
        std::string name,
        std::string department
    )
        : id_(id),
          name_(std::move(name)),
          department_(std::move(department)) {

        if (id_ <= 0) {
            throw ValidationError("Invalid employee ID.");
        }

        if (name_.empty() || department_.empty()) {
            throw ValidationError(
                "Name and department are required."
            );
        }
    }

    // Virtual destructor ensures correct destruction
    // when a derived object is deleted through a base pointer.
    virtual ~Employee() = default;

    Employee(const Employee&) = default;
    Employee& operator=(const Employee&) = default;

    virtual double calculateSalary() const = 0;

    virtual std::string employmentType() const = 0;

    virtual void display() const {
        std::cout
            << std::left
            << std::setw(12) << id_
            << std::setw(18) << name_
            << std::setw(16) << department_
            << std::setw(14) << employmentType()
            << std::fixed << std::setprecision(2)
            << calculateSalary()
            << '\n';
    }

    int id() const {
        return id_;
    }

    const std::string& name() const {
        return name_;
    }

    const std::string& department() const {
        return department_;
    }

    bool active() const {
        return active_;
    }

    void deactivate() {
        active_ = false;
    }
};

// Single inheritance
class PermanentEmployee : public Employee {
protected:
    double monthlySalary_;
    double annualBonus_;

public:
    PermanentEmployee(
        int id,
        std::string name,
        std::string department,
        double salary,
        double bonus
    )
        : Employee(id, std::move(name), std::move(department)),
          monthlySalary_(salary),
          annualBonus_(bonus) {

        validateMoney(salary);
        validateMoney(bonus);
    }

    double calculateSalary() const override {
        return monthlySalary_ + annualBonus_ / 12.0;
    }

    std::string employmentType() const override {
        return "Permanent";
    }
};

// Multilevel inheritance
class SeniorEmployee : public PermanentEmployee {
protected:
    double leadershipAllowance_;

public:
    SeniorEmployee(
        int id,
        std::string name,
        std::string department,
        double salary,
        double bonus,
        double allowance
    )
        : PermanentEmployee(
            id,
            std::move(name),
            std::move(department),
            salary,
            bonus
        ),
          leadershipAllowance_(allowance) {

        validateMoney(allowance);
    }

    double calculateSalary() const override {
        return PermanentEmployee::calculateSalary()
            + leadershipAllowance_;
    }

    std::string employmentType() const override {
        return "Senior";
    }
};

// Hierarchical inheritance
class ContractEmployee : public Employee {
private:
    double hourlyRate_;
    double hours_;

public:
    ContractEmployee(
        int id,
        std::string name,
        std::string department,
        double hourlyRate,
        double hours
    )
        : Employee(id, std::move(name), std::move(department)),
          hourlyRate_(hourlyRate),
          hours_(hours) {

        validateMoney(hourlyRate);
        validateMoney(hours);

        if (hours > 744) {
            throw ValidationError("Monthly hours exceed limit.");
        }
    }

    double calculateSalary() const override {
        return hourlyRate_ * hours_;
    }

    std::string employmentType() const override {
        return "Contract";
    }
};

class InternEmployee : public Employee {
private:
    double stipend_;

public:
    InternEmployee(
        int id,
        std::string name,
        std::string department,
        double stipend
    )
        : Employee(id, std::move(name), std::move(department)),
          stipend_(stipend) {

        validateMoney(stipend);
    }

    double calculateSalary() const override {
        return stipend_;
    }

    std::string employmentType() const override {
        return "Intern";
    }
};

// Interface-style abstract class.
class Taxable {
public:
    virtual ~Taxable() = default;

    virtual double calculateTax(double rate) const = 0;
};

// Multiple inheritance
class TaxablePermanentEmployee final
    : public PermanentEmployee,
      public Taxable {

public:
    using PermanentEmployee::PermanentEmployee;

    double calculateTax(double rate) const override {
        if (!std::isfinite(rate) || rate < 0 || rate > 1) {
            throw ValidationError("Invalid tax rate.");
        }

        return calculateSalary() * rate;
    }

    double netSalary(double rate) const {
        return calculateSalary() - calculateTax(rate);
    }
};

// Composition
class PayrollPolicy {
private:
    double deductionRate_;

public:
    explicit PayrollPolicy(double rate)
        : deductionRate_(rate) {

        if (!std::isfinite(rate) || rate < 0 || rate > 1) {
            throw ValidationError("Invalid deduction rate.");
        }
    }

    double calculateNet(double gross) const {
        if (!std::isfinite(gross) || gross < 0) {
            throw ValidationError("Invalid gross salary.");
        }

        return gross * (1.0 - deductionRate_);
    }
};

class PayrollEngine {
private:
    PayrollPolicy policy_;

    // Unique ownership prevents memory leaks.
    std::vector<std::unique_ptr<Employee>> employees_;

    std::unordered_map<int, Employee*> index_;

public:
    explicit PayrollEngine(PayrollPolicy policy)
        : policy_(std::move(policy)) {}

    void registerEmployee(
        std::unique_ptr<Employee> employee
    ) {
        if (!employee) {
            throw ValidationError("Null employee.");
        }

        if (index_.count(employee->id())) {
            throw ValidationError("Duplicate employee ID.");
        }

        int id = employee->id();
        Employee* raw = employee.get();

        employees_.push_back(std::move(employee));
        index_.emplace(id, raw);
    }

    Employee& findEmployee(int id) const {
        auto it = index_.find(id);

        if (it == index_.end()) {
            throw PayrollError("Employee not found.");
        }

        return *it->second;
    }

    void printPayroll() const {
        std::cout
            << "\n=== PAYROLL REPORT ===\n";

        std::cout
            << std::left
            << std::setw(12) << "ID"
            << std::setw(18) << "NAME"
            << std::setw(16) << "DEPARTMENT"
            << std::setw(14) << "TYPE"
            << "GROSS\n";

        double total = 0;

        for (const auto& employee : employees_) {
            if (!employee->active()) {
                continue;
            }

            employee->display();

            total += employee->calculateSalary();
        }

        std::cout << "\nTotal gross payroll: "
                  << std::fixed << std::setprecision(2)
                  << total << '\n';

        std::cout << "Estimated net payroll: "
                  << policy_.calculateNet(total) << '\n';
    }

    std::unordered_map<std::string, double>
    departmentTotals() const {
        std::unordered_map<std::string, double> totals;

        for (const auto& employee : employees_) {
            if (!employee->active()) {
                continue;
            }

            totals[employee->department()] +=
                employee->calculateSalary();
        }

        return totals;
    }

    void deactivate(int id) {
        findEmployee(id).deactivate();
    }
};

int main() {
    try {
        PayrollEngine engine(PayrollPolicy(0.12));

        engine.registerEmployee(
            std::make_unique<PermanentEmployee>(
                101, "Aarav", "Engineering",
                70000, 120000
            )
        );

        engine.registerEmployee(
            std::make_unique<SeniorEmployee>(
                102, "Meera", "Engineering",
                100000, 240000, 15000
            )
        );

        engine.registerEmployee(
            std::make_unique<ContractEmployee>(
                103, "Rohan", "Operations",
                800, 160
            )
        );

        engine.registerEmployee(
            std::make_unique<InternEmployee>(
                104, "Priya", "Research",
                25000
            )
        );

        auto taxable = std::make_unique<TaxablePermanentEmployee>(
            105, "Ananya", "Finance",
            85000, 60000
        );

        std::cout
            << "Taxable employee net salary: "
            << taxable->netSalary(0.10)
            << '\n';

        engine.registerEmployee(std::move(taxable));

        engine.printPayroll();

        std::cout << "\n=== DEPARTMENT TOTALS ===\n";

        for (const auto& [department, total] :
             engine.departmentTotals()) {
            std::cout << department << ": " << total << '\n';
        }

        std::cout << "\n=== RUNTIME POLYMORPHISM ===\n";

        Employee& employee = engine.findEmployee(102);

        std::cout
            << employee.name()
            << " earns "
            << employee.calculateSalary()
            << '\n';

        engine.deactivate(104);

        std::cout << "\n=== AFTER DEACTIVATION ===\n";
        engine.printPayroll();

        std::cout << "\n=== ERROR HANDLING ===\n";

        try {
            engine.findEmployee(999);
        } catch (const PayrollError& error) {
            std::cout << error.what() << '\n';
        }

        try {
            PermanentEmployee invalid(
                110, "Invalid", "IT", -1000, 0
            );
        } catch (const ValidationError& error) {
            std::cout << error.what() << '\n';
        }

        std::cout << "\nAll C++17 operations completed.\n";

    } catch (const std::exception& error) {
        std::cerr << "Fatal error: "
                  << error.what() << '\n';

        return 1;
    }

    return 0;
}
