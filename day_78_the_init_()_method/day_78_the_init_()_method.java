/*
 * THE __init__() METHOD
 *
 * Java 17 uses constructors rather than Python's __init__().
 *
 * This enterprise-oriented implementation covers:
 * - Default and parameterized constructors
 * - Constructor overloading
 * - Constructor chaining using this()
 * - Parent initialization using super()
 * - Record compact constructors
 * - Immutable object initialization
 * - Validation and custom exceptions
 * - Composition
 * - Factory methods
 * - Dependency injection
 * - State transitions
 * - Defensive copying
 * - Object reconstruction
 */

import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

// ==========================================================
// 1. CUSTOM EXCEPTION
// ==========================================================

class InitializationException extends RuntimeException {
    public InitializationException(String message) {
        super(message);
    }

    public InitializationException(String message, Throwable cause) {
        super(message, cause);
    }
}

// ==========================================================
// 2. BASIC CONSTRUCTOR
// ==========================================================

class Student {
    private final String name;
    private final int age;

    public Student(String name, int age) {
        if (name == null || name.isBlank()) {
            throw new InitializationException("Student name is required.");
        }

        if (age < 0 || age > 120) {
            throw new InitializationException("Invalid student age.");
        }

        this.name = name.strip();
        this.age = age;
    }

    public String introduce() {
        return name + " is " + age + " years old.";
    }
}

// ==========================================================
// 3. CONSTRUCTOR OVERLOADING AND CHAINING
// ==========================================================

class ServerConfiguration {
    private final String host;
    private final int port;
    private final boolean secure;

    public ServerConfiguration() {
        this("localhost", 3000, false);
    }

    public ServerConfiguration(String host) {
        this(host, 3000, false);
    }

    public ServerConfiguration(String host, int port, boolean secure) {
        if (host == null || host.isBlank()) {
            throw new InitializationException("Host is required.");
        }

        if (port < 1 || port > 65535) {
            throw new InitializationException("Invalid port.");
        }

        this.host = host.strip();
        this.port = port;
        this.secure = secure;
    }

    public String endpoint() {
        return (secure ? "https://" : "http://")
                + host + ":" + port;
    }
}

// ==========================================================
// 4. IMMUTABLE OBJECT INITIALIZATION
// ==========================================================

final class Employee {
    private final UUID id;
    private final String name;
    private final String department;
    private final Instant createdAt;

    public Employee(String name, String department) {
        this(UUID.randomUUID(), name, department, Instant.now());
    }

    public Employee(
            UUID id,
            String name,
            String department,
            Instant createdAt
    ) {
        this.id = Objects.requireNonNull(id, "Employee ID is required.");

        if (name == null || name.isBlank()) {
            throw new InitializationException("Employee name is required.");
        }

        if (department == null || department.isBlank()) {
            throw new InitializationException("Department is required.");
        }

        this.name = name.strip();
        this.department = department.strip();
        this.createdAt = Objects.requireNonNull(
                createdAt,
                "Creation timestamp is required."
        );
    }

    public UUID getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getDepartment() {
        return department;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}

// ==========================================================
// 5. JAVA 17 RECORD AND COMPACT CONSTRUCTOR
// ==========================================================

record Product(String name, BigDecimal price, String category) {

    public Product {
        if (name == null || name.isBlank()) {
            throw new InitializationException("Product name is required.");
        }

        Objects.requireNonNull(price, "Price is required.");

        if (price.signum() < 0) {
            throw new InitializationException("Price cannot be negative.");
        }

        if (category == null || category.isBlank()) {
            throw new InitializationException("Category is required.");
        }

        name = name.strip();
        category = category.strip();
    }
}

// ==========================================================
// 6. INHERITANCE AND SUPER()
// ==========================================================

class Person {
    protected final String name;
    protected final String email;

    public Person(String name, String email) {
        if (name == null || name.isBlank()) {
            throw new InitializationException("Name is required.");
        }

        if (email == null || !email.matches("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")) {
            throw new InitializationException("Invalid email.");
        }

        this.name = name.strip();
        this.email = email.strip();
    }
}

class Manager extends Person {
    private final int teamSize;

    public Manager(String name, String email, int teamSize) {
        super(name, email);

        if (teamSize < 0) {
            throw new InitializationException("Invalid team size.");
        }

        this.teamSize = teamSize;
    }

    public String description() {
        return name + " manages " + teamSize + " employees.";
    }
}

// ==========================================================
// 7. COMPOSITION AND DEFENSIVE COPYING
// ==========================================================

record Address(String city, String country) {

    public Address {
        if (city == null || city.isBlank()) {
            throw new InitializationException("City is required.");
        }

        if (country == null || country.isBlank()) {
            throw new InitializationException("Country is required.");
        }

        city = city.strip();
        country = country.strip();
    }
}

final class Organization {
    private final String name;
    private final Address address;
    private final List<String> departments;

    public Organization(
            String name,
            Address address,
            List<String> departments
    ) {
        if (name == null || name.isBlank()) {
            throw new InitializationException("Organization name is required.");
        }

        this.name = name.strip();
        this.address = Objects.requireNonNull(address);

        Objects.requireNonNull(departments);

        if (departments.stream().anyMatch(
                department -> department == null || department.isBlank()
        )) {
            throw new InitializationException("Invalid department.");
        }

        this.departments = List.copyOf(departments);
    }

    public List<String> getDepartments() {
        return departments;
    }

    public String getName() {
        return name;
    }

    public Address getAddress() {
        return address;
    }
}

// ==========================================================
// 8. BANK ACCOUNT WITH EXPLICIT STATE
// ==========================================================

enum AccountStatus {
    ACTIVE,
    SUSPENDED,
    CLOSED
}

class BankAccount {
    private final String accountNumber;
    private final String owner;

    private BigDecimal balance;
    private AccountStatus status;

    public BankAccount(
            String accountNumber,
            String owner,
            BigDecimal initialBalance
    ) {
        if (accountNumber == null || accountNumber.isBlank()) {
            throw new InitializationException("Account number is required.");
        }

        if (owner == null || owner.isBlank()) {
            throw new InitializationException("Owner is required.");
        }

        Objects.requireNonNull(initialBalance);

        if (initialBalance.signum() < 0) {
            throw new InitializationException("Negative initial balance.");
        }

        this.accountNumber = accountNumber.strip();
        this.owner = owner.strip();
        this.balance = initialBalance;
        this.status = AccountStatus.ACTIVE;
    }

    public void deposit(BigDecimal amount) {
        if (status != AccountStatus.ACTIVE) {
            throw new IllegalStateException("Account is not active.");
        }

        Objects.requireNonNull(amount);

        if (amount.signum() <= 0) {
            throw new IllegalArgumentException("Deposit must be positive.");
        }

        balance = balance.add(amount);
    }

    public void suspend() {
        if (status == AccountStatus.CLOSED) {
            throw new IllegalStateException("Closed account cannot be suspended.");
        }

        status = AccountStatus.SUSPENDED;
    }

    public BigDecimal getBalance() {
        return balance;
    }

    public AccountStatus getStatus() {
        return status;
    }
}

// ==========================================================
// 9. FACTORY METHOD AND OBJECT RECONSTRUCTION
// ==========================================================

class Configuration {
    private final Map<String, String> values;

    private Configuration(Map<String, String> values) {
        Objects.requireNonNull(values);

        if (values.entrySet().stream().anyMatch(
                entry -> entry.getKey() == null
                        || entry.getKey().isBlank()
                        || entry.getValue() == null
        )) {
            throw new InitializationException("Invalid configuration entry.");
        }

        this.values = Map.copyOf(values);
    }

    public static Configuration fromMap(Map<String, String> values) {
        return new Configuration(values);
    }

    public String get(String key) {
        return values.get(key);
    }
}

// ==========================================================
// 10. DEPENDENCY INJECTION THROUGH CONSTRUCTORS
// ==========================================================

interface AuditService {
    void record(String event);
}

class ConsoleAuditService implements AuditService {
    @Override
    public void record(String event) {
        System.out.println("[AUDIT] " + event);
    }
}

class DeploymentService {
    private final AuditService auditService;

    public DeploymentService(AuditService auditService) {
        this.auditService = Objects.requireNonNull(
                auditService,
                "Audit service is required."
        );
    }

    public void deploy(String application) {
        if (application == null || application.isBlank()) {
            throw new IllegalArgumentException("Application is required.");
        }

        auditService.record("Deployment requested: " + application);
    }
}

// ==========================================================
// 11. ENTERPRISE INITIALIZATION LIFECYCLE
// ==========================================================

enum DeploymentState {
    CREATED,
    VALIDATED,
    DEPLOYED,
    FAILED
}

class Deployment {
    private final String application;
    private final String environment;
    private final String version;

    private DeploymentState state;

    public Deployment(
            String application,
            String environment,
            String version
    ) {
        if (application == null || application.isBlank()) {
            throw new InitializationException("Application is required.");
        }

        if (!List.of("development", "testing", "production")
                .contains(environment)) {
            throw new InitializationException("Invalid environment.");
        }

        if (version == null || version.isBlank()) {
            throw new InitializationException("Version is required.");
        }

        this.application = application.strip();
        this.environment = environment;
        this.version = version.strip();
        this.state = DeploymentState.CREATED;
    }

    public void validate() {
        if (state != DeploymentState.CREATED) {
            throw new IllegalStateException("Invalid validation transition.");
        }

        state = DeploymentState.VALIDATED;
    }

    public void deploy() {
        if (state != DeploymentState.VALIDATED) {
            throw new IllegalStateException("Deployment must be validated.");
        }

        state = DeploymentState.DEPLOYED;
    }

    public void fail() {
        if (state == DeploymentState.DEPLOYED) {
            throw new IllegalStateException("Deployment is already complete.");
        }

        state = DeploymentState.FAILED;
    }

    public DeploymentState getState() {
        return state;
    }

    public String description() {
        return application + " | " + environment
                + " | " + version + " | " + state;
    }
}

// ==========================================================
// 12. EXECUTABLE TESTS
// ==========================================================

public class Main {

    private static void expectFailure(Runnable operation) {
        try {
            operation.run();
            throw new AssertionError("Expected validation failure.");
        } catch (InitializationException
                 | IllegalArgumentException
                 | IllegalStateException expected) {
            System.out.println("Rejected: " + expected.getMessage());
        }
    }

    public static void main(String[] args) {

        System.out.println("\n1. Basic initialization");

        Student student = new Student("Atul", 25);
        System.out.println(student.introduce());

        System.out.println("\n2. Constructor overloading");

        ServerConfiguration defaultServer = new ServerConfiguration();
        ServerConfiguration secureServer =
                new ServerConfiguration("example.com", 443, true);

        System.out.println(defaultServer.endpoint());
        System.out.println(secureServer.endpoint());

        System.out.println("\n3. Immutable initialization");

        Employee employee = new Employee("Anita", "Engineering");

        System.out.println(employee.getName());
        System.out.println(employee.getId());

        System.out.println("\n4. Record compact constructor");

        Product product = new Product(
                "Security Sensor",
                new BigDecimal("2499.00"),
                "Hardware"
        );

        System.out.println(product);

        System.out.println("\n5. Inheritance");

        Manager manager = new Manager(
                "Rahul",
                "rahul@example.com",
                8
        );

        System.out.println(manager.description());

        System.out.println("\n6. Composition");

        Organization organization = new Organization(
                "Research Laboratory",
                new Address("Lucknow", "India"),
                new ArrayList<>(List.of("AI", "Cybersecurity"))
        );

        System.out.println(organization.getName());
        System.out.println(organization.getDepartments());

        System.out.println("\n7. Account initialization");

        BankAccount account = new BankAccount(
                "ACC-1001",
                "Atul",
                new BigDecimal("5000.00")
        );

        account.deposit(new BigDecimal("1500.00"));

        System.out.println(account.getBalance());

        System.out.println("\n8. Factory construction");

        Configuration configuration = Configuration.fromMap(
                Map.of(
                        "database", "postgresql",
                        "environment", "testing"
                )
        );

        System.out.println(configuration.get("database"));

        System.out.println("\n9. Constructor dependency injection");

        DeploymentService service = new DeploymentService(
                new ConsoleAuditService()
        );

        service.deploy("Risk Engine");

        System.out.println("\n10. State transitions");

        Deployment deployment = new Deployment(
                "Risk Engine",
                "testing",
                "2.1.0"
        );

        deployment.validate();
        deployment.deploy();

        System.out.println(deployment.description());

        assert deployment.getState() == DeploymentState.DEPLOYED;
        assert account.getBalance().equals(new BigDecimal("6500.00"));
        assert student.introduce().contains("Atul");
        assert organization.getDepartments().size() == 2;

        System.out.println("\n11. Invalid initialization");

        expectFailure(() -> new Student("", 20));

        expectFailure(() -> new ServerConfiguration(
                "localhost", 70000, false
        ));

        expectFailure(() -> new Product(
                "Device",
                new BigDecimal("-10"),
                "Hardware"
        ));

        expectFailure(() -> new BankAccount(
                "ACC-2",
                "User",
                new BigDecimal("-100")
        ));

        expectFailure(() -> new Deployment(
                "Application",
                "unknown",
                "1.0"
        ));

        expectFailure(() -> new DeploymentService(null));

        System.out.println("\nAll Java 17 tests passed.");
    }
}
