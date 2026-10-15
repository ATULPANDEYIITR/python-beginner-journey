import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/*
 * Enterprise repository governance model.
 *
 * Java has no general named-argument syntax. Records, enums, explicit policy
 * objects, and validated builder methods provide named, auditable configuration.
 * The model separates review decisions from the rules that determine whether
 * those decisions satisfy a protected branch's merge requirements.
 */
public class KeywordArguments {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        APPROVED, CHANGES_REQUESTED, COMMENTED
    }

    enum CheckState {
        PENDING, SUCCESS, FAILURE
    }

    enum MergeStrategy {
        MERGE_COMMIT, SQUASH, REBASE
    }

    record Commit(String sha, List<String> changedFiles) {
        Commit {
            Objects.requireNonNull(sha, "sha");
            Objects.requireNonNull(changedFiles, "changedFiles");

            if (!Pattern.matches("[0-9a-f]{7,40}", sha)) {
                throw new IllegalArgumentException("Invalid lowercase commit SHA");
            }

            if (changedFiles.isEmpty()) {
                throw new IllegalArgumentException("Commit must change a file");
            }

            if (changedFiles.stream().anyMatch(
                    file -> file == null || file.isBlank() || file.startsWith("/")
            )) {
                throw new IllegalArgumentException(
                        "Changed file paths must be relative and non-empty"
                );
            }

            changedFiles = List.copyOf(new LinkedHashSet<>(changedFiles));
        }
    }

    record Review(
            String reviewer,
            ReviewState state,
            String commitSha,
            boolean dismissed,
            boolean eligible,
            Instant submittedAt
    ) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer identity is required");
            }

            Objects.requireNonNull(state, "state");
            Objects.requireNonNull(commitSha, "commitSha");
            Objects.requireNonNull(submittedAt, "submittedAt");
        }

        Review dismiss() {
            return new Review(
                    reviewer, state, commitSha, true, eligible, submittedAt
            );
        }
    }

    record Conversation(String id, boolean resolved) {
        Conversation {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Conversation ID is required");
            }
        }

        Conversation resolve() {
            return new Conversation(id, true);
        }
    }

    /*
     * The policy object groups related branch requirements and validates their
     * types at construction. Its collections are immutable snapshots.
     */
    record BranchProtection(
            String branch,
            int requiredApprovals,
            Set<String> requiredChecks,
            boolean dismissStaleReviews,
            boolean requireConversationResolution,
            boolean requireLinearHistory,
            boolean restrictDirectPushes,
            boolean allowForcePush,
            boolean allowDeletion,
            boolean enforceForAdministrators,
            boolean allowBypass
    ) {
        BranchProtection {
            if (branch == null || branch.isBlank()) {
                throw new IllegalArgumentException("Protected branch is required");
            }

            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                        "requiredApprovals cannot be negative"
                );
            }

            Objects.requireNonNull(requiredChecks, "requiredChecks");

            if (requiredChecks.stream().anyMatch(
                    check -> check == null || check.isBlank()
            )) {
                throw new IllegalArgumentException("Invalid required check name");
            }

            requiredChecks = Collections.unmodifiableSet(
                    new LinkedHashSet<>(requiredChecks)
            );
        }

        static Builder builder(String branch) {
            return new Builder(branch);
        }

        static final class Builder {
            private final String branch;
            private int requiredApprovals = 2;
            private Set<String> requiredChecks =
                    new LinkedHashSet<>(List.of("unit-tests", "security-scan"));
            private boolean dismissStaleReviews = true;
            private boolean requireConversationResolution = true;
            private boolean requireLinearHistory = true;
            private boolean restrictDirectPushes = true;
            private boolean allowForcePush;
            private boolean allowDeletion;
            private boolean enforceForAdministrators = true;
            private boolean allowBypass;

            private Builder(String branch) {
                this.branch = branch;
            }

            Builder requiredApprovals(int value) {
                requiredApprovals = value;
                return this;
            }

            Builder requiredChecks(String... values) {
                requiredChecks = new LinkedHashSet<>(List.of(values));
                return this;
            }

            Builder dismissStaleReviews(boolean value) {
                dismissStaleReviews = value;
                return this;
            }

            Builder requireConversationResolution(boolean value) {
                requireConversationResolution = value;
                return this;
            }

            Builder requireLinearHistory(boolean value) {
                requireLinearHistory = value;
                return this;
            }

            Builder restrictDirectPushes(boolean value) {
                restrictDirectPushes = value;
                return this;
            }

            Builder allowForcePush(boolean value) {
                allowForcePush = value;
                return this;
            }

            Builder allowDeletion(boolean value) {
                allowDeletion = value;
                return this;
            }

            Builder enforceForAdministrators(boolean value) {
                enforceForAdministrators = value;
                return this;
            }

            Builder allowBypass(boolean value) {
                allowBypass = value;
                return this;
            }

            BranchProtection build() {
                return new BranchProtection(
                        branch,
                        requiredApprovals,
                        requiredChecks,
                        dismissStaleReviews,
                        requireConversationResolution,
                        requireLinearHistory,
                        restrictDirectPushes,
                        allowForcePush,
                        allowDeletion,
                        enforceForAdministrators,
                        allowBypass
                );
            }
        }
    }

    record MergeEvaluation(
            boolean eligible,
            int validApprovals,
            List<String> blockers,
            String latestCommit
    ) {
        MergeEvaluation {
            blockers = List.copyOf(blockers);
        }
    }

    static final class PullRequest {
        private final int id;
        private final String title;
        private final String sourceBranch;
        private final String targetBranch;
        private final Set<String> requestedReviewers;
        private PullRequestState state;

        private final List<Commit> commits = new ArrayList<>();
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, CheckState> checks = new LinkedHashMap<>();
        private final Map<String, Conversation> conversations =
                new LinkedHashMap<>();

        private String mergedBy;
        private MergeStrategy mergeStrategy;

        PullRequest(
                int id,
                String title,
                String sourceBranch,
                String targetBranch,
                Set<String> requestedReviewers,
                boolean draft
        ) {
            if (id <= 0) {
                throw new IllegalArgumentException("Pull Request ID must be positive");
            }

            if (title == null || title.isBlank()) {
                throw new IllegalArgumentException("Title is required");
            }

            if (sourceBranch == null ||
                    !sourceBranch.startsWith("feature/")) {
                throw new IllegalArgumentException(
                        "Source branch must begin with feature/"
                );
            }

            if (targetBranch == null || targetBranch.isBlank() ||
                    sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException("Invalid target branch");
            }

            Objects.requireNonNull(requestedReviewers, "requestedReviewers");

            if (requestedReviewers.stream().anyMatch(
                    reviewer -> reviewer == null || reviewer.isBlank()
            )) {
                throw new IllegalArgumentException("Invalid requested reviewer");
            }

            this.id = id;
            this.title = title;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.requestedReviewers = Collections.unmodifiableSet(
                    new LinkedHashSet<>(requestedReviewers)
            );
            this.state = draft
                    ? PullRequestState.DRAFT
                    : PullRequestState.OPEN;
        }

        int id() {
            return id;
        }

        PullRequestState state() {
            return state;
        }

        List<Commit> commits() {
            return List.copyOf(commits);
        }

        List<Review> reviews() {
            return List.copyOf(reviews);
        }

        void markReady() {
            if (state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Only a draft can become ready");
            }
            state = PullRequestState.OPEN;
        }

        void addCommit(Commit commit, BranchProtection protection) {
            requireOpen();
            Objects.requireNonNull(commit, "commit");

            if (commits.stream().anyMatch(
                    existing -> existing.sha().equals(commit.sha())
            )) {
                throw new IllegalArgumentException("Duplicate commit SHA");
            }

            commits.add(commit);

            if (protection.dismissStaleReviews()) {
                String currentSha = commit.sha();

                for (int index = 0; index < reviews.size(); index++) {
                    Review review = reviews.get(index);

                    if (!review.commitSha().equals(currentSha) &&
                            !review.dismissed()) {
                        reviews.set(index, review.dismiss());
                    }
                }
            }
        }

        void submitReview(Review review) {
            requireOpen();
            Objects.requireNonNull(review, "review");

            if (!requestedReviewers.contains(review.reviewer())) {
                throw new IllegalArgumentException(
                        "Reviewer is not requested for this Pull Request"
                );
            }

            String currentSha = latestCommit()
                    .orElseThrow(() -> new IllegalStateException(
                            "A review requires at least one commit"
                    ));

            if (!review.commitSha().equals(currentSha)) {
                throw new IllegalArgumentException(
                        "Review must refer to the latest commit"
                );
            }

            if (!review.eligible()) {
                throw new IllegalArgumentException(
                        "Reviewer is not eligible to approve this change"
                );
            }

            // The latest active decision by a reviewer replaces the earlier one.
            for (int index = 0; index < reviews.size(); index++) {
                Review existing = reviews.get(index);

                if (existing.reviewer().equals(review.reviewer()) &&
                        !existing.dismissed()) {
                    reviews.set(index, existing.dismiss());
                }
            }

            reviews.add(review);
        }

        void setCheck(String name, CheckState state) {
            requireOpen();

            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Check name is required");
            }

            checks.put(name, Objects.requireNonNull(state, "state"));
        }

        void addConversation(String id) {
            requireOpen();

            if (conversations.containsKey(id)) {
                throw new IllegalArgumentException("Duplicate conversation ID");
            }

            conversations.put(id, new Conversation(id, false));
        }

        void resolveConversation(String id) {
            requireOpen();

            Conversation conversation = Optional.ofNullable(
                    conversations.get(id)
            ).orElseThrow(() -> new IllegalArgumentException(
                    "Unknown conversation: " + id
            ));

            conversations.put(id, conversation.resolve());
        }

        private void requireOpen() {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException(
                        "Operation requires an open Pull Request"
                );
            }
        }

        private Optional<String> latestCommit() {
            return commits.isEmpty()
                    ? Optional.empty()
                    : Optional.of(commits.get(commits.size() - 1).sha());
        }
    }

    static final class MergeEligibilityService {
        MergeEvaluation evaluate(
                PullRequest pullRequest,
                BranchProtection policy
        ) {
            Objects.requireNonNull(pullRequest, "pullRequest");
            Objects.requireNonNull(policy, "policy");

            List<String> blockers = new ArrayList<>();
            List<Commit> commits = pullRequest.commits();

            if (pullRequest.state() != PullRequestState.OPEN) {
                blockers.add("Pull Request is not open");
            }

            if (commits.isEmpty()) {
                blockers.add("No commits are present");
            }

            String latestCommit = commits.isEmpty()
                    ? null
                    : commits.get(commits.size() - 1).sha();

            Map<String, Review> latestByReviewer = new HashMap<>();

            for (Review review : pullRequest.reviews()) {
                if (review.dismissed() || !review.eligible()) {
                    continue;
                }

                if (!Objects.equals(review.commitSha(), latestCommit)) {
                    continue;
                }

                latestByReviewer.put(review.reviewer(), review);
            }

            List<Review> activeReviews = latestByReviewer.values()
                    .stream()
                    .toList();

            boolean changesRequested = activeReviews.stream().anyMatch(
                    review -> review.state() == ReviewState.CHANGES_REQUESTED
            );

            if (changesRequested) {
                blockers.add("A current reviewer has requested changes");
            }

            long approvals = activeReviews.stream()
                    .filter(review -> review.state() == ReviewState.APPROVED)
                    .count();

            if (approvals < policy.requiredApprovals()) {
                blockers.add(
                        "Insufficient approvals: required " +
                        policy.requiredApprovals() + ", received " + approvals
                );
            }

            Map<String, CheckState> checks = pullRequest.checks;

            for (String requiredCheck : policy.requiredChecks()) {
                if (checks.get(requiredCheck) != CheckState.SUCCESS) {
                    blockers.add(
                            "Required check is not successful: " + requiredCheck
                    );
                }
            }

            if (policy.requireConversationResolution()) {
                boolean unresolved = pullRequest.conversations.values()
                        .stream()
                        .anyMatch(conversation -> !conversation.resolved());

                if (unresolved) {
                    blockers.add("Unresolved review discussions remain");
                }
            }

            return new MergeEvaluation(
                    blockers.isEmpty(),
                    (int) approvals,
                    blockers,
                    latestCommit
            );
        }

        void merge(
                PullRequest pullRequest,
                BranchProtection policy,
                String actor,
                MergeStrategy strategy
        ) {
            if (actor == null || actor.isBlank()) {
                throw new IllegalArgumentException("Merge actor is required");
            }

            Objects.requireNonNull(strategy, "strategy");

            MergeEvaluation evaluation = evaluate(pullRequest, policy);

            if (!evaluation.eligible()) {
                throw new IllegalStateException(
                        "Merge blocked: " + String.join("; ", evaluation.blockers())
                );
            }

            pullRequest.state = PullRequestState.MERGED;
            pullRequest.mergedBy = actor;
            pullRequest.mergeStrategy = strategy;
        }
    }

    static final class RepositoryGovernance {
        private final String repositoryName;
        private final BranchProtection protection;
        private final Map<Integer, PullRequest> pullRequests =
                new LinkedHashMap<>();
        private final MergeEligibilityService eligibilityService =
                new MergeEligibilityService();

        RepositoryGovernance(
                String repositoryName,
                BranchProtection protection
        ) {
            if (repositoryName == null || repositoryName.isBlank()) {
                throw new IllegalArgumentException("Repository name is required");
            }

            this.repositoryName = repositoryName;
            this.protection = Objects.requireNonNull(protection, "protection");
        }

        void register(PullRequest pullRequest) {
            if (!pullRequest.targetBranch.equals(protection.branch())) {
                throw new IllegalArgumentException(
                        "Pull Request does not target the protected branch"
                );
            }

            if (pullRequests.putIfAbsent(
                    pullRequest.id(), pullRequest
            ) != null) {
                throw new IllegalArgumentException("Duplicate Pull Request ID");
            }
        }

        PullRequest get(int id) {
            return Optional.ofNullable(pullRequests.get(id))
                    .orElseThrow(() -> new IllegalArgumentException(
                            "Unknown Pull Request ID: " + id
                    ));
        }

        MergeEvaluation evaluate(int id) {
            return eligibilityService.evaluate(get(id), protection);
        }

        void merge(int id, String actor, MergeStrategy strategy) {
            eligibilityService.merge(
                    get(id), protection, actor, strategy
            );
        }

        void attemptDirectPush(String actor, boolean administrator) {
            if (actor == null || actor.isBlank()) {
                throw new IllegalArgumentException("Actor is required");
            }

            if (protection.restrictDirectPushes() &&
                    protection.enforceForAdministrators()) {
                throw new SecurityException(
                        "Direct pushes are prohibited for this protected branch"
                );
            }

            if (protection.restrictDirectPushes() && !administrator) {
                throw new SecurityException(
                        "Direct pushes are restricted to authorized actors"
                );
            }

            if (administrator && !protection.allowBypass()) {
                throw new SecurityException(
                        "Administrator bypass is disabled"
                );
            }
        }

        void attemptForcePush() {
            if (!protection.allowForcePush()) {
                throw new SecurityException(
                        "Force pushes are disabled for " + protection.branch()
                );
            }
        }

        void attemptBranchDeletion() {
            if (!protection.allowDeletion()) {
                throw new SecurityException(
                        "Deletion of the protected branch is disabled"
                );
            }
        }

        String repositoryName() {
            return repositoryName;
        }
    }

    public static void main(String[] args) {
        System.out.println("Enterprise repository governance");

        BranchProtection policy = BranchProtection.builder("main")
                .requiredApprovals(2)
                .requiredChecks(
                        "unit-tests",
                        "security-scan",
                        "lint"
                )
                .dismissStaleReviews(true)
                .requireConversationResolution(true)
                .requireLinearHistory(true)
                .restrictDirectPushes(true)
                .allowForcePush(false)
                .allowDeletion(false)
                .enforceForAdministrators(true)
                .allowBypass(false)
                .build();

        RepositoryGovernance repository = new RepositoryGovernance(
                "payments-platform",
                policy
        );

        PullRequest pullRequest = new PullRequest(
                418,
                "Enforce signed deployment artifacts",
                "feature/signed-artifacts",
                "main",
                Set.of("Maya", "Daniel"),
                false
        );

        repository.register(pullRequest);

        pullRequest.addCommit(
                new Commit(
                        "a1b2c3d",
                        List.of(
                                "src/signature.java",
                                "test/signature-test.java"
                        )
                ),
                policy
        );

        pullRequest.addConversation("security-comment-17");

        pullRequest.submitReview(
                new Review(
                        "Maya",
                        ReviewState.APPROVED,
                        "a1b2c3d",
                        false,
                        true,
                        Instant.now()
                )
        );

        pullRequest.submitReview(
                new Review(
                        "Daniel",
                        ReviewState.APPROVED,
                        "a1b2c3d",
                        false,
                        true,
                        Instant.now()
                )
        );

        pullRequest.setCheck("unit-tests", CheckState.SUCCESS);
        pullRequest.setCheck("security-scan", CheckState.SUCCESS);
        pullRequest.setCheck("lint", CheckState.SUCCESS);

        System.out.println("\nInitial eligibility");
        System.out.println(repository.evaluate(418));

        try {
            repository.merge(418, "release-maintainer", MergeStrategy.SQUASH);
        } catch (IllegalStateException exception) {
            System.out.println("Expected rejection: " + exception.getMessage());
        }

        pullRequest.resolveConversation("security-comment-17");

        // A changed commit requires fresh approval when stale-review dismissal
        // is enabled. The prior approval records remain auditable but inactive.
        pullRequest.addCommit(
                new Commit("b2c3d4e", List.of("src/signature.java")),
                policy
        );

        System.out.println("\nAfter source branch advances");
        System.out.println(repository.evaluate(418));

        pullRequest.submitReview(
                new Review(
                        "Maya",
                        ReviewState.APPROVED,
                        "b2c3d4e",
                        false,
                        true,
                        Instant.now()
                )
        );

        pullRequest.submitReview(
                new Review(
                        "Daniel",
                        ReviewState.APPROVED,
                        "b2c3d4e",
                        false,
                        true,
                        Instant.now()
                )
        );

        MergeEvaluation evaluation = repository.evaluate(418);
        System.out.println("\nAfter current approvals: " + evaluation);

        repository.merge(418, "release-maintainer", MergeStrategy.SQUASH);

        System.out.println(
                "Final state: " + pullRequest.state() +
                ", strategy: " + pullRequest.mergeStrategy +
                ", actor: " + pullRequest.mergedBy
        );

        try {
            repository.attemptDirectPush("administrator", true);
        } catch (SecurityException exception) {
            System.out.println("Protected push rejected: " + exception.getMessage());
        }

        try {
            repository.attemptForcePush();
        } catch (SecurityException exception) {
            System.out.println("Force push rejected: " + exception.getMessage());
        }

        try {
            repository.attemptBranchDeletion();
        } catch (SecurityException exception) {
            System.out.println("Deletion rejected: " + exception.getMessage());
        }

        try {
            BranchProtection.builder("main")
                    .requiredApprovals(-1)
                    .build();
        } catch (IllegalArgumentException exception) {
            System.out.println("Invalid policy rejected: " + exception.getMessage());
        }

        System.out.println(
                "Governance model completed for " + repository.repositoryName()
        );
    }
}
