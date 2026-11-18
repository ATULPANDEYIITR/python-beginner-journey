import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * ATTRIBUTES AND METHODS
 *
 * Enterprise-oriented object-oriented banking model.
 *
 * Demonstrates:
 * - Instance attributes
 * - Static attributes
 * - Private, protected and public access
 * - Immutable records
 * - Instance methods
 * - Static methods
 * - Final methods
 * - Inheritance
 * - Interfaces
 * - Method overriding
 * - Polymorphism
 * - Composition
 * - Generic repository
 * - Policy objects
 * - Validation
 * - State transitions
 * - Custom exceptions
 * - Immutable transaction history
 */

public class Main {

    // -----------------------------------------------------
    // ENUMERATIONS
    // -----------------------------------------------------

    enum AccountStatus {
        ACTIVE,
        FROZEN,
        CLOSED
    }

    enum TransactionType {
        DEPOSIT,
        WITHDRAWAL,
        TRANSFER_IN,
        TRANSFER_OUT
    }

    // -----------------------------------------------------
    // CUSTOM EXCEPTIONS
    // -----------------------------------------------------

    static class AccountException extends RuntimeException {
        public AccountException(String message) {
            super(message);
        }
    }

    static class ValidationException extends AccountException {
        public ValidationException(String message) {
            super(message);
        }
    }

    static class InsufficientFundsException extends AccountException {
        public InsufficientFundsException(String message) {
            super(message);
        }
    }

    static class StateTransitionException extends AccountException {
        public StateTransitionException(String message) {
            super(message);
        }
    }

    // -----------------------------------------------------
    // IMMUTABLE DATA TYPES
    // -----------------------------------------------------

    record Transaction(
        UUID transactionId,
        TransactionType type,
        BigDecimal amount,
        BigDecimal balanceAfter,
        Instant timestamp
    ) {
        Transaction {
            Objects.requireNonNull(transactionId);
            Objects.requireNonNull(type);
            Objects.requireNonNull(amount);
            Objects.requireNonNull(balanceAfter);
            Objects.requireNonNull(timestamp);
        }
    }

    record AccountSnapshot(
        String accountNumber,
        String owner,
        BigDecimal balance,
        AccountStatus status,
        String accountType
    ) {}

    // -----------------------------------------------------
    // INTERFACE
    // -----------------------------------------------------

    interface InterestBearing {
        BigDecimal calculateInterest();

        BigDecimal applyInterest();
    }

    // -----------------------------------------------------
    // POLICY OBJECT
    // -----------------------------------------------------

    static final class AccountPolicy {

        private final BigDecimal minimumBalance;
        private final BigDecimal maximumTransaction;

        AccountPolicy(
            BigDecimal minimumBalance,
            BigDecimal maximumTransaction
        ) {
            this.minimumBalance = validateMoney(minimumBalance);
            this.maximumTransaction = validateMoney(maximumTransaction);

            if (this.minimumBalance.signum() < 0 ||
                this.maximumTransaction.signum() <= 0) {
                throw new ValidationException(
                    "Invalid account policy."
                );
            }
        }

        void validateTransaction(BigDecimal amount) {
            validatePositiveAmount(amount);

            if (amount.compareTo(maximumTransaction) > 0) {
                throw new ValidationException(
                    "Transaction exceeds the configured limit."
                );
            }
        }

        void validateWithdrawal(
            BigDecimal balance,
            BigDecimal amount
        ) {
            if (balance.subtract(amount).compareTo(minimumBalance) < 0) {
                throw new InsufficientFundsException(
                    "Minimum balance requirement violated."
                );
            }
        }

        static AccountPolicy standard() {
            return new AccountPolicy(
                new BigDecimal("0.00"),
                new BigDecimal("1000000.00")
            );
        }
    }

    // -----------------------------------------------------
    // GENERIC REPOSITORY
    // -----------------------------------------------------

    static final class AccountRepository<T extends BankAccount> {

        private final Map<String, T> accounts = new HashMap<>();

        public void save(T account) {
            Objects.requireNonNull(account);

            if (accounts.containsKey(account.accountNumber())) {
                throw new ValidationException(
                    "Account number already registered."
                );
            }

            accounts.put(account.accountNumber(), account);
        }

        public Optional<T> findById(String accountNumber) {
            return Optional.ofNullable(accounts.get(accountNumber));
        }

        public List<T> findAll() {
            return List.copyOf(accounts.values());
        }

        public int size() {
            return accounts.size();
        }
    }

    // -----------------------------------------------------
    // BASE DOMAIN CLASS
    // -----------------------------------------------------

    static class BankAccount {

        // Static attributes belong to the class.
        public static String bankName = "National Digital Bank";

        private static final AtomicInteger ACCOUNT_COUNT =
            new AtomicInteger();

        // Instance attributes belong to individual objects.
        private final String accountNumber;
        private final String owner;

        private BigDecimal balance;
        private AccountStatus status;

        private final AccountPolicy policy;

        private final List<Transaction> transactionHistory =
            new ArrayList<>();

        protected final String currency = "INR";

        BankAccount(
            String accountNumber,
            String owner,
            BigDecimal initialBalance,
            AccountPolicy policy
        ) {
            this.accountNumber = requireText(
                accountNumber,
                "Account number"
            );

            this.owner = requireText(owner, "Owner");

            this.balance = validateMoney(initialBalance);

            if (this.balance.signum() < 0) {
                throw new ValidationException(
                    "Initial balance cannot be negative."
                );
            }

            this.policy = Objects.requireNonNull(policy);
            this.status = AccountStatus.ACTIVE;

            ACCOUNT_COUNT.incrementAndGet();
        }

        // -------------------------------------------------
        // STATIC METHODS
        // -------------------------------------------------

        public static int accountCount() {
            return ACCOUNT_COUNT.get();
        }

        public static void changeBankName(String name) {
            bankName = requireText(name, "Bank name");
        }

        public static BigDecimal validateMoney(BigDecimal value) {
            Objects.requireNonNull(value, "Amount is required.");

            try {
                return value.setScale(2, RoundingMode.UNNECESSARY);
            } catch (ArithmeticException exception) {
                throw new ValidationException(
                    "Amounts support two decimal places."
                );
            }
        }

        public static void validatePositiveAmount(BigDecimal amount) {
            BigDecimal normalized = validateMoney(amount);

            if (normalized.signum() <= 0) {
                throw new ValidationException(
                    "Amount must be positive."
                );
            }
        }

        private static String requireText(
            String value,
            String field
        ) {
            if (value == null || value.isBlank()) {
                throw new ValidationException(
                    field + " cannot be empty."
                );
            }

            return value.trim();
        }

        // -------------------------------------------------
        // GETTER METHODS
        // -------------------------------------------------

        public final String accountNumber() {
            return accountNumber;
        }

        public final String owner() {
            return owner;
        }

        public final BigDecimal balance() {
            return balance;
        }

        public final AccountStatus status() {
            return status;
        }

        public final List<Transaction> transactionHistory() {
            return Collections.unmodifiableList(
                new ArrayList<>(transactionHistory)
            );
        }

        // -------------------------------------------------
        // INTERNAL METHODS
        // -------------------------------------------------

        private void ensureActive() {
            if (status != AccountStatus.ACTIVE) {
                throw new StateTransitionException(
                    "Account is " + status + "."
                );
            }
        }

        private void record(
            TransactionType type,
            BigDecimal amount
        ) {
            transactionHistory.add(
                new Transaction(
                    UUID.randomUUID(),
                    type,
                    amount,
                    balance,
                    Instant.now()
                )
            );
        }

        // -------------------------------------------------
        // INSTANCE METHODS
        // -------------------------------------------------

        public synchronized void deposit(BigDecimal amount) {
            ensureActive();

            amount = validateMoney(amount);
            policy.validateTransaction(amount);

            balance = balance.add(amount);

            record(TransactionType.DEPOSIT, amount);
        }

        public synchronized void withdraw(BigDecimal amount) {
            ensureActive();

            amount = validateMoney(amount);
            policy.validateTransaction(amount);

            policy.validateWithdrawal(balance, amount);

            balance = balance.subtract(amount);

            record(TransactionType.WITHDRAWAL, amount);
        }

        /**
         * Synchronized instance method.
         * Both account locks are acquired in stable order to
         * reduce deadlock risk.
         */
        public void transferTo(
            BankAccount destination,
            BigDecimal amount
        ) {
            Objects.requireNonNull(destination);

            if (destination == this) {
                throw new ValidationException(
                    "Self-transfer is prohibited."
                );
            }

            amount = validateMoney(amount);

            BankAccount first =
                accountNumber.compareTo(destination.accountNumber) < 0
                    ? this : destination;

            BankAccount second = first == this
                    ? destination : this;

            synchronized (first) {
                synchronized (second) {
                    ensureActive();
                    destination.ensureActive();

                    policy.validateTransaction(amount);
                    destination.policy.validateTransaction(amount);

                    policy.validateWithdrawal(balance, amount);

                    BigDecimal sourceBefore = balance;
                    BigDecimal destinationBefore =
                        destination.balance;

                    try {
                        balance = balance.subtract(amount);
                        destination.balance =
                            destination.balance.add(amount);

                        record(
                            TransactionType.TRANSFER_OUT,
                            amount
                        );

                        destination.record(
                            TransactionType.TRANSFER_IN,
                            amount
                        );

                    } catch (RuntimeException exception) {
                        balance = sourceBefore;
                        destination.balance = destinationBefore;

                        throw exception;
                    }
                }
            }
        }

        public synchronized void freeze() {
            if (status == AccountStatus.CLOSED) {
                throw new StateTransitionException(
                    "Closed account cannot be frozen."
                );
            }

            status = AccountStatus.FROZEN;
        }

        public synchronized void unfreeze() {
            if (status != AccountStatus.FROZEN) {
                throw new StateTransitionException(
                    "Only frozen accounts can be activated."
                );
            }

            status = AccountStatus.ACTIVE;
        }

        public synchronized void close() {
            if (balance.signum() != 0) {
                throw new StateTransitionException(
                    "Account must have zero balance."
                );
            }

            status = AccountStatus.CLOSED;
        }

        // -------------------------------------------------
        // POLYMORPHIC METHODS
        // -------------------------------------------------

        public String accountType() {
            return "STANDARD";
        }

        public AccountSnapshot snapshot() {
            return new AccountSnapshot(
                accountNumber,
                owner,
                balance,
                status,
                accountType()
            );
        }

        public void display() {
            System.out.println(snapshot());
        }
    }

    // -----------------------------------------------------
    // INHERITANCE AND INTERFACE IMPLEMENTATION
    // -----------------------------------------------------

    static final class SavingsAccount
        extends BankAccount
        implements InterestBearing {

        private final BigDecimal interestRate;

        SavingsAccount(
            String accountNumber,
            String owner,
            BigDecimal initialBalance,
            BigDecimal interestRate,
            AccountPolicy policy
        ) {
            super(
                accountNumber,
                owner,
                initialBalance,
                policy
            );

            this.interestRate = validateMoney(interestRate);

            if (
                this.interestRate.signum() < 0 ||
                this.interestRate.compareTo(
                    new BigDecimal("100.00")
                ) > 0
            ) {
                throw new ValidationException(
                    "Interest rate must be between 0 and 100."
                );
            }
        }

        @Override
        public BigDecimal calculateInterest() {
            return balance()
                .multiply(interestRate)
                .divide(
                    new BigDecimal("100"),
                    2,
                    RoundingMode.HALF_UP
                );
        }

        @Override
        public BigDecimal applyInterest() {
            BigDecimal interest = calculateInterest();

            if (interest.signum() > 0) {
                deposit(interest);
            }

            return interest;
        }

        @Override
        public String accountType() {
            return "SAVINGS";
        }

        @Override
        public AccountSnapshot snapshot() {
            return super.snapshot();
        }

        public BigDecimal interestRate() {
            return interestRate;
        }
    }

    // -----------------------------------------------------
    // APPLICATION ENTRY POINT
    // -----------------------------------------------------

    public static void main(String[] args) {

        System.out.println("ATTRIBUTES AND METHODS");
        System.out.println("======================");

        AccountPolicy policy = AccountPolicy.standard();

        AccountRepository<BankAccount> repository =
            new AccountRepository<>();

        BankAccount current = new BankAccount(
            "ACC1001",
            "Rahul Sharma",
            new BigDecimal("50000.00"),
            policy
        );

        SavingsAccount savings = new SavingsAccount(
            "ACC1002",
            "Priya Verma",
            new BigDecimal("75000.00"),
            new BigDecimal("5.00"),
            policy
        );

        repository.save(current);
        repository.save(savings);

        System.out.println("\nInstance attributes:");
        System.out.println(current.accountNumber());
        System.out.println(current.owner());
        System.out.println(current.balance());

        System.out.println("\nStatic attributes:");
        System.out.println(BankAccount.bankName);
        System.out.println(BankAccount.accountCount());

        System.out.println("\nInstance methods:");

        current.deposit(new BigDecimal("5000.00"));
        current.withdraw(new BigDecimal("2000.00"));

        System.out.println(current.balance());

        System.out.println("\nStatic methods:");

        BankAccount.changeBankName(
            "Enterprise Banking Group"
        );

        System.out.println(BankAccount.bankName);

        System.out.println("\nInheritance and polymorphism:");

        for (BankAccount account : repository.findAll()) {
            account.display();
        }

        System.out.println("\nInterface methods:");

        BigDecimal interest = savings.applyInterest();

        System.out.println("Interest applied: " + interest);
        System.out.println("Savings balance: " + savings.balance());

        System.out.println("\nAccount transfer:");

        current.transferTo(
            savings,
            new BigDecimal("3000.00")
        );

        System.out.println("Source: " + current.balance());
        System.out.println("Destination: " + savings.balance());

        System.out.println("\nRepository methods:");

        Optional<BankAccount> result =
            repository.findById("ACC1001");

        System.out.println("Account found: " + result.isPresent());
        System.out.println("Repository size: " + repository.size());

        System.out.println("\nValidation:");

        try {
            current.withdraw(new BigDecimal("1000000.00"));
        } catch (AccountException exception) {
            System.out.println(exception.getMessage());
        }

        try {
            current.deposit(new BigDecimal("-500.00"));
        } catch (AccountException exception) {
            System.out.println(exception.getMessage());
        }

        System.out.println("\nState transitions:");

        current.freeze();

        try {
            current.deposit(new BigDecimal("100.00"));
        } catch (AccountException exception) {
            System.out.println(exception.getMessage());
        }

        current.unfreeze();

        if (
            current.balance().compareTo(
                new BigDecimal("50000.00")
            ) != 0
        ) {
            throw new AssertionError("Incorrect current balance.");
        }

        if (
            savings.balance().compareTo(
                new BigDecimal("81125.00")
            ) != 0
        ) {
            throw new AssertionError("Incorrect savings balance.");
        }

        if (current.transactionHistory().size() != 3) {
            throw new AssertionError("Incorrect transaction history.");
        }

        if (current.status() != AccountStatus.ACTIVE) {
            throw new AssertionError("Incorrect account state.");
        }

        System.out.println("\nAll assertions passed.");

        System.out.println("\nTransaction history:");

        for (Transaction transaction : current.transactionHistory()) {
            System.out.println(transaction);
        }
    }
}
