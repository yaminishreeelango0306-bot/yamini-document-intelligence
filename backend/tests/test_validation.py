from app.services.financial_validation_service import validate_invoice, validate_balance_sheet, validate_cash_flow

def f(v): return {"value":v}

def test_invoice_total_pass():
    fields={"subtotal":f(100),"tax_amount":f(10),"discount":f(0),"total_amount":f(110)}
    assert validate_invoice(fields,[])["overall_status"]=="PASS"

def test_balance_sheet_pass():
    fields={"total_assets":f(1000),"total_capital_and_liabilities":f(1000),"total_liabilities":f(600),"total_equity":f(400)}
    assert validate_balance_sheet(fields)["overall_status"]=="PASS"

def test_cash_flow_pass():
    fields={"operating_cash_flow":f(100),"investing_cash_flow":f(-20),"financing_cash_flow":f(10),"fx_adjustment":f(0),
            "net_change_in_cash":f(90),"opening_cash":f(10),"closing_cash":f(100)}
    assert validate_cash_flow(fields)["overall_status"]=="PASS"

