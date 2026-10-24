import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

public class ReusableFunctionsDemo {

    static final class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    enum TaskStatus {
        PENDING,
        RUNNING,
        COMPLETED,
        FAILED
    }

    record Statistics(
            int count,
            double minimum,
            double maximum,
            double mean,
            double populationStandardDeviation
    ) {}

    record Task<T>(
            String name,
            Function<T, ?> operation,
            T input
    ) {}

    static final class FunctionMetrics {
        private int calls;
        private int failures;
        private long totalNanoseconds;

        void recordStart() {
            calls++;
        }

        void recordFailure() {
            failures++;
        }

        void recordDuration(long nanoseconds) {
            totalNanoseconds += nanoseconds;
        }

        Map<String, Object> asMap() {
            double averageMilliseconds =
                    calls == 0
                            ? 0.0
                            : totalNanoseconds / 1_000_000.0 / calls;

            return Map.of(
                    "calls", calls,
                    "failures", failures,
                    "averageMilliseconds", averageMilliseconds
            );
        }
    }

    static final class FunctionRegistry {
        private final Map<String, Function<?, ?>> functions =
                new LinkedHashMap<>();

        private final Map<String, FunctionMetrics> metrics =
                new LinkedHashMap<>();

        public <T, R> void register(
                String name,
                Function<T, R> function
        ) {
            requireText(name, "function name");

            if (function == null) {
                throw new ValidationException(
                        "Function cannot be null."
                );
            }

            if (functions.containsKey(name)) {
                throw new ValidationException(
                        "Function already exists: " + name
                );
            }

            functions.put(name, function);
            metrics.put(name, new FunctionMetrics());
        }

        @SuppressWarnings("unchecked")
        public <T, R> R call(
                String name,
                T input
        ) {
            Function<?, ?> registered = functions.get(name);

            if (registered == null) {
                throw new IllegalArgumentException(
                        "Unknown function: " + name
                );
            }

            FunctionMetrics functionMetrics = metrics.get(name);
            functionMetrics.recordStart();

            long started = System.nanoTime();

            try {
                return ((Function<T, R>) registered).apply(input);
            } catch (RuntimeException exception) {
                functionMetrics.recordFailure();
                throw exception;
            } finally {
                functionMetrics.recordDuration(
                        System.nanoTime() - started
                );
            }
        }

        public Map<String, Object> metrics(String name) {
            FunctionMetrics result = metrics.get(name);

            if (result == null) {
                throw new IllegalArgumentException(
                        "Unknown function: " + name
                );
            }

            return result.asMap();
        }
    }

    static String requireText(String value, String field) {
        if (value == null) {
            throw new ValidationException(field + " cannot be null.");
        }

        String normalized = value.trim();

        if (normalized.isEmpty()) {
            throw new ValidationException(field + " cannot be empty.");
        }

        return normalized;
    }

    static List<String> normalizeTags(List<String> tags) {
        if (tags == null) {
            throw new ValidationException("Tags cannot be null.");
        }

        Set<String> unique = new LinkedHashSet<>();

        for (String tag : tags) {
            if (tag == null) {
                throw new ValidationException(
                        "A tag cannot be null."
                );
            }

            String normalized = tag.trim().toLowerCase();

            if (normalized.isEmpty()) {
                continue;
            }

            if (normalized.length() > 40) {
                throw new ValidationException(
                        "A tag cannot exceed 40 characters."
                );
            }

            unique.add(normalized);
        }

        return unique.stream()
                .sorted()
                .toList();
    }

    static Statistics calculateStatistics(List<Double> values) {
        if (values == null || values.isEmpty()) {
            throw new ValidationException(
                    "At least one value is required."
            );
        }

        if (values.stream().anyMatch(
                value -> value == null || !Double.isFinite(value)
        )) {
            throw new ValidationException(
                    "Values must be finite numbers."
            );
        }

        double minimum = Collections.min(values);
        double maximum = Collections.max(values);
        double total = values.stream()
                .mapToDouble(Double::doubleValue)
                .sum();

        double mean = total / values.size();

        double variance = values.stream()
                .mapToDouble(value -> {
                    double difference = value - mean;
                    return difference * difference;
                })
                .sum() / values.size();

        return new Statistics(
                values.size(),
                minimum,
                maximum,
                mean,
                Math.sqrt(variance)
        );
    }

    static <T> List<List<T>> chunk(
            List<T> values,
            int size
    ) {
        if (values == null) {
            throw new ValidationException(
                    "Values cannot be null."
            );
        }

        if (size <= 0) {
            throw new ValidationException(
                    "Chunk size must be positive."
            );
        }

        List<List<T>> result = new ArrayList<>();

        for (int start = 0; start < values.size(); start += size) {
            int end = Math.min(start + size, values.size());
            result.add(
                    List.copyOf(values.subList(start, end))
            );
        }

        return List.copyOf(result);
    }

    static <T> Map<String, Object> executeTask(Task<T> task) {
        String taskName = requireText(task.name(), "task name");

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("name", taskName);
        result.put("status", TaskStatus.RUNNING.name());

        try {
            Object value = task.operation().apply(task.input());
            result.put("status", TaskStatus.COMPLETED.name());
            result.put("value", value);
        } catch (RuntimeException exception) {
            result.put("status", TaskStatus.FAILED.name());
            result.put("error", exception.getMessage());
        }

        return result;
    }

    static void writeReport(
            Path path,
            Map<String, Object> report
    ) throws IOException {
        if (!path.toString().endsWith(".txt")) {
            throw new ValidationException(
                    "This demonstration writes text reports only."
            );
        }

        List<String> lines = report.entrySet()
                .stream()
                .map(entry ->
                        entry.getKey() + "=" + entry.getValue()
                )
                .toList();

        Files.write(path, lines);
    }

    public static void main(String[] args) {
        try {
            FunctionRegistry registry = new FunctionRegistry();

            registry.register(
                    "normalizeTags",
                    ReusableFunctionsDemo::normalizeTags
            );

            registry.register(
                    "statistics",
                    ReusableFunctionsDemo::calculateStatistics
            );

            List<String> tags = registry.call(
                    "normalizeTags",
                    Arrays.asList(
                            " Java ",
                            "java",
                            "functions",
                            "reuse"
                    )
            );

            Statistics statistics = registry.call(
                    "statistics",
                    Arrays.asList(
                            10.0,
                            20.0,
                            30.0,
                            40.0,
                            50.0
                    )
            );

            System.out.println("Normalized tags: " + tags);
            System.out.println("Statistics: " + statistics);

            List<Task<?>> tasks = List.of(
                    new Task<>(
                            "tag-normalization",
                            ReusableFunctionsDemo::normalizeTags,
                            Arrays.asList("API", "api", "database")
                    ),
                    new Task<>(
                            "statistics",
                            ReusableFunctionsDemo::calculateStatistics,
                            Arrays.asList(4.0, 8.0, 15.0, 16.0, 23.0, 42.0)
                    ),
                    new Task<>(
                            "invalid-statistics",
                            ReusableFunctionsDemo::calculateStatistics,
                            List.of()
                    )
            );

            List<Map<String, Object>> results = tasks.stream()
                    .map(task -> {
                        @SuppressWarnings("unchecked")
                        Task<Object> typed =
                                (Task<Object>) task;
                        return executeTask(typed);
                    })
                    .toList();

            results.forEach(System.out::println);

            System.out.println(
                    "Statistics metrics: " +
                    registry.metrics("statistics")
            );

            List<List<Integer>> chunks =
                    chunk(List.of(1, 2, 3, 4, 5), 2);

            System.out.println("Chunks: " + chunks);

            Map<String, Object> report = new LinkedHashMap<>();
            report.put("tags", tags);
            report.put("statistics", statistics);
            report.put("chunks", chunks);
            report.put(
                    "statisticsMetrics",
                    registry.metrics("statistics")
            );

            Path output = Path.of("function-report.txt");
            writeReport(output, report);
            System.out.println(
                    "Report written to " + output.toAbsolutePath()
            );

            if (!normalizeTags(
                    List.of("A", "a", "B")
            ).equals(List.of("a", "b"))) {
                throw new AssertionError(
                        "Tag normalization failed."
                );
            }

            if (calculateStatistics(
                    List.of(10.0, 20.0)
            ).mean() != 15.0) {
                throw new AssertionError(
                        "Statistics calculation failed."
                );
            }

            try {
                calculateStatistics(List.of());
                throw new AssertionError(
                        "Empty input should fail."
                );
            } catch (ValidationException expected) {
                System.out.println(
                        "Validation test passed."
                );
            }

        } catch (IOException | RuntimeException exception) {
            System.err.println(
                    "Execution failed: " + exception.getMessage()
            );
        }
    }
}
