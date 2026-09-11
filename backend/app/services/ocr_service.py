import os
import time
from pathlib import Path
from typing import Dict,List

os.environ["FLAGS_use_onednn"]="0"
os.environ["FLAGS_enable_pir_api"]="0"
os.environ["FLAGS_use_mkldnn"]="0"
os.environ["FLAGS_paddle_num_threads"]="4"
os.environ["OMP_NUM_THREADS"]="4"
os.environ["MKL_NUM_THREADS"]="4"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"]="True"

from PIL import Image
from pypdf import PdfReader
from paddleocr import PaddleOCR

ocr=PaddleOCR(
    device="cpu",
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    enable_mkldnn=False,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    text_det_limit_side_len=640
)

IMAGE_EXTENSIONS={
    ".jpg",
    ".jpeg",
    ".png"
}

PDF_EXTENSIONS={
    ".pdf"
}

MAX_IMAGE_SIZE=640
PDF_DPI=72


def _get_page_lines(result)->List[str]:
    lines=[]

    if result is None:
        return lines

    if isinstance(result,list):
        for item in result:
            lines.extend(_get_page_lines(item))
        return lines

    if isinstance(result,dict):
        rec_texts=result.get("rec_texts")

        if isinstance(rec_texts,list):
            for value in rec_texts:
                text=str(value).strip()

                if text:
                    lines.append(text)

        text=result.get("text")

        if isinstance(text,str) and text.strip():
            lines.append(text.strip())

        return lines

    rec_texts=getattr(
        result,
        "rec_texts",
        None
    )

    if isinstance(rec_texts,list):
        for value in rec_texts:
            text=str(value).strip()

            if text:
                lines.append(text)

    text=getattr(
        result,
        "text",
        None
    )

    if isinstance(text,str) and text.strip():
        lines.append(text.strip())

    return lines


def _prepare_image(source_path:str)->str:
    source=Path(source_path)

    prepared=source.with_name(
        f"{source.stem}_ocr.jpg"
    )

    started=time.perf_counter()

    with Image.open(source) as image:
        image=image.convert("RGB")

        width,height=image.size

        maximum=max(
            width,
            height
        )

        if maximum>MAX_IMAGE_SIZE:
            scale=MAX_IMAGE_SIZE/maximum

            width=max(
                1,
                int(width*scale)
            )

            height=max(
                1,
                int(height*scale)
            )

            image=image.resize(
                (width,height),
                Image.Resampling.BILINEAR
            )

        image.save(
            prepared,
            "JPEG",
            quality=60,
            optimize=False
        )

    elapsed=int(
        (time.perf_counter()-started)*1000
    )

    print(
        f"OCR image preparation completed: {elapsed} ms",
        flush=True
    )

    print(
        f"OCR image final size: {width}x{height}",
        flush=True
    )

    return str(prepared)


def _run_prediction(source_path:str):
    started=time.perf_counter()

    print(
        f"PaddleOCR prediction input: {source_path}",
        flush=True
    )

    result=ocr.predict(
        source_path
    )

    elapsed=int(
        (time.perf_counter()-started)*1000
    )

    print(
        f"PaddleOCR prediction completed: {elapsed} ms",
        flush=True
    )

    return result


def _process_image(source_path:str)->Dict[str,str]:
    started=time.perf_counter()

    print(
        f"OCR image started: {source_path}",
        flush=True
    )

    prepared_path=_prepare_image(
        source_path
    )

    try:
        result=_run_prediction(
            prepared_path
        )

        lines=_get_page_lines(
            result
        )

        print(
            f"OCR detected lines: {len(lines)}",
            flush=True
        )

        text="\n".join(lines)

        total_time=int(
            (time.perf_counter()-started)*1000
        )

        print(
            f"OCR image completed: {total_time} ms",
            flush=True
        )

        return {
            "1":text
        }

    finally:
        try:
            Path(prepared_path).unlink(
                missing_ok=True
            )
        except Exception:
            pass


def _pdf_to_image(
    pdf_path:str,
    page_number:int
)->str:
    import pymupdf

    started=time.perf_counter()

    pdf=pymupdf.open(
        pdf_path
    )

    try:
        page=pdf.load_page(
            page_number
        )

        zoom=PDF_DPI/72

        matrix=pymupdf.Matrix(
            zoom,
            zoom
        )

        pixmap=page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        output_path=Path(
            pdf_path
        ).with_name(
            f"{Path(pdf_path).stem}_page_{page_number+1}_ocr.jpg"
        )

        pixmap.save(
            str(output_path)
        )

        elapsed=int(
            (time.perf_counter()-started)*1000
        )

        print(
            f"PDF page rendering completed: {elapsed} ms",
            flush=True
        )

        return str(output_path)

    finally:
        pdf.close()


def _process_pdf(source_path:str)->Dict[str,str]:
    started=time.perf_counter()

    print(
        f"OCR PDF started: {source_path}",
        flush=True
    )

    reader=PdfReader(
        source_path
    )

    page_count=len(
        reader.pages
    )

    print(
        f"OCR PDF page count: {page_count}",
        flush=True
    )

    pages={}

    for page_number in range(page_count):
        page_started=time.perf_counter()

        print(
            f"OCR PDF page {page_number+1}/{page_count} started",
            flush=True
        )

        image_path=None
        prepared_path=None

        try:
            image_path=_pdf_to_image(
                source_path,
                page_number
            )

            prepared_path=_prepare_image(
                image_path
            )

            result=_run_prediction(
                prepared_path
            )

            lines=_get_page_lines(
                result
            )

            pages[
                str(page_number+1)
            ]="\n".join(lines)

            print(
                f"OCR detected lines on page {page_number+1}: {len(lines)}",
                flush=True
            )

            page_time=int(
                (
                    time.perf_counter()-
                    page_started
                )*1000
            )

            print(
                f"OCR PDF page {page_number+1} completed: {page_time} ms",
                flush=True
            )

        finally:
            if image_path:
                try:
                    Path(image_path).unlink(
                        missing_ok=True
                    )
                except Exception:
                    pass

            if prepared_path:
                try:
                    Path(prepared_path).unlink(
                        missing_ok=True
                    )
                except Exception:
                    pass

    total_time=int(
        (
            time.perf_counter()-
            started
        )*1000
    )

    print(
        f"OCR PDF completed: {total_time} ms",
        flush=True
    )

    print(
        f"OCR pages processed: {len(pages)}",
        flush=True
    )

    return pages


def _ocr_source(
    source_path:str
)->Dict[str,str]:

    suffix=Path(
        source_path
    ).suffix.lower()

    if suffix in IMAGE_EXTENSIONS:
        return _process_image(
            source_path
        )

    if suffix in PDF_EXTENSIONS:
        return _process_pdf(
            source_path
        )

    raise ValueError(
        "Unsupported file format: "
        f"{suffix}. Supported formats are PDF, JPG and PNG."
    )


def extract_text(
    source_path:str
)->Dict[str,str]:

    started=time.perf_counter()

    print(
        f"OCR extraction started: {source_path}",
        flush=True
    )

    result=_ocr_source(
        source_path
    )

    elapsed=int(
        (
            time.perf_counter()-
            started
        )*1000
    )

    print(
        f"OCR extraction completed: {elapsed} ms",
        flush=True
    )

    print(
        f"OCR extracted pages: {len(result)}",
        flush=True
    )

    return result