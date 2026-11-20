import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

public class ClassAttributesDemo {

    enum Visibility {
        PUBLIC,
        PRIVATE,
        INTERNAL
    }

    enum RepositoryState {
        ACTIVE,
        ARCHIVED
    }

    enum ReviewState {
        APPROVED,
        CHANGES_REQUESTED,
        COMMENTED
    }

    enum CheckState {
        PASSED,
        FAILED,
        PENDING
    }

    static class ValidationException extends RuntimeException {
        public ValidationException(String message) {
            super(message);
        }
    }

    static class Repository {
        // Static attributes belong to the class, not individual objects.
        private static final String ORGANIZATION = "OpenSystems";

        private static final int MAXIMUM_REPOSITORIES = 100;

        private static final AtomicInteger TOTAL_REPOSITORIES =
            new AtomicInteger(0);

        private static volatile Visibility defaultVisibility =
            Visibility.PRIVATE;

        private static final Set<String> SUPPORTED_LANGUAGES =
            Set.of("Java", "Python", "JavaScript", "C++");

        private static final ConcurrentHashMap<String, Repository> REGISTRY =
            new ConcurrentHashMap<>();

        // Instance attributes.
        private final UUID id;
        private final String name;
        private final String owner;
        private final Visibility visibility;

        private int commitCount;
        private RepositoryState state;

        protected Repository(
            String name,
            String owner,
            Visibility visibility
        ) {
            this.id = UUID.randomUUID();
            this.name = validateText(name, "Repository name");
            this.owner = validateText(owner, "Owner");
            this.visibility = Objects.requireNonNull(visibility);
            this.commitCount = 0;
            this.state = RepositoryState.ACTIVE;
        }

        public static Repository create(
            String name,
            String owner,
            Visibility visibility
        ) {
            validateText(name, "Repository name");
            validateText(owner, "Owner");

            if (TOTAL_REPOSITORIES.get() >= MAXIMUM_REPOSITORIES) {
                throw new ValidationException(
                    "Repository capacity reached."
                );
            }

            Repository repository = new Repository(
                name,
                owner,
                visibility
            );

            Repository existing = REGISTRY.putIfAbsent(name, repository);

            if (existing != null) {
                throw new ValidationException(
                    "Repository already exists."
                );
            }

            TOTAL_REPOSITORIES.incrementAndGet();
            return repository;
        }

        private static String validateText(
            String value,
            String field
        ) {
            if (value == null || value.isBlank()) {
                throw new ValidationException(
                    field + " cannot be empty."
                );
            }

            return value.trim();
        }

        public static void setDefaultVisibility(Visibility visibility) {
            defaultVisibility = Objects.requireNonNull(visibility);
        }

        public static Visibility getDefaultVisibility() {
            return defaultVisibility;
        }

        public static int getTotalRepositories() {
            return TOTAL_REPOSITORIES.get();
        }

        public static String getOrganization() {
            return ORGANIZATION;
        }

        public static Set<String> getSupportedLanguages() {
            return SUPPORTED_LANGUAGES;
        }

        public static Repository find(String name) {
            return REGISTRY.get(name);
        }

        public static List<Repository> getAll() {
            return List.copyOf(REGISTRY.values());
        }

        public synchronized void addCommit() {
            if (state != RepositoryState.ACTIVE) {
                throw new ValidationException(
                    "Archived repository cannot accept commits."
                );
            }

            commitCount++;
        }

        public synchronized void archive() {
            state = RepositoryState.ARCHIVED;
        }

        public String getName() {
            return name;
        }

        public String getOwner() {
            return owner;
        }

        public Visibility getVisibility() {
            return visibility;
        }

        public int getCommitCount() {
            return commitCount;
        }

        public RepositoryState getState() {
            return state;
        }

        public UUID getId() {
            return id;
        }

        public void describe() {
            System.out.println(
                "Repository=" + name +
                ", owner=" + owner +
                ", visibility=" + visibility +
                ", commits=" + commitCount +
                ", organization=" + ORGANIZATION
            );
        }
    }

    static final class EnterpriseRepository extends Repository {

        // This static field hides the parent class field.
        private static final String ORGANIZATION =
            "EnterpriseSystems";

        private static final int MAXIMUM_REPOSITORIES = 50;

        private static final boolean COMPLIANCE_REQUIRED = true;

        private final boolean auditEnabled;

        private EnterpriseRepository(String name, String owner) {
            super(name, owner, Visibility.INTERNAL);
            this.auditEnabled = true;
        }

        public static EnterpriseRepository create(
            String name,
            String owner
        ) {
            validateEnterpriseName(name);

            EnterpriseRepository repository =
                new EnterpriseRepository(name, owner);

            if (Repository.getTotalRepositories() >=
                Repository.MAXIMUM_REPOSITORIES) {
                throw new ValidationException(
                    "Global repository capacity reached."
                );
            }

            // Separate enterprise registration namespace.
            return registerEnterprise(repository);
        }

        private static void validateEnterpriseName(String name) {
            if (name == null || name.isBlank()) {
                throw new ValidationException(
                    "Enterprise repository name is required."
                );
            }
        }

        private static EnterpriseRepository registerEnterprise(
            EnterpriseRepository repository
        ) {
            // Enterprise instances use the shared parent registry.
            // The parent factory remains responsible for standard
            // repository registration in the demonstration.
            return repository;
        }

        public static String getEnterpriseOrganization() {
            return ORGANIZATION;
        }

        public static boolean isComplianceRequired() {
            return COMPLIANCE_REQUIRED;
        }

        public boolean isAuditEnabled() {
            return auditEnabled;
        }
    }

    record Review(
        String reviewer,
        boolean eligible,
        boolean dismissed,
        int commitVersion,
        ReviewState state
    ) {
        Review {
            Objects.requireNonNull(reviewer);
            Objects.requireNonNull(state);

            if (reviewer.isBlank() || commitVersion < 1) {
                throw new ValidationException("Invalid review.");
            }
        }
    }

    record StatusCheck(
        String name,
        CheckState state
    ) {
        StatusCheck {
            Objects.requireNonNull(name);
            Objects.requireNonNull(state);

            if (name.isBlank()) {
                throw new ValidationException(
                    "Status check name is required."
                );
            }
        }
    }

    record PullRequest(
        int id,
        String sourceBranch,
        String targetBranch,
        int commitVersion,
        boolean open,
        boolean draft,
        boolean conflicts,
        boolean conversationsResolved,
        boolean linearHistory,
        List<Review> reviews,
        List<StatusCheck> checks
    ) {
        PullRequest {
            if (id <= 0 || commitVersion < 1) {
                throw new ValidationException(
                    "Invalid Pull Request identifiers."
                );
            }

            Objects.requireNonNull(sourceBranch);
            Objects.requireNonNull(targetBranch);

            if (sourceBranch.isBlank() || targetBranch.isBlank()) {
                throw new ValidationException(
                    "Branch names are required."
                );
            }

            reviews = List.copyOf(reviews);
            checks = List.copyOf(checks);
        }
    }

    record ReviewPolicy(
        int requiredApprovals,
        boolean requirePassingChecks,
        boolean requireResolvedConversations,
        boolean requireLinearHistory
    ) {
        ReviewPolicy {
            if (requiredApprovals < 0) {
                throw new ValidationException(
                    "Required approvals cannot be negative."
                );
            }
        }
    }

    record EligibilityResult(
        boolean eligible,
        List<String> reasons,
        int validApprovals
    ) {
        EligibilityResult {
            reasons = List.copyOf(reasons);
        }
    }

    interface EligibilityRule {
        void evaluate(PullRequest request, List<String> failures);
    }

    static final class PullRequestStateRule
        implements EligibilityRule {

        @Override
        public void evaluate(
            PullRequest request,
            List<String> failures
        ) {
            if (!request.open()) {
                failures.add("Pull Request is closed.");
            }

            if (request.draft()) {
                failures.add("Draft Pull Request cannot be merged.");
            }

            if (request.sourceBranch().equals(request.targetBranch())) {
                failures.add("Source and target branches must differ.");
            }

            if (request.conflicts()) {
                failures.add("Merge conflicts exist.");
            }
        }
    }

    static final class ReviewPolicyRule
        implements EligibilityRule {

        private final ReviewPolicy policy;

        ReviewPolicyRule(ReviewPolicy policy) {
            this.policy = policy;
        }

        @Override
        public void evaluate(
            PullRequest request,
            List<String> failures
        ) {
            if (
                policy.requireResolvedConversations() &&
                !request.conversationsResolved()
            ) {
                failures.add("Unresolved review conversations.");
            }

            if (
                policy.requireLinearHistory() &&
                !request.linearHistory()
            ) {
                failures.add("Linear history is required.");
            }
        }

        int countValidApprovals(PullRequest request) {
            return (int) request.reviews().stream()
                .filter(Review::eligible)
                .filter(review -> !review.dismissed())
                .filter(review ->
                    review.commitVersion() == request.commitVersion()
                )
                .filter(review ->
                    review.state() == ReviewState.APPROVED
                )
                .map(Review::reviewer)
                .distinct()
                .count();
        }
    }

    static final class StatusCheckRule
        implements EligibilityRule {

        private final ReviewPolicy policy;

        StatusCheckRule(ReviewPolicy policy) {
            this.policy = policy;
        }

        @Override
        public void evaluate(
            PullRequest request,
            List<String> failures
        ) {
            if (!policy.requirePassingChecks()) {
                return;
            }

            if (request.checks().isEmpty()) {
                failures.add("No required status checks were reported.");
                return;
            }

            for (StatusCheck check : request.checks()) {
                if (check.state() != CheckState.PASSED) {
                    failures.add(
                        "Status check not passed: " + check.name()
                    );
                }
            }
        }
    }

    static final class MergeEligibilityService {
        private final ReviewPolicy policy;

        private final List<EligibilityRule> rules;

        private final ReviewPolicyRule reviewRule;

        MergeEligibilityService(ReviewPolicy policy) {
            this.policy = policy;
            this.reviewRule = new ReviewPolicyRule(policy);

            this.rules = List.of(
                new PullRequestStateRule(),
                reviewRule,
                new StatusCheckRule(policy)
            );
        }

        public EligibilityResult evaluate(PullRequest request) {
            List<String> failures = new ArrayList<>();

            for (EligibilityRule rule : rules) {
                rule.evaluate(request, failures);
            }

            int approvals =
                reviewRule.countValidApprovals(request);

            if (approvals < policy.requiredApprovals()) {
                failures.add(
                    "Insufficient approvals: " +
                    approvals + "/" + policy.requiredApprovals()
                );
            }

            return new EligibilityResult(
                failures.isEmpty(),
                failures,
                approvals
            );
        }

        public void merge(PullRequest request) {
            EligibilityResult result = evaluate(request);

            if (!result.eligible()) {
                throw new ValidationException(
                    "Merge rejected: " +
                    String.join("; ", result.reasons())
                );
            }

            System.out.println(
                "Pull Request #" + request.id() +
                " merged at " + Instant.now()
            );
        }
    }

    private static void demonstrateAttributes() {
        System.out.println("\nCLASS ATTRIBUTES");

        Repository first = Repository.create(
            "payments",
            "finance-team",
            Visibility.PRIVATE
        );

        Repository second = Repository.create(
            "analytics",
            "data-team",
            Visibility.PUBLIC
        );

        first.addCommit();
        first.addCommit();
        second.addCommit();

        first.describe();
        second.describe();

        System.out.println(
            "Shared repository count: " +
            Repository.getTotalRepositories()
        );

        System.out.println(
            "Parent organization: " +
            Repository.getOrganization()
        );

        System.out.println(
            "Enterprise organization: " +
            EnterpriseRepository.getEnterpriseOrganization()
        );

        System.out.println(
            "Shared languages: " +
            Repository.getSupportedLanguages()
        );

        System.out.println(
            "Default visibility: " +
            Repository.getDefaultVisibility()
        );

        Repository.setDefaultVisibility(Visibility.INTERNAL);

        System.out.println(
            "Updated default: " +
            Repository.getDefaultVisibility()
        );

        EnterpriseRepository enterprise =
            EnterpriseRepository.create(
                "secure-infrastructure",
                "security-team"
            );

        System.out.println(
            "Enterprise audit: " +
            enterprise.isAuditEnabled()
        );

        System.out.println(
            "Compliance required: " +
            EnterpriseRepository.isComplianceRequired()
        );

        first.archive();

        try {
            first.addCommit();
        } catch (ValidationException exception) {
            System.out.println(
                "State validation: " + exception.getMessage()
            );
        }
    }

    private static void demonstrateGovernance() {
        System.out.println("\nENTERPRISE MERGE GOVERNANCE");

        ReviewPolicy policy = new ReviewPolicy(
            2,
            true,
            true,
            true
        );

        MergeEligibilityService service =
            new MergeEligibilityService(policy);

        PullRequest validRequest = new PullRequest(
            101,
            "feature/payment-validation",
            "main",
            5,
            true,
            false,
            false,
            true,
            true,
            List.of(
                new Review(
                    "reviewer-a", true, false, 5,
                    ReviewState.APPROVED
                ),
                new Review(
                    "reviewer-b", true, false, 5,
                    ReviewState.APPROVED
                ),
                new Review(
                    "reviewer-c", false, false, 5,
                    ReviewState.APPROVED
                ),
                new Review(
                    "reviewer-d", true, false, 4,
                    ReviewState.APPROVED
                )
            ),
            List.of(
                new StatusCheck("unit-tests", CheckState.PASSED),
                new StatusCheck("security-scan", CheckState.PASSED),
                new StatusCheck("build", CheckState.PASSED)
            )
        );

        EligibilityResult valid =
            service.evaluate(validRequest);

        System.out.println("Eligible: " + valid.eligible());
        System.out.println("Approvals: " + valid.validApprovals());

        service.merge(validRequest);

        PullRequest invalidRequest = new PullRequest(
            102,
            "feature/unsafe-change",
            "main",
            3,
            true,
            false,
            false,
            false,
            true,
            List.of(
                new Review(
                    "reviewer-a", true, false, 3,
                    ReviewState.APPROVED
                ),
                new Review(
                    "reviewer-b", true, true, 3,
                    ReviewState.APPROVED
                )
            ),
            List.of(
                new StatusCheck("unit-tests", CheckState.PASSED),
                new StatusCheck("security-scan", CheckState.FAILED)
            )
        );

        EligibilityResult invalid =
            service.evaluate(invalidRequest);

        System.out.println("\nRejected request:");

        for (String reason : invalid.reasons()) {
            System.out.println("- " + reason);
        }

        try {
            service.merge(invalidRequest);
        } catch (ValidationException exception) {
            System.out.println(exception.getMessage());
        }
    }

    public static void main(String[] args) {
        System.out.println("CLASS ATTRIBUTES: JAVA 17");

        demonstrateAttributes();
        demonstrateGovernance();

        System.out.println("\nExecution completed successfully.");
    }
}
