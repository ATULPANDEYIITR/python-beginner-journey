import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Objects;

public class RaisingExceptionsDemo {

    static class ApplicationException extends Exception {
        ApplicationException(String message) {
            super(message);
        }

        ApplicationException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    static final class ValidationException extends ApplicationException {
        ValidationException(String message) {
            super(message);
        }
    }

    static final class ConfigurationException extends ApplicationException {
        ConfigurationException(String message) {
            super(message);
        }
    }

    static final class StorageException extends ApplicationException {
        StorageException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    record User(int id, String name, String email) {}

    interface UserRepository {
        void save(User user) throws StorageException;
    }

    static final class FileUserRepository implements UserRepository {
        private final Path path;

        FileUserRepository(Path path) throws ConfigurationException {
            if (path == null) {
                throw new ConfigurationException("Repository path is required.");
            }
            this.path = path;
        }

        @Override
        public void save(User user) throws StorageException {
            String line = "%d,%s,%s%n".formatted(
                user.id(),
                user.name(),
                user.email()
            );

            try {
                Files.writeString(
                    path,
                    line,
                    StandardOpenOption.CREATE,
                    StandardOpenOption.WRITE,
                    StandardOpenOption.APPEND
                );
            } catch (IOException exception) {
                throw new StorageException(
                    "Unable to persist user to " + path,
                    exception
                );
            }
        }
    }

    static User validateUser(
        int id,
        String name,
        String email
    ) throws ValidationException {
        if (id <= 0) {
            throw new ValidationException(
                "User ID must be greater than zero."
            );
        }

        if (name == null || name.isBlank()) {
            throw new ValidationException(
                "User name cannot be blank."
            );
        }

        if (email == null || !email.contains("@")) {
            throw new ValidationException(
                "Email must contain '@'."
            );
        }

        return new User(
            id,
            name.trim(),
            email.trim().toLowerCase()
        );
    }

    static double divide(double total, double divisor) {
        if (divisor == 0.0) {
            throw new ArithmeticException("Divisor cannot be zero.");
        }

        return total / divisor;
    }

    static int parseInteger(String value) throws ValidationException {
        Objects.requireNonNull(value, "value");

        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException exception) {
            throw new ValidationException(
                "Invalid integer: " + value
            );
        }
    }

    static User processUser(
        UserRepository repository,
        int id,
        String name,
        String email
    ) throws ValidationException, StorageException {
        User user = validateUser(id, name, email);
        repository.save(user);
        return user;
    }

    static String loadConfiguration(
        String databaseUrl
    ) throws ConfigurationException {
        if (databaseUrl == null || databaseUrl.isBlank()) {
            throw new ConfigurationException(
                "Database URL is required."
            );
        }

        return databaseUrl.trim();
    }

    static void demonstrateTryWithResources() {
        Path path = Path.of("java_exception_demo.txt");

        try (var writer = Files.newBufferedWriter(
            path,
            StandardOpenOption.CREATE,
            StandardOpenOption.TRUNCATE_EXISTING
        )) {
            writer.write("resource acquired");
            throw new IOException("Simulated I/O failure.");
        } catch (IOException exception) {
            System.out.println(
                "Resource failure: " + exception.getMessage()
            );
        } finally {
            try {
                Files.deleteIfExists(path);
            } catch (IOException exception) {
                System.err.println(
                    "Cleanup failure: " + exception.getMessage()
                );
            }
        }
    }

    static void runTests() throws Exception {
        User user = validateUser(1, "Ada", "ADA@EXAMPLE.COM");
        assert user.email().equals("ada@example.com");

        try {
            validateUser(0, "Ada", "ada@example.com");
            throw new AssertionError("Expected ValidationException.");
        } catch (ValidationException expected) {
            assert expected.getMessage().contains("greater than zero");
        }

        try {
            divide(10.0, 0.0);
            throw new AssertionError("Expected ArithmeticException.");
        } catch (ArithmeticException expected) {
            assert expected.getMessage().contains("zero");
        }

        try {
            parseInteger("abc");
            throw new AssertionError("Expected ValidationException.");
        } catch (ValidationException expected) {
            assert expected.getMessage().contains("Invalid integer");
        }
    }

    public static void main(String[] args) {
        System.out.println("Raising Exceptions Demonstration");

        try {
            String url = loadConfiguration(
                "postgresql://localhost/example"
            );
            System.out.println("Configuration accepted: " + url);
        } catch (ConfigurationException exception) {
            System.err.println(
                "Configuration failure: " + exception.getMessage()
            );
        }

        try {
            UserRepository repository =
                new FileUserRepository(Path.of("users_demo_java.csv"));

            User user = processUser(
                repository,
                101,
                "Grace Hopper",
                "Grace@Example.com"
            );

            System.out.println("User stored: " + user);
        } catch (ValidationException | StorageException exception) {
            System.err.println(
                "Application failure: " + exception.getMessage()
            );
        } catch (ConfigurationException exception) {
            System.err.println(
                "Repository configuration failure: "
                    + exception.getMessage()
            );
        }

        try {
            UserRepository repository =
                new FileUserRepository(Path.of("users_demo_java.csv"));

            processUser(
                repository,
                -4,
                "Invalid User",
                "invalid@example.com"
            );
        } catch (ValidationException exception) {
            System.out.println(
                "Expected validation failure: "
                    + exception.getMessage()
            );
        } catch (StorageException | ConfigurationException exception) {
            System.err.println(
                "Unexpected application failure: "
                    + exception.getMessage()
            );
        }

        try {
            divide(25.0, 0.0);
        } catch (ArithmeticException exception) {
            System.out.println(
                "Expected arithmetic failure: "
                    + exception.getMessage()
            );
        }

        demonstrateTryWithResources();

        try {
            runTests();
            System.out.println("All exception assertions passed.");
        } catch (Exception exception) {
            System.err.println(
                "Test failure: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
