#include <algorithm>
#include <chrono>
#include <cctype>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Installing Packages with pip
 *
 * C++17 package dependency and installation governance engine.
 *
 * Models:
 * - Package catalog
 * - Version requirements
 * - Dependency resolution
 * - Dependency cycles
 * - Conflicting versions
 * - Installation policies
 * - Installation states
 * - Installation eligibility
 *
 * This program models package installation decisions.
 * It does not replace the actual pip resolver.
 */

enum class PackageState {
    AVAILABLE,
    VALIDATED,
    RESOLVED,
    INSTALLING,
    INSTALLED,
    FAILED,
    BLOCKED
};

enum class RiskLevel {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
};

enum class Operation {
    INSTALL,
    UPGRADE,
    REMOVE
};

std::string toString(PackageState state) {
    switch (state) {
        case PackageState::AVAILABLE: return "AVAILABLE";
        case PackageState::VALIDATED: return "VALIDATED";
        case PackageState::RESOLVED: return "RESOLVED";
        case PackageState::INSTALLING: return "INSTALLING";
        case PackageState::INSTALLED: return "INSTALLED";
        case PackageState::FAILED: return "FAILED";
        case PackageState::BLOCKED: return "BLOCKED";
    }

    return "UNKNOWN";
}

struct Dependency {
    std::string name;
    std::string minimumVersion;
};

struct Package {
    std::string name;
    std::string version;
    std::string index;
    std::string sha256;
    RiskLevel risk = RiskLevel::LOW;
    std::vector<Dependency> dependencies;
};

struct InstallationRecord {
    std::string packageName;
    std::string version;
    PackageState state;
    std::string message;
};

class Version {
public:
    static std::vector<int> parse(const std::string& value) {
        if (value.empty()) {
            throw std::invalid_argument("Empty version.");
        }

        std::vector<int> parts;
        std::stringstream stream(value);
        std::string token;

        while (std::getline(stream, token, '.')) {
            if (token.empty()) {
                throw std::invalid_argument(
                    "Invalid version: " + value
                );
            }

            if (!std::all_of(
                    token.begin(),
                    token.end(),
                    [](unsigned char c) {
                        return std::isdigit(c);
                    })) {
                throw std::invalid_argument(
                    "This model accepts numeric versions only: " + value
                );
            }

            parts.push_back(std::stoi(token));
        }

        return parts;
    }

    static bool atLeast(
        const std::string& actual,
        const std::string& required
    ) {
        auto a = parse(actual);
        auto b = parse(required);

        const std::size_t size = std::max(
            a.size(), b.size()
        );

        a.resize(size, 0);
        b.resize(size, 0);

        return a >= b;
    }
};

class PackageCatalog {
private:
    std::map<std::string, Package> packages;

public:
    void add(const Package& package) {
        if (package.name.empty() || package.version.empty()) {
            throw std::invalid_argument(
                "Package name and version are required."
            );
        }

        Version::parse(package.version);

        if (!package.index.starts_with("https://")) {
            throw std::invalid_argument(
                "Package index must use HTTPS."
            );
        }

        if (!package.sha256.empty()) {
            if (
                package.sha256.size() != 64 ||
                !std::all_of(
                    package.sha256.begin(),
                    package.sha256.end(),
                    [](unsigned char c) {
                        return std::isxdigit(c);
                    }
                )
            ) {
                throw std::invalid_argument(
                    "Invalid SHA-256 digest."
                );
            }
        }

        const auto key = package.name;

        if (packages.count(key)) {
            throw std::invalid_argument(
                "Duplicate package: " + key
            );
        }

        packages.emplace(key, package);
    }

    const Package& get(const std::string& name) const {
        auto it = packages.find(name);

        if (it == packages.end()) {
            throw std::runtime_error(
                "Unknown package: " + name
            );
        }

        return it->second;
    }

    bool contains(const std::string& name) const {
        return packages.count(name) > 0;
    }

    std::size_t size() const {
        return packages.size();
    }
};

class SecurityPolicy {
private:
    std::set<std::string> allowedIndexes;
    std::set<std::string> deniedPackages;
    bool requireHash;
    RiskLevel maximumRisk;

public:
    SecurityPolicy(
        std::set<std::string> indexes,
        std::set<std::string> denied,
        bool hashRequired,
        RiskLevel riskLimit
    )
        : allowedIndexes(std::move(indexes)),
          deniedPackages(std::move(denied)),
          requireHash(hashRequired),
          maximumRisk(riskLimit) {}

    bool evaluate(const Package& package) const {
        if (deniedPackages.count(package.name)) {
            return false;
        }

        if (!allowedIndexes.count(package.index)) {
            return false;
        }

        if (
            requireHash &&
            package.sha256.empty()
        ) {
            return false;
        }

        if (
            static_cast<int>(package.risk) >
            static_cast<int>(maximumRisk)
        ) {
            return false;
        }

        return true;
    }
};

class DependencyResolver {
private:
    const PackageCatalog& catalog;
    std::map<std::string, int> colors;
    std::vector<std::string> ordered;
    std::map<std::string, std::string> selectedVersions;

    void visit(const std::string& name) {
        int& color = colors[name];

        if (color == 1) {
            throw std::runtime_error(
                "Circular dependency detected at " + name
            );
        }

        if (color == 2) {
            return;
        }

        color = 1;

        const Package& package = catalog.get(name);

        auto selected = selectedVersions.find(name);

        if (selected != selectedVersions.end()) {
            if (selected->second != package.version) {
                throw std::runtime_error(
                    "Conflicting package versions: " + name
                );
            }
        } else {
            selectedVersions[name] = package.version;
        }

        for (const auto& dependency : package.dependencies) {
            if (!catalog.contains(dependency.name)) {
                throw std::runtime_error(
                    "Missing dependency: " + dependency.name
                );
            }

            const Package& required =
                catalog.get(dependency.name);

            if (!Version::atLeast(
                    required.version,
                    dependency.minimumVersion
                )) {
                throw std::runtime_error(
                    "Dependency version not satisfied: " +
                    dependency.name
                );
            }

            visit(dependency.name);
        }

        color = 2;
        ordered.push_back(name);
    }

public:
    explicit DependencyResolver(
        const PackageCatalog& source
    ) : catalog(source) {}

    std::vector<std::string> resolve(
        const std::string& root
    ) {
        colors.clear();
        ordered.clear();
        selectedVersions.clear();

        visit(root);
        return ordered;
    }
};

class InstallationEngine {
private:
    const PackageCatalog& catalog;
    const SecurityPolicy& policy;
    std::vector<InstallationRecord> history;

public:
    InstallationEngine(
        const PackageCatalog& source,
        const SecurityPolicy& security
    ) : catalog(source), policy(security) {}

    bool install(const std::string& root) {
        DependencyResolver resolver(catalog);

        try {
            std::vector<std::string> plan =
                resolver.resolve(root);

            std::cout << "\nInstallation plan:\n";

            for (const auto& name : plan) {
                const Package& package = catalog.get(name);

                if (!policy.evaluate(package)) {
                    throw std::runtime_error(
                        "Security policy rejected " + name
                    );
                }

                std::cout
                    << "  " << name
                    << " == " << package.version
                    << '\n';
            }

            // Dependencies are processed before their dependents.
            for (const auto& name : plan) {
                const Package& package = catalog.get(name);

                history.push_back({
                    name,
                    package.version,
                    PackageState::INSTALLED,
                    "Approved by simulated installation engine."
                });
            }

            std::cout << "Installation plan approved.\n";
            return true;

        } catch (const std::exception& error) {
            history.push_back({
                root,
                "",
                PackageState::BLOCKED,
                error.what()
            });

            std::cerr
                << "Installation blocked: "
                << error.what()
                << '\n';

            return false;
        }
    }

    void printHistory() const {
        std::cout << "\nInstallation history:\n";

        for (const auto& record : history) {
            std::cout
                << std::left
                << std::setw(14) << record.packageName
                << std::setw(12) << record.version
                << std::setw(12) << toString(record.state)
                << record.message
                << '\n';
        }
    }
};

Package makePackage(
    std::string name,
    std::string version,
    RiskLevel risk,
    std::vector<Dependency> dependencies = {}
) {
    return Package{
        std::move(name),
        std::move(version),
        "https://pypi.org/simple",
        "",
        risk,
        std::move(dependencies)
    };
}

int main() {
    try {
        std::cout
            << "=== PIP PACKAGE GOVERNANCE ENGINE ===\n";

        PackageCatalog catalog;

        catalog.add(makePackage(
            "urllib3",
            "2.2.3",
            RiskLevel::LOW
        ));

        catalog.add(makePackage(
            "certifi",
            "2024.8.30",
            RiskLevel::LOW
        ));

        catalog.add(makePackage(
            "charset-normalizer",
            "3.4.0",
            RiskLevel::LOW
        ));

        catalog.add(makePackage(
            "idna",
            "3.10",
            RiskLevel::LOW
        ));

        catalog.add(makePackage(
            "requests",
            "2.32.3",
            RiskLevel::LOW,
            {
                {"urllib3", "1.21.1"},
                {"certifi", "2017.4.17"},
                {"charset-normalizer", "2.0.0"},
                {"idna", "2.5"}
            }
        ));

        catalog.add(makePackage(
            "unsafe-library",
            "1.0.0",
            RiskLevel::CRITICAL
        ));

        std::cout
            << "\nCatalog packages: "
            << catalog.size()
            << '\n';

        SecurityPolicy policy(
            {"https://pypi.org/simple"},
            {"malicious-package"},
            false,
            RiskLevel::HIGH
        );

        InstallationEngine engine(
            catalog,
            policy
        );

        std::cout << "\nScenario 1: Valid package\n";
        engine.install("requests");

        std::cout << "\nScenario 2: Security rejection\n";
        engine.install("unsafe-library");

        std::cout << "\nScenario 3: Missing package\n";
        engine.install("unknown-package");

        engine.printHistory();

        std::cout
            << "\nDependency resolution and policy evaluation "
            << "completed.\n";

        std::cout
            << "Note: This is a governance simulation, "
            << "not an actual pip installation.\n";

    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }

    return 0;
}
