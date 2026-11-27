/*
 * POLYMORPHISM IN JAVA 17
 *
 * Enterprise repository governance and merge authorization.
 *
 * Demonstrates:
 * 1. Interface-based polymorphism
 * 2. Abstract classes
 * 3. Method overriding
 * 4. Records and immutable domain objects
 * 5. Sealed interfaces
 * 6. Strategy-based policy evaluation
 * 7. Generic collections
 * 8. Streams
 * 9. Custom exceptions
 * 10. Explicit state transitions
 * 11. Approval eligibility
 * 12. Branch protection
 *
 * Compile:
 * javac --release 17 PolymorphismDemo.java
 *
 * Run:
 * java PolymorphismDemo
 */

import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.function.Predicate;
import java.util.stream.Collectors;


public class PolymorphismDemo {

    /* ======================================================
       1. ENUMERATIONS
       ====================================================== */

    enum ReviewState {
        APPROVED,
        CHANGES_REQUESTED,
        COMMENTED,
        DISMISSED
    }

    enum CheckState {
        PASSED,
        FAILED,
        PENDING
    }

    enum PullRequestState {
        DRAFT,
        OPEN,
        CLOSED,
        MERGED
    }

    enum MergeStrategy {
        MERGE_COMMIT,
        SQUASH,
        REBASE
    }


    /* ======================================================
       2. CUSTOM EXCEPTIONS
       ====================================================== */

    static class GovernanceException extends RuntimeException {
        GovernanceException(String message) {
            super(message);
        }
    }

    static class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }


    /* ======================================================
       3. IMMUTABLE DOMAIN TYPES
       ====================================================== */

    record Commit(
        String hash,
        String author,
        String message,
        Instant createdAt
    ) {
        Commit {
            requireText(hash, "Commit hash");
            requireText(author, "Author");
            requireText(message, "Commit message");
            Objects.requireNonNull(createdAt);
        }
    }


    record Review(
        String reviewerId,
        ReviewState state,
        String commitHash,
        boolean eligible,
        boolean conversationResolved
    ) {
        Review {
            requireText(reviewerId, "Reviewer ID");
            Objects.requireNonNull(state);
            requireText(commitHash, "Review commit hash");
        }
    }


    record StatusCheck(
        String name,
        CheckState state,
        String commitHash
    ) {
        StatusCheck {
            requireText(name, "Check name");
            Objects.requireNonNull(state);
            requireText(commitHash, "Check commit hash");
        }
    }


    record Branch(
        String name,
        String headCommit,
        boolean protectedBranch
    ) {
        Branch {
            requireText(name, "Branch name");
            requireText(headCommit, "Branch head");
        }
    }


    record ProtectionPolicy(
        int requiredApprovals,
        Set<String> requiredChecks,
        boolean requireResolvedConversations,
        boolean requireLinearHistory,
        boolean prohibitForcePush,
        boolean prohibitDeletion
    ) {
        ProtectionPolicy {
            if (requiredApprovals < 0) {
                throw new ValidationException(
                    "Approval requirement cannot be negative."
                );
            }

            requiredChecks = Set.copyOf(requiredChecks);
        }
    }


    record PullRequest(
        long id,
        String title,
        String sourceBranch,
        String targetBranch,
        String baseCommit,
        String headCommit,
        PullRequestState state,
        boolean draft,
        List<Commit> commits,
        List<Review> reviews,
        List<StatusCheck> checks
    ) {
        PullRequest {
            if (id <= 0) {
                throw new ValidationException(
                    "Pull Request ID must be positive."
                );
            }

            requireText(title, "Title");
            requireText(sourceBranch, "Source branch");
            requireText(targetBranch, "Target branch");
            requireText(baseCommit, "Base commit");
            requireText(headCommit, "Head commit");

            if (sourceBranch.equals(targetBranch)) {
                throw new ValidationException(
                    "Source and target branches must differ."
                );
            }

            Objects.requireNonNull(state);

            commits = List.copyOf(commits);
            reviews = List.copyOf(reviews);
            checks = List.copyOf(checks);

            if (commits.isEmpty()) {
                throw new ValidationException(
                    "Pull Request requires at least one commit."
                );
            }
        }
    }


    record EvaluationResult(
        boolean eligible,
        List<String> violations
    ) {
        EvaluationResult {
            violations = List.copyOf(violations);
        }
    }


    private static void requireText(
        String value,
        String field
    ) {
        if (value == null || value.isBlank()) {
            throw new ValidationException(
                field + " cannot be empty."
            );
        }
    }


    /* ======================================================
       4. SEALED POLICY INTERFACE
       ====================================================== */

    sealed interface GovernanceRule permits
        ApprovalRule,
        StatusCheckRule,
        ConversationRule,
        LinearHistoryRule,
        BranchProtectionRule {

        String name();

        List<String> evaluate(
            PullRequest pr,
            Branch target,
            ProtectionPolicy policy,
            MergeStrategy strategy
        );
    }


    /* ======================================================
       5. APPROVAL POLICY
       ====================================================== */

    static final class ApprovalRule implements GovernanceRule {

        @Override
        public String name() {
            return "ApprovalRule";
        }

        @Override
        public List<String> evaluate(
            PullRequest pr,
            Branch target,
            ProtectionPolicy policy,
            MergeStrategy strategy
        ) {

            Set<String> reviewers = pr.reviews()
                .stream()
                .filter(Review::eligible)
                .filter(r ->
                    r.state() == ReviewState.APPROVED
                )
                .filter(r ->
                    r.commitHash().equals(pr.headCommit())
                )
                .map(Review::reviewerId)
                .collect(Collectors.toSet());

            if (reviewers.size() < policy.requiredApprovals()) {
                return List.of(
                    "Required current approvals are missing."
                );
            }

            return List.of();
        }
    }


    /* ======================================================
       6. STATUS CHECK POLICY
       ====================================================== */

    static final class StatusCheckRule implements GovernanceRule {

        @Override
        public String name() {
            return "StatusCheckRule";
        }

        @Override
        public List<String> evaluate(
            PullRequest pr,
            Branch target,
            ProtectionPolicy policy,
            MergeStrategy strategy
        ) {

            Map<String, CheckState> currentChecks =
                pr.checks()
                    .stream()
                    .filter(c ->
                        c.commitHash().equals(pr.headCommit())
                    )
                    .collect(Collectors.toMap(
                        StatusCheck::name,
                        StatusCheck::state,
                        (first, second) -> second
                    ));

            List<String> violations = new ArrayList<>();

            for (String required : policy.requiredChecks()) {

                CheckState state = currentChecks.get(required);

                if (state == null) {
                    violations.add(
                        "Missing check: " + required
                    );
                } else if (state != CheckState.PASSED) {
                    violations.add(
                        "Check not passed: " + required
                    );
                }
            }

            return violations;
        }
    }


    /* ======================================================
       7. CONVERSATION POLICY
       ====================================================== */

    static final class ConversationRule implements GovernanceRule {

        @Override
        public String name() {
            return "ConversationRule";
        }

        @Override
        public List<String> evaluate(
            PullRequest pr,
            Branch target,
            ProtectionPolicy policy,
            MergeStrategy strategy
        ) {

            if (!policy.requireResolvedConversations()) {
                return List.of();
            }

            boolean unresolved = pr.reviews()
                .stream()
                .anyMatch(r -> !r.conversationResolved());

            return unresolved
                ? List.of("Review conversations remain unresolved.")
                : List.of();
        }
    }


    /* ======================================================
       8. LINEAR HISTORY POLICY
       ====================================================== */

    static final class LinearHistoryRule implements GovernanceRule {

        @Override
        public String name() {
            return "LinearHistoryRule";
        }

        @Override
        public List<String> evaluate(
            PullRequest pr,
            Branch target,
            ProtectionPolicy policy,
            MergeStrategy strategy
        ) {

            if (
                policy.requireLinearHistory() &&
                strategy == MergeStrategy.MERGE_COMMIT
            ) {
                return List.of(
                    "Merge commit prohibited by linear-history policy."
                );
            }

            return List.of();
        }
    }


    /* ======================================================
       9. BRANCH PROTECTION POLICY
       ====================================================== */

    static final class BranchProtectionRule
        implements GovernanceRule {

        @Override
        public String name() {
            return "BranchProtectionRule";
        }

        @Override
        public List<String> evaluate(
            PullRequest pr,
            Branch target,
            ProtectionPolicy policy,
            MergeStrategy strategy
        ) {

            if (!target.protectedBranch()) {
                return List.of();
            }

            if (
                pr.sourceBranch().equals(pr.targetBranch())
            ) {
                return List.of(
                    "Invalid source and target relationship."
                );
            }

            return List.of();
        }
    }


    /* ======================================================
       10. GOVERNANCE SERVICE
       ====================================================== */

    static final class GovernanceService {

        private final List<GovernanceRule> rules;

        GovernanceService(List<GovernanceRule> rules) {
            this.rules = List.copyOf(rules);

            if (this.rules.stream().anyMatch(Objects::isNull)) {
                throw new ValidationException(
                    "Governance rules cannot contain null."
                );
            }
        }

        EvaluationResult evaluate(
            PullRequest pr,
            Branch target,
            ProtectionPolicy policy,
            MergeStrategy strategy
        ) {

            Objects.requireNonNull(pr);
            Objects.requireNonNull(target);
            Objects.requireNonNull(policy);
            Objects.requireNonNull(strategy);

            List<String> violations = new ArrayList<>();

            if (pr.state() != PullRequestState.OPEN) {
                violations.add(
                    "Pull Request must be open."
                );

                return new EvaluationResult(false, violations);
            }

            if (pr.draft()) {
                violations.add(
                    "Draft Pull Request cannot be merged."
                );

                return new EvaluationResult(false, violations);
            }

            if (!pr.targetBranch().equals(target.name())) {
                violations.add(
                    "Target branch mismatch."
                );

                return new EvaluationResult(false, violations);
            }

            if (!pr.baseCommit().equals(target.headCommit())) {
                violations.add(
                    "Pull Request must synchronize with target branch."
                );

                return new EvaluationResult(false, violations);
            }

            for (GovernanceRule rule : rules) {
                violations.addAll(
                    rule.evaluate(
                        pr,
                        target,
                        policy,
                        strategy
                    )
                );
            }

            return new EvaluationResult(
                violations.isEmpty(),
                violations
            );
        }
    }


    /* ======================================================
       11. STATE TRANSITION SERVICE
       ====================================================== */

    static final class PullRequestLifecycle {

        private PullRequestState state;

        PullRequestLifecycle(PullRequestState initialState) {
            this.state = Objects.requireNonNull(initialState);
        }

        PullRequestState getState() {
            return state;
        }

        void open() {
            if (
                state != PullRequestState.DRAFT &&
                state != PullRequestState.CLOSED
            ) {
                throw new GovernanceException(
                    "Pull Request cannot be opened from current state."
                );
            }

            state = PullRequestState.OPEN;
        }

        void close() {
            if (state != PullRequestState.OPEN) {
                throw new GovernanceException(
                    "Only open Pull Requests can be closed."
                );
            }

            state = PullRequestState.CLOSED;
        }

        void merge() {
            if (state != PullRequestState.OPEN) {
                throw new GovernanceException(
                    "Only open Pull Requests can be merged."
                );
            }

            state = PullRequestState.MERGED;
        }
    }


    /* ======================================================
       12. MERGE AUTHORIZATION
       ====================================================== */

    static final class MergeAuthorizationService {

        private final GovernanceService governanceService;

        MergeAuthorizationService(
            GovernanceService governanceService
        ) {
            this.governanceService = governanceService;
        }

        EvaluationResult authorize(
            PullRequest pr,
            Branch target,
            ProtectionPolicy policy,
            MergeStrategy strategy
        ) {

            return governanceService.evaluate(
                pr,
                target,
                policy,
                strategy
            );
        }
    }


    /* ======================================================
       13. DEMONSTRATION
       ====================================================== */

    public static void main(String[] args) {

        System.out.println(
            "\n1. ENTERPRISE REPOSITORY GOVERNANCE"
        );

        Branch main = new Branch(
            "main",
            "commit-100",
            true
        );

        ProtectionPolicy policy = new ProtectionPolicy(
            2,
            Set.of(
                "unit-tests",
                "security-scan",
                "build"
            ),
            true,
            true,
            true,
            true
        );

        List<Commit> commits = List.of(
            new Commit(
                "commit-104",
                "developer1",
                "Add repository service",
                Instant.now()
            ),
            new Commit(
                "commit-105",
                "developer1",
                "Add input validation",
                Instant.now()
            )
        );

        List<Review> reviews = List.of(
            new Review(
                "reviewer1",
                ReviewState.APPROVED,
                "commit-105",
                true,
                true
            ),
            new Review(
                "reviewer2",
                ReviewState.APPROVED,
                "commit-105",
                true,
                true
            )
        );

        List<StatusCheck> checks = List.of(
            new StatusCheck(
                "unit-tests",
                CheckState.PASSED,
                "commit-105"
            ),
            new StatusCheck(
                "security-scan",
                CheckState.PASSED,
                "commit-105"
            ),
            new StatusCheck(
                "build",
                CheckState.PASSED,
                "commit-105"
            )
        );

        PullRequest pr = new PullRequest(
            501,
            "Implement secure repository service",
            "feature/repository-service",
            "main",
            "commit-100",
            "commit-105",
            PullRequestState.OPEN,
            false,
            commits,
            reviews,
            checks
        );

        List<GovernanceRule> rules = List.of(
            new ApprovalRule(),
            new StatusCheckRule(),
            new ConversationRule(),
            new LinearHistoryRule(),
            new BranchProtectionRule()
        );

        GovernanceService service =
            new GovernanceService(rules);

        MergeAuthorizationService authorization =
            new MergeAuthorizationService(service);

        System.out.println("\n2. POLYMORPHIC POLICY EVALUATION");

        EvaluationResult result = authorization.authorize(
            pr,
            main,
            policy,
            MergeStrategy.SQUASH
        );

        System.out.println(
            "Eligible: " + result.eligible()
        );

        result.violations().forEach(
            System.out::println
        );

        System.out.println("\n3. STALE APPROVAL TEST");

        PullRequest stalePR = new PullRequest(
            502,
            "Change service implementation",
            "feature/service-v2",
            "main",
            "commit-100",
            "commit-200",
            PullRequestState.OPEN,
            false,
            commits,
            reviews,
            checks
        );

        EvaluationResult staleResult = service.evaluate(
            stalePR,
            main,
            policy,
            MergeStrategy.SQUASH
        );

        System.out.println(staleResult);

        System.out.println("\n4. STATUS CHECK FAILURE");

        List<StatusCheck> failedChecks = List.of(
            new StatusCheck(
                "unit-tests",
                CheckState.PASSED,
                "commit-105"
            ),
            new StatusCheck(
                "security-scan",
                CheckState.FAILED,
                "commit-105"
            ),
            new StatusCheck(
                "build",
                CheckState.PASSED,
                "commit-105"
            )
        );

        PullRequest failedPR = new PullRequest(
            503,
            "Security validation update",
            "feature/security",
            "main",
            "commit-100",
            "commit-105",
            PullRequestState.OPEN,
            false,
            commits,
            reviews,
            failedChecks
        );

        System.out.println(
            service.evaluate(
                failedPR,
                main,
                policy,
                MergeStrategy.SQUASH
            )
        );

        System.out.println("\n5. DRAFT STATE");

        PullRequest draftPR = new PullRequest(
            504,
            "Draft implementation",
            "feature/draft",
            "main",
            "commit-100",
            "commit-105",
            PullRequestState.OPEN,
            true,
            commits,
            reviews,
            checks
        );

        System.out.println(
            service.evaluate(
                draftPR,
                main,
                policy,
                MergeStrategy.SQUASH
            )
        );

        System.out.println("\n6. LIFECYCLE TRANSITIONS");

        PullRequestLifecycle lifecycle =
            new PullRequestLifecycle(PullRequestState.DRAFT);

        lifecycle.open();

        System.out.println(lifecycle.getState());

        lifecycle.close();

        System.out.println(lifecycle.getState());

        lifecycle.open();
        lifecycle.merge();

        System.out.println(lifecycle.getState());

        System.out.println("\n7. EDGE CASE VALIDATION");

        try {
            new PullRequest(
                -1,
                "Invalid request",
                "main",
                "main",
                "commit-100",
                "commit-105",
                PullRequestState.OPEN,
                false,
                commits,
                reviews,
                checks
            );
        } catch (ValidationException exception) {
            System.out.println(
                "Rejected: " + exception.getMessage()
            );
        }

        try {
            lifecycle.merge();
        } catch (GovernanceException exception) {
            System.out.println(
                "Invalid transition: " + exception.getMessage()
            );
        }

        System.out.println("\n8. STREAM-BASED REVIEW ANALYSIS");

        long approvedCount = reviews.stream()
            .filter(r -> r.state() == ReviewState.APPROVED)
            .filter(Review::eligible)
            .count();

        System.out.println(
            "Eligible approvals: " + approvedCount
        );

        System.out.println("\nExecution completed.");
    }
}
