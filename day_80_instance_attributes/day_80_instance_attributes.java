import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

public class InstanceAttributes {

    enum DeviceStatus {
        ACTIVE,
        INACTIVE,
        MAINTENANCE
    }

    static class ValidationException extends RuntimeException {
        public ValidationException(String message) {
            super(message);
        }
    }

    record DeviceConfiguration(String ipAddress, int ports) {

        DeviceConfiguration {
            Objects.requireNonNull(ipAddress);

            if (ipAddress.isBlank()) {
                throw new ValidationException(
                    "IP address cannot be empty."
                );
            }

            if (ports < 1 || ports > 65535) {
                throw new ValidationException(
                    "Invalid port count."
                );
            }
        }
    }

    static final class Device {

        // Class-level attribute: shared across instances.
        public static final String CATEGORY = "NETWORK_EQUIPMENT";

        // Immutable instance attributes.
        private final String id;
        private final Instant createdAt;

        // Mutable instance attributes.
        private String name;
        private String manufacturer;
        private double temperature;
        private DeviceStatus status;
        private DeviceConfiguration configuration;
        private final List<String> tags;

        // Instance-specific revision counter.
        private long revision;

        public Device(
            String id,
            String name,
            String manufacturer,
            double temperature,
            DeviceStatus status,
            DeviceConfiguration configuration,
            List<String> tags
        ) {
            validateText(id, "ID");
            validateText(name, "Name");
            validateText(manufacturer, "Manufacturer");
            validateTemperature(temperature);

            this.id = id.trim();
            this.name = name.trim();
            this.manufacturer = manufacturer.trim();
            this.temperature = temperature;
            this.status = Objects.requireNonNull(status);
            this.configuration = Objects.requireNonNull(configuration);

            this.tags = new ArrayList<>(
                Objects.requireNonNull(tags)
            );

            if (this.tags.stream().anyMatch(
                tag -> tag == null || tag.isBlank()
            )) {
                throw new ValidationException("Invalid tag.");
            }

            this.createdAt = Instant.now();
            this.revision = 0;
        }

        private static void validateText(
            String value,
            String field
        ) {
            if (value == null || value.isBlank()) {
                throw new ValidationException(
                    field + " cannot be empty."
                );
            }
        }

        private static void validateTemperature(double value) {
            if (!Double.isFinite(value) ||
                value < -50 || value > 150) {
                throw new ValidationException(
                    "Temperature outside valid range."
                );
            }
        }

        public String getId() {
            return id;
        }

        public String getName() {
            return name;
        }

        public double getTemperature() {
            return temperature;
        }

        public DeviceStatus getStatus() {
            return status;
        }

        public long getRevision() {
            return revision;
        }

        public Instant getCreatedAt() {
            return createdAt;
        }

        public List<String> getTags() {
            return List.copyOf(tags);
        }

        public DeviceConfiguration getConfiguration() {
            return configuration;
        }

        public boolean isOverheating() {
            return temperature >= 70;
        }

        public void updateTemperature(double value) {
            validateTemperature(value);
            temperature = value;
            revision++;
        }

        public void updateName(String value) {
            validateText(value, "Name");
            name = value.trim();
            revision++;
        }

        public void updateManufacturer(String value) {
            validateText(value, "Manufacturer");
            manufacturer = value.trim();
            revision++;
        }

        public void updateStatus(DeviceStatus value) {
            status = Objects.requireNonNull(value);
            revision++;
        }

        public void updateConfiguration(
            DeviceConfiguration value
        ) {
            configuration = Objects.requireNonNull(value);
            revision++;
        }

        public void addTag(String value) {
            validateText(value, "Tag");

            if (!tags.contains(value)) {
                tags.add(value);
                revision++;
            }
        }

        public DeviceSnapshot snapshot() {
            return new DeviceSnapshot(
                id,
                name,
                manufacturer,
                temperature,
                status,
                configuration,
                List.copyOf(tags),
                createdAt,
                revision
            );
        }

        public void display() {
            System.out.println("\nDevice ID: " + id);
            System.out.println("Name: " + name);
            System.out.println("Manufacturer: " + manufacturer);
            System.out.println("Temperature: " + temperature);
            System.out.println("Status: " + status);
            System.out.println("Configuration: " + configuration);
            System.out.println("Tags: " + tags);
            System.out.println("Category: " + CATEGORY);
            System.out.println("Revision: " + revision);
        }
    }

    record DeviceSnapshot(
        String id,
        String name,
        String manufacturer,
        double temperature,
        DeviceStatus status,
        DeviceConfiguration configuration,
        List<String> tags,
        Instant createdAt,
        long revision
    ) {}

    interface DevicePolicy {
        boolean canRegister(Device device);
        boolean canUpdate(Device device);
    }

    static final class EnterpriseDevicePolicy
        implements DevicePolicy {

        private final Set<String> approvedManufacturers;

        EnterpriseDevicePolicy(Set<String> manufacturers) {
            approvedManufacturers = Set.copyOf(manufacturers);
        }

        @Override
        public boolean canRegister(Device device) {
            return approvedManufacturers.contains(
                device.snapshot().manufacturer()
            );
        }

        @Override
        public boolean canUpdate(Device device) {
            return device.getRevision() >= 0;
        }
    }

    static final class DeviceRegistry {

        private final Map<String, Device> devices = new HashMap<>();
        private final DevicePolicy policy;

        DeviceRegistry(DevicePolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        public void register(Device device) {
            Objects.requireNonNull(device);

            if (devices.containsKey(device.getId())) {
                throw new ValidationException(
                    "Duplicate device ID."
                );
            }

            if (!policy.canRegister(device)) {
                throw new ValidationException(
                    "Manufacturer is not approved."
                );
            }

            devices.put(device.getId(), device);
        }

        public Device get(String id) {
            Device device = devices.get(id);

            if (device == null) {
                throw new ValidationException(
                    "Device not found: " + id
                );
            }

            return device;
        }

        public void updateTemperature(
            String id,
            double temperature
        ) {
            Device device = get(id);

            if (!policy.canUpdate(device)) {
                throw new ValidationException(
                    "Update rejected by enterprise policy."
                );
            }

            device.updateTemperature(temperature);
        }

        public List<DeviceSnapshot> overheatingDevices() {
            return devices.values()
                .stream()
                .filter(Device::isOverheating)
                .map(Device::snapshot)
                .toList();
        }

        public Map<DeviceStatus, Long> statusReport() {
            EnumMap<DeviceStatus, Long> report =
                new EnumMap<>(DeviceStatus.class);

            for (DeviceStatus status : DeviceStatus.values()) {
                report.put(status, 0L);
            }

            Map<DeviceStatus, Long> counts = devices.values()
                .stream()
                .collect(Collectors.groupingBy(
                    Device::getStatus,
                    Collectors.counting()
                ));

            report.putAll(counts);
            return report;
        }

        public List<DeviceSnapshot> snapshots() {
            return devices.values()
                .stream()
                .map(Device::snapshot)
                .toList();
        }

        public int size() {
            return devices.size();
        }

        public void saveReport(Path destination)
            throws IOException {

            StringBuilder csv = new StringBuilder();

            csv.append(
                "id,name,manufacturer,temperature,status,revision\n"
            );

            for (Device device : devices.values()) {
                DeviceSnapshot item = device.snapshot();

                // Escape fields to prevent malformed CSV records.
                csv.append(csvEscape(item.id())).append(",");
                csv.append(csvEscape(item.name())).append(",");
                csv.append(csvEscape(item.manufacturer())).append(",");
                csv.append(item.temperature()).append(",");
                csv.append(item.status()).append(",");
                csv.append(item.revision()).append("\n");
            }

            Files.writeString(
                destination,
                csv.toString(),
                StandardCharsets.UTF_8
            );
        }

        private static String csvEscape(String value) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }
    }

    public static void main(String[] args) {

        try {
            System.out.println(
                "INSTANCE ATTRIBUTES: JAVA 17"
            );

            Device router = new Device(
                "DEV-001",
                "Core Router",
                "Cisco",
                42.5,
                DeviceStatus.ACTIVE,
                new DeviceConfiguration("192.168.1.1", 24),
                List.of("network", "critical")
            );

            Device firewall = new Device(
                "DEV-002",
                "Enterprise Firewall",
                "Fortinet",
                78.0,
                DeviceStatus.ACTIVE,
                new DeviceConfiguration("192.168.1.2", 8),
                List.of("security", "critical")
            );

            System.out.println("\n1. Instance-specific attributes");

            router.display();
            firewall.display();

            System.out.println("\n2. Independent updates");

            router.updateTemperature(35);

            System.out.println(
                "Router: " + router.getTemperature()
            );

            System.out.println(
                "Firewall: " + firewall.getTemperature()
            );

            System.out.println("\n3. Shared class attribute");

            System.out.println(Device.CATEGORY);
            System.out.println(router.CATEGORY);
            System.out.println(firewall.CATEGORY);

            System.out.println("\n4. Immutable instance identity");

            System.out.println("Router ID: " + router.getId());
            System.out.println("Created at: " + router.getCreatedAt());

            System.out.println("\n5. Instance-level nested attributes");

            router.updateConfiguration(
                new DeviceConfiguration("10.0.0.1", 48)
            );

            router.addTag("production");

            System.out.println(
                "Router configuration: " +
                router.getConfiguration()
            );

            System.out.println(
                "Firewall configuration: " +
                firewall.getConfiguration()
            );

            System.out.println("\n6. Enterprise policy");

            DevicePolicy policy = new EnterpriseDevicePolicy(
                Set.of("Cisco", "Fortinet", "Juniper")
            );

            DeviceRegistry registry = new DeviceRegistry(policy);

            registry.register(router);
            registry.register(firewall);

            System.out.println(
                "Registered devices: " + registry.size()
            );

            System.out.println("\n7. Policy-controlled update");

            registry.updateTemperature("DEV-001", 38);

            System.out.println(
                "Updated revision: " + router.getRevision()
            );

            System.out.println("\n8. Monitoring");

            registry.overheatingDevices().forEach(
                device -> System.out.println(
                    device.name() + ": " + device.temperature()
                )
            );

            System.out.println("\n9. Status report");

            registry.statusReport().forEach(
                (status, count) ->
                    System.out.println(status + ": " + count)
            );

            System.out.println("\n10. Immutable snapshots");

            List<DeviceSnapshot> snapshots = registry.snapshots();

            System.out.println(snapshots);

            System.out.println("\n11. Validation failure");

            try {
                registry.updateTemperature("DEV-001", 250);
            } catch (ValidationException exception) {
                System.out.println(
                    "Rejected: " + exception.getMessage()
                );
            }

            System.out.println(
                "Preserved temperature: " +
                router.getTemperature()
            );

            System.out.println("\n12. Duplicate registration");

            try {
                registry.register(router);
            } catch (ValidationException exception) {
                System.out.println(
                    "Rejected: " + exception.getMessage()
                );
            }

            System.out.println("\n13. Unapproved manufacturer");

            try {
                Device unapproved = new Device(
                    "DEV-003",
                    "Unknown Device",
                    "UnknownVendor",
                    30,
                    DeviceStatus.ACTIVE,
                    new DeviceConfiguration("10.0.0.3", 4),
                    List.of("test")
                );

                registry.register(unapproved);

            } catch (ValidationException exception) {
                System.out.println(
                    "Rejected: " + exception.getMessage()
                );
            }

            System.out.println("\n14. Report persistence");

            Path report = Path.of("device_instances_java.csv");

            registry.saveReport(report);

            System.out.println(
                "Saved: " + report.toAbsolutePath()
            );

            System.out.println("\nAll demonstrations completed.");

        } catch (IOException | RuntimeException exception) {
            System.err.println(
                "Application failure: " + exception.getMessage()
            );

            System.exitCode = 1;
        }
    }
}
