import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class Main {

    enum AccountStatus {
        ACTIVE,
        FROZEN,
        CLOSED
    }

    enum TransactionType {
        DEPOSIT,
        WITHDRAWAL,
        INTEREST
    }

    static class DomainException extends RuntimeException {
        public DomainException(String message) {
            super(message);
        }
    }

    record Transaction(
        long id,
        TransactionType type,
        double amount,
        double balanceAfter,
        long timestamp
    ) {}

    interface Auditable {
        List<Transaction> getTransactions();
    }

    interface AccountOperations {
        double deposit(double amount);
        double withdraw(double amount);
        double availableBalance();
    }

    abstract static class Account
            implements AccountOperations, Auditable {

        private static final AtomicLong ID_GENERATOR =
            new AtomicLong(1000);

        private final long accountId;
        private final String owner;
        private double balance;
        private AccountStatus status;
        private final List<Transaction> transactions =
            new ArrayList<>();

        protected Account(String owner, double openingBalance) {
            if (owner == null || owner.isBlank()) {
                throw new DomainException("Owner is required.");
            }

            validateAmount(openingBalance, true);

            this.accountId = ID_GENERATOR.incrementAndGet();
            this.owner = owner.trim();
            this.balance = openingBalance;
            this.status = AccountStatus.ACTIVE;
        }

        public long getAccountId() {
            return accountId;
        }

        public String getOwner() {
            return owner;
        }

        public synchronized double getBalance() {
            return balance;
        }

        public synchronized AccountStatus getStatus() {
            return status;
        }

        protected static double validateAmount(
                double amount,
                boolean allowZero) {

            if (!Double.isFinite(amount) ||
                (allowZero ? amount < 0 : amount <= 0)) {
                throw new DomainException("Invalid monetary amount.");
            }

            return Math.round(amount * 100.0) / 100.0;
        }

        protected synchronized void ensureActive() {
            if (status != AccountStatus.ACTIVE) {
                throw new DomainException(
                    "Account is " + status + "."
                );
            }
        }

        protected synchronized void record(
                TransactionType type,
                double amount) {

            transactions.add(new Transaction(
                transactions.size() + 1L,
                type,
                amount,
                balance,
                System.currentTimeMillis()
            ));
        }

        @Override
        public synchronized double deposit(double amount) {
            ensureActive();
            amount = validateAmount(amount, false);

            balance = Math.round((balance + amount) * 100.0) / 100.0;
            record(TransactionType.DEPOSIT, amount);

            return balance;
        }

        @Override
        public synchronized double withdraw(double amount) {
            ensureActive();
            amount = validateAmount(amount, false);

            if (amount > availableBalance()) {
                throw new DomainException("Insufficient funds.");
            }

            balance = Math.round((balance - amount) * 100.0) / 100.0;
            record(TransactionType.WITHDRAWAL, amount);

            return balance;
        }

        @Override
        public synchronized List<Transaction> getTransactions() {
            return List.copyOf(transactions);
        }

        public synchronized void freeze() {
            ensureActive();
            status = AccountStatus.FROZEN;
        }

        public synchronized void unfreeze() {
            if (status != AccountStatus.FROZEN) {
                throw new DomainException("Account is not frozen.");
            }

            status = AccountStatus.ACTIVE;
        }

        public synchronized void close() {
            if (status == AccountStatus.CLOSED || balance != 0) {
                throw new DomainException(
                    "Account must have zero balance before closing."
                );
            }

            status = AccountStatus.CLOSED;
        }

        public abstract String getAccountType();

        public synchronized Map<String, Object> toMap() {
            Map<String, Object> result = new LinkedHashMap<>();

            result.put("id", accountId);
            result.put("owner", owner);
            result.put("balance", balance);
            result.put("status", status);
            result.put("type", getAccountType());
            result.put("transactions", getTransactions());

            return Collections.unmodifiableMap(result);
        }
    }

    static final class SavingsAccount extends Account {

        private final double minimumBalance;
        private final double interestRate;

        public SavingsAccount(
                String owner,
                double openingBalance,
                double minimumBalance,
                double interestRate) {

            super(owner, openingBalance);

            if (!Double.isFinite(minimumBalance) ||
                minimumBalance < 0 ||
                !Double.isFinite(interestRate) ||
                interestRate < 0 ||
                interestRate > 1) {
                throw new DomainException(
                    "Invalid savings account configuration."
                );
            }

            this.minimumBalance = minimumBalance;
            this.interestRate = interestRate;
        }

        @Override
        public synchronized double availableBalance() {
            return Math.max(0, getBalance() - minimumBalance);
        }

        @Override
        public String getAccountType() {
            return "SAVINGS";
        }

        public synchronized double applyInterest() {
            ensureActive();

            double interest = Math.round(
                getBalance() * interestRate * 100.0
            ) / 100.0;

            if (interest > 0) {
                deposit(interest);
            }

            return interest;
        }
    }

    static final class CurrentAccount extends Account {

        private final double overdraftLimit;

        public CurrentAccount(
                String owner,
                double openingBalance,
                double overdraftLimit) {

            super(owner, openingBalance);

            if (!Double.isFinite(overdraftLimit) ||
                overdraftLimit < 0) {
                throw new DomainException("Invalid overdraft limit.");
            }

            this.overdraftLimit = overdraftLimit;
        }

        @Override
        public synchronized double availableBalance() {
            return getBalance() + overdraftLimit;
        }

        @Override
        public String getAccountType() {
            return "CURRENT";
        }
    }

    static class AccountRepository<T extends Account> {

        private final Map<Long, T> accounts =
            new ConcurrentHashMap<>();

        public void save(T account) {
            Objects.requireNonNull(account, "Account cannot be null.");

            T previous = accounts.putIfAbsent(
                account.getAccountId(),
                account
            );

            if (previous != null) {
                throw new DomainException("Duplicate account.");
            }
        }

        public T find(long id) {
            T account = accounts.get(id);

            if (account == null) {
                throw new DomainException("Account not found.");
            }

            return account;
        }

        public List<T> findAll() {
            return accounts.values()
                .stream()
                .sorted(Comparator.comparingLong(Account::getAccountId))
                .toList();
        }

        public int count() {
            return accounts.size();
        }
    }

    static class TransferService {

        public void transfer(
                Account source,
                Account destination,
                double amount) {

            Objects.requireNonNull(source);
            Objects.requireNonNull(destination);

            if (source == destination) {
                throw new DomainException(
                    "Source and destination must differ."
                );
            }

            Account first = source.getAccountId() <
                destination.getAccountId() ? source : destination;

            Account second = first == source ? destination : source;

            // Lock in a consistent order to reduce deadlock risk.
            synchronized (first) {
                synchronized (second) {
                    if (source.getStatus() != AccountStatus.ACTIVE ||
                        destination.getStatus() != AccountStatus.ACTIVE) {
                        throw new DomainException(
                            "Both accounts must be active."
                        );
                    }

                    Account.validateAmount(amount, false);

                    if (amount > source.availableBalance()) {
                        throw new DomainException("Insufficient funds.");
                    }

                    // A production transfer requires a database transaction.
                    double sourceBefore = source.getBalance();
                    double destinationBefore = destination.getBalance();

                    try {
                        source.withdraw(amount);
                        destination.deposit(amount);
                    } catch (RuntimeException exception) {
                        throw new DomainException(
                            "Transfer failed. Reconciliation required: " +
                            sourceBefore + " / " + destinationBefore
                        );
                    }
                }
            }
        }
    }

    static class ReportingService {

        public void printReport(
                AccountRepository<Account> repository) {

            System.out.println("\nACCOUNT REPORT");

            repository.findAll().forEach(account ->
                System.out.println(account.toMap())
            );

            double total = repository.findAll()
                .stream()
                .mapToDouble(Account::getBalance)
                .sum();

            System.out.printf(
                "Aggregate balance: %.2f%n",
                total
            );
        }
    }

    public static void main(String[] args) {

        AccountRepository<Account> repository =
            new AccountRepository<>();

        SavingsAccount savings = new SavingsAccount(
            "Aarav Sharma", 25000, 1000, 0.05
        );

        CurrentAccount current = new CurrentAccount(
            "Meera Verma", 10000, 5000
        );

        repository.save(savings);
        repository.save(current);

        savings.applyInterest();

        TransferService transferService = new TransferService();

        transferService.transfer(savings, current, 5000);

        ReportingService reportingService =
            new ReportingService();

        reportingService.printReport(repository);

        System.out.println(
            "\nRegistered accounts: " + repository.count()
        );

        try {
            savings.withdraw(100000);
        } catch (DomainException exception) {
            System.out.println(
                "Expected failure: " + exception.getMessage()
            );
        }

        try {
            new SavingsAccount("", 1000, 100, 0.05);
        } catch (DomainException exception) {
            System.out.println(
                "Constructor validation: " + exception.getMessage()
            );
        }

        current.withdraw(15000);
        current.close();

        System.out.println(
            "Final current-account state: " + current.getStatus()
        );
    }
}
