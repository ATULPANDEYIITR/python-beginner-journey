import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class RepositoryGovernance {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        COMMENTED, CHANGES_REQUESTED, APPROVED, DISMISSED
    }

    record Commit(String sha, String message) {
        public Commit {
            if (sha == null || sha.isBlank()) {
                throw new IllegalArgumentException("Commit SHA is required");
            }
            if (message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit message is required");
            }
        }
    }

    record Review(
        String reviewer,
        ReviewState state,
        String commitSha
    ) {
        public Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required");
            }
            if (commitSha == null || commitSha.isBlank()) {
                throw new IllegalArgumentException("Review commit SHA is required");
            }
        }
    }

    record BranchProtection(
        String protectedBranch,
        int requiredApprovals,
        Set<String> requiredChecks,
        boolean requireConversationResolution,
        boolean requireLinearHistory,
        boolean allowDirectPush
    ) {
        public BranchProtection {
            if (protectedBranch == null || protectedBranch.isBlank()) {
                throw new IllegalArgumentException("Protected branch is required");
            }
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Required approvals cannot be negative"
                );
            }

            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    static final class PullRequest {
        private final int number;
        private final String title;
        private final String sourceBranch;
        private final String targetBranch;
        private PullRequestState state;
        private final List<Commit> commits;
        private final Set<String> eligibleReviewers;
        private final List<Review> reviews;
        private final Map<String, Boolean> statusChecks;
        private int unresolvedConversations;

        PullRequest(
            int number,
            String title,
            String sourceBranch,
            String targetBranch,
            PullRequestState state,
            List<Commit> commits,
            Set<String> eligibleReviewers,
            List<Review> reviews,
            Map<String, Boolean> statusChecks,
            int unresolvedConversations
        ) {
            if (number <= 0) {
                throw new IllegalArgumentException("Invalid Pull Request number");
            }
            if (title == null || title.isBlank()) {
                throw new IllegalArgumentException("Pull Request title is required");
            }

            this.number = number;
            this.title = title;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.state = state;
            this.commits = new ArrayList<>(commits);
            this.eligibleReviewers = new HashSet<>(eligibleReviewers);
            this.reviews = new ArrayList<>(reviews);
            this.statusChecks = Map.copyOf(statusChecks);
            this.unresolvedConversations = unresolvedConversations;
        }

        String latestCommitSha() {
            if (commits.isEmpty()) {
                return null;
            }
            return commits.get(commits.size() - 1).sha();
        }

        void addCommit(Commit commit) {
            commits.add(commit);
        }

        void addReview(Review review) {
            reviews.add(review);
        }

        void setState(PullRequestState state) {
            this.state = state;
        }
    }

    @FunctionalInterface
    interface PolicyCheck {
        String evaluate(PullRequest pullRequest);
    }

    static final class MergeEligibilityService {
        private final BranchProtection protection;

        MergeEligibilityService(BranchProtection protection) {
            this.protection = protection;
        }

        /*
         * The returned function is a closure over the immutable policy.
         * Separate nested functions keep approval logic independent from
         * branch and status-check validation.
         */
        private PolicyCheck createApprovalPolicy() {
            final BranchProtection policy = protection;

            return pullRequest -> {
                String latestSha = pullRequest.latestCommitSha();

                if (latestSha == null) {
                    return "no commit exists to approve";
                }

                Set<String> currentApprovers = new HashSet<>();

                /*
                 * This nested stream operation expresses the approval rule:
                 * eligibility + approval state + latest commit must all match.
                 */
                pullRequest.reviews.stream()
                    .filter(review ->
                        review.state() == ReviewState.APPROVED)
                    .filter(review ->
                        review.commitSha().equals(latestSha))
                    .filter(review ->
                        pullRequest.eligibleReviewers.contains(
                            review.reviewer()
                        ))
                    .forEach(review ->
                        currentApprovers.add(review.reviewer())
                    );

                if (currentApprovers.size() < policy.requiredApprovals()) {
                    return "required approval threshold is not satisfied";
                }

                return null;
            };
        }

        private PolicyCheck createStatusPolicy() {
            final BranchProtection policy = protection;

            return pullRequest -> {
                for (String requiredCheck : policy.requiredChecks()) {
                    if (!pullRequest.statusChecks.getOrDefault(
                        requiredCheck, false
                    )) {
                        return "required status check failed: " + requiredCheck;
                    }
                }

                return null;
            };
        }

        private PolicyCheck createConversationPolicy() {
            return pullRequest -> {
                if (
                    protection.requireConversationResolution()
                    && pullRequest.unresolvedConversations > 0
                ) {
                    return "review conversations remain unresolved";
                }

                return null;
            };
        }

        List<String> evaluate(PullRequest pullRequest) {
            List<PolicyCheck> checks = List.of(
                createBranchPolicy(),
                createStatusPolicy(),
                createApprovalPolicy(),
                createConversationPolicy(),
                createHistoryPolicy()
            );

            return checks.stream()
                .map(check -> check.evaluate(pullRequest))
                .filter(message -> message != null)
                .toList();
        }

        private PolicyCheck createBranchPolicy() {
            final BranchProtection policy = protection;

            return pullRequest -> {
                if (!pullRequest.targetBranch.equals(
                    policy.protectedBranch()
                )) {
                    return "Pull Request does not target the protected branch";
                }

                if (pullRequest.state != PullRequestState.OPEN) {
                    return "Pull Request must be open";
                }

                if (
                    !policy.allowDirectPush()
                    && pullRequest.sourceBranch.equals(
                        policy.protectedBranch()
                    )
                ) {
                    return "direct push to protected branch is prohibited";
                }

                return null;
            };
        }

        private PolicyCheck createHistoryPolicy() {
            final BranchProtection policy = protection;

            return pullRequest -> {
                if (!policy.requireLinearHistory()) {
                    return null;
                }

                Set<String> seen = new HashSet<>();

                for (Commit commit : pullRequest.commits) {
                    if (!seen.add(commit.sha())) {
                        return "duplicate commit detected";
                    }
                }

                return null;
            };
        }

        boolean merge(PullRequest pullRequest) {
            List<String> failures = evaluate(pullRequest);

            if (!failures.isEmpty()) {
                System.out.println(
                    "PR #" + pullRequest.number + " rejected"
                );

                failures.forEach(
                    failure -> System.out.println("  - " + failure)
                );

                return false;
            }

            pullRequest.setState(PullRequestState.MERGED);
            System.out.println(
                "PR #" + pullRequest.number + " merged into "
                    + pullRequest.targetBranch
            );

            return true;
        }
    }

    public static void main(String[] args) {
        BranchProtection policy = new BranchProtection(
            "main",
            2,
            Set.of("tests", "security-scan"),
            true,
            true,
            false
        );

        MergeEligibilityService service =
            new MergeEligibilityService(policy);

        PullRequest pullRequest = new PullRequest(
            700,
            "Harden authentication policy",
            "feature/authentication",
            "main",
            PullRequestState.OPEN,
            List.of(
                new Commit("a1", "authentication policy"),
                new Commit("b2", "security validation")
            ),
            Set.of("alice", "bob", "carol"),
            List.of(
                new Review("alice", ReviewState.APPROVED, "b2"),
                new Review("bob", ReviewState.APPROVED, "b2")
            ),
            Map.of(
                "tests", true,
                "security-scan", true
            ),
            0
        );

        service.merge(pullRequest);

        PullRequest staleApprovalRequest = new PullRequest(
            701,
            "Update deployment rules",
            "feature/deployment",
            "main",
            PullRequestState.OPEN,
            List.of(
                new Commit("c1", "initial deployment rule"),
                new Commit("d2", "respond to review")
            ),
            Set.of("alice", "bob"),
            List.of(
                new Review("alice", ReviewState.APPROVED, "c1"),
                new Review("bob", ReviewState.APPROVED, "c1")
            ),
            Map.of(
                "tests", true,
                "security-scan", true
            ),
            0
        );

        System.out.println("\nStale approval scenario:");
        service.merge(staleApprovalRequest);

        staleApprovalRequest.addReview(
            new Review("alice", ReviewState.APPROVED, "d2")
        );
        staleApprovalRequest.addReview(
            new Review("bob", ReviewState.APPROVED, "d2")
        );

        System.out.println("\nFresh approval scenario:");
        service.merge(staleApprovalRequest);
    }
}
