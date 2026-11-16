"use strict";

const { EventEmitter } = require("node:events");
const { randomUUID } = require("node:crypto");
const fs = require("node:fs/promises");

class DomainError extends Error {
    constructor(message, code = "DOMAIN_ERROR") {
        super(message);
        this.name = "DomainError";
        this.code = code;
    }
}

const AccountState = Object.freeze({
    ACTIVE: "ACTIVE",
    FROZEN: "FROZEN",
    CLOSED: "CLOSED"
});

class Account {
    static #instances = new Map();

    #id;
    #owner;
    #balance;
    #state;
    #history = [];

    constructor(owner, openingBalance = 0) {
        if (typeof owner !== "string" || owner.trim().length === 0) {
            throw new DomainError("Owner is required.", "INVALID_OWNER");
        }

        this.#validateMoney(openingBalance, true);

        this.#id = randomUUID();
        this.#owner = owner.trim();
        this.#balance = Number(openingBalance.toFixed(2));
        this.#state = AccountState.ACTIVE;

        Account.#instances.set(this.#id, this);
    }

    #validateMoney(amount, allowZero = false) {
        if (
            typeof amount !== "number" ||
            !Number.isFinite(amount) ||
            (allowZero ? amount < 0 : amount <= 0)
        ) {
            throw new DomainError(
                allowZero
                    ? "Amount must be finite and non-negative."
                    : "Amount must be finite and positive.",
                "INVALID_AMOUNT"
            );
        }
    }

    #ensureActive() {
        if (this.#state !== AccountState.ACTIVE) {
            throw new DomainError(
                `Account is ${this.#state}.`,
                "INVALID_ACCOUNT_STATE"
            );
        }
    }

    #record(type, amount) {
        this.#history.push(Object.freeze({
            sequence: this.#history.length + 1,
            type,
            amount,
            balanceAfter: this.#balance,
            timestamp: new Date().toISOString()
        }));
    }

    get id() {
        return this.#id;
    }

    get owner() {
        return this.#owner;
    }

    get balance() {
        return this.#balance;
    }

    get state() {
        return this.#state;
    }

    get history() {
        return Object.freeze([...this.#history]);
    }

    deposit(amount) {
        this.#ensureActive();
        this.#validateMoney(amount);

        this.#balance = Number((this.#balance + amount).toFixed(2));
        this.#record("DEPOSIT", amount);

        return this.#balance;
    }

    withdraw(amount) {
        this.#ensureActive();
        this.#validateMoney(amount);

        if (amount > this.availableBalance()) {
            throw new DomainError("Insufficient funds.", "INSUFFICIENT_FUNDS");
        }

        this.#balance = Number((this.#balance - amount).toFixed(2));
        this.#record("WITHDRAWAL", amount);

        return this.#balance;
    }

    availableBalance() {
        return this.#balance;
    }

    freeze() {
        this.#ensureActive();
        this.#state = AccountState.FROZEN;
    }

    unfreeze() {
        if (this.#state !== AccountState.FROZEN) {
            throw new DomainError("Account is not frozen.");
        }

        this.#state = AccountState.ACTIVE;
    }

    close() {
        if (this.#state === AccountState.CLOSED || this.#balance !== 0) {
            throw new DomainError(
                "Account must be open and have zero balance."
            );
        }

        this.#state = AccountState.CLOSED;
    }

    toJSON() {
        return {
            id: this.#id,
            owner: this.#owner,
            balance: this.#balance,
            state: this.#state,
            history: this.#history
        };
    }

    static find(id) {
        return Account.#instances.get(id) ?? null;
    }

    static get count() {
        return Account.#instances.size;
    }
}

class SavingsAccount extends Account {
    #minimumBalance;
    #interestRate;

    constructor(owner, openingBalance, minimumBalance, interestRate) {
        super(owner, openingBalance);

        if (
            !Number.isFinite(minimumBalance) ||
            minimumBalance < 0 ||
            !Number.isFinite(interestRate) ||
            interestRate < 0 ||
            interestRate > 1
        ) {
            throw new DomainError("Invalid savings account configuration.");
        }

        this.#minimumBalance = minimumBalance;
        this.#interestRate = interestRate;
    }

    availableBalance() {
        return Math.max(0, this.balance - this.#minimumBalance);
    }

    applyInterest() {
        if (this.state !== AccountState.ACTIVE) {
            throw new DomainError("Account must be active.");
        }

        const interest = Number(
            (this.balance * this.#interestRate).toFixed(2)
        );

        if (interest > 0) {
            this.deposit(interest);
        }

        return interest;
    }
}

class CurrentAccount extends Account {
    #overdraftLimit;

    constructor(owner, openingBalance, overdraftLimit) {
        super(owner, openingBalance);

        if (!Number.isFinite(overdraftLimit) || overdraftLimit < 0) {
            throw new DomainError("Invalid overdraft limit.");
        }

        this.#overdraftLimit = overdraftLimit;
    }

    availableBalance() {
        return this.balance + this.#overdraftLimit;
    }
}

class Bank extends EventEmitter {
    #accounts = new Map();

    constructor(name) {
        super();

        if (typeof name !== "string" || !name.trim()) {
            throw new DomainError("Bank name is required.");
        }

        this.name = name.trim();
    }

    addAccount(account) {
        if (!(account instanceof Account)) {
            throw new TypeError("Expected an Account instance.");
        }

        if (this.#accounts.has(account.id)) {
            throw new DomainError("Account already registered.");
        }

        this.#accounts.set(account.id, account);
        this.emit("account:created", {
            accountId: account.id,
            owner: account.owner
        });
    }

    getAccount(id) {
        const account = this.#accounts.get(id);

        if (!account) {
            throw new DomainError("Account not found.", "NOT_FOUND");
        }

        return account;
    }

    transfer(sourceId, destinationId, amount) {
        if (sourceId === destinationId) {
            throw new DomainError("Source and destination must differ.");
        }

        const source = this.getAccount(sourceId);
        const destination = this.getAccount(destinationId);

        // Validate both accounts before modifying either balance.
        if (
            source.state !== AccountState.ACTIVE ||
            destination.state !== AccountState.ACTIVE
        ) {
            throw new DomainError("Both accounts must be active.");
        }

        if (
            !Number.isFinite(amount) ||
            amount <= 0 ||
            amount > source.availableBalance()
        ) {
            throw new DomainError("Transfer amount is invalid.");
        }

        // Roll back the first operation if the second operation fails.
        const originalSourceBalance = source.balance;

        try {
            source.withdraw(amount);
            destination.deposit(amount);
        } catch (error) {
            if (source.balance !== originalSourceBalance) {
                source.deposit(originalSourceBalance - source.balance);
            }

            throw error;
        }

        this.emit("transfer:completed", {
            sourceId,
            destinationId,
            amount
        });
    }

    listAccounts() {
        return Array.from(this.#accounts.values(), account =>
            account.toJSON()
        );
    }

    async exportReport(filename) {
        if (typeof filename !== "string" || !filename.trim()) {
            throw new DomainError("Filename is required.");
        }

        await fs.writeFile(
            filename,
            JSON.stringify(this.listAccounts(), null, 2),
            { encoding: "utf8", mode: 0o600 }
        );
    }
}

async function main() {
    const bank = new Bank("Enterprise Banking System");

    bank.on("account:created", event => {
        console.log("Created:", event.accountId);
    });

    bank.on("transfer:completed", event => {
        console.log("Transfer completed:", event);
    });

    const savings = new SavingsAccount(
        "Aarav Sharma",
        25000,
        1000,
        0.05
    );

    const current = new CurrentAccount(
        "Meera Verma",
        10000,
        5000
    );

    bank.addAccount(savings);
    bank.addAccount(current);

    savings.applyInterest();
    bank.transfer(savings.id, current.id, 5000);

    console.log("\nAccount details:");

    for (const account of bank.listAccounts()) {
        console.log({
            owner: account.owner,
            balance: account.balance,
            state: account.state
        });
    }

    console.log("\nTotal accounts:", Account.count);

    try {
        savings.withdraw(100000);
    } catch (error) {
        console.log("Expected failure:", error.message);
    }

    try {
        new SavingsAccount("", 1000, 100, 0.05);
    } catch (error) {
        console.log("Constructor validation:", error.message);
    }

    console.log(
        "Registry lookup:",
        Account.find(savings.id)?.owner
    );

    await bank.exportReport("bank_report.json");

    console.log("Report exported.");
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
