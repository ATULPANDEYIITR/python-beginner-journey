import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.stream.Collectors;

public class RepositoryGovernance {
    enum PullRequestState {
        OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        APPROVED, CHANGES_REQUESTED, COMMENTED
    }

    enum CheckState {
        PASSED, FAILED, PENDING
    }

    record Review(
        String reviewer,
        ReviewState state,
        String commitSha,
        boolean eligibleReviewer
    ) {
        Review {
            Objects.requireNonNull(reviewer, "reviewer");
            Objects.requireNonNull(state, "state");
            Objects.requireNonNull(commitSha, "commitSha");
            if (reviewer.isBlank() || commitSha.isBlank()) {
                throw new IllegalArgumentException(
                    "Reviewer and commit SHA must not be blank."
                );
            }
        }
    }

    record ReviewPolicy(
        int requiredApprovals,
        boolean dismissStaleApprovals,
        boolean requireResolvedConversations,
        boolean allowAuthorApproval,
        Set<String> requiredChecks,
        boolean requireLinearHistory
    ) {
        ReviewPolicy {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Required approvals cannot be negative."
                );
            }
            Objects.requireNonNull(requiredChecks, "requiredChecks");
            requiredChecks = Collections.unmodifiableSet(
                new TreeSet<>(requiredChecks)
            );
            if (requiredChecks.stream().anyMatch(String::isBlank)) {
                throw new IllegalArgumentException(
                    "Required check names cannot be blank."
                );
            }
        }
    }

    record BranchProtection(
        String branchName,
        boolean restrictDirectPushes,
        boolean allowForcePush,
        boolean allowDeletion,
        boolean allowAdministratorBypass,
        Set<String> authorizedPushers
    ) {
        BranchProtection {
            Objects.requireNonNull(branchName, "branchName");
            Objects.requireNonNull(authorizedPushers, "authorizedPushers");
            if (branchName.isBlank()) {
                throw new IllegalArgumentException(
                    "Protected branch name cannot be blank."
                );
            }
            authorizedPushers = Set.copyOf(authorizedPushers);
        }

        boolean canPushDirectly(String actor) {
            return !restrictDirectPushes || authorizedPushers.contains(actor);
        }

        boolean canForcePush(boolean administrator) {
            return allowForcePush ||
                (administrator && allowAdministratorBypass);
        }

        boolean canDelete(boolean administrator) {
            return allowDeletion ||
                (administrator && allowAdministratorBypass);
        }
    }

    static final class PullRequest {
        private final int number;
        private final String title;
        private final String author;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, CheckState> checks = new HashMap<>();
        private final Map<String, Boolean> conversations = new HashMap<>();

        private String headSha;
        private String baseSha;
        private PullRequestState state = PullRequestState.OPEN;
        private boolean draft;
        private boolean mergeConflict;
        private boolean linearHistory = true;

        PullRequest(
            int number,
            String title,
            String author,
            String sourceBranch,
            String targetBranch,
            String headSha,
            String baseSha,
            boolean draft
        ) {
            if (number <= 0) {
                throw new IllegalArgumentException(
                    "Pull request number must be positive."
                );
            }

            this.title = requireText(title, "title");
            this.author = requireText(author, "author");
            this.sourceBranch = requireText(sourceBranch, "sourceBranch");
            this.targetBranch = requireText(targetBranch, "targetBranch");
            this.headSha = requireText(headSha, "headSha");
            this.baseSha = requireText(baseSha, "baseSha");

            if (sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException(
                    "Source and target branches must differ."
                );
            }

            this.number = number;
            this.draft = draft;
        }

        private static String requireText(String value, String field) {
            Objects.requireNonNull(value, field);
            if (value.isBlank()) {
                throw new IllegalArgumentException(field + " must not be blank.");
            }
            return value;
        }

        void addReview(Review review) {
            requireOpen();
            Objects.requireNonNull(review, "review");

            if (!review.eligibleReviewer()) {
                throw new IllegalArgumentException(
                    "Reviewer is not eligible under repository policy."
                );
            }
            if (!reviewPolicyAuthorAllowed(review)) {
                throw new IllegalArgumentException(
                    "The pull request author cannot review their own changes."
                );
            }
            if (!review.commitSha().equals(headSha)) {
                throw new IllegalArgumentException(
                    "Review must target the current source commit."
                );
            }
            reviews.add(review);
        }

        private boolean reviewPolicyAuthorAllowed(Review review) {
            return !review.reviewer().equals(author);
        }

        void updateCheck(String name, CheckState result) {
            requireOpen();
            requireText(name, "check name");
            Objects.requireNonNull(result, "result");
            checks.put(name, result);
        }

        void updateConversation(String id, boolean resolved) {
            requireOpen();
            requireText(id, "conversation id");
            conversations.put(id, resolved);
        }

        void synchronize(String newHeadSha) {
            requireOpen();
            requireText(newHeadSha, "newHeadSha");
            if (headSha.equals(newHeadSha)) {
                throw new IllegalArgumentException(
                    "New source commit must differ from the current commit."
                );
            }

            headSha = newHeadSha;
            // Reviews stay in the audit history. Freshness is evaluated
            // against headSha, while old status results are discarded.
            checks.clear();
        }

        void updateBase(String newBaseSha) {
            requireOpen();
            requireText(newBaseSha, "newBaseSha");
            baseSha = newBaseSha;
        }

        void setDraft(boolean value) {
            requireOpen();
            draft = value;
        }

        void setMergeConflict(boolean value) {
            requireOpen();
            mergeConflict = value;
        }

        void setLinearHistory(boolean value) {
            requireOpen();
            linearHistory = value;
        }

        void close() {
            requireOpen();
            state = PullRequestState.CLOSED;
        }

        void reopen() {
            if (state != PullRequestState.CLOSED) {
                throw new IllegalStateException(
                    "Only closed pull requests can be reopened."
                );
            }
            state = PullRequestState.OPEN;
        }

        void markMerged() {
            requireOpen();
            state = PullRequestState.MERGED;
        }

        private void requireOpen() {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException(
                    "Operation requires an open pull request."
                );
            }
        }

        int number() {
            return number;
        }

        String title() {
            return title;
        }

        String author() {
            return author;
        }

        String sourceBranch() {
            return sourceBranch;
        }

        String targetBranch() {
            return targetBranch;
        }

        String headSha() {
            return headSha;
        }

        String baseSha() {
            return baseSha;
        }

        PullRequestState state() {
            return state;
        }

        boolean draft() {
            return draft;
        }

        boolean hasMergeConflict() {
            return mergeConflict;
        }

        boolean hasLinearHistory() {
            return linearHistory;
        }

        List<Review> reviews() {
            return List.copyOf(reviews);
        }

        Map<String, CheckState> checks() {
            return Map.copyOf(checks);
        }

        Map<String, Boolean> conversations() {
            return Map.copyOf(conversations);
        }
    }

    record MergeDecision(
        boolean eligible,
        int currentApprovals,
        List<String> blockers
    ) {
        MergeDecision {
            blockers = List.copyOf(blockers);
        }
    }

    static final class MergeEligibilityService {
        MergeDecision evaluate(
            PullRequest request,
            ReviewPolicy policy,
            BranchProtection protection
        ) {
            Objects.requireNonNull(request, "request");
            Objects.requireNonNull(policy, "policy");
            Objects.requireNonNull(protection, "protection");

            List<String> blockers = new ArrayList<>();

            if (request.state() != PullRequestState.OPEN) {
                blockers.add("Pull request is not open.");
            }
            if (request.draft()) {
                blockers.add("Draft must be marked ready.");
            }
            if (!request.targetBranch().equals(protection.branchName())) {
                blockers.add("Target branch has no matching evaluated policy.");
            }
            if (request.hasMergeConflict()) {
                blockers.add("Merge conflicts remain.");
            }
            if (policy.requireLinearHistory() && !request.hasLinearHistory()) {
                blockers.add("Linear-history policy is not satisfied.");
            }

            if (
                policy.requireResolvedConversations() &&
                request.conversations().values().stream().anyMatch(
                    resolved -> !resolved
                )
            ) {
                blockers.add("Review conversations remain unresolved.");
            }

            // Map replacement selects the most recent review per reviewer.
            // Filtering by current head makes older approvals stale.
            Map<String, Review> latest = new TreeMap<>();
            for (Review review : request.reviews()) {
                if (
                    review.eligibleReviewer() &&
                    !review.reviewer().equals(request.author()) &&
                    review.commitSha().equals(request.headSha())
                ) {
                    latest.put(review.reviewer(), review);
                }
            }

            long approvals = latest.values().stream()
                .filter(review -> review.state() == ReviewState.APPROVED)
                .count();

            boolean changesRequested = latest.values().stream()
                .anyMatch(
                    review -> review.state() == ReviewState.CHANGES_REQUESTED
                );

            if (approvals < policy.requiredApprovals()) {
                blockers.add("Required approval threshold is not met.");
            }
            if (changesRequested) {
                blockers.add("A current reviewer has requested changes.");
            }

            Map<String, CheckState> actualChecks = request.checks();
            for (String required : policy.requiredChecks()) {
                if (actualChecks.get(required) != CheckState.PASSED) {
                    blockers.add("Required check is not passing: " + required);
                }
            }

            return new MergeDecision(
                blockers.isEmpty(),
                Math.toIntExact(approvals),
                blockers
            );
        }

        void merge(
            PullRequest request,
            ReviewPolicy policy,
            BranchProtection protection
        ) {
            MergeDecision decision = evaluate(request, policy, protection);
            if (!decision.eligible()) {
                throw new IllegalStateException(
                    "Merge denied: " + String.join("; ", decision.blockers())
                );
            }
            request.markMerged();
        }
    }

    public static void main(String[] args) {
        ReviewPolicy policy = new ReviewPolicy(
            2,
            true,
            true,
            false,
            Set.of("unit-tests", "security-scan"),
            true
        );

        BranchProtection protection = new BranchProtection(
            "main",
            true,
            false,
            false,
            false,
            Set.of("release-bot")
        );

        PullRequest request = new PullRequest(
            184,
            "Enforce deployment approval policy",
            "maya",
            "feature/deployment-policy",
            "main",
            "a91c2ef",
            "70bd119",
            false
        );

        MergeEligibilityService service = new MergeEligibilityService();

        request.addReview(new Review(
            "alex", ReviewState.APPROVED, "a91c2ef", true
        ));
        request.addReview(new Review(
            "sam", ReviewState.APPROVED, "a91c2ef", true
        ));
        request.updateCheck("unit-tests", CheckState.PASSED);
        request.updateCheck("security-scan", CheckState.PASSED);
        request.updateConversation("review-thread-17", true);

        System.out.println("Pull request #" + request.number() + ": " + request.title());
        System.out.println(service.evaluate(request, policy, protection));

        request.synchronize("c814d02");
        System.out.println("After source update:");
        System.out.println(service.evaluate(request, policy, protection));

        request.addReview(new Review(
            "alex", ReviewState.APPROVED, "c814d02", true
        ));
        request.addReview(new Review(
            "sam", ReviewState.APPROVED, "c814d02", true
        ));
        request.updateCheck("unit-tests", CheckState.PASSED);
        request.updateCheck("security-scan", CheckState.PASSED);

        MergeDecision finalDecision = service.evaluate(
            request, policy, protection
        );
        System.out.println("After fresh validation: " + finalDecision);

        service.merge(request, policy, protection);
        System.out.println("Final state: " + request.state());

        System.out.println(
            "Developer direct push permitted: " +
            protection.canPushDirectly("maya")
        );
        System.out.println(
            "Release bot direct push permitted: " +
            protection.canPushDirectly("release-bot")
        );

        try {
            request.addReview(new Review(
                "lee", ReviewState.COMMENTED, "c814d02", true
            ));
        } catch (IllegalStateException exception) {
            System.out.println("Post-merge review rejected: " + exception.getMessage());
        }

        PullRequest reopenedExample = new PullRequest(
            185,
            "Update deployment checks",
            "maya",
            "feature/checks",
            "main",
            "f112abc",
            "70bd119",
            true
        );
        reopenedExample.close();
        reopenedExample.reopen();
        System.out.println("Reopened request state: " + reopenedExample.state());

        System.out.println(
            "Required check names: " +
            policy.requiredChecks().stream().sorted().collect(Collectors.joining(", "))
        );
    }
}
