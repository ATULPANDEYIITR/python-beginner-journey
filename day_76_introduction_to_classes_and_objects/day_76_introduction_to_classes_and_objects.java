import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * INTRODUCTION TO CLASSES AND OBJECTS
 *
 * Enterprise scenario: Order management system.
 *
 * Demonstrates:
 * - Classes and objects
 * - Encapsulation
 * - Constructors
 * - Inheritance
 * - Interfaces
 * - Abstraction
 * - Records
 * - Enums
 * - Generics
 * - Collections and streams
 * - Composition
 * - Immutable values
 * - State transitions
 * - Custom exceptions
 */

public class Main {

    enum OrderStatus {
        CREATED,
        CONFIRMED,
        PROCESSING,
        SHIPPED,
        DELIVERED,
        CANCELLED
    }

    static class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    static class ValidationException extends DomainException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class StateException extends DomainException {
        StateException(String message) {
            super(message);
        }
    }

    /*
     * Record:
     * An immutable data carrier with generated constructor,
     * accessors, equals, hashCode, and toString methods.
     */
    record Address(
        String street,
        String city,
        String postalCode,
        String country
    ) {
        Address {
            if (
                street == null || street.isBlank() ||
                city == null || city.isBlank() ||
                postalCode == null || postalCode.isBlank() ||
                country == null || country.isBlank()
            ) {
                throw new ValidationException(
                    "All address fields are required."
                );
            }
        }
    }

    record OrderEvent(
        OrderStatus status,
        Instant timestamp,
        String description
    ) {}

    interface DiscountPolicy {
        BigDecimal calculateDiscount(BigDecimal subtotal);
    }

    static class StandardDiscount implements DiscountPolicy {

        private final BigDecimal rate;

        StandardDiscount(BigDecimal rate) {
            Objects.requireNonNull(rate);

            if (
                rate.compareTo(BigDecimal.ZERO) < 0 ||
                rate.compareTo(new BigDecimal("0.50")) > 0
            ) {
                throw new ValidationException(
                    "Discount must be between 0% and 50%."
                );
            }

            this.rate = rate;
        }

        @Override
        public BigDecimal calculateDiscount(BigDecimal subtotal) {
            return subtotal.multiply(rate)
                .setScale(2, RoundingMode.HALF_UP);
        }
    }

    static abstract class Product {

        private final String productId;
        private final String name;
        private final BigDecimal price;

        protected Product(
            String productId,
            String name,
            BigDecimal price
        ) {
            if (
                productId == null || productId.isBlank() ||
                name == null || name.isBlank()
            ) {
                throw new ValidationException(
                    "Product identifier and name are required."
                );
            }

            Objects.requireNonNull(price);

            if (price.compareTo(BigDecimal.ZERO) <= 0) {
                throw new ValidationException(
                    "Product price must be positive."
                );
            }

            this.productId = productId;
            this.name = name;
            this.price = price.setScale(2, RoundingMode.HALF_UP);
        }

        public String getProductId() {
            return productId;
        }

        public String getName() {
            return name;
        }

        public BigDecimal getPrice() {
            return price;
        }

        public abstract String getCategory();
    }

    static class PhysicalProduct extends Product {

        private final double weightKg;

        PhysicalProduct(
            String id,
            String name,
            BigDecimal price,
            double weightKg
        ) {
            super(id, name, price);

            if (!Double.isFinite(weightKg) || weightKg <= 0) {
                throw new ValidationException(
                    "Weight must be positive and finite."
                );
            }

            this.weightKg = weightKg;
        }

        public double getWeightKg() {
            return weightKg;
        }

        @Override
        public String getCategory() {
            return "PHYSICAL";
        }
    }

    static class DigitalProduct extends Product {

        private final String downloadFormat;

        DigitalProduct(
            String id,
            String name,
            BigDecimal price,
            String downloadFormat
        ) {
            super(id, name, price);

            if (
                downloadFormat == null ||
                downloadFormat.isBlank()
            ) {
                throw new ValidationException(
                    "Download format is required."
                );
            }

            this.downloadFormat = downloadFormat;
        }

        @Override
        public String getCategory() {
            return "DIGITAL";
        }

        public String getDownloadFormat() {
            return downloadFormat;
        }
    }

    /*
     * Generic inventory class.
     * A Map maintains average O(1) product lookup.
     */
    static class Inventory<T extends Product> {

        private final Map<String, T> products = new HashMap<>();

        public void add(T product) {
            Objects.requireNonNull(product);

            if (products.containsKey(product.getProductId())) {
                throw new DomainException(
                    "Product identifier already exists."
                );
            }

            products.put(product.getProductId(), product);
        }

        public T get(String id) {
            T product = products.get(id);

            if (product == null) {
                throw new DomainException("Product not found: " + id);
            }

            return product;
        }

        public List<T> getAll() {
            return List.copyOf(products.values());
        }

        public int size() {
            return products.size();
        }
    }

    static class OrderItem {

        private final Product product;
        private final int quantity;

        OrderItem(Product product, int quantity) {
            this.product = Objects.requireNonNull(product);

            if (quantity <= 0) {
                throw new ValidationException(
                    "Quantity must be positive."
                );
            }

            this.quantity = quantity;
        }

        public BigDecimal subtotal() {
            return product.getPrice()
                .multiply(BigDecimal.valueOf(quantity));
        }

        public Product getProduct() {
            return product;
        }

        public int getQuantity() {
            return quantity;
        }
    }

    static class Customer {

        private final String customerId;
        private final String name;
        private final Address address;

        Customer(
            String customerId,
            String name,
            Address address
        ) {
            if (
                customerId == null || customerId.isBlank() ||
                name == null || name.isBlank()
            ) {
                throw new ValidationException(
                    "Customer information is required."
                );
            }

            this.customerId = customerId;
            this.name = name;
            this.address = Objects.requireNonNull(address);
        }

        public String getCustomerId() {
            return customerId;
        }

        public String getName() {
            return name;
        }

        public Address getAddress() {
            return address;
        }
    }

    static class Order {

        private static final Set<OrderStatus> TERMINAL_STATES =
            Set.of(OrderStatus.DELIVERED, OrderStatus.CANCELLED);

        private static final Map<OrderStatus, Set<OrderStatus>>
            TRANSITIONS = Map.of(
                OrderStatus.CREATED,
                Set.of(OrderStatus.CONFIRMED, OrderStatus.CANCELLED),

                OrderStatus.CONFIRMED,
                Set.of(OrderStatus.PROCESSING, OrderStatus.CANCELLED),

                OrderStatus.PROCESSING,
                Set.of(OrderStatus.SHIPPED, OrderStatus.CANCELLED),

                OrderStatus.SHIPPED,
                Set.of(OrderStatus.DELIVERED),

                OrderStatus.DELIVERED,
                Set.of(),

                OrderStatus.CANCELLED,
                Set.of()
            );

        private final String orderId;
        private final Customer customer;
        private final List<OrderItem> items;
        private final DiscountPolicy discountPolicy;
        private final List<OrderEvent> history = new ArrayList<>();

        private OrderStatus status;

        Order(
            Customer customer,
            List<OrderItem> items,
            DiscountPolicy discountPolicy
        ) {
            this.orderId = UUID.randomUUID().toString();
            this.customer = Objects.requireNonNull(customer);

            if (items == null || items.isEmpty()) {
                throw new ValidationException(
                    "An order must contain at least one item."
                );
            }

            this.items = List.copyOf(items);
            this.discountPolicy = Objects.requireNonNull(
                discountPolicy
            );

            this.status = OrderStatus.CREATED;

            recordEvent("Order created.");
        }

        public String getOrderId() {
            return orderId;
        }

        public OrderStatus getStatus() {
            return status;
        }

        public Customer getCustomer() {
            return customer;
        }

        public List<OrderItem> getItems() {
            return items;
        }

        public List<OrderEvent> getHistory() {
            return Collections.unmodifiableList(history);
        }

        public BigDecimal getSubtotal() {
            return items.stream()
                .map(OrderItem::subtotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
                .setScale(2, RoundingMode.HALF_UP);
        }

        public BigDecimal getDiscount() {
            BigDecimal discount =
                discountPolicy.calculateDiscount(getSubtotal());

            if (
                discount.compareTo(BigDecimal.ZERO) < 0 ||
                discount.compareTo(getSubtotal()) > 0
            ) {
                throw new DomainException(
                    "Discount policy returned an invalid value."
                );
            }

            return discount;
        }

        public BigDecimal getTotal() {
            return getSubtotal()
                .subtract(getDiscount())
                .setScale(2, RoundingMode.HALF_UP);
        }

        private void recordEvent(String description) {
            history.add(
                new OrderEvent(status, Instant.now(), description)
            );
        }

        public void transitionTo(OrderStatus nextStatus) {
            Objects.requireNonNull(nextStatus);

            if (TERMINAL_STATES.contains(status)) {
                throw new StateException(
                    "Terminal orders cannot be modified."
                );
            }

            if (!TRANSITIONS.get(status).contains(nextStatus)) {
                throw new StateException(
                    "Invalid transition: " + status +
                    " -> " + nextStatus
                );
            }

            status = nextStatus;

            recordEvent("Status changed to " + nextStatus);
        }
    }

    static class OrderService {

        private final Map<String, Order> orders = new HashMap<>();

        public void register(Order order) {
            Objects.requireNonNull(order);

            if (orders.containsKey(order.getOrderId())) {
                throw new DomainException(
                    "Order is already registered."
                );
            }

            orders.put(order.getOrderId(), order);
        }

        public Order find(String id) {
            Order order = orders.get(id);

            if (order == null) {
                throw new DomainException("Order not found.");
            }

            return order;
        }

        public List<Order> findByStatus(OrderStatus status) {
            return orders.values().stream()
                .filter(order -> order.getStatus() == status)
                .toList();
        }

        public BigDecimal totalRevenue() {
            return orders.values().stream()
                .filter(
                    order -> order.getStatus() ==
                        OrderStatus.DELIVERED
                )
                .map(Order::getTotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        }

        public int count() {
            return orders.size();
        }
    }

    public static void main(String[] args) {

        try {
            Inventory<Product> inventory = new Inventory<>();

            Product laptop = new PhysicalProduct(
                "P101",
                "Business Laptop",
                new BigDecimal("65000.00"),
                2.1
            );

            Product software = new DigitalProduct(
                "P102",
                "Security Software",
                new BigDecimal("5000.00"),
                "LICENSE"
            );

            inventory.add(laptop);
            inventory.add(software);

            Customer customer = new Customer(
                "C101",
                "Riya Sharma",
                new Address(
                    "MG Road",
                    "Lucknow",
                    "226001",
                    "India"
                )
            );

            List<OrderItem> items = List.of(
                new OrderItem(inventory.get("P101"), 1),
                new OrderItem(inventory.get("P102"), 2)
            );

            DiscountPolicy policy = new StandardDiscount(
                new BigDecimal("0.10")
            );

            Order order = new Order(
                customer,
                items,
                policy
            );

            OrderService service = new OrderService();
            service.register(order);

            System.out.println("Order ID: " + order.getOrderId());
            System.out.println("Customer: " + customer.getName());
            System.out.println("Inventory size: " + inventory.size());

            System.out.println(
                "Subtotal: " + order.getSubtotal()
            );

            System.out.println(
                "Discount: " + order.getDiscount()
            );

            System.out.println(
                "Total: " + order.getTotal()
            );

            // Explicit business-state transitions.
            order.transitionTo(OrderStatus.CONFIRMED);
            order.transitionTo(OrderStatus.PROCESSING);
            order.transitionTo(OrderStatus.SHIPPED);
            order.transitionTo(OrderStatus.DELIVERED);

            System.out.println("\nOrder history:");

            order.getHistory().forEach(event ->
                System.out.println(
                    event.timestamp() + " | " +
                    event.status() + " | " +
                    event.description()
                )
            );

            System.out.println(
                "\nDelivered orders: " +
                service.findByStatus(OrderStatus.DELIVERED).size()
            );

            System.out.println(
                "Revenue: " + service.totalRevenue()
            );

            // Verify terminal-state protection.
            try {
                order.transitionTo(OrderStatus.CANCELLED);
            } catch (StateException exception) {
                System.out.println(
                    "Expected state error: " +
                    exception.getMessage()
                );
            }

            // Verify validation.
            try {
                new OrderItem(laptop, 0);
            } catch (ValidationException exception) {
                System.out.println(
                    "Expected validation error: " +
                    exception.getMessage()
                );
            }

            // Verify missing product handling.
            try {
                inventory.get("UNKNOWN");
            } catch (DomainException exception) {
                System.out.println(
                    "Expected lookup error: " +
                    exception.getMessage()
                );
            }

            // Demonstrate stream-based category reporting.
            Map<String, Long> categoryCounts =
                inventory.getAll().stream()
                    .collect(
                        Collectors.groupingBy(
                            Product::getCategory,
                            Collectors.counting()
                        )
                    );

            System.out.println(
                "\nProduct category counts: " + categoryCounts
            );

            System.out.println("\nProgram completed successfully.");

        } catch (DomainException exception) {
            System.err.println(
                "Business failure: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
