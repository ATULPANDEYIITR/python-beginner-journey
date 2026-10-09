#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

enum class Status {
    Pending,
    InProgress,
    Completed
};

std::string statusName(Status status) {
    switch (status) {
        case Status::Pending: return "pending";
        case Status::InProgress: return "in_progress";
        case Status::Completed: return "completed";
    }
    throw std::logic_error("Unknown status.");
}

struct WorkOrder {
    std::string id;
    std::string description;
    std::string department;
    int priority;
    double estimatedHours;
    std::set<std::string> labels;
    std::vector<std::string> dependencies;
    Status status = Status::Pending;
};

class OperationsPlanner {
private:
    // The unordered map provides average O(1) lookup by work-order identifier.
    std::unordered_map<std::string, WorkOrder> orders_;

    // The vector preserves insertion order for stable reporting.
    std::vector<std::string> insertionOrder_;

    // Reverse edges make it possible to identify downstream work.
    std::unordered_map<std::string, std::vector<std::string>> dependents_;

    std::unordered_set<std::string> completed_;
    std::map<std::string, std::set<std::string>> byDepartment_;

public:
    void add(WorkOrder order) {
        if (order.id.empty() || order.description.empty()) {
            throw std::invalid_argument("Identifier and description are required.");
        }

        if (order.priority < 1 || order.priority > 5) {
            throw std::invalid_argument("Priority must be between 1 and 5.");
        }

        if (!std::isfinite(order.estimatedHours) || order.estimatedHours < 0) {
            throw std::invalid_argument("Effort must be finite and non-negative.");
        }

        if (orders_.count(order.id) != 0) {
            throw std::invalid_argument("Duplicate work-order identifier.");
        }

        std::set<std::string> uniqueDependencies(
            order.dependencies.begin(),
            order.dependencies.end()
        );

        if (uniqueDependencies.size() != order.dependencies.size()) {
            throw std::invalid_argument("Duplicate dependencies are not allowed.");
        }

        for (const auto& dependency : order.dependencies) {
            if (dependency == order.id || orders_.count(dependency) == 0) {
                throw std::invalid_argument(
                    "Dependencies must reference existing, different orders."
                );
            }
        }

        if (order.status == Status::Completed) {
            completed_.insert(order.id);
        }

        insertionOrder_.push_back(order.id);
        byDepartment_[order.department].insert(order.id);

        for (const auto& dependency : order.dependencies) {
            dependents_[dependency].push_back(order.id);
        }

        orders_.emplace(order.id, std::move(order));
    }

    std::vector<std::string> readyOrders() const {
        std::vector<std::string> result;

        for (const auto& id : insertionOrder_) {
            const WorkOrder& order = orders_.at(id);

            if (order.status != Status::Pending) {
                continue;
            }

            bool ready = std::all_of(
                order.dependencies.begin(),
                order.dependencies.end(),
                [this](const std::string& dependency) {
                    return completed_.count(dependency) != 0;
                }
            );

            if (ready) {
                result.push_back(id);
            }
        }

        std::sort(result.begin(), result.end(), [this](
            const std::string& left,
            const std::string& right
        ) {
            const auto& a = orders_.at(left);
            const auto& b = orders_.at(right);

            if (a.priority != b.priority) {
                return a.priority < b.priority;
            }

            return a.id < b.id;
        });

        return result;
    }

    void transition(const std::string& id, Status next) {
        auto iterator = orders_.find(id);

        if (iterator == orders_.end()) {
            throw std::out_of_range("Unknown work-order identifier.");
        }

        WorkOrder& order = iterator->second;

        if (order.status == Status::Pending && next == Status::InProgress) {
            for (const auto& dependency : order.dependencies) {
                if (completed_.count(dependency) == 0) {
                    throw std::logic_error(
                        "A prerequisite has not been completed."
                    );
                }
            }
        } else if (
            order.status == Status::InProgress &&
            next == Status::Completed
        ) {
            // Completion is allowed only after work has actually started.
        } else {
            throw std::logic_error(
                "Unsupported transition from " + statusName(order.status) +
                " to " + statusName(next)
            );
        }

        order.status = next;

        if (next == Status::Completed) {
            completed_.insert(id);
        }
    }

    std::vector<std::string> topologicalOrder() const {
        std::unordered_map<std::string, std::size_t> indegree;

        for (const auto& entry : orders_) {
            indegree[entry.first] = entry.second.dependencies.size();
        }

        std::queue<std::string> ready;

        for (const auto& id : insertionOrder_) {
            if (indegree.at(id) == 0) {
                ready.push(id);
            }
        }

        std::vector<std::string> result;

        while (!ready.empty()) {
            std::string current = ready.front();
            ready.pop();
            result.push_back(current);

            auto iterator = dependents_.find(current);

            if (iterator == dependents_.end()) {
                continue;
            }

            for (const auto& dependent : iterator->second) {
                if (--indegree.at(dependent) == 0) {
                    ready.push(dependent);
                }
            }
        }

        if (result.size() != orders_.size()) {
            throw std::logic_error("Dependency cycle detected.");
        }

        return result;
    }

    std::set<std::string> searchLabels(
        const std::set<std::string>& requiredLabels
    ) const {
        std::set<std::string> result;

        for (const auto& entry : orders_) {
            const WorkOrder& order = entry.second;

            bool matches = std::all_of(
                requiredLabels.begin(),
                requiredLabels.end(),
                [&order](const std::string& label) {
                    return order.labels.count(label) != 0;
                }
            );

            if (matches) {
                result.insert(order.id);
            }
        }

        return result;
    }

    std::map<std::string, double> effortTotals() const {
        std::map<std::string, double> totals;

        for (const auto& entry : orders_) {
            const WorkOrder& order = entry.second;
            totals[order.department] += order.estimatedHours;
        }

        return totals;
    }

    void printReport() const {
        std::cout << "\nDependency-safe execution order:\n";

        for (const auto& id : topologicalOrder()) {
            const auto& order = orders_.at(id);
            std::cout << id << " | " << order.description
                      << " | " << statusName(order.status) << '\n';
        }

        std::cout << "\nCurrently ready work:\n";

        for (const auto& id : readyOrders()) {
            std::cout << id << '\n';
        }

        std::cout << "\nEffort by department:\n";

        for (const auto& entry : effortTotals()) {
            std::cout << entry.first << ": "
                      << entry.second << " hours\n";
        }
    }

    void printSharedLabels(const std::string& first,
                           const std::string& second) const {
        const auto a = byDepartment_.find(first);
        const auto b = byDepartment_.find(second);

        if (a == byDepartment_.end() || b == byDepartment_.end()) {
            std::cout << "No matching department membership.\n";
            return;
        }

        std::vector<std::string> shared;

        std::set_intersection(
            a->second.begin(), a->second.end(),
            b->second.begin(), b->second.end(),
            std::back_inserter(shared)
        );

        std::cout << "Shared work orders: ";

        for (const auto& id : shared) {
            std::cout << id << ' ';
        }

        std::cout << '\n';
    }
};

int main() {
    try {
        OperationsPlanner planner;

        planner.add({
            "OPS-201",
            "Validate supplier delivery records",
            "Data Operations",
            1,
            2.5,
            {"validation", "quality"},
            {},
            Status::Pending
        });

        planner.add({
            "OPS-202",
            "Reconcile warehouse inventory",
            "Warehouse",
            2,
            4.0,
            {"reconciliation", "quality"},
            {"OPS-201"},
            Status::Pending
        });

        planner.add({
            "OPS-203",
            "Refresh procurement dashboard",
            "Analytics",
            1,
            3.0,
            {"reporting", "quality"},
            {"OPS-202"},
            Status::Pending
        });

        planner.add({
            "OPS-204",
            "Archive validation evidence",
            "Data Operations",
            3,
            1.0,
            {"validation", "audit"},
            {"OPS-201"},
            Status::Pending
        });

        planner.printReport();

        std::cout << "\nRecords carrying both validation and quality:\n";

        for (const auto& id : planner.searchLabels({"validation", "quality"})) {
            std::cout << id << '\n';
        }

        planner.transition("OPS-201", Status::InProgress);
        planner.transition("OPS-201", Status::Completed);

        std::cout << "\nReady after completing OPS-201:\n";

        for (const auto& id : planner.readyOrders()) {
            std::cout << id << '\n';
        }

        // A dependency prevents premature execution, even if a caller knows the ID.
        try {
            planner.transition("OPS-203", Status::InProgress);
        } catch (const std::logic_error& error) {
            std::cout << "Blocked transition: " << error.what() << '\n';
        }

        planner.printSharedLabels("Data Operations", "Warehouse");

    } catch (const std::exception& error) {
        std::cerr << "Operations planning failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
