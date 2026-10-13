import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * Enterprise repository governance model.
 *
 * Compile:
 *   javac ReturnValuesGovernance.java
 *
 * Run:
 *   java ReturnValuesGovernance
 *
 * The domain model distinguishes:
 * Pull Request state transitions, code review findings, approval policy,
 * and protected-branch merge enforcement.
 */

public class ReturnValuesGovernance {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        COMMENTED, CHANGES_REQUESTED, APPROVED, DISMISSED
    }

    enum MergeStrategy {
        MERGE_COMMIT, SQUASH, REBASE
    }

    enum CheckState {
        PENDING, PASSED, FAILED
    }

    record Commit(String id, String message, Instant createdAt) {
        Commit {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Commit ID is required.");
            }
            if (message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit message is required.");
            }
            Objects.requireNonNull(createdAt, "Commit timestamp is required.");
        }
    }

    record ReviewComment(
        String filePath,
        int line,
        String body,
        boolean resolved
    ) {
        ReviewComment {
            if (filePath == null || filePath.isBlank()) {
                throw new IllegalArgumentException("File path is required.");
            }
            if (line < 1) {
                throw new IllegalArgumentException("Line must be positive.");
            }
            if (body == null || body.isBlank()) {
                throw new IllegalArgumentException("Comment body is required.");
            }
        }

        ReviewComment resolve() {
            return new ReviewComment(filePath, line, body, true);
        }
    }

    record Review(
        String reviewer,
        ReviewState state,
        String commitId,
        List<ReviewComment> comments,
        Instant submittedAt
    ) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            Objects.requireNonNull(state);
            if (commitId == null || commitId.isBlank()) {
                throw new IllegalArgumentException("Reviewed commit is required.");
            }
            comments = List.copyOf(comments);
            Objects.requireNonNull(submittedAt);
        }
    }

    record MergeDecision(
        boolean eligible,
        List<String> blockers,
        Set<String> effectiveApprovers
    ) {
        MergeDecision {
            blockers = List.copyOf(blockers);
            effectiveApprovers = Set.copyOf(effectiveApprovers);
        }
    }

    record OperationResult<T>(
        boolean successful,
        T value,
        String error
    ) {
        OperationResult {
            if (successful && error != null) {
                throw new IllegalArgumentException(
                    "Successful results cannot contain an error."
                );
            }
            if (!successful && (error == null || error.isBlank())) {
                throw new IllegalArgumentException(
                    "Failed results require an error."
                );
            }
        }

        static <T> OperationResult<T> success(T value) {
            return new OperationResult<>(true, value, null);
        }

        static <T> OperationResult<T> failure(String error) {
            return new OperationResult<>(false, null, error);
        }

        Optional<T> optionalValue() {
            return Optional.ofNullable(value);
        }
    }

    static final class Branch {
        private final String name;
        private final boolean protectedBranch;
        private final boolean linearHistory;
        private final List<Commit> commits = new ArrayList<>();

        Branch(String name, boolean protectedBranch, boolean linearHistory) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Branch name is required.");
            }
            this.name = name;
            this.protectedBranch = protectedBranch;
            this.linearHistory = linearHistory;
        }

        void addCommit(Commit commit) {
            Objects.requireNonNull(commit);
            if (commits.stream().anyMatch(existing ->
                existing.id().equals(commit.id()))) {
                throw new IllegalArgumentException("Duplicate commit ID.");
            }
            commits.add(commit);
        }

        String head() {
            if (commits.isEmpty()) {
                return "";
            }
            return commits.get(commits.size() - 1).id();
        }

        String name() {
            return name;
        }

        boolean protectedBranch() {
            return protectedBranch;
        }

        boolean linearHistory() {
            return linearHistory;
        }

        List<Commit> commits() {
            return List.copyOf(commits);
        }
    }

    static final class BranchProtectionPolicy {
        private final int requiredApprovals;
        private final Set<String> requiredChecks;
        private final boolean requireResolvedConversations;
        private final boolean requireLinearHistory;
        private final boolean dismissStaleApprovals;
        private final boolean requireCodeOwnerApproval;
        private final Set<String> codeOwners;
        private final Set<String> bypassActors;

        BranchProtectionPolicy(
            int requiredApprovals,
            Set<String> requiredChecks,
            boolean requireResolvedConversations,
            boolean requireLinearHistory,
            boolean dismissStaleApprovals,
            boolean requireCodeOwnerApproval,
            Set<String> codeOwners,
            Set<String> bypassActors
        ) {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Required approvals cannot be negative."
                );
            }
            this.requiredApprovals = requiredApprovals;
            this.requiredChecks = Set.copyOf(requiredChecks);
            this.requireResolvedConversations = requireResolvedConversations;
            this.requireLinearHistory = requireLinearHistory;
            this.dismissStaleApprovals = dismissStaleApprovals;
            this.requireCodeOwnerApproval = requireCodeOwnerApproval;
            this.codeOwners = Set.copyOf(codeOwners);
            this.bypassActors = Set.copyOf(bypassActors);
        }
    }

    static final class PullRequest {
        private final String id;
        private final String author;
        private final Branch source;
        private final Branch target;
        private final BranchProtectionPolicy policy;

        private PullRequestState state;
        private final Set<String> requestedReviewers = new HashSet<>();
        private final Map<String, Review> latestReviews = new LinkedHashMap<>();
        private final Map<String, CheckState> checks = new HashMap<>();
        private final List<String> conversations = new ArrayList<>();
        private final Set<Integer> resolvedConversations = new HashSet<>();

        private String synchronizedTargetHead;
        private boolean baseSynchronized = true;
        private MergeStrategy mergeStrategy;

        PullRequest(
            String id,
            String author,
            Branch source,
            Branch target,
            BranchProtectionPolicy policy,
            boolean draft
        ) {
            if (id == null || id.isBlank() ||
                author == null || author.isBlank()) {
                throw new IllegalArgumentException("ID and author are required.");
            }
            this.id = id;
            this.author = author;
            this.source = Objects.requireNonNull(source);
            this.target = Objects.requireNonNull(target);
            this.policy = Objects.requireNonNull(policy);

            if (source.name().equals(target.name())) {
                throw new IllegalArgumentException("Branches must differ.");
            }
            if (source.commits().isEmpty()) {
                throw new IllegalArgumentException("Source branch has no commits.");
            }

            this.state = draft ? PullRequestState.DRAFT : PullRequestState.OPEN;
            this.synchronizedTargetHead = target.head();
        }

        void requestReview(String reviewer) {
            requireActive();
            if (reviewer == null || reviewer.isBlank() || reviewer.equals(author)) {
                throw new IllegalArgumentException(
                    "Reviewer must be a different, non-empty identity."
                );
            }
            requestedReviewers.add(reviewer);
        }

        OperationResult<Review> submitReview(
            String reviewer,
            ReviewState reviewState,
            List<ReviewComment> comments
        ) {
            requireActive();

            if (reviewer.equals(author)) {
                return OperationResult.failure("Self-review is prohibited.");
            }
            if (!requestedReviewers.contains(reviewer)) {
                return OperationResult.failure("Reviewer was not requested.");
            }
            if (reviewState == ReviewState.DISMISSED) {
                return OperationResult.failure(
                    "Dismissal must use the administrative operation."
                );
            }

            Review review = new Review(
                reviewer,
                reviewState,
                source.head(),
                comments,
                Instant.now()
            );

            // One current review per reviewer makes approval replacement
            // explicit instead of counting every historical approval.
            latestReviews.put(reviewer, review);
            return OperationResult.success(review);
        }

        void dismissApproval(String reviewer) {
            requireActive();
            Review existing = latestReviews.get(reviewer);
            if (existing == null || existing.state() != ReviewState.APPROVED) {
                throw new IllegalStateException("No active approval to dismiss.");
            }

            latestReviews.put(reviewer, new Review(
                existing.reviewer(),
                ReviewState.DISMISSED,
                existing.commitId(),
                existing.comments(),
                Instant.now()
            ));
        }

        void addConversation(String topic) {
            requireActive();
            if (topic == null || topic.isBlank()) {
                throw new IllegalArgumentException("Conversation topic is required.");
            }
            conversations.add(topic);
        }

        OperationResult<Boolean> resolveConversation(int index) {
            requireActive();
            if (index < 0 || index >= conversations.size()) {
                return OperationResult.failure("Conversation does not exist.");
            }
            resolvedConversations.add(index);
            return OperationResult.success(true);
        }

        void setCheck(String name, CheckState state) {
            requireActive();
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Check name is required.");
            }
            checks.put(name, Objects.requireNonNull(state));
        }

        void publishDraft() {
            if (state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Request is not a draft.");
            }
            state = PullRequestState.OPEN;
        }

        void synchronizeBase() {
            requireActive();
            synchronizedTargetHead = target.head();
            baseSynchronized = true;
        }

        void detectTargetChange() {
            requireActive();
            if (!target.head().equals(synchronizedTargetHead)) {
                baseSynchronized = false;
            }
        }

        MergeDecision evaluateMergeEligibility() {
            List<String> blockers = new ArrayList<>();
            Set<String> approvers = latestReviews.values().stream()
                .filter(review -> review.state() == ReviewState.APPROVED)
                .filter(review -> !review.reviewer().equals(author))
                .filter(review -> !policy.dismissStaleApprovals ||
                    review.commitId().equals(source.head()))
                .map(Review::reviewer)
                .collect(Collectors.toSet());

            if (state != PullRequestState.OPEN) {
                blockers.add("Request must be open and published.");
            }
            if (!baseSynchronized) {
                blockers.add("Target branch changed; synchronize the base.");
            }

            for (String requiredCheck : policy.requiredChecks) {
                if (checks.get(requiredCheck) != CheckState.PASSED) {
                    blockers.add("Required check is not passing: " + requiredCheck);
                }
            }

            if (approvers.size() < policy.requiredApprovals) {
                blockers.add("Insufficient effective approvals.");
            }

            if (policy.requireCodeOwnerApproval &&
                approvers.stream().noneMatch(policy.codeOwners::contains)) {
                blockers.add("Code-owner approval is missing.");
            }

            if (policy.requireResolvedConversations &&
                resolvedConversations.size() != conversations.size()) {
                blockers.add("Review conversations remain unresolved.");
            }

            if (policy.requireLinearHistory &&
                (!source.linearHistory() || !target.linearHistory())) {
                blockers.add("Linear history is required.");
            }

            return new MergeDecision(
                blockers.isEmpty(), blockers, approvers
            );
        }

        OperationResult<Commit> merge(String actor, MergeStrategy strategy) {
            if (state != PullRequestState.OPEN) {
                return OperationResult.failure("Only open requests can merge.");
            }

            MergeDecision decision = evaluateMergeEligibility();
            if (!decision.eligible()) {
                return OperationResult.failure(
                    String.join("; ", decision.blockers())
                );
            }

            this.mergeStrategy = Objects.requireNonNull(strategy);

            String message = switch (strategy) {
                case MERGE_COMMIT -> "Merge " + id;
                case SQUASH -> "Squash " + id;
                case REBASE -> "Rebase " + id;
            };

            Commit mergeCommit = new Commit(
                UUID.randomUUID().toString(),
                message + " by " + actor,
                Instant.now()
            );

            target.addCommit(mergeCommit);
            state = PullRequestState.MERGED;
            return OperationResult.success(mergeCommit);
        }

        void close() {
            requireActive();
            state = PullRequestState.CLOSED;
        }

        void reopen() {
            if (state != PullRequestState.CLOSED) {
                throw new IllegalStateException("Only closed requests can reopen.");
            }
            state = PullRequestState.OPEN;
            detectTargetChange();
        }

        private void requireActive() {
            if (state != PullRequestState.OPEN &&
                state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Request is no longer active.");
            }
        }

        PullRequestState state() {
            return state;
        }

        Optional<MergeStrategy> mergeStrategy() {
            return Optional.ofNullable(mergeStrategy);
        }
    }

    public static void main(String[] args) {
        Branch feature = new Branch("feature/policy-audit", false, true);
        feature.addCommit(new Commit(
            "c-501", "Add policy audit events", Instant.now()
        ));

        Branch main = new Branch("main", true, true);
        main.addCommit(new Commit(
            "c-500", "Initialize service", Instant.now()
        ));

        BranchProtectionPolicy policy = new BranchProtectionPolicy(
            2,
            Set.of("unit-tests", "security-scan"),
            true,
            true,
            true,
            true,
            Set.of("security-reviewer"),
            Set.of("release-admin")
        );

        PullRequest request = new PullRequest(
            "PR-501", "developer-1", feature, main, policy, true
        );

        request.requestReview("reviewer-2");
        request.requestReview("security-reviewer");
        request.addConversation("Verify actor identity in audit records.");

        System.out.println("Published before merge: " + request.state());
        request.publishDraft();

        request.submitReview("reviewer-2", ReviewState.APPROVED, List.of());
        request.submitReview(
            "security-reviewer",
            ReviewState.APPROVED,
            List.of(new ReviewComment(
                "src/AuditService.java", 73,
                "Preserve the initiating user's identity.", false
            ))
        );

        request.setCheck("unit-tests", CheckState.PASSED);
        request.setCheck("security-scan", CheckState.PASSED);

        System.out.println("Initial decision: " +
            request.evaluateMergeEligibility());

        request.resolveConversation(0);
        System.out.println("After discussion resolution: " +
            request.evaluateMergeEligibility());

        // A new commit makes revision-specific approvals stale.
        feature.addCommit(new Commit(
            "c-502", "Preserve initiating user identity", Instant.now()
        ));

        System.out.println("After source update: " +
            request.evaluateMergeEligibility());

        request.submitReview("reviewer-2", ReviewState.APPROVED, List.of());
        request.submitReview(
            "security-reviewer", ReviewState.APPROVED, List.of()
        );

        OperationResult<Commit> merge = request.merge(
            "release-manager", MergeStrategy.SQUASH
        );

        if (merge.successful()) {
            System.out.println("Merged commit: " + merge.value().id());
            System.out.println("Target head: " + main.head());
        } else {
            System.out.println("Merge blocked: " + merge.error());
        }

        OperationResult<String> emptyString =
            OperationResult.success("");

        System.out.println("Empty string is a successful value: " +
            emptyString.successful());

        OperationResult<String> failed =
            OperationResult.failure("Repository policy rejected the change.");

        System.out.println("Failure value is absent: " +
            failed.optionalValue().isEmpty());

        Map<ReviewState, Integer> reviewCounts =
            new EnumMap<>(ReviewState.class);

        for (ReviewState reviewState : ReviewState.values()) {
            reviewCounts.put(reviewState, 0);
        }

        reviewCounts.put(ReviewState.APPROVED, 2);
        reviewCounts.put(ReviewState.COMMENTED, 0);

        System.out.println("Review-state counts: " +
            Collections.unmodifiableMap(reviewCounts));
    }
}
