import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class FilePathManagerDemo {

    enum PathKind {
        FILE,
        DIRECTORY,
        MISSING
    }

    record PathInfo(
            String original,
            Path normalized,
            PathKind kind
    ) {}

    static class PathSecurityException extends RuntimeException {
        PathSecurityException(String message) {
            super(message);
        }
    }

    interface PathPolicy {
        Path validate(Path root, String relativePath);
    }

    static final class ManagedPathPolicy implements PathPolicy {
        @Override
        public Path validate(Path root, String relativePath) {
            if (relativePath == null || relativePath.isBlank()) {
                throw new PathSecurityException("Path cannot be empty");
            }

            if (relativePath.indexOf('\0') >= 0) {
                throw new PathSecurityException("NUL character is forbidden");
            }

            Path candidate = root.resolve(relativePath).normalize();

            if (!candidate.startsWith(root)) {
                throw new PathSecurityException(
                        "Path escapes managed root: " + relativePath
                );
            }

            return candidate;
        }
    }

    static final class RepositoryFileService {
        private final Path root;
        private final PathPolicy policy;

        RepositoryFileService(Path root, PathPolicy policy) throws IOException {
            this.root = root.toAbsolutePath().normalize();
            this.policy = policy;
            Files.createDirectories(this.root);
        }

        Path safePath(String relativePath) {
            return policy.validate(root, relativePath);
        }

        Path createDirectory(String relativePath) throws IOException {
            Path directory = safePath(relativePath);
            Files.createDirectories(directory);
            return directory;
        }

        Path writeText(String relativePath, String content) throws IOException {
            Path file = safePath(relativePath);

            if (content == null) {
                throw new IllegalArgumentException("Content cannot be null");
            }

            Files.createDirectories(file.getParent());
            Files.writeString(
                    file,
                    content,
                    StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE,
                    StandardOpenOption.TRUNCATE_EXISTING
            );

            return file;
        }

        PathInfo inspect(String relativePath) {
            Path file = safePath(relativePath);

            if (Files.isRegularFile(file)) {
                return new PathInfo(relativePath, file, PathKind.FILE);
            }

            if (Files.isDirectory(file)) {
                return new PathInfo(relativePath, file, PathKind.DIRECTORY);
            }

            return new PathInfo(relativePath, file, PathKind.MISSING);
        }

        List<Path> listFiles() throws IOException {
            try (Stream<Path> stream = Files.walk(root)) {
                return stream
                        .filter(Files::isRegularFile)
                        .sorted()
                        .collect(Collectors.toList());
            }
        }

        Map<String, Long> extensionReport() throws IOException {
            return listFiles()
                    .stream()
                    .collect(Collectors.groupingBy(
                            this::extension,
                            TreeMap::new,
                            Collectors.counting()
                    ));
        }

        private String extension(Path file) {
            String name = file.getFileName().toString();
            int position = name.lastIndexOf('.');

            if (position <= 0 || position == name.length() - 1) {
                return "[no extension]";
            }

            return name.substring(position).toLowerCase(Locale.ROOT);
        }

        Path copyFile(
                String source,
                String destination
        ) throws IOException {
            Path sourcePath = safePath(source);
            Path destinationPath = safePath(destination);

            if (!Files.isRegularFile(sourcePath)) {
                throw new NoSuchFileException(sourcePath.toString());
            }

            Files.createDirectories(destinationPath.getParent());

            return Files.copy(
                    sourcePath,
                    destinationPath,
                    StandardCopyOption.REPLACE_EXISTING
            );
        }

        Path relativeToRoot(Path file) {
            return root.relativize(file.toAbsolutePath().normalize());
        }
    }

    static void demonstratePathSyntax() {
        Path path = Paths.get(
                "reports",
                "2026",
                "november",
                "report.csv"
        );

        System.out.println("Path: " + path);
        System.out.println("Filename: " + path.getFileName());
        System.out.println("Parent: " + path.getParent());
        System.out.println("Extension: " +
                path.getFileName().toString()
                        .substring(path.getFileName().toString().lastIndexOf('.')));
        System.out.println("Normalized: " + path.normalize());
    }

    public static void main(String[] args) {
        demonstratePathSyntax();

        Path temporaryRoot;

        try {
            temporaryRoot = Files.createTempDirectory("java-path-demo-");
        } catch (IOException error) {
            System.err.println("Cannot create temporary directory: " +
                    error.getMessage());
            return;
        }

        RepositoryFileService service =
                new RepositoryFileService(
                        temporaryRoot,
                        new ManagedPathPolicy()
                );

        try {
            service.createDirectory("reports/2026/november");
            service.createDirectory("archive");

            service.writeText(
                    "reports/2026/november/report.txt",
                    "Quarterly operational report\n"
            );

            service.writeText(
                    "reports/2026/november/data.csv",
                    "id,value\n1,100\n2,250\n"
            );

            service.writeText(
                    "archive/README",
                    "Archived files are retained here.\n"
            );

            System.out.println("\nManaged root: " + temporaryRoot);

            List<String> inspected = List.of(
                    "reports/2026/november/report.txt",
                    "reports/2026/november",
                    "missing.txt"
            );

            for (String name : inspected) {
                System.out.println(service.inspect(name));
            }

            System.out.println("\nFiles:");

            for (Path file : service.listFiles()) {
                System.out.println("  " + service.relativeToRoot(file));
            }

            System.out.println("\nExtensions: " +
                    service.extensionReport());

            Path copied = service.copyFile(
                    "reports/2026/november/report.txt",
                    "archive/report.txt"
            );

            System.out.println("Copied: " +
                    service.relativeToRoot(copied));

            try {
                service.safePath("../../outside.txt");
            } catch (PathSecurityException error) {
                System.out.println(
                        "Blocked traversal: " + error.getMessage()
                );
            }

            try {
                service.safePath("/absolute/path.txt");
            } catch (PathSecurityException error) {
                System.out.println(
                        "Blocked absolute path: " + error.getMessage()
                );
            }

            if (service.inspect("archive/report.txt").kind()
                    != PathKind.FILE) {
                throw new IllegalStateException(
                        "Copied-file validation failed"
                );
            }

            if (service.inspect("missing.txt").kind()
                    != PathKind.MISSING) {
                throw new IllegalStateException(
                        "Missing-file validation failed"
                );
            }

            if (!service.extensionReport().get(".csv").equals(1L)) {
                throw new IllegalStateException(
                        "Extension validation failed"
                );
            }

            System.out.println(
                    "\nPath workflow completed successfully."
            );

        } catch (IOException | RuntimeException error) {
            System.err.println("Workflow failed: " +
                    error.getMessage());
        } finally {
            try (Stream<Path> paths = Files.walk(temporaryRoot)) {
                paths.sorted(Comparator.reverseOrder())
                        .forEach(path -> {
                            try {
                                Files.deleteIfExists(path);
                            } catch (IOException ignored) {
                                // Cleanup failure must not hide the primary result.
                            }
                        });
            } catch (IOException ignored) {
                // Temporary cleanup is best effort.
            }
        }
    }
}
