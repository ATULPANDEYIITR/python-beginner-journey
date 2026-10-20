#include <algorithm>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using Clock = std::chrono::steady_clock;

struct OrderEvent {
    std::string requestId;
    std::string orderId;
    std::string customerId;
    double amount{};
    std::string currency{"INR"};
    std::string idempotencyKey;
};

struct InvocationResult {
    std::string requestId;
    bool success{false};
    std::string error;
    double payable{};
    double durationMs{};
};

class LambdaFunction {
public:
    using Handler = std::function<OrderEvent(const OrderEvent&)>;

    LambdaFunction(std::string name, Handler handler, int timeoutMs, int memoryMb)
        : name_(std::move(name)),
          handler_(std::move(handler)),
          timeoutMs_(timeoutMs),
          memoryMb_(memoryMb) {
        if (name_.empty()) {
            throw std::invalid_argument("Function name cannot be empty");
        }
        if (!handler_) {
            throw std::invalid_argument("Handler cannot be empty");
        }
        if (timeoutMs_ <= 0) {
            throw std::invalid_argument("Timeout must be positive");
        }
        if (memoryMb_ < 128) {
            throw std::invalid_argument("Memory must be at least 128 MB");
        }
    }

    InvocationResult invoke(const OrderEvent& event) {
        ++invocations_;

        auto start = Clock::now();
        InvocationResult result;
        result.requestId = event.requestId;

        try {
            validate(event);

            OrderEvent processed = handler_(event);

            auto end = Clock::now();
            result.durationMs =
                std::chrono::duration<double, std::milli>(end - start).count();

            if (result.durationMs > timeoutMs_) {
                throw std::runtime_error("Lambda timeout exceeded");
            }

            result.success = true;
            result.payable = processed.amount;
        } catch (const std::exception& ex) {
            auto end = Clock::now();
            result.durationMs =
                std::chrono::duration<double, std::milli>(end - start).count();
            result.success = false;
            result.error = ex.what();
        }

        return result;
    }

    std::size_t invocations() const {
        return invocations_;
    }

private:
    static void validate(const OrderEvent& event) {
        if (event.orderId.empty()) {
            throw std::invalid_argument("orderId is required");
        }

        if (event.customerId.empty()) {
            throw std::invalid_argument("customerId is required");
        }

        if (!std::isfinite(event.amount) || event.amount <= 0.0) {
            throw std::invalid_argument(
                "amount must be finite and greater than zero");
        }

        if (event.idempotencyKey.empty()) {
            throw std::invalid_argument("idempotency key is required");
        }
    }

    std::string name_;
    Handler handler_;
    int timeoutMs_;
    int memoryMb_;
    std::size_t invocations_{0};
};

class PricingEngine {
public:
    OrderEvent operator()(const OrderEvent& input) const {
        OrderEvent output = input;

        double rate = 0.0;

        if (input.amount >= 10000.0) {
            rate = 0.15;
        } else if (input.amount >= 5000.0) {
            rate = 0.10;
        } else if (input.amount >= 1000.0) {
            rate = 0.05;
        }

        output.amount =
            std::round(input.amount * (1.0 - rate) * 100.0) / 100.0;

        return output;
    }
};

class IdempotencyStore {
public:
    bool alreadyProcessed(const std::string& key) const {
        return keys_.contains(key);
    }

    bool markProcessed(const std::string& key) {
        return keys_.insert(key).second;
    }

private:
    std::unordered_set<std::string> keys_;
};

class LambdaRouter {
public:
    void registerFunction(
        const std::string& eventType,
        LambdaFunction& function) {
        if (routes_.contains(eventType)) {
            throw std::logic_error("Duplicate event route: " + eventType);
        }

        routes_.emplace(eventType, &function);
    }

    InvocationResult dispatch(
        const std::string& eventType,
        const OrderEvent& event) {
        auto it = routes_.find(eventType);

        if (it == routes_.end()) {
            return {
                event.requestId,
                false,
                "No Lambda registered for event type",
                0.0,
                0.0,
            };
        }

        return it->second->invoke(event);
    }

private:
    std::unordered_map<std::string, LambdaFunction*> routes_;
};

class PaymentProcessor {
public:
    explicit PaymentProcessor(IdempotencyStore& store)
        : store_(store) {}

    OrderEvent operator()(const OrderEvent& input) {
        if (!store_.markProcessed(input.idempotencyKey)) {
            throw std::runtime_error("Duplicate event rejected");
        }

        OrderEvent output = input;
        output.amount = input.amount;
        return output;
    }

private:
    IdempotencyStore& store_;
};

static std::string makeRequestId(int value) {
    return "REQ-" + std::to_string(value);
}

int main() {
    try {
        PricingEngine pricingEngine;
        IdempotencyStore idempotencyStore;
        PaymentProcessor paymentProcessor(idempotencyStore);

        LambdaFunction pricing(
            "pricing-function",
            [&](const OrderEvent& event) {
                return pricingEngine(event);
            },
            1000,
            256);

        LambdaFunction payments(
            "payment-function",
            [&](const OrderEvent& event) {
                return paymentProcessor(event);
            },
            1000,
            256);

        LambdaRouter router;
        router.registerFunction("order.created", pricing);
        router.registerFunction("payment.requested", payments);

        OrderEvent order{
            makeRequestId(1001),
            "ORD-1001",
            "CUS-42",
            7500.00,
            "INR",
            "ORDER-1001-V1",
        };

        auto priced = router.dispatch("order.created", order);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Pricing Lambda\n";
        std::cout << "Success: " << std::boolalpha << priced.success << '\n';
        std::cout << "Payable: " << priced.payable << '\n';
        std::cout << "Duration: " << priced.durationMs << " ms\n\n";

        OrderEvent payment{
            makeRequestId(1002),
            "ORD-1001",
            "CUS-42",
            priced.payable,
            "INR",
            "PAYMENT-ORD-1001",
        };

        auto firstPayment =
            router.dispatch("payment.requested", payment);

        auto duplicatePayment =
            router.dispatch("payment.requested", payment);

        std::cout << "Payment Lambda\n";
        std::cout << "First attempt: "
                  << (firstPayment.success ? "accepted" : "rejected")
                  << '\n';
        std::cout << "Duplicate attempt: "
                  << (duplicatePayment.success ? "accepted" : "rejected")
                  << '\n';

        if (!duplicatePayment.success) {
            std::cout << "Reason: " << duplicatePayment.error << '\n';
        }

        OrderEvent invalid{
            makeRequestId(1003),
            "ORD-BAD",
            "CUS-42",
            -50.0,
            "INR",
            "INVALID-1",
        };

        auto invalidResult =
            router.dispatch("order.created", invalid);

        std::cout << "\nValidation failure\n";
        std::cout << "Success: " << invalidResult.success << '\n';
        std::cout << "Reason: " << invalidResult.error << '\n';

        std::cout << "\nOperational metrics\n";
        std::cout << "Pricing invocations: "
                  << pricing.invocations() << '\n';
        std::cout << "Payment invocations: "
                  << payments.invocations() << '\n';

        /*
         * Complexity:
         * - Event routing is O(1) average using unordered_map.
         * - Idempotency lookup is O(1) average using unordered_set.
         * - Individual handlers are O(1) for this workload.
         *
         * A production implementation would externalize idempotency state
         * because process-local state can disappear when a runtime is
         * recycled or scaled horizontally.
         */
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
