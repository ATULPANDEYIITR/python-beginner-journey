#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

class PathSecurityError : public std::runtime_error {
public:
    explicit PathSecurityError(const std::string& message)
        : std::runtime_error(message) {}
};

enum class PathKind {
    File,
    Directory,
    Missing
};

struct PathInfo {
    std::string original;
    fs::path normalized;
    PathKind kind;
};

class FilePathManager {
private:
    fs::path root;

    bool insideRoot(const fs::path& candidate) const {
        auto current = candidate;
        auto base = root;

        auto currentIt = current.begin();
        auto baseIt = base.begin();

        for (; baseIt != base.end(); ++baseIt, ++currentIt) {
            if (currentIt == current.end() || *currentIt != *baseIt) {
                return false;
            }
        }

        return true;
    }

public:
    explicit FilePathManager(const fs::path& rootPath)
        : root(fs::weakly_canonical(rootPath)) {
        fs::create_directories(root);
    }

    fs::path safePath(const fs::path& relative) const {
        if (relative.empty()) {
            throw PathSecurityError("Empty path");
        }

        if (relative.is_absolute()) {
            throw PathSecurityError("Absolute paths are not accepted");
        }

        fs::path candidate = fs::weakly_canonical(root / relative);

        if (!insideRoot(candidate)) {
            throw PathSecurityError(
                "Path escapes managed root: " + relative.string()
            );
        }

        return candidate;
    }

    fs::path createDirectory(const fs::path& relative) {
        fs::path directory = safePath(relative);
        fs::create_directories(directory);
        return directory;
    }

    fs::path writeText(
        const fs::path& relative,
        const std::string& content
    ) {
        fs::path file = safePath(relative);
        fs::create_directories(file.parent_path());

        std::ofstream output(file);
        if (!output) {
            throw std::runtime_error("Cannot open file for writing: " +
                                     file.string());
        }

        output << content;
        return file;
    }

    PathInfo inspect(const fs::path& relative) const {
        fs::path file = safePath(relative);

        if (!fs::exists(file)) {
            return {relative.string(), file, PathKind::Missing};
        }

        if (fs::is_regular_file(file)) {
            return {relative.string(), file, PathKind::File};
        }

        if (fs::is_directory(file)) {
            return {relative.string(), file, PathKind::Directory};
        }

        throw std::runtime_error("Unsupported filesystem object: " +
                                 file.string());
    }

    std::vector<fs::path> listFiles(
        const fs::path& relative = "."
    ) const {
        fs::path directory = safePath(relative);

        if (!fs::is_directory(directory)) {
            throw std::runtime_error("Not a directory: " + directory.string());
        }

        std::vector<fs::path> files;

        for (const auto& entry : fs::recursive_directory_iterator(directory)) {
            if (entry.is_regular_file()) {
                files.push_back(entry.path());
            }
        }

        std::sort(files.begin(), files.end());
        return files;
    }

    std::map<std::string, std::size_t> extensionReport() const {
        std::map<std::string, std::size_t> counts;

        for (const auto& file : listFiles()) {
            std::string extension = file.extension().string();

            if (extension.empty()) {
                extension = "[no extension]";
            }

            std::transform(
                extension.begin(),
                extension.end(),
                extension.begin(),
                [](unsigned char c) {
                    return static_cast<char>(std::tolower(c));
                }
            );

            ++counts[extension];
        }

        return counts;
    }

    fs::path copyFile(
        const fs::path& source,
        const fs::path& destination
    ) {
        fs::path sourcePath = safePath(source);
        fs::path destinationPath = safePath(destination);

        if (!fs::is_regular_file(sourcePath)) {
            throw std::runtime_error(
                "Source is not a regular file: " + sourcePath.string()
            );
        }

        fs::create_directories(destinationPath.parent_path());

        if (!fs::copy_file(
                sourcePath,
                destinationPath,
                fs::copy_options::overwrite_existing)) {
            throw std::runtime_error("Copy operation failed");
        }

        return destinationPath;
    }

    fs::path relativeToRoot(const fs::path& file) const {
        return fs::relative(file, root);
    }
};

std::string kindToString(PathKind kind) {
    switch (kind) {
        case PathKind::File:
            return "file";
        case PathKind::Directory:
            return "directory";
        case PathKind::Missing:
            return "missing";
    }

    return "unknown";
}

void demonstratePathSyntax() {
    fs::path path =
        fs::path("reports") / "2026" / "november" / "report.csv";

    std::cout << "Path: " << path << '\n';
    std::cout << "Filename: " << path.filename() << '\n';
    std::cout << "Stem: " << path.stem() << '\n';
    std::cout << "Extension: " << path.extension() << '\n';
    std::cout << "Parent: " << path.parent_path() << '\n';
}

int main() {
    try {
        demonstratePathSyntax();

        fs::path root =
            fs::temp_directory_path() / "cpp_file_path_demo";

        std::error_code cleanupError;
        fs::remove_all(root, cleanupError);

        FilePathManager manager(root);

        manager.createDirectory("reports/2026/november");
        manager.createDirectory("archive");

        manager.writeText(
            "reports/2026/november/report.txt",
            "Quarterly operational report\n"
        );

        manager.writeText(
            "reports/2026/november/data.csv",
            "id,value\n1,100\n2,250\n"
        );

        manager.writeText(
            "archive/README",
            "Archived files are retained here.\n"
        );

        std::cout << "\nManaged root: " << root << '\n';

        for (const auto& name : {
                 fs::path("reports/2026/november/report.txt"),
                 fs::path("reports/2026/november"),
                 fs::path("missing.txt")
             }) {
            PathInfo info = manager.inspect(name);

            std::cout << info.original
                      << ": "
                      << kindToString(info.kind)
                      << ", normalized="
                      << info.normalized
                      << '\n';
        }

        std::cout << "\nFiles:\n";

        for (const auto& file : manager.listFiles()) {
            std::cout << "  "
                      << manager.relativeToRoot(file)
                      << '\n';
        }

        std::cout << "\nExtensions:\n";

        for (const auto& [extension, count] :
             manager.extensionReport()) {
            std::cout << "  " << extension << ": " << count << '\n';
        }

        fs::path copied = manager.copyFile(
            "reports/2026/november/report.txt",
            "archive/report.txt"
        );

        std::cout << "Copied: "
                  << manager.relativeToRoot(copied)
                  << '\n';

        try {
            manager.safePath("../../outside.txt");
        } catch (const PathSecurityError& error) {
            std::cout << "Blocked traversal: "
                      << error.what()
                      << '\n';
        }

        try {
            manager.safePath("/absolute/path.txt");
        } catch (const PathSecurityError& error) {
            std::cout << "Blocked absolute path: "
                      << error.what()
                      << '\n';
        }

        if (manager.inspect("archive/report.txt").kind != PathKind::File) {
            throw std::runtime_error("Copied file validation failed");
        }

        if (manager.inspect("missing.txt").kind != PathKind::Missing) {
            throw std::runtime_error("Missing-file validation failed");
        }

        if (manager.extensionReport().at(".csv") != 1) {
            throw std::runtime_error("Extension-count validation failed");
        }

        fs::remove_all(root, cleanupError);

        std::cout << "\nPath workflow completed successfully.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
