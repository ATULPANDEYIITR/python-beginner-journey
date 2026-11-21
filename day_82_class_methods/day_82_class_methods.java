import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

/*
 * CLASS METHODS AND CLASS-LEVEL OPERATIONS IN JAVA 17
 *
 * Demonstrates:
 * - Static factory methods
 * - Static state
 * - Alternative constructors
 * - Static inheritance and method hiding
 * - Immutable report records
 * - Concurrent registries
 * - Business policy validation
 * - Enterprise service operations
 *
 * Compile:
 * javac ClassMethods.java
 *
 * Run:
 * java ClassMethods
 */

public class ClassMethods {

    enum ProductStatus {
        ACTIVE,
        DISCONTINUED
    }

    enum ProductCategory {
        ELECTRONICS,
        SOFTWARE,
        FURNITURE
    }

    static class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    record ProductInput(
        String id,
        String name,
        BigDecimal price,
        ProductCategory category
    ) {}

    record CategoryReport(
        ProductCategory category,
        long productCount,
        BigDecimal totalValue
    ) {}

    record AuditEvent(
        String eventId,
        String productId,
        String operation,
        Instant timestamp
    ) {}

    static class Product {

        private static final ConcurrentHashMap<String, Product> REGISTRY =
            new ConcurrentHashMap<>();

        private static final AtomicLong CREATED_COUNT =
            new AtomicLong();

        private static volatile BigDecimal minimumPrice =
            new BigDecimal("500.00");

        private final String id;
        private final String name;
        private final ProductCategory category;

        private BigDecimal price;
        private ProductStatus status;

        protected Product(ProductInput input) {
            Objects.requireNonNull(input, "Input is required.");

            this.id = validateText(input.id(), "Product ID");
            this.name = validateText(input.name(), "Product name");

            this.category = Objects.requireNonNull(
                input.category(),
                "Category is required."
            );

            this.price = validatePrice(input.price());
            this.status = ProductStatus.ACTIVE;
        }

        private static String validateText(
            String value,
            String field
        ) {
            if (value == null || value.isBlank()) {
                throw new DomainException(field + " cannot be empty.");
            }

            return value.trim();
        }

        private static BigDecimal validatePrice(BigDecimal price) {
            if (price == null || price.compareTo(BigDecimal.ZERO) <= 0) {
                throw new DomainException("Price must be positive.");
            }

            if (price.compareTo(minimumPrice) < 0) {
                throw new DomainException("Price is below the minimum.");
            }

            return price.setScale(2, RoundingMode.HALF_UP);
        }

        // Static factory method.
        public static Product create(ProductInput input) {
            Product product = new Product(input);

            Product previous = REGISTRY.putIfAbsent(
                product.id,
                product
            );

            if (previous != null) {
                throw new DomainException("Duplicate product ID.");
            }

            CREATED_COUNT.incrementAndGet();

            return product;
        }

        // Alternative constructor.
        public static Product fromCSV(String line) {
            if (line == null) {
                throw new DomainException("CSV cannot be null.");
            }

            String[] fields = line.split(",", -1);

            if (fields.length != 4) {
                throw new DomainException(
                    "Expected ID, name, price, category."
                );
            }

            try {
                return create(new ProductInput(
                    fields[0].trim(),
                    fields[1].trim(),
                    new BigDecimal(fields[2].trim()),
                    ProductCategory.valueOf(
                        fields[3].trim().toUpperCase()
                    )
                ));
            } catch (NumberFormatException | IllegalArgumentException error) {
                throw new DomainException(
                    "Invalid CSV values: " + error.getMessage()
                );
            }
        }

        public static Optional<Product> findById(String id) {
            return Optional.ofNullable(REGISTRY.get(id));
        }

        public static List<Product> findAll() {
            return REGISTRY.values()
                .stream()
                .sorted(Comparator.comparing(Product::getId))
                .toList();
        }

        public static long count() {
            return REGISTRY.size();
        }

        public static long createdCount() {
            return CREATED_COUNT.get();
        }

        public static void updateMinimumPrice(BigDecimal amount) {
            if (amount == null ||
                amount.compareTo(BigDecimal.ZERO) <= 0) {

                throw new DomainException(
                    "Minimum price must be positive."
                );
            }

            minimumPrice = amount.setScale(2, RoundingMode.HALF_UP);
        }

        public static BigDecimal getMinimumPrice() {
            return minimumPrice;
        }

        public static List<CategoryReport> generateReport() {
            Map<ProductCategory, List<Product>> grouped =
                REGISTRY.values()
                    .stream()
                    .filter(p -> p.status == ProductStatus.ACTIVE)
                    .collect(Collectors.groupingBy(p -> p.category));

            return grouped.entrySet()
                .stream()
                .map(entry -> {
                    BigDecimal total = entry.getValue()
                        .stream()
                        .map(p -> p.price)
                        .reduce(BigDecimal.ZERO, BigDecimal::add);

                    return new CategoryReport(
                        entry.getKey(),
                        entry.getValue().size(),
                        total
                    );
                })
                .sorted(Comparator.comparing(
                    report -> report.category().name()
                ))
                .toList();
        }

        public static boolean discontinue(String id) {
            Product product = REGISTRY.get(id);

            if (product == null) {
                return false;
            }

            synchronized (product) {
                product.status = ProductStatus.DISCONTINUED;
            }

            return true;
        }

        // Static utility method.
        public static BigDecimal calculateTax(
            BigDecimal amount,
            BigDecimal taxRate
        ) {
            if (amount == null || taxRate == null ||
                amount.signum() < 0 ||
                taxRate.signum() < 0 ||
                taxRate.compareTo(new BigDecimal("100")) > 0) {

                throw new DomainException("Invalid tax inputs.");
            }

            return amount.multiply(taxRate)
                .divide(new BigDecimal("100"), 2, RoundingMode.HALF_UP);
        }

        public synchronized void applyDiscount(BigDecimal percentage) {
            if (status != ProductStatus.ACTIVE) {
                throw new DomainException(
                    "Discontinued products cannot be discounted."
                );
            }

            if (percentage == null ||
                percentage.signum() < 0 ||
                percentage.compareTo(new BigDecimal("50")) > 0) {

                throw new DomainException(
                    "Discount must be between 0 and 50."
                );
            }

            BigDecimal multiplier = BigDecimal.ONE.subtract(
                percentage.divide(
                    new BigDecimal("100"),
                    4,
                    RoundingMode.HALF_UP
                )
            );

            price = price.multiply(multiplier)
                .setScale(2, RoundingMode.HALF_UP);
        }

        public String getId() {
            return id;
        }

        public BigDecimal getPrice() {
            return price;
        }

        public ProductStatus getStatus() {
            return status;
        }

        @Override
        public String toString() {
            return "Product{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", category=" + category +
                ", price=" + price +
                ", status=" + status +
                '}';
        }
    }

    static final class SubscriptionProduct extends Product {

        private final int durationMonths;

        private SubscriptionProduct(
            ProductInput input,
            int durationMonths
        ) {
            super(input);

            if (durationMonths < 1 || durationMonths > 60) {
                throw new DomainException(
                    "Duration must be between 1 and 60 months."
                );
            }

            this.durationMonths = durationMonths;
        }

        public static SubscriptionProduct createSubscription(
            ProductInput input,
            int durationMonths
        ) {
            SubscriptionProduct product =
                new SubscriptionProduct(input, durationMonths);

            Product previous = Product.REGISTRY.putIfAbsent(
                input.id(),
                product
            );

            if (previous != null) {
                throw new DomainException("Duplicate product ID.");
            }

            Product.CREATED_COUNT.incrementAndGet();

            return product;
        }

        public int getDurationMonths() {
            return durationMonths;
        }

        // Static methods are hidden, not overridden.
        public static String getProductType() {
            return "SUBSCRIPTION";
        }
    }

    static final class ProductService {

        private final List<AuditEvent> auditLog =
            Collections.synchronizedList(new ArrayList<>());

        public Product register(ProductInput input) {
            Product product = Product.create(input);

            auditLog.add(new AuditEvent(
                UUID.randomUUID().toString(),
                product.getId(),
                "REGISTER",
                Instant.now()
            ));

            return product;
        }

        public boolean discontinue(String id) {
            boolean changed = Product.discontinue(id);

            if (changed) {
                auditLog.add(new AuditEvent(
                    UUID.randomUUID().toString(),
                    id,
                    "DISCONTINUE",
                    Instant.now()
                ));
            }

            return changed;
        }

        public List<AuditEvent> getAuditLog() {
            synchronized (auditLog) {
                return List.copyOf(auditLog);
            }
        }
    }

    public static void main(String[] args) {

        try {
            System.out.println("1. Configure class-level policy");

            Product.updateMinimumPrice(
                new BigDecimal("500.00")
            );

            System.out.println(Product.getMinimumPrice());

            System.out.println("\n2. Static factory");

            ProductService service = new ProductService();

            Product laptop = service.register(
                new ProductInput(
                    "P101",
                    "Business Laptop",
                    new BigDecimal("75000"),
                    ProductCategory.ELECTRONICS
                )
            );

            System.out.println(laptop);

            System.out.println("\n3. Alternative constructor");

            Product chair = Product.fromCSV(
                "P102,Office Chair,12500,FURNITURE"
            );

            System.out.println(chair);

            System.out.println("\n4. Subclass-specific factory");

            SubscriptionProduct subscription =
                SubscriptionProduct.createSubscription(
                    new ProductInput(
                        "S101",
                        "Security Platform",
                        new BigDecimal("12000"),
                        ProductCategory.SOFTWARE
                    ),
                    12
                );

            System.out.println(subscription);
            System.out.println(
                "Duration: " + subscription.getDurationMonths()
            );

            System.out.println("\n5. Class-level lookup");

            System.out.println(
                Product.findById("P101").orElseThrow()
            );

            System.out.println("\n6. Instance operation");

            laptop.applyDiscount(new BigDecimal("10"));

            System.out.println(laptop.getPrice());

            System.out.println("\n7. Category reports");

            Product.generateReport().forEach(System.out::println);

            System.out.println("\n8. Static utility");

            System.out.println(
                Product.calculateTax(
                    new BigDecimal("75000"),
                    new BigDecimal("18")
                )
            );

            System.out.println("\n9. State transition");

            service.discontinue("P102");

            System.out.println(chair.getStatus());

            System.out.println("\n10. Registry statistics");

            System.out.println("Current: " + Product.count());
            System.out.println("Created: " + Product.createdCount());

            System.out.println("\n11. Audit trail");

            service.getAuditLog().forEach(System.out::println);

            System.out.println("\n12. Failure handling");

            try {
                Product.create(new ProductInput(
                    "P103",
                    "Invalid Product",
                    new BigDecimal("-100"),
                    ProductCategory.ELECTRONICS
                ));
            } catch (DomainException error) {
                System.out.println("Rejected: " + error.getMessage());
            }

        } catch (Exception error) {
            System.err.println(
                "Application failure: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
