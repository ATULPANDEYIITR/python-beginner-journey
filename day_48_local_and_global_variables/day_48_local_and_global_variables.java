import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.DoubleUnaryOperator;

public class VariableScopeEnterprise {

    // Static fields belong to the class rather than individual instances.
    private static final String APPLICATION_NAME = "Enterprise Inventory";
    private static final double TAX_RATE = 0.18;
    private static int processedTransactions = 0;

    private final String warehouseName;
    private final int capacity;
    private int stock;
    private final List<String> auditTrail = new ArrayList<>();

    public VariableScopeEnterprise(String warehouseName, int capacity, int initialStock) {
        this.warehouseName = Objects.requireNonNull(
            warehouseName, "Warehouse name is required."
        );

        if (warehouseName.isBlank()) {
            throw new IllegalArgumentException("Warehouse name cannot be blank.");
        }
        if (capacity < 0 || initialStock < 0 || initialStock > capacity) {
            throw new IllegalArgumentException("Invalid capacity or initial stock.");
        }

        this.capacity = capacity;
        this.stock = initialStock;
    }

    public void receive(int quantity) {
        validatePositiveQuantity(quantity);

        if (quantity > capacity - stock) {
            throw new IllegalStateException("Warehouse capacity exceeded.");
        }

        stock += quantity;
        auditTrail.add("Received " + quantity + "; stock=" + stock);
        processedTransactions++;
    }

    public void dispatch(int quantity) {
        validatePositiveQuantity(quantity);

        if (quantity > stock) {
            throw new IllegalStateException("Insufficient stock.");
        }

        stock -= quantity;
        auditTrail.add("Dispatched " + quantity + "; stock=" + stock);
        processedTransactions++;
    }

    private static void validatePositiveQuantity(int quantity) {
        // A parameter is local to the method invocation.
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive.");
        }
    }

    public int getStock() {
        return stock;
    }

    public List<String> getAuditTrail() {
        // Return a snapshot so callers cannot mutate the internal collection.
        return List.copyOf(auditTrail);
    }

    public static int getProcessedTransactions() {
        return processedTransactions;
    }

    private double calculateInvoice(double unitPrice, int quantity) {
        if (!Double.isFinite(unitPrice) || unitPrice < 0 || quantity < 0) {
            throw new IllegalArgumentException("Invalid price or quantity.");
        }

        // Local variables isolate calculations from object and class state.
        double subtotal = unitPrice * quantity;
        double tax = subtotal * TAX_RATE;
        return Math.round((subtotal + tax) * 100.0) / 100.0;
    }

    private DoubleUnaryOperator createMarkupCalculator(double markupRate) {
        if (!Double.isFinite(markupRate) || markupRate < -1.0) {
            throw new IllegalArgumentException("Invalid markup rate.");
        }

        // Captured local variables must be final or effectively final.
        final double capturedMarkupRate = markupRate;

        return price -> {
            if (!Double.isFinite(price) || price < 0) {
                throw new IllegalArgumentException("Invalid price.");
            }
            return price * (1.0 + capturedMarkupRate);
        };
    }

    private void demonstrateShadowing() {
        String warehouseName = "Temporary Report";
        // The local variable shadows the instance field.
        System.out.println("Local name: " + warehouseName);
        System.out.println("Instance name: " + this.warehouseName);
    }

    private void demonstrateLoopScope() {
        for (int index = 0; index < 3; index++) {
            String localLabel = "shipment-" + index;
            System.out.println(localLabel);
        }

        // index and localLabel are inaccessible outside the loop body.
    }

    public static void main(String[] args) {
        System.out.println("=== " + APPLICATION_NAME + " ===");

        try {
            VariableScopeEnterprise lucknow =
                new VariableScopeEnterprise("Lucknow Hub", 400, 100);

            VariableScopeEnterprise kanpur =
                new VariableScopeEnterprise("Kanpur Hub", 250, 60);

            lucknow.receive(35);
            lucknow.dispatch(20);
            kanpur.receive(15);

            System.out.println(lucknow.warehouseName + " stock: " + lucknow.getStock());
            System.out.println(kanpur.warehouseName + " stock: " + kanpur.getStock());

            System.out.println("Invoice: ₹" + lucknow.calculateInvoice(1250.0, 2));

            DoubleUnaryOperator applyMarkup = lucknow.createMarkupCalculator(0.12);
            System.out.printf("Marked-up price: ₹%.2f%n", applyMarkup.applyAsDouble(500));

            lucknow.demonstrateShadowing();
            lucknow.demonstrateLoopScope();

            System.out.println("Transactions across instances: "
                + VariableScopeEnterprise.getProcessedTransactions());

            System.out.println("Lucknow audit:");
            lucknow.getAuditTrail().forEach(System.out::println);

            try {
                lucknow.dispatch(10_000);
            } catch (IllegalStateException exception) {
                System.out.println("Rejected operation: " + exception.getMessage());
            }

            System.out.println("Stock after rejected dispatch: " + lucknow.getStock());

        } catch (IllegalArgumentException | IllegalStateException exception) {
            System.err.println("Inventory operation failed: " + exception.getMessage());
        }
    }
}
