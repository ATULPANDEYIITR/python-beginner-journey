"use strict";

/*
 * JAVASCRIPT INHERITANCE
 *
 * Employee payroll and event-driven processing.
 *
 * Demonstrates:
 * - ES6 classes
 * - extends and super
 * - Method overriding
 * - Prototype chains
 * - Static methods
 * - Getters
 * - Private class fields
 * - Multiple inheritance alternatives through mixins
 * - Polymorphism
 * - Composition
 * - Event-driven programming
 * - Async processing
 * - Promise-based error handling
 * - Runtime validation
 */

const EmploymentType = Object.freeze({
    PERMANENT: "PERMANENT",
    CONTRACT: "CONTRACT",
    INTERN: "INTERN"
});

class PayrollError extends Error {
    constructor(message) {
        super(message);
        this.name = "PayrollError";
    }
}

class ValidationError extends PayrollError {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class EmployeeNotFoundError extends PayrollError {
    constructor(id) {
        super(`Employee ${id} was not found.`);
        this.name = "EmployeeNotFoundError";
    }
}

function validateMoney(value, field) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value) ||
        value < 0
    ) {
        throw new ValidationError(
            `${field} must be a non-negative finite number.`
        );
    }
}

function validateEmployeeId(id) {
    if (!Number.isSafeInteger(id) || id <= 0) {
        throw new ValidationError("Invalid employee ID.");
    }
}

class Employee {
    #active = true;

    constructor(id, name, department, employmentType) {
        validateEmployeeId(id);

        if (typeof name !== "string" || !name.trim()) {
            throw new ValidationError("Employee name is required.");
        }

        if (
            typeof department !== "string" ||
            !department.trim()
        ) {
            throw new ValidationError("Department is required.");
        }

        if (!Object.values(EmploymentType).includes(employmentType)) {
            throw new ValidationError("Invalid employment type.");
        }

        this.id = id;
        this.name = name.trim();
        this.department = department.trim();
        this.employmentType = employmentType;
    }

    get active() {
        return this.#active;
    }

    deactivate() {
        this.#active = false;
    }

    calculateSalary() {
        throw new Error(
            "calculateSalary() must be implemented by a subclass."
        );
    }

    getDetails() {
        return Object.freeze({
            id: this.id,
            name: this.name,
            department: this.department,
            salary: this.calculateSalary(),
            active: this.active
        });
    }

    static isEmployee(value) {
        return value instanceof Employee;
    }
}

// Single inheritance
class PermanentEmployee extends Employee {
    constructor(id, name, department, salary, bonus = 0) {
        super(id, name, department, EmploymentType.PERMANENT);

        validateMoney(salary, "Monthly salary");
        validateMoney(bonus, "Annual bonus");

        this.monthlySalary = salary;
        this.annualBonus = bonus;
    }

    calculateSalary() {
        return this.monthlySalary + this.annualBonus / 12;
    }
}

// Multilevel inheritance
class SeniorEmployee extends PermanentEmployee {
    constructor(
        id,
        name,
        department,
        salary,
        bonus,
        allowance
    ) {
        super(id, name, department, salary, bonus);

        validateMoney(allowance, "Leadership allowance");

        this.allowance = allowance;
    }

    calculateSalary() {
        return super.calculateSalary() + this.allowance;
    }
}

// Hierarchical inheritance
class ContractEmployee extends Employee {
    constructor(id, name, department, hourlyRate, hours) {
        super(id, name, department, EmploymentType.CONTRACT);

        validateMoney(hourlyRate, "Hourly rate");
        validateMoney(hours, "Working hours");

        if (hours > 744) {
            throw new ValidationError("Monthly hours exceed limit.");
        }

        this.hourlyRate = hourlyRate;
        this.hours = hours;
    }

    calculateSalary() {
        return this.hourlyRate * this.hours;
    }
}

class InternEmployee extends Employee {
    constructor(id, name, department, stipend) {
        super(id, name, department, EmploymentType.INTERN);

        validateMoney(stipend, "Monthly stipend");

        this.stipend = stipend;
    }

    calculateSalary() {
        return this.stipend;
    }
}

// JavaScript has single class inheritance.
// Mixins provide reusable behavior without another superclass.
const TaxableMixin = Base => class extends Base {
    calculateTax(rate = 0.10) {
        if (rate < 0 || rate > 1 || !Number.isFinite(rate)) {
            throw new ValidationError("Invalid tax rate.");
        }

        return this.calculateSalary() * rate;
    }

    calculateNetSalary(rate = 0.10) {
        return this.calculateSalary() - this.calculateTax(rate);
    }
};

const AuditableMixin = Base => class extends Base {
    audit() {
        return Object.freeze({
            id: this.id,
            className: this.constructor.name,
            prototype: Object.getPrototypeOf(this).constructor.name
        });
    }
};

class TaxablePermanentEmployee extends
    AuditableMixin(TaxableMixin(PermanentEmployee)) {
    constructor(id, name, department, salary, bonus) {
        super(id, name, department, salary, bonus);
    }
}

// Composition: payroll rules are separate from employee classes.
class PayrollPolicy {
    constructor(deductionRate = 0.12) {
        if (
            !Number.isFinite(deductionRate) ||
            deductionRate < 0 ||
            deductionRate > 1
        ) {
            throw new ValidationError("Invalid deduction rate.");
        }

        this.deductionRate = deductionRate;
    }

    calculateNet(gross) {
        validateMoney(gross, "Gross salary");

        return gross * (1 - this.deductionRate);
    }
}

// Event-driven payroll service.
class PayrollService extends EventTarget {
    #employees = new Map();

    constructor(policy) {
        super();

        if (!(policy instanceof PayrollPolicy)) {
            throw new ValidationError("A payroll policy is required.");
        }

        this.policy = policy;
    }

    register(employee) {
        if (!Employee.isEmployee(employee)) {
            throw new ValidationError("Invalid employee object.");
        }

        if (this.#employees.has(employee.id)) {
            throw new ValidationError("Duplicate employee ID.");
        }

        this.#employees.set(employee.id, employee);

        this.dispatchEvent(
            new CustomEvent("employeeRegistered", {
                detail: employee.getDetails()
            })
        );
    }

    getEmployee(id) {
        const employee = this.#employees.get(id);

        if (!employee) {
            throw new EmployeeNotFoundError(id);
        }

        return employee;
    }

    async processEmployee(employee) {
        // Yielding allows independent payroll tasks to be scheduled.
        await Promise.resolve();

        const gross = employee.calculateSalary();

        if (!Number.isFinite(gross)) {
            throw new PayrollError("Invalid salary calculation.");
        }

        return {
            id: employee.id,
            name: employee.name,
            gross,
            net: this.policy.calculateNet(gross)
        };
    }

    async processPayroll() {
        const activeEmployees = [
            ...this.#employees.values()
        ].filter(employee => employee.active);

        const results = await Promise.all(
            activeEmployees.map(employee =>
                this.processEmployee(employee)
            )
        );

        this.dispatchEvent(
            new CustomEvent("payrollProcessed", {
                detail: {
                    employeeCount: results.length,
                    results
                }
            })
        );

        return results;
    }

    departmentTotals() {
        const totals = new Map();

        for (const employee of this.#employees.values()) {
            if (!employee.active) continue;

            const previous = totals.get(employee.department) ?? 0;

            totals.set(
                employee.department,
                previous + employee.calculateSalary()
            );
        }

        return Object.fromEntries(totals);
    }
}

async function main() {
    const service = new PayrollService(
        new PayrollPolicy(0.12)
    );

    service.addEventListener("employeeRegistered", event => {
        console.log(
            "Registered:",
            event.detail.name
        );
    });

    service.addEventListener("payrollProcessed", event => {
        console.log(
            "Payroll processed:",
            event.detail.employeeCount
        );
    });

    const employees = [
        new PermanentEmployee(
            101, "Aarav", "Engineering", 70000, 120000
        ),

        new SeniorEmployee(
            102, "Meera", "Engineering",
            100000, 240000, 15000
        ),

        new ContractEmployee(
            103, "Rohan", "Operations", 800, 160
        ),

        new InternEmployee(
            104, "Priya", "Research", 25000
        ),

        new TaxablePermanentEmployee(
            105, "Ananya", "Finance", 85000, 60000
        )
    ];

    for (const employee of employees) {
        service.register(employee);
    }

    console.log("\n=== POLYMORPHISM ===");

    for (const employee of employees) {
        console.log(
            employee.name,
            employee.calculateSalary()
        );
    }

    console.log("\n=== PROTOTYPE CHAIN ===");

    console.log(
        employees[1] instanceof SeniorEmployee
    );

    console.log(
        employees[1] instanceof PermanentEmployee
    );

    console.log(
        employees[1] instanceof Employee
    );

    console.log("\n=== MIXINS ===");

    console.log(employees[4].calculateNetSalary());
    console.log(employees[4].audit());

    console.log("\n=== ASYNC PAYROLL ===");

    const payroll = await service.processPayroll();

    for (const record of payroll) {
        console.log(record);
    }

    console.log("\n=== DEPARTMENT TOTALS ===");
    console.log(service.departmentTotals());

    service.getEmployee(104).deactivate();

    console.log("\n=== AFTER DEACTIVATION ===");
    console.log(await service.processPayroll());

    console.log("\n=== ERROR HANDLING ===");

    try {
        service.getEmployee(999);
    } catch (error) {
        console.error(error.name, error.message);
    }

    try {
        new PermanentEmployee(
            110, "Invalid", "IT", -5000, 0
        );
    } catch (error) {
        console.error(error.name, error.message);
    }

    console.log("\n=== ASSERTIONS ===");

    console.assert(
        employees[0].calculateSalary() === 80000,
        "Permanent salary calculation failed."
    );

    console.assert(
        employees[1].calculateSalary() === 135000,
        "Senior salary calculation failed."
    );

    console.assert(
        employees[2].calculateSalary() === 128000,
        "Contract salary calculation failed."
    );

    console.assert(
        employees[4].calculateNetSalary() === 80000,
        "Tax calculation failed."
    );

    console.log("JavaScript inheritance tests completed.");
}

main().catch(error => {
    console.error("Payroll execution failed:", error);
    process.exitCode = 1;
});
