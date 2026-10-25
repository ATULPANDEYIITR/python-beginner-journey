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
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

public class RepositoryGovernance {
    enum PullRequestState {
        DRAFT, OPEN, MERGED, CLOSED
    }

    enum ReviewState {
        COMMENTED, APPROVED, CHANGES_REQUESTED, DISMISSED
    }

    enum CheckState {
        PENDING, PASSED, FAILED
    }

    enum MergeStrategy {
        MERGE_COMMIT, SQUASH, REBASE
    }

    static final class GovernanceException extends RuntimeException {
        GovernanceException(String message) {
            super(message);
        }
    }

    static final class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    record Commit(String sha, String message, String parent, Instant createdAt) {
        Commit {
            requireText(sha, "Commit SHA");
            requireText(message, "Commit message");
            Objects.requireNonNull(createdAt, "createdAt");
        }

        static Commit create(String message, String parent) {
            requireText(message, "Commit message");
            String sha = UUID.randomUUID().toString().replace("-", "").substring(0, 12);
            return new Commit(sha, message, parent, Instant.now());
        }
    }

    static final class Branch {
        private final String name;
        private final List<Commit> commits = new ArrayList<>();
        private boolean deleted;

        Branch(String name) {
            this.name = requireText(name, "Branch name");
        }

        String name() {
            return name;
        }

        String head() {
            return commits.isEmpty() ? "" : commits.get(commits.size() - 1).sha();
        }

        List<Commit> commits() {
            return Collections.unmodifiableList(commits);
        }

        void addCommit(Commit commit) {
            if (deleted) throw new GovernanceException("Branch has been deleted");
            Objects.requireNonNull(commit, "commit");
            if (commits.stream().anyMatch(existing -> existing.sha().equals(commit.sha()))) {
                throw new ValidationException("Duplicate commit SHA");
            }

            String expectedParent = head();
            if (!Objects.equals(expectedParent, commit.parent())) {
                throw new ValidationException("Commit parent does not match branch head");
            }
            commits.add(commit);
        }
    }

    record ReviewComment(String id, String reviewer, String body,
                         boolean resolved, Instant createdAt) {
        ReviewComment {
            requireText(id, "Comment ID");
            requireText(reviewer, "Reviewer");
            requireText(body, "Comment body");
            Objects.requireNonNull(createdAt, "createdAt");
        }
    }

    static final class Review {
        private final String reviewer;
        private ReviewState state;
        private final String headSha;
        private final Instant submittedAt;
        private final List<ReviewComment> comments;

        Review(String reviewer, ReviewState state, String headSha,
               List<ReviewComment> comments) {
            this.reviewer = requireText(reviewer, "Reviewer");
            this.state = Objects.requireNonNull(state, "state");
            this.headSha = requireText(headSha, "Reviewed head");
            this.comments = List.copyOf(comments);
            this.submittedAt = Instant.now();
        }

        String reviewer() {
            return reviewer;
        }

        ReviewState state() {
            return state;
        }

        String headSha() {
            return headSha;
        }

        Instant submittedAt() {
            return submittedAt;
        }

        List<ReviewComment> comments() {
            return comments;
        }

        void dismiss() {
            if (state == ReviewState.DISMISSED) {
                throw new GovernanceException("Review is already dismissed");
            }
            state = ReviewState.DISMISSED;
        }
    }

    record CheckResult(String name, CheckState state, String headSha, Instant updatedAt) {
        CheckResult {
            requireText(name, "Check name");
            Objects.requireNonNull(state, "state");
            requireText(headSha, "Checked head");
            Objects.requireNonNull(updatedAt, "updatedAt");
        }
    }

    record BranchProtectionPolicy(
            int requiredApprovals,
            Set<String> requiredChecks,
            boolean requireResolvedConversations,
            boolean requireLinearHistory,
            boolean restrictDirectPush,
            boolean allowForcePush,
            boolean allowDeletion,
            boolean allowAdminBypass
    ) {
        BranchProtectionPolicy {
            if (requiredApprovals < 0) {
                throw new ValidationException("Required approvals cannot be negative");
            }
            Objects.requireNonNull(requiredChecks, "requiredChecks");
            if (requiredChecks.stream().anyMatch(name -> name == null || name.isBlank())) {
                throw new ValidationException("Required check names cannot be blank");
            }
            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    record Eligibility(boolean eligible, List<String> blockers,
                       Set<String> approvingReviewers) {
        Eligibility {
            blockers = List.copyOf(blockers);
            approvingReviewers = Set.copyOf(approvingReviewers);
        }
    }

    static final class PullRequest {
        private final int number;
        private final String author;
        private final Branch source;
        private final Branch target;
        private final Set<String> eligibleReviewers;
        private final MergeStrategy strategy;
        private PullRequestState state = PullRequestState.OPEN;
        private String headSha;
        private String baseSha;
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, CheckResult> checks = new HashMap<>();
        private final Map<String, Boolean> conversations = new LinkedHashMap<>();
        private String mergedCommit;

        PullRequest(int number, String author, Branch source, Branch target,
                    Set<String> eligibleReviewers, MergeStrategy strategy) {
            if (number <= 0) throw new ValidationException("PR number must be positive");
            this.number = number;
            this.author = requireText(author, "Author");
            this.source = Objects.requireNonNull(source, "source");
            this.target = Objects.requireNonNull(target, "target");
            if (source == target || source.name().equals(target.name())) {
                throw new ValidationException("Source and target must differ");
            }
            this.eligibleReviewers = Set.copyOf(eligibleReviewers);
            if (this.eligibleReviewers.contains(author)) {
                throw new ValidationException("Author cannot review their own PR");
            }
            this.strategy = Objects.requireNonNull(strategy, "strategy");
            this.headSha = source.head();
            this.baseSha = target.head();
        }

        int number() {
            return number;
        }

        PullRequestState state() {
            return state;
        }

        List<Review> reviews() {
            return Collections.unmodifiableList(reviews);
        }

        void markDraft() {
            requireOpen();
            state = PullRequestState.DRAFT;
        }

        void markReady() {
            if (state != PullRequestState.DRAFT) {
                throw new GovernanceException("Only draft PRs can become ready");
            }
            state = PullRequestState.OPEN;
        }

        void synchronizeBranches() {
            requireOpen();
            headSha = source.head();
            baseSha = target.head();
        }

        void addConversation(String id) {
            requireOpen();
            requireText(id, "Conversation ID");
            if (conversations.putIfAbsent(id, false) != null) {
                throw new ValidationException("Conversation ID already exists");
            }
        }

        void resolveConversation(String id) {
            requireOpen();
            if (!conversations.containsKey(id)) {
                throw new GovernanceException("Conversation not found");
            }
            conversations.put(id, true);
        }

        void submitReview(String reviewer, ReviewState decision, List<String> bodies) {
            requireOpen();
            requireText(reviewer, "Reviewer");
            Objects.requireNonNull(decision, "decision");
            if (!eligibleReviewers.contains(reviewer)) {
                throw new GovernanceException("Reviewer is not eligible");
            }
            if (reviewer.equals(author)) {
                throw new GovernanceException("Self-review is prohibited");
            }
            if (decision == ReviewState.DISMISSED) {
                throw new ValidationException("Dismissal is not a submitted decision");
            }
            if (headSha.isEmpty()) {
                throw new GovernanceException("Cannot review an empty changeset");
            }

            List<ReviewComment> comments = new ArrayList<>();
            for (String body : bodies) {
                comments.add(new ReviewComment(
                        UUID.randomUUID().toString(), reviewer, body, false, Instant.now()
                ));
            }
            reviews.add(new Review(reviewer, decision, headSha, comments));
        }

        void dismissReview(String reviewer) {
            requireOpen();
            Review latest = latestReviews().get(reviewer);
            if (latest == null) {
                throw new GovernanceException("No review exists for reviewer");
            }
            latest.dismiss();
        }

        private Map<String, Review> latestReviews() {
            Map<String, Review> latest = new HashMap<>();
            for (Review review : reviews) {
                latest.put(review.reviewer(), review);
            }
            return latest;
        }

        void updateCheck(String name, CheckState status) {
            requireOpen();
            checks.put(requireText(name, "Check name"),
                    new CheckResult(name, status, headSha, Instant.now()));
        }

        Eligibility evaluate(BranchProtectionPolicy policy) {
            List<String> blockers = new ArrayList<>();

            if (state != PullRequestState.OPEN) blockers.add("PR is not open");
            if (source.commits().isEmpty()) blockers.add("Source branch is empty");
            if (!headSha.equals(source.head())) blockers.add("Source head is stale");
            if (!baseSha.equals(target.head())) blockers.add("Target base is stale");

            Set<String> approvals = latestReviews().values().stream()
                    .filter(review -> review.state() == ReviewState.APPROVED)
                    .filter(review -> review.headSha().equals(headSha))
                    .map(Review::reviewer)
                    .filter(eligibleReviewers::contains)
                    .collect(Collectors.toSet());

            if (approvals.size() < policy.requiredApprovals()) {
                blockers.add("Insufficient current approvals: " + approvals.size()
                        + "/" + policy.requiredApprovals());
            }

            for (String required : policy.requiredChecks()) {
                CheckResult result = checks.get(required);
                if (result == null || result.state() != CheckState.PASSED
                        || !result.headSha().equals(headSha)) {
                    blockers.add("Required check missing, failing, or stale: " + required);
                }
            }

            if (policy.requireResolvedConversations()
                    && conversations.values().stream().anyMatch(resolved -> !resolved)) {
                blockers.add("Unresolved review conversations remain");
            }

            if (policy.requireLinearHistory() && strategy == MergeStrategy.MERGE_COMMIT) {
                blockers.add("Merge commits violate linear-history policy");
            }

            return new Eligibility(blockers.isEmpty(), blockers, approvals);
        }

        String merge(BranchProtectionPolicy policy) {
            requireOpen();
            Eligibility result = evaluate(policy);
            if (!result.eligible()) {
                throw new GovernanceException("Merge blocked: "
                        + String.join("; ", result.blockers()));
            }

            Commit mergeCommit = Commit.create(
                    "Merge pull request #" + number + " using " + strategy,
                    target.head()
            );
            target.addCommit(mergeCommit);
            mergedCommit = mergeCommit.sha();
            state = PullRequestState.MERGED;
            return mergedCommit;
        }

        void close() {
            requireOpen();
            state = PullRequestState.CLOSED;
        }

        void reopen() {
            if (state != PullRequestState.CLOSED) {
                throw new GovernanceException("Only closed, unmerged PRs can reopen");
            }
            state = PullRequestState.OPEN;
            synchronizeBranches();
        }

        private void requireOpen() {
            if (state != PullRequestState.OPEN) {
                throw new GovernanceException("Operation requires an open PR");
            }
        }
    }

    private static String requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new ValidationException(field + " must not be blank");
        }
        return value.trim();
    }

    public static void main(String[] args) {
        Branch main = new Branch("main");
        main.addCommit(new Commit("base001", "Initial release", "", Instant.now()));

        Branch feature = new Branch("feature/payment-validation");
        feature.addCommit(new Commit(
                "feat001", "Validate payment requests", "", Instant.now()
        ));

        BranchProtectionPolicy policy = new BranchProtectionPolicy(
                2,
                Set.of("build", "tests", "security"),
                true,
                true,
                true,
                false,
                false,
                false
        );

        PullRequest pr = new PullRequest(
                42, "developer", feature, main,
                Set.of("alex", "sam", "jordan"), MergeStrategy.SQUASH
        );

        pr.addConversation("thread-1");
        pr.updateCheck("build", CheckState.PASSED);
        pr.updateCheck("tests", CheckState.PASSED);
        pr.updateCheck("security", CheckState.PASSED);

        pr.submitReview("alex", ReviewState.APPROVED,
                List.of("Input validation is covered."));
        pr.submitReview("sam", ReviewState.CHANGES_REQUESTED,
                List.of("Add a duplicate transaction test."));

        Eligibility first = pr.evaluate(policy);
        System.out.println("Initial eligibility: " + first.eligible());
        first.blockers().forEach(reason -> System.out.println("  BLOCKED: " + reason));

        pr.submitReview("sam", ReviewState.APPROVED,
                List.of("Duplicate transaction test added."));
        pr.resolveConversation("thread-1");

        Eligibility finalResult = pr.evaluate(policy);
        System.out.println("Final eligibility: " + finalResult.eligible());
        if (!finalResult.eligible()) {
            throw new GovernanceException("Expected PR to be eligible");
        }

        System.out.println("Merged commit: " + pr.merge(policy));
        System.out.println("Final PR state: " + pr.state());

        try {
            pr.reopen();
        } catch (GovernanceException ex) {
            System.out.println("Expected lifecycle restriction: " + ex.getMessage());
        }

        try {
            new BranchProtectionPolicy(-1, Set.of(), true, true,
                    true, false, false, false);
        } catch (ValidationException ex) {
            System.out.println("Expected policy validation: " + ex.getMessage());
        }
    }
}
