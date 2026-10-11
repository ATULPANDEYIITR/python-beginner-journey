import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/*
 * Enterprise repository governance using explicit domain types.
 *
 * Compile and run:
 *   javac IntroductionToFunctions.java
 *   java IntroductionToFunctions
 */

public class IntroductionToFunctions {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewDecision {
        APPROVED, CHANGES_REQUESTED, COMMENTED
    }

    enum CheckStatus {
        PENDING, SUCCESS, FAILURE
    }

    record Commit(String sha, String message) {
        Commit {
            if (sha == null || !sha.matches("(?i)[a-f0-9]{7,40}")) {
                throw new IllegalArgumentException("Invalid commit identifier");
            }
            if (message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit message is required");
            }
        }
    }

    record Review(
        String reviewer,
        ReviewDecision decision,
        String commitSha,
        boolean dismissed
    ) {
        Review {
            Objects.requireNonNull(reviewer, "Reviewer is required");
            Objects.requireNonNull(decision, "Decision is required");
            Objects.requireNonNull(commitSha, "Commit reference is required");
            if (reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer cannot be blank");
            }
        }

        Review dismiss() {
            return new Review(reviewer, decision, commitSha, true);
        }
    }

    record ReviewPolicy(
        int requiredApprovals,
        Set<String> eligibleReviewers,
        Set<String> requiredChecks,
        boolean requireLinearHistory,
        boolean requireResolvedConversations
    ) {
        ReviewPolicy {
            if (requiredApprovals < 1) {
                throw new IllegalArgumentException("At least one approval is required");
            }
            eligibleReviewers = Set.copyOf(eligibleReviewers);
            requiredChecks = Set.copyOf(requiredChecks);
            if (eligibleReviewers.isEmpty()) {
                throw new IllegalArgumentException("Eligible reviewer set is empty");
            }
        }
    }

    record MergeEvaluation(boolean eligible, List<String> blockers, int approvals) {
        MergeEvaluation {
            blockers = List.copyOf(blockers);
        }
    }

    static final class PullRequest {
        private final int id;
        private final String author;
        private final String sourceBranch;
        private final String targetBranch;
        private PullRequestState state = PullRequestState.DRAFT;
        private final List<Commit> commits = new ArrayList<>();
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, CheckStatus> checks = new HashMap<>();
        private int unresolvedConversations;
        private boolean baseSynchronized;
        private boolean conflictsPresent;
        private boolean linearHistoryAvailable = true;

        PullRequest(int id, String author, String sourceBranch, String targetBranch) {
            if (id <= 0) {
                throw new IllegalArgumentException("Request ID must be positive");
            }
            if (author == null || author.isBlank()) {
                throw new IllegalArgumentException("Author is required");
            }
            if (sourceBranch == null || targetBranch == null
                || sourceBranch.isBlank() || targetBranch.isBlank()
                || sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException("Distinct source and target branches are required");
            }

            this.id = id;
            this.author = author;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
        }

        void addCommit(Commit commit) {
            requireMutable();
            commits.add(Objects.requireNonNull(commit));

            // Reviews remain in the audit history, but the evaluator compares
            // their commit reference with the new head to detect stale approval.
        }

        void open() {
            if (state != PullRequestState.DRAFT && state != PullRequestState.CLOSED) {
                throw new IllegalStateException("Only drafts or closed requests can be opened");
            }
            if (commits.isEmpty()) {
                throw new IllegalStateException("Cannot open a request without commits");
            }
            state = PullRequestState.OPEN;
        }

        void transitionToDraft() {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Only open requests can become drafts");
            }
            state = PullRequestState.DRAFT;
        }

        void close() {
            if (state != PullRequestState.OPEN && state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Request cannot be closed from its current state");
            }
            state = PullRequestState.CLOSED;
        }

        void submitReview(String reviewer, ReviewDecision decision, ReviewPolicy policy) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Reviews require an open request");
            }
            if (reviewer == null || reviewer.isBlank() || reviewer.equals(author)) {
                throw new IllegalArgumentException("Reviewer must be distinct from the author");
            }
            if (!policy.eligibleReviewers().contains(reviewer)) {
                throw new IllegalArgumentException("Reviewer is not eligible");
            }
            if (commits.isEmpty()) {
                throw new IllegalStateException("No changes are available to review");
            }

            reviews.add(new Review(
                reviewer,
                decision,
                commits.get(commits.size() - 1).sha(),
                false
            ));
        }

        void dismissLatestReview(String reviewer) {
            for (int i = reviews.size() - 1; i >= 0; i--) {
                Review review = reviews.get(i);
                if (review.reviewer().equals(reviewer) && !review.dismissed()) {
                    reviews.set(i, review.dismiss());
                    return;
                }
            }
            throw new IllegalArgumentException("No active review found for reviewer");
        }

        void updateCheck(String name, CheckStatus status) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Check name is required");
            }
            checks.put(name, Objects.requireNonNull(status));
        }

        void synchronizeWithBase(boolean conflicts, boolean linearHistoryAvailable) {
            this.baseSynchronized = !conflicts;
            this.conflictsPresent = conflicts;
            this.linearHistoryAvailable = linearHistoryAvailable;
        }

        void setUnresolvedConversations(int count) {
            if (count < 0) {
                throw new IllegalArgumentException("Conversation count cannot be negative");
            }
            unresolvedConversations = count;
        }

        private void requireMutable() {
            if (state == PullRequestState.MERGED || state == PullRequestState.CLOSED) {
                throw new IllegalStateException("Request is not mutable in its current state");
            }
        }

        private String headSha() {
            return commits.isEmpty() ? "" : commits.get(commits.size() - 1).sha();
        }
    }

    static final class MergeEligibilityService {
        MergeEvaluation evaluate(PullRequest request, ReviewPolicy policy) {
            List<String> blockers = new ArrayList<>();

            if (request.state != PullRequestState.OPEN) {
                blockers.add("Request must be open");
            }
            if (request.commits.isEmpty()) {
                blockers.add("At least one commit is required");
            }
            if (request.conflictsPresent || !request.baseSynchronized) {
                blockers.add("Source branch must be synchronized and conflict-free");
            }
            if (policy.requireLinearHistory() && !request.linearHistoryAvailable) {
                blockers.add("Linear history requirement is not satisfied");
            }
            if (policy.requireResolvedConversations()
                && request.unresolvedConversations > 0) {
                blockers.add("Review conversations must be resolved");
            }

            // Only the latest non-dismissed review per reviewer determines the
            // current decision. A later review replaces that reviewer's older state.
            Map<String, Review> latestByReviewer = new HashMap<>();
            for (Review review : request.reviews) {
                if (!review.dismissed()) {
                    latestByReviewer.put(review.reviewer(), review);
                }
            }

            int approvals = 0;
            boolean changesRequested = false;
            String head = request.headSha();

            for (Review review : latestByReviewer.values()) {
                if (!review.commitSha().equals(head)) {
                    continue;
                }
                if (review.reviewer().equals(request.author)) {
                    continue;
                }
                if (!policy.eligibleReviewers().contains(review.reviewer())) {
                    continue;
                }

                if (review.decision() == ReviewDecision.APPROVED) {
                    approvals++;
                } else if (review.decision() == ReviewDecision.CHANGES_REQUESTED) {
                    changesRequested = true;
                }
            }

            if (approvals < policy.requiredApprovals()) {
                blockers.add("Current approvals: " + approvals
                    + "/" + policy.requiredApprovals());
            }
            if (changesRequested) {
                blockers.add("A current review requests changes");
            }

            for (String required : policy.requiredChecks()) {
                if (request.checks.get(required) != CheckStatus.SUCCESS) {
                    blockers.add("Required check is not successful: " + required);
                }
            }

            return new MergeEvaluation(blockers.isEmpty(), blockers, approvals);
        }

        void merge(PullRequest request, ReviewPolicy policy) {
            MergeEvaluation evaluation = evaluate(request, policy);
            if (!evaluation.eligible()) {
                throw new IllegalStateException(
                    "Merge blocked: " + String.join("; ", evaluation.blockers())
                );
            }
            request.state = PullRequestState.MERGED;
        }
    }

    public static void main(String[] args) {
        ReviewPolicy policy = new ReviewPolicy(
            2,
            Set.of("reviewer-alex", "reviewer-priya", "reviewer-sam"),
            Set.of("unit-tests", "security-scan"),
            true,
            true
        );

        PullRequest request = new PullRequest(
            205,
            "feature-author",
            "feature/payment-validation",
            "main"
        );

        request.addCommit(new Commit("a1b2c3d", "Validate payment boundaries"));
        request.open();

        request.submitReview("reviewer-alex", ReviewDecision.APPROVED, policy);
        request.submitReview("reviewer-priya", ReviewDecision.APPROVED, policy);

        request.updateCheck("unit-tests", CheckStatus.SUCCESS);
        request.updateCheck("security-scan", CheckStatus.PENDING);
        request.synchronizeWithBase(false, true);
        request.setUnresolvedConversations(1);

        MergeEligibilityService service = new MergeEligibilityService();

        System.out.println("Initial eligibility:");
        printEvaluation(service.evaluate(request, policy));

        request.updateCheck("security-scan", CheckStatus.SUCCESS);
        request.setUnresolvedConversations(0);

        System.out.println("\nEligibility after checks and discussions are complete:");
        printEvaluation(service.evaluate(request, policy));

        service.merge(request, policy);
        System.out.println("Request state after merge: " + request.state);

        System.out.println("\nStale approval example:");
        PullRequest stale = new PullRequest(
            206,
            "feature-author",
            "feature/audit-logging",
            "main"
        );
        stale.addCommit(new Commit("111aaaa", "Add audit logging"));
        stale.open();
        stale.submitReview("reviewer-alex", ReviewDecision.APPROVED, policy);
        stale.submitReview("reviewer-priya", ReviewDecision.APPROVED, policy);
        stale.addCommit(new Commit("222bbbb", "Correct audit event ordering"));
        stale.synchronizeWithBase(false, true);
        stale.updateCheck("unit-tests", CheckStatus.SUCCESS);
        stale.updateCheck("security-scan", CheckStatus.SUCCESS);
        printEvaluation(service.evaluate(stale, policy));

        System.out.println("\nInvalid reviewer example:");
        try {
            stale.submitReview("feature-author", ReviewDecision.APPROVED, policy);
        } catch (IllegalArgumentException | IllegalStateException exception) {
            System.out.println("Review rejected: " + exception.getMessage());
        }
    }

    private static void printEvaluation(MergeEvaluation evaluation) {
        System.out.println("Eligible: " + evaluation.eligible());
        System.out.println("Current approvals: " + evaluation.approvals());
        for (String blocker : evaluation.blockers()) {
            System.out.println("Blocked by: " + blocker);
        }
    }
}
