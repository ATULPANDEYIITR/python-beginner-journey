import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import java.util.regex.Pattern;

public class PropertiesEnterprise {

    static class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    // 1. Property-style accessors with validation
    static final class Temperature {
        private double celsius;

        Temperature(double celsius) {
            setCelsius(celsius);
        }

        public double getCelsius() {
            return celsius;
        }

        public void setCelsius(double value) {
            if (!Double.isFinite(value) ||
                value < -273.15 || value > 1000) {
                throw new ValidationException("Invalid temperature.");
            }
            celsius = value;
        }

        public double getFahrenheit() {
            return celsius * 9 / 5 + 32;
        }

        public void setFahrenheit(double value) {
            if (!Double.isFinite(value)) {
                throw new ValidationException("Invalid Fahrenheit value.");
            }
            setCelsius((value - 32) * 5 / 9);
        }
    }

    // 2. Immutable identity property
    record EmployeeIdentity(int id, String name) {
        EmployeeIdentity {
            if (id <= 0 || name == null || name.isBlank()) {
                throw new ValidationException("Invalid employee identity.");
            }
        }
    }

    // 3. Computed properties
    static final class Rectangle {
        private double width;
        private double height;

        Rectangle(double width, double height) {
            setWidth(width);
            setHeight(height);
        }

        public double getWidth() {
            return width;
        }

        public void setWidth(double width) {
            if (!Double.isFinite(width) || width <= 0) {
                throw new ValidationException("Width must be positive.");
            }
            this.width = width;
        }

        public double getHeight() {
            return height;
        }

        public void setHeight(double height) {
            if (!Double.isFinite(height) || height <= 0) {
                throw new ValidationException("Height must be positive.");
            }
            this.height = height;
        }

        public double getArea() {
            return width * height;
        }

        public double getPerimeter() {
            return 2 * (width + height);
        }
    }

    // 4. Monetary property with decimal precision
    static final class BankAccount {
        private final String accountNumber;
        private BigDecimal balance;

        private static final Pattern ACCOUNT_PATTERN =
            Pattern.compile("[A-Z0-9]{6,20}");

        BankAccount(String accountNumber, BigDecimal openingBalance) {
            if (accountNumber == null ||
                !ACCOUNT_PATTERN.matcher(accountNumber).matches()) {
                throw new ValidationException("Invalid account number.");
            }

            this.accountNumber = accountNumber;
            setBalance(openingBalance);
        }

        public String getAccountNumber() {
            return accountNumber;
        }

        public BigDecimal getBalance() {
            return balance;
        }

        private void setBalance(BigDecimal value) {
            Objects.requireNonNull(value, "Balance is required.");

            BigDecimal normalized = value.setScale(2, RoundingMode.UNNECESSARY);

            if (normalized.signum() < 0) {
                throw new ValidationException("Negative balance prohibited.");
            }

            balance = normalized;
        }

        public void deposit(BigDecimal amount) {
            validateTransaction(amount);
            balance = balance.add(amount);
        }

        public void withdraw(BigDecimal amount) {
            validateTransaction(amount);

            if (amount.compareTo(balance) > 0) {
                throw new ValidationException("Insufficient funds.");
            }

            balance = balance.subtract(amount);
        }

        private void validateTransaction(BigDecimal amount) {
            Objects.requireNonNull(amount, "Amount is required.");

            if (amount.scale() > 2 || amount.signum() <= 0) {
                throw new ValidationException("Invalid transaction amount.");
            }
        }
    }

    // 5. Cached computed property
    static final class Inventory {
        private final Map<String, Integer> quantities = new HashMap<>();
        private long cachedTotal;
        private boolean dirty = true;
        private int calculationCount;

        public void setQuantity(String product, int quantity) {
            if (product == null || product.isBlank() || quantity < 0) {
                throw new ValidationException("Invalid inventory entry.");
            }

            quantities.put(product, quantity);
            dirty = true;
        }

        public long getTotalUnits() {
            if (dirty) {
                cachedTotal = quantities.values()
                    .stream()
                    .mapToLong(Integer::longValue)
                    .sum();

                calculationCount++;
                dirty = false;
            }

            return cachedTotal;
        }

        public int getCalculationCount() {
            return calculationCount;
        }
    }

    // 6. Enterprise state property
    enum AccountStatus {
        ACTIVE,
        SUSPENDED,
        CLOSED
    }

    static final class CustomerAccount {
        private final String customerId;
        private AccountStatus status;

        CustomerAccount(String customerId) {
            if (customerId == null || customerId.isBlank()) {
                throw new ValidationException("Customer ID required.");
            }

            this.customerId = customerId;
            this.status = AccountStatus.ACTIVE;
        }

        public String getCustomerId() {
            return customerId;
        }

        public AccountStatus getStatus() {
            return status;
        }

        public void setStatus(AccountStatus newStatus) {
            Objects.requireNonNull(newStatus);

            if (status == AccountStatus.CLOSED &&
                newStatus != AccountStatus.CLOSED) {
                throw new ValidationException("Closed account cannot reopen.");
            }

            status = newStatus;
        }
    }

    // 7. Property change tracking
    static final class AuditedRecord {
        private String name;
        private Instant updatedAt;

        AuditedRecord(String name) {
            setName(name);
        }

        public String getName() {
            return name;
        }

        public Instant getUpdatedAt() {
            return updatedAt;
        }

        public void setName(String value) {
            if (value == null || value.isBlank()) {
                throw new ValidationException("Name cannot be empty.");
            }

            String normalized = value.trim();

            if (!normalized.equals(name)) {
                name = normalized;
                updatedAt = Instant.now();
            }
        }
    }

    // 8. Concurrent computed-property cache
    static final class ReportService {
        private final ConcurrentHashMap<String, BigDecimal> cache =
            new ConcurrentHashMap<>();

        private final AtomicInteger calculations = new AtomicInteger();

        private final Map<String, Supplier<BigDecimal>> reportSources =
            Map.of(
                "SALES", () -> new BigDecimal("125000.00"),
                "COSTS", () -> new BigDecimal("85000.00")
            );

        public BigDecimal getReport(String reportName) {
            if (reportName == null || !reportSources.containsKey(reportName)) {
                throw new ValidationException("Unknown report.");
            }

            return cache.computeIfAbsent(reportName, key -> {
                calculations.incrementAndGet();
                return reportSources.get(key).get();
            });
        }

        public void invalidate(String reportName) {
            cache.remove(reportName);
        }

        public int getCalculationCount() {
            return calculations.get();
        }
    }

    // 9. Property validation and test scenarios
    private static void runTests() {
        Temperature temperature = new Temperature(25);
        assert temperature.getFahrenheit() == 77;

        temperature.setFahrenheit(32);
        assert Math.abs(temperature.getCelsius()) < 0.0001;

        boolean invalidTemperature = false;

        try {
            temperature.setCelsius(-300);
        } catch (ValidationException exception) {
            invalidTemperature = true;
        }

        assert invalidTemperature;

        EmployeeIdentity employee = new EmployeeIdentity(101, "Asha");
        assert employee.id() == 101;

        Rectangle rectangle = new Rectangle(10, 5);
        assert rectangle.getArea() == 50;

        BankAccount account = new BankAccount(
            "BANK1234",
            new BigDecimal("1000.00")
        );

        account.deposit(new BigDecimal("500.00"));
        account.withdraw(new BigDecimal("200.00"));

        assert account.getBalance().compareTo(
            new BigDecimal("1300.00")
        ) == 0;

        Inventory inventory = new Inventory();
        inventory.setQuantity("Laptop", 10);
        inventory.setQuantity("Keyboard", 20);

        assert inventory.getTotalUnits() == 30;
        assert inventory.getTotalUnits() == 30;
        assert inventory.getCalculationCount() == 1;

        inventory.setQuantity("Mouse", 5);
        assert inventory.getTotalUnits() == 35;

        CustomerAccount customer = new CustomerAccount("CUS001");
        customer.setStatus(AccountStatus.CLOSED);

        boolean invalidTransition = false;

        try {
            customer.setStatus(AccountStatus.ACTIVE);
        } catch (ValidationException exception) {
            invalidTransition = true;
        }

        assert invalidTransition;

        AuditedRecord record = new AuditedRecord("Repository");
        assert record.getUpdatedAt() != null;

        ReportService service = new ReportService();

        assert service.getReport("SALES").compareTo(
            new BigDecimal("125000.00")
        ) == 0;

        service.getReport("SALES");
        assert service.getCalculationCount() == 1;

        service.invalidate("SALES");
        service.getReport("SALES");
        assert service.getCalculationCount() == 2;

        System.out.println("All Java 17 property tests passed.");
    }

    public static void main(String[] args) {
        runTests();

        Temperature temperature = new Temperature(20);
        Rectangle rectangle = new Rectangle(12, 8);

        BankAccount account = new BankAccount(
            "CORP1234",
            new BigDecimal("25000.00")
        );

        account.deposit(new BigDecimal("5000.00"));

        System.out.println("Temperature: " + temperature.getCelsius());
        System.out.println("Fahrenheit: " + temperature.getFahrenheit());
        System.out.println("Rectangle area: " + rectangle.getArea());
        System.out.println("Account balance: " + account.getBalance());

        Inventory inventory = new Inventory();
        inventory.setQuantity("Servers", 5);
        inventory.setQuantity("Switches", 12);

        System.out.println("Inventory total: " + inventory.getTotalUnits());
    }
}
