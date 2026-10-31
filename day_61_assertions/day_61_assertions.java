import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public class AssertionsDemo {

    enum PullRequestState {
        DRAFT,
        OPEN,
        MERGED,
        CLOSED
    }

    static class ValidationException extends IllegalArgumentException {
        ValidationException(String message) {
            super(message);
        }
    }

    record Review(String reviewer, boolean approved, boolean unresolvedComments) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new ValidationException("reviewer identity is required");
            }
        }
    }

    static final class Repository {
        private final String name;
        private final String defaultBranch;
        private final Set<String> commits = new HashSet<>();

        Repository(String name, String defaultBranch) {
            if (name == null || name.isBlank()) {
                throw new ValidationException("repository name is required");
            }
            if (defaultBranch == null || defaultBranch.isBlank()) {
                throw new ValidationException("default branch is required");
            }

            this.name = name;
            this.defaultBranch = defaultBranch;
            checkInvariants();
        }

        void addCommit(String commitId) {
            if (commitId == null || commitId.isBlank()) {
                throw new ValidationException("commit ID is required");
            }

            if (!commits.add(commitId)) {
                throw new ValidationException("duplicate commit ID");
            }

            assert commits.contains(commitId) : "commit insertion invariant failed";
            checkInvariants();
        }

        int commitCount() {
            return commits.size();
        }

        private void checkInvariants() {
            assert name != null && !name.isBlank()
                    : "repository name invariant failed";
            assert defaultBranch != null && !defaultBranch.isBlank()
                    : "default branch invariant failed";
        }
    }

    static final class PullRequest {
        private final int number;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<String> commits = new ArrayList<>();
        private final List<Review> reviews = new ArrayList<>();
        private PullRequestState state = PullRequestState.DRAFT;

        PullRequest(int number, String sourceBranch, String targetBranch) {
            if (number <= 0) {
                throw new ValidationException("PR number must be positive");
            }
            if (sourceBranch == null || targetBranch == null ||
                    sourceBranch.isBlank() || targetBranch.isBlank()) {
                throw new ValidationException("branch names are required");
            }
            if (sourceBranch.equals(targetBranch)) {
                throw new ValidationException(
                        "source and target branches must differ"
                );
            }

            this.number = number;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            checkInvariants();
        }

        void addCommit(String commitId) {
            if (state == PullRequestState.MERGED) {
                throw new ValidationException(
                        "merged pull request cannot receive commits"
                );
            }
            if (commitId == null || commitId.isBlank()) {
                throw new ValidationException("commit ID is required");
            }
            if (commits.contains(commitId)) {
                throw new ValidationException("duplicate pull request commit");
            }

            commits.add(commitId);
            checkInvariants();
        }

        void addReview(Review review) {
            reviews.add(Objects.requireNonNull(review, "review cannot be null"));
            checkInvariants();
        }

        void markReady() {
            if (state == PullRequestState.MERGED) {
                throw new ValidationException(
                        "merged pull request cannot become ready"
                );
            }

            state = PullRequestState.OPEN;
            checkInvariants();
        }

        boolean hasApproval() {
            return reviews.stream()
                    .anyMatch(review ->
                            review.approved() && !review.unresolvedComments());
        }

        boolean hasUnresolvedComments() {
            return reviews.stream()
                    .anyMatch(Review::unresolvedComments);
        }

        boolean canMerge() {
            return state == PullRequestState.OPEN
                    && !commits.isEmpty()
                    && hasApproval()
                    && !hasUnresolvedComments();
        }

        void merge() {
            if (!canMerge()) {
                throw new ValidationException(
                        "pull request does not satisfy merge eligibility"
                );
            }

            state = PullRequestState.MERGED;
            checkInvariants();
        }

        PullRequestState state() {
            return state;
        }

        private void checkInvariants() {
            assert number > 0 : "PR number invariant failed";
            assert !sourceBranch.equals(targetBranch)
                    : "branch invariant failed";

            if (state == PullRequestState.MERGED) {
                assert !commits.isEmpty()
                        : "merged PR must contain a commit";
            }
        }
    }

    interface AssertionPolicy<T> {
        void validate(T value);
    }

    static final class RangePolicy implements AssertionPolicy<Integer> {
        private final int minimum;
        private final int maximum;

        RangePolicy(int minimum, int maximum) {
            if (minimum > maximum) {
                throw new ValidationException("minimum cannot exceed maximum");
            }
            this.minimum = minimum;
            this.maximum = maximum;
        }

        @Override
        public void validate(Integer value) {
            if (value == null || value < minimum || value > maximum) {
                throw new ValidationException(
                        "value must be between " + minimum + " and " + maximum
                );
            }
        }
    }

    static double average(List<Double> values) {
        if (values == null || values.isEmpty()) {
            throw new ValidationException("at least one value is required");
        }

        if (values.stream().anyMatch(value ->
                value == null || !Double.isFinite(value))) {
            throw new ValidationException("values must be finite numbers");
        }

        double result = values.stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElseThrow();

        double minimum = values.stream()
                .mapToDouble(Double::doubleValue)
                .min()
                .orElseThrow();

        double maximum = values.stream()
                .mapToDouble(Double::doubleValue)
                .max()
                .orElseThrow();

        assert result >= minimum : "average lower-bound postcondition failed";
        assert result <= maximum : "average upper-bound postcondition failed";

        return result;
    }

    static void runTests() {
        Repository repository = new Repository("assertion-lab", "main");
        repository.addCommit("c1");
        repository.addCommit("c2");

        assert repository.commitCount() == 2;

        try {
            repository.addCommit("c1");
            throw new AssertionError("duplicate commit should have failed");
        } catch (ValidationException expected) {
            // Expected external-input failure.
        }

        PullRequest pullRequest =
                new PullRequest(42, "feature/assertions", "main");

        pullRequest.addCommit("c1");
        pullRequest.addCommit("c2");
        pullRequest.addReview(new Review("reviewer-a", true, false));
        pullRequest.markReady();

        assert pullRequest.canMerge();

        pullRequest.merge();

        assert pullRequest.state() == PullRequestState.MERGED;

        try {
            pullRequest.addCommit("c3");
            throw new AssertionError("merged PR accepted a commit");
        } catch (ValidationException expected) {
            // Expected state-transition failure.
        }

        RangePolicy priorityPolicy = new RangePolicy(1, 5);
        priorityPolicy.validate(3);

        assert average(List.of(10.0, 20.0, 30.0)) == 20.0;

        try {
            average(List.of());
            throw new AssertionError("empty average should have failed");
        } catch (ValidationException expected) {
            // Expected validation failure.
        }
    }

    public static void main(String[] args) {
        runTests();
        System.out.println(
                "All Java 17 assertion demonstrations and tests passed."
        );
    }
}
