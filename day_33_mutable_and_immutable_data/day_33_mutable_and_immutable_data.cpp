#include <algorithm>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * C++ case study: immutable state snapshots for a code-review service.
 *
 * The system models a review service in which a Pull Request has revisions,
 * reviewers, labels, changed files, and status checks. Mutable working state
 * is used while constructing an update, while published ReviewSnapshot
 * objects are immutable values that can safely be retained by audit logs,
 * readers, or concurrent processing components.
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic mutable_immutable_data.cpp -o review_state
 */

enum class CheckStatus {
    Pending,
    Passed,
    Failed
};

std::string to_string(CheckStatus status) {
    switch (status) {
        case CheckStatus::Pending:
            return "pending";
        case CheckStatus::Passed:
            return "passed";
        case CheckStatus::Failed:
            return "failed";
    }

    throw std::logic_error("unknown check status");
}

struct ReviewSnapshot {
    const std::string pull_request_id;
    const int revision;
    const std::vector<std::string> approvals;
    const std::map<std::string, CheckStatus> checks;
    const std::vector<std::string> labels;

    ReviewSnapshot(
        std::string id,
        int revision_number,
        std::vector<std::string> approval_list,
        std::map<std::string, CheckStatus> check_map,
        std::vector<std::string> label_list
    )
        : pull_request_id(std::move(id)),
          revision(revision_number),
          approvals(std::move(approval_list)),
          checks(std::move(check_map)),
          labels(std::move(label_list)) {
        if (pull_request_id.empty()) {
            throw std::invalid_argument("pull request ID cannot be empty");
        }

        if (revision < 1) {
            throw std::invalid_argument("revision must be positive");
        }
    }

    bool has_approval(const std::string& reviewer) const {
        return std::find(
            approvals.begin(),
            approvals.end(),
            reviewer
        ) != approvals.end();
    }

    bool all_checks_passed() const {
        if (checks.empty()) {
            return false;
        }

        return std::all_of(
            checks.begin(),
            checks.end(),
            [](const auto& entry) {
                return entry.second == CheckStatus::Passed;
            }
        );
    }

    ReviewSnapshot with_approval(const std::string& reviewer) const {
        if (reviewer.empty()) {
            throw std::invalid_argument("reviewer cannot be empty");
        }

        if (has_approval(reviewer)) {
            return *this;
        }

        auto next_approvals = approvals;
        next_approvals.push_back(reviewer);

        return ReviewSnapshot(
            pull_request_id,
            revision,
            std::move(next_approvals),
            checks,
            labels
        );
    }

    ReviewSnapshot with_check(
        const std::string& check_name,
        CheckStatus status
    ) const {
        if (check_name.empty()) {
            throw std::invalid_argument("check name cannot be empty");
        }

        auto next_checks = checks;
        next_checks[check_name] = status;

        return ReviewSnapshot(
            pull_request_id,
            revision,
            approvals,
            std::move(next_checks),
            labels
        );
    }

    ReviewSnapshot with_label(const std::string& label) const {
        if (label.empty()) {
            throw std::invalid_argument("label cannot be empty");
        }

        if (std::find(labels.begin(), labels.end(), label) != labels.end()) {
            return *this;
        }

        auto next_labels = labels;
        next_labels.push_back(label);

        return ReviewSnapshot(
            pull_request_id,
            revision,
            approvals,
            checks,
            std::move(next_labels)
        );
    }

    ReviewSnapshot next_revision() const {
        // A new revision invalidates prior review approvals in this model.
        // The old snapshot remains untouched and therefore remains a valid
        // historical record of the earlier revision.
        return ReviewSnapshot(
            pull_request_id,
            revision + 1,
            {},
            checks,
            labels
        );
    }
};

class MutableReviewBuilder {
private:
    std::string pull_request_id_;
    int revision_;
    std::vector<std::string> approvals_;
    std::map<std::string, CheckStatus> checks_;
    std::vector<std::string> labels_;

public:
    MutableReviewBuilder(std::string id, int revision)
        : pull_request_id_(std::move(id)),
          revision_(revision) {
        if (pull_request_id_.empty()) {
            throw std::invalid_argument("pull request ID cannot be empty");
        }

        if (revision_ < 1) {
            throw std::invalid_argument("revision must be positive");
        }
    }

    void add_approval(const std::string& reviewer) {
        if (reviewer.empty()) {
            throw std::invalid_argument("reviewer cannot be empty");
        }

        if (std::find(approvals_.begin(), approvals_.end(), reviewer)
            == approvals_.end()) {
            approvals_.push_back(reviewer);
        }
    }

    void set_check(const std::string& name, CheckStatus status) {
        if (name.empty()) {
            throw std::invalid_argument("check name cannot be empty");
        }

        checks_[name] = status;
    }

    void add_label(const std::string& label) {
        if (label.empty()) {
            throw std::invalid_argument("label cannot be empty");
        }

        if (std::find(labels_.begin(), labels_.end(), label)
            == labels_.end()) {
            labels_.push_back(label);
        }
    }

    ReviewSnapshot publish() const {
        // The mutable builder owns construction-time state. Publishing creates
        // an independent value whose public members cannot be reassigned.
        return ReviewSnapshot(
            pull_request_id_,
            revision_,
            approvals_,
            checks_,
            labels_
        );
    }
};

class ReviewHistory {
private:
    std::vector<ReviewSnapshot> snapshots_;

public:
    void append(ReviewSnapshot snapshot) {
        snapshots_.push_back(std::move(snapshot));
    }

    const std::vector<ReviewSnapshot>& snapshots() const {
        return snapshots_;
    }
};

struct MergePolicy {
    const std::size_t required_approvals;
    const bool require_all_checks_passed;

    MergePolicy(
        std::size_t approvals,
        bool require_checks
    )
        : required_approvals(approvals),
          require_all_checks_passed(require_checks) {}
};

struct MergeDecision {
    bool eligible;
    std::vector<std::string> reasons;
};

MergeDecision evaluate_merge(
    const ReviewSnapshot& snapshot,
    const MergePolicy& policy
) {
    MergeDecision decision{true, {}};

    if (snapshot.approvals.size() < policy.required_approvals) {
        decision.eligible = false;
        decision.reasons.push_back(
            "insufficient approvals: " +
            std::to_string(snapshot.approvals.size()) +
            " available, " +
            std::to_string(policy.required_approvals) +
            " required"
        );
    }

    if (policy.require_all_checks_passed && !snapshot.all_checks_passed()) {
        decision.eligible = false;
        decision.reasons.push_back(
            "not all required checks have passed"
        );
    }

    return decision;
}

void print_snapshot(const ReviewSnapshot& snapshot, const std::string& name) {
    std::cout << "\n[" << name << "]\n";
    std::cout << "PR: " << snapshot.pull_request_id << '\n';
    std::cout << "Revision: " << snapshot.revision << '\n';

    std::cout << "Approvals:";
    if (snapshot.approvals.empty()) {
        std::cout << " none";
    } else {
        for (const auto& reviewer : snapshot.approvals) {
            std::cout << ' ' << reviewer;
        }
    }
    std::cout << '\n';

    std::cout << "Checks:\n";
    for (const auto& [name_key, status] : snapshot.checks) {
        std::cout << "  " << name_key << ": " << to_string(status) << '\n';
    }

    std::cout << "Labels:";
    for (const auto& label : snapshot.labels) {
        std::cout << ' ' << label;
    }
    std::cout << '\n';
}

void print_decision(const MergeDecision& decision) {
    std::cout << "Merge eligible: "
              << (decision.eligible ? "yes" : "no")
              << '\n';

    for (const auto& reason : decision.reasons) {
        std::cout << "  - " << reason << '\n';
    }
}

int main() {
    try {
        std::cout << "Mutable and Immutable Data: Review State Case Study\n";

        /*
         * Construction is intentionally mutable. Building a complex state
         * through a builder avoids repeatedly allocating intermediate domain
         * objects while fields are being collected.
         */
        MutableReviewBuilder builder("PR-1042", 1);
        builder.add_label("backend");
        builder.add_label("review");
        builder.set_check("lint", CheckStatus::Passed);
        builder.set_check("tests", CheckStatus::Passed);

        const ReviewSnapshot initial = builder.publish();
        const ReviewSnapshot reviewed = initial.with_approval("reviewer-a");

        MergePolicy policy(2, true);

        print_snapshot(initial, "Initial immutable snapshot");
        print_snapshot(reviewed, "After first approval");

        std::cout << "\nFirst merge evaluation:\n";
        print_decision(evaluate_merge(reviewed, policy));

        const ReviewSnapshot fully_approved =
            reviewed.with_approval("reviewer-b");

        std::cout << "\nSecond merge evaluation:\n";
        print_snapshot(fully_approved, "Fully approved revision");
        print_decision(evaluate_merge(fully_approved, policy));

        /*
         * A new revision is represented as a new immutable value. The previous
         * approval state remains available for audit purposes but does not
         * contaminate the new revision.
         */
        const ReviewSnapshot revised = fully_approved.next_revision();

        std::cout << "\nAfter a new revision:\n";
        print_snapshot(revised, "New revision");
        print_snapshot(fully_approved, "Historical previous revision");

        std::cout << "\nNew revision merge evaluation:\n";
        print_decision(evaluate_merge(revised, policy));

        /*
         * This demonstrates another immutable transition: the failing test
         * result creates another snapshot rather than modifying the published
         * revision in place.
         */
        const ReviewSnapshot failed_check =
            revised.with_check("tests", CheckStatus::Failed);

        std::cout << "\nFailure state:\n";
        print_snapshot(failed_check, "Failed-check snapshot");
        print_decision(evaluate_merge(failed_check, policy));

        ReviewHistory history;
        history.append(initial);
        history.append(reviewed);
        history.append(fully_approved);
        history.append(revised);
        history.append(failed_check);

        std::cout << "\nImmutable audit history contains "
                  << history.snapshots().size()
                  << " snapshots.\n";

        /*
         * The following relationship is important:
         *
         * Mutable construction state is convenient for controlled local work.
         * Immutable published state is safer at boundaries because consumers
         * cannot accidentally alter a snapshot after it has been recorded.
         *
         * Copying a std::vector or std::map is not free. This design favors
         * correctness and snapshot clarity over zero-copy updates. Large
         * systems can use structural sharing or persistent containers when
         * profiling demonstrates that repeated copies are a bottleneck.
         */
        std::cout << "\nDesign trade-off:\n";
        std::cout
            << "Mutable builders reduce construction complexity; immutable "
            << "snapshots improve ownership clarity and historical consistency.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Application error: " << error.what() << '\n';
        return 1;
    }
}
