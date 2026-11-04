#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

// ---------------------------------------------------------
// Domain model
// ---------------------------------------------------------

enum class OrderStatus {
    Pending,
    Shipped,
    Delivered,
    Cancelled
};

struct Order {
    int orderId;
    string customer;
    string product;
    double quantity;
    double unitPrice;
    OrderStatus status;

    double total() const {
        return quantity * unitPrice;
    }
};

struct SalesSummary {
    int orderCount = 0;
    double revenue = 0.0;
};

// ---------------------------------------------------------
// CSV parser
// ---------------------------------------------------------

class CSVParser {
public:

    static vector<string> parseLine(const string& line) {
        vector<string> fields;

        string field;
        bool insideQuotes = false;

        for (size_t i = 0; i < line.size(); ++i) {
            char ch = line[i];

            if (ch == '"') {
                if (insideQuotes &&
                    i + 1 < line.size() &&
                    line[i + 1] == '"') {

                    field += '"';
                    ++i;
                } else {
                    insideQuotes = !insideQuotes;
                }
            }
            else if (ch == ',' && !insideQuotes) {
                fields.push_back(field);
                field.clear();
            }
            else {
                field += ch;
            }
        }

        if (insideQuotes) {
            throw runtime_error("Unclosed quoted field");
        }

        fields.push_back(field);

        return fields;
    }

    static string escapeField(const string& value) {
        string safe = value;

        if (!safe.empty() &&
            (safe[0] == '=' ||
             safe[0] == '+' ||
             safe[0] == '-' ||
             safe[0] == '@')) {

            safe.insert(safe.begin(), '\'');
        }

        if (safe.find_first_of(",\"\r\n") == string::npos) {
            return safe;
        }

        string escaped = "\"";

        for (char ch : safe) {
            if (ch == '"') {
                escaped += "\"\"";
            } else {
                escaped += ch;
            }
        }

        escaped += '"';

        return escaped;
    }

    static string serializeRow(const vector<string>& row) {
        string output;

        for (size_t i = 0; i < row.size(); ++i) {
            if (i > 0) {
                output += ',';
            }

            output += escapeField(row[i]);
        }

        return output;
    }
};

// ---------------------------------------------------------
// Conversion helpers
// ---------------------------------------------------------

int parseInteger(const string& value) {
    size_t position = 0;

    int result = stoi(value, &position);

    if (position != value.size()) {
        throw runtime_error("Invalid integer");
    }

    return result;
}

double parseDouble(const string& value) {
    size_t position = 0;

    double result = stod(value, &position);

    if (position != value.size() || !isfinite(result)) {
        throw runtime_error("Invalid numeric value");
    }

    return result;
}

OrderStatus parseStatus(const string& value) {
    if (value == "PENDING") {
        return OrderStatus::Pending;
    }

    if (value == "SHIPPED") {
        return OrderStatus::Shipped;
    }

    if (value == "DELIVERED") {
        return OrderStatus::Delivered;
    }

    if (value == "CANCELLED") {
        return OrderStatus::Cancelled;
    }

    throw runtime_error("Unknown order status");
}

string statusToString(OrderStatus status) {
    switch (status) {
        case OrderStatus::Pending:
            return "PENDING";

        case OrderStatus::Shipped:
            return "SHIPPED";

        case OrderStatus::Delivered:
            return "DELIVERED";

        case OrderStatus::Cancelled:
            return "CANCELLED";
    }

    throw runtime_error("Invalid status");
}

// ---------------------------------------------------------
// Order validation
// ---------------------------------------------------------

Order parseOrder(
    const vector<string>& fields,
    size_t lineNumber
) {
    if (fields.size() != 6) {
        throw runtime_error(
            "Line " + to_string(lineNumber) +
            ": incorrect number of columns"
        );
    }

    Order order;

    try {
        order.orderId = parseInteger(fields[0]);

        order.customer = fields[1];
        order.product = fields[2];

        order.quantity = parseDouble(fields[3]);
        order.unitPrice = parseDouble(fields[4]);

        order.status = parseStatus(fields[5]);

        if (order.orderId <= 0) {
            throw runtime_error("Order ID must be positive");
        }

        if (order.customer.empty() || order.product.empty()) {
            throw runtime_error("Customer and product are required");
        }

        if (order.quantity <= 0 || order.unitPrice < 0) {
            throw runtime_error("Invalid quantity or unit price");
        }

    } catch (const exception& error) {
        throw runtime_error(
            "Line " + to_string(lineNumber) +
            ": " + error.what()
        );
    }

    return order;
}

// ---------------------------------------------------------
// Repository for CSV operations
// ---------------------------------------------------------

class OrderRepository {
private:
    string inputFile;
    string outputFile;

public:

    OrderRepository(
        const string& input,
        const string& output
    ) : inputFile(input), outputFile(output) {}

    vector<Order> readAll() const {
        ifstream file(inputFile);

        if (!file.is_open()) {
            throw runtime_error("Cannot open input CSV");
        }

        string line;

        if (!getline(file, line)) {
            throw runtime_error("CSV file is empty");
        }

        if (!line.empty() && line[0] == '\xEF') {
            line.erase(0, 3);
        }

        vector<string> headers = CSVParser::parseLine(line);

        const vector<string> expected = {
            "order_id",
            "customer",
            "product",
            "quantity",
            "unit_price",
            "status"
        };

        if (headers != expected) {
            throw runtime_error("CSV schema mismatch");
        }

        vector<Order> orders;
        set<int> seenIds;

        size_t lineNumber = 1;

        while (getline(file, line)) {
            ++lineNumber;

            if (!line.empty() && line.back() == '\r') {
                line.pop_back();
            }

            if (line.empty()) {
                continue;
            }

            try {
                Order order = parseOrder(
                    CSVParser::parseLine(line),
                    lineNumber
                );

                if (!seenIds.insert(order.orderId).second) {
                    cerr << "Rejected duplicate order ID at line "
                         << lineNumber << '\n';

                    continue;
                }

                orders.push_back(order);

            } catch (const exception& error) {
                cerr << error.what() << '\n';
            }
        }

        if (file.bad()) {
            throw runtime_error("Input file read failure");
        }

        return orders;
    }

    void writeAll(const vector<Order>& orders) const {
        const string temporaryFile = outputFile + ".tmp";

        {
            ofstream file(temporaryFile, ios::trunc);

            if (!file.is_open()) {
                throw runtime_error("Cannot create output CSV");
            }

            file
                << "order_id,customer,product,quantity,"
                << "unit_price,status\n";

            file << fixed << setprecision(2);

            for (const Order& order : orders) {
                vector<string> row = {
                    to_string(order.orderId),
                    order.customer,
                    order.product,
                    to_string(order.quantity),
                    to_string(order.unitPrice),
                    statusToString(order.status)
                };

                file << CSVParser::serializeRow(row) << '\n';
            }

            file.flush();

            if (!file.good()) {
                throw runtime_error("Failed while writing CSV");
            }
        }

        if (std::rename(
                temporaryFile.c_str(),
                outputFile.c_str()
            ) != 0) {

            std::remove(temporaryFile.c_str());

            throw runtime_error("Atomic output replacement failed");
        }
    }
};

// ---------------------------------------------------------
// Analytics engine
// ---------------------------------------------------------

class SalesAnalytics {
public:

    static map<string, SalesSummary> summarize(
        const vector<Order>& orders
    ) {
        map<string, SalesSummary> result;

        for (const Order& order : orders) {
            if (order.status != OrderStatus::Delivered) {
                continue;
            }

            SalesSummary& summary = result[order.product];

            summary.orderCount++;
            summary.revenue += order.total();
        }

        return result;
    }

    static double totalRevenue(const vector<Order>& orders) {
        double total = 0.0;

        for (const Order& order : orders) {
            if (order.status == OrderStatus::Delivered) {
                total += order.total();
            }
        }

        return total;
    }
};

// ---------------------------------------------------------
// CSV report generation
// ---------------------------------------------------------

void writeReport(
    const map<string, SalesSummary>& summaries,
    const string& outputFile
) {
    ofstream file(outputFile + ".tmp");

    if (!file.is_open()) {
        throw runtime_error("Cannot create report");
    }

    file << "product,order_count,revenue,average_order_value\n";

    file << fixed << setprecision(2);

    for (const auto& entry : summaries) {
        const auto& product = entry.first;
        const auto& summary = entry.second;

        double average = summary.revenue / summary.orderCount;

        vector<string> row = {
            product,
            to_string(summary.orderCount),
            to_string(summary.revenue),
            to_string(average)
        };

        file << CSVParser::serializeRow(row) << '\n';
    }

    file.close();

    if (!file.good()) {
        throw runtime_error("Report writing failed");
    }

    if (rename(
            (outputFile + ".tmp").c_str(),
            outputFile.c_str()
        ) != 0) {

        remove((outputFile + ".tmp").c_str());

        throw runtime_error("Report replacement failed");
    }
}

// ---------------------------------------------------------
// Sample input generation
// ---------------------------------------------------------

void createSampleCSV(const string& filename) {
    ofstream file(filename);

    if (!file.is_open()) {
        throw runtime_error("Cannot create sample CSV");
    }

    file << "order_id,customer,product,quantity,unit_price,status\n";

    file << "2001,Alice Johnson,Laptop,2,75000,DELIVERED\n";
    file << "2002,Bob Smith,Keyboard,3,2500,DELIVERED\n";
    file << "2003,Charlie Brown,Monitor,2,18000,PENDING\n";
    file << "2004,Diana Miller,\"Wireless, Mouse\",5,1200,DELIVERED\n";
    file << "2005,Eva Wilson,Laptop,1,75000,CANCELLED\n";
    file << "2006,Invalid User,Keyboard,-2,2500,DELIVERED\n";
    file << "2001,Duplicate User,Laptop,1,75000,DELIVERED\n";

    if (!file.good()) {
        throw runtime_error("Sample CSV generation failed");
    }
}

// ---------------------------------------------------------
// Tests
// ---------------------------------------------------------

void runTests() {
    vector<string> parsed = CSVParser::parseLine(
        "1,\"Alice, Smith\",\"A \"\"quoted\"\" value\""
    );

    if (parsed.size() != 3 ||
        parsed[1] != "Alice, Smith" ||
        parsed[2] != "A \"quoted\" value") {

        throw runtime_error("CSV parser test failed");
    }

    string escaped = CSVParser::escapeField("=SUM(A1:A5)");

    if (escaped != "'=SUM(A1:A5)") {
        throw runtime_error("Formula injection test failed");
    }

    Order order = parseOrder(
        {"1", "Alice", "Laptop", "2", "1000", "DELIVERED"},
        2
    );

    if (fabs(order.total() - 2000.0) > 0.000001) {
        throw runtime_error("Order calculation test failed");
    }

    try {
        parseOrder(
            {"0", "Alice", "Laptop", "2", "1000", "DELIVERED"},
            3
        );

        throw runtime_error("Invalid ID test failed");
    } catch (const runtime_error& error) {
        if (string(error.what()) == "Invalid ID test failed") {
            throw;
        }
    }

    cout << "All C++ tests passed.\n";
}

// ---------------------------------------------------------
// Main
// ---------------------------------------------------------

int main() {
    try {
        const string input = "orders_input.csv";
        const string output = "orders_processed.csv";
        const string report = "product_report.csv";

        runTests();

        createSampleCSV(input);

        OrderRepository repository(input, output);

        vector<Order> orders = repository.readAll();

        repository.writeAll(orders);

        auto summaries = SalesAnalytics::summarize(orders);

        writeReport(summaries, report);

        cout << "\nProcessed orders: " << orders.size() << '\n';

        cout << "Delivered revenue: "
             << fixed << setprecision(2)
             << SalesAnalytics::totalRevenue(orders)
             << '\n';

        cout << "\nProduct report:\n";

        for (const auto& entry : summaries) {
            cout << entry.first
                 << " | Orders: " << entry.second.orderCount
                 << " | Revenue: " << entry.second.revenue
                 << '\n';
        }

        cout << "\nGenerated files:\n";
        cout << output << '\n';
        cout << report << '\n';

    } catch (const exception& error) {
        cerr << "Application error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
