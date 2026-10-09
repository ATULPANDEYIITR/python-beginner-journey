import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Deque;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

public class DataStructuresEnterpriseDemo {

    enum WorkStatus {
        PENDING,
        IN_PROGRESS,
        COMPLETED
    }

    enum Department {
        DATA_OPERATIONS,
        WAREHOUSE,
        ANALYTICS,
        PROCUREMENT
    }

    record WorkRequest(
        String id,
        String title,
        Department department,
        int priority,
        double estimatedHours,
        Set<String> labels,
        List<String> dependencies
    ) {
        WorkRequest {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Work ID is required.");
            }
            if (title == null || title.isBlank()) {
                throw new IllegalArgumentException("Title is required.");
            }
            Objects.requireNonNull(department, "Department is required.");

            if (priority < 1 || priority > 5) {
                throw new IllegalArgumentException("Priority must be 1 through 5.");
            }

            if (!Double.isFinite(estimatedHours) || estimatedHours < 0) {
                throw new IllegalArgumentException(
                    "Estimated hours must be finite and non-negative."
                );
            }

            Objects.requireNonNull(labels, "Labels are required.");
            Objects.requireNonNull(dependencies, "Dependencies are required.");

            labels = Collections.unmodifiableSet(new LinkedHashSet<>(labels));
            dependencies = List.copyOf(dependencies);

            if (new HashSet<>(dependencies).size() != dependencies.size()) {
                throw new IllegalArgumentException("Duplicate dependencies.");
            }
        }
    }

    static final class WorkItem {
        private final WorkRequest request;
        private WorkStatus status = WorkStatus.PENDING;

        WorkItem(WorkRequest request) {
            this.request = request;
        }

        WorkRequest request() {
            return request;
        }

        WorkStatus status() {
            return status;
        }

        void transition(WorkStatus next) {
            boolean valid =
                status == WorkStatus.PENDING && next == WorkStatus.IN_PROGRESS
                || status == WorkStatus.IN_PROGRESS && next == WorkStatus.COMPLETED;

            if (!valid) {
                throw new IllegalStateException(
                    "Invalid state transition: " + status + " -> " + next
                );
            }

            status = next;
        }
    }

    static final class PlanningService {
        private final Map<String, WorkItem> items = new LinkedHashMap<>();
        private final Map<Department, Set<String>> byDepartment =
            new EnumMap<>(Department.class);
        private final Set<String> completedIds = new HashSet<>();
        private final Deque<String> recentActivity = new ArrayDeque<>();
        private final PriorityQueue<WorkRequest> schedulingQueue =
            new PriorityQueue<>(
                Comparator.comparingInt(WorkRequest::priority)
                    .thenComparing(WorkRequest::id)
            );

        void register(WorkRequest request) {
            if (items.containsKey(request.id())) {
                throw new IllegalArgumentException("Duplicate ID: " + request.id());
            }

            for (String dependency : request.dependencies()) {
                if (!items.containsKey(dependency)) {
                    throw new IllegalArgumentException(
                        "Dependency must be registered first: " + dependency
                    );
                }
            }

            items.put(request.id(), new WorkItem(request));
            byDepartment.computeIfAbsent(
                request.department(),
                ignored -> new LinkedHashSet<>()
            ).add(request.id());

            schedulingQueue.add(request);
            record("Registered " + request.id());
        }

        List<WorkRequest> readyWork() {
            return items.values().stream()
                .filter(item -> item.status() == WorkStatus.PENDING)
                .filter(item -> completedIds.containsAll(
                    item.request().dependencies()
                ))
                .map(WorkItem::request)
                .sorted(
                    Comparator.comparingInt(WorkRequest::priority)
                        .thenComparing(WorkRequest::id)
                )
                .toList();
        }

        void start(String id) {
            WorkItem item = requireItem(id);

            if (!completedIds.containsAll(item.request().dependencies())) {
                throw new IllegalStateException(
                    "Cannot start work with unfinished prerequisites: " + id
                );
            }

            item.transition(WorkStatus.IN_PROGRESS);
            record("Started " + id);
        }

        void complete(String id) {
            WorkItem item = requireItem(id);
            item.transition(WorkStatus.COMPLETED);
            completedIds.add(id);
            record("Completed " + id);
        }

        List<WorkRequest> searchAllLabels(Set<String> requiredLabels) {
            return items.values().stream()
                .map(WorkItem::request)
                .filter(request -> request.labels().containsAll(requiredLabels))
                .toList();
        }

        Map<Department, Double> effortByDepartment() {
            Map<Department, Double> totals = new EnumMap<>(Department.class);

            for (WorkItem item : items.values()) {
                WorkRequest request = item.request();

                totals.merge(
                    request.department(),
                    request.estimatedHours(),
                    Double::sum
                );
            }

            return totals;
        }

        Set<String> commonDepartmentItems(
            Department first,
            Department second
        ) {
            Set<String> intersection = new TreeSet<>(
                byDepartment.getOrDefault(first, Set.of())
            );

            intersection.retainAll(
                byDepartment.getOrDefault(second, Set.of())
            );

            return intersection;
        }

        List<WorkRequest> scheduledReadyWork() {
            // A priority queue is useful for dispatching, while the authoritative
            // status and dependency maps remain the source of truth.
            List<WorkRequest> ready = readyWork();
            Set<String> readyIds = new HashSet<>();

            for (WorkRequest request : ready) {
                readyIds.add(request.id());
            }

            List<WorkRequest> result = new ArrayList<>();

            for (WorkRequest candidate : schedulingQueue) {
                if (readyIds.contains(candidate.id())) {
                    result.add(candidate);
                }
            }

            result.sort(
                Comparator.comparingInt(WorkRequest::priority)
                    .thenComparing(WorkRequest::id)
            );

            return result;
        }

        Map<String, WorkStatus> statusSnapshot() {
            Map<String, WorkStatus> result = new LinkedHashMap<>();

            items.forEach((id, item) -> result.put(id, item.status()));

            return Collections.unmodifiableMap(result);
        }

        List<String> recentActivity() {
            return List.copyOf(recentActivity);
        }

        private WorkItem requireItem(String id) {
            WorkItem item = items.get(id);

            if (item == null) {
                throw new IllegalArgumentException("Unknown work ID: " + id);
            }

            return item;
        }

        private void record(String event) {
            if (recentActivity.size() == 10) {
                recentActivity.removeFirst();
            }

            recentActivity.addLast(event);
        }
    }

    public static void main(String[] args) {
        PlanningService service = new PlanningService();

        service.register(new WorkRequest(
            "SUP-301",
            "Validate supplier delivery records",
            Department.DATA_OPERATIONS,
            1,
            2.5,
            Set.of("validation", "quality"),
            List.of()
        ));

        service.register(new WorkRequest(
            "SUP-302",
            "Reconcile warehouse stock",
            Department.WAREHOUSE,
            2,
            4.0,
            Set.of("reconciliation", "quality"),
            List.of("SUP-301")
        ));

        service.register(new WorkRequest(
            "SUP-303",
            "Publish procurement analytics",
            Department.ANALYTICS,
            1,
            3.5,
            Set.of("reporting", "quality"),
            List.of("SUP-302")
        ));

        service.register(new WorkRequest(
            "SUP-304",
            "Archive validation evidence",
            Department.DATA_OPERATIONS,
            3,
            1.0,
            Set.of("validation", "audit"),
            List.of("SUP-301")
        ));

        System.out.println("Initially ready work:");

        service.readyWork().forEach(request ->
            System.out.println(request.id() + ": " + request.title())
        );

        try {
            service.start("SUP-302");
        } catch (IllegalStateException error) {
            System.out.println("Dependency enforcement: " + error.getMessage());
        }

        service.start("SUP-301");
        service.complete("SUP-301");

        System.out.println("\nReady after supplier validation:");

        service.scheduledReadyWork().forEach(request ->
            System.out.println(request.id() + ": " + request.title())
        );

        System.out.println("\nRecords with the quality label:");

        service.searchAllLabels(Set.of("quality")).forEach(request ->
            System.out.println(request.id())
        );

        System.out.println("\nEffort by department:");
        new TreeMap<>(service.effortByDepartment()).forEach((department, hours) ->
            System.out.printf("%s: %.1f hours%n", department, hours)
        );

        System.out.println("\nCommon department membership:");
        System.out.println(service.commonDepartmentItems(
            Department.DATA_OPERATIONS,
            Department.WAREHOUSE
        ));

        System.out.println("\nStatus snapshot:");
        System.out.println(service.statusSnapshot());

        System.out.println("\nRecent activity:");
        service.recentActivity().forEach(System.out::println);

        try {
            service.complete("SUP-303");
        } catch (IllegalStateException error) {
            System.out.println("\nInvalid completion rejected: " + error.getMessage());
        }
    }
}
