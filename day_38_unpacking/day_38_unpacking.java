import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.Collectors;

/*
 * Java 17 case study: enterprise operational-record processing.
 *
 * Java does not provide Python-style sequence unpacking syntax. Record
 * patterns are not available in Java 17, so this program uses records,
 * explicit component access, collection transformations, and method
 * parameter modeling to provide a strongly typed equivalent of the
 * decomposition performed by unpacking.
 *
 * The design emphasizes immutable domain objects, validation, explicit
 * workflow states, and safe extraction of selected fields.
 */

public class UnpackingEnterpriseCaseStudy {

    enum TransactionStatus {
        COMPLETED,
        PENDING,
        CANCELLED
    }

    record Transaction(
        String id,
        String region,
        double amount,
        TransactionStatus status
    ) {
        Transaction {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                    "Transaction id cannot be empty"
                );
            }

            if (region == null || region.isBlank()) {
                throw new IllegalArgumentException(
                    "Region cannot be empty"
                );
            }

            if (!Double.isFinite(amount) || amount < 0) {
                throw new IllegalArgumentException(
                    "Amount must be finite and non-negative"
                );
            }

            Objects.requireNonNull(
                status,
                "Transaction status is required"
            );
        }
    }

    record TransactionSummary(
        String id,
        String region,
        double amount,
        String status
    ) {}

    record ProcessingReport(
        Map<String, Double> completedTotals,
        List<String> rejectedIds
    ) {}

    static final class TransactionService {

        ProcessingReport process(
            List<Transaction> transactions
        ) {
            Objects.requireNonNull(
                transactions,
                "transactions cannot be null"
            );

            Map<String, Double> totals =
                transactions.stream()
                    .filter(
                        transaction ->
                            transaction.status()
                                == TransactionStatus.COMPLETED
                    )
                    .collect(
                        Collectors.groupingBy(
                            Transaction::region,
                            Collectors.summingDouble(
                                Transaction::amount
                            )
                        )
                    );

            List<String> rejected =
                transactions.stream()
                    .filter(
                        transaction ->
                            transaction.status()
                                != TransactionStatus.COMPLETED
                            && transaction.status()
                                != TransactionStatus.PENDING
                            && transaction.status()
                                != TransactionStatus.CANCELLED
                    )
                    .map(Transaction::id)
                    .toList();

            return new ProcessingReport(
                Map.copyOf(totals),
                List.copyOf(rejected)
            );
        }

        TransactionSummary summarize(
            Transaction transaction
        ) {
            Objects.requireNonNull(
                transaction,
                "transaction cannot be null"
            );

            /*
             * Java records expose named components instead of relying on
             * positional unpacking. This keeps the field relationship
             * explicit and type-safe.
             */
            String id = transaction.id();
            String region = transaction.region();
            double amount = transaction.amount();
            String status = transaction.status().name();

            return new TransactionSummary(
                id,
                region,
                amount,
                status
            );
        }
    }

    static final class Configuration {

        private final String host;
        private final int port;
        private final boolean enabled;

        Configuration(
            String host,
            int port,
            boolean enabled
        ) {
            if (host == null || host.isBlank()) {
                throw new IllegalArgumentException(
                    "Host cannot be empty"
                );
            }

            if (port < 1 || port > 65535) {
                throw new IllegalArgumentException(
                    "Port must be between 1 and 65535"
                );
            }

            this.host = host;
            this.port = port;
            this.enabled = enabled;
        }

        String host() {
            return host;
        }

        int port() {
            return port;
        }

        boolean enabled() {
            return enabled;
        }
    }

    static Configuration validateConfiguration(
        Map<String, Object> configuration
    ) {
        Objects.requireNonNull(
            configuration,
            "configuration cannot be null"
        );

        Object hostValue = configuration.get("host");
        Object portValue = configuration.get("port");
        Object enabledValue = configuration.get("enabled");

        if (!(hostValue instanceof String host)) {
            throw new IllegalArgumentException(
                "host must be a string"
            );
        }

        if (!(portValue instanceof Integer port)) {
            throw new IllegalArgumentException(
                "port must be an integer"
            );
        }

        if (!(enabledValue instanceof Boolean enabled)) {
            throw new IllegalArgumentException(
                "enabled must be boolean"
            );
        }

        return new Configuration(
            host,
            port,
            enabled
        );
    }

    static void demonstrateRecordComponents() {
        System.out.println(
            "\n=== Record component extraction ==="
        );

        Transaction transaction =
            new Transaction(
                "TX001",
                "North",
                12500.0,
                TransactionStatus.COMPLETED
            );

        String id = transaction.id();
        String region = transaction.region();
        double amount = transaction.amount();
        TransactionStatus status = transaction.status();

        System.out.printf(
            "id=%s, region=%s, amount=%.2f, status=%s%n",
            id,
            region,
            amount,
            status
        );
    }

    static void demonstrateNestedDomainData() {
        System.out.println(
            "\n=== Nested domain data ==="
        );

        List<Transaction> transactions = List.of(
            new Transaction(
                "TX001",
                "North",
                12500.0,
                TransactionStatus.COMPLETED
            ),
            new Transaction(
                "TX002",
                "North",
                3000.0,
                TransactionStatus.PENDING
            ),
            new Transaction(
                "TX003",
                "South",
                8900.0,
                TransactionStatus.COMPLETED
            )
        );

        TransactionService service =
            new TransactionService();

        for (Transaction transaction : transactions) {
            TransactionSummary summary =
                service.summarize(transaction);

            System.out.println(summary);
        }
    }

    static void demonstrateCollectionProcessing() {
        System.out.println(
            "\n=== Collection processing ==="
        );

        List<Transaction> transactions =
            new ArrayList<>();

        transactions.add(
            new Transaction(
                "TX101",
                "North",
                1000.0,
                TransactionStatus.COMPLETED
            )
        );

        transactions.add(
            new Transaction(
                "TX102",
                "North",
                2500.0,
                TransactionStatus.COMPLETED
            )
        );

        transactions.add(
            new Transaction(
                "TX103",
                "South",
                900.0,
                TransactionStatus.COMPLETED
            )
        );

        transactions.add(
            new Transaction(
                "TX104",
                "South",
                700.0,
                TransactionStatus.CANCELLED
            )
        );

        TransactionService service =
            new TransactionService();

        ProcessingReport report =
            service.process(transactions);

        report.completedTotals()
            .forEach(
                (region, total) ->
                    System.out.printf(
                        "%s => %.2f%n",
                        region,
                        total
                    )
            );

        System.out.println(
            "Rejected ids: "
                + report.rejectedIds()
        );
    }

    static void demonstrateMapExtraction() {
        System.out.println(
            "\n=== Map field extraction ==="
        );

        Map<String, Object> rawConfiguration =
            Map.of(
                "host",
                "api.internal",
                "port",
                8443,
                "enabled",
                true
            );

        Configuration configuration =
            validateConfiguration(
                rawConfiguration
            );

        System.out.println(
            "host=" + configuration.host()
                + ", port=" + configuration.port()
                + ", enabled=" + configuration.enabled()
        );
    }

    static void demonstrateValidationFailure() {
        System.out.println(
            "\n=== Validation failure ==="
        );

        try {
            new Transaction(
                "",
                "North",
                100.0,
                TransactionStatus.COMPLETED
            );
        } catch (IllegalArgumentException error) {
            System.out.println(
                "Rejected transaction: "
                    + error.getMessage()
            );
        }

        try {
            validateConfiguration(
                Map.of(
                    "host",
                    "api.internal",
                    "port",
                    70000,
                    "enabled",
                    true
                )
            );
        } catch (IllegalArgumentException error) {
            System.out.println(
                "Rejected configuration: "
                    + error.getMessage()
            );
        }
    }

    static void demonstrateStreamDecomposition() {
        System.out.println(
            "\n=== Stream-based decomposition ==="
        );

        List<Transaction> transactions = List.of(
            new Transaction(
                "TX201",
                "North",
                100.0,
                TransactionStatus.COMPLETED
            ),
            new Transaction(
                "TX202",
                "South",
                200.0,
                TransactionStatus.COMPLETED
            ),
            new Transaction(
                "TX203",
                "North",
                300.0,
                TransactionStatus.COMPLETED
            )
        );

        Map<String, List<Transaction>> grouped =
            transactions.stream()
                .collect(
                    Collectors.groupingBy(
                        Transaction::region
                    )
                );

        grouped.forEach(
            (region, records) -> {
                double total =
                    records.stream()
                        .mapToDouble(
                            Transaction::amount
                        )
                        .sum();

                System.out.printf(
                    "%s: %.2f%n",
                    region,
                    total
                );
            }
        );
    }

    public static void main(String[] args) {
        demonstrateRecordComponents();
        demonstrateNestedDomainData();
        demonstrateCollectionProcessing();
        demonstrateMapExtraction();
        demonstrateValidationFailure();
        demonstrateStreamDecomposition();

        System.out.println(
            "\nEnterprise case study completed."
        );
    }
}
