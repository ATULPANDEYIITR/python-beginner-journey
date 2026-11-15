"use strict";

/*
 * INTRODUCTION TO CLASSES AND OBJECTS
 *
 * Demonstrates:
 * - Objects and classes
 * - Constructors and instance properties
 * - Encapsulation using private fields
 * - Inheritance and polymorphism
 * - Composition
 * - Static methods
 * - Getters
 * - Maps and Sets
 * - Events and asynchronous processing
 * - Validation and error handling
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const crypto = require("node:crypto");
const fs = require("node:fs/promises");

class DomainError extends Error {
    constructor(message) {
        super(message);
        this.name = "DomainError";
    }
}

class ValidationError extends DomainError {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class TaskNotFoundError extends DomainError {
    constructor(id) {
        super(`Task ${id} does not exist.`);
        this.name = "TaskNotFoundError";
    }
}

const TaskStatus = Object.freeze({
    TODO: "TODO",
    IN_PROGRESS: "IN_PROGRESS",
    COMPLETED: "COMPLETED",
    CANCELLED: "CANCELLED"
});

class User {
    static #nextId = 1;

    constructor(name, email) {
        if (typeof name !== "string" || !name.trim()) {
            throw new ValidationError("User name is required.");
        }

        if (
            typeof email !== "string" ||
            !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
        ) {
            throw new ValidationError("Invalid email address.");
        }

        this.id = User.#nextId++;
        this.name = name.trim();
        this.email = email.toLowerCase();
        Object.freeze(this);
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            email: this.email
        };
    }
}

class Task {
    #status;
    #history = [];

    constructor(title, owner, priority = 3) {
        if (typeof title !== "string" || !title.trim()) {
            throw new ValidationError("Task title is required.");
        }

        if (!(owner instanceof User)) {
            throw new ValidationError("Task owner must be a User.");
        }

        if (!Number.isInteger(priority) || priority < 1 || priority > 5) {
            throw new ValidationError("Priority must be between 1 and 5.");
        }

        this.id = crypto.randomUUID();
        this.title = title.trim();
        this.owner = owner;
        this.priority = priority;
        this.createdAt = new Date().toISOString();

        this.#status = TaskStatus.TODO;
        this.#history.push({
            status: this.#status,
            timestamp: this.createdAt
        });
    }

    get status() {
        return this.#status;
    }

    get history() {
        return this.#history.map(entry => ({ ...entry }));
    }

    transition(nextStatus) {
        const transitions = {
            TODO: new Set([
                TaskStatus.IN_PROGRESS,
                TaskStatus.CANCELLED
            ]),
            IN_PROGRESS: new Set([
                TaskStatus.COMPLETED,
                TaskStatus.CANCELLED,
                TaskStatus.TODO
            ]),
            COMPLETED: new Set(),
            CANCELLED: new Set()
        };

        if (!Object.values(TaskStatus).includes(nextStatus)) {
            throw new ValidationError("Unknown task status.");
        }

        if (!transitions[this.#status].has(nextStatus)) {
            throw new DomainError(
                `Cannot transition from ${this.#status} to ${nextStatus}.`
            );
        }

        this.#status = nextStatus;

        this.#history.push({
            status: nextStatus,
            timestamp: new Date().toISOString()
        });
    }

    toJSON() {
        return {
            id: this.id,
            title: this.title,
            owner: this.owner.toJSON(),
            priority: this.priority,
            status: this.status,
            createdAt: this.createdAt,
            history: this.history
        };
    }
}

class UrgentTask extends Task {
    constructor(title, owner) {
        super(title, owner, 5);
    }

    get category() {
        return "URGENT";
    }
}

class Project extends EventEmitter {
    #tasks = new Map();
    #members = new Map();

    constructor(name) {
        super();

        if (typeof name !== "string" || !name.trim()) {
            throw new ValidationError("Project name is required.");
        }

        this.name = name.trim();
        this.createdAt = new Date().toISOString();
    }

    addMember(user) {
        if (!(user instanceof User)) {
            throw new ValidationError("Expected a User object.");
        }

        if (this.#members.has(user.id)) {
            throw new DomainError("User is already a project member.");
        }

        this.#members.set(user.id, user);

        this.emit("memberAdded", {
            project: this.name,
            user: user.name
        });
    }

    addTask(task) {
        if (!(task instanceof Task)) {
            throw new ValidationError("Expected a Task object.");
        }

        if (!this.#members.has(task.owner.id)) {
            throw new DomainError(
                "Task owner must belong to the project."
            );
        }

        if (this.#tasks.has(task.id)) {
            throw new DomainError("Duplicate task.");
        }

        this.#tasks.set(task.id, task);

        this.emit("taskCreated", {
            taskId: task.id,
            title: task.title
        });
    }

    getTask(id) {
        const task = this.#tasks.get(id);

        if (!task) {
            throw new TaskNotFoundError(id);
        }

        return task;
    }

    updateTask(id, nextStatus) {
        const task = this.getTask(id);
        const previousStatus = task.status;

        task.transition(nextStatus);

        this.emit("taskUpdated", {
            taskId: id,
            previousStatus,
            currentStatus: task.status
        });
    }

    getTasksByStatus(status) {
        return [...this.#tasks.values()]
            .filter(task => task.status === status);
    }

    getSummary() {
        const tasks = [...this.#tasks.values()];

        return {
            project: this.name,
            members: this.#members.size,
            totalTasks: tasks.length,
            completed: tasks.filter(
                task => task.status === TaskStatus.COMPLETED
            ).length,
            pending: tasks.filter(
                task => task.status === TaskStatus.TODO ||
                    task.status === TaskStatus.IN_PROGRESS
            ).length
        };
    }

    toJSON() {
        return {
            name: this.name,
            createdAt: this.createdAt,
            members: [...this.#members.values()].map(
                user => user.toJSON()
            ),
            tasks: [...this.#tasks.values()].map(
                task => task.toJSON()
            ),
            summary: this.getSummary()
        };
    }
}

class ProjectService {
    #projects = new Map();

    constructor() {
        this.processing = false;
    }

    register(project) {
        if (!(project instanceof Project)) {
            throw new ValidationError("Expected a Project object.");
        }

        if (this.#projects.has(project.name)) {
            throw new DomainError("Project already registered.");
        }

        this.#projects.set(project.name, project);
    }

    async processTask(projectName, taskId, status) {
        if (this.processing) {
            throw new DomainError("Service is already processing a task.");
        }

        const project = this.#projects.get(projectName);

        if (!project) {
            throw new DomainError("Project not found.");
        }

        this.processing = true;

        try {
            // Yield execution to the event loop.
            await new Promise(resolve => setImmediate(resolve));

            project.updateTask(taskId, status);

            return project.getTask(taskId).toJSON();
        } finally {
            this.processing = false;
        }
    }

    async exportProject(projectName, filename) {
        const project = this.#projects.get(projectName);

        if (!project) {
            throw new DomainError("Project not found.");
        }

        const content = JSON.stringify(project.toJSON(), null, 2);

        // Exclusive creation prevents accidental overwriting.
        await fs.writeFile(filename, content, {
            encoding: "utf8",
            flag: "wx",
            mode: 0o600
        });

        return filename;
    }
}

async function main() {
    const project = new Project("Repository Modernization");

    project.on("memberAdded", event => {
        console.log("Member added:", event.user);
    });

    project.on("taskCreated", event => {
        console.log("Task created:", event.title);
    });

    project.on("taskUpdated", event => {
        console.log(
            "Task updated:",
            event.previousStatus,
            "->",
            event.currentStatus
        );
    });

    const developer = new User(
        "Ananya Sharma",
        "ananya@example.com"
    );

    const reviewer = new User(
        "Rahul Verma",
        "rahul@example.com"
    );

    project.addMember(developer);
    project.addMember(reviewer);

    const task = new Task(
        "Implement authentication",
        developer,
        3
    );

    const urgentTask = new UrgentTask(
        "Resolve production security issue",
        reviewer
    );

    project.addTask(task);
    project.addTask(urgentTask);

    const service = new ProjectService();
    service.register(project);

    await service.processTask(
        project.name,
        task.id,
        TaskStatus.IN_PROGRESS
    );

    await service.processTask(
        project.name,
        task.id,
        TaskStatus.COMPLETED
    );

    console.log("\nProject summary:");
    console.log(project.getSummary());

    console.log("\nUrgent task category:");
    console.log(urgentTask.category);

    console.log("\nCompleted tasks:");
    console.log(
        project.getTasksByStatus(TaskStatus.COMPLETED)
            .map(item => item.title)
    );

    // Verify invalid transitions are rejected.
    try {
        task.transition(TaskStatus.TODO);
    } catch (error) {
        console.log("Expected error:", error.message);
    }

    // Verify project membership enforcement.
    try {
        project.addTask(
            new Task(
                "Unregistered owner task",
                new User("External User", "external@example.com")
            )
        );
    } catch (error) {
        console.log("Expected error:", error.message);
    }

    // Verify missing-object handling.
    try {
        project.getTask("invalid-task-id");
    } catch (error) {
        console.log("Expected error:", error.message);
    }

    console.log("\nComplete object structure:");
    console.log(JSON.stringify(project.toJSON(), null, 2));
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
