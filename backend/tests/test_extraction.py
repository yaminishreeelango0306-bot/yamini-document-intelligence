from app.services.extraction_service import extract_document

def test_invoice_extraction():
    text={"1":"INVOICE NO: INV-123\nDATE: March 9, 2022\nSubtotal 100\nSales Tax 10\nTotal Due 110"}
    result=extract_document(text,"invoice")
    assert result["fields"]["invoice_number"]["value"]=="INV-123"
    assert result["fields"]["total_amount"]["value"]==110.0

def test_statement_extraction():
    text={"1":"Interest earned 100\nOther income 20\nTotal 120\nInterest expended 40\nOperating expenses 30\nProvisions and contingencies 10\nTotal 80\nNet profit for the year 40"}
    result=extract_document(text,"profit_and_loss")
    assert result["fields"]["interest_earned"]["value"]==100.0
