import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/*
 * COMPOSITION IN JAVA 17
 *
 * Enterprise scenario: Document processing and approval platform.
 *
 * Demonstrates:
 * - Object composition
 * - Interfaces and delegation
 * - Records and immutable domain types
 * - Dependency injection
 * - Service composition
 * - Strategy composition
 * - Policy evaluation
 * - State transitions
 * - Asynchronous processing
 * - Validation and custom exceptions
 *
 * Compile:
 * javac CompositionDemo.java
 *
 * Run:
 * java CompositionDemo
 */

public class CompositionDemo {

    // -------------------------------------------------
    // 1. Domain exceptions
    // -------------------------------------------------

    static class CompositionException extends RuntimeException {
        public CompositionException(String message) {
            super(message);
        }

        public CompositionException(String message, Throwable cause) {
            super(message, cause);
        }
    }


    // -------------------------------------------------
    // 2. Immutable domain records
    // -------------------------------------------------

    record Document(
        String documentId,
        String owner,
        String content,
        String classification
    ) {
        Document {
            requireText(documentId, "documentId");
            requireText(owner, "owner");
            requireText(content, "content");
            requireText(classification, "classification");
        }
    }


    record ReviewDecision(
        String reviewer,
        Decision decision,
        String comment
    ) {
        ReviewDecision {
            requireText(reviewer, "reviewer");
            Objects.requireNonNull(decision);
            requireText(comment, "comment");
        }
    }


    enum Decision {
        APPROVE,
        REJECT,
        REQUEST_CHANGES
    }


    enum DocumentStatus {
        DRAFT,
        SUBMITTED,
        UNDER_REVIEW,
        APPROVED,
        REJECTED
    }


    private static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                field + " cannot be empty"
            );
        }
    }


    // -------------------------------------------------
    // 3. Component interfaces
    // -------------------------------------------------

    interface DocumentValidator {
        void validate(Document document);
    }

    interface DocumentStorage {
        void save(Document document);
        Document find(String documentId);
    }

    interface NotificationSender {
        CompletableFuture<Void> send(
            String recipient,
            String message
        );
    }


    // -------------------------------------------------
    // 4. Independent component implementations
    // -------------------------------------------------

    static class ClassificationValidator
            implements DocumentValidator {

        private final Set<String> permittedClassifications;

        ClassificationValidator(Set<String> classifications) {
            this.permittedClassifications =
                Set.copyOf(classifications);
        }

        @Override
        public void validate(Document document) {
            if (!permittedClassifications.contains(
                document.classification()
            )) {
                throw new CompositionException(
                    "Unsupported document classification"
                );
            }
        }
    }


    static class ContentValidator
            implements DocumentValidator {

        private final int maximumLength;

        ContentValidator(int maximumLength) {
            if (maximumLength <= 0) {
                throw new IllegalArgumentException(
                    "Maximum length must be positive"
                );
            }

            this.maximumLength = maximumLength;
        }

        @Override
        public void validate(Document document) {
            if (document.content().length() > maximumLength) {
                throw new CompositionException(
                    "Document exceeds maximum content length"
                );
            }
        }
    }


    static class CompositeValidator
            implements DocumentValidator {

        private final List<DocumentValidator> validators;

        CompositeValidator(List<DocumentValidator> validators) {
            this.validators = List.copyOf(validators);

            if (this.validators.isEmpty()) {
                throw new IllegalArgumentException(
                    "At least one validator is required"
                );
            }
        }

        @Override
        public void validate(Document document) {
            for (DocumentValidator validator : validators) {
                validator.validate(document);
            }
        }
    }


    // -------------------------------------------------
    // 5. Storage component
    // -------------------------------------------------

    static class InMemoryDocumentStorage
            implements DocumentStorage {

        private final Map<String, Document> documents =
            new ConcurrentHashMap<>();

        @Override
        public void save(Document document) {
            Objects.requireNonNull(document);

            documents.put(
                document.documentId(),
                document
            );
        }

        @Override
        public Document find(String documentId) {
            Document document = documents.get(documentId);

            if (document == null) {
                throw new CompositionException(
                    "Document not found: " + documentId
                );
            }

            return document;
        }
    }


    // -------------------------------------------------
    // 6. Notification component
    // -------------------------------------------------

    static class ConsoleNotificationSender
            implements NotificationSender {

        @Override
        public CompletableFuture<Void> send(
            String recipient,
            String message
        ) {
            return CompletableFuture.runAsync(() -> {
                System.out.println(
                    "[NOTIFICATION] "
                    + recipient
                    + ": "
                    + message
                );
            });
        }
    }


    // -------------------------------------------------
    // 7. Review policy composition
    // -------------------------------------------------

    record ReviewPolicy(
        int requiredApprovals,
        boolean requireDistinctReviewers,
        boolean rejectOnNegativeReview
    ) {
        ReviewPolicy {
            if (requiredApprovals < 1) {
                throw new IllegalArgumentException(
                    "At least one approval is required"
                );
            }
        }
    }


    static class ApprovalEvaluator {

        private final ReviewPolicy policy;

        ApprovalEvaluator(ReviewPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        boolean isApproved(List<ReviewDecision> reviews) {

            if (reviews == null || reviews.isEmpty()) {
                return false;
            }

            if (policy.requireDistinctReviewers()) {
                long distinctReviewers = reviews.stream()
                    .map(ReviewDecision::reviewer)
                    .distinct()
                    .count();

                if (distinctReviewers != reviews.size()) {
                    return false;
                }
            }

            if (policy.rejectOnNegativeReview()) {
                boolean rejected = reviews.stream()
                    .anyMatch(review ->
                        review.decision() == Decision.REJECT
                        || review.decision() == Decision.REQUEST_CHANGES
                    );

                if (rejected) {
                    return false;
                }
            }

            long approvals = reviews.stream()
                .filter(review ->
                    review.decision() == Decision.APPROVE
                )
                .count();

            return approvals >= policy.requiredApprovals();
        }
    }


    // -------------------------------------------------
    // 8. Authorization component
    // -------------------------------------------------

    enum Role {
        ADMINISTRATOR,
        AUTHOR,
        REVIEWER,
        VIEWER
    }


    enum Action {
        CREATE,
        READ,
        SUBMIT,
        REVIEW,
        APPROVE
    }


    static class AuthorizationPolicy {

        private final Map<Role, Set<Action>> permissions =
            new HashMap<>();

        AuthorizationPolicy() {
            permissions.put(
                Role.ADMINISTRATOR,
                EnumSet.allOf(Action.class)
            );

            permissions.put(
                Role.AUTHOR,
                EnumSet.of(
                    Action.CREATE,
                    Action.READ,
                    Action.SUBMIT
                )
            );

            permissions.put(
                Role.REVIEWER,
                EnumSet.of(
                    Action.READ,
                    Action.REVIEW,
                    Action.APPROVE
                )
            );

            permissions.put(
                Role.VIEWER,
                EnumSet.of(Action.READ)
            );
        }

        boolean permits(Role role, Action action) {
            return permissions.getOrDefault(
                role,
                Collections.emptySet()
            ).contains(action);
        }
    }


    // -------------------------------------------------
    // 9. Document aggregate
    // -------------------------------------------------

    static class DocumentWorkflow {

        private final Document document;

        private final AtomicReference<DocumentStatus> status =
            new AtomicReference<>(DocumentStatus.DRAFT);

        private final List<ReviewDecision> reviews =
            new ArrayList<>();

        DocumentWorkflow(Document document) {
            this.document = Objects.requireNonNull(document);
        }

        synchronized void submit() {
            transition(
                DocumentStatus.DRAFT,
                DocumentStatus.SUBMITTED
            );
        }

        synchronized void beginReview() {
            transition(
                DocumentStatus.SUBMITTED,
                DocumentStatus.UNDER_REVIEW
            );
        }

        synchronized void addReview(ReviewDecision review) {
            if (status.get() != DocumentStatus.UNDER_REVIEW) {
                throw new CompositionException(
                    "Reviews require an active review state"
                );
            }

            boolean alreadyReviewed = reviews.stream()
                .anyMatch(existing ->
                    existing.reviewer().equals(review.reviewer())
                );

            if (alreadyReviewed) {
                throw new CompositionException(
                    "Duplicate reviewer"
                );
            }

            reviews.add(Objects.requireNonNull(review));
        }

        synchronized void finalizeReview(
            ApprovalEvaluator evaluator
        ) {
            if (status.get() != DocumentStatus.UNDER_REVIEW) {
                throw new CompositionException(
                    "Document is not under review"
                );
            }

            boolean approved = evaluator.isApproved(
                List.copyOf(reviews)
            );

            status.set(
                approved
                    ? DocumentStatus.APPROVED
                    : DocumentStatus.REJECTED
            );
        }

        private void transition(
            DocumentStatus expected,
            DocumentStatus next
        ) {
            if (!status.compareAndSet(expected, next)) {
                throw new CompositionException(
                    "Invalid transition: "
                    + status.get()
                    + " -> "
                    + next
                );
            }
        }

        Document document() {
            return document;
        }

        DocumentStatus status() {
            return status.get();
        }

        synchronized List<ReviewDecision> reviews() {
            return List.copyOf(reviews);
        }
    }


    // -------------------------------------------------
    // 10. Enterprise application composition
    // -------------------------------------------------

    static class DocumentApplication {

        private final DocumentValidator validator;
        private final DocumentStorage storage;
        private final NotificationSender notification;
        private final ApprovalEvaluator approvalEvaluator;
        private final AuthorizationPolicy authorization;

        private final Map<String, DocumentWorkflow> workflows =
            new ConcurrentHashMap<>();

        DocumentApplication(
            DocumentValidator validator,
            DocumentStorage storage,
            NotificationSender notification,
            ApprovalEvaluator approvalEvaluator,
            AuthorizationPolicy authorization
        ) {
            this.validator = Objects.requireNonNull(validator);
            this.storage = Objects.requireNonNull(storage);
            this.notification = Objects.requireNonNull(notification);
            this.approvalEvaluator =
                Objects.requireNonNull(approvalEvaluator);
            this.authorization = Objects.requireNonNull(authorization);
        }

        DocumentWorkflow create(
            Role role,
            Document document
        ) {
            requirePermission(role, Action.CREATE);

            validator.validate(document);

            DocumentWorkflow workflow =
                new DocumentWorkflow(document);

            DocumentWorkflow previous = workflows.putIfAbsent(
                document.documentId(),
                workflow
            );

            if (previous != null) {
                throw new CompositionException(
                    "Document already exists"
                );
            }

            storage.save(document);

            return workflow;
        }

        void submit(
            Role role,
            String documentId
        ) {
            requirePermission(role, Action.SUBMIT);

            DocumentWorkflow workflow = getWorkflow(documentId);

            workflow.submit();

            notification.send(
                workflow.document().owner(),
                "Document submitted for review"
            );
        }

        void review(
            Role role,
            String documentId,
            ReviewDecision review
        ) {
            requirePermission(role, Action.REVIEW);

            if (!review.reviewer().equals(role.name())) {
                throw new CompositionException(
                    "Reviewer identity does not match authenticated role"
                );
            }

            getWorkflow(documentId).addReview(review);
        }

        void finalizeReview(
            Role role,
            String documentId
        ) {
            requirePermission(role, Action.APPROVE);

            DocumentWorkflow workflow = getWorkflow(documentId);

            workflow.finalizeReview(approvalEvaluator);

            notification.send(
                workflow.document().owner(),
                "Document status: " + workflow.status()
            );
        }

        private void requirePermission(Role role, Action action) {
            if (!authorization.permits(role, action)) {
                throw new CompositionException(
                    "Access denied: " + role + " cannot perform " + action
                );
            }
        }

        private DocumentWorkflow getWorkflow(String id) {
            DocumentWorkflow workflow = workflows.get(id);

            if (workflow == null) {
                throw new CompositionException(
                    "Workflow not found"
                );
            }

            return workflow;
        }

        List<DocumentWorkflow> approvedDocuments() {
            return workflows.values().stream()
                .filter(workflow ->
                    workflow.status() == DocumentStatus.APPROVED
                )
                .collect(Collectors.toList());
        }
    }


    // -------------------------------------------------
    // 11. Application factory
    // -------------------------------------------------

    static DocumentApplication createApplication() {

        DocumentValidator validator = new CompositeValidator(
            List.of(
                new ContentValidator(10000),
                new ClassificationValidator(
                    Set.of("PUBLIC", "INTERNAL", "CONFIDENTIAL")
                )
            )
        );

        DocumentStorage storage =
            new InMemoryDocumentStorage();

        NotificationSender notification =
            new ConsoleNotificationSender();

        ReviewPolicy policy = new ReviewPolicy(
            2,
            true,
            true
        );

        return new DocumentApplication(
            validator,
            storage,
            notification,
            new ApprovalEvaluator(policy),
            new AuthorizationPolicy()
        );
    }


    // -------------------------------------------------
    // 12. Executable tests
    // -------------------------------------------------

    public static void main(String[] args) {

        DocumentApplication application = createApplication();

        Document document = new Document(
            UUID.randomUUID().toString(),
            "atul@example.com",
            "Enterprise composition architecture specification",
            "INTERNAL"
        );

        try {
            DocumentWorkflow workflow = application.create(
                Role.AUTHOR,
                document
            );

            application.submit(
                Role.AUTHOR,
                document.documentId()
            );

            workflow.beginReview();

            application.review(
                Role.REVIEWER,
                document.documentId(),
                new ReviewDecision(
                    Role.REVIEWER.name(),
                    Decision.APPROVE,
                    "Technical validation completed"
                )
            );

            // A distinct second reviewer is required.
            ReviewDecision secondReview = new ReviewDecision(
                "SECOND_REVIEWER",
                Decision.APPROVE,
                "Governance requirements satisfied"
            );

            workflow.addReview(secondReview);

            application.finalizeReview(
                Role.REVIEWER,
                document.documentId()
            );

            if (workflow.status() != DocumentStatus.APPROVED) {
                throw new AssertionError(
                    "Document approval failed"
                );
            }

            System.out.println(
                "Document status: " + workflow.status()
            );

            System.out.println(
                "Approved document count: "
                + application.approvedDocuments().size()
            );

            // Verify unauthorized operations.
            try {
                application.finalizeReview(
                    Role.VIEWER,
                    document.documentId()
                );

                throw new AssertionError(
                    "Viewer authorization test failed"
                );

            } catch (CompositionException expected) {
                System.out.println(
                    "Unauthorized operation rejected"
                );
            }

            // Verify invalid document classification.
            try {
                Document invalid = new Document(
                    "DOC-INVALID",
                    "owner@example.com",
                    "Test",
                    "RESTRICTED"
                );

                application.create(Role.AUTHOR, invalid);

                throw new AssertionError(
                    "Classification validation failed"
                );

            } catch (CompositionException expected) {
                System.out.println(
                    "Invalid classification rejected"
                );
            }

            // Verify duplicate reviewer protection.
            try {
                workflow.addReview(
                    new ReviewDecision(
                        Role.REVIEWER.name(),
                        Decision.APPROVE,
                        "Duplicate review"
                    )
                );

                throw new AssertionError(
                    "Duplicate reviewer test failed"
                );

            } catch (CompositionException expected) {
                System.out.println(
                    "Duplicate reviewer rejected"
                );
            }

            System.out.println(
                "All Java 17 composition tests passed."
            );

        } catch (CompletionException exception) {
            throw new CompositionException(
                "Asynchronous operation failed",
                exception
            );
        }
    }
}
