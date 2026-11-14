import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * Enterprise Project Dependency Management.
 *
 * Java 17.
 * No external dependencies.
 */
public class DependencyManagement {

    enum PRState {
        DRAFT, OPEN, MERGED, CLOSED
    }

    enum ReviewState {
        APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED
    }

    enum CheckState {
        PENDING, PASSED, FAILED
    }

    enum MergeStrategy {
        MERGE_COMMIT, SQUASH, REBASE
    }

    static class DependencyException extends RuntimeException {
        DependencyException(String message) {
            super(message);
        }
    }

    static class ValidationException extends DependencyException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class GovernanceException extends DependencyException {
        GovernanceException(String message) {
            super(message);
        }
    }

    record Version(int major, int minor, int patch)
            implements Comparable<Version> {

        Version {
            if (major < 0 || minor < 0 || patch < 0) {
                throw new ValidationException("Negative version component");
            }
        }

        static Version parse(String value) {
            if (value == null ||
                    !Pattern.matches(
                            "(0|[1-9][0-9]*)\\." +
                            "(0|[1-9][0-9]*)\\." +
                            "(0|[1-9][0-9]*)",
                            value)) {
                throw new ValidationException(
                        "Invalid semantic version: " + value
                );
            }

            String[] parts = value.split("\\.");
            try {
                return new Version(
                        Integer.parseInt(parts[0]),
                        Integer.parseInt(parts[1]),
                        Integer.parseInt(parts[2])
                );
            } catch (NumberFormatException exception) {
                throw new ValidationException("Version component overflow");
            }
        }

        @Override
        public int compareTo(Version other) {
            int result = Integer.compare(major, other.major);
            if (result != 0) return result;

            result = Integer.compare(minor, other.minor);
            if (result != 0) return result;

            return Integer.compare(patch, other.patch);
        }

        @Override
        public String toString() {
            return major + "." + minor + "." + patch;
        }
    }

    record Dependency(
            String name,
            Version current,
            Version minimum,
            Version maximum,
            boolean direct,
            String license,
            int vulnerabilities,
            List<String> prerequisites,
            String source
    ) {
        Dependency {
            Objects.requireNonNull(name);
            Objects.requireNonNull(current);
            Objects.requireNonNull(minimum);
            Objects.requireNonNull(license);
            Objects.requireNonNull(source);

            if (!name.matches("[A-Za-z0-9_.-]{1,100}")) {
                throw new ValidationException("Invalid package name");
            }

            if (current.compareTo(minimum) < 0) {
                throw new ValidationException(
                        name + " is below minimum version"
                );
            }

            if (maximum != null &&
                    current.compareTo(maximum) > 0) {
                throw new ValidationException(
                        name + " exceeds maximum version"
                );
            }

            if (vulnerabilities < 0) {
                throw new ValidationException(
                        "Negative vulnerability count"
                );
            }

            prerequisites = List.copyOf(
                    Objects.requireNonNull(prerequisites)
            );
        }

        Dependency withVersion(Version version) {
            return new Dependency(
                    name, version, minimum, maximum,
                    direct, license, vulnerabilities,
                    prerequisites, source
            );
        }
    }

    record Review(
            String reviewer,
            ReviewState state,
            String commitHash,
            Instant submittedAt
    ) {}

    record ReviewPolicy(
            int requiredApprovals,
            boolean dismissStaleApprovals,
            boolean requireResolvedConversations
    ) {
        ReviewPolicy {
            if (requiredApprovals < 0) {
                throw new ValidationException(
                        "Approval count cannot be negative"
                );
            }
        }
    }

    record ProtectionPolicy(
            Set<String> allowedLicenses,
            int maximumVulnerabilities,
            boolean requirePassingChecks,
            boolean requireLockfile,
            boolean rejectDirectPush,
            boolean rejectForcePush,
            boolean rejectBranchDeletion,
            boolean requireLinearHistory,
            boolean administratorBypass
    ) {
        ProtectionPolicy {
            allowedLicenses = Set.copyOf(allowedLicenses);

            if (maximumVulnerabilities < 0) {
                throw new ValidationException(
                        "Invalid vulnerability threshold"
                );
            }
        }

        static ProtectionPolicy standard() {
            return new ProtectionPolicy(
                    Set.of("MIT", "Apache-2.0", "BSD-3-Clause"),
                    0,
                    true,
                    true,
                    true,
                    true,
                    true,
                    true,
                    false
            );
        }
    }

    static class PullRequest {
        private final int id;
        private final String sourceBranch;
        private final String targetBranch;

        private final Map<String, Version> changes;
        private final Map<String, Review> reviews = new LinkedHashMap<>();
        private final Map<String, CheckState> checks = new LinkedHashMap<>();
        private final Map<String, Boolean> conversations = new LinkedHashMap<>();

        private PRState state;
        private boolean draft;
        private boolean synchronizedWithBase = true;
        private boolean mergeConflicts;
        private String headCommit;

        PullRequest(
                int id,
                String sourceBranch,
                String targetBranch,
                Map<String, Version> changes,
                boolean draft
        ) {
            this.id = id;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.changes = new LinkedHashMap<>(changes);
            this.draft = draft;
            this.state = draft ? PRState.DRAFT : PRState.OPEN;
            this.headCommit = calculateCommit();
        }

        private String calculateCommit() {
            return digest(
                    id + ":" + sourceBranch + ":" + targetBranch +
                    ":" + new TreeMap<>(changes)
            );
        }

        void addCheck(String name, CheckState state) {
            if (this.state != PRState.OPEN || draft) {
                throw new GovernanceException("PR is not ready for checks");
            }
            checks.put(name, state);
        }

        void addConversation(String id, boolean resolved) {
            conversations.put(id, resolved);
        }

        void submitReview(String reviewer, ReviewState state) {
            if (this.state != PRState.OPEN || draft) {
                throw new GovernanceException("PR is not reviewable");
            }

            if (reviewer == null || reviewer.isBlank()) {
                throw new ValidationException("Reviewer is required");
            }

            reviews.put(
                    reviewer,
                    new Review(
                            reviewer,
                            state,
                            headCommit,
                            Instant.now()
                    )
            );
        }

        void pushCommit(Map<String, Version> updatedChanges,
                        ReviewPolicy policy) {
            if (state != PRState.OPEN) {
                throw new GovernanceException("PR is not open");
            }

            for (var entry : updatedChanges.entrySet()) {
                if (!changes.containsKey(entry.getKey())) {
                    throw new ValidationException(
                            "Unexpected dependency change"
                    );
                }
                changes.put(entry.getKey(), entry.getValue());
            }

            headCommit = calculateCommit();

            if (policy.dismissStaleApprovals()) {
                reviews.replaceAll((reviewer, review) ->
                        review.state() == ReviewState.APPROVED
                                ? new Review(
                                        reviewer,
                                        ReviewState.DISMISSED,
                                        review.commitHash(),
                                        review.submittedAt()
                                )
                                : review
                );
            }

            checks.replaceAll((name, state) -> CheckState.PENDING);
        }

        Map<String, Version> changes() {
            return Collections.unmodifiableMap(changes);
        }
    }

    interface DependencyScanner {
        List<String> scan(Map<String, Dependency> dependencies);
    }

    static class GovernanceScanner implements DependencyScanner {

        private final ProtectionPolicy policy;

        GovernanceScanner(ProtectionPolicy policy) {
            this.policy = policy;
        }

        @Override
        public List<String> scan(
                Map<String, Dependency> dependencies
        ) {
            List<String> violations = new ArrayList<>();

            dependencies.values().forEach(dependency -> {
                if (!policy.allowedLicenses().contains(
                        dependency.license())) {
                    violations.add(
                            dependency.name() + ": prohibited license"
                    );
                }

                if (dependency.vulnerabilities() >
                        policy.maximumVulnerabilities()) {
                    violations.add(
                            dependency.name() + ": vulnerability violation"
                    );
                }
            });

            return violations;
        }
    }

    static class DependencyRepository {
        private final Map<String, Dependency> dependencies =
                new LinkedHashMap<>();

        void add(Dependency dependency) {
            if (dependencies.putIfAbsent(
                    dependency.name(), dependency) != null) {
                throw new ValidationException(
                        "Duplicate dependency: " + dependency.name()
                );
            }
        }

        Dependency get(String name) {
            Dependency dependency = dependencies.get(name);

            if (dependency == null) {
                throw new ValidationException(
                        "Unknown dependency: " + name
                );
            }

            return dependency;
        }

        Map<String, Dependency> snapshot() {
            return Collections.unmodifiableMap(
                    new LinkedHashMap<>(dependencies)
            );
        }

        void apply(Map<String, Version> changes) {
            // Validate all entries before mutating repository state.
            Map<String, Dependency> replacements = new HashMap<>();

            changes.forEach((name, version) -> {
                Dependency current = get(name);

                if (version.compareTo(current.current()) <= 0) {
                    throw new ValidationException(
                            "Update is not an upgrade: " + name
                    );
                }

                if (current.maximum() != null &&
                        version.compareTo(current.maximum()) > 0) {
                    throw new ValidationException(
                            "Version exceeds maximum: " + name
                    );
                }

                replacements.put(name, current.withVersion(version));
            });

            dependencies.putAll(replacements);
        }
    }

    static class DependencyResolver {

        static List<String> resolve(
                Map<String, Dependency> dependencies
        ) {
            Map<String, Integer> color = new HashMap<>();
            List<String> result = new ArrayList<>();

            List<String> names = dependencies.keySet().stream()
                    .sorted()
                    .toList();

            for (String name : names) {
                visit(name, dependencies, color, result);
            }

            return List.copyOf(result);
        }

        private static void visit(
                String name,
                Map<String, Dependency> dependencies,
                Map<String, Integer> color,
                List<String> result
        ) {
            int state = color.getOrDefault(name, 0);

            if (state == 1) {
                throw new GovernanceException(
                        "Circular dependency: " + name
                );
            }

            if (state == 2) return;

            Dependency dependency = dependencies.get(name);

            if (dependency == null) {
                throw new ValidationException(
                        "Missing dependency: " + name
                );
            }

            color.put(name, 1);

            dependency.prerequisites().stream()
                    .sorted()
                    .forEach(child ->
                            visit(child, dependencies, color, result)
                    );

            color.put(name, 2);
            result.add(name);
        }
    }

    static class DependencyGovernanceService {

        private final DependencyRepository repository;
        private final ReviewPolicy reviewPolicy;
        private final ProtectionPolicy protectionPolicy;
        private final DependencyScanner scanner;

        private final Set<String> protectedBranches =
                new HashSet<>(Set.of("main"));

        private final Map<Integer, PullRequest> pullRequests =
                new LinkedHashMap<>();

        private int nextId = 1;

        DependencyGovernanceService(
                DependencyRepository repository,
                ReviewPolicy reviewPolicy,
                ProtectionPolicy protectionPolicy
        ) {
            this.repository = repository;
            this.reviewPolicy = reviewPolicy;
            this.protectionPolicy = protectionPolicy;
            this.scanner = new GovernanceScanner(protectionPolicy);
        }

        Map<String, Version> planUpdates(
                Map<String, Version> available
        ) {
            Map<String, Version> plan = new TreeMap<>();

            available.forEach((name, candidate) -> {
                Dependency current = repository.get(name);

                if (candidate.compareTo(current.current()) <= 0) {
                    return;
                }

                if (current.maximum() != null &&
                        candidate.compareTo(current.maximum()) > 0) {
                    return;
                }

                plan.put(name, candidate);
            });

            return Collections.unmodifiableMap(plan);
        }

        PullRequest openPullRequest(
                String source,
                String target,
                Map<String, Version> changes,
                boolean draft
        ) {
            if (source == null || target == null ||
                    source.isBlank() || target.isBlank() ||
                    source.equals(target)) {
                throw new ValidationException("Invalid branch names");
            }

            if (!protectedBranches.contains(target)) {
                throw new GovernanceException(
                        "Target branch is not protected"
                );
            }

            if (changes.isEmpty()) {
                throw new ValidationException("Empty changeset");
            }

            changes.forEach((name, version) -> {
                Dependency current = repository.get(name);

                if (version.compareTo(current.current()) <= 0) {
                    throw new ValidationException(
                            "Not an upgrade: " + name
                    );
                }

                if (current.maximum() != null &&
                        version.compareTo(current.maximum()) > 0) {
                    throw new ValidationException(
                            "Version outside allowed range: " + name
                    );
                }
            });

            PullRequest pr = new PullRequest(
                    nextId++, source, target, changes, draft
            );

            pullRequests.put(pr.id, pr);
            return pr;
        }

        List<String> evaluate(PullRequest pr) {
            List<String> failures = new ArrayList<>();

            if (pr.state != PRState.OPEN) {
                failures.add("PR is not open");
            }

            if (pr.draft) {
                failures.add("Draft PR cannot be merged");
            }

            if (pr.mergeConflicts) {
                failures.add("Merge conflicts exist");
            }

            if (!pr.synchronizedWithBase) {
                failures.add("Base branch synchronization required");
            }

            if (reviewPolicy.requireResolvedConversations() &&
                    pr.conversations.values().stream().anyMatch(
                            resolved -> !resolved)) {
                failures.add("Unresolved review conversations");
            }

            if (protectionPolicy.requirePassingChecks()) {
                if (pr.checks.isEmpty()) {
                    failures.add("No status checks configured");
                } else if (pr.checks.values().stream().anyMatch(
                        check -> check != CheckState.PASSED)) {
                    failures.add("Required status checks not passed");
                }
            }

            List<Review> currentReviews = pr.reviews.values().stream()
                    .filter(review ->
                            review.commitHash().equals(pr.headCommit))
                    .toList();

            if (currentReviews.stream().anyMatch(
                    review -> review.state() ==
                            ReviewState.CHANGES_REQUESTED)) {
                failures.add("Changes requested");
            }

            long approvalCount = currentReviews.stream()
                    .filter(review ->
                            review.state() == ReviewState.APPROVED)
                    .map(Review::reviewer)
                    .distinct()
                    .count();

            if (approvalCount < reviewPolicy.requiredApprovals()) {
                failures.add(
                        "Insufficient eligible approvals: " +
                        approvalCount
                );
            }

            failures.addAll(
                    scanner.scan(repository.snapshot())
            );

            try {
                DependencyResolver.resolve(repository.snapshot());
            } catch (DependencyException exception) {
                failures.add(exception.getMessage());
            }

            if (protectionPolicy.requireLockfile() &&
                    repository.snapshot().isEmpty()) {
                failures.add("Dependency inventory is empty");
            }

            return List.copyOf(failures);
        }

        void merge(PullRequest pr, MergeStrategy strategy) {
            List<String> failures = evaluate(pr);

            if (!failures.isEmpty()) {
                throw new GovernanceException(
                        String.join("; ", failures)
                );
            }

            // Repository changes occur only after policy validation.
            repository.apply(pr.changes());

            pr.state = PRState.MERGED;
            System.out.println(
                    "PR #" + pr.id + " merged using " + strategy
            );
        }

        void close(PullRequest pr) {
            if (pr.state == PRState.MERGED) {
                throw new GovernanceException(
                        "Merged PR cannot be closed as unmerged"
                );
            }
            pr.state = PRState.CLOSED;
        }

        void reopen(PullRequest pr) {
            if (pr.state != PRState.CLOSED) {
                throw new GovernanceException(
                        "Only closed unmerged PRs can be reopened"
                );
            }
            pr.state = PRState.OPEN;
        }
    }

    static String digest(String value) {
        try {
            MessageDigest digest =
                    MessageDigest.getInstance("SHA-256");

            byte[] bytes = digest.digest(
                    value.getBytes(java.nio.charset.StandardCharsets.UTF_8)
            );

            StringBuilder result = new StringBuilder();

            for (byte b : bytes) {
                result.append(String.format("%02x", b));
            }

            return result.toString();

        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException(exception);
        }
    }

    static void printInventory(DependencyRepository repository) {
        System.out.println("\nDEPENDENCY INVENTORY");

        repository.snapshot().values().stream()
                .sorted(Comparator.comparing(Dependency::name))
                .forEach(dependency ->
                        System.out.printf(
                                "%-16s %s | %s | vulnerabilities=%d%n",
                                dependency.name(),
                                dependency.current(),
                                dependency.license(),
                                dependency.vulnerabilities()
                        )
                );
    }

    public static void main(String[] args) {
        try {
            DependencyRepository repository =
                    new DependencyRepository();

            repository.add(new Dependency(
                    "httpx",
                    Version.parse("0.27.0"),
                    Version.parse("0.25.0"),
                    null,
                    true,
                    "BSD-3-Clause",
                    0,
                    List.of(),
                    "public-registry"
            ));

            repository.add(new Dependency(
                    "pydantic",
                    Version.parse("2.8.2"),
                    Version.parse("2.5.0"),
                    null,
                    true,
                    "MIT",
                    0,
                    List.of(),
                    "public-registry"
            ));

            repository.add(new Dependency(
                    "fastapi",
                    Version.parse("0.112.0"),
                    Version.parse("0.100.0"),
                    null,
                    true,
                    "MIT",
                    0,
                    List.of("httpx", "pydantic"),
                    "public-registry"
            ));

            repository.add(new Dependency(
                    "cryptography",
                    Version.parse("43.0.0"),
                    Version.parse("42.0.0"),
                    null,
                    true,
                    "Apache-2.0",
                    0,
                    List.of(),
                    "public-registry"
            ));

            ReviewPolicy reviewPolicy = new ReviewPolicy(
                    2, true, true
            );

            ProtectionPolicy protectionPolicy =
                    ProtectionPolicy.standard();

            DependencyGovernanceService service =
                    new DependencyGovernanceService(
                            repository,
                            reviewPolicy,
                            protectionPolicy
                    );

            printInventory(repository);

            System.out.println("\nRESOLUTION ORDER");
            System.out.println(
                    String.join(
                            " -> ",
                            DependencyResolver.resolve(repository.snapshot())
                    )
            );

            Map<String, Version> updates = service.planUpdates(
                    Map.of(
                            "httpx", Version.parse("0.28.1"),
                            "pydantic", Version.parse("2.9.2"),
                            "fastapi", Version.parse("0.115.0")
                    )
            );

            System.out.println("\nUPDATE PLAN");
            updates.forEach((name, version) ->
                    System.out.println(name + " -> " + version)
            );

            PullRequest pr = service.openPullRequest(
                    "dependency/quarterly-update",
                    "main",
                    updates,
                    false
            );

            pr.addCheck("unit-tests", CheckState.PASSED);
            pr.addCheck("security-scan", CheckState.PASSED);
            pr.addCheck("license-audit", CheckState.PASSED);

            pr.addConversation("compatibility", true);
            pr.addConversation("migration-impact", true);

            pr.submitReview(
                    "security-reviewer",
                    ReviewState.APPROVED
            );

            pr.submitReview(
                    "platform-reviewer",
                    ReviewState.APPROVED
            );

            System.out.println("\nMERGE ELIGIBILITY");
            List<String> failures = service.evaluate(pr);

            if (failures.isEmpty()) {
                System.out.println("ELIGIBLE");
                service.merge(pr, MergeStrategy.SQUASH);
            } else {
                failures.forEach(System.out::println);
            }

            printInventory(repository);

            // Demonstrate stale approval handling.
            PullRequest secondPR = service.openPullRequest(
                    "dependency/test-update",
                    "main",
                    Map.of(
                            "httpx",
                            Version.parse("0.28.2")
                    ),
                    false
            );

            secondPR.submitReview(
                    "reviewer-a",
                    ReviewState.APPROVED
            );

            secondPR.pushCommit(
                    Map.of("httpx", Version.parse("0.28.3")),
                    reviewPolicy
            );

            System.out.println("\nSTALE APPROVAL TEST");
            System.out.println(
                    "Approvals after new commit: " +
                    secondPR.reviews.values().stream()
                            .filter(r ->
                                    r.state() == ReviewState.APPROVED)
                            .count()
            );

            System.out.println("\nExecution completed.");

        } catch (DependencyException exception) {
            System.err.println("GOVERNANCE ERROR: " + exception.getMessage());
            System.exit(1);
        }
    }
}
