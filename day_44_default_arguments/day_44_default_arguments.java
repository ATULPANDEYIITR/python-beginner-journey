import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class RepositoryGovernance {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        COMMENTED, APPROVED, CHANGES_REQUESTED, DISMISSED
    }

    enum CheckState {
        PENDING, SUCCESS, FAILURE
    }

    enum MergeMethod {
        MERGE_COMMIT, SQUASH, REBASE
    }

    record Reviewer(String username, String team) {
        Reviewer {
            if (username == null || username.isBlank()) {
                throw new IllegalArgumentException("Reviewer username is required");
            }
            if (team == null || team.isBlank()) {
                throw new IllegalArgumentException("Reviewer team is required");
            }
        }
    }

    record Commit(String sha, String message) {
        Commit {
            if (sha == null || sha.isBlank()) {
                throw new IllegalArgumentException("Commit SHA is required");
            }
            if (message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit message is required");
            }
        }
    }

    record Review(
        Reviewer reviewer,
        ReviewState state,
        int revision,
        String comment,
        Instant submittedAt,
        boolean dismissed
    ) {
        Review {
            Objects.requireNonNull(reviewer);
            Objects.requireNonNull(state);
            Objects.requireNonNull(submittedAt);
            comment = comment == null ? "" : comment;
            if (revision < 0) {
                throw new IllegalArgumentException("Revision cannot be negative");
            }
        }

        Review dismiss() {
            return new Review(
                reviewer, ReviewState.DISMISSED, revision,
                comment, Instant.now(), true
            );
        }
    }

    record Policy(
        int requiredApprovals,
        Set<String> requiredChecks,
        Set<MergeMethod> permittedMergeMethods,
        boolean requireResolvedConversations,
        boolean requireLinearHistory,
        boolean dismissStaleApprovals,
        boolean allowAdministratorBypass
    ) {
        Policy {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Required approvals cannot be negative"
                );
            }
            requiredChecks = Set.copyOf(requiredChecks);
            permittedMergeMethods = Set.copyOf(permittedMergeMethods);
            if (permittedMergeMethods.isEmpty()) {
                throw new IllegalArgumentException(
                    "At least one merge method must be permitted"
                );
            }
        }

        static Policy standard() {
            return new Policy(
                2,
                Set.of("ci", "security"),
                EnumSet.of(MergeMethod.SQUASH, MergeMethod.REBASE),
                true,
                true,
                true,
                false
            );
        }
    }

    record Conversation(String id, String text, boolean resolved) {
        Conversation {
            if (id == null || id.isBlank() || text == null || text.isBlank()) {
                throw new IllegalArgumentException(
                    "Conversation ID and text are required"
                );
            }
        }

        Conversation resolve() {
            return new Conversation(id, text, true);
        }
    }

    record Eligibility(
        boolean eligible,
        int approvals,
        List<String> failures
    ) {
        Eligibility {
            failures = List.copyOf(failures);
        }
    }

    static final class PullRequest {
        private final int number;
        private final String title;
        private final String author;
        private final String sourceBranch;
        private final String targetBranch;

        private PullRequestState state;
        private int revision;
        private int baseRevision;

        private final List<Commit> commits = new ArrayList<>();
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, CheckState> checks = new HashMap<>();
        private final Map<String, Reviewer> requestedReviewers = new HashMap<>();
        private final Map<String, Conversation> conversations = new TreeMap<>();

        PullRequest(
            int number,
            String title,
            String author,
            String sourceBranch,
            String targetBranch,
            boolean draft
        ) {
            if (number <= 0) {
                throw new IllegalArgumentException("Pull request number must be positive");
            }

            this.number = number;
            this.title = requireText(title, "title");
            this.author = requireText(author, "author");
            this.sourceBranch = requireText(sourceBranch, "source branch");
            this.targetBranch = requireText(targetBranch, "target branch");

            if (sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException(
                    "Source and target branches must differ"
                );
            }

            this.state = draft ? PullRequestState.DRAFT : PullRequestState.OPEN;
        }

        private static String requireText(String value, String field) {
            if (value == null || value.isBlank()) {
                throw new IllegalArgumentException(field + " is required");
            }
            return value.trim();
        }

        void markReady() {
            if (state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Only a draft can become ready");
            }
            state = PullRequestState.OPEN;
        }

        void addCommit(Commit commit) {
            requireActive();
            if (commits.stream().anyMatch(existing -> existing.sha().equals(commit.sha()))) {
                throw new IllegalArgumentException("Duplicate commit SHA");
            }

            commits.add(commit);
            revision++;
            // Reviews remain in the audit history. Their revision determines
            // whether they are still valid for merge-eligibility evaluation.
        }

        void requestReview(Reviewer reviewer) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Reviews require an open pull request");
            }
            if (reviewer.username().equals(author)) {
                throw new IllegalArgumentException(
                    "The pull request author cannot review their own changes"
                );
            }
            requestedReviewers.put(reviewer.username(), reviewer);
        }

        void submitReview(
            Reviewer reviewer,
            ReviewState decision,
            String comment
        ) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Reviews require an open pull request");
            }
            if (reviewer.username().equals(author)) {
                throw new IllegalArgumentException("Self-approval is prohibited");
            }
            if (!requestedReviewers.containsKey(reviewer.username())) {
                throw new IllegalStateException(
                    "Reviewer must have an explicit review request"
                );
            }
            if (decision == ReviewState.DISMISSED) {
                throw new IllegalArgumentException(
                    "Dismissal must use the review-administration operation"
                );
            }

            reviews.add(new Review(
                reviewer, decision, revision, comment, Instant.now(), false
            ));
            requestedReviewers.remove(reviewer.username());
        }

        void dismissApproval(String username) {
            boolean dismissed = false;
            List<Review> updated = new ArrayList<>();

            for (Review review : reviews) {
                if (review.reviewer().username().equals(username)
                    && review.state() == ReviewState.APPROVED
                    && !review.dismissed()) {
                    updated.add(review.dismiss());
                    dismissed = true;
                } else {
                    updated.add(review);
                }
            }

            if (!dismissed) {
                throw new IllegalArgumentException(
                    "No active approval exists for " + username
                );
            }

            reviews.clear();
            reviews.addAll(updated);
        }

        void setCheck(String name, CheckState state) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Check name is required");
            }
            checks.put(name, Objects.requireNonNull(state));
        }

        void addConversation(String id, String text, boolean resolved) {
            Conversation conversation = new Conversation(id, text, resolved);
            if (conversations.putIfAbsent(id, conversation) != null) {
                throw new IllegalArgumentException("Duplicate conversation ID");
            }
        }

        void resolveConversation(String id) {
            Conversation conversation = conversations.get(id);
            if (conversation == null) {
                throw new IllegalArgumentException("Unknown conversation: " + id);
            }
            conversations.put(id, conversation.resolve());
        }

        boolean synchronizeWithBase(int newBaseRevision, boolean conflicts) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Only open pull requests can synchronize");
            }
            if (newBaseRevision < baseRevision) {
                throw new IllegalArgumentException(
                    "Base revision cannot move backwards"
                );
            }
            if (conflicts) {
                return false;
            }

            baseRevision = newBaseRevision;
            revision++;
            return true;
        }

        Eligibility evaluate(
            Policy policy,
            MergeMethod method,
            boolean administrator
        ) {
            List<String> failures = new ArrayList<>();

            if (state != PullRequestState.OPEN) {
                failures.add("Pull request is not open");
            }
            if (!policy.permittedMergeMethods().contains(method)) {
                failures.add("Merge method is not permitted");
            }
            if (policy.requireLinearHistory()
                && method == MergeMethod.MERGE_COMMIT) {
                failures.add("Linear history prohibits merge commits");
            }

            // A later review by the same reviewer supersedes an earlier review.
            Map<String, Review> latestReviews = reviews.stream()
                .collect(Collectors.toMap(
                    review -> review.reviewer().username(),
                    review -> review,
                    (left, right) ->
                        left.submittedAt().isAfter(right.submittedAt())
                            ? left : right
                ));

            int approvalCount = (int) latestReviews.values().stream()
                .filter(review -> review.state() == ReviewState.APPROVED)
                .filter(review -> !review.dismissed())
                .filter(review ->
                    !policy.dismissStaleApprovals()
                    || review.revision() == revision
                )
                .count();

            if (approvalCount < policy.requiredApprovals()) {
                failures.add(
                    "Insufficient current approvals: " + approvalCount
                    + "/" + policy.requiredApprovals()
                );
            }

            for (String requiredCheck : policy.requiredChecks()) {
                if (checks.get(requiredCheck) != CheckState.SUCCESS) {
                    failures.add(
                        "Required check has not succeeded: " + requiredCheck
                    );
                }
            }

            if (policy.requireResolvedConversations()
                && conversations.values().stream()
                    .anyMatch(conversation -> !conversation.resolved())) {
                failures.add("Unresolved review conversations remain");
            }

            if (!requestedReviewers.isEmpty()) {
                failures.add("Requested reviews remain outstanding");
            }

            // Administrative bypass must be an explicit policy decision.
            if (administrator && policy.allowAdministratorBypass()) {
                failures.clear();
            }

            return new Eligibility(
                failures.isEmpty(), approvalCount, failures
            );
        }

        void merge(Policy policy, MergeMethod method) {
            Eligibility result = evaluate(policy, method, false);
            if (!result.eligible()) {
                throw new IllegalStateException(
                    "Merge rejected: " + String.join("; ", result.failures())
                );
            }
            state = PullRequestState.MERGED;
        }

        void close() {
            if (state != PullRequestState.OPEN && state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Pull request cannot be closed");
            }
            state = PullRequestState.CLOSED;
        }

        void reopen() {
            if (state != PullRequestState.CLOSED) {
                throw new IllegalStateException(
                    "Only a closed, unmerged pull request can be reopened"
                );
            }
            state = PullRequestState.OPEN;
        }

        private void requireActive() {
            if (state != PullRequestState.OPEN && state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Pull request is no longer active");
            }
        }

        void printEligibility(Eligibility result) {
            System.out.println("\nPull request #" + number + ": " + title);
            System.out.println(sourceBranch + " -> " + targetBranch);
            System.out.println("State: " + state + ", revision: " + revision);
            System.out.println("Current approvals: " + result.approvals());
            System.out.println("Eligible: " + result.eligible());
            result.failures().forEach(failure -> System.out.println(" - " + failure));
        }

        PullRequestState state() {
            return state;
        }
    }

    public static void main(String[] args) {
        Policy policy = Policy.standard();

        PullRequest pullRequest = new PullRequest(
            304,
            "Require authorization for deployment changes",
            "developer-lee",
            "feature/deployment-authorization",
            "main",
            true
        );

        pullRequest.addCommit(
            new Commit("a91c3e0", "Add deployment authorization checks")
        );
        pullRequest.markReady();

        Reviewer alex = new Reviewer("reviewer-alex", "platform");
        Reviewer sam = new Reviewer("reviewer-sam", "security");

        pullRequest.requestReview(alex);
        pullRequest.requestReview(sam);

        pullRequest.submitReview(
            alex,
            ReviewState.APPROVED,
            "Authorization is checked before deployment."
        );
        pullRequest.submitReview(
            sam,
            ReviewState.APPROVED,
            "Security boundary and audit behavior are acceptable."
        );

        pullRequest.setCheck("ci", CheckState.SUCCESS);
        pullRequest.setCheck("security", CheckState.SUCCESS);
        pullRequest.addConversation(
            "discussion-44",
            "Confirm denied deployment requests are audited.",
            false
        );

        pullRequest.printEligibility(
            pullRequest.evaluate(policy, MergeMethod.SQUASH, false)
        );

        pullRequest.resolveConversation("discussion-44");
        pullRequest.addCommit(
            new Commit("b52d7f1", "Test denied deployment requests")
        );

        pullRequest.printEligibility(
            pullRequest.evaluate(policy, MergeMethod.SQUASH, false)
        );

        pullRequest.requestReview(alex);
        pullRequest.requestReview(sam);
        pullRequest.submitReview(alex, ReviewState.APPROVED, "Re-reviewed updated changes.");
        pullRequest.submitReview(sam, ReviewState.APPROVED, "Security tests verified.");

        Eligibility finalResult =
            pullRequest.evaluate(policy, MergeMethod.SQUASH, false);
        pullRequest.printEligibility(finalResult);

        pullRequest.merge(policy, MergeMethod.SQUASH);
        System.out.println("Final state: " + pullRequest.state());

        // A closed pull request cannot be merged or treated as merge-eligible.
        PullRequest abandoned = new PullRequest(
            305, "Archive an obsolete deployment proposal",
            "developer-mira", "docs/archive-proposal", "main", false
        );
        abandoned.close();

        Eligibility closedResult =
            abandoned.evaluate(policy, MergeMethod.SQUASH, false);
        abandoned.printEligibility(closedResult);

        try {
            abandoned.reopen();
            System.out.println("Reopened state: " + abandoned.state());
        } catch (IllegalStateException exception) {
            System.err.println(exception.getMessage());
        }
    }
}
