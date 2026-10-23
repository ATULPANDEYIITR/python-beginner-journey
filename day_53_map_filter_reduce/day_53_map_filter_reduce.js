'use strict';

/*
 * map(), filter(), and reduce() are Array transformation methods.
 * This program models an order-processing pipeline where:
 *
 * map    -> derives calculated values
 * filter -> keeps records satisfying business rules
 * reduce -> aggregates the remaining records
 *
 * The operations are deliberately separated so validation and business
 * policy remain explicit instead of being hidden inside one expression.
 */

class Order {
    constructor(id, customer, amount, status, region) {
        if (!Number.isInteger(id) || id <= 0) {
            throw new TypeError('Order id must be a positive integer');
        }

        if (typeof customer !== 'string' || customer.trim() === '') {
            throw new TypeError('Customer must be a non-empty string');
        }

        if (!Number.isFinite(amount) || amount < 0) {
            throw new TypeError('Amount must be a non-negative finite number');
        }

        const allowedStatuses = new Set(['paid', 'pending', 'cancelled']);

        if (!allowedStatuses.has(status)) {
            throw new TypeError(`Unsupported order status: ${status}`);
        }

        if (typeof region !== 'string' || region.trim() === '') {
            throw new TypeError('Region must be a non-empty string');
        }

        this.id = id;
        this.customer = customer.trim();
        this.amount = amount;
        this.status = status;
        this.region = region.trim();
        Object.freeze(this);
    }
}

const orders = [
    new Order(1001, 'Asha', 12500, 'paid', 'North'),
    new Order(1002, 'Rahul', 7300, 'pending', 'West'),
    new Order(1003, 'Meera', 18900, 'paid', 'North'),
    new Order(1004, 'Kabir', 4200, 'cancelled', 'South'),
    new Order(1005, 'Nisha', 9600, 'paid', 'West'),
];

function calculateOrderView(order) {
    // map() produces a new object rather than mutating the source order.
    return {
        id: order.id,
        customer: order.customer,
        region: order.region,
        grossAmount: order.amount,
        processingFee: Number((order.amount * 0.02).toFixed(2)),
        netAmount: Number((order.amount * 1.02).toFixed(2)),
    };
}

function isEligibleOrder(order) {
    // filter() implements the selection policy independently of mapping.
    return order.status === 'paid' && order.amount >= 5000;
}

function aggregateReport(ordersForAggregation) {
    // reduce() converts many records into one report object.
    return ordersForAggregation.reduce(
        (report, order) => {
            report.orderCount += 1;
            report.grossTotal += order.grossAmount;
            report.feeTotal += order.processingFee;
            report.netTotal += order.netAmount;

            report.regions[order.region] =
                (report.regions[order.region] || 0) + order.netAmount;

            return report;
        },
        {
            orderCount: 0,
            grossTotal: 0,
            feeTotal: 0,
            netTotal: 0,
            regions: Object.create(null),
        }
    );
}

function roundMoney(value) {
    return Number(value.toFixed(2));
}

function processOrders(sourceOrders) {
    if (!Array.isArray(sourceOrders)) {
        throw new TypeError('Expected an array of orders');
    }

    // filter first reduces the number of records that later operations
    // must process.
    const eligibleOrders = sourceOrders.filter(isEligibleOrder);

    // map transforms each eligible order into a reporting representation.
    const reportingRows = eligibleOrders.map(calculateOrderView);

    // reduce produces one aggregate result from the transformed rows.
    const report = aggregateReport(reportingRows);

    report.grossTotal = roundMoney(report.grossTotal);
    report.feeTotal = roundMoney(report.feeTotal);
    report.netTotal = roundMoney(report.netTotal);

    for (const region of Object.keys(report.regions)) {
        report.regions[region] = roundMoney(report.regions[region]);
    }

    return {
        eligibleOrders,
        reportingRows,
        report,
    };
}

function demonstratePipeline(values) {
    // The three methods can be composed when each stage has one clear role.
    const mapped = values.map(value => value * 3);
    const filtered = mapped.filter(value => value > 0);
    const reduced = filtered.reduce((total, value) => total + value, 0);

    return { values, mapped, filtered, reduced };
}

async function loadOrders() {
    // An async boundary models data arriving from an API, queue, or file.
    // No external package is required.
    return Promise.resolve(orders);
}

async function main() {
    try {
        const sourceOrders = await loadOrders();
        const result = processOrders(sourceOrders);

        console.log('Eligible orders:');
        console.table(result.reportingRows);

        console.log('Aggregate report:');
        console.log(result.report);

        console.log('Composed pipeline:');
        console.log(demonstratePipeline([-3, -1, 2, 4]));

        // reduce() should receive an initial value when an empty collection
        // is a valid input. This prevents the empty-array failure.
        const emptyTotal = [].reduce(
            (total, value) => total + value,
            0
        );

        console.log('Empty reduce result:', emptyTotal);
    } catch (error) {
        console.error(`Order processing failed: ${error.message}`);
        process.exitCode = 1;
    }
}

main();
