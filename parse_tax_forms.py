from collections import OrderedDict
import json
import re
import sys

import fitz  # PyMuPDF library


# Define regex patterns to identify all known tax forms.
# We identify a comprehensive set of forms to correctly determine when one
# form ends and another begins, even if we don't include all of them in the final output.
# The keys are compiled regex patterns, and values are the standardized document type.
# (Must be extended for more forms.)
ALL_FORM_PATTERNS = OrderedDict([
    (re.compile(r"SCHEDULE\s+1\s+\(Form\s+1040\)", re.IGNORECASE), "f1040s1"),
    (re.compile(r"SCHEDULE\s+2\s+\(Form\s+1040\)", re.IGNORECASE), "f1040s2"),
    (re.compile(r"SCHEDULE\s+3\s+\(Form\s+1040\)", re.IGNORECASE), "f1040s3"),
    (re.compile(r"SCHEDULE\s+A\s+\(Form\s+1040\)", re.IGNORECASE), "f1040sa"),
    (re.compile(r"SCHEDULE\s+B\s+\(Form\s+1040\)", re.IGNORECASE), "f1040sb"),
    (re.compile(r"SCHEDULE\s+C\s+\(Form\s+1040\)", re.IGNORECASE), "f1040sc"),
    (re.compile(r"SCHEDULE\s+D\s+\(Form\s+1040\)", re.IGNORECASE), "f1040sd"),
    (re.compile(r"SCHEDULE\s+E\s+\(Form\s+1040\)", re.IGNORECASE), "f1040se"),
    (re.compile(r"SCHEDULE\s+8812\s+\(Form\s+1040\)", re.IGNORECASE), "f1040s8812"),
    (re.compile(r"Form\s+1040\b", re.IGNORECASE), "1040f"),
    (re.compile(r"Form\s+8889\b", re.IGNORECASE), "f8889"),
    (re.compile(r"Form\s+8879\b", re.IGNORECASE), "f8879"),
    (re.compile(r"Form\s+1116\b", re.IGNORECASE), "f1116"),
    (re.compile(r"Form\s+4952\b", re.IGNORECASE), "f4952"),
    (re.compile(r"Form\s+8949\b", re.IGNORECASE), "f8949"),
    (re.compile(r"Form\s+8995\b", re.IGNORECASE), "f8995"),
    (re.compile(r"Form\s+8959\b", re.IGNORECASE), "f8959"),
    (re.compile(r"Form\s+8960\b", re.IGNORECASE), "f8960"),
    (re.compile(r"Form\s+8582\b", re.IGNORECASE), "f8582"),
    (re.compile(r"Form\s+8863\b", re.IGNORECASE), "f8863"),
    (re.compile(r"Form\s+8812\b", re.IGNORECASE), "f8812"),
    (re.compile(r"Form\s+2441\b", re.IGNORECASE), "f2441"),
])


def identify_form_on_page(page) -> fitz.Page | None:
    """
    Checks the top-left corner of a PDF page for a known form identifier.

    Args:
        page: A PyMuPDF page object.

    Returns:
        str or None: The document type if found, otherwise None.
    """
    # Define a bounding box for the top-left area to search.
    # Coordinates are (x0, y0, x1, y1). A standard 8.5x11in page is 612x792 points.
    search_rect = fitz.Rect(0, 0, 150, 70) # manually tested this size, works fine for our
    
    # Extract text only from this specific rectangle
    text = page.get_text("text", clip=search_rect)

    # Check the extracted text against our known patterns
    for pattern, doc_type in ALL_FORM_PATTERNS.items():
        if pattern.search(text):
            return doc_type
    return None

def find_tax_forms_in_pdf(pdf_path: str) -> list[dict]:
    """
    Reads a PDF file and builds a pipeline of identified tax forms and their page ranges.
    This version correctly merges consecutive pages of the same form.

    Args:
        pdf_path: The file path to the tax document PDF.

    Returns:
        A list of dictionaries, each representing a found tax form.
    """
    found_forms = []
    current_form = None

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error: Could not open or read PDF file at '{pdf_path}'. Reason: {e}")
        return []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        human_page_num = page_num + 1
        
        form_type = identify_form_on_page(page)
        
        if form_type:
            if current_form is None:
                current_form = {
                    "document_type": form_type,
                    "start_page": human_page_num
                }
            elif form_type != current_form["document_type"]:
                # A different form has started. Finalize the previous one.
                current_form["end_page"] = human_page_num - 1
                found_forms.append(current_form)
                
                # Start tracking the new form.
                current_form = {
                    "document_type": form_type,
                    "start_page": human_page_num
                }
            # If form_type is the same as current_form, do nothing.
            # This correctly treats it as a continuation page.
        
    # After the loop, if a form was being tracked, it ends on the last page.
    if current_form:
        current_form["end_page"] = len(doc)
        found_forms.append(current_form)
        
    return found_forms

def main(pdf_file_path):
    """
    Main function to run the script from the command line.
    """

    # These are the specific document types we would like to check according to description of Task.
    desired_forms = {
        "f1040s1", "f1040s3", "f1040sa", 
        "f1040sb", "f1040sc", "f1040sd", "f1040se", 
        "1040f", "f8889", "f8949"
    }

    all_identified_forms = find_tax_forms_in_pdf(pdf_file_path)

    if not all_identified_forms:
        print("No tax forms could be identified in the document.")
        return

    # Filter the results to include only the forms we're interested in.
    filtered_results = [
        form for form in all_identified_forms 
        if form["document_type"] in desired_forms
    ]
    return filtered_results


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python parse_tax_forms.py <path_to_your_pdf_file.pdf>")
        sys.exit(1)
        
    pdf_file_path = sys.argv[1]
    results = main(pdf_file_path)
    
    # Print the final list as a formatted JSON string.
    print(json.dumps(results, indent=4))