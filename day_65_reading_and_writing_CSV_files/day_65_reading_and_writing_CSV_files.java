import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Enterprise CSV Import and Export System.
 *
 * Java 17
 *
 * Features:
 * - CSV parsing and serialization
 * - Enterprise schema validation
 * - Immutable domain records
 * - Import policies
 * - Data-quality validation
 * - Duplicate detection
 * - Audit information
 * - Atomic file export
 * - Revenue aggregation
 * - Error isolation
 * - Formula injection prevention
 */

public class Main {

    // -----------------------------------------------------
    // Configuration
    // -----------------------------------------------------

    private static final Path DATA_DIRECTORY =
            Path.of("enterprise_csv_data");

    private static final Path INPUT_FILE =
            DATA_DIRECTORY.resolve("invoices.csv");

    private static final Path OUTPUT_FILE =
            DATA_DIRECTORY.resolve("approved_invoices.csv");

    private static final Path REPORT_FILE =
            DATA_DIRECTORY.resolve("customer_report.csv");

    private static final List<String> HEADERS = List.of(
            "invoice_id",
            "customer_id",
            "customer_name",
            "amount",
            "currency",
            "status"
    );

    // -----------------------------------------------------
    // Enumerations
    // -----------------------------------------------------

    enum InvoiceStatus {
        DRAFT,
        APPROVED,
        PAID,
        REJECTED
    }

    enum ImportStatus {
        ACCEPTED,
        INVALID,
        DUPLICATE
    }

    // -----------------------------------------------------
    // Domain records
    // -----------------------------------------------------

    record Invoice(
            long invoiceId,
            long customerId,
            String customerName,
            BigDecimal amount,
            String currency,
            InvoiceStatus status
    ) {
        Invoice {
            if (invoiceId <= 0 || customerId <= 0) {
                throw new IllegalArgumentException(
                        "Identifiers must be positive"
                );
            }

            if (customerName == null || customerName.isBlank()) {
                throw new IllegalArgumentException(
                        "Customer name is required"
                );
            }

            if (amount == null || amount.signum() < 0) {
                throw new IllegalArgumentException(
                        "Amount must be non-negative"
                );
            }

            if (currency == null || !currency.matches("[A-Z]{3}")) {
                throw new IllegalArgumentException(
                        "Invalid currency code"
                );
            }

            if (status == null) {
                throw new IllegalArgumentException(
                        "Invoice status is required"
                );
            }

            amount = amount.setScale(2, RoundingMode.HALF_UP);
        }
    }

    record ImportResult(
            ImportStatus status,
            Invoice invoice,
            String message,
            int lineNumber
    ) {}

    record CustomerSummary(
            long customerId,
            String customerName,
            int invoiceCount,
            BigDecimal totalAmount
    ) {}

    // -----------------------------------------------------
    // Custom exceptions
    // -----------------------------------------------------

    static class CSVImportException extends Exception {
        CSVImportException(String message) {
            super(message);
        }
    }

    static class CSVSchemaException extends CSVImportException {
        CSVSchemaException(String message) {
            super(message);
        }
    }

    // -----------------------------------------------------
    // CSV parser
    // -----------------------------------------------------

    static final class CSVCodec {

        private CSVCodec() {}

        static List<String> parse(String line)
                throws CSVImportException {

            List<String> fields = new ArrayList<>();

            StringBuilder field = new StringBuilder();

            boolean quoted = false;

            for (int i = 0; i < line.length(); i++) {
                char current = line.charAt(i);

                if (current == '"') {
                    if (quoted &&
                            i + 1 < line.length() &&
                            line.charAt(i + 1) == '"') {

                        field.append('"');
                        i++;

                    } else {
                        quoted = !quoted;
                    }

                } else if (current == ',' && !quoted) {
                    fields.add(field.toString());
                    field.setLength(0);

                } else {
                    field.append(current);
                }
            }

            if (quoted) {
                throw new CSVImportException(
                        "Unclosed quoted field"
                );
            }

            fields.add(field.toString());

            return fields;
        }

        static String escape(String value) {
            String safe = value == null ? "" : value;

            if (safe.stripLeading().matches("^[=+\\-@].*")) {
                safe = "'" + safe;
            }

            if (safe.indexOf(',') < 0 &&
                    safe.indexOf('"') < 0 &&
                    safe.indexOf('\n') < 0 &&
                    safe.indexOf('\r') < 0) {

                return safe;
            }

            return "\"" + safe.replace("\"", "\"\"") + "\"";
        }

        static String serialize(List<String> fields) {
            return fields.stream()
                    .map(CSVCodec::escape)
                    .collect(Collectors.joining(","));
        }
    }

    // -----------------------------------------------------
    // Import policy
    // -----------------------------------------------------

    interface InvoiceImportPolicy {
        boolean accepts(Invoice invoice);
    }

    static final class EnterpriseInvoicePolicy
            implements InvoiceImportPolicy {

        private final BigDecimal maximumAmount;

        EnterpriseInvoicePolicy(BigDecimal maximumAmount) {
            this.maximumAmount = maximumAmount;
        }

        @Override
        public boolean accepts(Invoice invoice) {
            return invoice.amount().compareTo(maximumAmount) <= 0
                    && invoice.status() != InvoiceStatus.REJECTED;
        }
    }

    // -----------------------------------------------------
    // Schema validation
    // -----------------------------------------------------

    static void validateHeaders(List<String> headers)
            throws CSVSchemaException {

        if (headers.size() != HEADERS.size()) {
            throw new CSVSchemaException(
                    "Incorrect number of CSV headers"
            );
        }

        if (new HashSet<>(headers).size() != headers.size()) {
            throw new CSVSchemaException(
                    "Duplicate headers detected"
            );
        }

        if (!HEADERS.equals(headers)) {
            throw new CSVSchemaException(
                    "CSV schema does not match invoice schema"
            );
        }
    }

    // -----------------------------------------------------
    // Invoice conversion
    // -----------------------------------------------------

    static Invoice parseInvoice(List<String> fields)
            throws CSVImportException {

        if (fields.size() != HEADERS.size()) {
            throw new CSVImportException(
                    "Incorrect number of fields"
            );
        }

        try {
            return new Invoice(
                    Long.parseLong(fields.get(0).trim()),
                    Long.parseLong(fields.get(1).trim()),
                    fields.get(2).trim(),
                    new BigDecimal(fields.get(3).trim()),
                    fields.get(4).trim().toUpperCase(),
                    InvoiceStatus.valueOf(
                            fields.get(5).trim().toUpperCase()
                    )
            );

        } catch (NumberFormatException |
                 IllegalArgumentException exception) {

            throw new CSVImportException(
                    "Invalid invoice: " + exception.getMessage()
            );
        }
    }

    // -----------------------------------------------------
    // Import service
    // -----------------------------------------------------

    static final class InvoiceImportService {

        private final InvoiceImportPolicy policy;

        private final Set<Long> importedIds = new HashSet<>();

        InvoiceImportService(InvoiceImportPolicy policy) {
            this.policy = policy;
        }

        ImportResult process(
                List<String> fields,
                int lineNumber
        ) {

            Invoice invoice;

            try {
                invoice = parseInvoice(fields);
            } catch (CSVImportException exception) {
                return new ImportResult(
                        ImportStatus.INVALID,
                        null,
                        exception.getMessage(),
                        lineNumber
                );
            }

            if (!importedIds.add(invoice.invoiceId())) {
                return new ImportResult(
                        ImportStatus.DUPLICATE,
                        null,
                        "Invoice ID already imported",
                        lineNumber
                );
            }

            if (!policy.accepts(invoice)) {
                return new ImportResult(
                        ImportStatus.INVALID,
                        null,
                        "Invoice violates enterprise import policy",
                        lineNumber
                );
            }

            return new ImportResult(
                    ImportStatus.ACCEPTED,
                    invoice,
                    "Invoice accepted",
                    lineNumber
            );
        }
    }

    // -----------------------------------------------------
    // CSV repository
    // -----------------------------------------------------

    static final class InvoiceRepository {

        List<ImportResult> importFile(
                Path file,
                InvoiceImportService service
        ) throws IOException, CSVImportException {

            List<ImportResult> results = new ArrayList<>();

            try (BufferedReader reader = Files.newBufferedReader(
                    file,
                    StandardCharsets.UTF_8
            )) {

                String headerLine = reader.readLine();

                if (headerLine == null) {
                    throw new CSVSchemaException("Empty CSV file");
                }

                if (headerLine.startsWith("\uFEFF")) {
                    headerLine = headerLine.substring(1);
                }

                validateHeaders(CSVCodec.parse(headerLine));

                String line;
                int lineNumber = 1;

                while ((line = reader.readLine()) != null) {
                    lineNumber++;

                    if (line.isBlank()) {
                        continue;
                    }

                    ImportResult result = service.process(
                            CSVCodec.parse(line),
                            lineNumber
                    );

                    results.add(result);

                    if (result.status() != ImportStatus.ACCEPTED) {
                        System.err.println(
                                "Line " + lineNumber +
                                ": " + result.message()
                        );
                    }
                }
            }

            return results;
        }

        void exportAtomically(
                Path output,
                List<Invoice> invoices
        ) throws IOException {

            Path directory = output.toAbsolutePath().getParent();

            Files.createDirectories(directory);

            Path temporary = Files.createTempFile(
                    directory,
                    "invoice-export-",
                    ".tmp"
            );

            try {
                try (BufferedWriter writer = Files.newBufferedWriter(
                        temporary,
                        StandardCharsets.UTF_8
                )) {

                    writer.write(CSVCodec.serialize(HEADERS));
                    writer.newLine();

                    for (Invoice invoice : invoices) {
                        List<String> fields = List.of(
                                String.valueOf(invoice.invoiceId()),
                                String.valueOf(invoice.customerId()),
                                invoice.customerName(),
                                invoice.amount().toPlainString(),
                                invoice.currency(),
                                invoice.status().name()
                        );

                        writer.write(CSVCodec.serialize(fields));
                        writer.newLine();
                    }
                }

                try {
                    Files.move(
                            temporary,
                            output,
                            StandardCopyOption.REPLACE_EXISTING,
                            StandardCopyOption.ATOMIC_MOVE
                    );

                } catch (AtomicMoveNotSupportedException exception) {
                    Files.move(
                            temporary,
                            output,
                            StandardCopyOption.REPLACE_EXISTING
                    );
                }

            } finally {
                Files.deleteIfExists(temporary);
            }
        }
    }

    // -----------------------------------------------------
    // Reporting service
    // -----------------------------------------------------

    static final class InvoiceReportingService {

        List<CustomerSummary> summarize(List<Invoice> invoices) {

            Map<Long, List<Invoice>> grouped = invoices.stream()
                    .filter(invoice ->
                            invoice.status() == InvoiceStatus.PAID
                    )
                    .collect(Collectors.groupingBy(
                            Invoice::customerId,
                            LinkedHashMap::new,
                            Collectors.toList()
                    ));

            return grouped.entrySet()
                    .stream()
                    .map(entry -> {
                        List<Invoice> customerInvoices = entry.getValue();

                        BigDecimal total = customerInvoices.stream()
                                .map(Invoice::amount)
                                .reduce(
                                        BigDecimal.ZERO,
                                        BigDecimal::add
                                );

                        String name = customerInvoices.get(0)
                                .customerName();

                        return new CustomerSummary(
                                entry.getKey(),
                                name,
                                customerInvoices.size(),
                                total
                        );
                    })
                    .toList();
        }

        void exportReport(
                Path file,
                List<CustomerSummary> summaries
        ) throws IOException {

            List<String> headers = List.of(
                    "customer_id",
                    "customer_name",
                    "invoice_count",
                    "total_paid"
            );

            try (BufferedWriter writer = Files.newBufferedWriter(
                    file,
                    StandardCharsets.UTF_8
            )) {

                writer.write(CSVCodec.serialize(headers));
                writer.newLine();

                for (CustomerSummary summary : summaries) {
                    writer.write(CSVCodec.serialize(List.of(
                            String.valueOf(summary.customerId()),
                            summary.customerName(),
                            String.valueOf(summary.invoiceCount()),
                            summary.totalAmount().toPlainString()
                    )));

                    writer.newLine();
                }
            }
        }
    }

    // -----------------------------------------------------
    // Sample input
    // -----------------------------------------------------

    static void createSampleCSV() throws IOException {
        Files.createDirectories(DATA_DIRECTORY);

        List<List<String>> rows = List.of(
                List.of("5001", "101", "Alice Johnson",
                        "15000.00", "INR", "PAID"),

                List.of("5002", "102", "Bob Smith",
                        "22000.00", "INR", "APPROVED"),

                List.of("5003", "101", "Alice Johnson",
                        "8500.00", "INR", "PAID"),

                List.of("5004", "103", "Charlie Brown, Jr.",
                        "12500.00", "INR", "PAID"),

                List.of("5005", "102", "Bob Smith",
                        "1000000.00", "INR", "APPROVED"),

                List.of("5006", "104", "Diana Miller",
                        "-500.00", "INR", "PAID"),

                List.of("5001", "101", "Duplicate Invoice",
                        "5000.00", "INR", "PAID")
        );

        try (BufferedWriter writer = Files.newBufferedWriter(
                INPUT_FILE,
                StandardCharsets.UTF_8
        )) {

            writer.write(CSVCodec.serialize(HEADERS));
            writer.newLine();

            for (List<String> row : rows) {
                writer.write(CSVCodec.serialize(row));
                writer.newLine();
            }
        }
    }

    // -----------------------------------------------------
    // Tests
    // -----------------------------------------------------

    static void runTests() throws Exception {

        List<String> parsed = CSVCodec.parse(
                "1,\"Alice, Smith\",\"A \"\"quoted\"\" value\""
        );

        if (!parsed.get(1).equals("Alice, Smith")) {
            throw new AssertionError("Comma parsing failed");
        }

        if (!parsed.get(2).equals("A \"quoted\" value")) {
            throw new AssertionError("Quote parsing failed");
        }

        if (!CSVCodec.escape("=SUM(A1:A5)")
                .equals("'=SUM(A1:A5)")) {

            throw new AssertionError("Formula protection failed");
        }

        try {
            validateHeaders(List.of("id", "id"));

            throw new AssertionError("Duplicate headers accepted");

        } catch (CSVSchemaException expected) {
            // Expected validation failure.
        }

        try {
            parseInvoice(List.of(
                    "0", "101", "Invalid", "100", "INR", "PAID"
            ));

            throw new AssertionError("Invalid invoice accepted");

        } catch (CSVImportException expected) {
            // Expected validation failure.
        }

        System.out.println("All Java tests passed.");
    }

    // -----------------------------------------------------
    // Main
    // -----------------------------------------------------

    public static void main(String[] args) {

        try {
            runTests();

            createSampleCSV();

            InvoiceImportPolicy policy =
                    new EnterpriseInvoicePolicy(
                            new BigDecimal("500000.00")
                    );

            InvoiceImportService importService =
                    new InvoiceImportService(policy);

            InvoiceRepository repository =
                    new InvoiceRepository();

            List<ImportResult> results = repository.importFile(
                    INPUT_FILE,
                    importService
            );

            List<Invoice> accepted = results.stream()
                    .filter(result ->
                            result.status() == ImportStatus.ACCEPTED
                    )
                    .map(ImportResult::invoice)
                    .toList();

            repository.exportAtomically(
                    OUTPUT_FILE,
                    accepted
            );

            InvoiceReportingService reporting =
                    new InvoiceReportingService();

            List<CustomerSummary> summaries =
                    reporting.summarize(accepted);

            reporting.exportReport(
                    REPORT_FILE,
                    summaries
            );

            System.out.println("\nImport statistics:");

            long acceptedCount = results.stream()
                    .filter(r -> r.status() == ImportStatus.ACCEPTED)
                    .count();

            long invalidCount = results.stream()
                    .filter(r -> r.status() == ImportStatus.INVALID)
                    .count();

            long duplicateCount = results.stream()
                    .filter(r -> r.status() == ImportStatus.DUPLICATE)
                    .count();

            System.out.println("Total: " + results.size());
            System.out.println("Accepted: " + acceptedCount);
            System.out.println("Invalid: " + invalidCount);
            System.out.println("Duplicates: " + duplicateCount);

            System.out.println("\nCustomer reports:");

            summaries.forEach(System.out::println);

            System.out.println("\nGenerated files:");
            System.out.println(OUTPUT_FILE);
            System.out.println(REPORT_FILE);

        } catch (Exception exception) {
            System.err.println(
                    "Enterprise CSV processing failed: " +
                    exception.getMessage()
            );

            System.exit(1);
        }
    }
}
