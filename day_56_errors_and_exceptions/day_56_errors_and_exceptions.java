import java.util.*;
import java.util.stream.Collectors;

public class RepositoryGovernanceExceptions {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        COMMENTED, APPROVED, CHANGES_REQUESTED, DISMISSED
    }

    enum CheckState {
        PASSING, FAILING, PENDING
    }

    interface MergeRule {
        void validate(PullRequest pullRequest, BranchProtection policy)
                throws GovernanceException;
    }

    static class GovernanceException extends Exception {
        GovernanceException(String message) {
            super(message);
        }
    }

    static class ValidationException extends GovernanceException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class InvalidStateException extends GovernanceException {
        InvalidStateException(String message) {
            super(message);
        }
    }

    static class PolicyViolationException extends GovernanceException {
        PolicyViolationException(String message) {
            super(message);
        }
    }

    static class StaleApprovalException extends GovernanceException {
        StaleApprovalException(String message) {
            super(message);
        }
    }

    record Commit(String sha, String message) {
        Commit {
            if (sha == null || sha.length() < 7) {
                throw new IllegalArgumentException("Commit SHA must contain at least seven characters.");
            }
            if (message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit message cannot be empty.");
            }
        }
    }

    record ReviewComment(String reviewer, String body, boolean resolved) {
        ReviewComment {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            if (body == null || body.isBlank()) {
                throw new IllegalArgumentException("Review comment cannot be empty.");
            }
        }

        ReviewComment resolve() {
            return new ReviewComment(reviewer, body, true);
        }
    }

    static final class Review {
        private final String reviewer;
        private ReviewState state;
        private final String reviewedCommit;
        private final List<ReviewComment> comments = new ArrayList<>();

        Review(String reviewer, ReviewState state, String reviewedCommit) {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            this.reviewer = reviewer;
            this.state = Objects.requireNonNull(state);
            this.reviewedCommit = Objects.requireNonNull(reviewedCommit);
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

        List<ReviewComment> comments() {
            return Collections.unmodifiableList(comments);
        }

        void addComment(String body) {
            comments.add(new ReviewComment(reviewer, body, false));
        }

        void resolveComments() {
            for (int i = 0; i < comments.size(); i++) {
                comments.set(i, comments.get(i).resolve());
            }
        }

        void approve() {
            state = ReviewState.APPROVED;
        }

        void requestChanges() {
            state = ReviewState.CHANGES_REQUESTED;
        }

        void dismiss() {
            state = ReviewState.DISMISSED;
        }
    }

    static final class Branch {
        private final String name;
        private final List<Commit> commits = new ArrayList<>();
        private boolean protectedBranch;

        Branch(String name) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Branch name is required.");
            }
            this.name = name;
        }

        String name() {
            return name;
        }

        List<Commit> commits() {
            return Collections.unmodifiableList(commits);
        }

        void addCommit(Commit commit) {
            commits.add(Objects.requireNonNull(commit));
        }

        void protect() {
            protectedBranch = true;
        }

        boolean isProtected() {
            return protectedBranch;
        }
    }

    static final class PullRequest {
        private final int number;
        private final Branch source;
        private final Branch target;
        private PullRequestState state;
        private final boolean draft;
        private final List<Commit> commits = new ArrayList<>();
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, CheckState> checks = new HashMap<>();
        private final Set<String> changedFiles = new HashSet<>();

        PullRequest(int number, Branch source, Branch target, boolean draft) {
            if (number <= 0) {
                throw new IllegalArgumentException("Pull Request number must be positive.");
            }
            if (source == target) {
                throw new IllegalArgumentException("Source and target branches must differ.");
            }

            this.number = number;
            this.source = source;
            this.target = target;
            this.draft = draft;
            this.state = draft ? PullRequestState.DRAFT : PullRequestState.OPEN;
        }

        int number() {
            return number;
        }

        Branch target() {
            return target;
        }

        PullRequestState state() {
            return state;
        }

        List<Commit> commits() {
            return Collections.unmodifiableList(commits);
        }

        List<Review> reviews() {
            return Collections.unmodifiableList(reviews);
        }

        Map<String, CheckState> checks() {
            return Collections.unmodifiableMap(checks);
        }

        Set<String> changedFiles() {
            return Collections.unmodifiableSet(changedFiles);
        }

        boolean isDraft() {
            return draft;
        }

        void addCommit(Commit commit) throws InvalidStateException {
            if (state != PullRequestState.OPEN) {
                throw new InvalidStateException("Only open Pull Requests accept commits.");
            }
            commits.add(commit);
        }

        void addReview(Review review) throws InvalidStateException {
            if (state != PullRequestState.OPEN) {
                throw new InvalidStateException("Only open Pull Requests accept reviews.");
            }
            reviews.add(review);
        }

        void setCheck(String name, CheckState state) {
            checks.put(name, state);
        }

        void addChangedFile(String file) {
            if (file == null || file.isBlank()) {
                throw new IllegalArgumentException("Changed file name is required.");
            }
            changedFiles.add(file);
        }

        void close() throws InvalidStateException {
            if (state == PullRequestState.MERGED) {
                throw new InvalidStateException("Merged Pull Requests cannot be closed.");
            }
            state = PullRequestState.CLOSED;
        }

        void reopen() throws InvalidStateException {
            if (state != PullRequestState.CLOSED) {
                throw new InvalidStateException("Only closed Pull Requests can be reopened.");
            }
            state = PullRequestState.OPEN;
        }

        void markMerged() throws InvalidStateException {
            if (state != PullRequestState.OPEN) {
                throw new InvalidStateException("Only open Pull Requests can be merged.");
            }
            state = PullRequestState.MERGED;
        }
    }

    static final class BranchProtection {
        private final int requiredReviews;
        private final Set<String> requiredChecks;
        private final boolean requireResolvedConversations;
        private final boolean requireLinearHistory;
        private final boolean allowForcePush;
        private final boolean allowDeletion;

        BranchProtection(
                int requiredReviews,
                Set<String> requiredChecks,
                boolean requireResolvedConversations,
                boolean requireLinearHistory,
                boolean allowForcePush,
                boolean allowDeletion
        ) {
            if (requiredReviews < 0) {
                throw new IllegalArgumentException("Required reviews cannot be negative.");
            }
            this.requiredReviews = requiredReviews;
            this.requiredChecks = Set.copyOf(requiredChecks);
            this.requireResolvedConversations = requireResolvedConversations;
            this.requireLinearHistory = requireLinearHistory;
            this.allowForcePush = allowForcePush;
            this.allowDeletion = allowDeletion;
        }
    }

    static final class BasicMergeRule implements MergeRule {
        @Override
        public void validate(
                PullRequest pullRequest,
                BranchProtection policy
        ) throws GovernanceException {
            if (pullRequest.state() != PullRequestState.OPEN) {
                throw new InvalidStateException("Pull Request is not open.");
            }

            if (pullRequest.isDraft()) {
                throw new PolicyViolationException("Draft Pull Requests cannot be merged.");
            }

            if (pullRequest.commits().isEmpty()) {
                throw new ValidationException("Pull Request contains no commits.");
            }

            if (pullRequest.changedFiles().isEmpty()) {
                throw new ValidationException("Pull Request contains no changed files.");
            }
        }
    }

    static final class ApprovalRule implements MergeRule {
        @Override
        public void validate(
                PullRequest pullRequest,
                BranchProtection policy
        ) throws GovernanceException {
            Set<String> eligibleApprovers = pullRequest.reviews().stream()
                    .filter(review -> review.state() == ReviewState.APPROVED)
                    .filter(review -> review.reviewedCommit()
                            .equals(pullRequest.commits().get(pullRequest.commits().size() - 1).sha()))
                    .map(Review::reviewer)
                    .collect(Collectors.toSet());

            if (eligibleApprovers.size() < policy.requiredReviews) {
                boolean staleApprovalExists = pullRequest.reviews().stream()
                        .anyMatch(review ->
                                review.state() == ReviewState.APPROVED &&
                                !review.reviewedCommit().equals(
                                        pullRequest.commits()
                                                .get(pullRequest.commits().size() - 1)
                                                .sha()
                                )
                        );

                if (staleApprovalExists) {
                    throw new StaleApprovalException(
                            "One or more approvals refer to an older commit."
                    );
                }

                throw new PolicyViolationException(
                        "Required approvals are not satisfied."
                );
            }
        }
    }

    static final class StatusCheckRule implements MergeRule {
        @Override
        public void validate(
                PullRequest pullRequest,
                BranchProtection policy
        ) throws GovernanceException {
            for (String required : policy.requiredChecks) {
                CheckState state = pullRequest.checks().get(required);
                if (state != CheckState.PASSING) {
                    throw new PolicyViolationException(
                            "Required status check is not passing: " + required
                    );
                }
            }
        }
    }

    static final class ConversationRule implements MergeRule {
        @Override
        public void validate(
                PullRequest pullRequest,
                BranchProtection policy
        ) throws GovernanceException {
            if (!policy.requireResolvedConversations) {
                return;
            }

            boolean unresolved = pullRequest.reviews().stream()
                    .flatMap(review -> review.comments().stream())
                    .anyMatch(comment -> !comment.resolved());

            if (unresolved) {
                throw new PolicyViolationException(
                        "Unresolved review conversations remain."
                );
            }
        }
    }

    static final class MergeEligibilityService {
        private final List<MergeRule> rules;

        MergeEligibilityService(List<MergeRule> rules) {
            this.rules = List.copyOf(rules);
        }

        void merge(PullRequest pullRequest, BranchProtection policy)
                throws GovernanceException {
            for (MergeRule rule : rules) {
                rule.validate(pullRequest, policy);
            }
            pullRequest.markMerged();
        }
    }

    public static void main(String[] args) {
        Branch main = new Branch("main");
        Branch feature = new Branch("feature/risk-controls");
        main.protect();

        Commit commit = new Commit(
                "abcdef1234567",
                "Implement transaction risk controls"
        );
        feature.addCommit(commit);

        PullRequest pullRequest =
                new PullRequest(700, feature, main, false);

        pullRequest.addCommit(commit);
        pullRequest.addChangedFile("RiskService.java");

        Review alice =
                new Review("alice", ReviewState.APPROVED, commit.sha());

        Review bob =
                new Review("bob", ReviewState.COMMENTED, commit.sha());
        bob.addComment("Validate the maximum transaction threshold.");

        pullRequest.addReview(alice);
        pullRequest.addReview(bob);

        pullRequest.setCheck("unit-tests", CheckState.PASSING);
        pullRequest.setCheck("security-scan", CheckState.PASSING);

        BranchProtection policy = new BranchProtection(
                2,
                Set.of("unit-tests", "security-scan"),
                true,
                true,
                false,
                false
        );

        MergeEligibilityService service =
                new MergeEligibilityService(List.of(
                        new BasicMergeRule(),
                        new ApprovalRule(),
                        new StatusCheckRule(),
                        new ConversationRule()
                ));

        try {
            service.merge(pullRequest, policy);
        } catch (GovernanceException error) {
            System.out.println("Expected governance failure: " + error.getMessage());
        }

        bob.resolveComments();
        bob.approve();

        try {
            service.merge(pullRequest, policy);
            System.out.println(
                    "Pull Request #" + pullRequest.number() +
                    " merged successfully."
            );
        } catch (GovernanceException error) {
            System.err.println("Unexpected merge failure: " + error.getMessage());
        }

        try {
            pullRequest.addCommit(
                    new Commit("deadbeef12345", "Illegal post-merge change")
            );
        } catch (InvalidStateException error) {
            System.out.println("Expected state failure: " + error.getMessage());
        }

        try {
            PullRequest closed = new PullRequest(701, feature, main, false);
            closed.close();
            closed.reopen();
            System.out.println(
                    "Reopened Pull Request #" + closed.number() +
                    " in state " + closed.state()
            );
        } catch (InvalidStateException error) {
            System.out.println("Unexpected transition failure: " + error.getMessage());
        }
    }
}
