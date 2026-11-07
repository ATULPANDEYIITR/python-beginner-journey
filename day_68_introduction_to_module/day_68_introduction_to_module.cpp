#include <algorithm>
#include <cmath>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Introduction to Modules in C++17
 *
 * C++17 does not provide the standardized C++20 module system.
 * This program demonstrates modular design using:
 * - Namespaces
 * - Classes
 * - Interfaces through abstract classes
 * - Separate logical components
 * - Dependency management
 * - Encapsulation
 * - Function registration
 * - Domain-specific validation
 *
 * Production C++17 projects commonly separate declarations
 * into .h/.hpp files and definitions into .cpp files.
 */

// =========================================================
// 1. Core module
// =========================================================

namespace Core {

    constexpr int MAX_RECORDS = 10000;

    enum class Status {
        SUCCESS,
        INVALID_INPUT,
        NOT_FOUND
    };

    struct Result {
        Status status;
        double value;
        std::string message;
    };

    void validateNumber(double value) {
        if (!std::isfinite(value)) {
            throw std::invalid_argument(
                "Input must be a finite number"
            );
        }
    }

}

// =========================================================
// 2. Mathematics module
// =========================================================

namespace Mathematics {

    class Calculator {
    public:

        double add(double a, double b) const {
            Core::validateNumber(a);
            Core::validateNumber(b);
            return a + b;
        }

        double multiply(double a, double b) const {
            Core::validateNumber(a);
            Core::validateNumber(b);
            return a * b;
        }

        double divide(double a, double b) const {
            Core::validateNumber(a);
            Core::validateNumber(b);

            if (b == 0.0) {
                throw std::domain_error(
                    "Division by zero"
                );
            }

            return a / b;
        }

        double average(
            const std::vector<double>& values
        ) const {

            if (values.empty()) {
                throw std::invalid_argument(
                    "Cannot calculate average of empty data"
                );
            }

            if (values.size() > Core::MAX_RECORDS) {
                throw std::length_error(
                    "Record limit exceeded"
                );
            }

            double total = 0.0;

            for (double value : values) {
                Core::validateNumber(value);
                total += value;
            }

            return total / values.size();
        }
    };

}

// =========================================================
// 3. Analytics module
// =========================================================

namespace Analytics {

    struct Report {
        std::size_t recordCount;
        double total;
        double average;
        double minimum;
        double maximum;
    };

    class ReportingService {
    private:
        Mathematics::Calculator calculator;

    public:

        Report generate(
            const std::vector<double>& records
        ) const {

            if (records.empty()) {
                throw std::invalid_argument(
                    "Report requires at least one record"
                );
            }

            if (records.size() > Core::MAX_RECORDS) {
                throw std::length_error(
                    "Too many records"
                );
            }

            double total = 0.0;

            for (double value : records) {
                Core::validateNumber(value);
                total += value;
            }

            const auto bounds = std::minmax_element(
                records.begin(),
                records.end()
            );

            return {
                records.size(),
                total,
                calculator.average(records),
                *bounds.first,
                *bounds.second
            };
        }
    };

}

// =========================================================
// 4. Module dependency manager
// =========================================================

namespace ModuleManagement {

    struct Module {
        std::string name;
        std::string version;
        std::vector<std::string> dependencies;
    };

    class Registry {
    private:
        std::map<std::string, Module> modules;

    public:

        void registerModule(const Module& module) {
            if (module.name.empty() ||
                module.version.empty()) {
                throw std::invalid_argument(
                    "Module name and version are required"
                );
            }

            if (modules.count(module.name)) {
                throw std::runtime_error(
                    "Duplicate module: " + module.name
                );
            }

            if (std::find(
                    module.dependencies.begin(),
                    module.dependencies.end(),
                    module.name
                ) != module.dependencies.end()) {

                throw std::invalid_argument(
                    "Self-dependency is not allowed"
                );
            }

            modules.emplace(module.name, module);
        }

        std::vector<std::string> resolve(
            const std::string& target
        ) const {

            if (!modules.count(target)) {
                throw std::runtime_error(
                    "Module not found: " + target
                );
            }

            std::set<std::string> visiting;
            std::set<std::string> visited;
            std::vector<std::string> order;

            std::function<void(const std::string&)> visit =
                [&](const std::string& name) {

                    if (visiting.count(name)) {
                        throw std::runtime_error(
                            "Circular dependency: " + name
                        );
                    }

                    if (visited.count(name)) {
                        return;
                    }

                    auto iterator = modules.find(name);

                    if (iterator == modules.end()) {
                        throw std::runtime_error(
                            "Missing dependency: " + name
                        );
                    }

                    visiting.insert(name);

                    for (const auto& dependency :
                         iterator->second.dependencies) {
                        visit(dependency);
                    }

                    visiting.erase(name);
                    visited.insert(name);
                    order.push_back(name);
                };

            visit(target);
            return order;
        }

        void display() const {
            for (const auto& entry : modules) {
                std::cout
                    << entry.second.name
                    << " v"
                    << entry.second.version
                    << '\n';
            }
        }
    };

}

// =========================================================
// 5. Plugin module
// =========================================================

namespace Plugins {

    class Plugin {
    public:
        virtual ~Plugin() = default;

        virtual std::string name() const = 0;

        virtual double execute(
            const std::vector<double>& values
        ) const = 0;
    };

    class TotalPlugin final : public Plugin {
    public:

        std::string name() const override {
            return "total";
        }

        double execute(
            const std::vector<double>& values
        ) const override {

            double total = 0.0;

            for (double value : values) {
                Core::validateNumber(value);
                total += value;
            }

            return total;
        }
    };

    class MaximumPlugin final : public Plugin {
    public:

        std::string name() const override {
            return "maximum";
        }

        double execute(
            const std::vector<double>& values
        ) const override {

            if (values.empty()) {
                throw std::invalid_argument(
                    "Maximum requires non-empty data"
                );
            }

            for (double value : values) {
                Core::validateNumber(value);
            }

            return *std::max_element(
                values.begin(),
                values.end()
            );
        }
    };

}

// =========================================================
// 6. Application module
// =========================================================

int main() {

    try {

        std::cout << "\n1. MATHEMATICS MODULE\n";

        Mathematics::Calculator calculator;

        std::cout << "Addition: "
                  << calculator.add(20, 10)
                  << '\n';

        std::cout << "Multiplication: "
                  << calculator.multiply(5, 6)
                  << '\n';

        std::cout << "Division: "
                  << calculator.divide(100, 4)
                  << '\n';


        std::cout << "\n2. ANALYTICS MODULE\n";

        std::vector<double> sales = {
            1200, 1500, 1800, 2000, 2500
        };

        Analytics::ReportingService reporting;

        Analytics::Report report =
            reporting.generate(sales);

        std::cout << "Records: "
                  << report.recordCount << '\n';

        std::cout << "Total: "
                  << report.total << '\n';

        std::cout << "Average: "
                  << report.average << '\n';

        std::cout << "Minimum: "
                  << report.minimum << '\n';

        std::cout << "Maximum: "
                  << report.maximum << '\n';


        std::cout << "\n3. MODULE REGISTRY\n";

        ModuleManagement::Registry registry;

        registry.registerModule({
            "core", "1.0.0", {}
        });

        registry.registerModule({
            "database", "2.0.0", {"core"}
        });

        registry.registerModule({
            "analytics", "1.0.0",
            {"core", "database"}
        });

        registry.registerModule({
            "dashboard", "1.0.0", {"analytics"}
        });

        std::cout << "Registered modules:\n";
        registry.display();

        std::cout << "Dependency load order:\n";

        for (const auto& name :
             registry.resolve("dashboard")) {
            std::cout << name << '\n';
        }


        std::cout << "\n4. PLUGIN MODULE\n";

        std::vector<std::unique_ptr<Plugins::Plugin>> plugins;

        plugins.push_back(
            std::make_unique<Plugins::TotalPlugin>()
        );

        plugins.push_back(
            std::make_unique<Plugins::MaximumPlugin>()
        );

        for (const auto& plugin : plugins) {
            std::cout
                << plugin->name()
                << ": "
                << plugin->execute(sales)
                << '\n';
        }


        std::cout << "\n5. ERROR HANDLING\n";

        try {
            calculator.divide(10, 0);
        } catch (const std::exception& error) {
            std::cout << "Handled: "
                      << error.what() << '\n';
        }

        try {
            registry.resolve("missing");
        } catch (const std::exception& error) {
            std::cout << "Dependency error: "
                      << error.what() << '\n';
        }


        std::cout << "\n6. VALIDATION\n";

        if (calculator.add(2, 3) != 5) {
            throw std::runtime_error(
                "Addition test failed"
            );
        }

        if (report.recordCount != 5) {
            throw std::runtime_error(
                "Reporting test failed"
            );
        }

        std::cout << "All tests passed.\n";

    } catch (const std::exception& error) {

        std::cerr << "Application failure: "
                  << error.what() << '\n';

        return 1;
    }

    return 0;
}
