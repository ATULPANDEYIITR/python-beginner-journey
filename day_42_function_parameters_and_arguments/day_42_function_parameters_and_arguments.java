import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Function parameter and argument modeling for an enterprise payment service.
 *
 * Compile: javac FunctionParameters.java
 * Run:     java FunctionParameters
 *
 * Requires Java 17 or later.
 */
public class FunctionParameters {

    enum PaymentStatus {
        CREATED, VALIDATED, AUTHORIZED, REJECTED
    }

    enum PaymentChannel {
        WEB, MOBILE, PARTNER_API
    }

    record PaymentRequest(
        String requestId,
        String accountId,
        BigDecimal amount,
        String currency,
        PaymentChannel channel
    ) {
        PaymentRequest {
            requireText(requestId, "requestId");
            requireText(accountId, "accountId");
            requireText(currency, "currency");

            Objects.requireNonNull(amount, "amount");
            Objects.requireNonNull(channel, "channel");

            if (amount.signum() <= 0) {
                throw new IllegalArgumentException("Payment amount must be positive");
            }
            if (currency.length() != 3 ||
                !currency.chars().allMatch(Character::isUpperCase)) {
                throw new IllegalArgumentException(
                    "Currency must be a three-letter uppercase code"
                );
            }
        }
    }

    record PaymentPolicy(
        BigDecimal singlePaymentLimit,
        BigDecimal dailyAccountLimit,
        boolean partnerApiEnabled,
        List<String> blockedAccounts
    ) {
        PaymentPolicy {
            Objects.requireNonNull(singlePaymentLimit, "singlePaymentLimit");
            Objects.requireNonNull(dailyAccountLimit, "dailyAccountLimit");
            blockedAccounts = List.copyOf(blockedAccounts);

            if (singlePaymentLimit.signum() <= 0 ||
                dailyAccountLimit.signum() <= 0) {
                throw new IllegalArgumentException("Limits must be positive");
            }
        }
    }

    record ValidationResult(boolean accepted, List<String> reasons) {
        ValidationResult {
            reasons = List.copyOf(reasons);
        }
    }

    record PaymentResult(
        String requestId,
        PaymentStatus status,
        BigDecimal amount,
        List<String> events
    ) {
        PaymentResult {
            events = List.copyOf(events);
        }
    }

    @FunctionalInterface
    interface PaymentAuthorizer {
        boolean authorize(PaymentRequest request, PaymentPolicy policy);
    }

    static void requireText(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must not be blank");
        }
    }

    // Separate arguments keep the rule explicit: amount is compared against
    // the single-payment limit, while policy controls the permitted maximum.
    static ValidationResult validateAmount(
        BigDecimal amount,
        BigDecimal singlePaymentLimit
    ) {
        Objects.requireNonNull(amount, "amount");
        Objects.requireNonNull(singlePaymentLimit, "singlePaymentLimit");

        List<String> reasons = new ArrayList<>();
        if (amount.signum() <= 0) {
            reasons.add("Amount must be positive");
        }
        if (amount.compareTo(singlePaymentLimit) > 0) {
            reasons.add("Single-payment limit exceeded");
        }
        return new ValidationResult(reasons.isEmpty(), reasons);
    }

    // A policy object groups related optional settings instead of requiring
    // callers to remember the position of several boolean and numeric values.
    static ValidationResult validateRequest(
        PaymentRequest request,
        PaymentPolicy policy
    ) {
        Objects.requireNonNull(request, "request");
        Objects.requireNonNull(policy, "policy");

        List<String> reasons = new ArrayList<>();
        ValidationResult amountResult = validateAmount(
            request.amount(), policy.singlePaymentLimit()
        );
        reasons.addAll(amountResult.reasons());

        if (policy.blockedAccounts().contains(request.accountId())) {
            reasons.add("Account is blocked");
        }
        if (request.channel() == PaymentChannel.PARTNER_API &&
            !policy.partnerApiEnabled()) {
            reasons.add("Partner API channel is disabled");
        }

        return new ValidationResult(reasons.isEmpty(), reasons);
    }

    // The strategy is a functional interface parameter. Different deployment
    // environments can inject different authorization mechanisms.
    static PaymentResult processPayment(
        PaymentRequest request,
        PaymentPolicy policy,
        PaymentAuthorizer authorizer
    ) {
        Objects.requireNonNull(request, "request");
        Objects.requireNonNull(policy, "policy");
        Objects.requireNonNull(authorizer, "authorizer");

        List<String> events = new ArrayList<>();
        events.add("CREATED");

        ValidationResult validation = validateRequest(request, policy);
        if (!validation.accepted()) {
            events.add("VALIDATION_REJECTED");
            events.addAll(validation.reasons());
            return new PaymentResult(
                request.requestId(),
                PaymentStatus.REJECTED,
                request.amount(),
                events
            );
        }

        events.add("VALIDATED");
        boolean authorized;
        try {
            authorized = authorizer.authorize(request, policy);
        } catch (RuntimeException exception) {
            events.add("AUTHORIZATION_ERROR");
            return new PaymentResult(
                request.requestId(),
                PaymentStatus.REJECTED,
                request.amount(),
                events
            );
        }

        if (!authorized) {
            events.add("AUTHORIZATION_DENIED");
            return new PaymentResult(
                request.requestId(),
                PaymentStatus.REJECTED,
                request.amount(),
                events
            );
        }

        events.add("AUTHORIZED");
        return new PaymentResult(
            request.requestId(),
            PaymentStatus.AUTHORIZED,
            request.amount(),
            events
        );
    }

    // Generic higher-order processing makes the mapping operation reusable
    // while keeping its parameter type checked by the compiler.
    static <T, R> List<R> mapValidated(
        List<T> values,
        Predicate<T> predicate,
        Function<T, R> mapper
    ) {
        Objects.requireNonNull(values, "values");
        Objects.requireNonNull(predicate, "predicate");
        Objects.requireNonNull(mapper, "mapper");

        return values.stream()
            .filter(predicate)
            .map(mapper)
            .collect(Collectors.toUnmodifiableList());
    }

    static BigDecimal calculateFee(
        BigDecimal amount,
        BigDecimal percentage,
        BigDecimal minimumFee
    ) {
        Objects.requireNonNull(amount, "amount");
        Objects.requireNonNull(percentage, "percentage");
        Objects.requireNonNull(minimumFee, "minimumFee");

        if (amount.signum() < 0 ||
            percentage.signum() < 0 ||
            minimumFee.signum() < 0) {
            throw new IllegalArgumentException("Fee inputs cannot be negative");
        }

        BigDecimal proportionalFee = amount
            .multiply(percentage)
            .divide(new BigDecimal("100"), 4, RoundingMode.HALF_UP);

        return proportionalFee.max(minimumFee)
            .setScale(2, RoundingMode.HALF_UP);
    }

    static void printResult(PaymentResult result) {
        System.out.println("Request: " + result.requestId());
        System.out.println("Status: " + result.status());
        System.out.println("Amount: " + result.amount());
        System.out.println("Events: " + result.events());
    }

    static void verify(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static void main(String[] args) {
        PaymentPolicy policy = new PaymentPolicy(
            new BigDecimal("50000.00"),
            new BigDecimal("150000.00"),
            false,
            List.of("ACC-BLOCKED")
        );

        PaymentAuthorizer accountAuthorizer = (request, selectedPolicy) ->
            request.amount().compareTo(selectedPolicy.dailyAccountLimit()) <= 0
                && !request.accountId().equals("ACC-SUSPENDED");

        PaymentRequest validRequest = new PaymentRequest(
            "PAY-2026-1001",
            "ACC-100",
            new BigDecimal("12500.00"),
            "INR",
            PaymentChannel.WEB
        );

        PaymentRequest overLimitRequest = new PaymentRequest(
            "PAY-2026-1002",
            "ACC-100",
            new BigDecimal("65000.00"),
            "INR",
            PaymentChannel.MOBILE
        );

        PaymentRequest blockedRequest = new PaymentRequest(
            "PAY-2026-1003",
            "ACC-BLOCKED",
            new BigDecimal("500.00"),
            "INR",
            PaymentChannel.WEB
        );

        PaymentRequest partnerRequest = new PaymentRequest(
            "PAY-2026-1004",
            "ACC-200",
            new BigDecimal("2500.00"),
            "INR",
            PaymentChannel.PARTNER_API
        );

        PaymentResult accepted = processPayment(
            validRequest, policy, accountAuthorizer
        );
        PaymentResult overLimit = processPayment(
            overLimitRequest, policy, accountAuthorizer
        );
        PaymentResult blocked = processPayment(
            blockedRequest, policy, accountAuthorizer
        );
        PaymentResult partner = processPayment(
            partnerRequest, policy, accountAuthorizer
        );

        printResult(accepted);
        printResult(overLimit);
        printResult(blocked);
        printResult(partner);

        BigDecimal fee = calculateFee(
            new BigDecimal("12500.00"),
            new BigDecimal("1.5"),
            new BigDecimal("10.00")
        );
        System.out.println("Transaction fee: " + fee);

        List<PaymentRequest> requests = List.of(
            validRequest, overLimitRequest, blockedRequest, partnerRequest
        );
        Map<String, BigDecimal> eligibleAmounts = mapValidated(
            requests,
            request -> validateRequest(request, policy).accepted(),
            PaymentRequest::amount
        ).stream().collect(Collectors.toMap(
            amount -> "eligible-" + amount.toPlainString(),
            Function.identity()
        ));
        System.out.println("Eligible amounts: " + eligibleAmounts);

        PaymentResult authorizationFailure = processPayment(
            validRequest,
            policy,
            (request, selectedPolicy) -> {
                throw new IllegalStateException("Authorization service unavailable");
            }
        );
        printResult(authorizationFailure);

        verify(accepted.status() == PaymentStatus.AUTHORIZED,
            "Valid payment should be authorized");
        verify(overLimit.status() == PaymentStatus.REJECTED,
            "Over-limit payment should be rejected");
        verify(blocked.status() == PaymentStatus.REJECTED,
            "Blocked account should be rejected");
        verify(partner.status() == PaymentStatus.REJECTED,
            "Disabled partner channel should be rejected");
        verify(authorizationFailure.status() == PaymentStatus.REJECTED,
            "Authorization failure must fail closed");

        try {
            new PaymentRequest(
                "PAY-INVALID",
                "ACC-300",
                new BigDecimal("-1.00"),
                "INR",
                PaymentChannel.WEB
            );
            throw new AssertionError("Negative payment should fail validation");
        } catch (IllegalArgumentException expected) {
            System.out.println("Invalid request rejected: " + expected.getMessage());
        }

        System.out.println("All enterprise payment parameter checks passed.");
    }
}
