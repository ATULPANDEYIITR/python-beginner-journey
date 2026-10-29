#include <algorithm>
#include <cassert>
#include <exception>
#include <fstream>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>

enum class Severity {
    Warning,
    Error,
    Critical
};

class ApplicationError : public std::runtime_error {
public:
    explicit ApplicationError(const std::string& message)
        : std::runtime_error(message) {}
};

class ValidationError : public ApplicationError {
public:
    explicit ValidationError(const std::string& message)
        : ApplicationError(message) {}
};

class ConfigurationError : public ApplicationError {
public:
    explicit ConfigurationError(const std::string& message)
        : ApplicationError(message) {}
};

class StorageError : public ApplicationError {
public:
    explicit StorageError(const std::string& message)
        : ApplicationError(message) {}
};

struct User {
    int id;
    std::string name;
    std::string email;
};

class UserRepository {
private:
    std::string filePath;

public:
    explicit UserRepository(std::string path)
        : filePath(std::move(path)) {
        if (filePath.empty()) {
            throw ConfigurationError("Repository path cannot be empty.");
        }
    }

    void save(const User& user) const {
        std::ofstream file(filePath, std::ios::app);

        if (!file) {
            throw StorageError(
                "Unable to open repository file: " + filePath
            );
        }

        file << user.id << ',' << user.name << ',' << user.email << '\n';

        if (!file) {
            throw StorageError(
                "Failed while writing user to: " + filePath
            );
        }
    }
};

User validateUser(
    int id,
    const std::string& name,
    const std::string& email
) {
    if (id <= 0) {
        throw ValidationError("User ID must be greater than zero.");
    }

    if (name.empty()) {
        throw ValidationError("User name cannot be empty.");
    }

    if (email.find('@') == std::string::npos) {
        throw ValidationError("Email must contain '@'.");
    }

    return User{id, name, email};
}

double divide(double total, double divisor) {
    if (divisor == 0.0) {
        throw std::domain_error("Divisor cannot be zero.");
    }

    return total / divisor;
}

int parseInteger(const std::string& value) {
    if (value.empty()) {
        throw ValidationError("Integer input cannot be empty.");
    }

    std::size_t consumed = 0;

    try {
        int result = std::stoi(value, &consumed);
        if (consumed != value.size()) {
            throw ValidationError("Input contains non-numeric characters.");
        }
        return result;
    } catch (const std::invalid_argument&) {
        throw ValidationError("Invalid integer: " + value);
    } catch (const std::out_of_range&) {
        throw ValidationError("Integer is outside the supported range.");
    }
}

void processUser(
    const UserRepository& repository,
    int id,
    const std::string& name,
    const std::string& email
) {
    User user = validateUser(id, name, email);
    repository.save(user);
}

void demonstrateExceptionTranslation() {
    try {
        parseInteger("invalid");
    } catch (const ValidationError& error) {
        std::cout << "Translated failure: " << error.what() << '\n';
    }
}

void demonstrateCleanup() {
    struct ResourceGuard {
        ~ResourceGuard() {
            std::cout << "Resource cleanup executed.\n";
        }
    };

    try {
        ResourceGuard guard;
        throw std::runtime_error("Simulated processing failure.");
    } catch (const std::exception& error) {
        std::cout << "Cleanup example: " << error.what() << '\n';
    }
}

void runTests() {
    User user = validateUser(1, "Ada", "ada@example.com");
    assert(user.id == 1);

    try {
        validateUser(0, "Ada", "ada@example.com");
        assert(false);
    } catch (const ValidationError&) {
    }

    try {
        divide(10.0, 0.0);
        assert(false);
    } catch (const std::domain_error&) {
    }

    try {
        parseInteger("abc");
        assert(false);
    } catch (const ValidationError&) {
    }
}

int main() {
    try {
        std::cout << "Raising Exceptions Demonstration\n";

        try {
            UserRepository repository("users_demo_cpp.csv");
            processUser(
                repository,
                101,
                "Grace Hopper",
                "grace@example.com"
            );
            std::cout << "User stored successfully.\n";
        } catch (const ValidationError& error) {
            std::cerr << "Validation failure: " << error.what() << '\n';
        } catch (const StorageError& error) {
            std::cerr << "Storage failure: " << error.what() << '\n';
        }

        try {
            UserRepository repository("users_demo_cpp.csv");
            processUser(
                repository,
                -4,
                "Invalid User",
                "invalid@example.com"
            );
        } catch (const ApplicationError& error) {
            std::cout << "Expected application failure: "
                      << error.what() << '\n';
        }

        try {
            divide(25.0, 0.0);
        } catch (const std::domain_error& error) {
            std::cout << "Expected arithmetic failure: "
                      << error.what() << '\n';
        }

        demonstrateExceptionTranslation();
        demonstrateCleanup();
        runTests();

        std::cout << "All exception assertions passed.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Unhandled fatal error: "
                  << error.what() << '\n';
        return 1;
    }
}
