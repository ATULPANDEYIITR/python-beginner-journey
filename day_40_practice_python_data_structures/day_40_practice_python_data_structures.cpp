#include <algorithm>
#include <cassert>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * Case study: Distribution-centre inventory and route management.
 *
 * The system uses associative containers for SKU lookup, sets for unique
 * shipment identifiers, a priority queue for urgent replenishment, and an
 * adjacency map for route planning. It is intentionally self-contained.
 */

struct InventoryItem {
    std::string sku;
    std::string description;
    int quantity;
    int reorderLevel;
    double unitCost;
};

class Inventory {
private:
    std::unordered_map<std::string, InventoryItem> items_;

public:
    void addItem(const InventoryItem& item) {
        if (item.sku.empty() || item.description.empty()) {
            throw std::invalid_argument("SKU and description are required");
        }
        if (item.quantity < 0 || item.reorderLevel < 0) {
            throw std::invalid_argument("Inventory quantities cannot be negative");
        }
        if (!std::isfinite(item.unitCost) || item.unitCost < 0) {
            throw std::invalid_argument("Unit cost must be finite and non-negative");
        }

        const auto [iterator, inserted] = items_.emplace(item.sku, item);
        if (!inserted) {
            throw std::invalid_argument("Duplicate SKU: " + item.sku);
        }
    }

    const InventoryItem& get(const std::string& sku) const {
        const auto iterator = items_.find(sku);
        if (iterator == items_.end()) {
            throw std::out_of_range("Unknown SKU: " + sku);
        }
        return iterator->second;
    }

    std::vector<InventoryItem> belowReorderLevel() const {
        std::vector<InventoryItem> result;
        for (const auto& [sku, item] : items_) {
            if (item.quantity < item.reorderLevel) {
                result.push_back(item);
            }
        }

        // unordered_map iteration order is unspecified; sort for reproducible output.
        std::sort(result.begin(), result.end(),
                  [](const InventoryItem& a, const InventoryItem& b) {
                      return a.sku < b.sku;
                  });
        return result;
    }

    double totalInventoryValue() const {
        double total = 0.0;
        for (const auto& [sku, item] : items_) {
            total += static_cast<double>(item.quantity) * item.unitCost;
        }
        return total;
    }
};

struct ReplenishmentTask {
    int urgency;
    std::string sku;
    int quantity;

    // priority_queue places the element with the largest comparator priority
    // at the top. Reverse urgency comparison so lower numbers run first.
    bool operator<(const ReplenishmentTask& other) const {
        if (urgency != other.urgency) {
            return urgency > other.urgency;
        }
        return sku > other.sku;
    }
};

class ReplenishmentScheduler {
private:
    std::priority_queue<ReplenishmentTask> tasks_;
    std::unordered_set<std::string> scheduledSkus_;

public:
    void schedule(const InventoryItem& item, int urgency) {
        if (item.sku.empty()) {
            throw std::invalid_argument("Cannot schedule an empty SKU");
        }
        if (urgency < 1 || urgency > 5) {
            throw std::invalid_argument("Urgency must be between 1 and 5");
        }
        if (item.quantity >= item.reorderLevel) {
            throw std::invalid_argument("Item does not require replenishment");
        }
        if (item.reorderLevel <= item.quantity) {
            throw std::invalid_argument("Replenishment quantity must be positive");
        }
        if (!scheduledSkus_.insert(item.sku).second) {
            throw std::invalid_argument("SKU already has a scheduled task");
        }

        tasks_.push({urgency, item.sku, item.reorderLevel - item.quantity});
    }

    bool empty() const {
        return tasks_.empty();
    }

    ReplenishmentTask next() {
        if (tasks_.empty()) {
            throw std::underflow_error("No replenishment tasks remain");
        }
        const auto task = tasks_.top();
        tasks_.pop();
        scheduledSkus_.erase(task.sku);
        return task;
    }
};

class RouteGraph {
private:
    std::map<std::string, std::map<std::string, double>> adjacency_;

public:
    void addUndirectedRoute(
        const std::string& from,
        const std::string& to,
        double distance
    ) {
        if (from.empty() || to.empty() || from == to) {
            throw std::invalid_argument("Route endpoints must be distinct and non-empty");
        }
        if (!std::isfinite(distance) || distance < 0) {
            throw std::invalid_argument("Distance must be finite and non-negative");
        }

        adjacency_[from][to] = distance;
        adjacency_[to][from] = distance;
    }

    std::pair<double, std::vector<std::string>> shortestPath(
        const std::string& source,
        const std::string& destination
    ) const {
        if (!adjacency_.count(source) || !adjacency_.count(destination)) {
            return {std::numeric_limits<double>::infinity(), {}};
        }

        using QueueEntry = std::pair<double, std::string>;
        std::priority_queue<
            QueueEntry,
            std::vector<QueueEntry>,
            std::greater<QueueEntry>
        > frontier;

        std::map<std::string, double> distances;
        std::map<std::string, std::string> previous;

        distances[source] = 0.0;
        frontier.push({0.0, source});

        while (!frontier.empty()) {
            const auto [distance, vertex] = frontier.top();
            frontier.pop();

            // Ignore outdated entries left in the heap by a later improvement.
            if (distance > distances.at(vertex)) {
                continue;
            }
            if (vertex == destination) {
                break;
            }

            for (const auto& [neighbor, weight] : adjacency_.at(vertex)) {
                const double candidate = distance + weight;
                const auto known = distances.find(neighbor);

                if (known == distances.end() || candidate < known->second) {
                    distances[neighbor] = candidate;
                    previous[neighbor] = vertex;
                    frontier.push({candidate, neighbor});
                }
            }
        }

        if (!distances.count(destination)) {
            return {std::numeric_limits<double>::infinity(), {}};
        }

        std::vector<std::string> path;
        std::string current = destination;
        path.push_back(current);

        while (current != source) {
            const auto parent = previous.find(current);
            if (parent == previous.end()) {
                throw std::logic_error("Path reconstruction failed");
            }
            current = parent->second;
            path.push_back(current);
        }

        std::reverse(path.begin(), path.end());
        return {distances.at(destination), path};
    }
};

int main() {
    try {
        Inventory inventory;
        inventory.addItem({"CPU-01", "Server processor", 2, 8, 240.00});
        inventory.addItem({"RAM-16", "Memory module", 14, 10, 68.50});
        inventory.addItem({"SSD-02", "Enterprise SSD", 1, 6, 115.00});
        inventory.addItem({"NET-10", "Network adapter", 4, 5, 39.99});

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Inventory value: $" << inventory.totalInventoryValue() << "\n";

        ReplenishmentScheduler scheduler;
        for (const auto& item : inventory.belowReorderLevel()) {
            const int urgency = item.quantity <= 2 ? 1 : 3;
            scheduler.schedule(item, urgency);
        }

        std::cout << "\nReplenishment schedule:\n";
        while (!scheduler.empty()) {
            const auto task = scheduler.next();
            std::cout << "Urgency " << task.urgency
                      << ", SKU " << task.sku
                      << ", quantity " << task.quantity << "\n";
        }

        RouteGraph routes;
        routes.addUndirectedRoute("Warehouse", "NorthHub", 4.5);
        routes.addUndirectedRoute("Warehouse", "SouthHub", 6.0);
        routes.addUndirectedRoute("NorthHub", "CityStore", 3.0);
        routes.addUndirectedRoute("SouthHub", "CityStore", 2.0);
        routes.addUndirectedRoute("NorthHub", "SouthHub", 1.5);

        const auto [distance, path] =
            routes.shortestPath("Warehouse", "CityStore");

        std::cout << "\nOptimal delivery route: ";
        for (std::size_t index = 0; index < path.size(); ++index) {
            if (index) std::cout << " -> ";
            std::cout << path[index];
        }
        std::cout << "\nDistance: " << distance << "\n";

        const auto [missingDistance, missingPath] =
            routes.shortestPath("Warehouse", "RemoteDepot");
        assert(std::isinf(missingDistance));
        assert(missingPath.empty());

        // Validation prevents duplicate identifiers and impossible inventory.
        bool duplicateRejected = false;
        try {
            inventory.addItem({"CPU-01", "Duplicate processor", 1, 2, 10.00});
        } catch (const std::invalid_argument&) {
            duplicateRejected = true;
        }
        assert(duplicateRejected);

        bool negativeRouteRejected = false;
        try {
            routes.addUndirectedRoute("Warehouse", "Unsafe", -4.0);
        } catch (const std::invalid_argument&) {
            negativeRouteRejected = true;
        }
        assert(negativeRouteRejected);

        bool unknownSkuRejected = false;
        try {
            (void)inventory.get("MISSING");
        } catch (const std::out_of_range&) {
            unknownSkuRejected = true;
        }
        assert(unknownSkuRejected);

        std::cout << "\nAll inventory and route checks passed.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << "\n";
        return 1;
    }
}
