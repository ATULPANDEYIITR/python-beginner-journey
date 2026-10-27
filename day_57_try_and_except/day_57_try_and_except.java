import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class ExceptionWorkflowDemo {

    enum PullRequestState {
        DRAFT,
        OPEN,
        BLOCKED,
        MERGEABLE,
        MERGED,
        CLOSED
    }

    enum ReviewDecision {
        PENDING,
        APPROVED,
        CHANGES_REQUESTED,
        REJECTED
    }

    record Review(
        String reviewer,
        ReviewDecision decision,
        boolean dismissed
    ) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new ValidationException("Reviewer is required.");
            }
            Objects.requireNonNull(decision, "Review decision is required.");
        }

        boolean activeApproval() {
            return decision == ReviewDecision.APPROVED && !dismissed;
        }

        boolean activeChangeRequest() {
            return decision == ReviewDecision.CHANGES_REQUESTED && !dismissed;
        }
    }

    record StatusCheck(String name, boolean passed) {
        StatusCheck {
            if (name == null || name.isBlank()) {
                throw new ValidationException("Status check name is required.");
            }
        }
    }

    record PullRequest(
        int number,
        String sourceBranch,
        String targetBranch,
        PullRequestState state,
        List<Review> reviews,
        List<StatusCheck> checks,
        int unresolvedConversations
    ) {
        PullRequest {
            if (number <= 0) {
                throw new ValidationException("Pull Request number must be positive.");
            }

            validateBranch(sourceBranch);
            validateBranch(targetBranch);

            if (sourceBranch.equals(targetBranch)) {
                throw new ValidationException(
                    "Source and target branches must differ."
                );
            }

            if (unresolvedConversations < 0) {
                throw new ValidationException(
                    "Unresolved conversations cannot be negative."
                );
            }

            reviews = List.copyOf(reviews);
            checks = List.copyOf(checks);
        }

        private static void validateBranch(String branch) {
            if (branch == null || branch.isBlank()) {
                throw new ValidationException("Branch name is required.");
            }

            if (branch.length() > 255) {
                throw new ValidationException("Branch name is too long.");
            }
        }
    }

    static class RepositoryException extends RuntimeException {
        RepositoryException(String message) {
            super(message);
        }

        RepositoryException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    static class ValidationException extends RepositoryException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class MergePolicyException extends RepositoryException {
        MergePolicyException(String message) {
            super(message);
        }
    }

    interface MergePolicy {
        boolean isEligible(PullRequest pullRequest);
    }

    static final class ProtectedBranchPolicy implements MergePolicy {
        private final int requiredApprovals;
        private final boolean requirePassedChecks;
        private final boolean requireResolvedConversations;

        ProtectedBranchPolicy(
            int requiredApprovals,
            boolean requirePassedChecks,
            boolean requireResolvedConversations
        ) {
            if (requiredApprovals < 0) {
                throw new ValidationException(
                    "Required approvals cannot be negative."
                );
            }

            this.requiredApprovals = requiredApprovals;
            this.requirePassedChecks = requirePassedChecks;
            this.requireResolvedConversations =
                requireResolvedConversations;
        }

        @Override
        public boolean isEligible(PullRequest pullRequest) {
            Objects.requireNonNull(
                pullRequest,
                "Pull Request cannot be null."
            );

            if (pullRequest.state() == PullRequestState.MERGED ||
                pullRequest.state() == PullRequestState.CLOSED ||
                pullRequest.state() == PullRequestState.DRAFT) {
                return false;
            }

            boolean changesRequested = pullRequest.reviews()
                .stream()
                .anyMatch(Review::activeChangeRequest);

            if (changesRequested) {
                return false;
            }

            long approvals = pullRequest.reviews()
                .stream()
                .filter(Review::activeApproval)
                .count();

            if (approvals < requiredApprovals) {
                return false;
            }

            if (requirePassedChecks &&
                (pullRequest.checks().isEmpty() ||
                 pullRequest.checks().stream().anyMatch(
                     check -> !check.passed()
                 ))) {
                return false;
            }

            if (requireResolvedConversations &&
                pullRequest.unresolvedConversations() > 0) {
                return false;
            }

            return true;
        }
    }

    static final class PullRequestService {
        private final MergePolicy policy;

        PullRequestService(MergePolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        PullRequest merge(PullRequest pullRequest) {
            try {
                if (!policy.isEligible(pullRequest)) {
                    throw new MergePolicyException(
                        "Pull Request does not satisfy the merge policy."
                    );
                }

                return new PullRequest(
                    pullRequest.number(),
                    pullRequest.sourceBranch(),
                    pullRequest.targetBranch(),
                    PullRequestState.MERGED,
                    pullRequest.reviews(),
                    pullRequest.checks(),
                    pullRequest.unresolvedConversations()
                );
            } catch (MergePolicyException exception) {
                throw exception;
            } catch (RuntimeException exception) {
                throw new RepositoryException(
                    "Unexpected failure while merging Pull Request.",
                    exception
                );
            }
        }
    }

    static void process(PullRequest request, PullRequestService service) {
        try {
            PullRequest result = service.merge(request);

            System.out.printf(
                "PR #%d merged successfully. State: %s%n",
                result.number(),
                result.state()
            );
        } catch (MergePolicyException exception) {
            System.out.printf(
                "PR #%d blocked: %s%n",
                request.number(),
                exception.getMessage()
            );
        } catch (ValidationException exception) {
            System.out.printf(
                "PR #%d validation failure: %s%n",
                request.number(),
                exception.getMessage()
            );
        } catch (RepositoryException exception) {
            System.out.printf(
                "PR #%d repository failure: %s%n",
                request.number(),
                exception.getMessage()
            );
        }
    }

    static PullRequest buildValidRequest() {
        return new PullRequest(
            201,
            "feature/reliable-exceptions",
            "main",
            PullRequestState.OPEN,
            List.of(
                new Review("alice", ReviewDecision.APPROVED, false),
                new Review("bob", ReviewDecision.APPROVED, false)
            ),
            List.of(
                new StatusCheck("build", true),
                new StatusCheck("tests", true),
                new StatusCheck("security", true)
            ),
            0
        );
    }

    static PullRequest buildBlockedRequest() {
        return new PullRequest(
            202,
            "feature/incomplete-work",
            "main",
            PullRequestState.OPEN,
            List.of(
                new Review("alice", ReviewDecision.APPROVED, false)
            ),
            List.of(
                new StatusCheck("build", true),
                new StatusCheck("security", false)
            ),
            2
        );
    }

    public static void main(String[] args) {
        try {
            MergePolicy policy =
                new ProtectedBranchPolicy(2, true, true);

            PullRequestService service =
                new PullRequestService(policy);

            PullRequest valid = buildValidRequest();
            PullRequest blocked = buildBlockedRequest();

            process(valid, service);
            process(blocked, service);

            try {
                new PullRequest(
                    203,
                    "",
                    "main",
                    PullRequestState.OPEN,
                    List.of(),
                    List.of(),
                    0
                );
            } catch (ValidationException exception) {
                System.out.println(
                    "Expected validation failure: " +
                    exception.getMessage()
                );
            }

            try {
                Map<String, String> configuration =
                    Map.of("requiredApprovals", "not-a-number");

                int requiredApprovals = Integer.parseInt(
                    configuration.get("requiredApprovals")
                );

                System.out.println(requiredApprovals);
            } catch (NumberFormatException exception) {
                System.out.println(
                    "Configuration parsing failed: " +
                    exception.getMessage()
                );
            }

        } catch (RepositoryException exception) {
            System.err.println(
                "Fatal repository error: " +
                exception.getMessage()
            );
        }
    }
}
