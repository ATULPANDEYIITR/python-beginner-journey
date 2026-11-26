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
 * Method Overriding in an Enterprise Notification Platform.
 *
 * Java version: 17
 */

public class Main {

    enum DeliveryStatus {
        CREATED,
        VALIDATED,
        SENT,
        FAILED
    }

    enum NotificationChannel {
        EMAIL,
        SMS,
        PUSH,
        PRIORITY_EMAIL
    }

    enum Severity {
        LOW,
        NORMAL,
        HIGH,
        CRITICAL
    }

    record NotificationRequest(
        String id,
        String recipient,
        String message,
        Severity severity
    ) {
        NotificationRequest {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Invalid notification ID");
            }

            if (recipient == null || recipient.isBlank()) {
                throw new IllegalArgumentException("Recipient is required");
            }

            if (message == null || message.isBlank()) {
                throw new IllegalArgumentException("Message is required");
            }

            Objects.requireNonNull(severity);
        }
    }

    record DeliveryReceipt(
        String notificationId,
        String channel,
        DeliveryStatus status,
        int messageUnits,
        String description,
        Instant timestamp
    ) {}

    static class NotificationException extends RuntimeException {
        NotificationException(String message) {
            super(message);
        }
    }

    interface DeliveryPolicy {
        double calculateCost(NotificationRequest request);

        void validate(NotificationRequest request);

        String describe();
    }

    abstract static class NotificationService
            implements DeliveryPolicy {

        private final String serviceName;

        protected NotificationService(String serviceName) {
            if (serviceName == null || serviceName.isBlank()) {
                throw new IllegalArgumentException(
                    "Service name is required"
                );
            }

            this.serviceName = serviceName;
        }

        @Override
        public void validate(NotificationRequest request) {
            Objects.requireNonNull(request);

            if (request.message().length() > 5000) {
                throw new NotificationException(
                    "Notification exceeds maximum length"
                );
            }
        }

        @Override
        public String describe() {
            return serviceName;
        }

        public abstract DeliveryReceipt send(
            NotificationRequest request
        );

        protected DeliveryReceipt receipt(
            NotificationRequest request,
            NotificationChannel channel,
            int units,
            String description
        ) {
            return new DeliveryReceipt(
                request.id(),
                channel.name(),
                DeliveryStatus.SENT,
                units,
                description,
                Instant.now()
            );
        }
    }

    static class EmailService extends NotificationService {

        EmailService() {
            super("Standard Email");
        }

        @Override
        public double calculateCost(NotificationRequest request) {
            validate(request);
            return 0.05;
        }

        @Override
        public DeliveryReceipt send(NotificationRequest request) {
            validate(request);

            if (!request.recipient().contains("@")) {
                throw new NotificationException(
                    "Invalid email address"
                );
            }

            return receipt(
                request,
                NotificationChannel.EMAIL,
                1,
                "Standard email delivered"
            );
        }
    }

    static class SmsService extends NotificationService {

        SmsService() {
            super("SMS Gateway");
        }

        @Override
        public double calculateCost(NotificationRequest request) {
            validate(request);

            int length = request.message().length();
            return Math.ceil(length / 160.0) * 0.12;
        }

        @Override
        public DeliveryReceipt send(NotificationRequest request) {
            validate(request);

            if (!request.recipient().matches("\\+?[0-9]{10,15}")) {
                throw new NotificationException(
                    "Invalid mobile number"
                );
            }

            int units = Math.max(
                1,
                (int) Math.ceil(request.message().length() / 160.0)
            );

            return receipt(
                request,
                NotificationChannel.SMS,
                units,
                "SMS delivered in " + units + " unit(s)"
            );
        }
    }

    static class PushService extends NotificationService {

        PushService() {
            super("Mobile Push");
        }

        @Override
        public double calculateCost(NotificationRequest request) {
            validate(request);
            return 0.0;
        }

        @Override
        public DeliveryReceipt send(NotificationRequest request) {
            validate(request);

            if (!request.recipient().startsWith("device:")) {
                throw new NotificationException(
                    "Invalid device identifier"
                );
            }

            return receipt(
                request,
                NotificationChannel.PUSH,
                1,
                "Push notification delivered"
            );
        }
    }

    static class PriorityEmailService extends EmailService {

        @Override
        public double calculateCost(NotificationRequest request) {
            return super.calculateCost(request) + 0.25;
        }

        @Override
        public DeliveryReceipt send(NotificationRequest request) {
            DeliveryReceipt original = super.send(request);

            return new DeliveryReceipt(
                original.notificationId(),
                NotificationChannel.PRIORITY_EMAIL.name(),
                original.status(),
                original.messageUnits(),
                "Priority delivery: " + original.description(),
                original.timestamp()
            );
        }

        @Override
        public String describe() {
            return "Priority Email Service";
        }
    }

    static final class ServiceRegistry {

        private final Map<NotificationChannel, NotificationService>
            services = new HashMap<>();

        void register(
            NotificationChannel channel,
            NotificationService service
        ) {
            Objects.requireNonNull(channel);
            Objects.requireNonNull(service);

            if (services.putIfAbsent(channel, service) != null) {
                throw new IllegalStateException(
                    "Channel already registered: " + channel
                );
            }
        }

        NotificationService get(NotificationChannel channel) {
            NotificationService service = services.get(channel);

            if (service == null) {
                throw new NotificationException(
                    "No service registered for " + channel
                );
            }

            return service;
        }

        Map<NotificationChannel, NotificationService> all() {
            return Collections.unmodifiableMap(services);
        }
    }

    static final class NotificationAudit {

        private final List<DeliveryReceipt> receipts =
            new ArrayList<>();

        void record(DeliveryReceipt receipt) {
            receipts.add(Objects.requireNonNull(receipt));
        }

        List<DeliveryReceipt> getReceipts() {
            return List.copyOf(receipts);
        }

        long countSuccessful() {
            return receipts.stream()
                .filter(r -> r.status() == DeliveryStatus.SENT)
                .count();
        }
    }

    static final class NotificationCoordinator {

        private final ServiceRegistry registry;
        private final NotificationAudit audit;
        private final Set<String> processedIds = new HashSet<>();

        NotificationCoordinator(
            ServiceRegistry registry,
            NotificationAudit audit
        ) {
            this.registry = registry;
            this.audit = audit;
        }

        DeliveryReceipt dispatch(
            NotificationRequest request,
            NotificationChannel channel
        ) {
            Objects.requireNonNull(request);
            Objects.requireNonNull(channel);

            if (processedIds.contains(request.id())) {
                throw new NotificationException(
                    "Duplicate notification request"
                );
            }

            NotificationService service = registry.get(channel);

            service.validate(request);

            double cost = service.calculateCost(request);

            if (!Double.isFinite(cost) || cost < 0) {
                throw new NotificationException(
                    "Invalid calculated delivery cost"
                );
            }

            // Runtime polymorphism selects the concrete send() override.
            DeliveryReceipt receipt = service.send(request);

            audit.record(receipt);
            processedIds.add(request.id());

            return receipt;
        }

        Map<String, Long> reportByChannel() {
            return audit.getReceipts()
                .stream()
                .collect(Collectors.groupingBy(
                    DeliveryReceipt::channel,
                    Collectors.counting()
                ));
        }
    }

    static void demonstrateOverriding() {
        System.out.println("METHOD OVERRIDING");
        System.out.println("==============================");

        ServiceRegistry registry = new ServiceRegistry();

        registry.register(
            NotificationChannel.EMAIL,
            new EmailService()
        );

        registry.register(
            NotificationChannel.SMS,
            new SmsService()
        );

        registry.register(
            NotificationChannel.PUSH,
            new PushService()
        );

        registry.register(
            NotificationChannel.PRIORITY_EMAIL,
            new PriorityEmailService()
        );

        NotificationAudit audit = new NotificationAudit();

        NotificationCoordinator coordinator =
            new NotificationCoordinator(registry, audit);

        List<NotificationRequest> requests = List.of(
            new NotificationRequest(
                "NOT-1001",
                "customer@example.com",
                "Your order has been confirmed.",
                Severity.NORMAL
            ),
            new NotificationRequest(
                "NOT-1002",
                "+919876543210",
                "Your verification code is 123456.",
                Severity.HIGH
            ),
            new NotificationRequest(
                "NOT-1003",
                "device:ANDROID-001",
                "A new login was detected.",
                Severity.CRITICAL
            ),
            new NotificationRequest(
                "NOT-1004",
                "manager@example.com",
                "Critical infrastructure alert.",
                Severity.CRITICAL
            )
        );

        List<NotificationChannel> channels = List.of(
            NotificationChannel.EMAIL,
            NotificationChannel.SMS,
            NotificationChannel.PUSH,
            NotificationChannel.PRIORITY_EMAIL
        );

        for (int i = 0; i < requests.size(); i++) {
            try {
                DeliveryReceipt result = coordinator.dispatch(
                    requests.get(i),
                    channels.get(i)
                );

                System.out.println("\n" + result);
            } catch (NotificationException error) {
                System.out.println(
                    "Delivery failed: " + error.getMessage()
                );
            }
        }

        System.out.println("\nREGISTERED SERVICES");

        registry.all().forEach((channel, service) -> {
            System.out.println(
                channel + " -> " + service.describe()
            );
        });

        System.out.println("\nREPORTING");

        coordinator.reportByChannel().forEach(
            (channel, count) ->
                System.out.println(channel + ": " + count)
        );

        System.out.println(
            "Successful deliveries: " + audit.countSuccessful()
        );

        System.out.println("\nINVALID RECIPIENT TEST");

        try {
            coordinator.dispatch(
                new NotificationRequest(
                    "NOT-1005",
                    "invalid-address",
                    "Test message",
                    Severity.NORMAL
                ),
                NotificationChannel.EMAIL
            );
        } catch (NotificationException error) {
            System.out.println(error.getMessage());
        }

        System.out.println("\nDUPLICATE REQUEST TEST");

        try {
            coordinator.dispatch(
                requests.get(0),
                NotificationChannel.EMAIL
            );
        } catch (NotificationException error) {
            System.out.println(error.getMessage());
        }

        System.out.println("\nINHERITED METHOD OVERRIDING");

        PriorityEmailService priority = new PriorityEmailService();

        NotificationRequest sample = new NotificationRequest(
            UUID.randomUUID().toString(),
            "admin@example.com",
            "Priority notification",
            Severity.HIGH
        );

        System.out.println(
            "Priority service: " + priority.describe()
        );

        System.out.println(
            "Priority cost: " + priority.calculateCost(sample)
        );
    }

    public static void main(String[] args) {
        try {
            demonstrateOverriding();
        } catch (Exception error) {
            System.err.println(
                "Application failure: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
