import java.util.*;
import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;

/*
 * Working with JSON
 *
 * Enterprise-oriented JSON processing implementation.
 *
 * Includes:
 * - JSON object and array modeling
 * - Recursive-descent parsing
 * - Serialization
 * - Schema validation
 * - Immutable domain records
 * - Service-layer processing
 * - Nested property retrieval
 * - File persistence
 * - Data sanitization
 * - Hash generation
 *
 * Java 17 standard library only.
 */

public class Main {

    private static final int MAX_DEPTH = 30;
    private static final long MAX_FILE_SIZE = 2L * 1024 * 1024;

    static class JSONException extends RuntimeException {
        JSONException(String message) {
            super(message);
        }
    }

    enum CustomerStatus {
        ACTIVE,
        INACTIVE,
        PENDING
    }

    record Customer(
        int customerId,
        String name,
        String email,
        CustomerStatus status,
        double balance
    ) {
        Customer {
            if (customerId <= 0) {
                throw new JSONException("Invalid customer ID");
            }

            if (name == null || name.isBlank()) {
                throw new JSONException("Customer name is required");
            }

            if (
                email == null ||
                !email.matches("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")
            ) {
                throw new JSONException("Invalid email address");
            }

            Objects.requireNonNull(status);

            if (!Double.isFinite(balance) || balance < 0) {
                throw new JSONException("Invalid balance");
            }
        }
    }

    record Product(
        String name,
        double price,
        int quantity
    ) {
        Product {
            if (name == null || name.isBlank()) {
                throw new JSONException("Product name is required");
            }

            if (!Double.isFinite(price) || price < 0) {
                throw new JSONException("Invalid product price");
            }

            if (quantity <= 0) {
                throw new JSONException("Invalid product quantity");
            }
        }
    }

    record Order(
        int orderId,
        int customerId,
        List<Product> products,
        String status
    ) {
        Order {
            if (orderId <= 0 || customerId <= 0) {
                throw new JSONException("Invalid order identifiers");
            }

            products = List.copyOf(products);

            if (products.isEmpty()) {
                throw new JSONException("Order must contain products");
            }

            if (!Set.of("pending", "completed", "cancelled").contains(status)) {
                throw new JSONException("Invalid order status");
            }
        }

        double total() {
            return products.stream()
                .mapToDouble(p -> p.price() * p.quantity())
                .sum();
        }
    }

    static class JSONParser {

        private final String input;
        private int position = 0;

        JSONParser(String input) {
            if (input == null) {
                throw new JSONException("JSON input cannot be null");
            }

            if (input.length() > MAX_FILE_SIZE) {
                throw new JSONException("JSON input exceeds size limit");
            }

            this.input = input;
        }

        private void skipWhitespace() {
            while (
                position < input.length() &&
                Character.isWhitespace(input.charAt(position))
            ) {
                position++;
            }
        }

        private char peek() {
            skipWhitespace();

            if (position >= input.length()) {
                throw new JSONException("Unexpected end of JSON");
            }

            return input.charAt(position);
        }

        private boolean consume(char expected) {
            skipWhitespace();

            if (
                position < input.length() &&
                input.charAt(position) == expected
            ) {
                position++;
                return true;
            }

            return false;
        }

        private void expect(char expected) {
            if (!consume(expected)) {
                throw new JSONException(
                    "Expected character: " + expected
                );
            }
        }

        Object parse() {
            Object result = parseValue(0);

            skipWhitespace();

            if (position != input.length()) {
                throw new JSONException("Unexpected trailing content");
            }

            return result;
        }

        private Object parseValue(int depth) {
            if (depth > MAX_DEPTH) {
                throw new JSONException("Maximum nesting depth exceeded");
            }

            char c = peek();

            if (c == '{') return parseObject(depth);
            if (c == '[') return parseArray(depth);
            if (c == '"') return parseString();

            if (c == '-' || Character.isDigit(c)) {
                return parseNumber();
            }

            if (input.startsWith("true", position)) {
                position += 4;
                return true;
            }

            if (input.startsWith("false", position)) {
                position += 5;
                return false;
            }

            if (input.startsWith("null", position)) {
                position += 4;
                return null;
            }

            throw new JSONException("Invalid JSON token");
        }

        private Map<String, Object> parseObject(int depth) {
            expect('{');

            Map<String, Object> result = new LinkedHashMap<>();

            if (consume('}')) {
                return result;
            }

            while (true) {
                if (peek() != '"') {
                    throw new JSONException("Object key must be a string");
                }

                String key = parseString();

                expect(':');

                Object value = parseValue(depth + 1);

                if (result.containsKey(key)) {
                    throw new JSONException(
                        "Duplicate JSON property: " + key
                    );
                }

                result.put(key, value);

                if (consume('}')) {
                    return result;
                }

                expect(',');
            }
        }

        private List<Object> parseArray(int depth) {
            expect('[');

            List<Object> result = new ArrayList<>();

            if (consume(']')) {
                return result;
            }

            while (true) {
                result.add(parseValue(depth + 1));

                if (consume(']')) {
                    return result;
                }

                expect(',');
            }
        }

        private String parseString() {
            expect('"');

            StringBuilder result = new StringBuilder();

            while (position < input.length()) {
                char c = input.charAt(position++);

                if (c == '"') {
                    return result.toString();
                }

                if (c < 0x20) {
                    throw new JSONException(
                        "Unescaped control character"
                    );
                }

                if (c != '\\') {
                    result.append(c);
                    continue;
                }

                if (position >= input.length()) {
                    throw new JSONException("Incomplete escape sequence");
                }

                char escaped = input.charAt(position++);

                switch (escaped) {
                    case '"' -> result.append('"');
                    case '\\' -> result.append('\\');
                    case '/' -> result.append('/');
                    case 'b' -> result.append('\b');
                    case 'f' -> result.append('\f');
                    case 'n' -> result.append('\n');
                    case 'r' -> result.append('\r');
                    case 't' -> result.append('\t');

                    case 'u' -> {
                        if (position + 4 > input.length()) {
                            throw new JSONException(
                                "Incomplete Unicode escape"
                            );
                        }

                        String hex = input.substring(
                            position,
                            position + 4
                        );

                        try {
                            result.append(
                                (char) Integer.parseInt(hex, 16)
                            );
                        } catch (NumberFormatException error) {
                            throw new JSONException(
                                "Invalid Unicode escape"
                            );
                        }

                        position += 4;
                    }

                    default -> throw new JSONException(
                        "Invalid string escape"
                    );
                }
            }

            throw new JSONException("Unterminated JSON string");
        }

        private Number parseNumber() {
            int start = position;

            if (consume('-')) {
                if (position >= input.length()) {
                    throw new JSONException("Invalid number");
                }
            }

            if (position < input.length() && input.charAt(position) == '0') {
                position++;

                if (
                    position < input.length() &&
                    Character.isDigit(input.charAt(position))
                ) {
                    throw new JSONException("Leading zeros are invalid");
                }
            } else {
                if (
                    position >= input.length() ||
                    !Character.isDigit(input.charAt(position))
                ) {
                    throw new JSONException("Invalid number");
                }

                while (
                    position < input.length() &&
                    Character.isDigit(input.charAt(position))
                ) {
                    position++;
                }
            }

            if (position < input.length() && input.charAt(position) == '.') {
                position++;

                int fractionStart = position;

                while (
                    position < input.length() &&
                    Character.isDigit(input.charAt(position))
                ) {
                    position++;
                }

                if (fractionStart == position) {
                    throw new JSONException("Invalid decimal fraction");
                }
            }

            if (
                position < input.length() &&
                (input.charAt(position) == 'e' ||
                 input.charAt(position) == 'E')
            ) {
                position++;

                if (
                    position < input.length() &&
                    (input.charAt(position) == '+' ||
                     input.charAt(position) == '-')
                ) {
                    position++;
                }

                int exponentStart = position;

                while (
                    position < input.length() &&
                    Character.isDigit(input.charAt(position))
                ) {
                    position++;
                }

                if (exponentStart == position) {
                    throw new JSONException("Invalid exponent");
                }
            }

            String text = input.substring(start, position);

            try {
                double value = Double.parseDouble(text);

                if (!Double.isFinite(value)) {
                    throw new JSONException("Number outside supported range");
                }

                return value;
            } catch (NumberFormatException error) {
                throw new JSONException("Invalid number");
            }
        }
    }

    static class JSONSerializer {

        static String stringify(Object value) {
            StringBuilder output = new StringBuilder();
            append(value, output, 0);
            return output.toString();
        }

        private static void append(
            Object value,
            StringBuilder output,
            int depth
        ) {
            if (depth > MAX_DEPTH) {
                throw new JSONException(
                    "Maximum serialization depth exceeded"
                );
            }

            if (value == null) {
                output.append("null");
                return;
            }

            if (value instanceof String text) {
                appendString(text, output);
                return;
            }

            if (value instanceof Boolean) {
                output.append(value);
                return;
            }

            if (value instanceof Number number) {
                double numericValue = number.doubleValue();

                if (!Double.isFinite(numericValue)) {
                    throw new JSONException("Invalid JSON number");
                }

                output.append(number);
                return;
            }

            if (value instanceof Map<?, ?> map) {
                output.append('{');

                boolean first = true;

                for (Map.Entry<?, ?> entry : map.entrySet()) {
                    if (!(entry.getKey() instanceof String key)) {
                        throw new JSONException(
                            "JSON object keys must be strings"
                        );
                    }

                    if (!first) {
                        output.append(',');
                    }

                    appendString(key, output);
                    output.append(':');
                    append(entry.getValue(), output, depth + 1);

                    first = false;
                }

                output.append('}');
                return;
            }

            if (value instanceof Collection<?> collection) {
                output.append('[');

                boolean first = true;

                for (Object item : collection) {
                    if (!first) {
                        output.append(',');
                    }

                    append(item, output, depth + 1);
                    first = false;
                }

                output.append(']');
                return;
            }

            throw new JSONException(
                "Unsupported JSON value type: " +
                value.getClass().getName()
            );
        }

        private static void appendString(
            String value,
            StringBuilder output
        ) {
            output.append('"');

            for (int i = 0; i < value.length(); i++) {
                char c = value.charAt(i);

                switch (c) {
                    case '"' -> output.append("\\\"");
                    case '\\' -> output.append("\\\\");
                    case '\b' -> output.append("\\b");
                    case '\f' -> output.append("\\f");
                    case '\n' -> output.append("\\n");
                    case '\r' -> output.append("\\r");
                    case '\t' -> output.append("\\t");

                    default -> {
                        if (c < 0x20) {
                            output.append(String.format(
                                "\\u%04x",
                                (int) c
                            ));
                        } else {
                            output.append(c);
                        }
                    }
                }
            }

            output.append('"');
        }
    }

    static class CustomerValidator {

        static Customer fromJSON(Map<String, Object> data) {
            Set<String> required = Set.of(
                "customerId",
                "name",
                "email",
                "status",
                "balance"
            );

            if (!data.keySet().containsAll(required)) {
                throw new JSONException("Missing required customer fields");
            }

            int id = Math.toIntExact(
                ((Number) data.get("customerId")).longValue()
            );

            String name = (String) data.get("name");
            String email = (String) data.get("email");

            CustomerStatus status;

            try {
                status = CustomerStatus.valueOf(
                    ((String) data.get("status")).toUpperCase(Locale.ROOT)
                );
            } catch (IllegalArgumentException error) {
                throw new JSONException("Invalid customer status");
            }

            double balance = ((Number) data.get("balance")).doubleValue();

            return new Customer(
                id,
                name,
                email,
                status,
                balance
            );
        }
    }

    static class OrderService {

        private final Map<Integer, Order> orders = new HashMap<>();

        public void register(Order order) {
            if (orders.containsKey(order.orderId())) {
                throw new JSONException("Duplicate order ID");
            }

            orders.put(order.orderId(), order);
        }

        public double getTotal(int orderId) {
            Order order = orders.get(orderId);

            if (order == null) {
                throw new JSONException("Order does not exist");
            }

            return order.total();
        }

        public List<Map<String, Object>> export() {
            return orders.values().stream()
                .sorted(Comparator.comparingInt(Order::orderId))
                .map(order -> {
                    List<Map<String, Object>> items =
                        order.products().stream()
                            .map(product -> Map.<String, Object>of(
                                "name", product.name(),
                                "price", product.price(),
                                "quantity", product.quantity()
                            ))
                            .toList();

                    return Map.<String, Object>of(
                        "orderId", order.orderId(),
                        "customerId", order.customerId(),
                        "status", order.status(),
                        "total", order.total(),
                        "items", items
                    );
                })
                .toList();
        }
    }

    static class JSONFileRepository {

        private final Path file;

        JSONFileRepository(Path file) {
            this.file = file;
        }

        void save(Object data) throws IOException {
            String content = JSONSerializer.stringify(data);

            byte[] bytes = content.getBytes(StandardCharsets.UTF_8);

            if (bytes.length > MAX_FILE_SIZE) {
                throw new JSONException("JSON file exceeds size limit");
            }

            Path parent = file.toAbsolutePath().getParent();

            Files.createDirectories(parent);

            Path temporary = Files.createTempFile(
                parent,
                "json-",
                ".tmp"
            );

            try {
                Files.write(temporary, bytes);

                try {
                    Files.move(
                        temporary,
                        file,
                        StandardCopyOption.ATOMIC_MOVE,
                        StandardCopyOption.REPLACE_EXISTING
                    );
                } catch (AtomicMoveNotSupportedException error) {
                    Files.move(
                        temporary,
                        file,
                        StandardCopyOption.REPLACE_EXISTING
                    );
                }
            } finally {
                Files.deleteIfExists(temporary);
            }
        }

        Object load() throws IOException {
            if (!Files.isRegularFile(file)) {
                throw new JSONException("JSON file does not exist");
            }

            if (Files.size(file) > MAX_FILE_SIZE) {
                throw new JSONException("JSON file exceeds size limit");
            }

            String content = Files.readString(
                file,
                StandardCharsets.UTF_8
            );

            return new JSONParser(content).parse();
        }
    }

    static Object sanitize(Object value) {
        Set<String> sensitive = Set.of(
            "password",
            "token",
            "secret",
            "access_token",
            "api_key"
        );

        if (value instanceof Map<?, ?> map) {
            Map<String, Object> result = new LinkedHashMap<>();

            for (Map.Entry<?, ?> entry : map.entrySet()) {
                String key = (String) entry.getKey();

                if (!sensitive.contains(key.toLowerCase(Locale.ROOT))) {
                    result.put(key, sanitize(entry.getValue()));
                }
            }

            return result;
        }

        if (value instanceof List<?> list) {
            return list.stream()
                .map(Main::sanitize)
                .toList();
        }

        return value;
    }

    static String sha256(String input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");

            byte[] hash = digest.digest(
                input.getBytes(StandardCharsets.UTF_8)
            );

            return HexFormat.of().formatHex(hash);
        } catch (NoSuchAlgorithmException error) {
            throw new JSONException("SHA-256 unavailable");
        }
    }

    public static void main(String[] args) throws Exception {

        System.out.println("\n=== JSON Parsing ===");

        String customerJSON = """
            {
                "customerId": 101,
                "name": "Atul Pandey",
                "email": "atul@example.com",
                "status": "active",
                "balance": 12500.50
            }
            """;

        Object parsed = new JSONParser(customerJSON).parse();

        Customer customer = CustomerValidator.fromJSON(
            (Map<String, Object>) parsed
        );

        System.out.println(customer);

        System.out.println("\n=== JSON Serialization ===");

        Map<String, Object> customerDocument = new LinkedHashMap<>();

        customerDocument.put("customerId", customer.customerId());
        customerDocument.put("name", customer.name());
        customerDocument.put("email", customer.email());
        customerDocument.put("status", customer.status().name().toLowerCase());
        customerDocument.put("balance", customer.balance());

        System.out.println(
            JSONSerializer.stringify(customerDocument)
        );

        System.out.println("\n=== Order Processing ===");

        OrderService service = new OrderService();

        Order order = new Order(
            5001,
            101,
            List.of(
                new Product("Laptop", 65000, 1),
                new Product("Mouse", 800, 2)
            ),
            "completed"
        );

        service.register(order);

        System.out.println("Order total: " + service.getTotal(5001));

        System.out.println("\n=== JSON Nested Data ===");

        Map<String, Object> nested = new LinkedHashMap<>();

        nested.put(
            "customer",
            Map.of(
                "address",
                Map.of(
                    "city", "Lucknow",
                    "country", "India"
                )
            )
        );

        Map<String, Object> customerNode =
            (Map<String, Object>) nested.get("customer");

        Map<String, Object> address =
            (Map<String, Object>) customerNode.get("address");

        System.out.println("City: " + address.get("city"));

        System.out.println("\n=== JSON File Persistence ===");

        Path directory = Files.createTempDirectory("json-workflow");

        try {
            Path file = directory.resolve("orders.json");

            JSONFileRepository repository =
                new JSONFileRepository(file);

            repository.save(service.export());

            Object loaded = repository.load();

            System.out.println(JSONSerializer.stringify(loaded));
        } finally {
            try (var files = Files.walk(directory)) {
                files.sorted(Comparator.reverseOrder())
                    .forEach(path -> {
                        try {
                            Files.deleteIfExists(path);
                        } catch (IOException error) {
                            throw new UncheckedIOException(error);
                        }
                    });
            }
        }

        System.out.println("\n=== Sensitive Data Filtering ===");

        Map<String, Object> sensitive = Map.of(
            "username", "atul",
            "access_token", "hidden",
            "profile", Map.of(
                "email", "atul@example.com",
                "password", "hidden"
            )
        );

        Object sanitized = sanitize(sensitive);

        System.out.println(JSONSerializer.stringify(sanitized));

        System.out.println("\n=== JSON Hash ===");

        System.out.println(
            sha256(JSONSerializer.stringify(customerDocument))
        );

        System.out.println("\n=== Error Handling ===");

        List<String> invalidInputs = List.of(
            "{\"name\":\"Atul\",}",
            "{\"value\":NaN}",
            "{\"name\":\"A\",\"name\":\"B\"}",
            "[1,2,]"
        );

        for (String input : invalidInputs) {
            try {
                new JSONParser(input).parse();
                System.out.println("Unexpected acceptance");
            } catch (JSONException error) {
                System.out.println("Rejected: " + error.getMessage());
            }
        }

        System.out.println("\n=== Assertions ===");

        if (service.getTotal(5001) != 66600) {
            throw new AssertionError("Incorrect order total");
        }

        if (!customer.name().equals("Atul Pandey")) {
            throw new AssertionError("Customer validation failed");
        }

        System.out.println("All JSON workflow checks passed.");
    }
}
