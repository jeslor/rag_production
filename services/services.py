
from pypdf import PdfReader
from pathlib import Path
import fitz
from langchain_core.documents import Document




def ingest_pdf_directory(directory_path: str) -> list[Document]:
    documents = []
    path = Path(directory_path)

    # Track counts for production monitoring
    success_count = 0
    error_count = 0

    for pdf_path in path.glob("**/*.pdf"):
        try:
            reader = PdfReader(pdf_path)
            file_text_extracted = False

            for page_num, page in enumerate(reader.pages):
                # 'plain' layout mode preserves structural text placement
                # similar to how LangChain's internal hooks handle it
                text = page.extract_text(extraction_mode="plain")

                # If plain mode yields nothing, try layout mode as a fallback
                if not text or not text.strip():
                    text = page.extract_text(extraction_mode="layout")

                # Fallback to absolute raw extraction if layout fails
                if not text or not text.strip():
                    text = page.extract_text()

                if text:  # Take whatever text we successfully found
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": str(pdf_path),
                            "file_name": pdf_path.name,
                            "page": page_num + 1
                        }
                    )
                    documents.append(doc)
                    file_text_extracted = True

            if file_text_extracted:
                success_count += 1
            else:
                print(  # This alerts you if a file was read but resulted in 0 text strings
                    f"⚠️ Warning: Loaded '{pdf_path.name}' but extracted 0 characters. Might be scanned/image-only."
                )

        except Exception as e:
            error_count += 1
            print(f"❌ Error processing {pdf_path.name}: {e}")
            continue

    print(f"\n--- Ingestion Summary: Successfully parsed {success_count} PDFs. Failed on {error_count} PDFs. ---")
    return documents

def ingest_pdf_directory_pymupdf(directory_path: str) -> list[Document]:
    documents = []
    path = Path(directory_path)

    success_count = 0

    # Iterate through all PDFS in the data folder or in the company repository.
    for pdf_path in path.glob("**/*.pdf"):
        try:
            # open the document with PYMUPDF (highly resilient for complex layouts)
            doc_object = fitz.open(pdf_path)
            file_has_text = False

            for page_num, page in enumerate(doc_object):
                # "blocks"-> text extraction preserves column reading orders automatically
                text = page.get_text("text")

                # fallback for production grade -> grab whatever layout strings present
                if not text.strip():
                    text = page.get_text("block")

                    # if it is a structured image page, we still keep this object
                    # with a place holder or layout tag for the metadata index
                    if isinstance(text, list):
                        text = "\n".join([b[4] for b in text if isinstance(b, tuple) and len(b) > 4])

                doc = Document(
                    page_content= text if text.strip() else f"[Image page/ Graphic Conent]",
                    metadata={
                        "source": str(pdf_path),
                        "file_name": pdf_path.name,
                        "page": page_num + 1,
                        "total_pages": len(doc_object)
                    }
                )
                documents.append(doc)
                file_has_text = True

            if file_has_text:
                print(f"✅ Successfully ingested: {pdf_path.name} ({len(doc_object)} pages)")
        except Exception as e:
            print(f"❌ Error processing {pdf_path.name}: {e}")
            continue

    print(f"\n--- Processed {success_count} health knowledge assets ---")
    return documents
