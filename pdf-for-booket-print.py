import os
import sys
import fitz


def create_tmp_pdf(file_path: str) -> str:
    """
    Creates a temporary PDF file with n (number of pages) multiple of 4 or
    n % 4 == 0.
    If the PDF already has n % 4 == 0, the temporary file will be identical
    to the original. If it isn't, blank* pages will be added until n % 4 == 0.
    *An invisible text (white on white) is added in order to avoid empty page
    error when applying Document.select() method booklet page setup.

    Args:
        - file_path: path to PDF file to process

    Returns:
        - tmp_filepath: path to tmp PDF file created
    """
    doc = fitz.open(file_path)

    while doc.page_count % 4 != 0:
        doc.insert_page(-1, "copyright Jun Suzuki - 2022", color=1)

    tmp_filepath = file_path.split(".pdf")[0] + "_tmp.pdf"
    doc.save(tmp_filepath)

    return tmp_filepath


def reorder_pages(file_path: str) -> list:
    """
    Reorders pages for booklet print (2 pages / A4).

    Args:
        - file_path: path to PDF file to process

    Returns:
        - list of tuples of 4 integers :
            - idx_fbtm : index of front bottom page
            - idx_ftop : index of front top page
            - idx_btop : index of back top page
            - idx bbtm : index of back bottom page
    """

    doc = fitz.open(file_path)

    pages = [i for i in range(doc.page_count)]
    new_order = []

    while len(pages) > 0:
        new_order.append((pages.pop(-1), pages.pop(0), pages.pop(0), pages.pop(-1)))

    return new_order


def create_pdf_for_booklet_print(file_path: str, new_order: list) -> None:
    """
    Creates a new PDF for a double-sided booklet print from a PDF with n
    (number of pages) multiple of 4. The new PDF has one front page containing
    2 original pages and a back page containing 2 original pages.

    Args:
        - file_path: path to PDF file to process
    """

    new_doc = fitz.open()

    for idx_fbtm, idx_ftop, idx_btop, idx_bbtm in new_order:

        """Generating front page"""
        front = new_doc.new_page()

        front_top = fitz.Rect(0, 0, front.rect.width, front.rect.height / 2)
        front_btm = front_top + (0, front.rect.height / 2, 0, front.rect.height / 2)

        ftop = fitz.open(file_path)
        ftop.select([idx_ftop, idx_ftop + 1])
        front.show_pdf_page(front_top, ftop, 0, rotate=90)

        fbtm = fitz.open(file_path)
        if idx_fbtm < fbtm.page_count - 1:
            fbtm.select([idx_fbtm, idx_fbtm + 1])
        else:
            fbtm.select(
                [
                    idx_fbtm,
                ]
            )
        front.show_pdf_page(front_btm, fbtm, 0, rotate=90)

        """ Generating back page
        """
        back = new_doc.new_page()

        back_top = fitz.Rect(0, 0, back.rect.width, back.rect.height / 2)
        back_btm = back_top + (0, back.rect.height / 2, 0, back.rect.height / 2)

        btop = fitz.open(file_path)
        btop.select([idx_btop, idx_btop + 1])
        back.show_pdf_page(back_top, btop, 0, rotate=270)

        bbtm = fitz.open(file_path)
        bbtm.select([idx_bbtm, idx_bbtm + 1])
        back.show_pdf_page(back_btm, bbtm, 0, rotate=270)

    output_file = file_path.replace("_tmp.pdf", "_booklet.pdf")
    new_doc.save(output_file)


def generate_booklet_layout(file_path: str) -> None:
    """
    Main function calling sub methods one by one :
    1. Creation of a temporary normalised PDF
    2. Generation of a new page order for double-pages A4
    3. Creation of the final PDF for booklet print

    Args:
        - file_path: path to PDF file to process
    """

    tmp_filepath = create_tmp_pdf(file_path)
    new_order = reorder_pages(tmp_filepath)
    create_pdf_for_booklet_print(tmp_filepath, new_order)

    """ Delete temporary file
    """
    os.remove(tmp_filepath)


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Error: specify PDF file path as an argument.")
    elif len(sys.argv) > 2:
        print("Error: too many arguments have been passed. One is needed (file path).")
    else:
        generate_booklet_layout(sys.argv[1])
