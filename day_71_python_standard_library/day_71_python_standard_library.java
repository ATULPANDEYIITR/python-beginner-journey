import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/*
 * Python Standard Library: Enterprise Java 17 Comparison
 *
 * Java implementation using only JDK facilities.
 *
 * Demonstrates:
 * records, enums, immutable domain objects, service layers,
 * validation, state transitions, streams, concurrency,
 * filesystem operations, cryptography and testing.
 */

public class StandardLibraryEnterprise {

    enum Status {
        PENDING,
        RUNNING,
        COMPLETED,
        FAILED
    }

    enum Priority {
        LOW(1),
        NORMAL(2),
        HIGH(3),
        CRITICAL(4);

        private final int weight;

        Priority(int weight) {
            this.weight = weight;
        }

        public int weight() {
            return weight;
        }
    }

    record Job(
        long id,
        String name,
        Priority priority,
        Status status,
        int attempts,
        Instant createdAt
    ) {
        Job {
            if (id <= 0) {
                throw new IllegalArgumentException(
                    "Job ID must be positive"
                );
            }

            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Job name is required"
                );
            }

            Objects.requireNonNull(priority);
            Objects.requireNonNull(status);
            Objects.requireNonNull(createdAt);

            if (attempts < 0) {
                throw new IllegalArgumentException(
                    "Attempts cannot be negative"
                );
            }
        }

        static Job create(
            long id,
            String name,
            Priority priority
        ) {
            return new Job(
                id,
                name,
                priority,
                Status.PENDING,
                0,
                Instant.now()
            );
        }

        Job transition(Status next) {
            boolean valid = switch (status) {
                case PENDING -> next == Status.RUNNING;
                case RUNNING ->
                    next == Status.COMPLETED ||
                    next == Status.FAILED;
                case FAILED -> next == Status.PENDING;
                case COMPLETED -> false;
            };

            if (!valid) {
                throw new IllegalStateException(
                    "Invalid transition: " +
                    status + " -> " + next
                );
            }

            return new Job(
                id,
                name,
                priority,
                next,
                attempts +
                    (next == Status.RUNNING ? 1 : 0),
                createdAt
            );
        }
    }

    record ExecutionResult(
        long jobId,
        boolean successful,
        String message,
        long durationMillis
    ) {}

    interface JobExecutor {
        ExecutionResult execute(Job job);
    }

    static class JobValidationException extends RuntimeException {
        JobValidationException(String message) {
            super(message);
        }
    }

    static class JobRepository {
        private final Map<Long, Job> jobs = new HashMap<>();

        public synchronized void insert(Job job) {
            Objects.requireNonNull(job);

            if (jobs.containsKey(job.id())) {
                throw new JobValidationException(
                    "Duplicate job identifier"
                );
            }

            jobs.put(job.id(), job);
        }

        public synchronized Optional<Job> find(long id) {
            return Optional.ofNullable(jobs.get(id));
        }

        public synchronized void update(Job job) {
            if (!jobs.containsKey(job.id())) {
                throw new JobValidationException(
                    "Cannot update unknown job"
                );
            }

            jobs.put(job.id(), job);
        }

        public synchronized List<Job> findAll() {
            return jobs.values()
                .stream()
                .sorted(
                    Comparator
                        .comparingInt(
                            (Job job) ->
                                job.priority().weight()
                        )
                        .reversed()
                        .thenComparingLong(Job::id)
                )
                .toList();
        }

        public synchronized Map<Status, Long> statistics() {
            return jobs.values()
                .stream()
                .collect(
                    Collectors.groupingBy(
                        Job::status,
                        () -> new EnumMap<>(Status.class),
                        Collectors.counting()
                    )
                );
        }
    }

    static class Policy {
        private final int maximumAttempts;
        private final Set<Priority> executablePriorities;

        Policy(
            int maximumAttempts,
            Set<Priority> executablePriorities
        ) {
            if (maximumAttempts < 1) {
                throw new IllegalArgumentException(
                    "Maximum attempts must be positive"
                );
            }

            this.maximumAttempts = maximumAttempts;
            this.executablePriorities =
                Set.copyOf(executablePriorities);
        }

        boolean permits(Job job) {
            return executablePriorities.contains(
                job.priority()
            ) && job.attempts() < maximumAttempts;
        }
    }

    static class JobService {
        private final JobRepository repository;
        private final Policy policy;

        JobService(
            JobRepository repository,
            Policy policy
        ) {
            this.repository = repository;
            this.policy = policy;
        }

        public Job submit(
            long id,
            String name,
            Priority priority
        ) {
            Job job = Job.create(id, name, priority);
            repository.insert(job);
            return job;
        }

        public Job transition(
            long id,
            Status next
        ) {
            Job job = repository.find(id)
                .orElseThrow(
                    () -> new JobValidationException(
                        "Unknown job: " + id
                    )
                );

            if (
                next == Status.RUNNING &&
                !policy.permits(job)
            ) {
                throw new JobValidationException(
                    "Execution policy rejected job"
                );
            }

            Job updated = job.transition(next);
            repository.update(updated);

            return updated;
        }
    }

    static class StandardJobExecutor implements JobExecutor {
        @Override
        public ExecutionResult execute(Job job) {
            long start = System.nanoTime();

            try {
                Thread.sleep(20);

                return new ExecutionResult(
                    job.id(),
                    true,
                    "Completed",
                    TimeUnit.NANOSECONDS.toMillis(
                        System.nanoTime() - start
                    )
                );

            } catch (InterruptedException exception) {
                Thread.currentThread().interrupt();

                return new ExecutionResult(
                    job.id(),
                    false,
                    "Interrupted",
                    TimeUnit.NANOSECONDS.toMillis(
                        System.nanoTime() - start
                    )
                );
            }
        }
    }

    static String sha256(String input) {
        try {
            MessageDigest digest =
                MessageDigest.getInstance("SHA-256");

            byte[] hash = digest.digest(
                input.getBytes(StandardCharsets.UTF_8)
            );

            StringBuilder output = new StringBuilder();

            for (byte value : hash) {
                output.append(
                    String.format("%02x", value & 0xff)
                );
            }

            return output.toString();

        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException(
                "SHA-256 unavailable",
                exception
            );
        }
    }

    static void exportCsv(
        List<Job> jobs,
        Path destination
    ) throws IOException {
        Path absolute = destination.toAbsolutePath();
        Path parent = absolute.getParent();

        if (parent != null) {
            Files.createDirectories(parent);
        }

        Path temporary = Files.createTempFile(
            parent,
            "jobs-",
            ".tmp"
        );

        boolean moved = false;

        try {
            try (BufferedWriter writer = Files.newBufferedWriter(
                temporary,
                StandardCharsets.UTF_8
            )) {
                writer.write(
                    "id,name,priority,status,attempts,created_at"
                );
                writer.newLine();

                for (Job job : jobs) {
                    writer.write(
                        job.id() + "," +
                        csv(job.name()) + "," +
                        job.priority() + "," +
                        job.status() + "," +
                        job.attempts() + "," +
                        job.createdAt()
                    );
                    writer.newLine();
                }
            }

            try {
                Files.move(
                    temporary,
                    absolute,
                    java.nio.file.StandardCopyOption.REPLACE_EXISTING,
                    java.nio.file.StandardCopyOption.ATOMIC_MOVE
                );
            } catch (java.nio.file.AtomicMoveNotSupportedException e) {
                Files.move(
                    temporary,
                    absolute,
                    java.nio.file.StandardCopyOption.REPLACE_EXISTING
                );
            }

            moved = true;

        } finally {
            if (!moved) {
                Files.deleteIfExists(temporary);
            }
        }
    }

    static String csv(String value) {
        return "\"" +
            value.replace("\"", "\"\"") +
            "\"";
    }

    static CompletableFuture<ExecutionResult> executeAsync(
        Job job,
        JobExecutor executor,
        ExecutorService pool
    ) {
        return CompletableFuture.supplyAsync(
            () -> executor.execute(job),
            pool
        );
    }

    static void runTests() {
        JobRepository repository = new JobRepository();

        Policy policy = new Policy(
            3,
            Set.of(
                Priority.NORMAL,
                Priority.HIGH,
                Priority.CRITICAL
            )
        );

        JobService service = new JobService(
            repository,
            policy
        );

        Job job = service.submit(
            1,
            "Automated test",
            Priority.HIGH
        );

        job = service.transition(1, Status.RUNNING);
        job = service.transition(1, Status.COMPLETED);

        if (job.status() != Status.COMPLETED) {
            throw new AssertionError("Transition test failed");
        }

        try {
            service.transition(1, Status.RUNNING);
            throw new AssertionError(
                "Invalid transition was accepted"
            );
        } catch (IllegalStateException expected) {
            // Expected invalid state transition.
        }

        if (sha256("abc").length() != 64) {
            throw new AssertionError("Digest test failed");
        }

        if (
            IntStream.rangeClosed(1, 5)
                .map(value -> value * value)
                .sum() != 55
        ) {
            throw new AssertionError("Stream test failed");
        }

        System.out.println("All Java tests passed.");
    }

    public static void main(String[] args) {
        JobRepository repository = new JobRepository();

        Policy policy = new Policy(
            3,
            Set.of(
                Priority.NORMAL,
                Priority.HIGH,
                Priority.CRITICAL
            )
        );

        JobService service = new JobService(
            repository,
            policy
        );

        ExecutorService executor =
            Executors.newFixedThreadPool(4);

        try {
            service.submit(
                1001,
                "Import transaction records",
                Priority.HIGH
            );

            service.submit(
                1002,
                "Validate access configuration",
                Priority.CRITICAL
            );

            service.submit(
                1003,
                "Generate analytics report",
                Priority.NORMAL
            );

            service.transition(1001, Status.RUNNING);
            service.transition(1001, Status.COMPLETED);

            service.transition(1002, Status.RUNNING);
            service.transition(1002, Status.FAILED);

            List<Job> jobs = repository.findAll();

            System.out.println("JOB REPORT");

            jobs.forEach(System.out::println);

            System.out.println("\nSTATUS STATISTICS");

            repository.statistics().forEach(
                (status, count) ->
                    System.out.println(status + ": " + count)
            );

            JobExecutor jobExecutor =
                new StandardJobExecutor();

            List<CompletableFuture<ExecutionResult>> futures =
                jobs.stream()
                    .filter(job -> job.status() == Status.PENDING)
                    .map(job ->
                        executeAsync(job, jobExecutor, executor)
                    )
                    .toList();

            CompletableFuture.allOf(
                futures.toArray(new CompletableFuture<?>[0])
            ).join();

            System.out.println("\nASYNC EXECUTION");

            futures.stream()
                .map(CompletableFuture::join)
                .forEach(System.out::println);

            System.out.println("\nSTREAM ANALYSIS");

            double average = IntStream.rangeClosed(1, 5)
                .mapToDouble(value -> value * 10.0)
                .average()
                .orElseThrow();

            System.out.println("Average: " + average);

            System.out.println("\nSHA-256");

            System.out.println(
                sha256("Python Standard Library")
            );

            exportCsv(
                repository.findAll(),
                Path.of("java_jobs.csv")
            );

            runTests();

        } catch (Exception exception) {
            System.err.println(
                "Execution failed: " + exception.getMessage()
            );

            exception.printStackTrace();
            System.exitCode = 1;

        } finally {
            executor.shutdown();

            try {
                if (
                    !executor.awaitTermination(
                        10,
                        TimeUnit.SECONDS
                    )
                ) {
                    executor.shutdownNow();
                }
            } catch (InterruptedException exception) {
                executor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }
}
