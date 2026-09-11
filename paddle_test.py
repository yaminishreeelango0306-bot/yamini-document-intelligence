import os

os.environ["FLAGS_enable_pir_api"]="0"

from paddleocr import PaddleOCR

pdf_path=r"C:\Users\yamus\OneDrive\Documents\New Dataset\Balance Sheet\Consolidated Balance Sheet 2019.pdf"

ocr=PaddleOCR(
    lang="en",
    enable_mkldnn=False
)

result=ocr.predict(pdf_path)

for page in result:
    print(page)