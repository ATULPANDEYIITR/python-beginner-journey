import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class ListComprehensionPatterns {

    record Product(String name, double price, int stock, String category) {
        Product {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Product name is required");
            }
            if (!Double.isFinite(price) || price <= 0) {
                throw new IllegalArgumentException("Price must be positive");
            }
            if (stock < 0) {
                throw new IllegalArgumentException("Stock cannot be negative");
            }
            if (category == null || category.isBlank()) {
                throw new IllegalArgumentException("Category is required");
            }
        }

        double inventoryValue() {
            return price * stock;
        }
    }

    record InventoryProjection(String name, double inventoryValue) {
    }

    private static void heading(String title) {
        System.out.println("\n" + "=".repeat(72));
        System.out.println(title);
        System.out.println("=".repeat(72));
    }

    /*
     * Java does not provide Python's list-comprehension syntax.
     * Stream pipelines provide a related declarative model:
     *
     * source -> filter -> map -> collect
     *
     * The implementation deliberately uses Java's type system, records,
     * predicates, streams, and immutable result handling.
     */

    private static List<Integer> squareEvenNumbers(List<Integer> numbers) {
        Objects.requireNonNull(numbers, "numbers");

        return numbers.stream()
                .filter(Objects::nonNull)
                .filter(number -> number % 2 == 0)
                .map(number -> number * number)
                .toList();
    }

    private static List<String> activePassingNames(
            List<StudentRecord> records
    ) {
        return records.stream()
                .filter(Objects::nonNull)
                .filter(StudentRecord::active)
                .filter(record -> record.score() >= 50)
                .map(StudentRecord::name)
                .toList();
    }

    private record StudentRecord(
            String name,
            int score,
            boolean active
    ) {
        StudentRecord {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Name is required");
            }
            if (score < 0 || score > 100) {
                throw new IllegalArgumentException(
                        "Score must be between 0 and 100"
                );
            }
        }
    }

    private static List<InventoryProjection> projectHardware(
            List<Product> products
    ) {
        return products.stream()
                .filter(Objects::nonNull)
                .filter(product -> product.stock() > 0)
                .filter(product -> product.category().equals("hardware"))
                .map(product -> new InventoryProjection(
                        product.name(),
                        product.inventoryValue()
                ))
                .toList();
    }

    private static List<String> normalizeWords(List<String> words) {
        return words.stream()
                .filter(Objects::nonNull)
                .map(String::trim)
                .filter(word -> !word.isEmpty())
                .map(String::toLowerCase)
                .toList();
    }

    private static Set<Integer> uniqueSquares(List<Integer> values) {
        return values.stream()
                .filter(Objects::nonNull)
                .map(value -> value * value)
                .collect(Collectors.toUnmodifiableSet());
    }

    private static <T> List<T> select(
            List<T> values,
            Predicate<T> condition
    ) {
        Objects.requireNonNull(values, "values");
        Objects.requireNonNull(condition, "condition");

        return values.stream()
                .filter(condition)
                .toList();
    }

    private static void demonstrateBasicPipeline() {
        heading("Basic map and filter pipeline");

        List<Integer> numbers = List.of(1, 2, 3, 4, 5, 6);

        List<Integer> squares = squareEvenNumbers(numbers);

        System.out.println("Even squares: " + squares);
    }

    private static void demonstrateStructuredData() {
        heading("Structured-data projection");

        List<Product> products = List.of(
                new Product("Keyboard", 79.99, 12, "hardware"),
                new Product("Mouse", 29.99, 0, "hardware"),
                new Product("Monitor", 249.50, 7, "hardware"),
                new Product("Notebook", 8.50, 25, "stationery"),
                new Product("Cable", 12.75, 18, "hardware")
        );

        List<InventoryProjection> projections =
                projectHardware(products);

        projections.forEach(projection ->
                System.out.printf(
                        "%s -> %.2f%n",
                        projection.name(),
                        projection.inventoryValue()
                )
        );
    }

    private static void demonstrateConditionalMapping() {
        heading("Conditional mapping");

        List<Integer> scores = List.of(35, 50, 72, 91, 48);

        List<String> labels = scores.stream()
                .map(score ->
                        score >= 50
                                ? score + ":pass"
                                : score + ":fail"
                )
                .toList();

        System.out.println("Labels: " + labels);
    }

    private static void demonstrateNestedData() {
        heading("Nested collections");

        List<List<Integer>> groups = List.of(
                List.of(1, 2),
                List.of(3, 4),
                List.of(5, 6)
        );

        // flatMap() combines nested streams into one stream.
        List<Integer> flattened = groups.stream()
                .flatMap(List::stream)
                .toList();

        System.out.println("Flattened values: " + flattened);

        List<String> coordinatePairs = IntStream.range(0, 3)
                .boxed()
                .flatMap(x ->
                        IntStream.range(0, 3)
                                .mapToObj(y -> "(" + x + "," + y + ")")
                )
                .toList();

        System.out.println("Coordinate pairs: " + coordinatePairs);
    }

    private static void demonstrateValidation() {
        heading("Validation boundaries");

        List<String> rawWords = List.of(
                " Python ",
                "",
                " Java ",
                "   ",
                "C++"
        );

        System.out.println("Normalized words: "
                + normalizeWords(rawWords));

        try {
            new Product("", 20.0, 3, "hardware");
        } catch (IllegalArgumentException error) {
            System.out.println(
                    "Expected domain validation failure: "
                            + error.getMessage()
            );
        }

        List<Integer> mixed = new ArrayList<>();
        mixed.add(2);
        mixed.add(null);
        mixed.add(4);

        System.out.println("Null-safe squares: "
                + squareEvenNumbers(mixed));
    }

    private static void demonstrateReusablePredicates() {
        heading("Reusable filtering rules");

        List<Integer> values = List.of(-3, -1, 0, 2, 4, 8, 11);

        Predicate<Integer> positive =
                value -> value > 0;

        Predicate<Integer> even =
                value -> value % 2 == 0;

        List<Integer> positiveEven =
                select(values, positive.and(even));

        System.out.println("Positive even values: " + positiveEven);
    }

    private static void demonstrateDistinctTransformation() {
        heading("Distinct transformed results");

        List<Integer> values = List.of(2, 2, 3, 3, 4);

        Set<Integer> squares = uniqueSquares(values);

        System.out.println("Unique squares: " + squares);
    }

    private static void demonstrateEmptyResults() {
        heading("Empty-result behavior");

        List<Integer> empty = Collections.emptyList();

        System.out.println(
                "Empty source: " + squareEvenNumbers(empty)
        );

        List<Integer> noMatches = select(
                List.of(1, 3, 5),
                value -> value > 100
        );

        System.out.println("No matches: " + noMatches);
    }

    private static void demonstrateReadabilityAndImmutability() {
        heading("Readability and result ownership");

        List<StudentRecord> students = List.of(
                new StudentRecord("Alice", 91, true),
                new StudentRecord("Bob", 42, false),
                new StudentRecord("Carol", 77, true),
                new StudentRecord("David", 35, true)
        );

        List<String> eligible =
                activePassingNames(students);

        System.out.println("Eligible names: " + eligible);

        /*
         * Stream.toList() returns an unmodifiable list in modern Java.
         * This makes the ownership of a pipeline result explicit and prevents
         * accidental mutation after the transformation has completed.
         */
        try {
            eligible.add("Unexpected");
        } catch (UnsupportedOperationException error) {
            System.out.println(
                    "Result is intentionally unmodifiable."
            );
        }
    }

    private static void demonstratePerformance() {
        heading("Performance considerations");

        List<Integer> values = IntStream.range(0, 500_000)
                .boxed()
                .toList();

        long start = System.nanoTime();

        List<Integer> result = values.stream()
                .filter(value -> value % 2 == 0)
                .map(value -> value * value)
                .toList();

        long elapsed = System.nanoTime() - start;

        System.out.printf(
                "Input size: %d%nOutput size: %d%nElapsed: %.3f ms%n",
                values.size(),
                result.size(),
                elapsed / 1_000_000.0
        );

        /*
         * Stream pipelines can express lazy intermediate operations such as
         * filter() and map(). The terminal toList() materializes the result.
         * Parallel streams are not automatically faster; splitting overhead,
         * ordering requirements, and task granularity must justify parallelism.
         */
    }

    public static void main(String[] args) {
        try {
            demonstrateBasicPipeline();
            demonstrateStructuredData();
            demonstrateConditionalMapping();
            demonstrateNestedData();
            demonstrateValidation();
            demonstrateReusablePredicates();
            demonstrateDistinctTransformation();
            demonstrateEmptyResults();
            demonstrateReadabilityAndImmutability();
            demonstratePerformance();
        } catch (RuntimeException error) {
            System.err.println(
                    "Unexpected application failure: "
                            + error.getMessage()
            );
            System.exit(1);
        }
    }
}
