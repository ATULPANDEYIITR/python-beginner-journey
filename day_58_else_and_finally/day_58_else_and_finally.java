import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class RepositoryGovernanceDemo {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        COMMENTED, CHANGES_REQUESTED, APPROVED, DISMISSED
    }

    record Review(
            String reviewer,
            ReviewState state,
            String commitSha,
            boolean stale) {

        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            if (commitSha == null || commitSha.isBlank()) {
                throw new IllegalArgumentException("Commit SHA is required.");
            }
        }

        Review markStale() {
            return new Review(reviewer, state, commitSha, true);
        }
    }

    record StatusCheck(String name, boolean passed) {
        StatusCheck {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Status name is required.");
            }
        }
    }

    record BranchProtectionPolicy(
            int requiredApprovals,
            Set<String> requiredChecks,
            boolean requireResolvedConversations,
            boolean requireLinearHistory) {

        BranchProtectionPolicy {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                        "Required approvals cannot be negative.");
            }
            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    static final class GovernanceException extends Exception {
        GovernanceException(String message) {
            super(message);
        }
    }

    static final class PullRequest {
        private final int number;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<String> commits;
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, StatusCheck> checks = new HashMap<>();

        private PullRequestState state;
        private String mergeStrategy = "squash";
        private boolean synchronizedWithBase = true;
        private int unresolvedConversations;

        PullRequest(
                int number,
                String sourceBranch,
                String targetBranch,
                List<String> commits,
                boolean draft) {

            if (sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException(
                        "Source and target branches must differ.");
            }
            if (commits == null || commits.isEmpty()) {
                throw new IllegalArgumentException(
                        "Pull request requires commits.");
            }

            this.number = number;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.commits = List.copyOf(commits);
            this.state = draft
                    ? PullRequestState.DRAFT
                    : PullRequestState.OPEN;
        }

        int number() {
            return number;
        }

        PullRequestState state() {
            return state;
        }

        String headSha() {
            return commits.get(commits.size() - 1);
        }

        void addReview(Review review) throws GovernanceException {
            if (state != PullRequestState.OPEN
                    && state != PullRequestState.DRAFT) {
                throw new GovernanceException(
                        "Reviews are not allowed for closed PRs.");
            }
            reviews.add(review);
        }

        void setStatusCheck(String name, boolean passed) {
            checks.put(name, new StatusCheck(name, passed));
        }

        void setUnresolvedConversations(int count) {
            if (count < 0) {
                throw new IllegalArgumentException(
                        "Conversation count cannot be negative.");
            }
            unresolvedConversations = count;
        }

        void setMergeStrategy(String strategy) {
            mergeStrategy = strategy;
        }

        void synchronizeWithBase() {
            synchronizedWithBase = true;

            for (int i = 0; i < reviews.size(); i++) {
                reviews.set(i, reviews.get(i).markStale());
            }
        }

        int activeApprovals() {
            return (int) reviews.stream()
                    .filter(review ->
                            review.state() == ReviewState.APPROVED
                            && !review.stale()
                            && review.commitSha().equals(headSha()))
                    .count();
        }
    }

    static final class MergeEligibilityService {

        private final BranchProtectionPolicy policy;

        MergeEligibilityService(BranchProtectionPolicy policy) {
            this.policy = policy;
        }

        List<String> validate(PullRequest pr) {
            List<String> failures = new ArrayList<>();

            if (pr.state() != PullRequestState.OPEN) {
                failures.add("Pull request is not open.");
            }

            if (pr.activeApprovals() < policy.requiredApprovals()) {
                failures.add(
                        "Required approvals are not satisfied.");
            }

            for (String requiredCheck : policy.requiredChecks()) {
                StatusCheck check = getCheck(pr, requiredCheck);

                if (check == null || !check.passed()) {
                    failures.add(
                            "Required status check failed: "
                                    + requiredCheck);
                }
            }

            return failures;
        }

        private StatusCheck getCheck(PullRequest pr, String name) {
            try {
                var field = PullRequest.class
                        .getDeclaredField("checks");
                field.setAccessible(true);

                @SuppressWarnings("unchecked")
                Map<String, StatusCheck> checks =
                        (Map<String, StatusCheck>) field.get(pr);

                return checks.get(name);
            } catch (ReflectiveOperationException ex) {
                throw new IllegalStateException(
                        "Governance state could not be inspected.", ex);
            }
        }

        boolean isEligible(PullRequest pr) {
            return validate(pr).isEmpty();
        }
    }

    static final class RepositoryService {

        private final Set<String> branches =
                new HashSet<>(Set.of("main", "develop"));
        private final Set<String> commits = new HashSet<>();
        private final List<String> auditLog = new ArrayList<>();
        private final MergeEligibilityService eligibilityService;
        private int nextPrNumber = 1;

        RepositoryService(BranchProtectionPolicy policy) {
            eligibilityService = new MergeEligibilityService(policy);
        }

        void addCommit(String sha) {
            if (sha == null || sha.length() < 7) {
                throw new IllegalArgumentException(
                        "Commit SHA must contain at least seven characters.");
            }

            if (!commits.add(sha)) {
                throw new IllegalArgumentException(
                        "Duplicate commit.");
            }
        }

        PullRequest createPullRequest(
                String source,
                String target,
                List<String> changes,
                boolean draft) {

            if (!branches.contains(source) || !branches.contains(target)) {
                throw new IllegalArgumentException(
                        "Unknown branch.");
            }

            if (!commits.containsAll(changes)) {
                throw new IllegalArgumentException(
                        "Changeset contains unknown commits.");
            }

            return new PullRequest(
                    nextPrNumber++,
                    source,
                    target,
                    changes,
                    draft);
        }

        boolean merge(PullRequest pr) {
            try {
                List<String> failures =
                        eligibilityService.validate(pr);

                if (!failures.isEmpty()) {
                    throw new GovernanceException(
                            String.join(" ", failures));
                } else {
                    pr.state = PullRequestState.MERGED;
                    auditLog.add(
                            "PR-" + pr.number() + " merged.");
                    return true;
                }
            } catch (GovernanceException ex) {
                auditLog.add(
                        "PR-" + pr.number()
                                + " rejected: " + ex.getMessage());
                return false;
            } finally {
                // Java's finally block is used for an audit guarantee that
                // must run after both successful and failed merge attempts.
                auditLog.add(
                        "PR-" + pr.number()
                                + " merge attempt finalized.");
            }
        }

        List<String> auditLog() {
            return List.copyOf(auditLog);
        }
    }

    public static void main(String[] args) {
        BranchProtectionPolicy policy =
                new BranchProtectionPolicy(
                        2,
                        Set.of("tests", "security"),
                        true,
                        true);

        RepositoryService repository =
                new RepositoryService(policy);

        repository.addCommit("abcdef1");
        repository.addCommit("abcdef2");

        PullRequest pr = repository.createPullRequest(
                "develop",
                "main",
                List.of("abcdef1", "abcdef2"),
                false);

        try {
            pr.addReview(new Review(
                    "alice",
                    ReviewState.APPROVED,
                    pr.headSha(),
                    false));

            pr.addReview(new Review(
                    "bob",
                    ReviewState.APPROVED,
                    pr.headSha(),
                    false));
        } catch (GovernanceException ex) {
            System.err.println(
                    "Review operation failed: " + ex.getMessage());
            return;
        }

        pr.setStatusCheck("tests", true);
        pr.setStatusCheck("security", true);

        MergeEligibilityService service =
                new MergeEligibilityService(policy);

        try {
            List<String> failures = service.validate(pr);

            if (failures.isEmpty()) {
                System.out.println("PR is eligible.");
            } else {
                System.out.println("PR is blocked:");
                failures.forEach(failure ->
                        System.out.println("  - " + failure));
            }
        } catch (RuntimeException ex) {
            System.err.println(
                    "Validation failure: " + ex.getMessage());
        } finally {
            System.out.println(
                    "Eligibility evaluation completed.");
        }

        boolean merged = repository.merge(pr);

        System.out.println("Merged: " + merged);
        System.out.println("Final state: " + pr.state());

        System.out.println("\nAudit log:");
        repository.auditLog().forEach(
                event -> System.out.println("  " + event));

        // Synchronization makes previous approvals stale.
        if (pr.state() == PullRequestState.MERGED) {
            System.out.println(
                    "\nMerged PR requires no further approval.");
        } else {
            pr.synchronizeWithBase();
            System.out.println(
                    "\nCurrent approvals after synchronization: "
                            + pr.activeApprovals());
        }
    }
}
