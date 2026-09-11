from typing import Any, Dict, List, Optional

from ..core.config import TOLERANCE


def _value(fields, key):
    item = fields.get(key, {})

    if isinstance(item, dict):
        value = item.get("value")

        if isinstance(value, (int, float)):
            return float(value)

    return None


def _check(
    name,
    formula,
    operands,
    calculated,
    reported,
    period=None
):
    if calculated is None or reported is None:
        return {
            "name": name,
            "formula": formula,
            "operands": operands,
            "calculated_value": calculated,
            "reported_value": reported,
            "variance": None,
            "status": "NOT_APPLICABLE",
            "period": period
        }

    variance = round(calculated - reported, 6)

    status = (
        "PASS"
        if abs(variance) <= TOLERANCE
        else "FAIL"
    )

    return {
        "name": name,
        "formula": formula,
        "operands": operands,
        "calculated_value": round(calculated, 6),
        "reported_value": round(reported, 6),
        "variance": variance,
        "status": status,
        "period": period
    }


def _result(checks):
    failed = [
        check["name"]
        for check in checks
        if check["status"] == "FAIL"
    ]

    passed = [
        check["name"]
        for check in checks
        if check["status"] == "PASS"
    ]

    warnings = [
        check["name"]
        for check in checks
        if check["status"] == "WARNING"
    ]

    if failed:
        overall_status = "FAIL"
    elif passed:
        overall_status = "PASS"
    else:
        overall_status = "NOT_APPLICABLE"

    return {
        "checks": checks,
        "overall_status": overall_status,
        "issues": [
            f"Validation failed: {name}"
            for name in failed
        ],
        "warnings": [
            f"Validation warning: {name}"
            for name in warnings
        ]
    }


def validate_invoice(fields, line_items):
    checks = []

    subtotal = _value(fields, "subtotal")
    tax = _value(fields, "tax_amount")
    discount = _value(fields, "discount")
    shipping = _value(fields, "shipping")
    total = _value(fields, "total_amount")
    cash_paid = _value(fields, "cash_paid")
    change = _value(fields, "change")

    if shipping is None:
        shipping = 0.0

    if (
        subtotal is not None
        and tax is not None
        and total is not None
    ):
        discount_value = discount if discount is not None else 0.0

        calculated_total = (
            subtotal
            + tax
            + shipping
            - discount_value
        )

        total_check = _check(
            "invoice_total_check",
            "subtotal + tax_amount + shipping - discount ≈ total_amount",
            {
                "subtotal": subtotal,
                "tax_amount": tax,
                "shipping": shipping,
                "discount": discount_value
            },
            calculated_total,
            total
        )

        if total_check["status"] == "FAIL":
            inclusive_tax_total = (
                subtotal
                + shipping
                - discount_value
            )

            inclusive_check = _check(
                "invoice_inclusive_tax_check",
                "subtotal + shipping - discount ≈ total_amount",
                {
                    "subtotal": subtotal,
                    "shipping": shipping,
                    "discount": discount_value
                },
                inclusive_tax_total,
                total
            )

            if inclusive_check["status"] == "PASS":
                total_check["status"] = "WARNING"
                total_check["warning"] = (
                    "Displayed total reconciles without adding "
                    "tax separately. Tax may already be included "
                    "in the displayed total."
                )

        checks.append(total_check)

    else:
        checks.append(
            _check(
                "invoice_total_check",
                "subtotal + tax_amount + shipping - discount ≈ total_amount",
                {
                    "subtotal": subtotal,
                    "tax_amount": tax,
                    "shipping": shipping,
                    "discount": discount
                },
                None,
                total
            )
        )

    amounts = []

    if isinstance(line_items, list):
        for item in line_items:
            if not isinstance(item, dict):
                continue

            amount = item.get("amount")

            if isinstance(amount, (int, float)):
                amounts.append(float(amount))

    if amounts and subtotal is not None:
        checks.append(
            _check(
                "line_items_subtotal_check",
                "sum(line_items.amount) ≈ subtotal",
                {
                    "line_item_amounts": amounts
                },
                sum(amounts),
                subtotal
            )
        )
    else:
        checks.append(
            _check(
                "line_items_subtotal_check",
                "sum(line_items.amount) ≈ subtotal",
                {
                    "line_item_amounts": amounts
                },
                None,
                subtotal
            )
        )

    if (
        cash_paid is not None
        and total is not None
        and change is not None
    ):
        checks.append(
            _check(
                "cash_change_check",
                "cash_paid - total_amount ≈ change",
                {
                    "cash_paid": cash_paid,
                    "total_amount": total
                },
                cash_paid - total,
                change
            )
        )
    else:
        checks.append(
            _check(
                "cash_change_check",
                "cash_paid - total_amount ≈ change",
                {
                    "cash_paid": cash_paid,
                    "total_amount": total
                },
                None,
                change
            )
        )

    return _result(checks)


def validate_balance_sheet(fields):
    total_assets = _value(fields, "total_assets")
    total_liabilities = _value(fields, "total_liabilities")
    total_equity = _value(fields, "total_equity")
    total_capital_and_liabilities = _value(
        fields,
        "total_capital_and_liabilities"
    )

    checks = []

    if (
        total_assets is not None
        and total_capital_and_liabilities is not None
    ):
        checks.append(
            _check(
                "balance_sheet_equation",
                "total_capital_and_liabilities ≈ total_assets",
                {
                    "total_capital_and_liabilities": total_capital_and_liabilities,
                    "total_assets": total_assets
                },
                total_capital_and_liabilities,
                total_assets
            )
        )
    elif (
        total_assets is not None
        and total_liabilities is not None
        and total_equity is not None
    ):
        checks.append(
            _check(
                "balance_sheet_equation",
                "total_liabilities + total_equity ≈ total_assets",
                {
                    "total_liabilities": total_liabilities,
                    "total_equity": total_equity
                },
                total_liabilities + total_equity,
                total_assets
            )
        )
    else:
        checks.append(
            _check(
                "balance_sheet_equation",
                "total_capital_and_liabilities ≈ total_assets",
                {
                    "total_capital_and_liabilities": total_capital_and_liabilities,
                    "total_assets": total_assets
                },
                None,
                total_assets
            )
        )

    if (
        total_liabilities is not None
        and total_equity is not None
        and total_capital_and_liabilities is not None
    ):
        checks.append(
            _check(
                "liabilities_equity_check",
                "total_liabilities + total_equity ≈ total_capital_and_liabilities",
                {
                    "total_liabilities": total_liabilities,
                    "total_equity": total_equity
                },
                total_liabilities + total_equity,
                total_capital_and_liabilities
            )
        )

    return _result(checks)


def validate_profit_and_loss(fields):
    interest_earned = _value(fields, "interest_earned")
    other_income = _value(fields, "other_income")
    total_income = _value(fields, "total_income")

    interest_expended = _value(fields, "interest_expended")
    operating_expenses = _value(fields, "operating_expenses")
    provisions = _value(
        fields,
        "provisions_and_contingencies"
    )
    total_expenditure = _value(
        fields,
        "total_expenditure"
    )

    revenue = _value(fields, "revenue")
    cost_of_sales = _value(
        fields,
        "cost_of_sales"
    )
    gross_profit = _value(
        fields,
        "gross_profit"
    )
    operating_profit = _value(
        fields,
        "operating_profit"
    )
    tax = _value(fields, "tax")
    net_profit = _value(
        fields,
        "net_profit"
    )

    checks = []

    if (
        interest_earned is not None
        and other_income is not None
        and total_income is not None
    ):
        checks.append(
            _check(
                "total_income_check",
                "interest_earned + other_income ≈ total_income",
                {
                    "interest_earned": interest_earned,
                    "other_income": other_income
                },
                interest_earned + other_income,
                total_income
            )
        )
    else:
        checks.append(
            _check(
                "total_income_check",
                "interest_earned + other_income ≈ total_income",
                {
                    "interest_earned": interest_earned,
                    "other_income": other_income
                },
                None,
                total_income
            )
        )

    if (
        interest_expended is not None
        and operating_expenses is not None
        and provisions is not None
        and total_expenditure is not None
    ):
        checks.append(
            _check(
                "total_expenditure_check",
                "interest_expended + operating_expenses + provisions_and_contingencies ≈ total_expenditure",
                {
                    "interest_expended": interest_expended,
                    "operating_expenses": operating_expenses,
                    "provisions_and_contingencies": provisions
                },
                interest_expended
                + operating_expenses
                + provisions,
                total_expenditure
            )
        )
    else:
        checks.append(
            _check(
                "total_expenditure_check",
                "interest_expended + operating_expenses + provisions_and_contingencies ≈ total_expenditure",
                {
                    "interest_expended": interest_expended,
                    "operating_expenses": operating_expenses,
                    "provisions_and_contingencies": provisions
                },
                None,
                total_expenditure
            )
        )

    if (
        revenue is not None
        and cost_of_sales is not None
        and gross_profit is not None
    ):
        checks.append(
            _check(
                "gross_profit_check",
                "revenue - cost_of_sales ≈ gross_profit",
                {
                    "revenue": revenue,
                    "cost_of_sales": cost_of_sales
                },
                revenue - cost_of_sales,
                gross_profit
            )
        )
    else:
        checks.append(
            _check(
                "gross_profit_check",
                "revenue - cost_of_sales ≈ gross_profit",
                {
                    "revenue": revenue,
                    "cost_of_sales": cost_of_sales
                },
                None,
                gross_profit
            )
        )

    if (
        gross_profit is not None
        and operating_expenses is not None
        and operating_profit is not None
    ):
        checks.append(
            _check(
                "operating_profit_check",
                "gross_profit - operating_expenses ≈ operating_profit",
                {
                    "gross_profit": gross_profit,
                    "operating_expenses": operating_expenses
                },
                gross_profit - operating_expenses,
                operating_profit
            )
        )
    else:
        checks.append(
            _check(
                "operating_profit_check",
                "gross_profit - operating_expenses ≈ operating_profit",
                {
                    "gross_profit": gross_profit,
                    "operating_expenses": operating_expenses
                },
                None,
                operating_profit
            )
        )

    if (
        total_income is not None
        and total_expenditure is not None
        and net_profit is not None
    ):
        checks.append(
            _check(
                "net_profit_check",
                "total_income - total_expenditure ≈ net_profit",
                {
                    "total_income": total_income,
                    "total_expenditure": total_expenditure
                },
                total_income - total_expenditure,
                net_profit
            )
        )
    else:
        checks.append(
            _check(
                "net_profit_check",
                "total_income - total_expenditure ≈ net_profit",
                {
                    "total_income": total_income,
                    "total_expenditure": total_expenditure
                },
                None,
                net_profit
            )
        )

    if (
        operating_profit is not None
        and tax is not None
        and net_profit is not None
    ):
        checks.append(
            _check(
                "tax_profit_check",
                "operating_profit - tax ≈ net_profit",
                {
                    "operating_profit": operating_profit,
                    "tax": tax
                },
                operating_profit - tax,
                net_profit
            )
        )

    return _result(checks)


def validate_cash_flow(fields):
    operating = _value(
        fields,
        "operating_cash_flow"
    )
    investing = _value(
        fields,
        "investing_cash_flow"
    )
    financing = _value(
        fields,
        "financing_cash_flow"
    )
    fx = _value(
        fields,
        "fx_adjustment"
    )

    net_change = _value(
        fields,
        "net_change_in_cash"
    )

    opening = _value(
        fields,
        "opening_cash"
    )
    closing = _value(
        fields,
        "closing_cash"
    )

    checks = []

    component_values_available = (
        operating is not None
        and investing is not None
        and financing is not None
        and net_change is not None
    )

    if fx is None:
        fx_for_calculation = 0.0
    else:
        fx_for_calculation = fx

    if component_values_available:
        calculated_change = (
            operating
            + investing
            + financing
            + fx_for_calculation
        )
    else:
        calculated_change = None

    component_check = _check(
        "net_cash_change_check",
        "operating_cash_flow + investing_cash_flow + financing_cash_flow + fx_adjustment ≈ net_change_in_cash",
        {
            "operating_cash_flow": operating,
            "investing_cash_flow": investing,
            "financing_cash_flow": financing,
            "fx_adjustment": fx
        },
        calculated_change,
        net_change
    )

    if (
        component_check["status"] == "FAIL"
        and opening is not None
        and net_change is not None
        and closing is not None
    ):
        roll_forward = opening + net_change

        if abs(roll_forward - closing) <= TOLERANCE:
            component_check["status"] = "WARNING"
            component_check["warning"] = (
                "Cash flow components do not reconcile with "
                "the reported net change, but opening cash plus "
                "reported net change reconciles with closing cash."
            )

    checks.append(component_check)

    if (
        opening is not None
        and net_change is not None
        and closing is not None
    ):
        checks.append(
            _check(
                "closing_cash_check",
                "opening_cash + net_change_in_cash ≈ closing_cash",
                {
                    "opening_cash": opening,
                    "net_change_in_cash": net_change
                },
                opening + net_change,
                closing
            )
        )
    else:
        checks.append(
            _check(
                "closing_cash_check",
                "opening_cash + net_change_in_cash ≈ closing_cash",
                {
                    "opening_cash": opening,
                    "net_change_in_cash": net_change
                },
                None,
                closing
            )
        )

    return _result(checks)


def validate_financials(
    document_type,
    fields,
    line_items
):
    if isinstance(document_type, str):
        document_type = document_type.lower().strip()
    else:
        document_type = ""

    if not isinstance(fields, dict):
        fields = {}

    if not isinstance(line_items, list):
        line_items = []

    if document_type == "invoice":
        return validate_invoice(
            fields,
            line_items
        )

    if document_type == "balance_sheet":
        return validate_balance_sheet(
            fields
        )

    if document_type in (
        "profit_loss",
        "profit_and_loss",
        "income_statement"
    ):
        return validate_profit_and_loss(
            fields
        )

    if document_type in (
        "cash_flow",
        "cash_flow_statement"
    ):
        return validate_cash_flow(
            fields
        )

    return {
        "checks": [],
        "overall_status": "NOT_APPLICABLE",
        "issues": [],
        "warnings": []
    }