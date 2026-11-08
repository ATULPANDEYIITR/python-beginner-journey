#include <algorithm>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Creating Your Own Modules
 *
 * C++17 module architecture using namespaces, abstract interfaces,
 * polymorphism, dependency graphs and a module registry.
 *
 * C++17 does not provide standardized C++ modules.
 * This implementation uses conventional translation-unit boundaries
 * and namespace-based interfaces.
 */

namespace module_system {

enum class State {
    Registered,
    Initialized,
    Active,
    Failed,
    Disabled
};

enum class Permission {
    ReadData,
    WriteData,
    Calculate,
    ExportData
};

std::string stateName(State state) {
    switch (state) {
        case State::Registered: return "Registered";
        case State::Initialized: return "Initialized";
        case State::Active: return "Active";
        case State::Failed: return "Failed";
        case State::Disabled: return "Disabled";
    }

    return "Unknown";
}

struct Version {
    int major;
    int minor;
    int patch;

    bool operator>=(const Version& other) const {
        if (major != other.major) {
            return major > other.major;
        }

        if (minor != other.minor) {
            return minor > other.minor;
        }

        return patch >= other.patch;
    }

    std::string toString() const {
        return std::to_string(major) + "." +
               std::to_string(minor) + "." +
               std::to_string(patch);
    }
};

struct Dependency {
    std::string name;
    Version minimumVersion;
};

struct Metadata {
    std::string name;
    Version version;
    std::string description;
    std::set<Permission> permissions;
    std::vector<Dependency> dependencies;
};

struct Configuration {
    int precision = 2;
    std::string reportTitle = "Module Report";
};

struct Payload {
    std::string operation;
    std::vector<double> values;
};

struct Result {
    std::string moduleName;
    std::string operation;
    double value;
    std::size_t inputCount;
};

class Module {
public:
    virtual ~Module() = default;

    virtual void initialize(
        const Configuration& configuration
    ) = 0;

    virtual Result execute(
        const Payload& payload
    ) const = 0;

    virtual void shutdown() = 0;
};

struct ModuleRecord {
    Metadata metadata;
    std::unique_ptr<Module> implementation;
    State state = State::Registered;
    std::size_t executionCount = 0;
    std::string lastError;
};

class AnalyticsModule final : public Module {
private:
    int precision_ = 2;
    bool initialized_ = false;

public:
    void initialize(
        const Configuration& configuration
    ) override {
        if (
            configuration.precision < 0 ||
            configuration.precision > 12
        ) {
            throw std::invalid_argument(
                "Precision must be between 0 and 12."
            );
        }

        precision_ = configuration.precision;
        initialized_ = true;
    }

    Result execute(const Payload& payload) const override {
        if (!initialized_) {
            throw std::runtime_error(
                "Analytics module is not initialized."
            );
        }

        if (payload.values.empty()) {
            throw std::invalid_argument(
                "Input collection cannot be empty."
            );
        }

        for (double value : payload.values) {
            if (!std::isfinite(value)) {
                throw std::invalid_argument(
                    "Input contains a non-finite number."
                );
            }
        }

        double result = 0.0;

        if (payload.operation == "sum") {
            for (double value : payload.values) {
                result += value;
            }
        } else if (payload.operation == "average") {
            for (double value : payload.values) {
                result += value;
            }

            result /= static_cast<double>(
                payload.values.size()
            );
        } else if (payload.operation == "maximum") {
            result = *std::max_element(
                payload.values.begin(),
                payload.values.end()
            );
        } else if (payload.operation == "minimum") {
            result = *std::min_element(
                payload.values.begin(),
                payload.values.end()
            );
        } else {
            throw std::invalid_argument(
                "Unsupported analytics operation."
            );
        }

        const double factor = std::pow(
            10.0,
            precision_
        );

        result = std::round(result * factor) / factor;

        return {
            "analytics",
            payload.operation,
            result,
            payload.values.size()
        };
    }

    void shutdown() override {
        initialized_ = false;
    }
};

class ModuleRegistry {
private:
    std::map<std::string, ModuleRecord> modules_;

    std::set<Permission> allowedPermissions_ = {
        Permission::ReadData,
        Permission::WriteData,
        Permission::Calculate,
        Permission::ExportData
    };

    void validateMetadata(const Metadata& metadata) const {
        if (
            metadata.name.empty() ||
            !std::islower(
                static_cast<unsigned char>(metadata.name[0])
            )
        ) {
            throw std::invalid_argument(
                "Invalid module name."
            );
        }

        if (metadata.description.empty()) {
            throw std::invalid_argument(
                "Module description is required."
            );
        }

        for (Permission permission : metadata.permissions) {
            if (!allowedPermissions_.count(permission)) {
                throw std::runtime_error(
                    "Module requests unauthorized permissions."
                );
            }
        }
    }

    void visit(
        const std::string& name,
        std::set<std::string>& visited,
        std::set<std::string>& visiting,
        std::vector<std::string>& order
    ) const {
        if (visiting.count(name)) {
            throw std::runtime_error(
                "Circular dependency detected: " + name
            );
        }

        if (visited.count(name)) {
            return;
        }

        auto it = modules_.find(name);

        if (it == modules_.end()) {
            throw std::runtime_error(
                "Missing module: " + name
            );
        }

        visiting.insert(name);

        for (
            const Dependency& dependency :
            it->second.metadata.dependencies
        ) {
            auto required = modules_.find(dependency.name);

            if (required == modules_.end()) {
                throw std::runtime_error(
                    "Missing dependency: " + dependency.name
                );
            }

            if (
                required->second.state == State::Disabled
            ) {
                throw std::runtime_error(
                    "Dependency is disabled: " + dependency.name
                );
            }

            if (
                !(required->second.metadata.version >=
                  dependency.minimumVersion)
            ) {
                throw std::runtime_error(
                    "Dependency version requirement not met."
                );
            }

            visit(
                dependency.name,
                visited,
                visiting,
                order
            );
        }

        visiting.erase(name);
        visited.insert(name);
        order.push_back(name);
    }

public:
    void registerModule(
        Metadata metadata,
        std::unique_ptr<Module> implementation
    ) {
        validateMetadata(metadata);

        if (!implementation) {
            throw std::invalid_argument(
                "Module implementation cannot be null."
            );
        }

        if (modules_.count(metadata.name)) {
            throw std::runtime_error(
                "Duplicate module registration."
            );
        }

        std::string name = metadata.name;

        ModuleRecord record;
        record.metadata = std::move(metadata);
        record.implementation = std::move(implementation);

        modules_.emplace(name, std::move(record));

        std::cout << "Registered: " << name << '\n';
    }

    std::vector<std::string> dependencyOrder(
        const std::string& name
    ) const {
        std::set<std::string> visited;
        std::set<std::string> visiting;
        std::vector<std::string> order;

        visit(name, visited, visiting, order);

        return order;
    }

    void activate(
        const std::string& name,
        const Configuration& configuration
    ) {
        const auto order = dependencyOrder(name);

        for (const std::string& current : order) {
            ModuleRecord& record = modules_.at(current);

            if (record.state == State::Active) {
                continue;
            }

            if (record.state == State::Disabled) {
                throw std::runtime_error(
                    "Cannot activate disabled module."
                );
            }

            try {
                record.implementation->initialize(
                    configuration
                );

                record.state = State::Active;

                std::cout << "Activated: " << current << '\n';

            } catch (const std::exception& error) {
                record.state = State::Failed;
                record.lastError = error.what();

                throw;
            }
        }
    }

    Result execute(
        const std::string& name,
        const Payload& payload
    ) {
        auto it = modules_.find(name);

        if (it == modules_.end()) {
            throw std::runtime_error(
                "Module not found."
            );
        }

        ModuleRecord& record = it->second;

        if (record.state != State::Active) {
            throw std::runtime_error(
                "Module is not active."
            );
        }

        try {
            Result result =
                record.implementation->execute(payload);

            ++record.executionCount;

            return result;

        } catch (const std::exception& error) {
            record.lastError = error.what();
            throw;
        }
    }

    void disable(const std::string& name) {
        auto it = modules_.find(name);

        if (it == modules_.end()) {
            throw std::runtime_error(
                "Module not found."
            );
        }

        for (const auto& entry : modules_) {
            if (entry.second.state != State::Active) {
                continue;
            }

            for (
                const Dependency& dependency :
                entry.second.metadata.dependencies
            ) {
                if (dependency.name == name) {
                    throw std::runtime_error(
                        "Cannot disable a module with active dependents."
                    );
                }
            }
        }

        ModuleRecord& record = it->second;

        if (record.state == State::Active) {
            record.implementation->shutdown();
        }

        record.state = State::Disabled;
    }

    void printInventory() const {
        std::cout << "\nMODULE INVENTORY\n";

        for (const auto& entry : modules_) {
            const ModuleRecord& record = entry.second;

            std::cout
                << std::left
                << std::setw(15) << entry.first
                << std::setw(12)
                << record.metadata.version.toString()
                << std::setw(15)
                << stateName(record.state)
                << "Executions: "
                << record.executionCount
                << '\n';

            if (!record.lastError.empty()) {
                std::cout
                    << "Last error: "
                    << record.lastError
                    << '\n';
            }
        }
    }
};

void runTests(ModuleRegistry& registry) {
    Result result = registry.execute(
        "analytics",
        {"average", {10, 20, 30, 40}}
    );

    if (result.value != 25.0) {
        throw std::runtime_error(
            "Average calculation test failed."
        );
    }

    bool emptyInputRejected = false;

    try {
        registry.execute(
            "analytics",
            {"sum", {}}
        );
    } catch (const std::invalid_argument&) {
        emptyInputRejected = true;
    }

    if (!emptyInputRejected) {
        throw std::runtime_error(
            "Empty input validation test failed."
        );
    }

    bool invalidOperationRejected = false;

    try {
        registry.execute(
            "analytics",
            {"multiply", {2, 3}}
        );
    } catch (const std::invalid_argument&) {
        invalidOperationRejected = true;
    }

    if (!invalidOperationRejected) {
        throw std::runtime_error(
            "Operation validation test failed."
        );
    }

    std::cout << "\nAll tests passed.\n";
}

} // namespace module_system


int main() {
    using namespace module_system;

    try {
        ModuleRegistry registry;

        Metadata analyticsMetadata{
            "analytics",
            {2, 1, 0},
            "Reusable numerical analytics module",
            {Permission::Calculate},
            {}
        };

        Metadata reportingMetadata{
            "reporting",
            {1, 0, 0},
            "Reporting functionality dependent on analytics",
            {Permission::ReadData, Permission::ExportData},
            {
                {"analytics", {2, 0, 0}}
            }
        };

        registry.registerModule(
            analyticsMetadata,
            std::make_unique<AnalyticsModule>()
        );

        registry.registerModule(
            reportingMetadata,
            std::make_unique<AnalyticsModule>()
        );

        Configuration configuration;
        configuration.precision = 3;
        configuration.reportTitle = "Quarterly Analytics";

        registry.activate(
            "reporting",
            configuration
        );

        Result result = registry.execute(
            "analytics",
            {
                "average",
                {100.0, 150.0, 200.0, 250.0}
            }
        );

        std::cout << "\nEXECUTION RESULT\n";
        std::cout << "Module: " << result.moduleName << '\n';
        std::cout << "Operation: " << result.operation << '\n';
        std::cout << "Result: " << result.value << '\n';
        std::cout << "Inputs: " << result.inputCount << '\n';

        runTests(registry);

        registry.printInventory();

        registry.disable("reporting");
        registry.disable("analytics");

    } catch (const std::exception& error) {
        std::cerr
            << "Application error: "
            << error.what()
            << '\n';

        return 1;
    }

    return 0;
}
