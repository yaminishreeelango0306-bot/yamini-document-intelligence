import re
from typing import Any, Dict, List, Optional


FIELD_ALIASES = {
    "document_date": [
        "document date",
        "statement date",
        "reporting date",
        "year ended",
        "for the year ended",
        "as at",
        "as of",
        "invoice date",
        "date"
    ],
    "currency": [
        "currency code",
        "currency"
    ],
    "revenue": [
        "revenue",
        "total revenue",
        "sales revenue",
        "sales",
        "turnover",
        "income from operations"
    ],
    "cost_of_sales": [
        "cost of sales",
        "cost of goods sold",
        "cost of goods"
    ],
    "gross_profit": [
        "gross profit"
    ],
    "operating_profit": [
        "operating profit",
        "profit from operations",
        "operating income"
    ],
    "interest_earned": [
        "interest earned",
        "interest income",
        "interest received"
    ],
    "other_income": [
        "other income",
        "other operating income"
    ],
    "total_income": [
        "total income",
        "total revenue and other income"
    ],
    "interest_expended": [
        "interest expended",
        "interest expense",
        "interest expenses",
        "finance cost",
        "finance costs"
    ],
    "operating_expenses": [
        "operating expenses",
        "operating expense"
    ],
    "provisions_and_contingencies": [
        "provisions and contingencies",
        "provision and contingencies",
        "provisions"
    ],
    "total_expenditure": [
        "total expenditure",
        "total expenses",
        "total expense"
    ],
    "tax": [
        "income tax",
        "tax expense",
        "provision for tax",
        "tax"
    ],
    "net_profit": [
        "net profit",
        "profit after tax",
        "profit for the year",
        "net income",
        "profit attributable"
    ],
    "total_assets": [
        "total assets"
    ],
    "total_liabilities": [
        "total liabilities"
    ],
    "total_equity": [
        "total equity",
        "shareholders equity",
        "shareholders' equity"
    ],
    "total_capital_and_liabilities": [
        "total capital and liabilities",
        "capital and liabilities total"
    ],
    "operating_cash_flow": [
        "operating cash flow",
        "cash flow from operating activities",
        "net cash from operating activities",
        "net cash flow from operating activities",
        "net cash flow used in operating activities",
        "net cash flow (used in) / from operating activities",
        "cash generated from operations"
    ],
    "investing_cash_flow": [
        "investing cash flow",
        "cash flow from investing activities",
        "net cash from investing activities",
        "net cash flow from investing activities",
        "net cash flow used in investing activities"
    ],
    "financing_cash_flow": [
        "financing cash flow",
        "cash flow from financing activities",
        "net cash from financing activities",
        "net cash flow from financing activities"
    ],
    "fx_adjustment": [
        "foreign exchange adjustment",
        "fx adjustment",
        "effect of exchange fluctuation",
        "effect of exchange fluctuations",
        "effect of exchange rate changes",
        "exchange fluctuation on translation reserve"
    ],
    "net_change_in_cash": [
        "net change in cash",
        "net increase in cash",
        "net decrease in cash",
        "net increase / (decrease) in cash",
        "net increase /(decrease) in cash",
        "net increase in cash and cash equivalents",
        "net decrease in cash and cash equivalents",
        "net increase /(decrease) in cash and cash equivalents"
    ],
    "opening_cash": [
        "opening cash",
        "cash at beginning of year",
        "cash and cash equivalents at beginning",
        "cash and cash equivalents as at april 1st"
    ],
    "closing_cash": [
        "closing cash",
        "cash at end of year",
        "cash and cash equivalents at end",
        "cash and cash equivalents as at march 31st"
    ],
    "invoice_number": [
        "invoice number",
        "invoice no",
        "invoice #",
        "bill number",
        "bill no"
    ],
    "vendor_name": [
        "vendor name",
        "supplier name",
        "seller name",
        "vendor",
        "supplier",
        "seller"
    ],
    "customer_name": [
        "customer name",
        "buyer name",
        "bill to",
        "customer",
        "buyer"
    ],
    "subtotal": [
        "subtotal",
        "sub total"
    ],
    "discount": [
        "discount"
    ],
    "tax_amount": [
        "tax amount",
        "gst",
        "vat",
        "sales tax"
    ],
    "total_amount": [
        "total amount",
        "grand total",
        "amount due",
        "invoice total",
        "total"
    ],
    "shipping": [
        "shipping",
        "shipping charges",
        "delivery charges",
        "freight",
        "transport charges"
    ],
    "cash_paid": [
        "cash paid",
        "amount paid",
        "paid amount"
    ],
    "change": [
        "change",
        "balance change"
    ]
}


STATEMENT_ALIASES = {
    "balance_sheet": [
        "balance sheet",
        "consolidated balance sheet",
        "statement of financial position",
        "financial position"
    ],
    "profit_and_loss": [
        "profit and loss",
        "profit & loss",
        "profit and loss account",
        "statement of profit and loss",
        "income statement",
        "consolidated statement of profit and loss"
    ],
    "cash_flow": [
        "cash flow",
        "cash flows",
        "cash flow statement",
        "statement of cash flows",
        "consolidated cash flow statement"
    ],
    "invoice": [
        "invoice",
        "tax invoice",
        "commercial invoice",
        "bill"
    ]
}


def _empty_field():
    return {
        "value": None,
        "confidence": 0
    }


def _make_field(value, confidence, source_line=None, raw=None):
    result = {
        "value": value,
        "confidence": round(float(confidence), 3)
    }

    if source_line is not None or raw is not None:
        result["evidence"] = {
            "source_line": source_line or "",
            "raw": raw or ""
        }

    return result


def _normalise_text(text):
    if not text:
        return ""

    text = str(text)
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\x0c", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _clean_line(line):
    if not line:
        return ""

    line = str(line).strip()
    line = re.sub(r"[ \t]+", " ", line)

    return line.strip()


def _normalise_for_matching(text):
    if not text:
        return ""

    text = str(text).lower()
    text = text.replace("&", " and ")
    text = text.replace("’", "'")
    text = re.sub(r"[\s|:._\\/-]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _prepare_lines(text):
    text = _normalise_text(text)

    lines = []

    for line in text.splitlines():
        line = _clean_line(line)

        if line:
            lines.append(line)

    return lines


def _pages_to_text(pages):
    if pages is None:
        return ""

    if isinstance(pages, str):
        return pages

    page_texts = []

    if isinstance(pages, dict):
        if isinstance(pages.get("pages"), list):
            for page in pages["pages"]:
                if isinstance(page, str):
                    page_texts.append(page)
                elif isinstance(page, dict):
                    value = page.get("text")

                    if value:
                        page_texts.append(str(value))
                    elif page.get("content"):
                        page_texts.append(str(page["content"]))
        else:
            for value in pages.values():
                if isinstance(value, str):
                    page_texts.append(value)
                elif isinstance(value, dict):
                    value_text = value.get("text")

                    if value_text:
                        page_texts.append(str(value_text))
                    elif value.get("content"):
                        page_texts.append(str(value["content"]))

    elif isinstance(pages, list):
        for page in pages:
            if isinstance(page, str):
                page_texts.append(page)
            elif isinstance(page, dict):
                value = page.get("text")

                if value:
                    page_texts.append(str(value))
                elif page.get("content"):
                    page_texts.append(str(page["content"]))

    return "\n".join(page_texts)


def _normalise_ocr_number_text(value):
    if not value:
        return ""

    value = str(value)
    value = value.replace("O", "0")
    value = value.replace("o", "0")
    value = re.sub(r"(?<=\d)\s+(?=,\d)", "", value)
    value = re.sub(r"(?<=\d),\s+(?=\d)", ",", value)

    return value


def _parse_number(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = _normalise_ocr_number_text(value)

    value = value.replace("₹", "")
    value = value.replace("$", "")
    value = value.replace("€", "")
    value = value.replace("£", "")
    value = value.replace(" ", "")

    negative = False

    if value.startswith("(") and value.endswith(")"):
        negative = True
        value = value[1:-1]

    value = re.sub(r"[^0-9,.\-+]", "", value)

    if not value:
        return None

    if value.count(",") > 0 and value.count(".") > 0:
        last_comma = value.rfind(",")
        last_dot = value.rfind(".")

        if last_comma > last_dot:
            decimal_part = value[last_comma + 1:]

            if len(decimal_part) <= 2:
                value = value.replace(".", "")
                value = value.replace(",", ".")
            else:
                value = value.replace(",", "")
        else:
            decimal_part = value[last_dot + 1:]

            if len(decimal_part) <= 2:
                value = value.replace(",", "")
            else:
                value = value.replace(".", "")
                value = value.replace(",", "")

    elif value.count(",") > 0:
        parts = value.split(",")

        if all(len(part) == 3 for part in parts[1:]):
            value = "".join(parts)
        else:
            value = value.replace(",", "")

    elif value.count(".") > 1:
        parts = value.split(".")

        if all(len(part) == 3 for part in parts[1:]):
            value = "".join(parts)
        else:
            value = "".join(parts)

    try:
        number = float(value)

        if negative:
            number = -number

        return number

    except ValueError:
        return None


_NUMBER_PATTERN = re.compile(
    r"""
    (?P<currency>[₹$€£])?
    \s*
    (?P<number>
        \(?
        [+-]?
        (?:
            \d{1,3}(?:,\d{3})+
            |
            \d{1,3}(?:\.\d{3})+
            |
            \d+
        )
        (?:[.,]\d+)?
        \)?
    )
    """,
    re.VERBOSE
)


def _extract_numeric_tokens(line):
    if not line:
        return []

    line = _normalise_ocr_number_text(line)

    results = []

    for match in _NUMBER_PATTERN.finditer(line):
        raw = match.group("number")
        value = _parse_number(raw)

        if value is None:
            continue

        results.append(
            {
                "value": value,
                "raw": raw,
                "start": match.start(),
                "end": match.end()
            }
        )

    return results


def _is_probable_year(value):
    return 1900 <= value <= 2100


def _find_next_numeric_line(lines, start_index, max_distance=4):
    for index in range(
        start_index + 1,
        min(len(lines), start_index + max_distance + 1)
    ):
        values = _extract_numeric_tokens(lines[index])

        if values:
            useful = [
                item
                for item in values
                if not _is_probable_year(item["value"])
            ]

            if useful:
                return {
                    "values": useful,
                    "line_index": index,
                    "source_line": lines[index]
                }

    return None


def _alias_match(line, alias):
    normalized_line = _normalise_for_matching(line)
    normalized_alias = _normalise_for_matching(alias)

    if not normalized_line or not normalized_alias:
        return False

    if normalized_line == normalized_alias:
        return True

    if normalized_line.startswith(normalized_alias + " "):
        return True

    if " " + normalized_alias + " " in " " + normalized_line + " ":
        return True

    return False


def _find_matching_alias(line, aliases):
    for alias in aliases:
        if _alias_match(line, alias):
            return alias

    return None


def _find_best_value_for_alias(lines, aliases):
    best = None

    for index, line in enumerate(lines):
        matched_alias = _find_matching_alias(line, aliases)

        if matched_alias is None:
            continue

        values = _extract_numeric_tokens(line)
        source_line = line

        if not values:
            next_result = _find_next_numeric_line(
                lines,
                index,
                max_distance=4
            )

            if next_result:
                values = next_result["values"]
                source_line = next_result["source_line"]

        if not values:
            continue

        useful_values = [
            value
            for value in values
            if not _is_probable_year(value["value"])
        ]

        if not useful_values:
            continue

        selected = useful_values[0]

        confidence = 0.90

        if len(useful_values) == 1:
            confidence += 0.05

        if _normalise_for_matching(line).startswith(
            _normalise_for_matching(matched_alias)
        ):
            confidence += 0.03

        candidate = _make_field(
            selected["value"],
            min(confidence, 0.98),
            source_line,
            selected["raw"]
        )

        if (
            best is None
            or candidate["confidence"] > best["confidence"]
        ):
            best = candidate

    if best is None:
        return _empty_field()

    return best


def _find_value_after_label(lines, label_index, max_distance=4):
    current_values = _extract_numeric_tokens(
        lines[label_index]
    )

    useful = [
        item
        for item in current_values
        if not _is_probable_year(item["value"])
    ]

    if useful:
        return useful

    next_result = _find_next_numeric_line(
        lines,
        label_index,
        max_distance
    )

    if next_result:
        return next_result["values"]

    return []


def _extract_date(text):
    patterns = [
        r"\b[A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}\b",
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",
        r"\b\d{1,2}[-/][A-Za-z]{3,9}[-/]\d{2,4}\b",
        r"\b[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}\b"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return _make_field(
                match.group(0),
                0.94,
                match.group(0),
                match.group(0)
            )

    return _empty_field()


def _extract_currency(text):
    patterns = [
        (r"\bINR\b", "INR"),
        (r"\bUSD\b", "USD"),
        (r"\bEUR\b", "EUR"),
        (r"\bGBP\b", "GBP"),
        (r"\bAED\b", "AED"),
        (r"\bAUD\b", "AUD"),
        (r"\bCAD\b", "CAD"),
        (r"\bJPY\b", "JPY"),
        (r"\bRupees?\b", "INR"),
        (r"\bDollars?\b", "USD"),
        (r"\bEuros?\b", "EUR"),
        (r"\bPounds?\b", "GBP"),
        (r"₹", "INR"),
        (r"\$", "USD"),
        (r"€", "EUR"),
        (r"£", "GBP")
    ]

    for pattern, currency in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return _make_field(
                currency,
                0.94,
                match.group(0),
                match.group(0)
            )

    if re.search(
        r"\bin\s*['’]?\s*000\b",
        text,
        re.IGNORECASE
    ):
        return _make_field(
            "INR",
            0.60,
            "in '000",
            "in '000"
        )

    return _empty_field()


def _detect_document_type(text):
    normalized = _normalise_for_matching(text)

    scores = {
        "balance_sheet": 0,
        "profit_and_loss": 0,
        "cash_flow": 0,
        "invoice": 0
    }

    for document_type, aliases in STATEMENT_ALIASES.items():
        for alias in aliases:
            alias_normalized = _normalise_for_matching(alias)

            if alias_normalized in normalized:
                scores[document_type] += 1

    if "capital and liabilities" in normalized:
        scores["balance_sheet"] += 10

    if "total assets" in normalized:
        scores["balance_sheet"] += 5

    if "cash flow from operating activities" in normalized:
        scores["cash_flow"] += 5

    if "cash flow from investing activities" in normalized:
        scores["cash_flow"] += 5

    if "cash flow from financing activities" in normalized:
        scores["cash_flow"] += 5

    if "profit before tax" in normalized:
        scores["profit_and_loss"] += 5

    if "profit after tax" in normalized:
        scores["profit_and_loss"] += 5

    if "invoice number" in normalized:
        scores["invoice"] += 5

    if "invoice no" in normalized:
        scores["invoice"] += 5

    detected = max(
        scores,
        key=scores.get
    )

    if scores[detected] == 0:
        return "generic"

    return detected


def _extract_fixed_fields(text,lines):
    return {
        "document_date":_extract_date(text),
        "currency":_extract_currency(text)
    }


def _extract_p_and_l_fields(text,lines):
    fields = {}

    keys = [
        "revenue",
        "cost_of_sales",
        "gross_profit",
        "operating_profit",
        "interest_earned",
        "other_income",
        "total_income",
        "interest_expended",
        "operating_expenses",
        "provisions_and_contingencies",
        "total_expenditure",
        "tax",
        "net_profit"
    ]

    for key in keys:
        fields[key] = _find_best_value_for_alias(
            lines,
            FIELD_ALIASES[key]
        )

    return fields


def _find_cash_flow_value(lines,aliases):
    return _find_best_value_for_alias(
        lines,
        aliases
    )


def _extract_cash_flow_specific_fields(text,lines):
    fields = {}

    fields["operating_cash_flow"] = _find_cash_flow_value(
        lines,
        FIELD_ALIASES["operating_cash_flow"]
    )

    fields["investing_cash_flow"] = _find_cash_flow_value(
        lines,
        FIELD_ALIASES["investing_cash_flow"]
    )

    fields["financing_cash_flow"] = _find_cash_flow_value(
        lines,
        FIELD_ALIASES["financing_cash_flow"]
    )

    fields["fx_adjustment"] = _find_cash_flow_value(
        lines,
        FIELD_ALIASES["fx_adjustment"]
    )

    fields["net_change_in_cash"] = _find_cash_flow_value(
        lines,
        FIELD_ALIASES["net_change_in_cash"]
    )

    fields["opening_cash"] = _find_cash_flow_value(
        lines,
        FIELD_ALIASES["opening_cash"]
    )

    fields["closing_cash"] = _find_cash_flow_value(
        lines,
        FIELD_ALIASES["closing_cash"]
    )

    return fields


def _extract_text_value(lines,aliases):
    normalized_aliases = [
        _normalise_for_matching(alias)
        for alias in aliases
    ]

    for index,line in enumerate(lines):
        normalized_line = _normalise_for_matching(line)
        matched_alias = None

        for alias in normalized_aliases:
            if alias in normalized_line:
                matched_alias = alias
                break

        if matched_alias is None:
            continue

        pattern = re.compile(
            re.escape(matched_alias).replace(
                r"\ ",
                r"\s+"
            ),
            re.IGNORECASE
        )

        match = pattern.search(line)

        if match:
            value = line[match.end():].strip()

            value = re.sub(
                r"^[\s:=-]+",
                "",
                value
            ).strip()

            if value:
                return _make_field(
                    value,
                    0.88,
                    line,
                    value
                )

        if index + 1 < len(lines):
            next_line = lines[index + 1]

            if not _extract_numeric_tokens(next_line):
                return _make_field(
                    next_line,
                    0.80,
                    next_line,
                    next_line
                )

    return _empty_field()


def _extract_invoice_number(text,lines):
    patterns = [
        r"\binvoice\s*(?:number|no\.?|#)\s*[:#-]?\s*([A-Za-z0-9-]+)",
        r"\bbill\s*(?:number|no\.?)\s*[:#-]?\s*([A-Za-z0-9-]+)",
        r"\b(?:meld|inv|invoice)\s*#\s*([A-Za-z0-9-]+)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            value = match.group(1).strip()

            return _make_field(
                value,
                0.94,
                match.group(0),
                match.group(0)
            )

    for line in lines:
        normalized = _normalise_for_matching(line)

        if "invoice" in normalized or "bill" in normalized:
            values = re.findall(
                r"[A-Za-z0-9]+[-]?[A-Za-z0-9]+",
                line
            )

            for value in values:
                if any(char.isdigit() for char in value):
                    return _make_field(
                        value,
                        0.80,
                        line,
                        line
                    )

        if re.search(
            r"\b[A-Za-z]{2,}\s*#\s*\d+\b",
            line,
            re.IGNORECASE
        ):
            match = re.search(
                r"#\s*([A-Za-z0-9-]+)",
                line
            )

            if match:
                return _make_field(
                    match.group(1),
                    0.90,
                    line,
                    line
                )

    return _empty_field()


def _extract_vendor_name(lines):
    explicit = _extract_text_value(
        lines,
        FIELD_ALIASES["vendor_name"]
    )

    if explicit["value"] is not None:
        return explicit

    blocked = {
        "invoice",
        "meld",
        "from",
        "total",
        "ticket completed",
        "invoice date",
        "notes",
        "no",
        "description",
        "quantity",
        "rate",
        "cost",
        "amount"
    }

    for index,line in enumerate(lines):
        normalized = _normalise_for_matching(line)

        if not normalized:
            continue

        if normalized in blocked:
            continue

        if any(
            item in normalized
            for item in [
                "invoice date",
                "ticket completed",
                "notes",
                "description",
                "quantity",
                "rate",
                "cost",
                "amount"
            ]
        ):
            continue

        if re.search(r"\b\d{3,}\b",line):
            continue

        if re.search(
            r"\b[A-Za-z]+\s*#\s*\d+",
            line
        ):
            continue

        if index <= 4:
            words = re.findall(
                r"[A-Za-z][A-Za-z&'.-]*",
                line
            )

            if len(words) >= 2:
                return _make_field(
                    line,
                    0.82,
                    line,
                    line
                )

    return _empty_field()


def _extract_invoice_total(lines):
    total_patterns = [
        r"^\s*total\s*[:\-]?\s*[$€£₹]?\s*[\d,.\-()]+",
        r"\bgrand\s+total\b",
        r"\btotal\s+amount\b",
        r"\binvoice\s+total\b",
        r"\bamount\s+due\b"
    ]

    candidates = []

    for line in lines:
        normalized = _normalise_for_matching(line)

        matched = False

        for pattern in total_patterns:
            if re.search(pattern,line,re.IGNORECASE):
                matched = True
                break

        if not matched:
            continue

        values = _extract_numeric_tokens(line)

        if not values:
            continue

        useful = [
            item
            for item in values
            if not _is_probable_year(item["value"])
        ]

        if not useful:
            continue

        selected = useful[-1]

        confidence = 0.95

        if normalized.startswith("total"):
            confidence = 0.97

        candidates.append(
            _make_field(
                selected["value"],
                confidence,
                line,
                selected["raw"]
            )
        )

    if candidates:
        return max(
            candidates,
            key=lambda item:item["confidence"]
        )

    return _empty_field()


def _extract_invoice_fields(text,lines):
    fields = {}

    fields["invoice_number"] = _extract_invoice_number(
        text,
        lines
    )

    fields["vendor_name"] = _extract_vendor_name(
        lines
    )

    fields["customer_name"] = _extract_text_value(
        lines,
        FIELD_ALIASES["customer_name"]
    )

    fields["document_date"] = _extract_date(text)

    fields["currency"] = _extract_currency(text)

    fields["subtotal"] = _find_best_value_for_alias(
        lines,
        FIELD_ALIASES["subtotal"]
    )

    fields["discount"] = _find_best_value_for_alias(
        lines,
        FIELD_ALIASES["discount"]
    )

    fields["tax_amount"] = _find_best_value_for_alias(
        lines,
        FIELD_ALIASES["tax_amount"]
    )

    fields["total_amount"] = _extract_invoice_total(
        lines
    )

    fields["shipping"] = _find_best_value_for_alias(
        lines,
        FIELD_ALIASES["shipping"]
    )

    fields["cash_paid"] = _find_best_value_for_alias(
        lines,
        FIELD_ALIASES["cash_paid"]
    )

    fields["change"] = _find_best_value_for_alias(
        lines,
        FIELD_ALIASES["change"]
    )

    return fields


def _find_section_indexes(lines):
    result = {
        "capital_and_liabilities": None,
        "assets": None
    }

    for index,line in enumerate(lines):
        normalized = _normalise_for_matching(line)

        if (
            result["capital_and_liabilities"] is None
            and (
                "capital and liabilities" in normalized
                or normalized == "capital liabilities"
            )
        ):
            result["capital_and_liabilities"] = index

        if (
            result["assets"] is None
            and normalized in (
                "assets",
                "asset"
            )
        ):
            result["assets"] = index

    return result


def _clean_financial_label(line):
    label = _clean_line(line)

    label = re.sub(
        r"\b\d+[A-Za-z]?\b$",
        "",
        label
    ).strip()

    label = re.sub(
        r"\s+",
        " ",
        label
    )

    return label


def _looks_like_schedule_number(line):
    value = _clean_line(line)

    return bool(
        re.fullmatch(
            r"\d+[A-Za-z]?",
            value
        )
    )


def _looks_like_date_line(line):
    normalized = _normalise_for_matching(line)

    return (
        "mar 31" in normalized
        or "31 mar" in normalized
        or "april" in normalized
        or "march" in normalized
    )


def _is_bad_financial_label(label):
    normalized = _normalise_for_matching(label)

    if not normalized:
        return True

    blocked = [
        "total",
        "capital and liabilities",
        "assets",
        "as at",
        "schedule",
        "in 000",
        "membership no",
        "mumbai",
        "mumbal",
        "chief financial officer",
        "company secretary",
        "executive director",
        "managing director",
        "chairperson",
        "directors",
        "annual report",
        "significant accounting policies",
        "the schedules referred",
        "as per our report",
        "for and on behalf"
    ]

    for item in blocked:
        if item in normalized:
            return True

    return False


def _get_numeric_values_from_following_lines(
    lines,
    start_index,
    max_distance=5
):
    values = []
    raw_lines = []

    for index in range(
        start_index,
        min(
            len(lines),
            start_index + max_distance + 1
        )
    ):
        line = lines[index]

        numeric_values = _extract_numeric_tokens(line)

        if numeric_values:
            useful = [
                item
                for item in numeric_values
                if not _is_probable_year(item["value"])
            ]

            if useful:
                values.extend(useful)
                raw_lines.append(line)

                if len(values) >= 2:
                    break

        else:
            normalized = _normalise_for_matching(line)

            if normalized in (
                "assets",
                "capital and liabilities",
                "total"
            ):
                break

            if _looks_like_schedule_number(line):
                continue

            if index > start_index:
                break

    return values[:2],raw_lines


def _extract_balance_rows(text):
    lines = _prepare_lines(text)

    sections = _find_section_indexes(lines)

    capital_start = sections["capital_and_liabilities"]
    assets_start = sections["assets"]

    rows = []

    if capital_start is not None:
        end_index = (
            assets_start
            if assets_start is not None
            else len(lines)
        )

        index = capital_start + 1

        while index < end_index:
            line = lines[index]
            normalized = _normalise_for_matching(line)

            if normalized == "total":
                index += 1
                continue

            if _looks_like_schedule_number(line):
                index += 1
                continue

            if _looks_like_date_line(line):
                index += 1
                continue

            if _is_bad_financial_label(line):
                index += 1
                continue

            values,raw_lines = _get_numeric_values_from_following_lines(
                lines,
                index + 1,
                max_distance=5
            )

            if values:
                label = _clean_financial_label(line)

                if (
                    label
                    and not _is_bad_financial_label(label)
                    and len(label) >= 3
                ):
                    rows.append(
                        {
                            "section":"liabilities",
                            "label":label,
                            "values":[
                                item["value"]
                                for item in values
                            ],
                            "amount":values[0]["value"],
                            "raw":"\n".join(
                                [line] + raw_lines
                            )
                        }
                    )

                    index += 1 + len(raw_lines)
                    continue

            index += 1

    if assets_start is not None:
        index = assets_start + 1

        while index < len(lines):
            line = lines[index]
            normalized = _normalise_for_matching(line)

            if normalized == "total":
                index += 1
                continue

            if normalized.startswith("contingent liabilities"):
                break

            if normalized.startswith("bills for collection"):
                break

            if normalized.startswith(
                "significant accounting policies"
            ):
                break

            if _looks_like_schedule_number(line):
                index += 1
                continue

            if _looks_like_date_line(line):
                index += 1
                continue

            if _is_bad_financial_label(line):
                index += 1
                continue

            values,raw_lines = _get_numeric_values_from_following_lines(
                lines,
                index + 1,
                max_distance=5
            )

            if values:
                label = _clean_financial_label(line)

                if (
                    label
                    and not _is_bad_financial_label(label)
                    and len(label) >= 3
                ):
                    rows.append(
                        {
                            "section":"assets",
                            "label":label,
                            "values":[
                                item["value"]
                                for item in values
                            ],
                            "amount":values[0]["value"],
                            "raw":"\n".join(
                                [line] + raw_lines
                            )
                        }
                    )

                    index += 1 + len(raw_lines)
                    continue

            index += 1

    return rows


def _find_total_after_section(
    lines,
    start_index,
    end_index
):
    for index in range(
        start_index + 1,
        end_index
    ):
        normalized = _normalise_for_matching(
            lines[index]
        )

        if normalized != "total":
            continue

        values,raw_lines = _get_numeric_values_from_following_lines(
            lines,
            index + 1,
            max_distance=3
        )

        if values:
            value = values[0]

            return _make_field(
                value["value"],
                0.98,
                value["raw"],
                value["raw"]
            )

    return _empty_field()


def _extract_balance_sheet_totals(text):
    lines = _prepare_lines(text)

    result = {
        "total_assets":_empty_field(),
        "total_liabilities":_empty_field(),
        "total_equity":_empty_field(),
        "total_capital_and_liabilities":_empty_field()
    }

    sections = _find_section_indexes(lines)

    capital_start = sections["capital_and_liabilities"]
    assets_start = sections["assets"]

    capital_end = (
        assets_start
        if assets_start is not None
        else len(lines)
    )

    if capital_start is not None:
        result["total_capital_and_liabilities"] = (
            _find_total_after_section(
                lines,
                capital_start,
                capital_end
            )
        )

    if assets_start is not None:
        result["total_assets"] = (
            _find_total_after_section(
                lines,
                assets_start,
                len(lines)
            )
        )

    explicit_liabilities = _find_best_value_for_alias(
        lines,
        FIELD_ALIASES["total_liabilities"]
    )

    explicit_equity = _find_best_value_for_alias(
        lines,
        FIELD_ALIASES["total_equity"]
    )

    if explicit_liabilities["value"] is not None:
        result["total_liabilities"] = explicit_liabilities

    if explicit_equity["value"] is not None:
        result["total_equity"] = explicit_equity

    rows = _extract_balance_rows(text)

    liability_rows = [
        row
        for row in rows
        if row["section"] == "liabilities"
    ]

    if result["total_liabilities"]["value"] is None:
        liability_names = [
            "deposits",
            "borrowings",
            "other liabilities and provisions",
            "other liabilities"
        ]

        liability_total = 0
        found = False

        for row in liability_rows:
            normalized_label = _normalise_for_matching(
                row["label"]
            )

            if any(
                name in normalized_label
                for name in liability_names
            ):
                liability_total += row["amount"]
                found = True

        if found:
            result["total_liabilities"] = _make_field(
                liability_total,
                0.90,
                "Derived from Deposits + Borrowings + Other liabilities and provisions",
                str(liability_total)
            )

    if result["total_equity"]["value"] is None:
        equity_names = [
            "capital",
            "reserves and surplus",
            "minority interest"
        ]

        equity_total = 0
        found = False

        for row in liability_rows:
            normalized_label = _normalise_for_matching(
                row["label"]
            )

            if any(
                normalized_label == name
                or normalized_label.startswith(name + " ")
                for name in equity_names
            ):
                equity_total += row["amount"]
                found = True

        if found:
            result["total_equity"] = _make_field(
                equity_total,
                0.90,
                "Derived from Capital + Reserves and surplus + Minority interest",
                str(equity_total)
            )

    return result


def _extract_balance_sheet_line_items(text):
    return _extract_balance_rows(text)


def _is_financial_description(line):
    normalized = _normalise_for_matching(line)

    if not normalized:
        return False

    excluded = [
        "consolidated cash flow statement",
        "consolidated cash flowstatement",
        "for the year ended",
        "year ended",
        "in 000",
        "in000",
        "hdfc bank limited annual report",
        "as per our report",
        "for and on behalf",
        "chartered accountants",
        "membership no",
        "firm registration no",
        "chief financial officer",
        "executive director",
        "managing director",
        "chairperson",
        "directors",
        "vice president",
        "company secretary"
    ]

    for word in excluded:
        if word in normalized:
            return False

    return True


def _extract_financial_line_items(text,document_type):
    if document_type == "balance_sheet":
        return []

    lines = _prepare_lines(text)
    items = []

    index = 0

    while index < len(lines):
        line = lines[index]

        if _looks_like_schedule_number(line):
            index += 1
            continue

        if not _is_financial_description(line):
            index += 1
            continue

        normalized = _normalise_for_matching(line)

        if normalized.startswith("total"):
            index += 1
            continue

        values = _extract_numeric_tokens(line)

        if values:
            index += 1
            continue

        next_values,raw_lines = _get_numeric_values_from_following_lines(
            lines,
            index + 1,
            max_distance=4
        )

        if next_values:
            useful_values = [
                item["value"]
                for item in next_values
                if not _is_probable_year(item["value"])
            ]

            if useful_values:
                items.append(
                    {
                        "label":line,
                        "values":useful_values,
                        "amount":useful_values[0],
                        "raw":"\n".join(
                            [line] + raw_lines
                        )
                    }
                )

                index += 1 + len(raw_lines)
                continue

        index += 1

    return items


def _extract_tables(text):
    lines = _prepare_lines(text)

    rows = []

    for line in lines:
        values = _extract_numeric_tokens(line)

        if values:
            rows.append(
                {
                    "raw":line,
                    "values":[
                        item["value"]
                        for item in values
                    ]
                }
            )

    if not rows:
        return []

    return [
        {
            "rows":rows
        }
    ]


def _looks_like_invoice_item_line(line):
    normalized = _normalise_for_matching(line)

    if not normalized:
        return False

    blocked = [
        "invoice",
        "meld",
        "beyond digital imaging",
        "from",
        "ticket completed",
        "invoice date",
        "sept",
        "sep",
        "oct",
        "notes",
        "total",
        "subtotal",
        "discount",
        "tax",
        "gst",
        "vat",
        "amount due",
        "invoice total",
        "description",
        "quantity",
        "rate",
        "cost",
        "amount"
    ]

    for word in blocked:
        if normalized.startswith(word):
            return False

    if re.search(
        r"\b[A-Z]{1,3}\d{3,}\b",
        line
    ):
        return False

    if re.search(
        r"\b\d{3,}\b",
        line
    ):
        return True

    return False


def _extract_invoice_line_items(text):
    lines = _prepare_lines(text)

    items = []

    header_found = False

    for line in lines:
        normalized = _normalise_for_matching(line)

        if normalized == "description":
            header_found = True
            continue

        if (
            "description" in normalized
            and "quantity" in normalized
        ):
            header_found = True
            continue

        if any(
            word in normalized
            for word in [
                "subtotal",
                "sub total",
                "discount",
                "grand total",
                "total amount",
                "amount due"
            ]
        ):
            continue

        values = _extract_numeric_tokens(line)

        if not values:
            continue

        if not header_found:
            continue

        if not _looks_like_invoice_item_line(line):
            continue

        if len(values) < 2:
            continue

        amounts = [
            value["value"]
            for value in values
        ]

        first_number = values[0]

        description = line[:first_number["start"]].strip()

        description = re.sub(
            r"^[\s|:.-]+",
            "",
            description
        ).strip()

        if not description:
            continue

        if len(description) < 2:
            continue

        if not re.search(
            r"[A-Za-z]",
            description
        ):
            continue

        items.append(
            {
                "description":description,
                "amount":amounts[-1],
                "values":amounts,
                "raw":line
            }
        )

    return items


def _extract_statement_fields(
    text,
    document_type
):
    lines = _prepare_lines(text)

    fields = _extract_fixed_fields(
        text,
        lines
    )

    if document_type == "profit_and_loss":
        specific = _extract_p_and_l_fields(
            text,
            lines
        )

        fields.update(specific)

    elif document_type == "cash_flow":
        specific = _extract_cash_flow_specific_fields(
            text,
            lines
        )

        fields.update(specific)

    elif document_type == "balance_sheet":
        totals = _extract_balance_sheet_totals(
            text
        )

        fields.update(totals)

    return fields


def _extract_invoice(text):
    lines = _prepare_lines(text)

    return _extract_invoice_fields(
        text,
        lines
    )


def _extract_statement(
    text,
    document_type
):
    return _extract_statement_fields(
        text,
        document_type
    )


def _extract_generic(text):
    lines = _prepare_lines(text)

    return _extract_fixed_fields(
        text,
        lines
    )


def _normalise_requested_type(document_type):
    if not document_type:
        return None

    requested = str(
        document_type
    ).strip().lower()

    aliases = {
        "balance sheet":"balance_sheet",
        "balancesheet":"balance_sheet",
        "balance_sheet":"balance_sheet",
        "profit and loss":"profit_and_loss",
        "profit & loss":"profit_and_loss",
        "p&l":"profit_and_loss",
        "pnl":"profit_and_loss",
        "profit_and_loss":"profit_and_loss",
        "income statement":"profit_and_loss",
        "cash flow":"cash_flow",
        "cashflow":"cash_flow",
        "cash_flow":"cash_flow",
        "cash_flow_statement":"cash_flow",
        "cash flow statement":"cash_flow",
        "invoice":"invoice"
    }

    return aliases.get(
        requested,
        requested
    )


def extract_document(
    pages,
    document_type=None
):
    text = _pages_to_text(pages)
    text = _normalise_text(text)

    if not text:
        detected_type = (
            _normalise_requested_type(document_type)
            or "generic"
        )

        return {
            "document_type":detected_type,
            "fields":{},
            "line_items":[],
            "tables":[],
            "raw_text_by_page":pages
        }

    requested_type = _normalise_requested_type(
        document_type
    )

    if requested_type in (
        "invoice",
        "balance_sheet",
        "profit_and_loss",
        "cash_flow"
    ):
        detected_type = requested_type
    else:
        detected_type = _detect_document_type(text)

    if detected_type == "invoice":
        fields = _extract_invoice(text)

        line_items = _extract_invoice_line_items(
            text
        )

    elif detected_type in (
        "balance_sheet",
        "profit_and_loss",
        "cash_flow"
    ):
        fields = _extract_statement(
            text,
            detected_type
        )

        line_items = _extract_financial_line_items(
            text,
            detected_type
        )

        if detected_type == "balance_sheet":
            line_items = _extract_balance_sheet_line_items(
                text
            )

    else:
        fields = _extract_generic(text)

        line_items = _extract_financial_line_items(
            text,
            detected_type
        )

    tables = _extract_tables(text)

    return {
        "document_type":detected_type,
        "fields":fields,
        "line_items":line_items,
        "tables":tables,
        "raw_text_by_page":pages
    }