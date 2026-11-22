import java.math.BigDecimal;
import java.math.RoundingMode;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.regex.Pattern;

/*
 * STATIC METHODS IN JAVA 17
 *
 * Enterprise scenario: Financial services and account management.
 *
 * Concepts:
 * - Static methods and static fields.
 * - Instance methods versus static methods.
 * - Static factory methods.
 * - Utility classes.
 * - Static initialization.
 * - Static nested classes.
 * - Immutable records.
 * - Policy evaluation.
 * - Concurrent collections.
 * - Caching.
 * - Cryptographic utilities.
 * - Custom exceptions.
 *
 * Compile:
 * javac StaticMethods.java
 *
 * Execute:
 * java StaticMethods
 */

public class StaticMethods {

    // ========================================================
    // 1. STATIC MATHEMATICAL UTILITY METHODS
    // ========================================================

    public static final class MathService {

        private MathService() {
            throw new AssertionError("Utility class cannot be instantiated.");
        }

        public static BigDecimal add(
                BigDecimal first,
                BigDecimal second) {

            Objects.requireNonNull(first, "First operand is required.");
            Objects.requireNonNull(second, "Second operand is required.");

            return first.add(second);
        }

        public static BigDecimal subtract(
                BigDecimal first,
                BigDecimal second) {

            Objects.requireNonNull(first, "First operand is required.");
            Objects.requireNonNull(second, "Second operand is required.");

            return first.subtract(second);
        }

        public static BigDecimal multiply(
                BigDecimal first,
                BigDecimal second) {

            Objects.requireNonNull(first, "First operand is required.");
            Objects.requireNonNull(second, "Second operand is required.");

            return first.multiply(second);
        }

        public static BigDecimal divide(
                BigDecimal first,
                BigDecimal second) {

            Objects.requireNonNull(first, "First operand is required.");
            Objects.requireNonNull(second, "Second operand is required.");

            if (second.compareTo(BigDecimal.ZERO) == 0) {
                throw new ArithmeticException("Division by zero.");
            }

            return first.divide(second, 2, RoundingMode.HALF_UP);
        }
    }

    // ========================================================
    // 2. DOMAIN ENUMERATIONS AND RECORDS
    // ========================================================

    enum TransactionType {
        CREDIT,
        DEBIT
    }

    enum TransactionStatus {
        PENDING,
        COMPLETED,
        REJECTED
    }

    enum Role {
        READER,
        ANALYST,
        ADMINISTRATOR
    }

    enum Operation {
        READ,
        ANALYZE,
        WRITE,
        DELETE
    }

    record TransactionRequest(
            String transactionId,
            TransactionType type,
            BigDecimal amount) {

        TransactionRequest {
            if (transactionId == null || transactionId.isBlank()) {
                throw new IllegalArgumentException(
                        "Transaction ID is required.");
            }

            Objects.requireNonNull(type, "Transaction type is required.");
            Objects.requireNonNull(amount, "Amount is required.");

            if (amount.compareTo(BigDecimal.ZERO) <= 0) {
                throw new IllegalArgumentException(
                        "Amount must be positive.");
            }
        }
    }

    record TransactionResult(
            String transactionId,
            TransactionStatus status,
            BigDecimal previousBalance,
            BigDecimal currentBalance,
            String message) {
    }

    record Employee(
            long employeeId,
            String name,
            String department) {

        Employee {
            if (employeeId <= 0) {
                throw new IllegalArgumentException("Invalid employee ID.");
            }

            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Employee name is required.");
            }

            if (department == null || department.isBlank()) {
                throw new IllegalArgumentException("Department is required.");
            }
        }
    }

    // ========================================================
    // 3. STATIC VALIDATION SERVICE
    // ========================================================

    public static final class ValidationService {

        private static final Pattern EMAIL_PATTERN =
                Pattern.compile(
                        "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
                );

        private ValidationService() {
        }

        public static boolean validEmail(String email) {
            return email != null &&
                    EMAIL_PATTERN.matcher(email).matches();
        }

        public static boolean validPort(int port) {
            return port >= 1 && port <= 65535;
        }

        public static boolean validPositiveAmount(BigDecimal amount) {
            return amount != null &&
                    amount.compareTo(BigDecimal.ZERO) > 0;
        }

        public static boolean validEmployeeId(long employeeId) {
            return employeeId > 0;
        }
    }

    // ========================================================
    // 4. STATIC FACTORY METHODS
    // ========================================================

    public static final class EmployeeFactory {

        private EmployeeFactory() {
        }

        public static Employee create(
                long employeeId,
                String name,
                String department) {

            return new Employee(employeeId, name, department);
        }

        public static Employee fromMap(Map<String, String> data) {
            Objects.requireNonNull(data, "Employee data is required.");

            try {
                return create(
                        Long.parseLong(data.get("employeeId")),
                        data.get("name"),
                        data.get("department")
                );
            } catch (NumberFormatException exception) {
                throw new IllegalArgumentException(
                        "Employee ID must be numeric.",
                        exception
                );
            }
        }
    }

    // ========================================================
    // 5. STATIC POLICY OBJECTS
    // ========================================================

    public static final class AuthorizationPolicy {

        private static final Map<Role, Set<Operation>> PERMISSIONS;

        static {
            Map<Role, Set<Operation>> permissions = new HashMap<>();

            permissions.put(
                    Role.READER,
                    Set.of(Operation.READ)
            );

            permissions.put(
                    Role.ANALYST,
                    Set.of(Operation.READ, Operation.ANALYZE)
            );

            permissions.put(
                    Role.ADMINISTRATOR,
                    Set.of(
                            Operation.READ,
                            Operation.ANALYZE,
                            Operation.WRITE,
                            Operation.DELETE
                    )
            );

            PERMISSIONS = Collections.unmodifiableMap(permissions);
        }

        private AuthorizationPolicy() {
        }

        public static boolean evaluate(
                Role role,
                Operation operation) {

            Objects.requireNonNull(role, "Role is required.");
            Objects.requireNonNull(operation, "Operation is required.");

            return PERMISSIONS.getOrDefault(role, Set.of())
                    .contains(operation);
        }
    }

    // ========================================================
    // 6. ENTERPRISE ACCOUNT SERVICE
    // ========================================================

    public static final class AccountService {

        private static final AtomicLong ACCOUNT_SEQUENCE =
                new AtomicLong(1000);

        private final long accountId;
        private final String owner;

        private BigDecimal balance;

        private final Set<String> processedTransactions =
                new HashSet<>();

        public AccountService(
                String owner,
                BigDecimal openingBalance) {

            if (owner == null || owner.isBlank()) {
                throw new IllegalArgumentException("Owner is required.");
            }

            if (openingBalance == null ||
                    openingBalance.compareTo(BigDecimal.ZERO) < 0) {

                throw new IllegalArgumentException(
                        "Invalid opening balance.");
            }

            this.accountId = ACCOUNT_SEQUENCE.incrementAndGet();
            this.owner = owner;
            this.balance = openingBalance;
        }

        // Instance method: accesses account-specific state.
        public synchronized BigDecimal getBalance() {
            return balance;
        }

        public long getAccountId() {
            return accountId;
        }

        public String getOwner() {
            return owner;
        }

        // Static method: creates a new account independently of an instance.
        public static AccountService openAccount(
                String owner,
                BigDecimal openingBalance) {

            return new AccountService(owner, openingBalance);
        }

        public synchronized TransactionResult process(
                TransactionRequest request) {

            Objects.requireNonNull(request, "Transaction is required.");

            BigDecimal previousBalance = balance;

            if (processedTransactions.contains(request.transactionId())) {
                return new TransactionResult(
                        request.transactionId(),
                        TransactionStatus.REJECTED,
                        previousBalance,
                        previousBalance,
                        "Duplicate transaction."
                );
            }

            BigDecimal newBalance;

            if (request.type() == TransactionType.CREDIT) {
                newBalance = balance.add(request.amount());
            } else {
                if (request.amount().compareTo(balance) > 0) {
                    return new TransactionResult(
                            request.transactionId(),
                            TransactionStatus.REJECTED,
                            previousBalance,
                            previousBalance,
                            "Insufficient balance."
                    );
                }

                newBalance = balance.subtract(request.amount());
            }

            // State transition is committed only after validation.
            processedTransactions.add(request.transactionId());
            balance = newBalance;

            return new TransactionResult(
                    request.transactionId(),
                    TransactionStatus.COMPLETED,
                    previousBalance,
                    balance,
                    "Transaction completed."
            );
        }

        public static long nextAccountNumber() {
            return ACCOUNT_SEQUENCE.get() + 1;
        }
    }

    // ========================================================
    // 7. STATIC NESTED CLASS
    // ========================================================

    public static class Report {

        private final String title;
        private final String content;

        public Report(String title, String content) {
            if (title == null || title.isBlank()) {
                throw new IllegalArgumentException("Title is required.");
            }

            this.title = title;
            this.content = Objects.requireNonNull(content);
        }

        public String render() {
            return title + System.lineSeparator() + content;
        }

        // Static nested class has no implicit enclosing object.
        public static final class Builder {

            private String title;
            private String content = "";

            public Builder title(String title) {
                this.title = title;
                return this;
            }

            public Builder content(String content) {
                this.content = content;
                return this;
            }

            public Report build() {
                return new Report(title, content);
            }
        }
    }

    // ========================================================
    // 8. STATIC CACHING
    // ========================================================

    public static final class DiscountEngine {

        private static final int MAX_CACHE_SIZE = 500;

        private static final Map<String, BigDecimal> CACHE =
                new ConcurrentHashMap<>();

        private DiscountEngine() {
        }

        public static BigDecimal calculate(
                BigDecimal price,
                BigDecimal discountRate) {

            if (price == null || discountRate == null) {
                throw new IllegalArgumentException(
                        "Pricing parameters are required.");
            }

            if (price.compareTo(BigDecimal.ZERO) < 0 ||
                    discountRate.compareTo(BigDecimal.ZERO) < 0 ||
                    discountRate.compareTo(BigDecimal.ONE) > 0) {

                throw new IllegalArgumentException(
                        "Invalid pricing parameters.");
            }

            String key = price.toPlainString()
                    + ":"
                    + discountRate.toPlainString();

            BigDecimal existing = CACHE.get(key);

            if (existing != null) {
                return existing;
            }

            BigDecimal result = price.multiply(
                    BigDecimal.ONE.subtract(discountRate)
            ).setScale(2, RoundingMode.HALF_UP);

            // ConcurrentHashMap provides thread-safe individual operations.
            // This bounded insertion policy is intentionally simple.
            if (CACHE.size() < MAX_CACHE_SIZE) {
                CACHE.putIfAbsent(key, result);
            }

            return CACHE.getOrDefault(key, result);
        }

        public static int cacheSize() {
            return CACHE.size();
        }
    }

    // ========================================================
    // 9. STATIC CRYPTOGRAPHIC UTILITY
    // ========================================================

    public static final class HashService {

        private HashService() {
        }

        public static String sha256(String input) {
            Objects.requireNonNull(input, "Input is required.");

            try {
                MessageDigest digest =
                        MessageDigest.getInstance("SHA-256");

                byte[] result = digest.digest(
                        input.getBytes(StandardCharsets.UTF_8)
                );

                StringBuilder hexadecimal = new StringBuilder();

                for (byte value : result) {
                    hexadecimal.append(
                            String.format("%02x", value & 0xff)
                    );
                }

                return hexadecimal.toString();

            } catch (NoSuchAlgorithmException exception) {
                throw new IllegalStateException(
                        "SHA-256 is unavailable.",
                        exception
                );
            }
        }
    }

    // ========================================================
    // 10. STATIC ANALYTICS
    // ========================================================

    public record Statistics(
            int count,
            BigDecimal minimum,
            BigDecimal maximum,
            BigDecimal mean,
            BigDecimal median) {
    }

    public static final class AnalyticsService {

        private AnalyticsService() {
        }

        public static Statistics calculate(List<BigDecimal> values) {
            if (values == null || values.isEmpty()) {
                throw new IllegalArgumentException(
                        "At least one observation is required.");
            }

            List<BigDecimal> sorted = new ArrayList<>(values);

            if (sorted.stream().anyMatch(Objects::isNull)) {
                throw new IllegalArgumentException(
                        "Dataset contains null observations.");
            }

            Collections.sort(sorted);

            BigDecimal sum = sorted.stream()
                    .reduce(BigDecimal.ZERO, BigDecimal::add);

            int count = sorted.size();

            BigDecimal mean = sum.divide(
                    BigDecimal.valueOf(count),
                    4,
                    RoundingMode.HALF_UP
            );

            BigDecimal median;

            if (count % 2 == 0) {
                median = sorted.get(count / 2 - 1)
                        .add(sorted.get(count / 2))
                        .divide(BigDecimal.valueOf(2), 4, RoundingMode.HALF_UP);
            } else {
                median = sorted.get(count / 2);
            }

            return new Statistics(
                    count,
                    sorted.get(0),
                    sorted.get(count - 1),
                    mean,
                    median
            );
        }
    }

    // ========================================================
    // 11. STATIC CONFIGURATION VALIDATION
    // ========================================================

    public record ApplicationConfiguration(
            String application,
            String environment,
            int port) {
    }

    public static final class ConfigurationValidator {

        private static final Set<String> ENVIRONMENTS =
                Set.of("development", "testing", "production");

        private ConfigurationValidator() {
        }

        public static List<String> validate(
                ApplicationConfiguration configuration) {

            List<String> errors = new ArrayList<>();

            if (configuration == null) {
                return List.of("Configuration is required.");
            }

            if (configuration.application() == null ||
                    configuration.application().isBlank()) {

                errors.add("Application name is required.");
            }

            if (!ENVIRONMENTS.contains(configuration.environment())) {
                errors.add("Unsupported environment.");
            }

            if (!ValidationService.validPort(configuration.port())) {
                errors.add("Invalid port.");
            }

            return List.copyOf(errors);
        }
    }

    // ========================================================
    // 12. TESTING
    // ========================================================

    private static void runTests() {

        assert MathService.add(
                new BigDecimal("10"),
                new BigDecimal("20")
        ).compareTo(new BigDecimal("30")) == 0;

        assert ValidationService.validEmail("admin@example.com");
        assert !ValidationService.validEmail("invalid-email");

        assert AuthorizationPolicy.evaluate(
                Role.ANALYST,
                Operation.ANALYZE
        );

        assert !AuthorizationPolicy.evaluate(
                Role.READER,
                Operation.DELETE
        );

        AccountService account = AccountService.openAccount(
                "Research Unit",
                new BigDecimal("10000")
        );

        TransactionResult debit = account.process(
                new TransactionRequest(
                        "TX-001",
                        TransactionType.DEBIT,
                        new BigDecimal("2500")
                )
        );

        assert debit.status() == TransactionStatus.COMPLETED;

        assert account.getBalance().compareTo(
                new BigDecimal("7500")
        ) == 0;

        TransactionResult duplicate = account.process(
                new TransactionRequest(
                        "TX-001",
                        TransactionType.CREDIT,
                        new BigDecimal("500")
                )
        );

        assert duplicate.status() == TransactionStatus.REJECTED;

        assert account.getBalance().compareTo(
                new BigDecimal("7500")
        ) == 0;

        BigDecimal discounted = DiscountEngine.calculate(
                new BigDecimal("1000"),
                new BigDecimal("0.10")
        );

        assert discounted.compareTo(new BigDecimal("900.00")) == 0;

        assert HashService.sha256("repository").length() == 64;

        Statistics statistics = AnalyticsService.calculate(
                List.of(
                        new BigDecimal("10"),
                        new BigDecimal("20"),
                        new BigDecimal("30"),
                        new BigDecimal("40")
                )
        );

        assert statistics.mean().compareTo(
                new BigDecimal("25.0000")
        ) == 0;

        assert statistics.median().compareTo(
                new BigDecimal("25")
        ) == 0;

        System.out.println("All Java 17 static method tests passed.");
    }

    // ========================================================
    // 13. APPLICATION ENTRY POINT
    // ========================================================

    public static void main(String[] args) {

        System.out.println("STATIC METHODS IN JAVA 17");
        System.out.println("=========================");

        System.out.println("\n1. Mathematical utility methods");

        System.out.println(
                "Addition: " +
                MathService.add(
                        new BigDecimal("150"),
                        new BigDecimal("250")
                )
        );

        System.out.println("\n2. Employee factory");

        Employee employee = EmployeeFactory.create(
                101,
                "Aarav Sharma",
                "Research"
        );

        System.out.println(employee);

        System.out.println("\n3. Enterprise account");

        AccountService account = AccountService.openAccount(
                "Technology Division",
                new BigDecimal("100000")
        );

        System.out.println("Account number: " + account.getAccountId());

        TransactionResult transaction = account.process(
                new TransactionRequest(
                        "TX-1001",
                        TransactionType.DEBIT,
                        new BigDecimal("15000")
                )
        );

        System.out.println("Transaction status: " + transaction.status());
        System.out.println("Remaining balance: " + account.getBalance());

        System.out.println("\n4. Authorization policy");

        System.out.println(
                "Administrator can delete: " +
                AuthorizationPolicy.evaluate(
                        Role.ADMINISTRATOR,
                        Operation.DELETE
                )
        );

        System.out.println(
                "Reader can delete: " +
                AuthorizationPolicy.evaluate(
                        Role.READER,
                        Operation.DELETE
                )
        );

        System.out.println("\n5. Static nested report builder");

        Report report = new Report.Builder()
                .title("Financial Report")
                .content("Quarterly transaction processing completed.")
                .build();

        System.out.println(report.render());

        System.out.println("\n6. Static discount calculation");

        System.out.println(
                DiscountEngine.calculate(
                        new BigDecimal("50000"),
                        new BigDecimal("0.15")
                )
        );

        System.out.println("\n7. Cryptographic hashing");

        System.out.println(HashService.sha256("enterprise-data"));

        System.out.println("\n8. Analytics");

        System.out.println(
                AnalyticsService.calculate(
                        List.of(
                                new BigDecimal("100"),
                                new BigDecimal("200"),
                                new BigDecimal("300"),
                                new BigDecimal("400")
                        )
                )
        );

        System.out.println("\n9. Configuration validation");

        ApplicationConfiguration configuration =
                new ApplicationConfiguration(
                        "FinancialApplication",
                        "production",
                        8080
                );

        System.out.println(
                ConfigurationValidator.validate(configuration)
        );

        System.out.println("\n10. Automated verification");

        runTests();
    }
}
