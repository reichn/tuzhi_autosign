from pathlib import Path
from datetime import datetime

# import fitz  # PyMuPDF
import pymupdf
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from svglib.svglib import svg2rlg
import io
from PIL import Image


class Tuzhi(object):
    def __init__(self, h=0, w=0, path="", name=""):
        self._h = h
        self._w = w
        self._path = path
        self._name = name
        self._category = ""
        self.set_category()

    @property
    def size(self):
        return self._h, self._w

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self.name

    @property
    def category(self):
        return self._category

    @path.setter
    def path(self, path):
        self._path = path

    @name.setter
    def name(self, name):
        self._name = name

    def set_category(self):
        if self._h > self._w:
            self._category = "A4h"
        else:
            if self._h == 2384 and self._w == 3370:
                self._category = "A0"
            if self._h == 1684 and self._w == 2384:
                self._category = "A1"
            if self._h == 1191 and self._w == 1684:
                self._category = "A2"
            if self._h == 842 and self._w == 1191:
                self._category = "A3"
            if self._h == 595 and self._w == 842:
                self._category = "A4"

    def __str__(self):
        return self._category


def get_pdf_page_size(pdf_path, page_number=1):
    with pymupdf.open(pdf_path) as doc:
        page = doc[page_number - 1]
        return (round(page.rect.width), round(page.rect.height))


def extract_text_with_coordinates(pdf_path, word):
    with pymupdf.open(pdf_path) as doc:
        all_text_data = []
        for page_num, page in enumerate(doc):
            text_instances = page.search_for(word)
            for inst in text_instances:
                all_text_data.append({"page": page_num + 1, "text": word, "bbox": inst})
    return all_text_data


def get_word_positions(pdf_path, word):
    text_data = extract_text_with_coordinates(pdf_path, word)
    for item in text_data:
        print(f"Page {item['page']}: Text: '{item['text']}', BBox: {item['bbox']}")
    return text_data[0]["bbox"] if text_data else None


def resize_image(input_path, output_path, size):
    with Image.open(input_path) as img:
        img_resized = img.resize(size)
        img_resized.save(output_path, quality=95)


def add_text_to_pdf_page(pdf_path, page_number, text_position, output_path):
    # Open the existing PDF
    pdf_document = pymupdf.open(pdf_path)
    page = pdf_document[page_number]

    # Register the custom font
    font_path = "hyswlongfangsong.ttf"  # Make sure this path is correct
    font_name = "HYFS"

    # Load the font file
    with open(font_path, "rb") as font_file:
        font_buffer = font_file.read()

    # Insert the font into the PDF
    page.insert_font(fontbuffer=font_buffer, fontname=font_name)

    if text_position:
        x0, y0, _, _ = text_position
        x0 += 30
    else:
        x0, y0 = 100, 100  # Default position if text_position is None

    today = datetime.today().date().strftime(r"%Y%m%d")

    # Insert text directly to the page
    x0 = 300
    y0 = 300
    page.insert_text((x0, y0), today, fontname=font_name, fontsize=24)

    # Save the modified PDF
    pdf_document.save(output_path)
    pdf_document.close()

    print(f"Added text '{today}' to {output_path} at position ({x0}, {y0})")


def add_svg_to_pdf(input_pdf, svg_file, output_pdf, page_number, x, y, width, height):
    drawing = svg2rlg(svg_file)

    page_size = get_pdf_page_size(input_pdf, page_number + 1)

    # Calculate scaling factors
    scale_x = width / drawing.width
    scale_y = height / drawing.height

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=page_size)

    # Apply scaling and positioning
    can.saveState()
    can.translate(x, page_size[1] - y - height)
    can.scale(scale_x, scale_y)

    renderPDF.draw(drawing, can, 0, 0)

    can.restoreState()
    can.save()
    packet.seek(0)

    # Merge with original PDF using PyMuPDF
    pdf_document = pymupdf.open(input_pdf)
    new_page = pdf_document[page_number]
    new_pdf = pymupdf.open("pdf", packet.getvalue())
    new_page.show_pdf_page(new_page.rect, new_pdf, 0)
    pdf_document.save(output_pdf)
    pdf_document.close()

    print(
        f"Added {svg_file} to {output_pdf} at position ({x}, {y}) with size ({width}, {height})"
    )


if __name__ == "__main__":
    file1_path = "a2.pdf"
    file1_h, file1_w = get_pdf_page_size(file1_path)
    tuzhi1 = Tuzhi(file1_h, file1_w, file1_path)

    print(tuzhi1)
    print(tuzhi1.path)
    print(tuzhi1.size)

    tuzhi1_sign_position = get_word_positions(tuzhi1.path, "设计")
    resize_image("sign_demo_3.png", "sign_demo_resized.png", (50, 30))

    add_text_to_pdf_page(tuzhi1.path, 0, (100, 100, 100, 100), "a2_sign.pdf")

    # add_svg_to_pdf(tuzhi1.path, "sign_svg.svg", "a2_sign.pdf", 0, 500, 300, 150, 100)
