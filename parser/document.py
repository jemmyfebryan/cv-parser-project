from io import BytesIO
import PyPDF2
import docx2txt

def read_pdf(pdf_file):
    # Create an in-memory file-like object
    # pdf_file = BytesIO(binary_data)

    # Use PyPDF2 to read the PDF content
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    text_content = ''
    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        text_content += page.extract_text()

    return text_content

def read_docx(docx_file):
    # Convert the docx to PDF and write the result to the BytesIO object
    # docx_file = BytesIO(binary_data)

    text_content = docx2txt.process(docx_file)

    return text_content