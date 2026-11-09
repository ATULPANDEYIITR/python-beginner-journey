/*
 * IMPORTING MODULES IN C++17
 *
 * C++17 uses textual inclusion through #include.
 * Standardized C++ modules and the import keyword are not
 * part of C++17.
 *
 * This program demonstrates:
 * - Standard-library header imports
 * - Header guards and translation-unit boundaries
 * - Namespace qualification
 * - Modular domain design
 * - Dependency registration
 * - Dependency ordering
 * - Circular dependency detection
 * - Module initialization
 * - Module lookup and caching
 * - Failure handling
 *
 * Compile:
 * g++ -std=c++17 -Wall -Wextra -pedantic -O2 importing_modules.cpp -o importing_modules
 *
 * Run:
 * ./importing_modules
 */

#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <utility>


// ---------------------------------------------------------
// 1. Standard-library imports
// ---------------------------------------------------------

namespace examples {

void demonstrateStandardImports() {

    std::cout << "\n1. STANDARD-LIBRARY IMPORTS\n";

    std::vector<int> numbers = {
        10, 20, 30, 40, 50
    };

    int total = 0;

    for (int number : numbers) {
        total += number;
    }

    double average =
        static_cast<double>(total) / numbers.size();

    std::cout << "Average: " << average << '\n';

    std::set<std::string> languages = {
        "Python",
        "Java",
        "C++",
        "JavaScript"
    };

    std::cout << "Unique languages:\n";

    for (const auto& language : languages) {
        std::cout << "  " << language << '\n';
    }
}

}


// ---------------------------------------------------------
// 2. Namespace qualification
// ---------------------------------------------------------

namespace analytics {

double calculateMean(
    const std::vector<double>& values
) {

    if (values.empty()) {
        throw std::invalid_argument(
            "Cannot calculate the mean of an empty collection"
        );
    }

    double total = 0.0;

    for (double value : values) {

        if (!std::isfinite(value)) {
            throw std::invalid_argument(
                "Non-finite values are not supported"
            );
        }

        total += value;
    }

    return total / values.size();
}

}


// ---------------------------------------------------------
// 3. Module domain model
// ---------------------------------------------------------

namespace repository {

enum class ModuleState {
    Registered,
    Loading,
    Loaded,
    Failed
};

struct Module {

    std::string name;

    std::vector<std::string> dependencies;

    ModuleState state = ModuleState::Registered;

    std::function<void()> initializer;
};


// ---------------------------------------------------------
// 4. Module registry
// ---------------------------------------------------------

class ModuleRegistry {

private:

    std::map<std::string, Module> modules;

    std::vector<std::string> loadOrder;

    void loadRecursive(
        const std::string& name
    ) {

        auto iterator = modules.find(name);

        if (iterator == modules.end()) {
            throw std::runtime_error(
                "Unknown module: " + name
            );
        }

        Module& module = iterator->second;

        if (module.state == ModuleState::Loaded) {
            return;
        }

        if (module.state == ModuleState::Loading) {
            throw std::runtime_error(
                "Circular dependency detected: " + name
            );
        }

        if (module.state == ModuleState::Failed) {
            throw std::runtime_error(
                "Module previously failed: " + name
            );
        }

        module.state = ModuleState::Loading;

        try {

            for (const auto& dependency :
                 module.dependencies) {

                loadRecursive(dependency);
            }

            if (module.initializer) {
                module.initializer();
            }

            module.state = ModuleState::Loaded;

            loadOrder.push_back(name);

        } catch (...) {

            module.state = ModuleState::Failed;

            throw;
        }
    }

public:

    void registerModule(Module module) {

        if (module.name.empty()) {
            throw std::invalid_argument(
                "Module name cannot be empty"
            );
        }

        if (modules.count(module.name) != 0) {
            throw std::invalid_argument(
                "Duplicate module: " + module.name
            );
        }

        if (!module.initializer) {
            throw std::invalid_argument(
                "Module initializer is required"
            );
        }

        std::set<std::string> uniqueDependencies(
            module.dependencies.begin(),
            module.dependencies.end()
        );

        if (
            uniqueDependencies.size() !=
            module.dependencies.size()
        ) {
            throw std::invalid_argument(
                "Duplicate module dependencies"
            );
        }

        if (uniqueDependencies.count(module.name)) {
            throw std::invalid_argument(
                "A module cannot depend on itself"
            );
        }

        modules.emplace(
            module.name,
            std::move(module)
        );
    }

    void load(const std::string& name) {

        loadRecursive(name);
    }

    void loadAll() {

        for (const auto& entry : modules) {
            load(entry.first);
        }
    }

    ModuleState getState(
        const std::string& name
    ) const {

        auto iterator = modules.find(name);

        if (iterator == modules.end()) {
            throw std::out_of_range(
                "Module not registered: " + name
            );
        }

        return iterator->second.state;
    }

    void printStatus() const {

        std::cout << "\nMODULE STATUS\n";

        for (const auto& entry : modules) {

            std::string state;

            switch (entry.second.state) {

                case ModuleState::Registered:
                    state = "REGISTERED";
                    break;

                case ModuleState::Loading:
                    state = "LOADING";
                    break;

                case ModuleState::Loaded:
                    state = "LOADED";
                    break;

                case ModuleState::Failed:
                    state = "FAILED";
                    break;
            }

            std::cout
                << entry.first
                << " : "
                << state
                << '\n';
        }

        std::cout << "\nLOAD ORDER\n";

        for (const auto& name : loadOrder) {
            std::cout << name << '\n';
        }
    }
};

}


// ---------------------------------------------------------
// 5. Independent application modules
// ---------------------------------------------------------

namespace application {

void initializeConfiguration() {
    std::cout << "Initializing configuration module\n";
}

void initializeDatabase() {
    std::cout << "Initializing database module\n";
}

void initializeAnalytics() {
    std::cout << "Initializing analytics module\n";
}

void initializeReporting() {
    std::cout << "Initializing reporting module\n";
}

void initializeApplication() {
    std::cout << "Initializing application module\n";
}

}


// ---------------------------------------------------------
// 6. Dependency registration
// ---------------------------------------------------------

void demonstrateModuleRegistry() {

    using repository::Module;
    using repository::ModuleRegistry;

    std::cout << "\n2. MODULE DEPENDENCY REGISTRY\n";

    ModuleRegistry registry;

    registry.registerModule({
        "configuration",
        {},
        repository::ModuleState::Registered,
        application::initializeConfiguration
    });

    registry.registerModule({
        "database",
        {"configuration"},
        repository::ModuleState::Registered,
        application::initializeDatabase
    });

    registry.registerModule({
        "analytics",
        {"database", "configuration"},
        repository::ModuleState::Registered,
        application::initializeAnalytics
    });

    registry.registerModule({
        "reporting",
        {"analytics"},
        repository::ModuleState::Registered,
        application::initializeReporting
    });

    registry.registerModule({
        "application",
        {"reporting", "configuration"},
        repository::ModuleState::Registered,
        application::initializeApplication
    });

    registry.load("application");

    // Repeated loading reuses the initialized module.
    registry.load("application");

    registry.printStatus();
}


// ---------------------------------------------------------
// 7. Dependency failure scenarios
// ---------------------------------------------------------

void demonstrateFailures() {

    std::cout << "\n3. DEPENDENCY FAILURE HANDLING\n";

    repository::ModuleRegistry registry;

    registry.registerModule({
        "first",
        {"second"},
        repository::ModuleState::Registered,
        []() {}
    });

    registry.registerModule({
        "second",
        {"first"},
        repository::ModuleState::Registered,
        []() {}
    });

    try {
        registry.load("first");
    } catch (const std::exception& error) {
        std::cout
            << "Circular dependency: "
            << error.what()
            << '\n';
    }

    repository::ModuleRegistry missing;

    missing.registerModule({
        "service",
        {"missing"},
        repository::ModuleState::Registered,
        []() {}
    });

    try {
        missing.load("service");
    } catch (const std::exception& error) {
        std::cout
            << "Missing dependency: "
            << error.what()
            << '\n';
    }
}


// ---------------------------------------------------------
// 8. Namespace and mathematical module demonstration
// ---------------------------------------------------------

void demonstrateNamespaceImport() {

    std::cout << "\n4. NAMESPACE-BASED MODULE USE\n";

    const std::vector<double> values = {
        12.5, 15.5, 18.0, 20.0
    };

    const double result =
        analytics::calculateMean(values);

    std::cout << "Mean: " << result << '\n';

    try {

        analytics::calculateMean({});

    } catch (const std::invalid_argument& error) {

        std::cout
            << "Validation error: "
            << error.what()
            << '\n';
    }
}


// ---------------------------------------------------------
// 9. Validation tests
// ---------------------------------------------------------

void runTests() {

    if (
        analytics::calculateMean({2.0, 4.0, 6.0})
        != 4.0
    ) {
        throw std::runtime_error(
            "Mean calculation test failed"
        );
    }

    repository::ModuleRegistry registry;

    registry.registerModule({
        "base",
        {},
        repository::ModuleState::Registered,
        []() {}
    });

    registry.registerModule({
        "service",
        {"base"},
        repository::ModuleState::Registered,
        []() {}
    });

    registry.load("service");

    if (
        registry.getState("base") !=
        repository::ModuleState::Loaded
    ) {
        throw std::runtime_error(
            "Base module loading test failed"
        );
    }

    if (
        registry.getState("service") !=
        repository::ModuleState::Loaded
    ) {
        throw std::runtime_error(
            "Service module loading test failed"
        );
    }

    std::cout << "\nAll C++17 tests passed.\n";
}


// ---------------------------------------------------------
// 10. Main
// ---------------------------------------------------------

int main() {

    try {

        examples::demonstrateStandardImports();

        demonstrateNamespaceImport();

        demonstrateModuleRegistry();

        demonstrateFailures();

        runTests();

        std::cout << "\nExecution completed.\n";

        return 0;

    } catch (const std::exception& error) {

        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
