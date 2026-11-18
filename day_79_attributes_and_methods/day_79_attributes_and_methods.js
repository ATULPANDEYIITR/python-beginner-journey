"use strict";

/**
 * ATTRIBUTES AND METHODS
 *
 * Event-driven object-oriented banking model.
 *
 * Demonstrates:
 * - Instance and static attributes
 * - Public and private class fields
 * - Instance and static methods
 * - Getters and setters
 * - Inheritance and overriding
 * - Composition
 * - Polymorphism
 * - Asynchronous methods
 * - Events and observers
 * - Validation and state transitions
 * - Immutable transaction snapshots
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");


class DomainError extends Error {
    constructor(message, code) {
        super(message);
        this.name = this.constructor.name;
        this.code = code;
    }
}

class ValidationError extends DomainError {}
class InsufficientFundsError extends DomainError {}
class AccountStateError extends DomainError {}
class DuplicateAccountError extends DomainError {}


const AccountStatus = Object.freeze({
    ACTIVE: "ACTIVE",
    FROZEN: "FROZEN",
    CLOSED: "CLOSED"
});


class AccountRegistry {
    #accounts = new Map();

    register(account) {
        if (this.#accounts.has(account.accountNumber)) {
            throw new DuplicateAccountError(
                "Account number already exists.",
                "DUPLICATE_ACCOUNT"
            );
        }

        this.#accounts.set(account.accountNumber, account);
    }

    find(accountNumber) {
        return this.#accounts.get(accountNumber) ?? null;
    }

    list() {
        return Object.freeze([...this.#accounts.values()]);
    }

    get size() {
        return this.#accounts.size;
    }
}


class BankAccount extends EventEmitter {
    static bankName = "National Digital Bank";
    static minimumBalance = 0;
    static accountCount = 0;

    #balance;
    #status = AccountStatus.ACTIVE;
    #history = [];
    #sequence = 0;

    constructor(accountNumber, owner, initialBalance = 0) {
        super();

        if (
            typeof accountNumber !== "string" ||
            accountNumber.trim().length === 0
        ) {
            throw new ValidationError(
                "Account number is required.",
                "INVALID_ACCOUNT"
            );
        }

        if (
            typeof owner !== "string" ||
            owner.trim().length === 0
        ) {
            throw new ValidationError(
                "Owner is required.",
                "INVALID_OWNER"
            );
        }

        this.accountNumber = accountNumber.trim();
        this.owner = owner.trim();

        this.#balance = BankAccount.toCents(initialBalance);

        if (this.#balance < 0) {
            throw new ValidationError(
                "Initial balance cannot be negative.",
                "NEGATIVE_BALANCE"
            );
        }

        BankAccount.accountCount++;
    }

    // Public getter exposes data without exposing private storage.
    get balance() {
        return this.#balance / 100;
    }

    get status() {
        return this.#status;
    }

    get transactionHistory() {
        return Object.freeze(
            this.#history.map(transaction =>
                Object.freeze({ ...transaction })
            )
        );
    }

    static toCents(value) {
        if (
            typeof value !== "number" ||
            !Number.isFinite(value)
        ) {
            throw new ValidationError(
                "Amount must be a finite number.",
                "INVALID_AMOUNT"
            );
        }

        const cents = Math.round(value * 100);

        if (Math.abs(value * 100 - cents) > 1e-7) {
            throw new ValidationError(
                "Amounts support two decimal places.",
                "INVALID_PRECISION"
            );
        }

        return cents;
    }

    static validateAmount(value) {
        const cents = BankAccount.toCents(value);

        if (cents <= 0) {
            throw new ValidationError(
                "Amount must be positive.",
                "NON_POSITIVE_AMOUNT"
            );
        }

        return cents;
    }

    static formatCurrency(value) {
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR"
        }).format(value);
    }

    static changeBankName(name) {
        if (typeof name !== "string" || !name.trim()) {
            throw new ValidationError(
                "Bank name cannot be empty.",
                "INVALID_BANK_NAME"
            );
        }

        BankAccount.bankName = name.trim();
    }

    static create(accountNumber, owner, initialBalance = 0) {
        return new BankAccount(
            accountNumber,
            owner,
            initialBalance
        );
    }

    #ensureActive() {
        if (this.#status !== AccountStatus.ACTIVE) {
            throw new AccountStateError(
                `Account is ${this.#status}.`,
                "ACCOUNT_UNAVAILABLE"
            );
        }
    }

    #record(type, amount) {
        const transaction = Object.freeze({
            id: ++this.#sequence,
            type,
            amount: amount / 100,
            balanceAfter: this.#balance / 100,
            timestamp: new Date().toISOString()
        });

        this.#history.push(transaction);

        // Consumers receive events after the state has changed.
        this.emit("transaction", transaction);
    }

    deposit(amount) {
        this.#ensureActive();

        const cents = BankAccount.validateAmount(amount);

        this.#balance += cents;
        this.#record("DEPOSIT", cents);

        return this.balance;
    }

    withdraw(amount) {
        this.#ensureActive();

        const cents = BankAccount.validateAmount(amount);

        if (this.#balance - cents < 0) {
            throw new InsufficientFundsError(
                "Insufficient balance.",
                "INSUFFICIENT_FUNDS"
            );
        }

        this.#balance -= cents;
        this.#record("WITHDRAWAL", cents);

        return this.balance;
    }

    freeze() {
        if (this.#status === AccountStatus.CLOSED) {
            throw new AccountStateError(
                "Closed accounts cannot be frozen.",
                "ACCOUNT_CLOSED"
            );
        }

        this.#status = AccountStatus.FROZEN;
        this.emit("statusChanged", this.#status);
    }

    unfreeze() {
        if (this.#status !== AccountStatus.FROZEN) {
            throw new AccountStateError(
                "Account is not frozen.",
                "INVALID_TRANSITION"
            );
        }

        this.#status = AccountStatus.ACTIVE;
        this.emit("statusChanged", this.#status);
    }

    close() {
        if (this.#balance !== 0) {
            throw new AccountStateError(
                "Account must have zero balance.",
                "NONZERO_BALANCE"
            );
        }

        this.#status = AccountStatus.CLOSED;
        this.emit("statusChanged", this.#status);
    }

    /**
     * Asynchronous transfer with ordered account locking.
     *
     * The lock prevents concurrent transfers from modifying
     * the same account simultaneously within this process.
     */
    static #locks = new Map();

    static async #withLocks(accounts, operation) {
        const ordered = [...new Set(accounts)]
            .sort((a, b) =>
                a.accountNumber.localeCompare(b.accountNumber)
            );

        const previous = ordered.map(account =>
            BankAccount.#locks.get(account) ?? Promise.resolve()
        );

        let release;

        const current = new Promise(resolve => {
            release = resolve;
        });

        for (const account of ordered) {
            BankAccount.#locks.set(
                account,
                current
            );
        }

        try {
            await Promise.all(previous);
            return await operation();
        } finally {
            release();

            for (const account of ordered) {
                if (BankAccount.#locks.get(account) === current) {
                    BankAccount.#locks.delete(account);
                }
            }
        }
    }

    async transferTo(destination, amount) {
        if (!(destination instanceof BankAccount)) {
            throw new ValidationError(
                "Destination must be a bank account.",
                "INVALID_DESTINATION"
            );
        }

        if (destination === this) {
            throw new ValidationError(
                "Self-transfer is prohibited.",
                "SELF_TRANSFER"
            );
        }

        const cents = BankAccount.validateAmount(amount);

        return BankAccount.#withLocks(
            [this, destination],
            async () => {
                this.#ensureActive();
                destination.#ensureActive();

                if (this.#balance < cents) {
                    throw new InsufficientFundsError(
                        "Insufficient transfer balance.",
                        "INSUFFICIENT_FUNDS"
                    );
                }

                // All checks occur before either balance changes.
                this.#balance -= cents;
                destination.#balance += cents;

                this.#record("TRANSFER_OUT", cents);
                destination.#record("TRANSFER_IN", cents);

                return Object.freeze({
                    sourceBalance: this.balance,
                    destinationBalance: destination.balance
                });
            }
        );
    }

    toJSON() {
        return {
            accountNumber: this.accountNumber,
            owner: this.owner,
            balance: this.balance,
            status: this.status
        };
    }
}


// Specialized class with method overriding.
class SavingsAccount extends BankAccount {
    constructor(accountNumber, owner, balance = 0, interestRate = 4) {
        super(accountNumber, owner, balance);

        if (
            !Number.isFinite(interestRate) ||
            interestRate < 0 ||
            interestRate > 100
        ) {
            throw new ValidationError(
                "Interest rate must be between 0 and 100.",
                "INVALID_INTEREST_RATE"
            );
        }

        this.interestRate = interestRate;
    }

    calculateInterest() {
        return Math.round(
            this.balance * this.interestRate
        ) / 100;
    }

    applyInterest() {
        const interest = this.calculateInterest();

        if (interest > 0) {
            this.deposit(interest);
        }

        return interest;
    }

    toJSON() {
        return {
            ...super.toJSON(),
            interestRate: this.interestRate,
            accountType: "SAVINGS"
        };
    }
}


// ---------------------------------------------------------
// APPLICATION EXECUTION
// ---------------------------------------------------------

async function main() {
    console.log("ATTRIBUTES AND METHODS");
    console.log("=".repeat(45));

    const registry = new AccountRegistry();

    const current = BankAccount.create(
        "ACC1001",
        "Rahul Sharma",
        50000
    );

    const savings = new SavingsAccount(
        "ACC1002",
        "Priya Verma",
        75000,
        5
    );

    registry.register(current);
    registry.register(savings);

    current.on("transaction", transaction => {
        console.log("Current account event:", transaction.type);
    });

    savings.on("statusChanged", status => {
        console.log("Savings status event:", status);
    });

    console.log("\nInstance attributes:");
    console.log(current.accountNumber);
    console.log(current.owner);
    console.log(current.balance);

    console.log("\nStatic attributes:");
    console.log(BankAccount.bankName);
    console.log(BankAccount.accountCount);

    console.log("\nInstance methods:");
    current.deposit(5000);
    current.withdraw(2000);

    console.log("Balance:", current.balance);

    console.log("\nStatic methods:");
    console.log(BankAccount.formatCurrency(current.balance));

    BankAccount.changeBankName("Enterprise Banking Group");

    console.log("\nUpdated class attribute:");
    console.log(BankAccount.bankName);

    console.log("\nInheritance and polymorphism:");
    console.log(savings.toJSON());

    const interest = savings.applyInterest();
    console.log("Interest applied:", interest);

    console.log("\nAsynchronous transfer:");
    const transfer = await current.transferTo(savings, 3000);

    console.log(transfer);

    console.log("\nRegistry:");
    console.log("Accounts:", registry.size);
    console.log("Found:", registry.find("ACC1001") !== null);

    console.log("\nValidation:");

    try {
        current.withdraw(1000000);
    } catch (error) {
        console.log(error.name, error.message);
    }

    try {
        current.deposit(-500);
    } catch (error) {
        console.log(error.name, error.message);
    }

    try {
        registry.register(current);
    } catch (error) {
        console.log(error.name, error.message);
    }

    console.log("\nEncapsulation:");

    assert.equal(current.balance, 50000);
    assert.equal(savings.balance, 81125);

    assert.equal(current.transactionHistory.length, 3);

    const history = current.transactionHistory;

    try {
        history.push({});
    } catch (error) {
        console.log("Transaction history is immutable.");
    }

    current.freeze();

    try {
        current.deposit(100);
    } catch (error) {
        console.log(error.name, error.message);
    }

    current.unfreeze();

    assert.equal(current.status, AccountStatus.ACTIVE);

    console.log("\nAll assertions passed.");
}

main().catch(error => {
    console.error("Application failure:", error);
    process.exitCode = 1;
});
