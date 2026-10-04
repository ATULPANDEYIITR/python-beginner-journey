#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Copying Data: repository configuration governance case study
 *
 * Scenario:
 * A deployment control service maintains configuration for several production
 * services. Operators can inspect configuration, create isolated snapshots,
 * modify working copies, publish new versions, and roll back.
 *
 * The case study demonstrates:
 * - value semantics and object copying
 * - shallow versus deep ownership
 * - explicit copy constructors
 * - copy-and-modify workflows
 * - validation and failure handling
 * - snapshot isolation
 * - performance trade-offs
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic copying_data.cpp -o copying_data
 */

namespace copying_data {

void printHeading(const std::string& title) {
    std::cout << "\n" << std::string(78, '=') << "\n"
              << title << "\n"
              << std::string(78, '=') << "\n";
}

struct RetryPolicy {
    int max_attempts{};
    int backoff_ms{};

    void validate() const {
        if (max_attempts < 0 || max_attempts > 20) {
            throw std::invalid_argument(
                "max_attempts must be between 0 and 20"
            );
        }

        if (backoff_ms < 0 || backoff_ms > 60'000) {
            throw std::invalid_argument(
                "backoff_ms must be between 0 and 60000"
            );
        }
    }
};

struct ServiceConfiguration {
    std::string service_name;
    std::vector<std::string> regions;
    std::map<std::string, int> limits;
    RetryPolicy retry;
    std::map<std::string, bool> feature_flags;

    void validate() const {
        if (service_name.empty()) {
            throw std::invalid_argument("service_name cannot be empty");
        }

        if (regions.empty()) {
            throw std::invalid_argument("at least one region is required");
        }

        for (const auto& [name, limit] : limits) {
            if (name.empty()) {
                throw std::invalid_argument("limit name cannot be empty");
            }

            if (limit < 0) {
                throw std::invalid_argument(
                    "configuration limits cannot be negative"
                );
            }
        }

        retry.validate();
    }
};

void printConfiguration(const ServiceConfiguration& configuration) {
    std::cout << "Service: " << configuration.service_name << "\n";

    std::cout << "Regions: ";
    for (std::size_t i = 0; i < configuration.regions.size(); ++i) {
        if (i != 0) {
            std::cout << ", ";
        }
        std::cout << configuration.regions[i];
    }
    std::cout << "\n";

    std::cout << "Limits:\n";
    for (const auto& [name, value] : configuration.limits) {
        std::cout << "  " << name << " = " << value << "\n";
    }

    std::cout << "Retry: attempts=" << configuration.retry.max_attempts
              << ", backoff_ms=" << configuration.retry.backoff_ms << "\n";

    std::cout << "Features:\n";
    for (const auto& [name, enabled] : configuration.feature_flags) {
        std::cout << "  " << name << " = "
                  << (enabled ? "enabled" : "disabled") << "\n";
    }
}

/*
 * C++ containers have value semantics. Copying a ServiceConfiguration copies
 * the vector, map, and string contents rather than creating aliases to the
 * same elements. This is a fundamentally different default ownership model
 * from JavaScript object references.
 */
void demonstrateValueCopying() {
    printHeading("C++ value semantics");

    ServiceConfiguration original{
        "checkout",
        {"ap-south-1", "eu-west-1"},
        {{"requests_per_minute", 1000}},
        {4, 250},
        {{"fraud_detection", true}}
    };

    ServiceConfiguration copy = original;

    copy.regions.push_back("us-east-1");
    copy.limits["requests_per_minute"] = 2000;
    copy.feature_flags["async_settlement"] = true;

    std::cout << "Original configuration:\n";
    printConfiguration(original);

    std::cout << "\nCopied configuration after mutation:\n";
    printConfiguration(copy);

    assert(original.regions.size() == 2);
    assert(original.limits.at("requests_per_minute") == 1000);
    assert(original.feature_flags.size() == 1);

    std::cout << "\nNested containers remain independent after the copy.\n";
}

/*
 * A pointer-backed model makes ownership explicit. The default copy operation
 * for a raw pointer would copy only the address. The DeepConfiguration class
 * therefore owns its dynamically allocated RetryPolicy and implements the
 * Rule of Five correctly enough for this focused example.
 *
 * In production C++, std::unique_ptr is preferable to a raw owning pointer.
 */
class DeepConfiguration {
private:
    std::string service_name_;
    std::vector<std::string> regions_;
    std::unique_ptr<RetryPolicy> retry_;

public:
    DeepConfiguration(
        std::string service_name,
        std::vector<std::string> regions,
        RetryPolicy retry
    )
        : service_name_(std::move(service_name)),
          regions_(std::move(regions)),
          retry_(std::make_unique<RetryPolicy>(retry)) {
        validate();
    }

    DeepConfiguration(const DeepConfiguration& other)
        : service_name_(other.service_name_),
          regions_(other.regions_),
          retry_(std::make_unique<RetryPolicy>(*other.retry_)) {}

    DeepConfiguration& operator=(const DeepConfiguration& other) {
        if (this != &other) {
            service_name_ = other.service_name_;
            regions_ = other.regions_;
            retry_ = std::make_unique<RetryPolicy>(*other.retry_);
        }
        return *this;
    }

    DeepConfiguration(DeepConfiguration&&) noexcept = default;
    DeepConfiguration& operator=(DeepConfiguration&&) noexcept = default;
    ~DeepConfiguration() = default;

    void validate() const {
        if (service_name_.empty()) {
            throw std::invalid_argument("service name cannot be empty");
        }

        if (regions_.empty()) {
            throw std::invalid_argument("at least one region is required");
        }

        if (!retry_) {
            throw std::logic_error("retry policy cannot be null");
        }

        retry_->validate();
    }

    void setBackoff(int milliseconds) {
        if (milliseconds < 0) {
            throw std::invalid_argument("backoff cannot be negative");
        }

        retry_->backoff_ms = milliseconds;
    }

    int backoff() const {
        return retry_->backoff_ms;
    }

    const std::vector<std::string>& regions() const {
        return regions_;
    }

    void addRegion(const std::string& region) {
        if (region.empty()) {
            throw std::invalid_argument("region cannot be empty");
        }

        regions_.push_back(region);
    }
};

void demonstrateExplicitDeepOwnership() {
    printHeading("Explicit deep ownership");

    DeepConfiguration original(
        "billing",
        {"ap-south-1", "eu-central-1"},
        {5, 500}
    );

    DeepConfiguration clone = original;

    clone.setBackoff(1500);
    clone.addRegion("us-east-1");

    std::cout << "Original backoff: " << original.backoff() << "\n";
    std::cout << "Clone backoff: " << clone.backoff() << "\n";
    std::cout << "Original region count: " << original.regions().size() << "\n";
    std::cout << "Clone region count: " << clone.regions().size() << "\n";

    assert(original.backoff() == 500);
    assert(clone.backoff() == 1500);
}

class ConfigurationStore {
private:
    ServiceConfiguration current_;
    std::vector<ServiceConfiguration> snapshots_;

public:
    explicit ConfigurationStore(ServiceConfiguration initial)
        : current_(std::move(initial)) {
        current_.validate();
    }

    const ServiceConfiguration& view() const noexcept {
        return current_;
    }

    ServiceConfiguration workingCopy() const {
        /*
         * The caller receives a value copy. It can make several changes without
         * mutating the published configuration until commit() is called.
         */
        return current_;
    }

    void commit(ServiceConfiguration candidate) {
        candidate.validate();

        /*
         * Store a full historical snapshot. This gives rollback a stable value
         * independent of later modifications to current_.
         */
        snapshots_.push_back(current_);
        current_ = std::move(candidate);
    }

    void rollback() {
        if (snapshots_.empty()) {
            throw std::runtime_error("No previous configuration exists.");
        }

        current_ = snapshots_.back();
        snapshots_.pop_back();
    }

    std::size_t snapshotCount() const noexcept {
        return snapshots_.size();
    }
};

void demonstrateTransactionalCopyWorkflow() {
    printHeading("Transactional copy-and-commit workflow");

    ConfigurationStore store({
        "inventory",
        {"ap-south-1"},
        {{"requests_per_minute", 800}},
        {3, 300},
        {{"cache", true}}
    });

    auto candidate = store.workingCopy();

    candidate.regions.push_back("eu-west-1");
    candidate.limits["requests_per_minute"] = 1200;
    candidate.feature_flags["inventory_v2"] = true;

    std::cout << "Published configuration before commit:\n";
    printConfiguration(store.view());

    store.commit(std::move(candidate));

    std::cout << "\nPublished configuration after commit:\n";
    printConfiguration(store.view());

    std::cout << "\nHistorical snapshots: "
              << store.snapshotCount() << "\n";

    store.rollback();

    std::cout << "\nConfiguration after rollback:\n";
    printConfiguration(store.view());
}

class CopyOnWriteConfiguration {
private:
    std::shared_ptr<ServiceConfiguration> state_;

public:
    explicit CopyOnWriteConfiguration(ServiceConfiguration configuration)
        : state_(
              std::make_shared<ServiceConfiguration>(
                  std::move(configuration)
              )
          ) {}

    /*
     * Copying the wrapper is cheap because shared_ptr shares ownership.
     * Mutation calls detach first when multiple wrappers reference the same
     * state. This avoids an immediate deep copy when no mutation occurs.
     */
    CopyOnWriteConfiguration cloneView() const {
        return *this;
    }

    void setLimit(const std::string& name, int value) {
        if (value < 0) {
            throw std::invalid_argument("limit cannot be negative");
        }

        if (!state_.unique()) {
            state_ = std::make_shared<ServiceConfiguration>(*state_);
        }

        state_->limits[name] = value;
    }

    int limit(const std::string& name) const {
        auto iterator = state_->limits.find(name);

        if (iterator == state_->limits.end()) {
            throw std::out_of_range("unknown limit: " + name);
        }

        return iterator->second;
    }

    std::size_t owners() const noexcept {
        return state_.use_count();
    }
};

void demonstrateCopyOnWrite() {
    printHeading("Copy-on-write ownership");

    CopyOnWriteConfiguration original({
        "recommendation",
        {"ap-south-1"},
        {{"requests_per_minute", 500}},
        {4, 250},
        {{"personalization", true}}
    });

    auto view = original.cloneView();

    std::cout << "Shared owners before mutation: "
              << original.owners() << "\n";

    view.setLimit("requests_per_minute", 900);

    std::cout << "Original limit: "
              << original.limit("requests_per_minute") << "\n";

    std::cout << "Modified view limit: "
              << view.limit("requests_per_minute") << "\n";

    std::cout << "Original owners after detachment: "
              << original.owners() << "\n";
}

void demonstrateFailureHandling() {
    printHeading("Validation and failure handling");

    try {
        ServiceConfiguration invalid{
            "",
            {},
            {{"requests_per_minute", -10}},
            {50, -1},
            {}
        };

        invalid.validate();
    } catch (const std::exception& error) {
        std::cout << "Rejected invalid configuration: "
                  << error.what() << "\n";
    }

    ConfigurationStore store({
        "reporting",
        {"eu-west-1"},
        {{"requests_per_minute", 100}},
        {2, 100},
        {}
    });

    try {
        store.rollback();
    } catch (const std::exception& error) {
        std::cout << "Rollback rejected: " << error.what() << "\n";
    }
}

void demonstrateConstOwnership() {
    printHeading("Read-only access versus copied mutable access");

    ConfigurationStore store({
        "fraud",
        {"ap-south-1", "eu-west-1"},
        {{"requests_per_minute", 300}},
        {6, 200},
        {{"rules_engine", true}}
    });

    const ServiceConfiguration& published = store.view();

    std::cout << "Published service through const reference: "
              << published.service_name << "\n";

    auto editable = store.workingCopy();
    editable.feature_flags["rules_engine"] = false;

    std::cout << "Published feature remains: "
              << (store.view().feature_flags.at("rules_engine")
                      ? "enabled"
                      : "disabled")
              << "\n";

    std::cout << "Editable copy feature: "
              << (editable.feature_flags.at("rules_engine")
                      ? "enabled"
                      : "disabled")
              << "\n";
}

void demonstrateCopyCost() {
    printHeading("Copy cost and data size");

    constexpr std::size_t service_count = 5000;

    std::vector<ServiceConfiguration> configurations;
    configurations.reserve(service_count);

    for (std::size_t i = 0; i < service_count; ++i) {
        configurations.push_back({
            "service-" + std::to_string(i),
            {"ap-south-1", "eu-west-1"},
            {{"requests_per_minute", 1000}},
            {4, 250},
            {{"audit_logging", true}}
        });
    }

    const auto start = std::chrono::steady_clock::now();

    auto copied = configurations;

    const auto end = std::chrono::steady_clock::now();

    const auto elapsed =
        std::chrono::duration_cast<std::chrono::microseconds>(
            end - start
        ).count();

    std::cout << "Configurations copied: " << copied.size() << "\n";
    std::cout << "Measured copy time: " << elapsed << " microseconds\n";

    /*
     * This measurement is illustrative rather than a benchmark. Real
     * performance analysis must control compiler flags, allocator behavior,
     * CPU frequency, memory locality, workload size, and repeated runs.
     */
}

void demonstrateOwnershipRules() {
    printHeading("Ownership rules for copying data");

    std::cout
        << "Value-owned containers: copying duplicates their stored values.\n"
        << "Raw pointers: copying an address does not copy the pointed object.\n"
        << "unique_ptr: ownership is exclusive and ordinary copying is disabled.\n"
        << "shared_ptr: copies share ownership and may require copy-on-write for "
           "isolated mutation.\n"
        << "const references: provide read-only access without transferring "
           "ownership.\n"
        << "Snapshots: explicit value copies can preserve historical state.\n";
}

} // namespace copying_data

int main() {
    using namespace copying_data;

    std::cout << "COPYING DATA IN C++17\n";

    demonstrateValueCopying();
    demonstrateExplicitDeepOwnership();
    demonstrateTransactionalCopyWorkflow();
    demonstrateCopyOnWrite();
    demonstrateFailureHandling();
    demonstrateConstOwnership();
    demonstrateCopyCost();
    demonstrateOwnershipRules();

    std::cout << "\nAll copying-data case-study demonstrations completed.\n";

    return 0;
}
