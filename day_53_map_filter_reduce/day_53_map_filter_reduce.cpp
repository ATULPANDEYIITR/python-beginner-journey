#include <algorithm>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

struct PullLikeRecord {
    int id;
    std::string title;
    std::string author;
    int changedLines;
    bool testsPassed;
    bool approved;
    bool conflicts;
};

struct Evaluation {
    int id;
    std::string title;
    int changedLines;
    bool mergeEligible;
    std::string reason;
};

class RepositoryGovernance {
private:
    std::vector<PullLikeRecord> records;

    static bool isValid(const PullLikeRecord& record) {
        return record.id > 0 &&
               !record.title.empty() &&
               !record.author.empty() &&
               record.changedLines >= 0;
    }

    static bool passesGovernance(const PullLikeRecord& record) {
        /*
         * The policy intentionally requires all merge prerequisites:
         * successful validation, successful tests, approval, and no conflict.
         */
        return isValid(record) &&
               record.testsPassed &&
               record.approved &&
               !record.conflicts;
    }

public:
    explicit RepositoryGovernance(std::vector<PullLikeRecord> input)
        : records(std::move(input)) {
        for (const auto& record : records) {
            if (!isValid(record)) {
                throw std::invalid_argument("Invalid repository change record");
            }
        }
    }

    std::vector<PullLikeRecord> approvedChanges() const {
        // std::copy_if is the C++ equivalent of a filter operation.
        std::vector<PullLikeRecord> result;
        std::copy_if(
            records.begin(),
            records.end(),
            std::back_inserter(result),
            [](const PullLikeRecord& record) {
                return record.approved;
            }
        );
        return result;
    }

    std::vector<Evaluation> evaluate() const {
        /*
         * std::transform performs the map role. Each repository record is
         * converted into a separate governance evaluation.
         */
        std::vector<Evaluation> result;
        result.reserve(records.size());

        std::transform(
            records.begin(),
            records.end(),
            std::back_inserter(result),
            [](const PullLikeRecord& record) {
                Evaluation evaluation{
                    record.id,
                    record.title,
                    record.changedLines,
                    false,
                    {}
                };

                if (record.conflicts) {
                    evaluation.reason = "merge conflict exists";
                } else if (!record.testsPassed) {
                    evaluation.reason = "required tests failed";
                } else if (!record.approved) {
                    evaluation.reason = "required approval missing";
                } else {
                    evaluation.mergeEligible = true;
                    evaluation.reason = "all merge conditions satisfied";
                }

                return evaluation;
            }
        );

        return result;
    }

    int totalChangedLinesOfEligibleChanges() const {
        const auto evaluations = evaluate();

        /*
         * First remove ineligible evaluations, then accumulate their changed
         * line counts. This separates selection from aggregation.
         */
        std::vector<int> eligibleLineCounts;

        std::transform(
            evaluations.begin(),
            evaluations.end(),
            std::back_inserter(eligibleLineCounts),
            [](const Evaluation& evaluation) {
                return evaluation.mergeEligible
                    ? evaluation.changedLines
                    : 0;
            }
        );

        // std::accumulate performs the reduce role with an explicit identity.
        return std::accumulate(
            eligibleLineCounts.begin(),
            eligibleLineCounts.end(),
            0
        );
    }

    std::unordered_map<std::string, int> changedLinesByAuthor() const {
        /*
         * This aggregation intentionally operates on the source records,
         * showing that reduce-style accumulation does not have to produce
         * a scalar. The result can be a map.
         */
        std::unordered_map<std::string, int> totals;

        for (const auto& record : records) {
            totals[record.author] += record.changedLines;
        }

        return totals;
    }
};

int main() {
    try {
        const std::vector<PullLikeRecord> records{
            {501, "Add payment validation", "Asha", 48, true, true, false},
            {502, "Update deployment manifest", "Rahul", 31, true, false, false},
            {503, "Improve search index", "Meera", 76, false, true, false},
            {504, "Fix authorization policy", "Kabir", 22, true, true, true},
            {505, "Optimize report query", "Asha", 64, true, true, false}
        };

        RepositoryGovernance governance(records);

        const auto approved = governance.approvedChanges();
        std::cout << "Approved changes: " << approved.size() << "\n\n";

        const auto evaluations = governance.evaluate();

        std::cout << std::left
                  << std::setw(8) << "ID"
                  << std::setw(30) << "Change"
                  << std::setw(12) << "Lines"
                  << std::setw(14) << "Eligible"
                  << "Reason\n";

        std::cout << std::string(90, '-') << '\n';

        for (const auto& evaluation : evaluations) {
            std::cout << std::left
                      << std::setw(8) << evaluation.id
                      << std::setw(30) << evaluation.title
                      << std::setw(12) << evaluation.changedLines
                      << std::setw(14)
                      << (evaluation.mergeEligible ? "yes" : "no")
                      << evaluation.reason << '\n';
        }

        std::cout << "\nChanged lines in merge-eligible changes: "
                  << governance.totalChangedLinesOfEligibleChanges()
                  << "\n";

        const auto authorTotals = governance.changedLinesByAuthor();

        std::cout << "\nChanged lines by author:\n";
        for (const auto& [author, lines] : authorTotals) {
            std::cout << "  " << author << ": " << lines << '\n';
        }

        // Explicit initial values make empty reductions well-defined.
        const std::vector<int> empty;
        const int emptyTotal = std::accumulate(
            empty.begin(),
            empty.end(),
            0
        );

        std::cout << "\nEmpty reduction: " << emptyTotal << '\n';

        /*
         * Complexity:
         * - filtering: O(n)
         * - transformation: O(n)
         * - aggregation: O(n) expected for unordered_map
         * - storage: O(n)
         *
         * The implementation uses separate passes because each pass has a
         * single policy role and can be inspected independently.
         */
    } catch (const std::exception& error) {
        std::cerr << "Governance evaluation failed: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
