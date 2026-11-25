import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.function.Predicate;

/**
 * MULTIPLE INHERITANCE IN JAVA 17
 *
 * Java classes support single class inheritance.
 * Multiple inheritance of type and behavior is supported
 * through interfaces and default methods.
 *
 * Demonstrates:
 * - Interface-based multiple inheritance
 * - Default methods
 * - Diamond conflicts
 * - Explicit interface method resolution
 * - Abstract classes and interfaces
 * - Records
 * - Generics
 * - Policy-based capabilities
 * - Enterprise validation
 * - State transitions
 * - Asynchronous execution
 *
 * Compile: javac MultipleInheritanceDemo.java
 * Run:     java MultipleInheritanceDemo
 */

public class MultipleInheritanceDemo {

    // ========================================================
    // 1. BASIC INTERFACE-BASED MULTIPLE INHERITANCE
    // ========================================================

    interface Loggable {
        void log(String message);
    }

    interface Validatable<T> {
        boolean validate(T value);
    }

    interface Persistable<T> {
        void save(T value);
    }

    static class RepositoryService
            implements Loggable, Validatable<String>,
                       Persistable<String> {

        private final List<String> records = new ArrayList<>();

        @Override
        public void log(String message) {
            System.out.println("[LOG] " + message);
        }

        @Override
        public boolean validate(String value) {
            return value != null && !value.isBlank();
        }

        @Override
        public void save(String value) {
            if (!validate(value)) {
                throw new IllegalArgumentException(
                    "Invalid repository value"
                );
            }

            records.add(value);
            log("Saved: " + value);
        }

        public List<String> records() {
            return Collections.unmodifiableList(records);
        }
    }


    // ========================================================
    // 2. DIAMOND INHERITANCE THROUGH INTERFACES
    // ========================================================

    interface Device {
        default String describe() {
            return "Generic device";
        }
    }

    interface Camera extends Device {
        default String capture() {
            return "Image captured";
        }

        @Override
        default String describe() {
            return "Camera device";
        }
    }

    interface NetworkAdapter extends Device {
        default String connect() {
            return "Network connected";
        }

        @Override
        default String describe() {
            return "Network device";
        }
    }

    static class SmartCamera implements Camera, NetworkAdapter {

        // Both parent interfaces provide describe().
        // The implementing class must resolve the conflict.

        @Override
        public String describe() {
            return Camera.super.describe()
                    + " with "
                    + NetworkAdapter.super.describe();
        }

        public void operate() {
            System.out.println(describe());
            System.out.println(capture());
            System.out.println(connect());
        }
    }


    // ========================================================
    // 3. DEFAULT METHOD CONFLICT RESOLUTION
    // ========================================================

    interface CSVExporter {
        default String export() {
            return "CSV DATA";
        }
    }

    interface JSONExporter {
        default String export() {
            return "{\"format\":\"JSON\"}";
        }
    }

    static class DataExporter
            implements CSVExporter, JSONExporter {

        @Override
        public String export() {
            return CSVExporter.super.export();
        }

        public String exportJSON() {
            return JSONExporter.super.export();
        }
    }


    // ========================================================
    // 4. ABSTRACT CLASS PLUS MULTIPLE INTERFACES
    // ========================================================

    abstract static class EnterpriseComponent {

        private final String componentId;

        protected EnterpriseComponent(String componentId) {
            if (componentId == null || componentId.isBlank()) {
                throw new IllegalArgumentException(
                    "Component ID is required"
                );
            }

            this.componentId = componentId;
        }

        public String componentId() {
            return componentId;
        }

        public abstract void execute();
    }

    interface Auditable {
        void audit(String message);
    }

    interface Secure {
        boolean authorize(String username);
    }

    static class DeploymentComponent
            extends EnterpriseComponent
            implements Auditable, Secure {

        private final List<String> auditRecords = new ArrayList<>();

        DeploymentComponent(String id) {
            super(id);
        }

        @Override
        public void execute() {
            System.out.println(
                "Deployment executed: " + componentId()
            );
        }

        @Override
        public void audit(String message) {
            auditRecords.add(message);
        }

        @Override
        public boolean authorize(String username) {
            return username != null
                    && username.equals("release_admin");
        }

        public List<String> auditRecords() {
            return Collections.unmodifiableList(auditRecords);
        }
    }


    // ========================================================
    // 5. GENERIC CAPABILITY INTERFACES
    // ========================================================

    interface Readable<K, V> {
        V read(K key);
    }

    interface Writable<K, V> {
        void write(K key, V value);
    }

    interface Deletable<K> {
        boolean delete(K key);
    }

    static class MultiCapabilityRepository<K, V>
            implements Readable<K, V>,
                       Writable<K, V>,
                       Deletable<K> {

        private final Map<K, V> records = new HashMap<>();

        @Override
        public V read(K key) {
            if (!records.containsKey(key)) {
                throw new IllegalArgumentException(
                    "Record not found: " + key
                );
            }

            return records.get(key);
        }

        @Override
        public void write(K key, V value) {
            Objects.requireNonNull(key, "Key cannot be null");
            Objects.requireNonNull(value, "Value cannot be null");

            records.put(key, value);
        }

        @Override
        public boolean delete(K key) {
            return records.remove(key) != null;
        }

        public int size() {
            return records.size();
        }
    }


    // ========================================================
    // 6. RECORDS AND POLICY TYPES
    // ========================================================

    enum Permission {
        READ,
        WRITE,
        DELETE,
        DEPLOY
    }

    enum AccountStatus {
        ACTIVE,
        SUSPENDED,
        DISABLED
    }

    record User(String username, AccountStatus status,
                Set<Permission> permissions) {

        User {
            if (username == null || username.isBlank()) {
                throw new IllegalArgumentException(
                    "Username is required"
                );
            }

            Objects.requireNonNull(status);
            permissions = Set.copyOf(permissions);
        }
    }

    interface AuthorizationPolicy {
        boolean evaluate(User user, Permission permission);
    }

    static class DefaultAuthorizationPolicy
            implements AuthorizationPolicy {

        @Override
        public boolean evaluate(User user, Permission permission) {
            Objects.requireNonNull(user);
            Objects.requireNonNull(permission);

            return user.status() == AccountStatus.ACTIVE
                    && user.permissions().contains(permission);
        }
    }


    // ========================================================
    // 7. POLICY COMPOSITION
    // ========================================================

    static class PolicyEngine {

        private final List<Predicate<User>> userRules =
                new ArrayList<>();

        private final Map<Permission, AuthorizationPolicy> policies =
                new EnumMap<>(Permission.class);

        public void addUserRule(Predicate<User> rule) {
            userRules.add(Objects.requireNonNull(rule));
        }

        public void registerPolicy(
                Permission permission,
                AuthorizationPolicy policy) {

            if (policies.putIfAbsent(
                    permission,
                    Objects.requireNonNull(policy)
            ) != null) {
                throw new IllegalStateException(
                    "Policy already registered: " + permission
                );
            }
        }

        public boolean authorize(User user, Permission permission) {
            Objects.requireNonNull(user);
            Objects.requireNonNull(permission);

            for (Predicate<User> rule : userRules) {
                if (!rule.test(user)) {
                    return false;
                }
            }

            AuthorizationPolicy policy = policies.get(permission);

            if (policy == null) {
                return false;
            }

            return policy.evaluate(user, permission);
        }
    }


    // ========================================================
    // 8. ENTERPRISE WORKFLOW AND STATE MANAGEMENT
    // ========================================================

    enum WorkflowState {
        CREATED,
        VALIDATING,
        PROCESSING,
        COMPLETED,
        FAILED
    }

    record StateChange(
            WorkflowState previous,
            WorkflowState current,
            Instant changedAt
    ) {}

    interface StateAware {
        WorkflowState state();
    }

    interface AuditedWorkflow {
        List<StateChange> history();
    }

    static class EnterpriseWorkflow
            implements StateAware, AuditedWorkflow {

        private WorkflowState state = WorkflowState.CREATED;

        private final List<StateChange> history =
                new ArrayList<>();

        private static final Map<WorkflowState, Set<WorkflowState>>
                ALLOWED = Map.of(
                    WorkflowState.CREATED,
                    Set.of(
                        WorkflowState.VALIDATING,
                        WorkflowState.FAILED
                    ),
                    WorkflowState.VALIDATING,
                    Set.of(
                        WorkflowState.PROCESSING,
                        WorkflowState.FAILED
                    ),
                    WorkflowState.PROCESSING,
                    Set.of(
                        WorkflowState.COMPLETED,
                        WorkflowState.FAILED
                    ),
                    WorkflowState.COMPLETED,
                    Set.of(),
                    WorkflowState.FAILED,
                    Set.of()
                );

        public void transition(WorkflowState next) {
            if (!ALLOWED.get(state).contains(next)) {
                throw new IllegalStateException(
                    "Invalid transition: " + state + " -> " + next
                );
            }

            WorkflowState previous = state;
            state = next;

            history.add(new StateChange(
                previous,
                next,
                Instant.now()
            ));
        }

        @Override
        public WorkflowState state() {
            return state;
        }

        @Override
        public List<StateChange> history() {
            return List.copyOf(history);
        }

        public void execute() {
            try {
                transition(WorkflowState.VALIDATING);
                transition(WorkflowState.PROCESSING);
                transition(WorkflowState.COMPLETED);
            } catch (RuntimeException exception) {
                if (state == WorkflowState.VALIDATING
                        || state == WorkflowState.PROCESSING) {
                    transition(WorkflowState.FAILED);
                }

                throw exception;
            }
        }
    }


    // ========================================================
    // 9. ASYNCHRONOUS MULTIPLE CAPABILITY EXECUTION
    // ========================================================

    interface AsyncOperation<T> {
        CompletableFuture<T> execute();
    }

    static class AsyncService
            implements AsyncOperation<String> {

        @Override
        public CompletableFuture<String> execute() {
            return CompletableFuture.supplyAsync(
                () -> "Asynchronous operation completed"
            );
        }

        public CompletableFuture<String> executeWithValidation(
                Predicate<String> validator) {

            return execute().thenApply(result -> {
                if (!validator.test(result)) {
                    throw new CompletionException(
                        new IllegalStateException(
                            "Result validation failed"
                        )
                    );
                }

                return result;
            });
        }
    }


    // ========================================================
    // 10. AUTOMATED TESTS
    // ========================================================

    static void runTests() {
        RepositoryService repository = new RepositoryService();

        repository.save("Record A");

        if (repository.records().size() != 1) {
            throw new AssertionError("Repository save failed");
        }

        try {
            repository.save("");
            throw new AssertionError("Invalid value was accepted");
        } catch (IllegalArgumentException expected) {
            // Expected validation failure.
        }

        SmartCamera camera = new SmartCamera();

        if (!camera.describe().contains("Camera")) {
            throw new AssertionError("Diamond resolution failed");
        }

        DataExporter exporter = new DataExporter();

        if (!exporter.export().equals("CSV DATA")) {
            throw new AssertionError("CSV resolution failed");
        }

        if (!exporter.exportJSON().contains("JSON")) {
            throw new AssertionError("JSON resolution failed");
        }

        DeploymentComponent deployment =
                new DeploymentComponent("DEPLOY-101");

        deployment.audit("Release approved");

        if (!deployment.authorize("release_admin")) {
            throw new AssertionError("Authorization failed");
        }

        if (deployment.authorize("unknown")) {
            throw new AssertionError("Unauthorized user accepted");
        }

        MultiCapabilityRepository<Integer, String> storage =
                new MultiCapabilityRepository<>();

        storage.write(1, "Record");

        if (!storage.read(1).equals("Record")) {
            throw new AssertionError("Read failed");
        }

        if (!storage.delete(1)) {
            throw new AssertionError("Delete failed");
        }

        if (storage.size() != 0) {
            throw new AssertionError("Storage state incorrect");
        }

        User admin = new User(
            "release_admin",
            AccountStatus.ACTIVE,
            Set.of(Permission.READ, Permission.DEPLOY)
        );

        PolicyEngine engine = new PolicyEngine();

        engine.addUserRule(
            user -> user.username().startsWith("release_")
        );

        engine.registerPolicy(
            Permission.DEPLOY,
            new DefaultAuthorizationPolicy()
        );

        if (!engine.authorize(admin, Permission.DEPLOY)) {
            throw new AssertionError("Deployment policy failed");
        }

        EnterpriseWorkflow workflow = new EnterpriseWorkflow();
        workflow.execute();

        if (workflow.state() != WorkflowState.COMPLETED) {
            throw new AssertionError("Workflow failed");
        }

        if (workflow.history().size() != 3) {
            throw new AssertionError("Audit history incomplete");
        }

        try {
            workflow.transition(WorkflowState.FAILED);
            throw new AssertionError("Invalid transition accepted");
        } catch (IllegalStateException expected) {
            // Terminal states cannot transition.
        }

        String asyncResult = new AsyncService()
                .executeWithValidation(
                    result -> result.contains("completed")
                )
                .join();

        if (!asyncResult.contains("completed")) {
            throw new AssertionError("Async operation failed");
        }

        System.out.println("All Java 17 tests passed.");
    }


    // ========================================================
    // 11. MAIN
    // ========================================================

    public static void main(String[] args) {

        System.out.println("MULTIPLE INHERITANCE IN JAVA 17");

        System.out.println("\n1. Interface-based inheritance");

        RepositoryService repository = new RepositoryService();
        repository.save("Enterprise deployment record");

        System.out.println("\n2. Diamond inheritance");

        SmartCamera camera = new SmartCamera();
        camera.operate();

        System.out.println("\n3. Default method conflict resolution");

        DataExporter exporter = new DataExporter();

        System.out.println("CSV: " + exporter.export());
        System.out.println("JSON: " + exporter.exportJSON());

        System.out.println("\n4. Abstract class and interfaces");

        DeploymentComponent deployment =
                new DeploymentComponent("DEPLOY-202");

        deployment.execute();
        deployment.audit("Deployment reviewed");

        System.out.println(
            "Authorized: " + deployment.authorize("release_admin")
        );

        System.out.println("\n5. Generic multi-capability repository");

        MultiCapabilityRepository<Integer, String> storage =
                new MultiCapabilityRepository<>();

        storage.write(101, "Production configuration");

        System.out.println(storage.read(101));
        System.out.println("Deleted: " + storage.delete(101));

        System.out.println("\n6. Policy evaluation");

        User user = new User(
            "release_admin",
            AccountStatus.ACTIVE,
            Set.of(Permission.READ, Permission.DEPLOY)
        );

        PolicyEngine policyEngine = new PolicyEngine();

        policyEngine.addUserRule(
            account -> account.username().startsWith("release_")
        );

        policyEngine.registerPolicy(
            Permission.DEPLOY,
            new DefaultAuthorizationPolicy()
        );

        System.out.println(
            "Deploy permitted: "
                    + policyEngine.authorize(user, Permission.DEPLOY)
        );

        System.out.println("\n7. Enterprise workflow");

        EnterpriseWorkflow workflow = new EnterpriseWorkflow();
        workflow.execute();

        System.out.println("State: " + workflow.state());

        workflow.history().forEach(System.out::println);

        System.out.println("\n8. Asynchronous execution");

        String result = new AsyncService()
                .execute()
                .join();

        System.out.println(result);

        System.out.println("\n9. Automated validation");

        runTests();
    }
}
