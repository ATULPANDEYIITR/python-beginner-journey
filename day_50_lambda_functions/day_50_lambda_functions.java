import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;

/**
 * Enterprise-oriented model of Lambda-style serverless execution.
 *
 * The model separates:
 * - domain events
 * - handler logic
 * - invocation policy
 * - idempotency
 * - event routing
 * - failure states
 *
 * Compile:
 * javac LambdaFunctionsDemo.java
 *
 * Run:
 * java LambdaFunctionsDemo
 */
public class LambdaFunctionsDemo {

    enum InvocationStatus {
        SUCCESS,
        VALIDATION_FAILURE,
        HANDLER_FAILURE,
        TIMEOUT,
        DUPLICATE
    }

    enum EventType {
        ORDER_CREATED,
        PAYMENT_REQUESTED
    }

    record Order(
            String orderId,
            String customerId,
            double amount,
            String currency,
            String idempotencyKey) {

        Order {
            if (orderId == null || orderId.isBlank()) {
                throw new IllegalArgumentException("orderId is required");
            }
            if (customerId == null || customerId.isBlank()) {
                throw new IllegalArgumentException("customerId is required");
            }
            if (!Double.isFinite(amount) || amount <= 0) {
                throw new IllegalArgumentException(
                        "amount must be finite and positive");
            }
            if (currency == null || currency.isBlank()) {
                throw new IllegalArgumentException("currency is required");
            }
            if (idempotencyKey == null || idempotencyKey.isBlank()) {
                throw new IllegalArgumentException(
                        "idempotencyKey is required");
            }
        }

        Order withAmount(double newAmount) {
            return new Order(
                    orderId,
                    customerId,
                    Math.round(newAmount * 100.0) / 100.0,
                    currency,
                    idempotencyKey);
        }
    }

    record InvocationContext(
            String requestId,
            Instant invokedAt) {
    }

    record InvocationResult<T>(
            String requestId,
            InvocationStatus status,
            T value,
            String error,
            long durationNanos) {

        boolean successful() {
            return status == InvocationStatus.SUCCESS;
        }
    }

    interface LambdaHandler<I, O> {
        O handle(I input, InvocationContext context) throws Exception;
    }

    static final class LambdaFunction<I, O> {
        private final String name;
        private final LambdaHandler<I, O> handler;
        private final long timeoutMillis;
        private int invocationCount;

        LambdaFunction(
                String name,
                LambdaHandler<I, O> handler,
                long timeoutMillis) {

            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                        "Lambda name is required");
            }
            if (handler == null) {
                throw new IllegalArgumentException(
                        "Lambda handler is required");
            }
            if (timeoutMillis <= 0) {
                throw new IllegalArgumentException(
                        "Timeout must be positive");
            }

            this.name = name;
            this.handler = handler;
            this.timeoutMillis = timeoutMillis;
        }

        InvocationResult<O> invoke(I input) {
            invocationCount++;

            String requestId = UUID.randomUUID().toString();
            InvocationContext context =
                    new InvocationContext(requestId, Instant.now());

            long started = System.nanoTime();

            try {
                O result = handler.handle(input, context);

                long duration = System.nanoTime() - started;
                long durationMillis =
                        duration / 1_000_000;

                if (durationMillis > timeoutMillis) {
                    return new InvocationResult<>(
                            requestId,
                            InvocationStatus.TIMEOUT,
                            null,
                            "Configured Lambda timeout exceeded",
                            duration);
                }

                return new InvocationResult<>(
                        requestId,
                        InvocationStatus.SUCCESS,
                        result,
                        null,
                        duration);

            } catch (IllegalArgumentException ex) {
                return new InvocationResult<>(
                        requestId,
                        InvocationStatus.VALIDATION_FAILURE,
                        null,
                        ex.getMessage(),
                        System.nanoTime() - started);

            } catch (Exception ex) {
                return new InvocationResult<>(
                        requestId,
                        InvocationStatus.HANDLER_FAILURE,
                        null,
                        ex.getMessage(),
                        System.nanoTime() - started);
            }
        }

        String name() {
            return name;
        }

        int invocationCount() {
            return invocationCount;
        }
    }

    static final class IdempotencyRepository {
        private final Set<String> processedKeys = new HashSet<>();

        boolean claim(String key) {
            Objects.requireNonNull(key, "key");
            return processedKeys.add(key);
        }
    }

    static final class OrderPricingService {

        Order calculate(Order order) {
            double rate;

            if (order.amount() >= 10_000) {
                rate = 0.15;
            } else if (order.amount() >= 5_000) {
                rate = 0.10;
            } else if (order.amount() >= 1_000) {
                rate = 0.05;
            } else {
                rate = 0.0;
            }

            return order.withAmount(
                    order.amount() * (1.0 - rate));
        }
    }

    static final class PaymentService {
        private final IdempotencyRepository repository;

        PaymentService(IdempotencyRepository repository) {
            this.repository = repository;
        }

        Order accept(Order order) {
            if (!repository.claim(order.idempotencyKey())) {
                throw new DuplicateEventException(
                        "Payment event has already been processed");
            }

            return order;
        }
    }

    static final class DuplicateEventException
            extends RuntimeException {

        DuplicateEventException(String message) {
            super(message);
        }
    }

    static final class EventRouter {
        private final Map<EventType, LambdaFunction<Order, Order>>
                handlers = new HashMap<>();

        void register(
                EventType eventType,
                LambdaFunction<Order, Order> function) {

            if (handlers.putIfAbsent(eventType, function) != null) {
                throw new IllegalStateException(
                        "Handler already registered for " + eventType);
            }
        }

        InvocationResult<Order> dispatch(
                EventType eventType,
                Order order) {

            LambdaFunction<Order, Order> function =
                    Optional.ofNullable(handlers.get(eventType))
                            .orElseThrow(() ->
                                    new IllegalStateException(
                                            "No Lambda registered for "
                                                    + eventType));

            return function.invoke(order);
        }
    }

    static void printResult(
            String operation,
            InvocationResult<Order> result) {

        System.out.println(operation);
        System.out.println("Status: " + result.status());
        System.out.println("Request ID: " + result.requestId());

        if (result.successful()) {
            System.out.printf(
                    "Amount: %.2f %s%n",
                    result.value().amount(),
                    result.value().currency());
        } else {
            System.out.println("Error: " + result.error());
        }

        System.out.printf(
                "Duration: %.3f ms%n%n",
                result.durationNanos() / 1_000_000.0);
    }

    public static void main(String[] args) {
        OrderPricingService pricingService =
                new OrderPricingService();

        IdempotencyRepository idempotencyRepository =
                new IdempotencyRepository();

        PaymentService paymentService =
                new PaymentService(idempotencyRepository);

        LambdaFunction<Order, Order> pricingFunction =
                new LambdaFunction<>(
                        "order-pricing",
                        (order, context) ->
                                pricingService.calculate(order),
                        1_000);

        LambdaFunction<Order, Order> paymentFunction =
                new LambdaFunction<>(
                        "payment-processing",
                        (order, context) ->
                                paymentService.accept(order),
                        1_000);

        EventRouter router = new EventRouter();

        router.register(
                EventType.ORDER_CREATED,
                pricingFunction);

        router.register(
                EventType.PAYMENT_REQUESTED,
                paymentFunction);

        Order order = new Order(
                "ORD-1001",
                "CUS-42",
                7_500.00,
                "INR",
                "PAY-ORD-1001");

        InvocationResult<Order> priced =
                router.dispatch(EventType.ORDER_CREATED, order);

        printResult("Pricing invocation", priced);

        if (!priced.successful()) {
            return;
        }

        InvocationResult<Order> payment =
                router.dispatch(
                        EventType.PAYMENT_REQUESTED,
                        priced.value());

        printResult("Payment invocation", payment);

        InvocationResult<Order> duplicatePayment =
                router.dispatch(
                        EventType.PAYMENT_REQUESTED,
                        priced.value());

        printResult("Duplicate payment invocation", duplicatePayment);

        try {
            new Order(
                    "ORD-BAD",
                    "CUS-42",
                    -50,
                    "INR",
                    "BAD-KEY");
        } catch (IllegalArgumentException ex) {
            System.out.println("Domain validation failure:");
            System.out.println(ex.getMessage());
        }

        /*
         * Domain state is intentionally separated from Lambda execution.
         * In production, IdempotencyRepository would normally be backed by
         * durable shared storage. A local HashSet cannot coordinate
         * horizontally scaled function instances.
         */
        System.out.println("\nOperational metrics:");
        System.out.println(
                pricingFunction.name()
                        + ": "
                        + pricingFunction.invocationCount()
                        + " invocations");

        System.out.println(
                paymentFunction.name()
                        + ": "
                        + paymentFunction.invocationCount()
                        + " invocations");
    }
}
