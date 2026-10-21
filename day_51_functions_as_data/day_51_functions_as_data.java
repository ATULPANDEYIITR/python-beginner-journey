import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.BiPredicate;
import java.util.function.Function;
import java.util.stream.Collectors;

public class FunctionsAsDataGovernance {

    enum PullRequestState {
        DRAFT,
        OPEN,
        CLOSED,
        MERGED
    }

    enum ReviewState {
        COMMENTED,
        APPROVED,
        CHANGES_REQUESTED,
        DISMISSED
    }

    enum MergeStrategy {
        MERGE_COMMIT,
        SQUASH,
        REBASE
    }

    record Commit(String sha, String message, String author) {
        Commit {
            if (sha == null || sha.isBlank()) {
                throw new IllegalArgumentException("Commit SHA is required.");
            }
            if (message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit message is required.");
            }
            if (author == null || author.isBlank()) {
                throw new IllegalArgumentException("Commit author is required.");
            }
        }
    }

    record Review(
            String reviewer,
            ReviewState state,
            List<String> comments,
            Instant submittedAt
    ) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            Objects.requireNonNull(state, "Review state is required.");
            comments = List.copyOf(comments == null ? List.of() : comments);
            submittedAt = submittedAt == null ? Instant.now() : submittedAt;
        }
    }

    record BranchProtection(
            String branch,
            int requiredReviews,
            Set<String> requiredStatusChecks,
            boolean requireConversationResolution,
            boolean requireLinearHistory,
            boolean allowDirectPush,
            boolean allowForcePush,
            boolean allowDeletion,
            boolean allowAdminBypass
    ) {
        BranchProtection {
            if (branch == null || branch.isBlank()) {
                throw new IllegalArgumentException("Protected branch is required.");
            }
            if (requiredReviews < 0) {
                throw new IllegalArgumentException(
                        "Required review count cannot be negative."
                );
            }
            requiredStatusChecks =
                    Set.copyOf(requiredStatusChecks == null
                            ? Set.of()
                            : requiredStatusChecks);
        }
    }

    static final class PullRequest {
        private final int number;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<Commit> commits = new ArrayList<>();
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, Boolean> statusChecks = new HashMap<>();

        private PullRequestState state;
        private int openConversations;
        private boolean mergeable = true;
        private boolean synchronizedWithBase = true;

        PullRequest(
                int number,
                String sourceBranch,
                String targetBranch,
                List<Commit> commits,
                boolean draft
        ) {
            if (number <= 0) {
                throw new IllegalArgumentException("PR number must be positive.");
            }
            if (sourceBranch == null || targetBranch == null
                    || sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException("Invalid branch pair.");
            }

            this.number = number;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.commits.addAll(commits == null ? List.of() : commits);
            this.state = draft
                    ? PullRequestState.DRAFT
                    : PullRequestState.OPEN;
        }

        void submitReview(Review review) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException(
                        "Only open Pull Requests accept reviews."
                );
            }
            reviews.add(Objects.requireNonNull(review));
        }

        void setStatus(String name, boolean passed) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Status name is required.");
            }
            statusChecks.put(name, passed);
        }

        void setOpenConversations(int count) {
            if (count < 0) {
                throw new IllegalArgumentException(
                        "Conversation count cannot be negative."
                );
            }
            openConversations = count;
        }

        void markConflict() {
            mergeable = false;
            synchronizedWithBase = false;
        }

        void synchronize() {
            synchronizedWithBase = true;
            mergeable = true;
        }

        void close() {
            if (state == PullRequestState.MERGED) {
                throw new IllegalStateException(
                        "Merged Pull Requests cannot be closed."
                );
            }
            state = PullRequestState.CLOSED;
        }

        void reopen() {
            if (state != PullRequestState.CLOSED) {
                throw new IllegalStateException(
                        "Only closed Pull Requests can be reopened."
                );
            }
            state = PullRequestState.OPEN;
        }

        void markMerged() {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException(
                        "Only open Pull Requests can be merged."
                );
            }
            state = PullRequestState.MERGED;
        }

        int number() {
            return number;
        }

        String targetBranch() {
            return targetBranch;
        }

        PullRequestState state() {
            return state;
        }

        List<Review> reviews() {
            return List.copyOf(reviews);
        }

        Map<String, Boolean> statusChecks() {
            return Map.copyOf(statusChecks);
        }

        boolean mergeable() {
            return mergeable;
        }

        boolean synchronizedWithBase() {
            return synchronizedWithBase;
        }

        int openConversations() {
            return openConversations;
        }

        List<Commit> commits() {
            return List.copyOf(commits);
        }
    }

    static final class Repository {
        private final String name;
        private final String defaultBranch;
        private final Map<String, BranchProtection> protections =
                new HashMap<>();

        Repository(String name, String defaultBranch) {
            this.name = Objects.requireNonNull(name);
            this.defaultBranch = Objects.requireNonNull(defaultBranch);
        }

        void protect(BranchProtection protection) {
            protections.put(protection.branch(), protection);
        }

        BranchProtection protectionFor(String branch) {
            return protections.get(branch);
        }
    }

    /*
     * A GovernanceRule is a function stored as a domain value.
     * The same interface can represent named rules, lambdas, method
     * references, or policy functions created at runtime.
     */
    @FunctionalInterface
    interface GovernanceRule
            extends BiPredicate<PullRequest, Repository> {
    }

    static final class GovernancePolicy {
        private final Map<String, GovernanceRule> rules = new HashMap<>();

        void register(String name, GovernanceRule rule) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Rule name is required.");
            }
            rules.put(name, Objects.requireNonNull(rule));
        }

        boolean evaluate(
                String name,
                PullRequest pr,
                Repository repository
        ) {
            GovernanceRule rule = rules.get(name);

            if (rule == null) {
                throw new IllegalArgumentException(
                        "Unknown governance rule: " + name
                );
            }

            return rule.test(pr, repository);
        }

        Map<String, Boolean> evaluateAll(
                PullRequest pr,
                Repository repository
        ) {
            return rules.entrySet()
                    .stream()
                    .collect(Collectors.toMap(
                            Map.Entry::getKey,
                            entry -> entry.getValue().test(pr, repository)
                    ));
        }
    }

    static BranchProtection requireProtection(
            PullRequest pr,
            Repository repository
    ) {
        BranchProtection protection =
                repository.protectionFor(pr.targetBranch());

        if (protection == null) {
            throw new IllegalStateException(
                    "Target branch is not governed by protection policy."
            );
        }

        return protection;
    }

    static final GovernanceRule OPEN_AND_MERGEABLE =
            (pr, repo) ->
                    pr.state() == PullRequestState.OPEN
                            && pr.mergeable()
                            && pr.synchronizedWithBase();

    static final GovernanceRule REQUIRED_APPROVALS =
            (pr, repo) -> {
                BranchProtection policy = requireProtection(pr, repo);

                Set<String> eligibleApprovers =
                        pr.reviews()
                                .stream()
                                .filter(review ->
                                        review.state()
                                                == ReviewState.APPROVED)
                                .map(Review::reviewer)
                                .collect(Collectors.toCollection(HashSet::new));

                return eligibleApprovers.size()
                        >= policy.requiredReviews();
            };

    static final GovernanceRule NO_REQUESTED_CHANGES =
            (pr, repo) ->
                    pr.reviews()
                            .stream()
                            .noneMatch(review ->
                                    review.state()
                                            == ReviewState.CHANGES_REQUESTED);

    static final GovernanceRule STATUS_CHECKS =
            (pr, repo) -> {
                BranchProtection policy = requireProtection(pr, repo);

                return policy.requiredStatusChecks()
                        .stream()
                        .allMatch(check ->
                                Boolean.TRUE.equals(
                                        pr.statusChecks().get(check)));
            };

    static final GovernanceRule CONVERSATIONS_RESOLVED =
            (pr, repo) -> {
                BranchProtection policy = requireProtection(pr, repo);

                return !policy.requireConversationResolution()
                        || pr.openConversations() == 0;
            };

    static GovernanceRule all(
            List<GovernanceRule> rules
    ) {
        if (rules.isEmpty()) {
            throw new IllegalArgumentException(
                    "At least one governance rule is required."
            );
        }

        return (pr, repository) ->
                rules.stream()
                        .allMatch(rule -> rule.test(pr, repository));
    }

    static String merge(
            PullRequest pr,
            Repository repository,
            MergeStrategy strategy
    ) {
        GovernanceRule mergePolicy = all(List.of(
                OPEN_AND_MERGEABLE,
                REQUIRED_APPROVALS,
                NO_REQUESTED_CHANGES,
                STATUS_CHECKS,
                CONVERSATIONS_RESOLVED
        ));

        if (!mergePolicy.test(pr, repository)) {
            throw new IllegalStateException(
                    "Pull Request does not satisfy merge policy."
            );
        }

        pr.markMerged();

        return switch (strategy) {
            case MERGE_COMMIT ->
                    "Merge commit created for PR #" + pr.number();
            case SQUASH ->
                    "PR #" + pr.number() + " squashed into "
                            + pr.targetBranch();
            case REBASE ->
                    "PR #" + pr.number() + " rebased into "
                            + pr.targetBranch();
        };
    }

    /*
     * Functions can also be used for transformations unrelated to the
     * governance predicates while remaining part of the same data-oriented
     * design. The Function interface carries the transformation as data.
     */
    static String normalizeBranch(
            String branch,
            List<Function<String, String>> transformations
    ) {
        Objects.requireNonNull(branch);

        String result = branch;

        for (Function<String, String> transformation : transformations) {
            result = transformation.apply(result);
        }

        return result;
    }

    public static void main(String[] args) {
        Repository repository =
                new Repository("customer-platform", "main");

        repository.protect(
                new BranchProtection(
                        "main",
                        2,
                        Set.of("unit-tests", "security-scan"),
                        true,
                        true,
                        false,
                        false,
                        false,
                        false
                )
        );

        PullRequest pr = new PullRequest(
                900,
                "feature/customer-validation",
                "main",
                List.of(
                        new Commit(
                                "a100",
                                "Validate customer records",
                                "alice"
                        ),
                        new Commit(
                                "a101",
                                "Add validation tests",
                                "alice"
                        )
                ),
                false
        );

        pr.submitReview(new Review(
                "bob",
                ReviewState.APPROVED,
                List.of(),
                Instant.now()
        ));

        pr.submitReview(new Review(
                "carol",
                ReviewState.APPROVED,
                List.of(),
                Instant.now()
        ));

        pr.setStatus("unit-tests", true);
        pr.setStatus("security-scan", true);
        pr.setOpenConversations(0);

        GovernancePolicy policy = new GovernancePolicy();

        policy.register("mergeable", OPEN_AND_MERGEABLE);
        policy.register("approvals", REQUIRED_APPROVALS);
        policy.register("review-state", NO_REQUESTED_CHANGES);
        policy.register("status-checks", STATUS_CHECKS);
        policy.register("conversations", CONVERSATIONS_RESOLVED);

        /*
         * A policy is now a registry of executable functions. The registry
         * can be evaluated without coupling the caller to individual rule
         * implementations.
         */
        System.out.println("Policy evaluation:");
        policy.evaluateAll(pr, repository)
                .forEach((name, passed) ->
                        System.out.println(
                                "  " + name + " = " + passed
                        ));

        System.out.println(
                merge(pr, repository, MergeStrategy.SQUASH)
        );

        List<Function<String, String>> branchRules = List.of(
                String::trim,
                value -> value.toLowerCase().replace(' ', '-'),
                value -> value.replaceAll("[^a-z0-9/_-]", "")
        );

        System.out.println(
                "Normalized branch: "
                        + normalizeBranch(
                                " Feature Customer Validation ",
                                branchRules
                        )
        );

        /*
         * Failure case: duplicate approval from one reviewer does not
         * satisfy two-reviewer policy.
         */
        PullRequest blocked = new PullRequest(
                901,
                "feature/report",
                "main",
                List.of(
                        new Commit(
                                "b200",
                                "Add report endpoint",
                                "dave"
                        )
                ),
                false
        );

        blocked.submitReview(new Review(
                "bob",
                ReviewState.APPROVED,
                List.of(),
                Instant.now()
        ));

        blocked.submitReview(new Review(
                "bob",
                ReviewState.APPROVED,
                List.of(),
                Instant.now()
        ));

        blocked.setStatus("unit-tests", true);
        blocked.setStatus("security-scan", true);

        System.out.println(
                "Duplicate approval accepted: "
                        + REQUIRED_APPROVALS.test(blocked, repository)
        );

        try {
            merge(blocked, repository, MergeStrategy.MERGE_COMMIT);
        } catch (IllegalStateException error) {
            System.out.println(
                    "Expected merge failure: " + error.getMessage()
            );
        }

        /*
         * Administrative bypass is deliberately represented as a separate
         * policy concern. A normal merge operation does not silently bypass
         * branch protection simply because an administrator exists.
         */
        System.out.println(
                "Protected branch: "
                        + repository.protectionFor("main").branch()
        );
    }
}
