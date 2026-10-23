import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.BinaryOperator;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class FunctionalOrderGovernance {

    enum OrderStatus {
        PAID,
        PENDING,
        CANCELLED
    }

    record Order(
        long id,
        String customer,
        String department,
        double amount,
        OrderStatus status
    ) {
        Order {
            if (id <= 0) {
                throw new IllegalArgumentException("Order id must be positive");
            }
            if (customer == null || customer.isBlank()) {
                throw new IllegalArgumentException("Customer is required");
            }
            if (department == null || department.isBlank()) {
                throw new IllegalArgumentException("Department is required");
            }
            if (!Double.isFinite(amount) || amount < 0) {
                throw new IllegalArgumentException("Amount must be non-negative");
            }
            Objects.requireNonNull(status, "status is required");
        }
    }

    record OrderProjection(
        long id,
        String customer,
        double amount,
        double serviceFee
    ) {}

    record DepartmentTotal(
        String department,
        double amount
    ) {}

    static <T, R> List<R> map(
        List<T> source,
        Function<T, R> mapper
    ) {
        return source.stream()
            .map(mapper)
            .toList();
    }

    static <T> List<T> filter(
        List<T> source,
        Predicate<T> predicate
    ) {
        return source.stream()
            .filter(predicate)
            .toList();
    }

    static <T> T reduce(
        List<T> source,
        T identity,
        BinaryOperator<T> accumulator
    ) {
        return source.stream()
            .reduce(identity, accumulator);
    }

    static double roundMoney(double amount) {
        return Math.round(amount * 100.0) / 100.0;
    }

    static OrderProjection projectOrder(Order order) {
        double fee = roundMoney(order.amount() * 0.015);

        return new OrderProjection(
            order.id(),
            order.customer(),
            order.amount(),
            fee
        );
    }

    static boolean isRevenueEligible(Order order) {
        return order.status() == OrderStatus.PAID
            && order.amount() >= 5000;
    }

    static Map<String, Double> departmentRevenue(
        List<Order> orders
    ) {
        /*
         * filter selects records under the revenue policy.
         * map transforms the selected domain objects into their monetary
         * contribution.
         * groupingBy then creates a departmental aggregation.
         */
        return orders.stream()
            .filter(FunctionalOrderGovernance::isRevenueEligible)
            .collect(Collectors.groupingBy(
                Order::department,
                Collectors.summingDouble(Order::amount)
            ))
            .entrySet()
            .stream()
            .collect(Collectors.toUnmodifiableMap(
                Map.Entry::getKey,
                entry -> roundMoney(entry.getValue())
            ));
    }

    static double totalRevenue(List<Order> orders) {
        List<Double> eligibleAmounts = map(
            filter(orders, FunctionalOrderGovernance::isRevenueEligible),
            Order::amount
        );

        return roundMoney(
            reduce(
                eligibleAmounts,
                0.0,
                Double::sum
            )
        );
    }

    static List<DepartmentTotal> departmentTotals(
        List<Order> orders
    ) {
        return departmentRevenue(orders)
            .entrySet()
            .stream()
            .map(entry -> new DepartmentTotal(
                entry.getKey(),
                entry.getValue()
            ))
            .sorted((left, right) ->
                Double.compare(right.amount(), left.amount()))
            .toList();
    }

    public static void main(String[] args) {
        List<Order> orders = List.of(
            new Order(9001, "Asha", "Engineering", 12000, OrderStatus.PAID),
            new Order(9002, "Rahul", "Finance", 4700, OrderStatus.PAID),
            new Order(9003, "Meera", "Engineering", 18500, OrderStatus.PAID),
            new Order(9004, "Kabir", "Operations", 9100, OrderStatus.PENDING),
            new Order(9005, "Nisha", "Finance", 7300, OrderStatus.PAID)
        );

        List<Order> eligible = filter(
            orders,
            FunctionalOrderGovernance::isRevenueEligible
        );

        List<OrderProjection> projections = map(
            eligible,
            FunctionalOrderGovernance::projectOrder
        );

        double total = totalRevenue(orders);

        System.out.println("Revenue-eligible orders:");
        projections.forEach(projection ->
            System.out.printf(
                "  %d | %s | %.2f | fee %.2f%n",
                projection.id(),
                projection.customer(),
                projection.amount(),
                projection.serviceFee()
            )
        );

        System.out.printf(
            "%nTotal eligible revenue: %.2f%n",
            total
        );

        System.out.println("\nDepartment totals:");
        departmentTotals(orders).forEach(totalByDepartment ->
            System.out.printf(
                "  %s: %.2f%n",
                totalByDepartment.department(),
                totalByDepartment.amount()
            )
        );

        /*
         * Java streams are lazy until a terminal operation is invoked.
         * map and filter describe transformations and selection, while
         * reduce supplies a single accumulated result.
         *
         * An identity value is important for empty input because it defines
         * the result without requiring an arbitrary first element.
         */
        List<Integer> empty = new ArrayList<>();
        int emptySum = reduce(empty, 0, Integer::sum);

        System.out.println("\nEmpty reduction: " + emptySum);

        /*
         * Performance:
         * A linear stream pipeline is normally O(n). Grouping introduces
         * additional memory proportional to the number of departments.
         *
         * Domain records are immutable, reducing accidental mutation while
         * processing a shared collection.
         */
    }
}
