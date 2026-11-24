import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/*
 * JAVA 17 INHERITANCE
 *
 * Enterprise employee payroll and governance model.
 *
 * Demonstrates:
 * - Abstract classes
 * - Interfaces
 * - Single inheritance
 * - Multilevel inheritance
 * - Hierarchical inheritance
 * - Multiple interface implementation
 * - Method overriding
 * - Runtime polymorphism
 * - Records
 * - Immutable collections
 * - Generics
 * - Streams
 * - Composition
 * - Domain validation
 * - State transitions
 * - Custom exceptions
 */

public class Main {

    enum EmploymentType {
        PERMANENT,
        CONTRACT,
        INTERN
    }

    enum EmployeeStatus {
        ACTIVE,
        INACTIVE
    }

    static class PayrollException extends RuntimeException {
        PayrollException(String message) {
            super(message);
        }
    }

    static class ValidationException extends PayrollException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class EmployeeNotFoundException
            extends PayrollException {
        EmployeeNotFoundException(int id) {
            super("Employee not found: " + id);
        }
    }

    record PayrollResult(
            int employeeId,
            String employeeName,
            double grossSalary,
            double deductions,
            double netSalary
    ) {}

    record DepartmentReport(
            String department,
            double totalGross
    ) {}

    interface Taxable {
        double calculateTax(double rate);

        default double calculateNetSalary(double rate) {
            return getGrossSalary() - calculateTax(rate);
        }

        double getGrossSalary();
    }

    interface Auditable {
        String auditDescription();

        default boolean auditPassed() {
            return !auditDescription().isBlank();
        }
    }

    abstract static class Employee {

        private final int id;
        private final String name;
        private final String department;
        private final EmploymentType employmentType;

        private EmployeeStatus status;

        protected Employee(
                int id,
                String name,
                String department,
                EmploymentType employmentType
        ) {
            if (id <= 0) {
                throw new ValidationException(
                        "Employee ID must be positive."
                );
            }

            if (name == null || name.isBlank()) {
                throw new ValidationException(
                        "Employee name is required."
                );
            }

            if (department == null || department.isBlank()) {
                throw new ValidationException(
                        "Department is required."
                );
            }

            this.id = id;
            this.name = name;
            this.department = department;
            this.employmentType =
                    Objects.requireNonNull(employmentType);

            this.status = EmployeeStatus.ACTIVE;
        }

        public abstract double calculateSalary();

        public final void deactivate() {
            this.status = EmployeeStatus.INACTIVE;
        }

        public final boolean isActive() {
            return status == EmployeeStatus.ACTIVE;
        }

        public final int getId() {
            return id;
        }

        public final String getName() {
            return name;
        }

        public final String getDepartment() {
            return department;
        }

        public final EmploymentType getEmploymentType() {
            return employmentType;
        }

        public final EmployeeStatus getStatus() {
            return status;
        }

        public final double getGrossSalary() {
            return calculateSalary();
        }

        public String getDetails() {
            return String.format(
                    "%d | %s | %s | %.2f",
                    id,
                    name,
                    department,
                    calculateSalary()
            );
        }
    }

    // Single inheritance
    static class PermanentEmployee extends Employee {

        private final double monthlySalary;
        private final double annualBonus;

        PermanentEmployee(
                int id,
                String name,
                String department,
                double salary,
                double bonus
        ) {
            super(
                    id,
                    name,
                    department,
                    EmploymentType.PERMANENT
            );

            validateMoney(salary, "Monthly salary");
            validateMoney(bonus, "Annual bonus");

            this.monthlySalary = salary;
            this.annualBonus = bonus;
        }

        @Override
        public double calculateSalary() {
            return monthlySalary + annualBonus / 12.0;
        }
    }

    // Multilevel inheritance
    static class SeniorEmployee extends PermanentEmployee {

        private final double leadershipAllowance;

        SeniorEmployee(
                int id,
                String name,
                String department,
                double salary,
                double bonus,
                double allowance
        ) {
            super(id, name, department, salary, bonus);

            validateMoney(allowance, "Leadership allowance");

            this.leadershipAllowance = allowance;
        }

        @Override
        public double calculateSalary() {
            return super.calculateSalary()
                    + leadershipAllowance;
        }
    }

    // Hierarchical inheritance
    static class ContractEmployee extends Employee {

        private final double hourlyRate;
        private final double hours;

        ContractEmployee(
                int id,
                String name,
                String department,
                double hourlyRate,
                double hours
        ) {
            super(
                    id,
                    name,
                    department,
                    EmploymentType.CONTRACT
            );

            validateMoney(hourlyRate, "Hourly rate");
            validateMoney(hours, "Working hours");

            if (hours > 744) {
                throw new ValidationException(
                        "Monthly working hours exceed limit."
                );
            }

            this.hourlyRate = hourlyRate;
            this.hours = hours;
        }

        @Override
        public double calculateSalary() {
            return hourlyRate * hours;
        }
    }

    static class InternEmployee extends Employee {

        private final double stipend;

        InternEmployee(
                int id,
                String name,
                String department,
                double stipend
        ) {
            super(
                    id,
                    name,
                    department,
                    EmploymentType.INTERN
            );

            validateMoney(stipend, "Stipend");

            this.stipend = stipend;
        }

        @Override
        public double calculateSalary() {
            return stipend;
        }
    }

    // Multiple interface implementation
    static class TaxablePermanentEmployee
            extends PermanentEmployee
            implements Taxable, Auditable {

        TaxablePermanentEmployee(
                int id,
                String name,
                String department,
                double salary,
                double bonus
        ) {
            super(id, name, department, salary, bonus);
        }

        @Override
        public double calculateTax(double rate) {
            if (!Double.isFinite(rate) || rate < 0 || rate > 1) {
                throw new ValidationException(
                        "Tax rate must be between zero and one."
                );
            }

            return calculateSalary() * rate;
        }

        @Override
        public String auditDescription() {
            return "Taxable permanent employee: " + getId();
        }
    }

    // Hybrid inheritance
    static class DepartmentManager
            extends SeniorEmployee
            implements Taxable, Auditable {

        private final double managementBonus;

        DepartmentManager(
                int id,
                String name,
                String department,
                double salary,
                double bonus,
                double allowance,
                double managementBonus
        ) {
            super(
                    id,
                    name,
                    department,
                    salary,
                    bonus,
                    allowance
            );

            validateMoney(
                    managementBonus,
                    "Management bonus"
            );

            this.managementBonus = managementBonus;
        }

        @Override
        public double calculateSalary() {
            return super.calculateSalary()
                    + managementBonus;
        }

        @Override
        public double calculateTax(double rate) {
            if (!Double.isFinite(rate) || rate < 0 || rate > 1) {
                throw new ValidationException(
                        "Invalid tax rate."
                );
            }

            return calculateSalary() * rate;
        }

        @Override
        public String auditDescription() {
            return "Department manager: " + getId();
        }
    }

    // Composition separates payroll rules from employee inheritance.
    static final class PayrollPolicy {

        private final double deductionRate;

        PayrollPolicy(double deductionRate) {
            if (
                    !Double.isFinite(deductionRate)
                            || deductionRate < 0
                            || deductionRate > 1
            ) {
                throw new ValidationException(
                        "Invalid deduction rate."
                );
            }

            this.deductionRate = deductionRate;
        }

        PayrollResult calculate(Employee employee) {
            double gross = employee.calculateSalary();
            double deductions = gross * deductionRate;

            return new PayrollResult(
                    employee.getId(),
                    employee.getName(),
                    gross,
                    deductions,
                    gross - deductions
            );
        }
    }

    static final class PayrollService {

        private final PayrollPolicy policy;

        private final Map<Integer, Employee> employees =
                new HashMap<>();

        PayrollService(PayrollPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        void register(Employee employee) {
            Objects.requireNonNull(employee);

            if (employees.containsKey(employee.getId())) {
                throw new ValidationException(
                        "Duplicate employee ID."
                );
            }

            employees.put(employee.getId(), employee);
        }

        Employee findEmployee(int id) {
            Employee employee = employees.get(id);

            if (employee == null) {
                throw new EmployeeNotFoundException(id);
            }

            return employee;
        }

        Optional<Employee> findActiveEmployee(int id) {
            return Optional.ofNullable(employees.get(id))
                    .filter(Employee::isActive);
        }

        List<PayrollResult> processPayroll() {
            return employees.values()
                    .stream()
                    .filter(Employee::isActive)
                    .map(policy::calculate)
                    .sorted((a, b) ->
                            Integer.compare(
                                    a.employeeId(),
                                    b.employeeId()
                            ))
                    .toList();
        }

        List<DepartmentReport> departmentReports() {
            Map<String, Double> totals =
                    employees.values()
                            .stream()
                            .filter(Employee::isActive)
                            .collect(Collectors.groupingBy(
                                    Employee::getDepartment,
                                    Collectors.summingDouble(
                                            Employee::calculateSalary
                                    )
                            ));

            return totals.entrySet()
                    .stream()
                    .map(entry -> new DepartmentReport(
                            entry.getKey(),
                            entry.getValue()
                    ))
                    .toList();
        }

        <T extends Employee> List<T> findByType(
                Class<T> employeeClass
        ) {
            return employees.values()
                    .stream()
                    .filter(employee ->
                            employeeClass.isInstance(employee))
                    .map(employee ->
                            employeeClass.cast(employee))
                    .toList();
        }

        void deactivate(int id) {
            findEmployee(id).deactivate();
        }

        int employeeCount() {
            return employees.size();
        }
    }

    private static void validateMoney(
            double amount,
            String field
    ) {
        if (!Double.isFinite(amount) || amount < 0) {
            throw new ValidationException(
                    field + " must be finite and non-negative."
            );
        }
    }

    private static void demonstrateInheritance() {

        System.out.println("\n=== INHERITANCE ===");

        Employee permanent = new PermanentEmployee(
                101, "Aarav", "Engineering",
                70000, 120000
        );

        Employee senior = new SeniorEmployee(
                102, "Meera", "Engineering",
                100000, 240000, 15000
        );

        Employee contractor = new ContractEmployee(
                103, "Rohan", "Operations",
                800, 160
        );

        Employee intern = new InternEmployee(
                104, "Priya", "Research",
                25000
        );

        System.out.println(permanent.getDetails());
        System.out.println(senior.getDetails());
        System.out.println(contractor.getDetails());
        System.out.println(intern.getDetails());

        System.out.println("\n=== RUNTIME POLYMORPHISM ===");

        List<Employee> employees = List.of(
                permanent,
                senior,
                contractor,
                intern
        );

        employees.forEach(employee ->
                System.out.println(
                        employee.getName()
                                + ": "
                                + employee.calculateSalary()
                )
        );

        System.out.println("\n=== INTERFACE INHERITANCE ===");

        TaxablePermanentEmployee taxable =
                new TaxablePermanentEmployee(
                        105, "Ananya", "Finance",
                        85000, 60000
                );

        System.out.println(
                "Net salary: "
                        + taxable.calculateNetSalary(0.10)
        );

        System.out.println(taxable.auditDescription());

        System.out.println("\n=== HYBRID INHERITANCE ===");

        DepartmentManager manager =
                new DepartmentManager(
                        106, "Vikram", "Engineering",
                        120000, 300000,
                        20000, 15000
                );

        System.out.println(
                manager.getDetails()
        );

        System.out.println(
                "Manager net salary: "
                        + manager.calculateNetSalary(0.10)
        );
    }

    private static void demonstrateEnterprisePayroll() {

        System.out.println("\n=== ENTERPRISE PAYROLL ===");

        PayrollService service = new PayrollService(
                new PayrollPolicy(0.12)
        );

        service.register(new PermanentEmployee(
                201, "Kabir", "Technology",
                90000, 120000
        ));

        service.register(new ContractEmployee(
                202, "Sana", "Technology",
                600, 150
        ));

        service.register(new InternEmployee(
                203, "Dev", "Research",
                20000
        ));

        System.out.println("\nPayroll results:");

        service.processPayroll().forEach(System.out::println);

        System.out.println("\nDepartment reports:");

        service.departmentReports().forEach(
                System.out::println
        );

        System.out.println("\nPermanent employees:");

        service.findByType(PermanentEmployee.class)
                .forEach(employee ->
                        System.out.println(employee.getDetails())
                );

        service.deactivate(203);

        System.out.println("\nAfter deactivation:");

        service.processPayroll().forEach(System.out::println);

        try {
            service.findEmployee(999);
        } catch (EmployeeNotFoundException exception) {
            System.out.println(exception.getMessage());
        }

        try {
            service.register(new InternEmployee(
                    201, "Duplicate", "IT", 15000
            ));
        } catch (ValidationException exception) {
            System.out.println(exception.getMessage());
        }
    }

    private static void runTests() {

        PermanentEmployee employee =
                new PermanentEmployee(
                        1, "Test", "IT", 50000, 12000
                );

        if (employee.calculateSalary() != 51000) {
            throw new AssertionError("Permanent salary failed.");
        }

        SeniorEmployee senior =
                new SeniorEmployee(
                        2, "Senior", "IT",
                        50000, 12000, 5000
                );

        if (senior.calculateSalary() != 56000) {
            throw new AssertionError("Senior salary failed.");
        }

        if (!(senior instanceof Employee)) {
            throw new AssertionError("Inheritance failed.");
        }

        TaxablePermanentEmployee taxable =
                new TaxablePermanentEmployee(
                        3, "Taxable", "Finance",
                        50000, 12000
                );

        if (taxable.calculateNetSalary(0.10) != 45900) {
            throw new AssertionError("Tax calculation failed.");
        }

        PayrollService service = new PayrollService(
                new PayrollPolicy(0.10)
        );

        service.register(employee);

        if (service.employeeCount() != 1) {
            throw new AssertionError("Registration failed.");
        }

        System.out.println("\nAll Java 17 assertions passed.");
    }

    public static void main(String[] args) {

        demonstrateInheritance();

        demonstrateEnterprisePayroll();

        runTests();
    }
}
