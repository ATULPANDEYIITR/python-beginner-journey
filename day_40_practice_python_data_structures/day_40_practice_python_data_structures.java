import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;

/*
 * Enterprise case study: employee training and competency records.
 *
 * The domain uses immutable records, enums for controlled states, nested
 * maps for employee-to-course indexes, sets for completed-course uniqueness,
 * and explicit validation for record transitions.
 *
 * Compile: javac PracticeDataStructures.java
 * Run:     java PracticeDataStructures
 */

public class PracticeDataStructures {

    enum CourseStatus {
        NOT_STARTED,
        IN_PROGRESS,
        COMPLETED,
        BLOCKED
    }

    record Employee(String employeeId, String name, String department) {
        Employee {
            employeeId = requireText(employeeId, "employeeId");
            name = requireText(name, "name");
            department = requireText(department, "department");
        }
    }

    record Course(String courseId, String title, int requiredHours) {
        Course {
            courseId = requireText(courseId, "courseId");
            title = requireText(title, "title");
            if (requiredHours < 1 || requiredHours > 500) {
                throw new IllegalArgumentException(
                    "requiredHours must be between 1 and 500"
                );
            }
        }
    }

    record Enrollment(
        String employeeId,
        String courseId,
        CourseStatus status,
        int hoursCompleted,
        int score
    ) {
        Enrollment {
            employeeId = requireText(employeeId, "employeeId");
            courseId = requireText(courseId, "courseId");
            Objects.requireNonNull(status, "status");

            if (hoursCompleted < 0) {
                throw new IllegalArgumentException(
                    "hoursCompleted cannot be negative"
                );
            }
            if (score < 0 || score > 100) {
                throw new IllegalArgumentException("score must be from 0 to 100");
            }
            if (status == CourseStatus.COMPLETED && score < 60) {
                throw new IllegalArgumentException(
                    "A completed course requires a passing score"
                );
            }
        }
    }

    static String requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(field + " cannot be blank");
        }
        return value.strip();
    }

    static final class TrainingRegistry {
        private final Map<String, Employee> employees = new HashMap<>();
        private final Map<String, Course> courses = new HashMap<>();

        // The outer map supports employee lookups; the inner map enforces one
        // current enrollment per employee and course combination.
        private final Map<String, Map<String, Enrollment>> enrollments =
            new HashMap<>();

        // EnumMap provides an efficient, type-safe breakdown of course states.
        private final EnumMap<CourseStatus, Integer> statusCounts =
            new EnumMap<>(CourseStatus.class);

        void addEmployee(Employee employee) {
            Objects.requireNonNull(employee, "employee");
            if (employees.putIfAbsent(employee.employeeId(), employee) != null) {
                throw new IllegalArgumentException(
                    "Duplicate employee: " + employee.employeeId()
                );
            }
        }

        void addCourse(Course course) {
            Objects.requireNonNull(course, "course");
            if (courses.putIfAbsent(course.courseId(), course) != null) {
                throw new IllegalArgumentException(
                    "Duplicate course: " + course.courseId()
                );
            }
        }

        void enroll(Enrollment enrollment) {
            Objects.requireNonNull(enrollment, "enrollment");

            if (!employees.containsKey(enrollment.employeeId())) {
                throw new IllegalArgumentException("Unknown employee");
            }
            Course course = courses.get(enrollment.courseId());
            if (course == null) {
                throw new IllegalArgumentException("Unknown course");
            }
            if (enrollment.hoursCompleted() > course.requiredHours()) {
                throw new IllegalArgumentException(
                    "Completed hours exceed course requirements"
                );
            }
            if (enrollment.status() == CourseStatus.COMPLETED
                && enrollment.hoursCompleted() < course.requiredHours()) {
                throw new IllegalArgumentException(
                    "Completed enrollment requires all course hours"
                );
            }

            Map<String, Enrollment> employeeEnrollments =
                enrollments.computeIfAbsent(
                    enrollment.employeeId(), ignored -> new HashMap<>()
                );

            Enrollment previous = employeeEnrollments.get(enrollment.courseId());
            if (previous != null) {
                statusCounts.compute(
                    previous.status(),
                    (status, count) -> count == null || count <= 1
                        ? null : count - 1
                );
            }

            employeeEnrollments.put(enrollment.courseId(), enrollment);
            statusCounts.merge(enrollment.status(), 1, Integer::sum);
        }

        Enrollment getEnrollment(String employeeId, String courseId) {
            Map<String, Enrollment> employeeEnrollments =
                enrollments.get(employeeId);

            if (employeeEnrollments == null
                || !employeeEnrollments.containsKey(courseId)) {
                throw new IllegalArgumentException("Enrollment not found");
            }
            return employeeEnrollments.get(courseId);
        }

        List<Enrollment> completedCourses(String employeeId) {
            if (!employees.containsKey(employeeId)) {
                throw new IllegalArgumentException("Unknown employee");
            }

            return enrollments.getOrDefault(employeeId, Collections.emptyMap())
                .values()
                .stream()
                .filter(e -> e.status() == CourseStatus.COMPLETED)
                .sorted((a, b) -> a.courseId().compareTo(b.courseId()))
                .collect(Collectors.toCollection(ArrayList::new));
        }

        Map<CourseStatus, Integer> statusReport() {
            return new EnumMap<>(statusCounts);
        }

        List<String> employeesMissingMandatoryCourse(String courseId) {
            if (!courses.containsKey(courseId)) {
                throw new IllegalArgumentException("Unknown course");
            }

            Set<String> completedEmployees = new HashSet<>();

            for (Map.Entry<String, Map<String, Enrollment>> entry
                : enrollments.entrySet()) {
                Enrollment enrollment = entry.getValue().get(courseId);
                if (enrollment != null
                    && enrollment.status() == CourseStatus.COMPLETED) {
                    completedEmployees.add(entry.getKey());
                }
            }

            return employees.keySet().stream()
                .filter(id -> !completedEmployees.contains(id))
                .sorted()
                .collect(Collectors.toList());
        }

        Map<String, Long> completedCourseCountsByDepartment() {
            Map<String, Long> counts = employees.values().stream()
                .collect(Collectors.groupingBy(
                    Employee::department,
                    TreeMap::new,
                    Collectors.counting()
                ));

            // Replace employee totals with actual completed-enrollment totals.
            Map<String, Long> completed = new TreeMap<>();
            for (Map<String, Enrollment> employeeEnrollments
                : enrollments.values()) {
                for (Enrollment enrollment : employeeEnrollments.values()) {
                    if (enrollment.status() == CourseStatus.COMPLETED) {
                        String department = employees.get(
                            enrollment.employeeId()
                        ).department();
                        completed.merge(department, 1L, Long::sum);
                    }
                }
            }

            // Departments without completed enrollments remain visible.
            counts.keySet().forEach(department ->
                completed.putIfAbsent(department, 0L)
            );
            return completed;
        }
    }

    public static void main(String[] args) {
        TrainingRegistry registry = new TrainingRegistry();

        registry.addEmployee(new Employee("E-101", "Asha Verma", "Operations"));
        registry.addEmployee(new Employee("E-102", "Ravi Kumar", "Finance"));
        registry.addEmployee(new Employee("E-103", "Mira Shah", "Operations"));

        registry.addCourse(new Course("SEC-01", "Security Fundamentals", 8));
        registry.addCourse(new Course("DATA-02", "Data Quality", 12));
        registry.addCourse(new Course("PROC-03", "Process Improvement", 10));

        registry.enroll(new Enrollment(
            "E-101", "SEC-01", CourseStatus.COMPLETED, 8, 92
        ));
        registry.enroll(new Enrollment(
            "E-101", "DATA-02", CourseStatus.IN_PROGRESS, 6, 70
        ));
        registry.enroll(new Enrollment(
            "E-102", "SEC-01", CourseStatus.COMPLETED, 8, 81
        ));
        registry.enroll(new Enrollment(
            "E-103", "SEC-01", CourseStatus.BLOCKED, 2, 0
        ));
        registry.enroll(new Enrollment(
            "E-103", "PROC-03", CourseStatus.NOT_STARTED, 0, 0
        ));

        // Updating an enrollment replaces its prior state rather than creating
        // a duplicate employee-course row.
        registry.enroll(new Enrollment(
            "E-101", "DATA-02", CourseStatus.COMPLETED, 12, 88
        ));

        System.out.println("Asha's completed courses:");
        for (Enrollment enrollment : registry.completedCourses("E-101")) {
            System.out.println("  " + enrollment.courseId()
                + ", score " + enrollment.score());
        }

        System.out.println("\nEnrollment state counts:");
        registry.statusReport().forEach((status, count) ->
            System.out.println("  " + status + ": " + count)
        );

        System.out.println("\nEmployees missing SEC-01:");
        System.out.println(
            registry.employeesMissingMandatoryCourse("SEC-01")
        );

        System.out.println("\nCompleted courses by department:");
        registry.completedCourseCountsByDepartment().forEach(
            (department, count) ->
                System.out.println("  " + department + ": " + count)
        );

        try {
            registry.enroll(new Enrollment(
                "E-103", "SEC-01", CourseStatus.COMPLETED, 8, 45
            ));
        } catch (IllegalArgumentException error) {
            System.out.println("\nRejected invalid completion: "
                + error.getMessage());
        }

        try {
            registry.enroll(new Enrollment(
                "E-999", "SEC-01", CourseStatus.IN_PROGRESS, 2, 0
            ));
        } catch (IllegalArgumentException error) {
            System.out.println("Rejected unknown employee: "
                + error.getMessage());
        }

        System.out.println("\nAll training registry checks completed.");
    }
}
