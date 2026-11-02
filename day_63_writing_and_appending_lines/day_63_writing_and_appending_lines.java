import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class FileWritingDemo {

    enum WriteMode {
        WRITE,
        APPEND
    }

    record WriteResult(
        Path path,
        WriteMode mode,
        long bytesWritten,
        long lineCount
    ) {}

    record AuditRecord(
        String operation,
        String filename,
        long bytes,
        long lines,
        Instant timestamp
    ) {}

    static class FileOperationException extends Exception {
        FileOperationException(String message) {
            super(message);
        }

        FileOperationException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    interface ContentPolicy {
        void validate(String content) throws FileOperationException;
    }

    static final class SizePolicy implements ContentPolicy {
        private final long maximumBytes;

        SizePolicy(long maximumBytes) {
            if (maximumBytes <= 0) {
                throw new IllegalArgumentException(
                    "Maximum size must be positive."
                );
            }
            this.maximumBytes = maximumBytes;
        }

        @Override
        public void validate(String content) throws FileOperationException {
            long bytes = content.getBytes(StandardCharsets.UTF_8).length;

            if (bytes > maximumBytes) {
                throw new FileOperationException(
                    "Content exceeds the configured size limit."
                );
            }
        }
    }

    static final class FileStore {
        private final Path baseDirectory;
        private final ContentPolicy contentPolicy;
        private final List<AuditRecord> auditLog = new ArrayList<>();

        FileStore(Path baseDirectory, ContentPolicy contentPolicy)
            throws FileOperationException {

            this.baseDirectory = baseDirectory.toAbsolutePath().normalize();
            this.contentPolicy = Objects.requireNonNull(contentPolicy);

            try {
                Files.createDirectories(this.baseDirectory);
            } catch (IOException error) {
                throw new FileOperationException(
                    "Unable to initialize storage directory.",
                    error
                );
            }
        }

        private Path safePath(String filename)
            throws FileOperationException {

            if (filename == null || filename.isBlank()) {
                throw new FileOperationException(
                    "A valid filename is required."
                );
            }

            Path target =
                baseDirectory.resolve(filename).normalize();

            if (!target.startsWith(baseDirectory)) {
                throw new FileOperationException(
                    "Path escapes the configured directory."
                );
            }

            if (Files.exists(target) && Files.isDirectory(target)) {
                throw new FileOperationException(
                    "The target path is a directory."
                );
            }

            return target;
        }

        WriteResult write(String filename, String content)
            throws FileOperationException {
            return save(filename, content, WriteMode.WRITE);
        }

        WriteResult append(String filename, String content)
            throws FileOperationException {
            return save(filename, content, WriteMode.APPEND);
        }

        private WriteResult save(
            String filename,
            String content,
            WriteMode mode
        ) throws FileOperationException {

            Objects.requireNonNull(content, "content");

            contentPolicy.validate(content);

            Path target = safePath(filename);

            try {
                Files.createDirectories(target.getParent());

                if (mode == WriteMode.WRITE) {
                    Files.writeString(
                        target,
                        content,
                        StandardCharsets.UTF_8,
                        StandardOpenOption.CREATE,
                        StandardOpenOption.TRUNCATE_EXISTING,
                        StandardOpenOption.WRITE
                    );
                } else {
                    Files.writeString(
                        target,
                        content,
                        StandardCharsets.UTF_8,
                        StandardOpenOption.CREATE,
                        StandardOpenOption.APPEND,
                        StandardOpenOption.WRITE
                    );
                }
            } catch (IOException error) {
                throw new FileOperationException(
                    "File operation failed for " + filename,
                    error
                );
            }

            long bytes =
                content.getBytes(StandardCharsets.UTF_8).length;

            long lines = content.isEmpty()
                ? 0
                : content.lines().count();

            auditLog.add(
                new AuditRecord(
                    mode.name().toLowerCase(),
                    baseDirectory.relativize(target).toString(),
                    bytes,
                    lines,
                    Instant.now()
                )
            );

            return new WriteResult(target, mode, bytes, lines);
        }

        void appendLines(String filename, List<String> lines)
            throws FileOperationException {

            Objects.requireNonNull(lines, "lines");

            StringBuilder content = new StringBuilder();

            for (String line : lines) {
                if (line == null) {
                    throw new FileOperationException(
                        "A line cannot be null."
                    );
                }

                content
                    .append(line.replace("\r", "").replace("\n", ""))
                    .append('\n');
            }

            append(filename, content.toString());
        }

        String read(String filename)
            throws FileOperationException {

            Path target = safePath(filename);

            try {
                return Files.readString(
                    target,
                    StandardCharsets.UTF_8
                );
            } catch (IOException error) {
                throw new FileOperationException(
                    "Unable to read " + filename,
                    error
                );
            }
        }

        long size(String filename)
            throws FileOperationException {

            Path target = safePath(filename);

            try {
                return Files.size(target);
            } catch (IOException error) {
                throw new FileOperationException(
                    "Unable to determine file size.",
                    error
                );
            }
        }

        List<AuditRecord> auditLog() {
            return List.copyOf(auditLog);
        }
    }

    public static void main(String[] args) {
        Path temporaryDirectory;

        try {
            temporaryDirectory =
                Files.createTempDirectory("java-file-writing-");

            FileStore store = new FileStore(
                temporaryDirectory,
                new SizePolicy(5 * 1024 * 1024)
            );

            store.write(
                "logs/application.log",
                "Application started\n"
            );

            store.append(
                "logs/application.log",
                "Configuration loaded\n"
            );

            store.appendLines(
                "logs/application.log",
                List.of(
                    "Database connection established",
                    "Worker process started",
                    "Application ready"
                )
            );

            String expected =
                "Application started\n" +
                "Configuration loaded\n" +
                "Database connection established\n" +
                "Worker process started\n" +
                "Application ready\n";

            String actual = store.read("logs/application.log");

            if (!actual.equals(expected)) {
                throw new FileOperationException(
                    "Content validation failed."
                );
            }

            long expectedSize =
                expected.getBytes(StandardCharsets.UTF_8).length;

            if (store.size("logs/application.log") != expectedSize) {
                throw new FileOperationException(
                    "File-size validation failed."
                );
            }

            try {
                store.append("../outside.txt", "blocked\n");
                throw new FileOperationException(
                    "Path traversal was not rejected."
                );
            } catch (FileOperationException expectedFailure) {
                if (!expectedFailure.getMessage()
                    .contains("Path escapes")) {
                    throw expectedFailure;
                }
            }

            System.out.println("File content:");
            System.out.print(actual);

            System.out.println("\nAudit records:");
            store.auditLog().forEach(System.out::println);

            deleteRecursively(temporaryDirectory);

        } catch (Exception error) {
            System.err.println("Error: " + error.getMessage());
            System.exit(1);
        }
    }

    private static void deleteRecursively(Path root)
        throws IOException {

        if (!Files.exists(root)) {
            return;
        }

        try (var paths = Files.walk(root)) {
            paths
                .sorted((a, b) -> b.compareTo(a))
                .forEach(path -> {
                    try {
                        Files.deleteIfExists(path);
                    } catch (IOException error) {
                        throw new RuntimeException(error);
                    }
                });
        }
    }
}
