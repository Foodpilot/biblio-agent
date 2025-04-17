import fitz  # PyMuPDF
from PIL import Image
import io
import os
import requests
import tempfile


def extract_text_from_pdf(pdf_url):
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/pdf"
    }
    
    # Download the PDF file
    response = requests.get(pdf_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to download PDF: {pdf_url}")

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        tmp_pdf_path = tmp_file.name

    # Open and extract text
    doc = fitz.open(tmp_pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    return text


def extract_text_by_page(pdf_path):
    """Renvoie un dictionnaire {page_num: text}"""
    doc = fitz.open(pdf_path)
    return {i + 1: page.get_text() for i, page in enumerate(doc)}


def extract_images_from_pdf(pdf_path, output_folder="extracted_images"):
    """Extrait toutes les images du PDF et les sauvegarde."""
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    saved_images = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            image_path = os.path.join(output_folder, f"page{page_index + 1}_img{img_index + 1}.{image_ext}")
            image.save(image_path)
            saved_images.append(image_path)
    return saved_images


def build_summary_prompt(user_question, text_sample):
    """Construit un prompt pour envoyer à GPT"""
    return f"""
You are an expert scientific assistant.

The user asked: "{user_question}"

Here is an extract from a scientific paper:
{text_sample[:3000]}  # truncate to stay within token limits

Summarize the main findings, key figures or methods related to the question. Respond clearly and concisely.
"""


def main():
    pdf_path = "https://www.sciencedirect.com/science/article/pii/S2213422014000456/pdfft?md5=3652074e62c88adb1415a2dce80a7c3f&pid=1-s2.0-S2213422014000456-main.pdf"  # Change this to your PDF path
    user_question = "What are the main findings of this paper?"

    # Extract text and images
    full_text = extract_text_from_pdf(pdf_path)
    pages_text = extract_text_by_page(pdf_path)
    images = extract_images_from_pdf(pdf_path)

    # Print extracted text and images
    print("Full Text:\n", full_text)
    print("Pages Text:\n", pages_text)
    print("Extracted Images:\n", images)

    # Build summary prompt
    text_sample = pages_text[1]  # Example: using text from page 1
    summary_prompt = build_summary_prompt(user_question, text_sample)
    print("Summary Prompt:\n", summary_prompt)
    
    
if __name__ == "__main__":
    main()