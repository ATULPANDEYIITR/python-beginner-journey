/*
 * LIST INDEXING AND SLICING
 * =========================
 *
 * C++ does not provide a built-in "list slicing" operator comparable to
 * Python's sequence[start:stop:step] syntax. This case study therefore
 * implements reusable indexing, slicing, windowing, pagination, rotation,
 * filtering, and range-selection utilities over std::vector.
 *
 * The program models a realistic analytics pipeline for transaction data.
 * It begins with direct vector indexing and progressively develops a small
 * collection-processing system.
 *
 * Compile:
 *     g++ -std=c++17 -O2 -Wall -Wextra -pedantic list_indexing_slicing.cpp -o app
 *
 * Run:
 *     ./app
 */

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <numeric>
#include <optional>
#include <ranges>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using std::cout;
using std::size_t;
using std::string;
using std::vector;


// ---------------------------------------------------------------------------
// SECTION 1: OUTPUT HELPERS
// ---------------------------------------------------------------------------

template <typename T>
void printVector(const vector<T>& values, const string& label) {
    cout << label << ": [";

    for (size_t index = 0; index < values.size(); ++index) {
        if (index > 0) {
            cout << ", ";
        }

        cout << values[index];
    }

    cout << "]\n";
}

void printSection(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}


// ---------------------------------------------------------------------------
// SECTION 2: BASIC INDEXING
// ---------------------------------------------------------------------------

void demonstrateBasicIndexing() {
    printSection("1. Basic Vector Indexing");

    vector<int> numbers{10, 20, 30, 40, 50};

    printVector(numbers, "numbers");

    // std::vector uses zero-based indexing.
    cout << "numbers[0]: " << numbers[0] << "\n";
    cout << "numbers[1]: " << numbers[1] << "\n";
    cout << "numbers[4]: " << numbers[4] << "\n";

    // at() performs bounds checking and throws std::out_of_range if needed.
    cout << "numbers.at(2): " << numbers.at(2) << "\n";
}


// ---------------------------------------------------------------------------
// SECTION 3: SAFE VERSUS UNSAFE ACCESS
// ---------------------------------------------------------------------------

void demonstrateBoundsChecking() {
    printSection("2. Bounds Checking");

    vector<int> values{10, 20, 30};

    try {
        cout << "at(10): " << values.at(10) << "\n";
    } catch (const std::out_of_range& error) {
        cout << "Caught out_of_range: " << error.what() << "\n";
    }

    /*
     * values[10] is not a safe way to test bounds.
     *
     * For std::vector::operator[], an invalid index results in undefined
     * behavior. Production code should use a known-valid index or at()
     * when runtime checking is required.
     */
}


// ---------------------------------------------------------------------------
// SECTION 4: NEGATIVE INDEXING
// ---------------------------------------------------------------------------

template <typename T>
const T& atNegativeAware(const vector<T>& values, long long index) {
    if (values.empty()) {
        throw std::out_of_range("Cannot index an empty vector.");
    }

    long long normalized = index;

    if (normalized < 0) {
        normalized += static_cast<long long>(values.size());
    }

    if (normalized < 0 ||
        normalized >= static_cast<long long>(values.size())) {
        throw std::out_of_range("Index outside vector bounds.");
    }

    return values[static_cast<size_t>(normalized)];
}

void demonstrateNegativeIndexing() {
    printSection("3. Python-Like Negative Indexing Helper");

    vector<int> values{10, 20, 30, 40, 50};

    cout << "Index 0: " << atNegativeAware(values, 0) << "\n";
    cout << "Index -1: " << atNegativeAware(values, -1) << "\n";
    cout << "Index -2: " << atNegativeAware(values, -2) << "\n";

    try {
        cout << atNegativeAware(values, -100) << "\n";
    } catch (const std::out_of_range& error) {
        cout << "Invalid negative index: " << error.what() << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 5: SLICE DATA STRUCTURE
// ---------------------------------------------------------------------------

struct Slice {
    std::optional<long long> start;
    std::optional<long long> stop;
    long long step{1};
};


// ---------------------------------------------------------------------------
// SECTION 6: NORMALIZED SLICE BOUNDS
// ---------------------------------------------------------------------------

struct NormalizedSlice {
    long long start;
    long long stop;
    long long step;
};

NormalizedSlice normalizeSlice(
    size_t length,
    const Slice& slice
) {
    if (slice.step == 0) {
        throw std::invalid_argument("Slice step cannot be zero.");
    }

    const long long n = static_cast<long long>(length);
    const long long step = slice.step;

    if (step > 0) {
        long long start = slice.start.value_or(0);
        long long stop = slice.stop.value_or(n);

        if (start < 0) {
            start += n;
        }

        if (stop < 0) {
            stop += n;
        }

        start = std::clamp(start, 0LL, n);
        stop = std::clamp(stop, 0LL, n);

        return {start, stop, step};
    }

    long long start = slice.start.value_or(n - 1);
    long long stop = slice.stop.value_or(-1);

    if (start < 0) {
        start += n;
    }

    if (slice.stop.has_value() && stop < 0) {
        stop += n;
    }

    start = std::clamp(start, -1LL, n - 1);
    stop = std::clamp(stop, -1LL, n - 1);

    return {start, stop, step};
}


// ---------------------------------------------------------------------------
// SECTION 7: GENERAL SLICE IMPLEMENTATION
// ---------------------------------------------------------------------------

template <typename T>
vector<T> slice(
    const vector<T>& values,
    const Slice& specification
) {
    const NormalizedSlice normalized =
        normalizeSlice(values.size(), specification);

    vector<T> result;

    if (normalized.step > 0) {
        for (
            long long index = normalized.start;
            index < normalized.stop;
            index += normalized.step
        ) {
            result.push_back(values[static_cast<size_t>(index)]);
        }
    } else {
        for (
            long long index = normalized.start;
            index > normalized.stop;
            index += normalized.step
        ) {
            if (index >= 0 &&
                index < static_cast<long long>(values.size())) {
                result.push_back(values[static_cast<size_t>(index)]);
            }
        }
    }

    return result;
}


// ---------------------------------------------------------------------------
// SECTION 8: BASIC SLICING
// ---------------------------------------------------------------------------

void demonstrateBasicSlicing() {
    printSection("4. Basic Slicing");

    vector<int> values{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

    printVector(values, "values");

    printVector(
        slice(values, Slice{2, 6, 1}),
        "slice(2, 6)"
    );

    printVector(
        slice(values, Slice{0, 4, 1}),
        "slice(0, 4)"
    );

    printVector(
        slice(values, Slice{5, std::nullopt, 1}),
        "slice(5, end)"
    );
}


// ---------------------------------------------------------------------------
// SECTION 9: NEGATIVE SLICE BOUNDARIES
// ---------------------------------------------------------------------------

void demonstrateNegativeSlices() {
    printSection("5. Negative Slice Boundaries");

    vector<int> values{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

    printVector(
        slice(values, Slice{-5, std::nullopt, 1}),
        "last five"
    );

    printVector(
        slice(values, Slice{std::nullopt, -2, 1}),
        "all except last two"
    );

    printVector(
        slice(values, Slice{-7, -2, 1}),
        "negative-boundary region"
    );
}


// ---------------------------------------------------------------------------
// SECTION 10: STEP SLICING
// ---------------------------------------------------------------------------

void demonstrateStepSlicing() {
    printSection("6. Step-Based Slicing");

    vector<int> values{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

    printVector(
        slice(values, Slice{std::nullopt, std::nullopt, 2}),
        "every second value"
    );

    printVector(
        slice(values, Slice{1, std::nullopt, 2}),
        "every second value starting at index 1"
    );

    printVector(
        slice(values, Slice{2, 9, 3}),
        "step of three"
    );
}


// ---------------------------------------------------------------------------
// SECTION 11: REVERSE SLICING
// ---------------------------------------------------------------------------

void demonstrateReverseSlicing() {
    printSection("7. Reverse Slicing");

    vector<int> values{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

    printVector(
        slice(values, Slice{std::nullopt, std::nullopt, -1}),
        "full reverse"
    );

    printVector(
        slice(values, Slice{8, 2, -1}),
        "reverse section"
    );

    printVector(
        slice(values, Slice{9, 1, -2}),
        "reverse with step -2"
    );
}


// ---------------------------------------------------------------------------
// SECTION 12: SLICE ASSIGNMENT
// ---------------------------------------------------------------------------

template <typename T>
void replaceSlice(
    vector<T>& values,
    const Slice& specification,
    const vector<T>& replacement
) {
    const NormalizedSlice normalized =
        normalizeSlice(values.size(), specification);

    vector<size_t> positions;

    if (normalized.step > 0) {
        for (
            long long index = normalized.start;
            index < normalized.stop;
            index += normalized.step
        ) {
            positions.push_back(static_cast<size_t>(index));
        }
    } else {
        for (
            long long index = normalized.start;
            index > normalized.stop;
            index += normalized.step
        ) {
            if (index >= 0 &&
                index < static_cast<long long>(values.size())) {
                positions.push_back(static_cast<size_t>(index));
            }
        }
    }

    /*
     * Python's extended slice assignment requires equal lengths when
     * step != 1. We reproduce that important constraint here.
     */
    if (normalized.step != 1 &&
        positions.size() != replacement.size()) {
        throw std::invalid_argument(
            "Extended slice replacement must have equal lengths."
        );
    }

    if (normalized.step != 1) {
        for (size_t i = 0; i < positions.size(); ++i) {
            values[positions[i]] = replacement[i];
        }

        return;
    }

    const size_t begin = static_cast<size_t>(normalized.start);
    const size_t end = static_cast<size_t>(normalized.stop);

    values.erase(
        values.begin() + static_cast<std::ptrdiff_t>(begin),
        values.begin() + static_cast<std::ptrdiff_t>(end)
    );

    values.insert(
        values.begin() + static_cast<std::ptrdiff_t>(begin),
        replacement.begin(),
        replacement.end()
    );
}


// ---------------------------------------------------------------------------
// SECTION 13: SLICE REPLACEMENT
// ---------------------------------------------------------------------------

void demonstrateSliceReplacement() {
    printSection("8. Slice Replacement");

    vector<int> values{0, 1, 2, 3, 4, 5};

    replaceSlice(
        values,
        Slice{2, 5, 1},
        vector<int>{20, 30, 40}
    );

    printVector(values, "same-size replacement");

    replaceSlice(
        values,
        Slice{1, 3, 1},
        vector<int>{100, 200, 300, 400}
    );

    printVector(values, "longer replacement");

    replaceSlice(
        values,
        Slice{1, 5, 1},
        vector<int>{999}
    );

    printVector(values, "shorter replacement");
}


// ---------------------------------------------------------------------------
// SECTION 14: EXTENDED SLICE REPLACEMENT
// ---------------------------------------------------------------------------

void demonstrateExtendedReplacement() {
    printSection("9. Extended Slice Replacement");

    vector<int> values{0, 1, 2, 3, 4, 5, 6, 7};

    replaceSlice(
        values,
        Slice{std::nullopt, std::nullopt, 2},
        vector<int>{100, 200, 300, 400}
    );

    printVector(values, "even-position replacement");

    try {
        replaceSlice(
            values,
            Slice{std::nullopt, std::nullopt, 2},
            vector<int>{1, 2}
        );
    } catch (const std::invalid_argument& error) {
        cout << "Expected replacement error: "
             << error.what() << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 15: PAGINATION
// ---------------------------------------------------------------------------

template <typename T>
vector<T> page(
    const vector<T>& values,
    size_t pageNumber,
    size_t pageSize
) {
    if (pageNumber == 0) {
        throw std::invalid_argument("Page number must start at 1.");
    }

    if (pageSize == 0) {
        throw std::invalid_argument("Page size must be positive.");
    }

    const size_t start = (pageNumber - 1) * pageSize;

    if (start >= values.size()) {
        return {};
    }

    const size_t stop = std::min(start + pageSize, values.size());

    return vector<T>(
        values.begin() + static_cast<std::ptrdiff_t>(start),
        values.begin() + static_cast<std::ptrdiff_t>(stop)
    );
}

void demonstratePagination() {
    printSection("10. Pagination");

    vector<string> records;

    for (int number = 1; number <= 23; ++number) {
        records.push_back(
            "record-" + (number < 10 ? "0" : "") + std::to_string(number)
        );
    }

    for (size_t pageNumber = 1; pageNumber <= 5; ++pageNumber) {
        printVector(
            page(records, pageNumber, 5),
            "page " + std::to_string(pageNumber)
        );
    }
}


// ---------------------------------------------------------------------------
// SECTION 16: CHUNKING
// ---------------------------------------------------------------------------

template <typename T>
vector<vector<T>> chunk(
    const vector<T>& values,
    size_t chunkSize
) {
    if (chunkSize == 0) {
        throw std::invalid_argument("Chunk size cannot be zero.");
    }

    vector<vector<T>> result;

    for (size_t start = 0; start < values.size(); start += chunkSize) {
        const size_t stop = std::min(
            start + chunkSize,
            values.size()
        );

        result.emplace_back(
            values.begin() + static_cast<std::ptrdiff_t>(start),
            values.begin() + static_cast<std::ptrdiff_t>(stop)
        );
    }

    return result;
}

void demonstrateChunking() {
    printSection("11. Chunking");

    vector<int> values{1, 2, 3, 4, 5, 6, 7, 8, 9};

    const auto batches = chunk(values, 4);

    for (size_t index = 0; index < batches.size(); ++index) {
        printVector(
            batches[index],
            "batch " + std::to_string(index + 1)
        );
    }
}


// ---------------------------------------------------------------------------
// SECTION 17: SLIDING WINDOWS
// ---------------------------------------------------------------------------

template <typename T>
vector<vector<T>> slidingWindows(
    const vector<T>& values,
    size_t width
) {
    if (width == 0) {
        throw std::invalid_argument("Window width must be positive.");
    }

    if (width > values.size()) {
        return {};
    }

    vector<vector<T>> result;

    for (size_t start = 0;
         start + width <= values.size();
         ++start) {
        result.emplace_back(
            values.begin() + static_cast<std::ptrdiff_t>(start),
            values.begin() + static_cast<std::ptrdiff_t>(start + width)
        );
    }

    return result;
}

void demonstrateSlidingWindows() {
    printSection("12. Sliding Windows");

    vector<int> values{10, 20, 30, 40, 50};

    const auto windows = slidingWindows(values, 3);

    for (const auto& windowValues : windows) {
        printVector(windowValues, "window");
    }
}


// ---------------------------------------------------------------------------
// SECTION 18: TOP-N ANALYSIS
// ---------------------------------------------------------------------------

struct Player {
    string name;
    int score;
};

void demonstrateTopN() {
    printSection("13. Top-N Analysis");

    vector<Player> players{
        {"A", 91},
        {"B", 87},
        {"C", 99},
        {"D", 94},
        {"E", 88},
    };

    std::sort(
        players.begin(),
        players.end(),
        [](const Player& left, const Player& right) {
            return left.score > right.score;
        }
    );

    const size_t topCount = std::min<size_t>(3, players.size());

    for (size_t index = 0; index < topCount; ++index) {
        cout << players[index].name
             << " -> "
             << players[index].score
             << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 19: RECORD MODEL
// ---------------------------------------------------------------------------

struct Sale {
    string transactionId;
    double amount;
    string region;
};

std::ostream& operator<<(std::ostream& output, const Sale& sale) {
    output << "{id=" << sale.transactionId
           << ", amount=" << std::fixed << std::setprecision(2)
           << sale.amount
           << ", region=" << sale.region
           << "}";

    return output;
}


// ---------------------------------------------------------------------------
// SECTION 20: SALES CASE STUDY
// ---------------------------------------------------------------------------

class SalesRepository {
private:
    vector<Sale> sales;

public:
    explicit SalesRepository(vector<Sale> initialSales)
        : sales(std::move(initialSales)) {}

    const vector<Sale>& all() const {
        return sales;
    }

    vector<Sale> recent(size_t count) const {
        if (count >= sales.size()) {
            return sales;
        }

        return vector<Sale>(
            sales.end() - static_cast<std::ptrdiff_t>(count),
            sales.end()
        );
    }

    vector<Sale> topByAmount(size_t count) const {
        vector<Sale> sorted = sales;

        std::sort(
            sorted.begin(),
            sorted.end(),
            [](const Sale& left, const Sale& right) {
                return left.amount > right.amount;
            }
        );

        const size_t actualCount =
            std::min(count, sorted.size());

        sorted.resize(actualCount);

        return sorted;
    }

    vector<Sale> region(const string& targetRegion) const {
        vector<Sale> result;

        std::copy_if(
            sales.begin(),
            sales.end(),
            std::back_inserter(result),
            [&targetRegion](const Sale& sale) {
                return sale.region == targetRegion;
            }
        );

        return result;
    }

    double total() const {
        return std::accumulate(
            sales.begin(),
            sales.end(),
            0.0,
            [](double total, const Sale& sale) {
                return total + sale.amount;
            }
        );
    }

    double average() const {
        if (sales.empty()) {
            return 0.0;
        }

        return total() / static_cast<double>(sales.size());
    }
};


// ---------------------------------------------------------------------------
// SECTION 21: SALES CASE STUDY EXECUTION
// ---------------------------------------------------------------------------

void demonstrateSalesCaseStudy() {
    printSection("14. Industry-Style Sales Analytics Case Study");

    SalesRepository repository({
        {"S001", 1200.00, "North"},
        {"S002", 850.00, "South"},
        {"S003", 2100.00, "North"},
        {"S004", 1750.00, "West"},
        {"S005", 950.00, "East"},
        {"S006", 3200.00, "North"},
        {"S007", 1100.00, "South"},
        {"S008", 2800.00, "West"},
        {"S009", 1600.00, "East"},
        {"S010", 4000.00, "North"},
    });

    const auto recentSales = repository.recent(5);
    const auto topSales = repository.topByAmount(3);
    const auto northSales = repository.region("North");

    cout << "Recent sales:\n";

    for (const Sale& sale : recentSales) {
        cout << "  " << sale << "\n";
    }

    cout << "\nTop sales:\n";

    for (const Sale& sale : topSales) {
        cout << "  " << sale << "\n";
    }

    cout << "\nNorth-region sales:\n";

    for (const Sale& sale : northSales) {
        cout << "  " << sale << "\n";
    }

    cout << "\nTotal sales: "
         << repository.total()
         << "\n";

    cout << "Average sale: "
         << repository.average()
         << "\n";
}


// ---------------------------------------------------------------------------
// SECTION 22: POSITIONAL SAMPLING
// ---------------------------------------------------------------------------

template <typename T>
vector<T> everyNth(
    const vector<T>& values,
    size_t step
) {
    if (step == 0) {
        throw std::invalid_argument("Step must be positive.");
    }

    vector<T> result;

    for (size_t index = 0;
         index < values.size();
         index += step) {
        result.push_back(values[index]);
    }

    return result;
}

void demonstrateSampling() {
    printSection("15. Stride-Based Sampling");

    vector<int> values;

    for (int number = 0; number < 20; ++number) {
        values.push_back(number);
    }

    printVector(
        everyNth(values, 2),
        "every second"
    );

    printVector(
        everyNth(values, 3),
        "every third"
    );
}


// ---------------------------------------------------------------------------
// SECTION 23: PARTITIONING
// ---------------------------------------------------------------------------

template <typename T>
std::pair<vector<T>, vector<T>> partitionAt(
    const vector<T>& values,
    size_t position
) {
    position = std::min(position, values.size());

    vector<T> left(
        values.begin(),
        values.begin() + static_cast<std::ptrdiff_t>(position)
    );

    vector<T> right(
        values.begin() + static_cast<std::ptrdiff_t>(position),
        values.end()
    );

    return {std::move(left), std::move(right)};
}

void demonstratePartitioning() {
    printSection("16. Partitioning");

    vector<int> values{0, 1, 2, 3, 4, 5};

    auto [left, right] = partitionAt(values, 3);

    printVector(left, "left");
    printVector(right, "right");
}


// ---------------------------------------------------------------------------
// SECTION 24: ROTATION
// ---------------------------------------------------------------------------

template <typename T>
vector<T> rotateLeft(
    const vector<T>& values,
    size_t positions
) {
    if (values.empty()) {
        return {};
    }

    positions %= values.size();

    vector<T> result;

    result.insert(
        result.end(),
        values.begin() + static_cast<std::ptrdiff_t>(positions),
        values.end()
    );

    result.insert(
        result.end(),
        values.begin(),
        values.begin() + static_cast<std::ptrdiff_t>(positions)
    );

    return result;
}

template <typename T>
vector<T> rotateRight(
    const vector<T>& values,
    size_t positions
) {
    if (values.empty()) {
        return {};
    }

    positions %= values.size();

    if (positions == 0) {
        return values;
    }

    const size_t split = values.size() - positions;

    vector<T> result;

    result.insert(
        result.end(),
        values.begin() + static_cast<std::ptrdiff_t>(split),
        values.end()
    );

    result.insert(
        result.end(),
        values.begin(),
        values.begin() + static_cast<std::ptrdiff_t>(split)
    );

    return result;
}

void demonstrateRotation() {
    printSection("17. Rotation");

    vector<int> values{1, 2, 3, 4, 5};

    printVector(
        rotateLeft(values, 2),
        "left rotation"
    );

    printVector(
        rotateRight(values, 2),
        "right rotation"
    );

    printVector(
        rotateLeft(values, 7),
        "left rotation by 7"
    );
}


// ---------------------------------------------------------------------------
// SECTION 25: STRING INDEXING
// ---------------------------------------------------------------------------

void demonstrateStringIndexing() {
    printSection("18. std::string Indexing and Substrings");

    string text = "PYTHON";

    cout << "First character: " << text[0] << "\n";
    cout << "Last character: " << text.at(text.size() - 1) << "\n";

    // std::string::substr(position, count) differs from Python slicing:
    // the second argument is a count rather than an ending position.
    cout << "Middle: " << text.substr(1, 4) << "\n";

    string reversed(text.rbegin(), text.rend());
    cout << "Reverse: " << reversed << "\n";
}


// ---------------------------------------------------------------------------
// SECTION 26: VECTOR ITERATORS
// ---------------------------------------------------------------------------

void demonstrateIterators() {
    printSection("19. Iterators as a General Sequence Mechanism");

    vector<int> values{10, 20, 30, 40, 50};

    auto begin = values.begin() + 1;
    auto end = values.begin() + 4;

    vector<int> selected(begin, end);

    printVector(selected, "iterator-selected region");

    /*
     * Random-access iterators allow arithmetic such as:
     *
     * iterator + n
     * iterator - n
     * iterator difference
     *
     * std::vector provides random-access iterators.
     */
}


// ---------------------------------------------------------------------------
// SECTION 27: C++20 RANGES NOTE
// ---------------------------------------------------------------------------

void demonstrateRanges() {
    printSection("20. C++ Standard Library Range Concepts");

    vector<int> values{1, 2, 3, 4, 5, 6};

    /*
     * This program is compiled as C++17 for broad compatibility, so the
     * implementation deliberately relies on C++17 facilities.
     *
     * C++20 introduces std::ranges and std::span, which provide more
     * expressive ways to describe views and ranges without necessarily
     * copying the underlying data.
     */

    printVector(values, "C++17 vector");
}


// ---------------------------------------------------------------------------
// SECTION 28: NON-OWNING VIEW WITH std::span-LIKE DESIGN
// ---------------------------------------------------------------------------

class VectorWindow {
private:
    const vector<int>& values;
    size_t start;
    size_t count;

public:
    VectorWindow(
        const vector<int>& source,
        size_t windowStart,
        size_t windowCount
    )
        : values(source),
          start(std::min(windowStart, source.size())),
          count(std::min(
              windowCount,
              source.size() - std::min(windowStart, source.size())
          )) {}

    size_t size() const {
        return count;
    }

    int at(size_t index) const {
        if (index >= count) {
            throw std::out_of_range("Window index out of range.");
        }

        return values[start + index];
    }

    void print(const string& label) const {
        cout << label << ": [";

        for (size_t index = 0; index < count; ++index) {
            if (index > 0) {
                cout << ", ";
            }

            cout << values[start + index];
        }

        cout << "]\n";
    }
};

void demonstrateNonOwningWindow() {
    printSection("21. Non-Owning Window");

    vector<int> values{10, 20, 30, 40, 50};

    VectorWindow window(values, 1, 3);

    window.print("window");

    cout << "window[0]: "
         << window.at(0)
         << "\n";

    /*
     * The VectorWindow stores a reference to the original vector rather
     * than allocating a second vector for the selected region.
     *
     * The referenced vector must remain alive while the view is used.
     */
}


// ---------------------------------------------------------------------------
// SECTION 29: PERFORMANCE COMPARISON
// ---------------------------------------------------------------------------

void demonstratePerformancePrinciples() {
    printSection("22. Performance Characteristics");

    vector<int> values(100'000);

    std::iota(values.begin(), values.end(), 0);

    volatile long long checksum = 0;

    for (size_t index = 0; index < 10'000; ++index) {
        checksum += values[index];
    }

    cout << "Indexed-read checksum: "
         << checksum
         << "\n";

    /*
     * Typical complexity:
     *
     * vector[index]      -> O(1)
     * vector.at(index)   -> O(1)
     * copying k elements -> O(k)
     * insertion in middle-> O(n)
     * deletion in middle -> O(n)
     * sorting            -> O(n log n) average/common implementation model
     *
     * A copied slice owns its elements. A non-owning view can avoid that
     * allocation when the lifetime and mutability requirements permit it.
     */
}


// ---------------------------------------------------------------------------
// SECTION 30: MEMORY AND OWNERSHIP
// ---------------------------------------------------------------------------

void demonstrateOwnership() {
    printSection("23. Copying and Ownership");

    vector<int> original{1, 2, 3, 4, 5};

    vector<int> copy = original;

    copy[0] = 999;

    printVector(original, "original");
    printVector(copy, "copy");

    /*
     * std::vector copy construction produces independent storage.
     *
     * This differs from a raw pointer or reference, which does not itself
     * create an independent collection.
     */
}


// ---------------------------------------------------------------------------
// SECTION 31: MOVE SEMANTICS
// ---------------------------------------------------------------------------

vector<int> createLargeVector() {
    vector<int> values;

    for (int number = 0; number < 10'000; ++number) {
        values.push_back(number);
    }

    return values;
}

void demonstrateMoveSemantics() {
    printSection("24. Move Semantics");

    vector<int> data = createLargeVector();

    cout << "Created vector size: "
         << data.size()
         << "\n";

    vector<int> moved = std::move(data);

    cout << "Moved vector size: "
         << moved.size()
         << "\n";

    /*
     * A moved-from vector remains valid but its exact state is
     * implementation-dependent. Code should not rely on it containing
     * the old elements.
     */
}


// ---------------------------------------------------------------------------
// SECTION 32: DATA VALIDATION
// ---------------------------------------------------------------------------

bool isValidWindow(
    size_t length,
    size_t start,
    size_t count
) {
    if (start > length) {
        return false;
    }

    return count <= length - start;
}

void demonstrateValidation() {
    printSection("25. Window Validation");

    cout << std::boolalpha;

    cout << "valid (10, 2, 5): "
         << isValidWindow(10, 2, 5)
         << "\n";

    cout << "invalid (10, 8, 5): "
         << isValidWindow(10, 8, 5)
         << "\n";
}


// ---------------------------------------------------------------------------
// SECTION 33: FIXED-WIDTH RECORD PROCESSING
// ---------------------------------------------------------------------------

struct FixedWidthRecord {
    string country;
    string year;
    string status;
};

FixedWidthRecord parseFixedWidth(const string& raw) {
    if (raw.size() < 18) {
        throw std::invalid_argument(
            "Fixed-width record is too short."
        );
    }

    return {
        raw.substr(0, 10),
        raw.substr(10, 8),
        raw.substr(18)
    };
}

void demonstrateFixedWidthProcessing() {
    printSection("26. Fixed-Width Record Processing");

    const string raw = "INDIA     2026   ACTIVE  ";

    const FixedWidthRecord record = parseFixedWidth(raw);

    cout << "Country: " << record.country << "\n";
    cout << "Year: " << record.year << "\n";
    cout << "Status: " << record.status << "\n";
}


// ---------------------------------------------------------------------------
// SECTION 34: EDGE CASES
// ---------------------------------------------------------------------------

void demonstrateEdgeCases() {
    printSection("27. Edge Cases");

    vector<int> values{1, 2, 3};

    printVector(
        slice(values, Slice{100, 200, 1}),
        "outside forward range"
    );

    printVector(
        slice(values, Slice{-100, std::nullopt, 1}),
        "very negative start"
    );

    printVector(
        slice(values, Slice{2, 1, 1}),
        "empty forward slice"
    );

    printVector(
        slice(values, Slice{0, 2, -1}),
        "empty reverse slice"
    );

    try {
        slice(values, Slice{0, 3, 0});
    } catch (const std::invalid_argument& error) {
        cout << "Zero-step error: "
             << error.what()
             << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 35: EMPTY VECTORS
// ---------------------------------------------------------------------------

void demonstrateEmptyVectors() {
    printSection("28. Empty Vector Behavior");

    vector<int> empty;

    printVector(
        slice(empty, Slice{std::nullopt, std::nullopt, 1}),
        "full empty slice"
    );

    try {
        empty.at(0);
    } catch (const std::out_of_range& error) {
        cout << "Empty vector access error: "
             << error.what()
             << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 36: TRANSACTION FILTERING
// ---------------------------------------------------------------------------

vector<Sale> filterAmountAtLeast(
    const vector<Sale>& sales,
    double minimumAmount
) {
    vector<Sale> result;

    std::copy_if(
        sales.begin(),
        sales.end(),
        std::back_inserter(result),
        [minimumAmount](const Sale& sale) {
            return sale.amount >= minimumAmount;
        }
    );

    return result;
}

void demonstrateTransactionFiltering() {
    printSection("29. Transaction Filtering");

    const vector<Sale> sales{
        {"S001", 1200.00, "North"},
        {"S002", 850.00, "South"},
        {"S003", 2100.00, "North"},
        {"S004", 1750.00, "West"},
        {"S005", 950.00, "East"},
    };

    const auto highValue =
        filterAmountAtLeast(sales, 1500.00);

    for (const Sale& sale : highValue) {
        cout << sale << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 37: RECENT DATA ANALYSIS
// ---------------------------------------------------------------------------

double averageAmounts(const vector<Sale>& sales) {
    if (sales.empty()) {
        return 0.0;
    }

    const double total = std::accumulate(
        sales.begin(),
        sales.end(),
        0.0,
        [](double total, const Sale& sale) {
            return total + sale.amount;
        }
    );

    return total / static_cast<double>(sales.size());
}

void demonstrateRecentAnalysis() {
    printSection("30. Recent Transaction Window");

    const vector<Sale> sales{
        {"S001", 1200.00, "North"},
        {"S002", 850.00, "South"},
        {"S003", 2100.00, "North"},
        {"S004", 1750.00, "West"},
        {"S005", 950.00, "East"},
        {"S006", 3200.00, "North"},
        {"S007", 1100.00, "South"},
        {"S008", 2800.00, "West"},
    };

    const auto recent = vector<Sale>(
        sales.end() - 5,
        sales.end()
    );

    for (const auto& sale : recent) {
        cout << sale << "\n";
    }

    cout << "Recent average: "
         << averageAmounts(recent)
         << "\n";
}


// ---------------------------------------------------------------------------
// SECTION 38: TESTING THE SLICE IMPLEMENTATION
// ---------------------------------------------------------------------------

void runSliceTests() {
    printSection("31. Automated Slice Tests");

    const vector<int> values{0, 1, 2, 3, 4};

    assert(
        slice(values, Slice{2, 5, 1})
        == vector<int>{2, 3, 4}
    );

    assert(
        slice(values, Slice{std::nullopt, std::nullopt, -1})
        == vector<int>{4, 3, 2, 1, 0}
    );

    assert(
        slice(values, Slice{std::nullopt, std::nullopt, 2})
        == vector<int>{0, 2, 4}
    );

    assert(
        slice(values, Slice{-2, std::nullopt, 1})
        == vector<int>{3, 4}
    );

    assert(
        slice(values, Slice{1, 4, 2})
        == vector<int>{1, 3}
    );

    cout << "All slice tests passed.\n";
}


// ---------------------------------------------------------------------------
// SECTION 39: TESTING PAGINATION
// ---------------------------------------------------------------------------

void runPaginationTests() {
    printSection("32. Pagination Tests");

    const vector<int> values{1, 2, 3, 4, 5, 6, 7};

    assert(
        page(values, 1, 3)
        == vector<int>{1, 2, 3}
    );

    assert(
        page(values, 2, 3)
        == vector<int>{4, 5, 6}
    );

    assert(
        page(values, 3, 3)
        == vector<int>{7}
    );

    assert(
        page(values, 4, 3).empty()
    );

    cout << "All pagination tests passed.\n";
}


// ---------------------------------------------------------------------------
// SECTION 40: TESTING CHUNKING
// ---------------------------------------------------------------------------

void runChunkTests() {
    printSection("33. Chunking Tests");

    const vector<int> values{1, 2, 3, 4, 5};

    const auto result = chunk(values, 2);

    assert(result.size() == 3);
    assert(result[0] == vector<int>{1, 2});
    assert(result[1] == vector<int>{3, 4});
    assert(result[2] == vector<int>{5});

    cout << "All chunking tests passed.\n";
}


// ---------------------------------------------------------------------------
// SECTION 41: ARCHITECTURAL CASE STUDY PIPELINE
// ---------------------------------------------------------------------------

class AnalyticsPipeline {
private:
    vector<Sale> source;

public:
    explicit AnalyticsPipeline(vector<Sale> records)
        : source(std::move(records)) {}

    vector<Sale> latest(size_t count) const {
        return vector<Sale>(
            source.end() -
                static_cast<std::ptrdiff_t>(
                    std::min(count, source.size())
                ),
            source.end()
        );
    }

    vector<Sale> sampled(size_t step) const {
        return everyNth(source, step);
    }

    vector<Sale> highest(size_t count) const {
        vector<Sale> result = source;

        std::sort(
            result.begin(),
            result.end(),
            [](const Sale& left, const Sale& right) {
                return left.amount > right.amount;
            }
        );

        if (count < result.size()) {
            result.resize(count);
        }

        return result;
    }

    vector<vector<Sale>> batches(size_t size) const {
        return chunk(source, size);
    }
};


// ---------------------------------------------------------------------------
// SECTION 42: PIPELINE EXECUTION
// ---------------------------------------------------------------------------

void demonstratePipeline() {
    printSection("34. Complete Analytics Pipeline");

    AnalyticsPipeline pipeline({
        {"S001", 1200.00, "North"},
        {"S002", 850.00, "South"},
        {"S003", 2100.00, "North"},
        {"S004", 1750.00, "West"},
        {"S005", 950.00, "East"},
        {"S006", 3200.00, "North"},
        {"S007", 1100.00, "South"},
        {"S008", 2800.00, "West"},
        {"S009", 1600.00, "East"},
        {"S010", 4000.00, "North"},
    });

    cout << "Latest records:\n";

    for (const auto& sale : pipeline.latest(4)) {
        cout << "  " << sale << "\n";
    }

    cout << "\nSampled records:\n";

    for (const auto& sale : pipeline.sampled(2)) {
        cout << "  " << sale << "\n";
    }

    cout << "\nHighest-value records:\n";

    for (const auto& sale : pipeline.highest(3)) {
        cout << "  " << sale << "\n";
    }

    cout << "\nBatches:\n";

    const auto batches = pipeline.batches(3);

    for (size_t batchNumber = 0;
         batchNumber < batches.size();
         ++batchNumber) {
        cout << "Batch " << batchNumber + 1 << ":\n";

        for (const auto& sale : batches[batchNumber]) {
            cout << "  " << sale << "\n";
        }
    }
}


// ---------------------------------------------------------------------------
// SECTION 43: FAILURE CONDITIONS
// ---------------------------------------------------------------------------

void demonstrateFailureConditions() {
    printSection("35. Failure Conditions");

    try {
        vector<int> values{1, 2, 3};
        slice(values, Slice{0, 3, 0});
    } catch (const std::exception& error) {
        cout << "Slice failure: "
             << error.what()
             << "\n";
    }

    try {
        page(vector<int>{1, 2, 3}, 0, 2);
    } catch (const std::exception& error) {
        cout << "Pagination failure: "
             << error.what()
             << "\n";
    }

    try {
        chunk(vector<int>{1, 2, 3}, 0);
    } catch (const std::exception& error) {
        cout << "Chunk failure: "
             << error.what()
             << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 44: DESIGN TRADE-OFFS
// ---------------------------------------------------------------------------

void demonstrateDesignTradeoffs() {
    printSection("36. Design Trade-Offs");

    /*
     * Option 1: Copy selected data into a new vector.
     *
     * Advantages:
     * - Independent ownership.
     * - Safe after the original vector changes or is destroyed.
     * - Simple semantics.
     *
     * Costs:
     * - O(k) time.
     * - O(k) additional memory.
     *
     * Option 2: Keep iterator pairs or a view object.
     *
     * Advantages:
     * - Avoids copying.
     * - Efficient for read-only analysis.
     *
     * Costs:
     * - The source object must remain alive.
     * - Mutations to the source can affect the view.
     * - Lifetime management becomes important.
     *
     * Option 3: std::span in C++20.
     *
     * This is a standard non-owning contiguous-memory view and is often
     * appropriate when an API should accept a portion of an existing array
     * or vector without copying.
     */

    vector<int> data{1, 2, 3, 4, 5};

    VectorWindow view(data, 1, 3);

    view.print("non-owning view");
}


// ---------------------------------------------------------------------------
// SECTION 45: SECURITY CONSIDERATIONS
// ---------------------------------------------------------------------------

void demonstrateSecurityConsiderations() {
    printSection("37. Security and Reliability Considerations");

    /*
     * Index and slice calculations often use values supplied by users,
     * network requests, files, or other external systems.
     *
     * Important rules:
     *
     * 1. Validate signed values before converting them to size_t.
     * 2. Avoid integer overflow when calculating start + length.
     * 3. Use checked access when failure must be handled explicitly.
     * 4. Do not use operator[] with untrusted indexes unless validity has
     *    already been established.
     * 5. Avoid allocating huge copied slices based directly on untrusted
     *    limits.
     * 6. Keep non-owning views alive only while their source remains valid.
     */

    const size_t dataSize = 100;
    const size_t offset = 90;
    const size_t requested = 50;

    const bool valid =
        offset <= dataSize &&
        requested <= dataSize - offset;

    cout << "Validated external window: "
         << std::boolalpha
         << valid
         << "\n";
}


// ---------------------------------------------------------------------------
// SECTION 46: COMPLEXITY TABLE AS PROGRAM OUTPUT
// ---------------------------------------------------------------------------

void demonstrateComplexity() {
    printSection("38. Complexity Model");

    cout << "vector[index]             -> O(1)\n";
    cout << "vector.at(index)          -> O(1)\n";
    cout << "copy k selected elements  -> O(k)\n";
    cout << "middle insertion          -> O(n)\n";
    cout << "middle deletion           -> O(n)\n";
    cout << "std::sort                 -> O(n log n) typical\n";
    cout << "filtering an n-element vector -> O(n)\n";
}


// ---------------------------------------------------------------------------
// SECTION 47: FINAL INTEGRATED REPORT
// ---------------------------------------------------------------------------

void printFinalReport() {
    printSection("39. Final Technical Principles");

    const vector<string> principles{
        "C++ std::vector uses zero-based indexing.",
        "operator[] provides unchecked indexed access.",
        "at() provides bounds-checked access.",
        "C++ has no built-in Python-style slicing syntax.",
        "Iterator ranges can represent selected portions of vectors.",
        "A copied slice owns independent elements.",
        "A view can avoid copying but introduces lifetime requirements.",
        "Negative indexing must be implemented explicitly in C++.",
        "A slice can be modeled with start, stop, and step.",
        "A zero slice step is invalid.",
        "Forward slices normally use an exclusive stop boundary.",
        "Reverse traversal requires a negative step or reverse iterators.",
        "Slice assignment can be modeled with erase and insert.",
        "Extended replacement requires matching selected-element counts.",
        "Pagination is naturally expressed through iterator ranges.",
        "Chunking is repeated contiguous slicing.",
        "Sliding windows create overlapping contiguous regions.",
        "Filtering selects by value or predicate rather than position alone.",
        "std::vector copies require additional memory proportional to data size.",
        "Non-owning views can improve performance when lifetimes are controlled.",
        "External indexes must be validated before use.",
        "Overflow-safe size calculations are important for robust systems.",
    };

    for (size_t index = 0; index < principles.size(); ++index) {
        cout << std::setw(2)
             << index + 1
             << ". "
             << principles[index]
             << "\n";
    }
}


// ---------------------------------------------------------------------------
// MAIN
// ---------------------------------------------------------------------------

int main() {
    try {
        demonstrateBasicIndexing();
        demonstrateBoundsChecking();
        demonstrateNegativeIndexing();
        demonstrateBasicSlicing();
        demonstrateNegativeSlices();
        demonstrateStepSlicing();
        demonstrateReverseSlicing();
        demonstrateSliceReplacement();
        demonstrateExtendedReplacement();
        demonstratePagination();
        demonstrateChunking();
        demonstrateSlidingWindows();
        demonstrateTopN();
        demonstrateSalesCaseStudy();
        demonstrateSampling();
        demonstratePartitioning();
        demonstrateRotation();
        demonstrateStringIndexing();
        demonstrateIterators();
        demonstrateRanges();
        demonstrateNonOwningWindow();
        demonstratePerformancePrinciples();
        demonstrateOwnership();
        demonstrateMoveSemantics();
        demonstrateValidation();
        demonstrateFixedWidthProcessing();
        demonstrateEdgeCases();
        demonstrateEmptyVectors();
        demonstrateTransactionFiltering();
        demonstrateRecentAnalysis();
        runSliceTests();
        runPaginationTests();
        runChunkTests();
        demonstratePipeline();
        demonstrateFailureConditions();
        demonstrateDesignTradeoffs();
        demonstrateSecurityConsiderations();
        demonstrateComplexity();
        printFinalReport();

        cout << "\nProgram completed successfully.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: "
                  << error.what()
                  << "\n";

        return 1;
    }
}
