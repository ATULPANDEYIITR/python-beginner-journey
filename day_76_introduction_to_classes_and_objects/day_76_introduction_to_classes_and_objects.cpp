#include <algorithm>
#include <iomanip>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

/*
 * INTRODUCTION TO CLASSES AND OBJECTS
 *
 * Scenario: Vehicle fleet management.
 *
 * Concepts:
 * - Classes and objects
 * - Constructors
 * - Encapsulation
 * - Inheritance
 * - Runtime polymorphism
 * - Abstract classes
 * - Composition
 * - Virtual destructors
 * - Smart pointers
 * - STL containers and algorithms
 * - Object lifetime and ownership
 */

enum class VehicleStatus {
    Available,
    InUse,
    Maintenance
};

class VehicleException : public std::runtime_error {
public:
    explicit VehicleException(const std::string& message)
        : std::runtime_error(message) {}
};

class Vehicle {
private:
    int id_;
    std::string registration_;
    std::string manufacturer_;
    double mileage_;
    VehicleStatus status_;

    static int nextId_;

protected:
    void ensureAvailable() const {
        if (status_ != VehicleStatus::Available) {
            throw VehicleException("Vehicle is not available.");
        }
    }

public:
    Vehicle(
        std::string registration,
        std::string manufacturer,
        double mileage
    )
        : id_(nextId_++),
          registration_(std::move(registration)),
          manufacturer_(std::move(manufacturer)),
          mileage_(mileage),
          status_(VehicleStatus::Available) {

        if (registration_.empty() || manufacturer_.empty()) {
            throw std::invalid_argument(
                "Registration and manufacturer are required."
            );
        }

        if (mileage_ < 0) {
            throw std::invalid_argument(
                "Mileage cannot be negative."
            );
        }
    }

    virtual ~Vehicle() = default;

    int id() const {
        return id_;
    }

    const std::string& registration() const {
        return registration_;
    }

    double mileage() const {
        return mileage_;
    }

    VehicleStatus status() const {
        return status_;
    }

    void assign() {
        ensureAvailable();
        status_ = VehicleStatus::InUse;
    }

    void release() {
        if (status_ != VehicleStatus::InUse) {
            throw VehicleException(
                "Only assigned vehicles can be released."
            );
        }

        status_ = VehicleStatus::Available;
    }

    void sendToMaintenance() {
        if (status_ == VehicleStatus::InUse) {
            throw VehicleException(
                "Cannot service an assigned vehicle."
            );
        }

        status_ = VehicleStatus::Maintenance;
    }

    void completeMaintenance() {
        if (status_ != VehicleStatus::Maintenance) {
            throw VehicleException(
                "Vehicle is not under maintenance."
            );
        }

        status_ = VehicleStatus::Available;
    }

    void updateMileage(double newMileage) {
        if (newMileage < mileage_) {
            throw std::invalid_argument(
                "Mileage cannot decrease."
            );
        }

        mileage_ = newMileage;
    }

    virtual double operatingCost() const = 0;

    virtual std::string category() const = 0;

    virtual void display() const {
        std::cout
            << "ID: " << id_
            << " | Registration: " << registration_
            << " | Manufacturer: " << manufacturer_
            << " | Mileage: " << mileage_
            << " | Category: " << category()
            << " | Status: " << statusName()
            << '\n';
    }

    std::string statusName() const {
        switch (status_) {
            case VehicleStatus::Available:
                return "Available";
            case VehicleStatus::InUse:
                return "In Use";
            case VehicleStatus::Maintenance:
                return "Maintenance";
        }

        return "Unknown";
    }
};

int Vehicle::nextId_ = 1;

class Car : public Vehicle {
private:
    int passengerCapacity_;
    double costPerKilometer_;

public:
    Car(
        std::string registration,
        std::string manufacturer,
        double mileage,
        int capacity,
        double cost
    )
        : Vehicle(
            std::move(registration),
            std::move(manufacturer),
            mileage
        ),
          passengerCapacity_(capacity),
          costPerKilometer_(cost) {

        if (capacity <= 0 || cost < 0) {
            throw std::invalid_argument(
                "Invalid car specifications."
            );
        }
    }

    double operatingCost() const override {
        return mileage() * costPerKilometer_;
    }

    std::string category() const override {
        return "Passenger Car";
    }

    void display() const override {
        Vehicle::display();

        std::cout
            << "Passenger capacity: "
            << passengerCapacity_ << '\n';
    }
};

class Truck : public Vehicle {
private:
    double loadCapacity_;
    double costPerKilometer_;

public:
    Truck(
        std::string registration,
        std::string manufacturer,
        double mileage,
        double loadCapacity,
        double cost
    )
        : Vehicle(
            std::move(registration),
            std::move(manufacturer),
            mileage
        ),
          loadCapacity_(loadCapacity),
          costPerKilometer_(cost) {

        if (loadCapacity <= 0 || cost < 0) {
            throw std::invalid_argument(
                "Invalid truck specifications."
            );
        }
    }

    double operatingCost() const override {
        return mileage() * costPerKilometer_;
    }

    std::string category() const override {
        return "Commercial Truck";
    }

    void display() const override {
        Vehicle::display();

        std::cout
            << "Load capacity: "
            << loadCapacity_ << " tonnes\n";
    }
};

/*
 * Composition:
 * Fleet owns the Vehicle objects through unique_ptr.
 * Each object is destroyed automatically when the Fleet is destroyed.
 */
class Fleet {
private:
    std::unordered_map<int, std::unique_ptr<Vehicle>> vehicles_;

public:
    void add(std::unique_ptr<Vehicle> vehicle) {
        if (!vehicle) {
            throw std::invalid_argument(
                "Cannot register a null vehicle."
            );
        }

        int id = vehicle->id();

        auto result = vehicles_.emplace(
            id,
            std::move(vehicle)
        );

        if (!result.second) {
            throw VehicleException(
                "Duplicate vehicle identifier."
            );
        }
    }

    Vehicle& get(int id) {
        auto iterator = vehicles_.find(id);

        if (iterator == vehicles_.end()) {
            throw VehicleException("Vehicle not found.");
        }

        return *iterator->second;
    }

    const Vehicle& get(int id) const {
        auto iterator = vehicles_.find(id);

        if (iterator == vehicles_.end()) {
            throw VehicleException("Vehicle not found.");
        }

        return *iterator->second;
    }

    void printReport() const {
        std::cout << "\nFLEET REPORT\n";

        for (const auto& entry : vehicles_) {
            entry.second->display();
            std::cout
                << "Operating cost: "
                << std::fixed
                << std::setprecision(2)
                << entry.second->operatingCost()
                << "\n\n";
        }
    }

    double totalOperatingCost() const {
        double total = 0;

        for (const auto& entry : vehicles_) {
            total += entry.second->operatingCost();
        }

        return total;
    }

    std::vector<int> availableVehicles() const {
        std::vector<int> result;

        for (const auto& entry : vehicles_) {
            if (
                entry.second->status() ==
                VehicleStatus::Available
            ) {
                result.push_back(entry.first);
            }
        }

        std::sort(result.begin(), result.end());

        return result;
    }

    std::size_t size() const {
        return vehicles_.size();
    }
};

int main() {
    try {
        Fleet fleet;

        auto car = std::make_unique<Car>(
            "UP32AB1234",
            "Toyota",
            15000,
            5,
            8.5
        );

        auto truck = std::make_unique<Truck>(
            "UP32CD5678",
            "Tata",
            25000,
            12.5,
            18.0
        );

        int carId = car->id();
        int truckId = truck->id();

        fleet.add(std::move(car));
        fleet.add(std::move(truck));

        // Runtime polymorphism: base-class references call
        // the correct derived-class implementations.
        std::cout << "Initial fleet:\n";
        fleet.printReport();

        // Change vehicle state.
        fleet.get(carId).assign();

        try {
            fleet.get(carId).sendToMaintenance();
        } catch (const VehicleException& error) {
            std::cout
                << "Expected state error: "
                << error.what() << '\n';
        }

        fleet.get(carId).release();
        fleet.get(carId).sendToMaintenance();

        fleet.get(carId).completeMaintenance();
        fleet.get(carId).updateMileage(16000);

        // Polymorphic cost calculation.
        std::cout << "\nUpdated operating costs:\n";

        for (int id : {carId, truckId}) {
            const Vehicle& vehicle = fleet.get(id);

            std::cout
                << vehicle.category()
                << ": "
                << vehicle.operatingCost()
                << '\n';
        }

        std::cout
            << "\nAvailable vehicles: ";

        for (int id : fleet.availableVehicles()) {
            std::cout << id << ' ';
        }

        std::cout
            << "\nTotal vehicles: "
            << fleet.size()
            << '\n';

        std::cout
            << "Fleet operating cost: "
            << fleet.totalOperatingCost()
            << '\n';

        // Invalid mileage is rejected.
        try {
            fleet.get(carId).updateMileage(100);
        } catch (const std::invalid_argument& error) {
            std::cout
                << "Expected validation error: "
                << error.what() << '\n';
        }

        // Missing object lookup.
        try {
            fleet.get(9999);
        } catch (const VehicleException& error) {
            std::cout
                << "Expected lookup error: "
                << error.what() << '\n';
        }

        std::cout << "\nProgram completed successfully.\n";

    } catch (const std::exception& error) {
        std::cerr
            << "Application failure: "
            << error.what() << '\n';

        return 1;
    }

    return 0;
}
