import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.DirectoryStream;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.BasicFileAttributes;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

public class FileExceptionPractice {

    enum ProcessingState {
        RECEIVED,
        VALIDATED,
        PROCESSED,
        REJECTED
    }

    static class FileWorkflowException extends Exception {
        FileWorkflowException(String message) {
            super(message);
        }

        FileWorkflowException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    static class ValidationException extends FileWorkflowException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class StorageException extends FileWorkflowException {
        StorageException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    static class DataFormatException extends FileWorkflowException {
        DataFormatException(String message) {
            super(message);
        }
    }

    record ImportRecord(
        int id,
        String department,
        String employee,
        double amount
    ) {
        ImportRecord {
            if (id <= 0) {
                throw new IllegalArgumentException(
                    "Record ID must be positive."
                );
            }

            if (department == null || department.isBlank()) {
                throw new IllegalArgumentException(
                    "Department cannot be empty."
                );
            }

            if (employee == null || employee.isBlank()) {
                throw new IllegalArgumentException(
                    "Employee cannot be empty."
                );
            }

            if (!Double.isFinite(amount) || amount < 0) {
                throw new IllegalArgumentException(
                    "Amount must be finite and non-negative."
                );
            }
        }
    }

    record ProcessingResult(
        int recordId,
        ProcessingState state,
        String message
    ) {}

    interface RecordValidator {
        void validate(ImportRecord record)
            throws ValidationException;
    }

    static class ExpensePolicy implements RecordValidator {
        private final double maximumAmount;
        private final Set<String> permittedDepartments;

        ExpensePolicy(
            double maximumAmount,
            Set<String> permittedDepartments
        ) {
            if (!Double.isFinite(maximumAmount) || maximumAmount <= 0) {
                throw new IllegalArgumentException(
                    "Maximum amount must be positive."
                );
            }

            this.maximumAmount = maximumAmount;
            this.permittedDepartments = Set.copyOf(
                permittedDepartments
            );
        }

        @Override
        public void validate(ImportRecord record)
            throws ValidationException {

            if (!permittedDepartments.contains(record.department())) {
                throw new ValidationException(
                    "Department is not authorized."
                );
            }

            if (record.amount() > maximumAmount) {
                throw new ValidationException(
                    "Expense exceeds the permitted amount."
                );
            }
        }
    }

    static class CsvImportService {
        private final RecordValidator validator;

        CsvImportService(RecordValidator validator) {
            this.validator = validator;
        }

        List<ProcessingResult> importFile(Path file)
            throws FileWorkflowException {

            List<ProcessingResult> results = new ArrayList<>();

            try (BufferedReader reader = Files.newBufferedReader(
                file, StandardCharsets.UTF_8
            )) {
                String header = reader.readLine();

                if (header == null ||
                    !header.equals("id,department,employee,amount")) {
                    throw new DataFormatException(
                        "Unexpected CSV header."
                    );
                }

                String line;
                int lineNumber = 1;

                while ((line = reader.readLine()) != null) {
                    lineNumber++;

                    if (line.isBlank()) {
                        continue;
                    }

                    try {
                        ImportRecord record = parse(line);
                        validator.validate(record);

                        results.add(new ProcessingResult(
                            record.id(),
                            ProcessingState.PROCESSED,
                            "Validated and accepted"
                        ));
                    } catch (
                        IllegalArgumentException |
                        ValidationException exception
                    ) {
                        results.add(new ProcessingResult(
                            -lineNumber,
                            ProcessingState.REJECTED,
                            exception.getMessage()
                        ));
                    }
                }

                return results;

            } catch (IOException exception) {
                throw new StorageException(
                    "Unable to import CSV file.", exception
                );
            }
        }

        private ImportRecord parse(String line)
            throws DataFormatException {

            // This demonstration accepts simple unquoted CSV fields.
            String[] fields = line.split(",", -1);

            if (fields.length != 4) {
                throw new DataFormatException(
                    "Expected four CSV fields."
                );
            }

            try {
                return new ImportRecord(
                    Integer.parseInt(fields[0].trim()),
                    fields[1].trim(),
                    fields[2].trim(),
                    Double.parseDouble(fields[3].trim())
                );
            } catch (NumberFormatException exception) {
                throw new DataFormatException(
                    "Invalid numeric CSV field."
                );
            }
        }
    }

    static class AtomicFileWriter {

        static void write(Path destination, String content)
            throws StorageException {

            Path parent = destination.toAbsolutePath().getParent();
            Path temporary = null;

            try {
                Files.createDirectories(parent);

                temporary = Files.createTempFile(
                    parent,
                    "workflow-",
                    ".tmp"
                );

                try (BufferedWriter writer = Files.newBufferedWriter(
                    temporary,
                    StandardCharsets.UTF_8,
                    StandardOpenOption.TRUNCATE_EXISTING
                )) {
                    writer.write(content);
                }

                try {
                    Files.move(
                        temporary,
                        destination,
                        StandardCopyOption.ATOMIC_MOVE,
                        StandardCopyOption.REPLACE_EXISTING
                    );
                } catch (AtomicMoveNotSupportedException exception) {
                    Files.move(
                        temporary,
                        destination,
                        StandardCopyOption.REPLACE_EXISTING
                    );
                }

            } catch (IOException exception) {
                throw new StorageException(
                    "Atomic file write failed.", exception
                );
            } finally {
                if (temporary != null) {
                    try {
                        Files.deleteIfExists(temporary);
                    } catch (IOException ignored) {
                        // Cleanup failure must not hide the original error.
                    }
                }
            }
        }
    }

    static class AuditLogger {
        private final Path auditFile;

        AuditLogger(Path auditFile) {
            this.auditFile = auditFile;
        }

        void append(String event) throws StorageException {
            String safeEvent = event.replace("\n", " ")
                                    .replace("\r", " ");

            String entry = Instant.now() + " | " + safeEvent
                + System.lineSeparator();

            try {
                Files.createDirectories(auditFile.toAbsolutePath().getParent());

                Files.writeString(
                    auditFile,
                    entry,
                    StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE,
                    StandardOpenOption.APPEND
                );
            } catch (IOException exception) {
                throw new StorageException(
                    "Audit append failed.", exception
                );
            }
        }
    }

    static class DirectoryScanner {

        static Map<String, Integer> countExtensions(Path root)
            throws IOException {

            Map<String, Integer> counts = new HashMap<>();

            try (var paths = Files.walk(root)) {
                paths.filter(Files::isRegularFile)
                     .forEach(file -> {
                         String name = file.getFileName().toString();
                         int position = name.lastIndexOf('.');
                         String extension = position >= 0
                             ? name.substring(position).toLowerCase()
                             : "[no extension]";

                         counts.merge(extension, 1, Integer::sum);
                     });
            }

            return counts;
        }
    }

    static String sha256(Path file)
        throws StorageException {

        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");

            try (var input = Files.newInputStream(file)) {
                byte[] buffer = new byte[8192];
                int bytesRead;

                while ((bytesRead = input.read(buffer)) != -1) {
                    digest.update(buffer, 0, bytesRead);
                }
            }

            StringBuilder result = new StringBuilder();

            for (byte value : digest.digest()) {
                result.append(String.format("%02x", value));
            }

            return result.toString();

        } catch (IOException | NoSuchAlgorithmException exception) {
            throw new StorageException(
                "Hash calculation failed.", exception
            );
        }
    }

    static void runTests(Path root) throws Exception {
        Path file = root.resolve("test.txt");

        AtomicFileWriter.write(file, "first version");
        AtomicFileWriter.write(file, "second version");

        String content = Files.readString(file);

        if (!content.equals("second version")) {
            throw new AssertionError("Atomic write test failed.");
        }

        try {
            new ImportRecord(0, "IT", "Employee", 100);
            throw new AssertionError("Invalid record was accepted.");
        } catch (IllegalArgumentException expected) {
            // Expected validation failure.
        }

        System.out.println("All tests passed.");
    }

    public static void main(String[] args) {
        Path root = null;

        try {
            root = Files.createTempDirectory("java-file-practice");

            Path input = root.resolve("expenses.csv");

            String csv = """
                id,department,employee,amount
                1,IT,Aarav,1200
                2,FINANCE,Meera,4500
                3,HR,Rohan,800
                4,IT,Anaya,-50
                5,IT,Kabir,25000
                invalid,IT,Employee,100
                """;

            Files.writeString(
                input,
                csv,
                StandardCharsets.UTF_8
            );

            ExpensePolicy policy = new ExpensePolicy(
                10000,
                Set.of("IT", "FINANCE")
            );

            CsvImportService service = new CsvImportService(policy);

            List<ProcessingResult> results =
                service.importFile(input);

            Map<ProcessingState, Long> totals = results.stream()
                .collect(Collectors.groupingBy(
                    ProcessingResult::state,
                    Collectors.counting()
                ));

            System.out.println("Import results:");

            results.forEach(result ->
                System.out.printf(
                    "%d | %s | %s%n",
                    result.recordId(),
                    result.state(),
                    result.message()
                )
            );

            System.out.println("\nState totals:");
            totals.forEach((state, count) ->
                System.out.println(state + ": " + count)
            );

            AuditLogger audit = new AuditLogger(
                root.resolve("logs/audit.log")
            );

            audit.append("Import started");
            audit.append("Import completed");

            Path report = root.resolve("reports/import-report.txt");

            AtomicFileWriter.write(
                report,
                "Import timestamp: " + Instant.now() + "\n"
                + "Records processed: " + results.size() + "\n"
                + "Accepted: " + totals.getOrDefault(
                    ProcessingState.PROCESSED, 0L
                ) + "\n"
                + "Rejected: " + totals.getOrDefault(
                    ProcessingState.REJECTED, 0L
                ) + "\n"
            );

            System.out.println("\nReport:");
            System.out.println(Files.readString(report));

            System.out.println(
                "Report SHA-256: " + sha256(report)
            );

            System.out.println("\nFile extensions:");

            DirectoryScanner.countExtensions(root)
                .forEach((extension, count) ->
                    System.out.println(extension + ": " + count)
                );

            runTests(root);

        } catch (FileWorkflowException exception) {
            System.err.println(
                exception.getClass().getSimpleName()
                + ": " + exception.getMessage()
            );
            System.exitCode = 1;
        } catch (IOException exception) {
            System.err.println(
                "Filesystem failure: " + exception.getMessage()
            );
            System.exitCode = 1;
        } catch (Exception exception) {
            System.err.println(
                "Unexpected failure: " + exception.getMessage()
            );
            System.exitCode = 1;
        } finally {
            if (root != null) {
                try (var paths = Files.walk(root)) {
                    paths.sorted(Comparator.reverseOrder())
                         .forEach(file -> {
                             try {
                                 Files.deleteIfExists(file);
                             } catch (IOException exception) {
                                 System.err.println(
                                     "Cleanup warning: " + file
                                 );
                             }
                         });
                } catch (IOException exception) {
                    System.err.println(
                        "Cleanup failed: " + exception.getMessage()
                    );
                }
            }
        }
    }
}
