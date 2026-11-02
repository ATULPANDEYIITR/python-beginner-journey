#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

enum class WriteMode {
    Write,
    Append
};

struct WriteResult {
    fs::path path;
    WriteMode mode;
    std::size_t bytesWritten;
    std::size_t lineCount;
};

struct AuditRecord {
    std::string operation;
    std::string filename;
    std::size_t bytes;
    std::size_t lines;
};

class FileOperationError : public std::runtime_error {
public:
    explicit FileOperationError(const std::string& message)
        : std::runtime_error(message) {}
};

class FileStore {
private:
    fs::path baseDirectory;
    std::size_t maxBytes;
    std::vector<AuditRecord> auditLog;

    fs::path safePath(const std::string& filename) const {
        if (filename.empty() || filename == "." || filename == "..") {
            throw FileOperationError("A valid filename is required.");
        }

        const fs::path target =
            fs::weakly_canonical(baseDirectory / filename);

        const fs::path base =
            fs::weakly_canonical(baseDirectory);

        auto baseIt = base.begin();
        auto targetIt = target.begin();

        while (baseIt != base.end() &&
               targetIt != target.end() &&
               *baseIt == *targetIt) {
            ++baseIt;
            ++targetIt;
        }

        if (baseIt != base.end()) {
            throw FileOperationError(
                "Path escapes the configured directory."
            );
        }

        return target;
    }

    static std::size_t countLines(const std::string& content) {
        if (content.empty()) {
            return 0;
        }

        std::size_t lines =
            static_cast<std::size_t>(
                std::count(content.begin(), content.end(), '\n')
            );

        if (content.back() != '\n') {
            ++lines;
        }

        return lines;
    }

    WriteResult save(
        const std::string& filename,
        const std::string& content,
        WriteMode mode
    ) {
        if (content.size() > maxBytes) {
            throw FileOperationError("Content exceeds the configured size limit.");
        }

        const fs::path target = safePath(filename);

        std::error_code error;
        fs::create_directories(target.parent_path(), error);

        if (error) {
            throw FileOperationError(
                "Unable to create parent directories: " + error.message()
            );
        }

        std::ios::openmode flags =
            std::ios::out |
            (mode == WriteMode::Write ? std::ios::trunc : std::ios::app);

        std::ofstream output(target, flags);

        if (!output.is_open()) {
            throw FileOperationError(
                "Unable to open file for writing: " + target.string()
            );
        }

        output << content;
        output.flush();

        if (!output) {
            throw FileOperationError(
                "The write operation failed: " + target.string()
            );
        }

        const std::string relative =
            fs::relative(target, baseDirectory).string();

        auditLog.push_back({
            mode == WriteMode::Write ? "write" : "append",
            relative,
            content.size(),
            countLines(content)
        });

        return {
            target,
            mode,
            content.size(),
            countLines(content)
        };
    }

public:
    explicit FileStore(fs::path directory,
                       std::size_t maximumBytes = 5 * 1024 * 1024)
        : baseDirectory(fs::absolute(std::move(directory))),
          maxBytes(maximumBytes) {
        std::error_code error;
        fs::create_directories(baseDirectory, error);

        if (error) {
            throw FileOperationError(
                "Unable to initialize storage directory: " +
                error.message()
            );
        }
    }

    WriteResult write(
        const std::string& filename,
        const std::string& content
    ) {
        return save(filename, content, WriteMode::Write);
    }

    WriteResult append(
        const std::string& filename,
        const std::string& content
    ) {
        return save(filename, content, WriteMode::Append);
    }

    WriteResult appendLines(
        const std::string& filename,
        const std::vector<std::string>& lines
    ) {
        std::string content;

        for (const auto& line : lines) {
            std::string normalized = line;
            normalized.erase(
                std::remove(
                    normalized.begin(),
                    normalized.end(),
                    '\r'
                ),
                normalized.end()
            );

            normalized.erase(
                std::remove(
                    normalized.begin(),
                    normalized.end(),
                    '\n'
                ),
                normalized.end()
            );

            content += normalized;
            content += '\n';
        }

        return append(filename, content);
    }

    std::string read(const std::string& filename) const {
        const fs::path target = safePath(filename);

        std::ifstream input(target);

        if (!input.is_open()) {
            throw FileOperationError(
                "Unable to open file for reading: " + target.string()
            );
        }

        return std::string(
            std::istreambuf_iterator<char>(input),
            std::istreambuf_iterator<char>()
        );
    }

    std::size_t size(const std::string& filename) const {
        const fs::path target = safePath(filename);

        std::error_code error;
        const auto result = fs::file_size(target, error);

        if (error) {
            throw FileOperationError(
                "Unable to determine file size: " + error.message()
            );
        }

        return static_cast<std::size_t>(result);
    }

    const std::vector<AuditRecord>& auditRecords() const {
        return auditLog;
    }
};

int main() {
    try {
        const fs::path temporaryDirectory =
            fs::temp_directory_path() / "cpp_file_writing_case";

        std::error_code cleanupError;
        fs::remove_all(temporaryDirectory, cleanupError);

        FileStore store(temporaryDirectory);

        store.write(
            "logs/application.log",
            "Application started\n"
        );

        store.append(
            "logs/application.log",
            "Configuration loaded\n"
        );

        store.appendLines(
            "logs/application.log",
            {
                "Database connection established",
                "Worker process started",
                "Application ready"
            }
        );

        const std::string expected =
            "Application started\n"
            "Configuration loaded\n"
            "Database connection established\n"
            "Worker process started\n"
            "Application ready\n";

        const std::string actual =
            store.read("logs/application.log");

        if (actual != expected) {
            throw FileOperationError("Content validation failed.");
        }

        if (store.size("logs/application.log") != expected.size()) {
            throw FileOperationError("File-size validation failed.");
        }

        try {
            store.append("../outside.txt", "blocked\n");
            throw FileOperationError(
                "Path traversal was not rejected."
            );
        } catch (const FileOperationError& error) {
            if (std::string(error.what()).find("Path escapes") ==
                std::string::npos) {
                throw;
            }
        }

        std::cout << "File content:\n";
        std::cout << actual;

        std::cout << "\nAudit records:\n";
        for (const auto& record : store.auditRecords()) {
            std::cout
                << record.operation << " | "
                << record.filename << " | "
                << record.bytes << " bytes | "
                << record.lines << " lines\n";
        }

        fs::remove_all(temporaryDirectory, cleanupError);
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
