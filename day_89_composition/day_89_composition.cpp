#include <algorithm>
#include <cmath>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * COMPOSITION IN C++17
 *
 * Scenario: Enterprise smart-building management system.
 *
 * Demonstrates:
 * - Object composition
 * - Ownership and lifetime management
 * - Unique and shared pointers
 * - Dependency injection
 * - Component delegation
 * - Nested composition
 * - Runtime component registration
 * - Event processing
 * - Validation and failure handling
 *
 * Compile:
 * g++ -std=c++17 -Wall -Wextra -pedantic composition.cpp -o composition
 */

namespace building {

// -----------------------------------------------------
// 1. Domain types
// -----------------------------------------------------

enum class DeviceStatus {
    OFF,
    ON,
    ERROR
};

enum class Permission {
    READ,
    CONTROL,
    ADMIN
};

struct SensorReading {
    double temperature;
    double humidity;
};

struct DeviceConfiguration {
    std::string deviceId;
    std::string location;
    double temperatureThreshold;
};


// -----------------------------------------------------
// 2. Independent components
// -----------------------------------------------------

class TemperatureSensor {
private:
    double temperature_;
    double humidity_;

public:
    TemperatureSensor(double temperature, double humidity)
        : temperature_(temperature), humidity_(humidity) {

        if (!std::isfinite(temperature_) ||
            !std::isfinite(humidity_)) {
            throw std::invalid_argument(
                "Sensor readings must be finite"
            );
        }

        if (humidity_ < 0 || humidity_ > 100) {
            throw std::invalid_argument(
                "Humidity must be between 0 and 100"
            );
        }
    }

    SensorReading read() const {
        return {temperature_, humidity_};
    }

    void update(double temperature, double humidity) {
        if (!std::isfinite(temperature) ||
            !std::isfinite(humidity)) {
            throw std::invalid_argument(
                "Invalid sensor reading"
            );
        }

        if (humidity < 0 || humidity > 100) {
            throw std::invalid_argument(
                "Humidity must be between 0 and 100"
            );
        }

        temperature_ = temperature;
        humidity_ = humidity;
    }
};


class Actuator {
private:
    bool active_ = false;

public:
    void activate() {
        active_ = true;
    }

    void deactivate() {
        active_ = false;
    }

    bool active() const {
        return active_;
    }
};


class Logger {
public:
    void info(const std::string& message) const {
        std::cout << "[INFO] " << message << '\n';
    }

    void error(const std::string& message) const {
        std::cerr << "[ERROR] " << message << '\n';
    }
};


// -----------------------------------------------------
// 3. Composition using unique ownership
// -----------------------------------------------------

class HVACController {
private:
    std::unique_ptr<TemperatureSensor> sensor_;
    std::unique_ptr<Actuator> actuator_;
    double threshold_;

public:
    HVACController(
        std::unique_ptr<TemperatureSensor> sensor,
        std::unique_ptr<Actuator> actuator,
        double threshold
    )
        : sensor_(std::move(sensor)),
          actuator_(std::move(actuator)),
          threshold_(threshold) {

        if (!sensor_ || !actuator_) {
            throw std::invalid_argument(
                "HVAC requires a sensor and actuator"
            );
        }

        if (!std::isfinite(threshold_)) {
            throw std::invalid_argument(
                "Threshold must be finite"
            );
        }
    }

    void evaluate() {
        const SensorReading reading = sensor_->read();

        if (reading.temperature > threshold_) {
            actuator_->activate();
        } else {
            actuator_->deactivate();
        }
    }

    bool coolingActive() const {
        return actuator_->active();
    }

    void updateSensor(double temperature, double humidity) {
        sensor_->update(temperature, humidity);
    }
};


// -----------------------------------------------------
// 4. Composition through abstract interfaces
// -----------------------------------------------------

class INotification {
public:
    virtual ~INotification() = default;

    virtual void send(
        const std::string& recipient,
        const std::string& message
    ) = 0;
};


class ConsoleNotification : public INotification {
public:
    void send(
        const std::string& recipient,
        const std::string& message
    ) override {

        std::cout
            << "[NOTIFICATION] "
            << recipient
            << ": "
            << message
            << '\n';
    }
};


class AlertService {
private:
    std::shared_ptr<INotification> notification_;

public:
    explicit AlertService(
        std::shared_ptr<INotification> notification
    )
        : notification_(std::move(notification)) {

        if (!notification_) {
            throw std::invalid_argument(
                "Notification component is required"
            );
        }
    }

    void raiseAlert(
        const std::string& recipient,
        const std::string& message
    ) const {
        notification_->send(recipient, message);
    }
};


// -----------------------------------------------------
// 5. Device as a composed aggregate
// -----------------------------------------------------

class SmartDevice {
private:
    DeviceConfiguration configuration_;

    // Unique ownership: the device owns its controller.
    std::unique_ptr<HVACController> controller_;

    std::shared_ptr<Logger> logger_;

    DeviceStatus status_ = DeviceStatus::OFF;

public:
    SmartDevice(
        DeviceConfiguration configuration,
        std::unique_ptr<HVACController> controller,
        std::shared_ptr<Logger> logger
    )
        : configuration_(std::move(configuration)),
          controller_(std::move(controller)),
          logger_(std::move(logger)) {

        if (configuration_.deviceId.empty() ||
            configuration_.location.empty()) {
            throw std::invalid_argument(
                "Device identity and location are required"
            );
        }

        if (!controller_ || !logger_) {
            throw std::invalid_argument(
                "Device dependencies cannot be null"
            );
        }

        if (!std::isfinite(configuration_.temperatureThreshold)) {
            throw std::invalid_argument(
                "Invalid temperature threshold"
            );
        }
    }

    void activate() {
        if (status_ == DeviceStatus::ERROR) {
            throw std::runtime_error(
                "Cannot activate an error-state device"
            );
        }

        if (status_ == DeviceStatus::ON) {
            return;
        }

        status_ = DeviceStatus::ON;
        logger_->info(configuration_.deviceId + " activated");
    }

    void deactivate() {
        if (status_ == DeviceStatus::OFF) {
            return;
        }

        status_ = DeviceStatus::OFF;
        logger_->info(configuration_.deviceId + " deactivated");
    }

    void updateSensor(double temperature, double humidity) {
        if (status_ != DeviceStatus::ON) {
            throw std::runtime_error(
                "Device must be active"
            );
        }

        try {
            controller_->updateSensor(temperature, humidity);
            controller_->evaluate();
        } catch (...) {
            status_ = DeviceStatus::ERROR;
            throw;
        }
    }

    bool coolingActive() const {
        return controller_->coolingActive();
    }

    DeviceStatus status() const {
        return status_;
    }

    const std::string& id() const {
        return configuration_.deviceId;
    }
};


// -----------------------------------------------------
// 6. Building composition
// -----------------------------------------------------

class Building {
private:
    std::string name_;

    // Building owns its devices.
    std::map<std::string, std::unique_ptr<SmartDevice>> devices_;

    std::shared_ptr<Logger> logger_;

public:
    Building(
        std::string name,
        std::shared_ptr<Logger> logger
    )
        : name_(std::move(name)),
          logger_(std::move(logger)) {

        if (name_.empty() || !logger_) {
            throw std::invalid_argument(
                "Invalid building configuration"
            );
        }
    }

    void addDevice(std::unique_ptr<SmartDevice> device) {
        if (!device) {
            throw std::invalid_argument(
                "Device cannot be null"
            );
        }

        const std::string id = device->id();

        if (devices_.count(id)) {
            throw std::runtime_error(
                "Duplicate device ID: " + id
            );
        }

        devices_.emplace(id, std::move(device));
    }

    SmartDevice& getDevice(const std::string& id) {
        auto iterator = devices_.find(id);

        if (iterator == devices_.end()) {
            throw std::out_of_range(
                "Device not found: " + id
            );
        }

        return *iterator->second;
    }

    void activateAll() {
        for (auto& entry : devices_) {
            entry.second->activate();
        }
    }

    void report() const {
        std::cout << "\nBuilding: " << name_ << '\n';

        for (const auto& entry : devices_) {
            const SmartDevice& device = *entry.second;

            std::cout
                << "Device: " << entry.first
                << " | Status: "
                << (device.status() == DeviceStatus::ON
                    ? "ON" : "OFF")
                << " | Cooling: "
                << (device.coolingActive() ? "ACTIVE" : "INACTIVE")
                << '\n';
        }
    }

    std::size_t deviceCount() const {
        return devices_.size();
    }
};


// -----------------------------------------------------
// 7. Policy composition
// -----------------------------------------------------

class AccessPolicy {
private:
    std::map<std::string, std::set<Permission>> permissions_;

public:
    AccessPolicy() {
        permissions_["administrator"] = {
            Permission::READ,
            Permission::CONTROL,
            Permission::ADMIN
        };

        permissions_["operator"] = {
            Permission::READ,
            Permission::CONTROL
        };

        permissions_["observer"] = {
            Permission::READ
        };
    }

    bool allows(
        const std::string& role,
        Permission permission
    ) const {

        auto iterator = permissions_.find(role);

        if (iterator == permissions_.end()) {
            return false;
        }

        return iterator->second.count(permission) > 0;
    }
};


// -----------------------------------------------------
// 8. Factory for nested component composition
// -----------------------------------------------------

std::unique_ptr<SmartDevice> createDevice(
    const std::string& id,
    const std::string& location,
    double temperature,
    double humidity,
    double threshold,
    const std::shared_ptr<Logger>& logger
) {

    auto sensor = std::make_unique<TemperatureSensor>(
        temperature,
        humidity
    );

    auto actuator = std::make_unique<Actuator>();

    auto controller = std::make_unique<HVACController>(
        std::move(sensor),
        std::move(actuator),
        threshold
    );

    DeviceConfiguration configuration{
        id,
        location,
        threshold
    };

    return std::make_unique<SmartDevice>(
        std::move(configuration),
        std::move(controller),
        logger
    );
}


// -----------------------------------------------------
// 9. Executable tests
// -----------------------------------------------------

void runTests() {
    auto logger = std::make_shared<Logger>();

    Building building("Corporate Headquarters", logger);

    building.addDevice(
        createDevice(
            "HVAC-001",
            "First Floor",
            32.0,
            55.0,
            25.0,
            logger
        )
    );

    building.addDevice(
        createDevice(
            "HVAC-002",
            "Second Floor",
            22.0,
            45.0,
            25.0,
            logger
        )
    );

    if (building.deviceCount() != 2) {
        throw std::runtime_error(
            "Building composition test failed"
        );
    }

    building.activateAll();

    SmartDevice& first = building.getDevice("HVAC-001");

    first.updateSensor(32.0, 55.0);

    if (!first.coolingActive()) {
        throw std::runtime_error(
            "HVAC cooling evaluation failed"
        );
    }

    SmartDevice& second = building.getDevice("HVAC-002");

    second.updateSensor(22.0, 45.0);

    if (second.coolingActive()) {
        throw std::runtime_error(
            "Unexpected cooling activation"
        );
    }

    // Verify role-based authorization.
    AccessPolicy policy;

    if (!policy.allows("administrator", Permission::ADMIN)) {
        throw std::runtime_error(
            "Administrator authorization failed"
        );
    }

    if (policy.allows("observer", Permission::CONTROL)) {
        throw std::runtime_error(
            "Observer received unauthorized control access"
        );
    }

    // Verify notification composition.
    auto notification =
        std::make_shared<ConsoleNotification>();

    AlertService alerts(notification);

    alerts.raiseAlert(
        "security@example.com",
        "Temperature threshold exceeded"
    );

    // Verify missing device handling.
    try {
        building.getDevice("UNKNOWN");
        throw std::runtime_error(
            "Missing device test failed"
        );
    } catch (const std::out_of_range&) {
        logger->info("Missing device handled correctly");
    }

    // Verify constructor validation.
    try {
        TemperatureSensor invalid(25.0, 150.0);

        throw std::runtime_error(
            "Invalid sensor test failed"
        );
    } catch (const std::invalid_argument&) {
        logger->info("Invalid sensor rejected correctly");
    }

    building.report();

    logger->info("All C++17 composition tests passed");
}

} // namespace building


// -----------------------------------------------------
// 10. Main
// -----------------------------------------------------

int main() {
    try {
        building::runTests();
        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Application failure: "
            << error.what()
            << '\n';

        return 1;
    }
}
