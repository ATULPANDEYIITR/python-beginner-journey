import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

/*
 * Enterprise repository governance model.
 *
 * The exception hierarchy separates invalid input, invalid transitions,
 * reviewer authorization, policy rejection, and concurrent modification.
 */
public class Main {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewDecision {
        COMMENTED, APPROVED, CHANGES_REQUESTED, DISMISSED
    }

    enum CheckState {
        PENDING, SUCCESS, FAILURE
    }

    enum MergeStrategy {
        MERGE, SQUASH, REBASE
    }

    static class WorkflowException extends RuntimeException {
        private final String code;
        private final boolean retryable;
        private final Map<String, String> context;

        WorkflowException(
                String message,
                String code,
                boolean retryable,
                Map<String, String> context
        ) {
            super(message);
            this.code = code;
            this.retryable = retryable;
            this.context = Collections.unmodifiableMap(
                    new LinkedHashMap<>(context)
            );
        }

        String code() {
            return code;
        }

        boolean retryable() {
            return retryable;
        }

        Map<String, String> context() {
            return context;
        }
    }

    static class ValidationException extends WorkflowException {
        ValidationException(String message) {
            super(message, "VALIDATION_ERROR", false, Map.of());
        }
    }

    static class ResourceNotFoundException extends WorkflowException {
        ResourceNotFoundException(String message) {
            super(message, "RESOURCE_NOT_FOUND", false, Map.of());
        }
    }

    static class StateTransitionException extends WorkflowException {
        StateTransitionException(String message, String state) {
            super(
                    message,
                    "INVALID_STATE_TRANSITION",
                    false,
                    Map.of("state", state)
            );
        }
    }

    static class ReviewerEligibilityException extends WorkflowException {
        ReviewerEligibilityException(String reviewer) {
            super(
                    "Reviewer is not eligible to review this change.",
                    "REVIEWER_NOT_ELIGIBLE",
                    false,
                    Map.of("reviewer", reviewer)
            );
        }
    }

    static class ProtectionViolationException extends WorkflowException {
        ProtectionViolationException(String branch) {
            super(
                    "Direct mutation of protected branch is prohibited.",
                    "BRANCH_PROTECTION_VIOLATION",
                    false,
                    Map.of("branch", branch)
            );
        }
    }

    static class MergeConflictException extends WorkflowException {
        MergeConflictException(int number) {
            super(
                    "Base synchronization produced merge conflicts.",
                    "MERGE_CONFLICT",
                    false,
                    Map.of("pullRequest", Integer.toString(number))
            );
        }
    }

    static class MergeEligibilityException extends WorkflowException {
        private final List<String> reasons;

        MergeEligibilityException(List<String> reasons) {
            super(
                    "Pull Request does not satisfy repository policy.",
                    "MERGE_NOT_ELIGIBLE",
                    false,
                    Map.of("reasonCount", Integer.toString(reasons.size()))
            );
            this.reasons = List.copyOf(reasons);
        }

        List<String> reasons() {
            return reasons;
        }
    }

    static class ConcurrentModificationException extends WorkflowException {
        ConcurrentModificationException(int expected, int actual) {
            super(
                    "Pull Request changed after it was inspected.",
                    "CONCURRENCY_CONFLICT",
                    true,
                    Map.of(
                            "expectedVersion", Integer.toString(expected),
                            "actualVersion", Integer.toString(actual)
                    )
            );
        }
    }

    record CommitRef(
            String sha,
            String parentSha,
            String message,
            String author
    ) {
        CommitRef {
            Objects.requireNonNull(sha);
            Objects.requireNonNull(message);
            Objects.requireNonNull(author);
            if (sha.isBlank() || message.isBlank() || author.isBlank()) {
                throw new ValidationException("Commit fields cannot be blank.");
            }
        }
    }

    record ReviewRecord(
            String reviewer,
            ReviewDecision decision,
            String commitSha,
            String baseSha,
            String body
    ) {
        ReviewRecord {
            Objects.requireNonNull(reviewer);
            Objects.requireNonNull(decision);
            Objects.requireNonNull(commitSha);
            Objects.requireNonNull(baseSha);
            body = body == null ? "" : body;
        }
    }

    record StatusCheck(
            String name,
            String commitSha,
            CheckState state,
            String details
    ) {
        StatusCheck {
            if (name == null || name.isBlank()) {
                throw new ValidationException("Status-check name is required.");
            }
            Objects.requireNonNull(commitSha);
            Objects.requireNonNull(state);
            details = details == null ? "" : details;
        }
    }

    record ReviewDiscussion(
            int id,
            String reviewer,
            String path,
            int line,
            String body,
            boolean resolved
    ) {
        ReviewDiscussion resolve() {
            return new ReviewDiscussion(
                    id, reviewer, path, line, body, true
            );
        }
    }

    static final class Branch {
        private final String name;
        private String headSha;
        private final boolean protectedBranch;
        private boolean deleted;

        Branch(String name, String headSha, boolean protectedBranch) {
            this.name = name;
            this.headSha = headSha;
            this.protectedBranch = protectedBranch;
        }

        String name() {
            return name;
        }

        String headSha() {
            return headSha;
        }

        boolean protectedBranch() {
            return protectedBranch;
        }

        boolean deleted() {
            return deleted;
        }

        void advance(String newHead) {
            if (deleted) {
                throw new StateTransitionException(
                        "A deleted branch cannot be advanced.",
                        "DELETED"
                );
            }
            headSha = newHead;
        }

        void delete() {
            deleted = true;
        }
    }

    /*
     * Policy is immutable. A repository must replace its policy object to
     * change governance settings, making policy changes explicit and auditable.
     */
    record BranchProtectionPolicy(
            int requiredApprovals,
            Set<String> requiredChecks,
            boolean requireConversationResolution,
            boolean requireLinearHistory,
            boolean restrictDirectPush,
            boolean restrictForcePush,
            boolean restrictDeletion,
            boolean dismissStaleReviews,
            boolean enforceAdministrators,
            boolean allowBypass,
            Set<String> bypassUsers,
            Set<MergeStrategy> allowedStrategies
    ) {
        BranchProtectionPolicy {
            if (requiredApprovals < 0) {
                throw new ValidationException(
                        "Required approval count cannot be negative."
                );
            }
            requiredChecks = Set.copyOf(requiredChecks);
            bypassUsers = Set.copyOf(bypassUsers);
            allowedStrategies = Set.copyOf(allowedStrategies);
        }

        static BranchProtectionPolicy standard() {
            return new BranchProtectionPolicy(
                    1,
                    Set.of("unit-tests", "security-scan"),
                    true,
                    true,
                    true,
                    true,
                    true,
                    true,
                    true,
                    false,
                    Set.of(),
                    EnumSet.of(MergeStrategy.SQUASH, MergeStrategy.REBASE)
            );
        }
    }

    static final class PullRequestAggregate {
        private final int number;
        private final String title;
        private final String author;
        private final String sourceBranch;
        private final String targetBranch;
        private PullRequestState state;
        private String baseShaSeen;
        private String mergedSha;
        private boolean hasConflicts;
        private int version = 1;

        private final Set<String> requestedReviewers = new HashSet<>();
        private final List<ReviewRecord> reviews = new ArrayList<>();
        private final List<ReviewDiscussion> discussions = new ArrayList<>();
        private final Map<String, StatusCheck> checks = new HashMap<>();

        PullRequestAggregate(
                int number,
                String title,
                String author,
                String sourceBranch,
                String targetBranch,
                PullRequestState state,
                String baseShaSeen
        ) {
            this.number = number;
            this.title = title;
            this.author = author;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.state = state;
            this.baseShaSeen = baseShaSeen;
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

        PullRequestState state() {
            return state;
        }

        String baseShaSeen() {
            return baseShaSeen;
        }

        boolean hasConflicts() {
            return hasConflicts;
        }

        int version() {
            return version;
        }

        List<ReviewRecord> reviews() {
            return List.copyOf(reviews);
        }

        List<ReviewDiscussion> discussions() {
            return List.copyOf(discussions);
        }

        Map<String, StatusCheck> checks() {
            return Map.copyOf(checks);
        }

        String mergedSha() {
            return mergedSha;
        }

        private void requireState(PullRequestState expected, String operation) {
            if (state != expected) {
                throw new StateTransitionException(
                        operation + " is invalid from the current state.",
                        state.name()
                );
            }
        }

        void markReady() {
            requireState(PullRequestState.DRAFT, "Mark ready");
            state = PullRequestState.OPEN;
            version++;
        }

        void requestReview(String reviewer) {
            requireState(PullRequestState.OPEN, "Request review");
            requestedReviewers.add(reviewer);
            version++;
        }

        void submitReview(ReviewRecord review) {
            requireState(PullRequestState.OPEN, "Submit review");
            reviews.add(review);
            requestedReviewers.remove(review.reviewer());
            version++;
        }

        void dismissLatestReview(String reviewer) {
            requireState(PullRequestState.OPEN, "Dismiss review");
            int index = -1;
            for (int i = reviews.size() - 1; i >= 0; i--) {
                if (reviews.get(i).reviewer().equals(reviewer)) {
                    index = i;
                    break;
                }
            }

            if (index < 0) {
                throw new ResourceNotFoundException(
                        "No review exists for the specified reviewer."
                );
            }

            ReviewRecord old = reviews.get(index);
            reviews.set(
                    index,
                    new ReviewRecord(
                            old.reviewer(),
                            ReviewDecision.DISMISSED,
                            old.commitSha(),
                            old.baseSha(),
                            old.body()
                    )
            );
            version++;
        }

        void addDiscussion(ReviewDiscussion discussion) {
            requireState(PullRequestState.OPEN, "Add discussion");
            discussions.add(discussion);
            version++;
        }

        void resolveDiscussion(int discussionId) {
            requireState(PullRequestState.OPEN, "Resolve discussion");
            for (int i = 0; i < discussions.size(); i++) {
                if (discussions.get(i).id() == discussionId) {
                    discussions.set(i, discussions.get(i).resolve());
                    version++;
                    return;
                }
            }
            throw new ResourceNotFoundException(
                    "Review discussion does not exist."
            );
        }

        void updateCheck(StatusCheck check) {
            requireState(PullRequestState.OPEN, "Update status check");
            checks.put(check.name() + ":" + check.commitSha(), check);
            version++;
        }

        void synchronizeBase(String newBaseSha, boolean conflict) {
            requireState(PullRequestState.OPEN, "Synchronize base");
            hasConflicts = conflict;
            if (conflict) {
                version++;
                throw new MergeConflictException(number);
            }
            baseShaSeen = newBaseSha;
            version++;
        }

        void markMerged(String commitSha) {
            requireState(PullRequestState.OPEN, "Merge");
            state = PullRequestState.MERGED;
            mergedSha = commitSha;
            version++;
        }

        void close() {
            if (state != PullRequestState.OPEN &&
                    state != PullRequestState.DRAFT) {
                throw new StateTransitionException(
                        "Pull Request cannot be closed from this state.",
                        state.name()
                );
            }
            state = PullRequestState.CLOSED;
            version++;
        }

        void reopen() {
            requireState(PullRequestState.CLOSED, "Reopen");
            state = PullRequestState.OPEN;
            version++;
        }
    }

    record EligibilityResult(
            boolean eligible,
            int approvals,
            List<String> reasons,
            boolean bypassApplied
    ) {
        EligibilityResult {
            reasons = List.copyOf(reasons);
        }
    }

    /*
     * MergePolicy separates repository policy from workflow state changes.
     * Additional policy implementations can be supplied without rewriting
     * the Pull Request aggregate.
     */
    interface MergePolicy {
        EligibilityResult evaluate(
                PullRequestAggregate pullRequest,
                Branch source,
                Branch target,
                BranchProtectionPolicy policy,
                MergeStrategy strategy,
                String actor
        );
    }

    static final class StandardMergePolicy implements MergePolicy {

        private Map<String, ReviewRecord> latestReviews(
                PullRequestAggregate pr
        ) {
            Map<String, ReviewRecord> latest = new LinkedHashMap<>();
            for (ReviewRecord review : pr.reviews()) {
                latest.put(review.reviewer(), review);
            }
            return latest;
        }

        @Override
        public EligibilityResult evaluate(
                PullRequestAggregate pr,
                Branch source,
                Branch target,
                BranchProtectionPolicy policy,
                MergeStrategy strategy,
                String actor
        ) {
            List<String> reasons = new ArrayList<>();

            boolean bypass =
                    policy.allowBypass() &&
                    !policy.enforceAdministrators() &&
                    policy.bypassUsers().contains(actor);

            if (pr.state() != PullRequestState.OPEN) {
                reasons.add("Pull Request is not open.");
            }
            if (!pr.baseShaSeen().equals(target.headSha())) {
                reasons.add("Base branch must be synchronized.");
            }
            if (pr.hasConflicts()) {
                reasons.add("Merge conflicts remain unresolved.");
            }
            if (!policy.allowedStrategies().contains(strategy)) {
                reasons.add("Merge strategy is not permitted.");
            }
            if (policy.requireLinearHistory() &&
                    strategy == MergeStrategy.MERGE) {
                reasons.add("Selected merge strategy violates linear history.");
            }

            Map<String, ReviewRecord> latest = latestReviews(pr);
            List<ReviewRecord> applicable = latest.values().stream()
                    .filter(review ->
                            review.decision() != ReviewDecision.DISMISSED)
                    .filter(review ->
                            !policy.dismissStaleReviews() ||
                            review.commitSha().equals(source.headSha()))
                    .toList();

            int approvals = (int) applicable.stream()
                    .filter(review ->
                            review.decision() == ReviewDecision.APPROVED)
                    .count();

            boolean changesRequested = applicable.stream()
                    .anyMatch(review ->
                            review.decision() == ReviewDecision.CHANGES_REQUESTED);

            if (!bypass) {
                if (approvals < policy.requiredApprovals()) {
                    reasons.add(
                            "Insufficient current approvals: " + approvals +
                            " of " + policy.requiredApprovals() + "."
                    );
                }
                if (changesRequested) {
                    reasons.add("A reviewer has requested changes.");
                }

                List<String> missingChecks = policy.requiredChecks().stream()
                        .filter(name -> {
                            StatusCheck check = pr.checks().get(
                                    name + ":" + source.headSha()
                            );
                            return check == null ||
                                    check.state() != CheckState.SUCCESS;
                        })
                        .sorted()
                        .toList();

                if (!missingChecks.isEmpty()) {
                    reasons.add(
                            "Missing or unsuccessful checks: " +
                            String.join(", ", missingChecks)
                    );
                }

                boolean unresolved = pr.discussions().stream()
                        .anyMatch(discussion -> !discussion.resolved());
                if (policy.requireConversationResolution() && unresolved) {
                    reasons.add("Review discussions remain unresolved.");
                }
            }

            return new EligibilityResult(
                    reasons.isEmpty(),
                    approvals,
                    reasons,
                    bypass
            );
        }
    }

    static final class GovernanceService {
        private final Map<String, Branch> branches = new HashMap<>();
        private final Map<String, CommitRef> commits = new HashMap<>();
        private final Map<Integer, PullRequestAggregate> pullRequests =
                new HashMap<>();
        private final Set<String> eligibleReviewers;
        private final BranchProtectionPolicy protection;
        private final MergePolicy mergePolicy;
        private final AtomicInteger commitSequence = new AtomicInteger();
        private int nextPullRequest = 0;
        private int nextDiscussion = 0;

        GovernanceService(
                Set<String> eligibleReviewers,
                BranchProtectionPolicy protection,
                MergePolicy mergePolicy
        ) {
            this.eligibleReviewers = Set.copyOf(eligibleReviewers);
            this.protection = protection;
            this.mergePolicy = mergePolicy;

            CommitRef root = createCommit(
                    "Initial repository state",
                    null,
                    "system"
            );
            branches.put("main", new Branch("main", root.sha(), true));
        }

        private CommitRef createCommit(
                String message,
                String parentSha,
                String author
        ) {
            String sha = "commit-" + commitSequence.incrementAndGet();
            CommitRef commit = new CommitRef(
                    sha, parentSha, message, author
            );
            commits.put(sha, commit);
            return commit;
        }

        private Branch requireBranch(String name) {
            Branch branch = branches.get(name);
            if (branch == null || branch.deleted()) {
                throw new ResourceNotFoundException(
                        "Branch '" + name + "' does not exist."
                );
            }
            return branch;
        }

        private PullRequestAggregate requirePullRequest(int number) {
            PullRequestAggregate pr = pullRequests.get(number);
            if (pr == null) {
                throw new ResourceNotFoundException(
                        "Pull Request #" + number + " does not exist."
                );
            }
            return pr;
        }

        private boolean canBypass(String actor) {
            return protection.allowBypass() &&
                    !protection.enforceAdministrators() &&
                    protection.bypassUsers().contains(actor);
        }

        void createBranch(String name, String fromBranch) {
            if (name == null || name.isBlank()) {
                throw new ValidationException("Branch name is required.");
            }
            Branch parent = requireBranch(fromBranch);
            if (branches.containsKey(name) && !branches.get(name).deleted()) {
                throw new ValidationException("Branch already exists.");
            }
            branches.put(name, new Branch(name, parent.headSha(), false));
        }

        CommitRef pushCommit(
                String branchName,
                String message,
                String author,
                boolean force
        ) {
            Branch branch = requireBranch(branchName);
            boolean bypass = canBypass(author);

            if (branch.protectedBranch() && !bypass) {
                if (protection.restrictDirectPush()) {
                    throw new ProtectionViolationException(branchName);
                }
                if (force && protection.restrictForcePush()) {
                    throw new ProtectionViolationException(branchName);
                }
            }

            CommitRef commit = createCommit(
                    message,
                    branch.headSha(),
                    author
            );
            branch.advance(commit.sha());

            // A source-head change invalidates reviews tied to the old SHA.
            pullRequests.values().stream()
                    .filter(pr -> pr.sourceBranch().equals(branchName))
                    .filter(pr -> pr.state() == PullRequestState.OPEN ||
                            pr.state() == PullRequestState.DRAFT)
                    .forEach(pr -> {
                        // The aggregate version is changed through its normal
                        // workflow methods; a new check or review is required.
                    });

            return commit;
        }

        int createPullRequest(
                String title,
                String sourceBranch,
                String targetBranch,
                String author,
                boolean draft
        ) {
            Branch source = requireBranch(sourceBranch);
            Branch target = requireBranch(targetBranch);

            if (title == null || title.isBlank() ||
                    author == null || author.isBlank()) {
                throw new ValidationException(
                        "Pull Request title and author are required."
                );
            }
            if (sourceBranch.equals(targetBranch)) {
                throw new ValidationException(
                        "Source and target branches must differ."
                );
            }
            if (source.headSha().equals(target.headSha())) {
                throw new ValidationException(
                        "The source branch contains no new commits."
                );
            }

            boolean duplicate = pullRequests.values().stream()
                    .anyMatch(pr ->
                            pr.sourceBranch().equals(sourceBranch) &&
                            pr.targetBranch().equals(targetBranch) &&
                            (pr.state() == PullRequestState.OPEN ||
                             pr.state() == PullRequestState.DRAFT));
            if (duplicate) {
                throw new ValidationException(
                        "An active Pull Request already exists."
                );
            }

            int number = ++nextPullRequest;
            PullRequestAggregate pr = new PullRequestAggregate(
                    number,
                    title,
                    author,
                    sourceBranch,
                    targetBranch,
                    draft ? PullRequestState.DRAFT : PullRequestState.OPEN,
                    target.headSha()
            );
            pullRequests.put(number, pr);
            return number;
        }

        void readyForReview(int number) {
            requirePullRequest(number).markReady();
        }

        void requestReview(int number, String reviewer) {
            PullRequestAggregate pr = requirePullRequest(number);
            if (reviewer.equals(pr.author()) ||
                    !eligibleReviewers.contains(reviewer)) {
                throw new ReviewerEligibilityException(reviewer);
            }
            pr.requestReview(reviewer);
        }

        void submitReview(
                int number,
                String reviewer,
                ReviewDecision decision,
                String body
        ) {
            PullRequestAggregate pr = requirePullRequest(number);
            if (reviewer.equals(pr.author()) ||
                    !eligibleReviewers.contains(reviewer)) {
                throw new ReviewerEligibilityException(reviewer);
            }

            String sourceHead = requireBranch(pr.sourceBranch()).headSha();
            String targetHead = requireBranch(pr.targetBranch()).headSha();

            pr.submitReview(
                    new ReviewRecord(
                            reviewer,
                            decision,
                            sourceHead,
                            targetHead,
                            body
                    )
            );
        }

        int addDiscussion(
                int number,
                String reviewer,
                String path,
                int line,
                String body
        ) {
            PullRequestAggregate pr = requirePullRequest(number);
            if (reviewer.equals(pr.author()) ||
                    !eligibleReviewers.contains(reviewer)) {
                throw new ReviewerEligibilityException(reviewer);
            }
            if (path == null || path.isBlank() ||
                    body == null || body.isBlank() || line < 1) {
                throw new ValidationException(
                        "Discussion requires a path, body, and positive line."
                );
            }

            int id = ++nextDiscussion;
            pr.addDiscussion(
                    new ReviewDiscussion(
                            id, reviewer, path, line, body, false
                    )
            );
            return id;
        }

        void resolveDiscussion(int number, int discussionId) {
            requirePullRequest(number).resolveDiscussion(discussionId);
        }

        void setStatusCheck(
                int number,
                String name,
                CheckState state,
                String details
        ) {
            PullRequestAggregate pr = requirePullRequest(number);
            String currentHead = requireBranch(pr.sourceBranch()).headSha();

            pr.updateCheck(
                    new StatusCheck(name, currentHead, state, details)
            );
        }

        void synchronizeBase(int number, boolean conflict) {
            PullRequestAggregate pr = requirePullRequest(number);
            String targetHead = requireBranch(pr.targetBranch()).headSha();
            pr.synchronizeBase(targetHead, conflict);
        }

        EligibilityResult evaluate(
                int number,
                MergeStrategy strategy,
                String actor
        ) {
            PullRequestAggregate pr = requirePullRequest(number);
            return mergePolicy.evaluate(
                    pr,
                    requireBranch(pr.sourceBranch()),
                    requireBranch(pr.targetBranch()),
                    protection,
                    strategy,
                    actor
            );
        }

        CommitRef merge(
                int number,
                MergeStrategy strategy,
                String actor,
                int expectedVersion
        ) {
            PullRequestAggregate pr = requirePullRequest(number);

            if (expectedVersion != 0 && expectedVersion != pr.version()) {
                throw new ConcurrentModificationException(
                        expectedVersion,
                        pr.version()
                );
            }

            EligibilityResult result = evaluate(number, strategy, actor);
            if (!result.eligible()) {
                throw new MergeEligibilityException(result.reasons());
            }

            Branch target = requireBranch(pr.targetBranch());
            CommitRef mergeCommit = createCommit(
                    strategy + " Pull Request #" + number + ": " + pr.title(),
                    target.headSha(),
                    actor
            );

            target.advance(mergeCommit.sha());
            pr.markMerged(mergeCommit.sha());
            return mergeCommit;
        }

        void closePullRequest(int number) {
            requirePullRequest(number).close();
        }

        void reopenPullRequest(int number) {
            requirePullRequest(number).reopen();
        }
    }

    private static void printError(WorkflowException error) {
        System.out.println(
                error.code() + ": " + error.getMessage() +
                " | retryable=" + error.retryable() +
                " | context=" + error.context()
        );
    }

    public static void main(String[] args) {
        BranchProtectionPolicy policy =
                BranchProtectionPolicy.standard();

        GovernanceService service = new GovernanceService(
                Set.of("bob", "carol", "dave"),
                policy,
                new StandardMergePolicy()
        );

        try {
            service.createBranch(
                    "feature/refund-validation",
                    "main"
            );
            service.pushCommit(
                    "feature/refund-validation",
                    "Validate refund amounts",
                    "alice",
                    false
            );

            int number = service.createPullRequest(
                    "Add refund validation",
                    "feature/refund-validation",
                    "main",
                    "alice",
                    true
            );

            service.readyForReview(number);
            service.requestReview(number, "bob");

            int discussion = service.addDiscussion(
                    number,
                    "bob",
                    "payments/RefundService.java",
                    62,
                    "Validate the amount before submitting the refund."
            );
            service.resolveDiscussion(number, discussion);

            service.setStatusCheck(
                    number,
                    "unit-tests",
                    CheckState.SUCCESS,
                    "All tests passed"
            );
            service.setStatusCheck(
                    number,
                    "security-scan",
                    CheckState.SUCCESS,
                    "No critical findings"
            );
            service.submitReview(
                    number,
                    "bob",
                    ReviewDecision.APPROVED,
                    "The validation is correct."
            );

            EligibilityResult report = service.evaluate(
                    number,
                    MergeStrategy.SQUASH,
                    "alice"
            );

            System.out.println("Pull Request #" + number);
            System.out.println("Eligible: " + report.eligible());
            System.out.println("Approvals: " + report.approvals());
            report.reasons().forEach(reason ->
                    System.out.println("  - " + reason)
            );

            PullRequestAggregate pr = service.requirePullRequest(number);
            CommitRef merge = service.merge(
                    number,
                    MergeStrategy.SQUASH,
                    "alice",
                    pr.version()
            );
            System.out.println("Merged as " + merge.sha());

            try {
                service.pushCommit(
                        "main",
                        "Unauthorized direct write",
                        "alice",
                        false
                );
            } catch (ProtectionViolationException error) {
                System.out.println("\nProtected branch rejection:");
                printError(error);
            }

            service.createBranch("feature/second-change", "main");
            service.pushCommit(
                    "feature/second-change",
                    "Add another validation rule",
                    "alice",
                    false
            );

            int second = service.createPullRequest(
                    "Add another validation rule",
                    "feature/second-change",
                    "main",
                    "alice",
                    false
            );

            try {
                service.submitReview(
                        second,
                        "alice",
                        ReviewDecision.APPROVED,
                        "Self approval"
                );
            } catch (ReviewerEligibilityException error) {
                System.out.println("\nSelf-review rejection:");
                printError(error);
            }

            service.submitReview(
                    second,
                    "bob",
                    ReviewDecision.APPROVED,
                    "Approved before the next source commit."
            );

            service.pushCommit(
                    "feature/second-change",
                    "Correct an amount boundary condition",
                    "alice",
                    false
            );

            // Current-head checks do not make an old approval current.
            service.setStatusCheck(
                    second,
                    "unit-tests",
                    CheckState.SUCCESS,
                    "Tests passed"
            );
            service.setStatusCheck(
                    second,
                    "security-scan",
                    CheckState.SUCCESS,
                    "Scan passed"
            );

            EligibilityResult staleResult = service.evaluate(
                    second,
                    MergeStrategy.SQUASH,
                    "alice"
            );
            System.out.println("\nEligibility after source update:");
            System.out.println("Eligible: " + staleResult.eligible());
            staleResult.reasons().forEach(reason ->
                    System.out.println("  - " + reason)
            );

            try {
                service.merge(
                        second,
                        MergeStrategy.SQUASH,
                        "alice",
                        0
                );
            } catch (MergeEligibilityException error) {
                System.out.println("\nMerge rejection:");
                printError(error);
                error.reasons().forEach(reason ->
                        System.out.println("  - " + reason)
                );
            }

        } catch (WorkflowException error) {
            printError(error);
            System.exit(1);
        }
    }
}
