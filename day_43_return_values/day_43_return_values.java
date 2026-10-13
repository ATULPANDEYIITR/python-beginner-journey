import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

/*
 * Enterprise repository governance and return-value design.
 *
 * Compile and run with Java 17 or later:
 *   javac ReturnValuesGovernance.java
 *   java ReturnValuesGovernance
 *
 * This model uses typed results for expected failures, exceptions for
 * programming or state-contract violations, immutable records for returned
 * values, and explicit policy evaluation for merge decisions.
 */

public class ReturnValuesGovernance {

    enum PullRequestState {
        OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        APPROVED, CHANGES_REQUESTED, COMMENTED
    }

    enum CheckState {
        PENDING, SUCCESS, FAILURE
    }

    enum MergeStrategy {
        MERGE_COMMIT, SQUASH, REBASE
    }

    record Repository(String name, String defaultBranch) {
        Repository {
            requireText(name, "Repository name");
            requireText(defaultBranch, "Default branch");
        }
    }

    record BranchProtection(
        String branchName,
        int requiredApprovals,
        Set<String> requiredChecks,
        boolean requireResolvedConversations,
        boolean requireLinearHistory,
        boolean prohibitDirectPushes,
        boolean prohibitForcePushes,
        boolean prohibitDeletion,
        boolean allowAdministratorBypass,
        Set<MergeStrategy> permittedStrategies
    ) {
        BranchProtection {
            requireText(branchName, "Branch name");
            if (requiredApprovals < 0 || requiredApprovals > 20) {
                throw new IllegalArgumentException("Invalid approval threshold.");
            }
            requiredChecks = Set.copyOf(requiredChecks);
            permittedStrategies = Set.copyOf(permittedStrategies);
            if (permittedStrategies.isEmpty()) {
                throw new IllegalArgumentException(
                    "At least one merge strategy must be permitted."
                );
            }
        }
    }

    record Review(
        String reviewerId,
        ReviewState state,
        String commitSha,
        String body,
        Instant submittedAt
    ) {
        Review {
            requireText(reviewerId, "Reviewer ID");
            Objects.requireNonNull(state, "Review state");
            requireText(commitSha, "Commit SHA");
            body = body == null ? "" : body;
            Objects.requireNonNull(submittedAt, "Submission time");
        }
    }

    record InlineComment(
        String reviewerId,
        String filePath,
        int line,
        String body,
        boolean resolved
    ) {
        InlineComment {
            requireText(reviewerId, "Reviewer ID");
            requireText(filePath, "File path");
            if (line < 1) {
                throw new IllegalArgumentException("Line number must be positive.");
            }
            requireText(body, "Comment body");
        }

        InlineComment resolve() {
            return new InlineComment(reviewerId, filePath, line, body, true);
        }
    }

    record PullRequest(
        String id,
        String title,
        String authorId,
        String sourceBranch,
        String targetBranch,
        String headSha,
        PullRequestState state,
        boolean draft,
        List<Review
