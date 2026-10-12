#include <algorithm>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Compile with: g++ -std=c++17 -Wall -Wextra -pedantic function_parameters.cpp -o parameters
// Run with: ./parameters

namespace procurement {

struct PurchaseLine {
    std::string item;
    double unit_price;
    int quantity;
};

struct CostPolicy {
    double tax_rate;
    double maximum_discount;
    double shipping_rate;
};

struct CostBreakdown {
    double subtotal;
    double discount;
    double taxable_amount;
    double tax;
    double shipping;
    double total;
};

// const references avoid copying strings and prevent accidental mutation.
// A value parameter is appropriate for the small integer quantity.
double line_total(const PurchaseLine& line) {
    if (line.item.empty()) {
        throw std::invalid_argument("Item name cannot be empty");
    }
    if (!std::isfinite(line.unit_price) || line.unit_price < 0.0) {
        throw std::invalid_argument("Unit price must be finite and non-negative");
    }
    if (line.quantity < 0) {
        throw std::invalid_argument("Quantity cannot be negative");
    }
    return line.unit_price * static_cast<double>(line.quantity);
}

// The policy is passed by const reference because several settings belong
// together and should remain consistent throughout the calculation.
CostBreakdown calculate_purchase(
    const std::vector<PurchaseLine>& lines,
    const CostPolicy& policy,
    double discount_rate = 0.0,
    double shipping_override = -1.0
) {
    if (lines.empty()) {
        throw std::invalid_argument("A purchase requires at least one line");
    }
    if (!std::isfinite(policy.tax_rate) ||
        policy.tax_rate < 0.0 || policy.tax_rate > 1.0) {
        throw std::invalid_argument("Tax rate must be between zero and one");
    }
    if (!std::isfinite(policy.maximum_discount) ||
        policy.maximum_discount < 0.0 ||
        policy.maximum_discount > 1.0) {
        throw std::invalid_argument("Invalid maximum discount");
    }
    if (!std::isfinite(policy.shipping_rate) || policy.shipping_rate < 0.0) {
        throw std::invalid_argument("Shipping rate cannot be negative");
    }
    if (!std::isfinite(discount_rate) ||
        discount_rate < 0.0 ||
        discount_rate > policy.maximum_discount) {
        throw std::invalid_argument("Discount violates the cost policy");
    }
    if (!std::isfinite(shipping_override) && shipping_override != -1.0) {
        throw std::invalid_argument("Shipping override must be finite");
    }
    if (shipping_override < 0.0 && shipping_override != -1.0) {
        throw std::invalid_argument("Shipping override cannot be negative");
    }

    double subtotal = 0.0;
    for (const auto& line : lines) {
        subtotal += line_total(line);
        if (!std::isfinite(subtotal)) {
            throw std::overflow_error("Purchase subtotal overflowed");
        }
    }

    const double discount = subtotal * discount_rate;
    const double taxable = subtotal - discount;
    const double tax = taxable * policy.tax_rate;
    const double shipping = shipping_override >= 0.0
        ? shipping_override
        : taxable * policy.shipping_rate;
    const double total = taxable + tax + shipping;

    if (!std::isfinite(total)) {
        throw std::overflow_error("Purchase total overflowed");
    }

    return {
        subtotal,
        discount,
        taxable,
        tax,
        shipping,
        std::round(total * 100.0) / 100.0
    };
}

// This overload demonstrates a named domain type instead of a long list of
// positional parameters. It prevents callers from confusing two rates.
CostBreakdown calculate_purchase(
    const std::vector<PurchaseLine>& lines,
    const CostPolicy& policy,
    std::optional<double> discount,
    std::optional<double> shipping
) {
    return calculate_purchase(
        lines,
        policy,
        discount.value_or(0.0),
        shipping.value_or(-1.0)
    );
}

// A forwarding reference supports lvalues and rvalues without forcing a copy.
// This wrapper preserves the wrapped function's argument types.
template <typename Function, typename... Args>
auto invoke_checked(Function&& function, Args&&... args)
    -> decltype(std::invoke(
        std::forward<Function>(function),
        std::forward<Args>(args)...
    )) {
    return std::invoke(
        std::forward<Function>(function),
        std::forward<Args>(args)...
    );
}

// A callback parameter separates the selection policy from aggregation.
double sum_selected(
    const std::vector<PurchaseLine>& lines,
    const std::function<bool(const PurchaseLine&)>& include
) {
    double total = 0.0;
    for (const auto& line : lines) {
        if (include(line)) {
            total += line_total(line);
        }
    }
    return total;
}

// Reference output parameters let a caller obtain multiple results without
// allocating a separate result object, although a return struct is often
// easier to read and harder to misuse.
bool try_parse_quantity(
    const std::string& input,
    int& quantity,
    std::string& error
) {
    if (input.empty()) {
        error = "Quantity is empty";
        return false;
    }

    try {
        std::size_t parsed = 0;
        const int candidate = std::stoi(input, &parsed);
        if (parsed != input.size()) {
            error = "Quantity contains trailing characters";
            return false;
        }
        if (candidate < 0) {
            error = "Quantity cannot be negative";
            return false;
        }
        quantity = candidate;
        error.clear();
        return true;
    } catch (const std::invalid_argument&) {
        error = "Quantity is not an integer";
    } catch (const std::out_of_range&) {
        error = "Quantity exceeds the supported integer range";
    }
    return false;
}

void print_breakdown(const CostBreakdown& cost) {
    std::cout << std::fixed << std::setprecision(2)
              << "Subtotal:        " << cost.subtotal << '\n'
              << "Discount:        " << cost.discount << '\n'
              << "Taxable amount:  " << cost.taxable_amount << '\n'
              << "Tax:             " << cost.tax << '\n'
              << "Shipping:        " << cost.shipping << '\n'
              << "Final total:     " << cost.total << '\n';
}

}  // namespace procurement

int main() {
    using namespace procurement;

    try {
        std::cout << "Procurement cost engine\n"
                  << "-----------------------\n";

        const std::vector<PurchaseLine> lines{
            {"Industrial sensor", 2450.00, 4},
            {"Calibration kit", 1800.00, 2},
            {"Shielded cable", 350.00, 10}
        };

        const CostPolicy standard_policy{
            0.18,  // Tax rate
            0.15,  // Maximum authorized discount
            0.025  // Shipping rate on the discounted amount
        };

        std::cout << "\nStandard purchase:\n";
        const CostBreakdown standard = calculate_purchase(
            lines, standard_policy
        );
        print_breakdown(standard);

        std::cout << "\nNegotiated purchase:\n";
        const CostBreakdown negotiated = calculate_purchase(
            lines,
            standard_policy,
            0.10,
            450.00
        );
        print_breakdown(negotiated);

        std::cout << "\nCallback-selected total:\n";
        const double equipment_total = sum_selected(
            lines,
            [](const PurchaseLine& line) {
                return line.item != "Shielded cable";
            }
        );
        std::cout << equipment_total << '\n';

        std::cout << "\nGeneric invocation:\n";
        const double direct_total = invoke_checked(
            line_total, PurchaseLine{"Replacement valve", 900.0, 3}
        );
        std::cout << direct_total << '\n';

        std::cout << "\nInput validation:\n";
        int parsed_quantity = 0;
        std::string error;
        for (const std::string input : {"12", "-3", "4items", "999999999999"}) {
            if (try_parse_quantity(input, parsed_quantity, error)) {
                std::cout << input << " -> " << parsed_quantity << '\n';
            } else {
                std::cout << input << " rejected: " << error << '\n';
            }
        }

        std::cout << "\nFailure handling:\n";
        try {
            (void)calculate_purchase(lines, standard_policy, 0.25);
        } catch (const std::invalid_argument& exception) {
            std::cout << "Rejected discount: " << exception.what() << '\n';
        }

        try {
            const std::vector<PurchaseLine> invalid{
                {"Invalid sensor", -10.0, 2}
            };
            (void)calculate_purchase(invalid, standard_policy);
        } catch (const std::invalid_argument& exception) {
            std::cout << "Rejected line: " << exception.what() << '\n';
        }

        std::cout << "\nOptional configuration:\n";
        const CostBreakdown configured = calculate_purchase(
            lines,
            standard_policy,
            std::optional<double>{0.05},
            std::optional<double>{0.0}
        );
        print_breakdown(configured);

    } catch (const std::exception& exception) {
        std::cerr << "Purchase processing failed: "
                  << exception.what() << '\n';
        return 1;
    }

    return 0;
}
