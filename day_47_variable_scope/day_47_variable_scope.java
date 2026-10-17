import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

public class VariableScopeEnterprise {
    enum ReviewState {
        PENDING, APPROVED, CHANGES_REQUESTED, DISMISSED
    }

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    record InlineComment(String path, int line, String body) {
        InlineComment {
            if (path == null || path.isBlank() || line < 1
                    || body == null || body.isBlank()) {
                throw new IllegalArgumentException("Invalid inline comment");
            }
        }
    }

    record Commit(String id, String message) {
        Commit {
            if (id == null || id.isBlank() || message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit identity and message are required");
            }
        }
    }

    static final class Review {
        private final String reviewer;
        private final String reviewedCommit;
        private ReviewState state;
        private final List<InlineComment> comments = new ArrayList<>();

        Review(String reviewer, String reviewedCommit) {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer identity is required");
            }
            this.reviewer = reviewer;
            this.reviewedCommit = Objects.requireNonNull(reviewedCommit);
            this.state = ReviewState.PENDING;
        }

        void addComment(InlineComment comment) {
            comments.add(Objects.requireNonNull(comment));
        }

        void transition(ReviewState next) {
            boolean allowed = switch (state) {
                case PENDING -> next == ReviewState.APPROVED
                        || next == ReviewState.CHANGES_REQUESTED;
                case APPROVED -> next == ReviewState.DISMISSED;
                case CHANGES_REQUESTED -> next == ReviewState.DISMISSED;
                case DISMISSED -> false;
            };

            if (!allowed) {
                throw new IllegalStateException(
                        "Invalid review transition: " + state + " -> " + next);
            }
            state = next;
        }

        String reviewer() {
            return reviewer;
        }

        ReviewState state() {
            return state;
        }

        String reviewedCommit() {
            return reviewedCommit;
        }

        List<InlineComment> comments() {
            return List.copyOf(comments);
        }
    }

    static final class PullRequest {
        private final int id;
        private final String author;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<Commit> commits = new ArrayList<>();
        private final Map<String, Review> latestReviews = new HashMap<>();
        private final Map<String, Boolean> checks = new HashMap<>();
        private PullRequestState state = PullRequestState.OPEN;
        private boolean staleApprovals;
        private boolean unresolvedConversations;

        PullRequest(int id, String author, String sourceBranch, String targetBranch) {
            if (id <= 0 || author == null || author.isBlank()
                    || sourceBranch == null || sourceBranch.isBlank()
                    || targetBranch == null || targetBranch.isBlank()) {
                throw new IllegalArgumentException("Invalid pull request metadata");
            }
            this.id = id;
            this.author = author;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
        }

        void addCommit(Commit commit) {
            requireOpen();
            commits.add(Objects.requireNonNull(commit));
            staleApprovals = true;
        }

        void synchronizeWithBase(String newBaseCommit) {
            requireOpen();
            if (newBaseCommit == null || newBaseCommit.isBlank()) {
                throw new IllegalArgumentException("Base commit is required");
            }
            // Synchronization may change the effective diff and invalidate approvals.
            staleApprovals = true;
        }

        void addReview(Review review) {
            requireOpen();
            if (review.reviewer().equals(author)) {
                throw new IllegalArgumentException("Authors cannot approve their own changes");
            }
            latestReviews.put(review.reviewer(), review);
        }

        void setCheck(String name, boolean passed) {
            requireOpen();
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Check name is required");
            }
            checks.put(name, passed);
        }

        void setUnresolvedConversations(boolean unresolved) {
            requireOpen();
            unresolvedConversations = unresolved;
        }

        void close() {
            requireOpen();
            state = PullRequestState.CLOSED;
        }

        void reopen() {
            if (state != PullRequestState.CLOSED) {
                throw new IllegalStateException("Only a closed request can be reopened");
            }
            state = PullRequestState.OPEN;
        }

        void markMerged() {
            requireOpen();
            state = PullRequestState.MERGED;
        }

        private void requireOpen() {
            if (state != PullRequestState.OPEN && state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Pull request is not editable");
            }
        }

        int id() {
            return id;
        }

        String author() {
            return author;
        }

        String targetBranch() {
            return targetBranch;
        }

        List<Commit> commits() {
            return List.copyOf(commits);
        }

        Map<String, Review> reviews() {
            return Map.copyOf(latestReviews);
        }

        Map<String, Boolean> checks() {
            return Map.copyOf(checks);
        }

        boolean staleApprovals() {
            return staleApprovals;
        }

        boolean unresolvedConversations() {
            return unresolvedConversations;
        }

        PullRequestState state() {
            return state;
        }
    }

    record BranchProtection(
            String branch,
            int requiredApprovals,
            Set<String> requiredChecks,
            boolean requireResolvedConversations,
            boolean dismissStaleApprovals,
            boolean restrictDirectPushes,
            boolean blockForcePushes,
            boolean blockDeletion,
            boolean requireLinearHistory,
            boolean administratorBypassAllowed) {

        BranchProtection {
            if (branch == null || branch.isBlank() || requiredApprovals < 0) {
                throw new IllegalArgumentException("Invalid branch protection policy");
            }
            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    record MergeDecision(boolean eligible, List<String> failures) {
        MergeDecision {
            failures = List.copyOf(failures);
        }
    }

    static final class MergeEligibilityService {
        private final BranchProtection protection;

        MergeEligibilityService(BranchProtection protection) {
            this.protection = Objects.requireNonNull(protection);
        }

        MergeDecision evaluate(PullRequest request) {
            List<String> failures = new ArrayList<>();

            if (request.state() != PullRequestState.OPEN) {
                failures.add("Pull request is not open");
            }

            if (!request.targetBranch().equals(protection.branch())) {
                failures.add("Target branch does not match protected branch");
            }

            if (request.commits().isEmpty()) {
                failures.add("Pull request contains no commits");
            }

            Set<String> eligibleApprovers = request.reviews().values().stream()
                    .filter(review -> review.state() == ReviewState.APPROVED)
                    .filter(review -> !review.reviewer().equals(request.author()))
                    .filter(review -> !protection.dismissStaleApprovals()
                            || !request.staleApprovals())
                    .map(Review::reviewer)
                    .collect(Collectors.toCollection(HashSet::new));

            if (eligibleApprovers.size() < protection.requiredApprovals()) {
                failures.add("Insufficient current, distinct approvals");
            }

            for (String checkName : protection.requiredChecks()) {
                Boolean passed = request.checks().get(checkName);
                if (passed == null) {
                    failures.add("Missing required check: " + checkName);
                } else if (!passed) {
                    failures.add("Failed required check: " + checkName);
                }
            }

            if (protection.requireResolvedConversations()
                    && request.unresolvedConversations()) {
                failures.add("Review conversations remain unresolved");
            }

            if (protection.requireLinearHistory()
                    && !Boolean.TRUE.equals(request.checks().get("linear-history"))) {
                failures.add("Linear history is not verified");
            }

            return new MergeDecision(failures.isEmpty(), failures);
        }

        void merge(PullRequest request) {
            MergeDecision decision = evaluate(request);
            if (!decision.eligible()) {
                throw new IllegalStateException(
                        "Merge blocked for PR #" + request.id() + ": "
                                + String.join("; ", decision.failures()));
            }
            request.markMerged();
        }

        boolean directPushAllowed(boolean administrator) {
            return !protection.restrictDirectPushes()
                    || (administrator && protection.administratorBypassAllowed());
        }

        boolean forcePushAllowed(boolean administrator) {
            return !protection.blockForcePushes()
                    || (administrator && protection.administratorBypassAllowed());
        }

        boolean branchDeletionAllowed(boolean administrator) {
            return !protection.blockDeletion()
                    || (administrator && protection.administratorBypassAllowed());
        }
    }

    public static void main(String[] args) {
        BranchProtection policy = new BranchProtection(
                "main",
                2,
                Set.of("unit-tests", "security-scan", "linear-history"),
                true,
                true,
                true,
                true,
                true,
                true,
                false
        );

        MergeEligibilityService service = new MergeEligibilityService(policy);

        PullRequest request = new PullRequest(
                412, "developer-mira", "feature/token-validation", "main");

        request.addCommit(new Commit("c401", "Validate token audience"));
        request.addCommit(new Commit("c402", "Reject expired credentials"));

        Review securityReview = new Review("reviewer-ada", "c402");
        securityReview.addComment(new InlineComment(
                "src/auth/TokenValidator.java",
                74,
                "Reject a missing audience before signature acceptance."));
        securityReview.transition(ReviewState.APPROVED);
        request.addReview(securityReview);

        Review reliabilityReview = new Review("reviewer-lin", "c402");
        reliabilityReview.transition(ReviewState.APPROVED);
        request.addReview(reliabilityReview);

        request.setCheck("unit-tests", true);
        request.setCheck("security-scan", true);
        request.setCheck("linear-history", true);
        request.setUnresolvedConversations(false);

        // Adding commits marks approvals stale; explicit policy evaluation
        // prevents a previously accepted review from silently authorizing new code.
        System.out.println("Eligible before synchronization: "
                + service.evaluate(request).eligible());

        request.synchronizeWithBase("base-commit-900");
        MergeDecision blocked = service.evaluate(request);
        System.out.println("Eligible after synchronization: " + blocked.eligible());
        blocked.failures().forEach(System.out::println);

        request.close();
        request.reopen();

        // Re-review the updated changeset.
        Review refreshedAda = new Review("reviewer-ada", "c402");
        refreshedAda.transition(ReviewState.APPROVED);
        request.addReview(refreshedAda);

        Review refreshedLin = new Review("reviewer-lin", "c402");
        refreshedLin.transition(ReviewState.APPROVED);
        request.addReview(refreshedLin);

        // In a real service, review commit IDs must match the latest head commit.
        // This model demonstrates the explicit stale-approval flag separately.
        try {
            service.merge(request);
            System.out.println("Merged PR #" + request.id());
        } catch (IllegalStateException exception) {
            System.out.println("Merge rejected: " + exception.getMessage());
        }

        System.out.println("Contributor direct push permitted: "
                + service.directPushAllowed(false));
        System.out.println("Administrator bypass permitted: "
                + service.forcePushAllowed(true));
    }
}
