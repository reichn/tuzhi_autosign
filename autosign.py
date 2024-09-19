from pathlib import Path
from datetime import datetime
import fitz  # PyMuPDF
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


def get_pdf_page_size(pdf_path, page_number=1):
    with fitz.open(pdf_path) as doc:
        page = doc[page_number - 1]
        return (round(page.rect.width), round(page.rect.height))


def extract_text_with_coordinates(pdf_path, word):
    with fitz.open(pdf_path) as doc:
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


def add_image_and_text_to_pdf_page(
    pdf_path, image_path, page_number, sign_position, output_path
):
    page_size = get_pdf_page_size(pdf_path, page_number + 1)

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=page_size)

    if sign_position:
        x0, y0, _, _ = sign_position
        x0 += 30
        y0 = page_size[1] - y0  # Adjust for ReportLab's coordinate system
    else:
        x0, y0 = 100, 100  # Default position if sign_position is None

    can.drawImage(image_path, x0, y0 - 15, width=25, height=15)

    today = datetime.today().date().strftime(r"%Y%m%d")
    can.setFont("Helvetica", 10)
    can.drawString(x0 + 30, y0 - 10, today)

    can.save()
    packet.seek(0)

    # Merge with original PDF using PyMuPDF
    pdf_document = fitz.open(pdf_path)
    new_page = pdf_document[page_number]
    new_pdf = fitz.open("pdf", packet.getvalue())
    new_page.show_pdf_page(new_page.rect, new_pdf, 0)
    pdf_document.save(output_path)
    pdf_document.close()


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
    pdf_document = fitz.open(input_pdf)
    new_page = pdf_document[page_number]
    new_pdf = fitz.open("pdf", packet.getvalue())
    new_page.show_pdf_page(new_page.rect, new_pdf, 0)
    pdf_document.save(output_pdf)
    pdf_document.close()

    print(
        f"Added {svg_file} to {output_pdf} at position ({x}, {y}) with size ({width}, {height})"
    )


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


if __name__ == "__main__":
    file1_path = "a2.pdf"
    file1_h, file1_w = get_pdf_page_size(file1_path)
    tuzhi1 = Tuzhi(file1_h, file1_w, file1_path)

    print(tuzhi1)
    print(tuzhi1.path)
    print(tuzhi1.size)

    tuzhi1_sign_position = get_word_positions(tuzhi1.path, "设计")
    resize_image("sign_demo_3.png", "sign_demo_resized.png", (50, 30))

    add_image_and_text_to_pdf_page(
        tuzhi1.path, r"sign_demo_resized.png", 0, tuzhi1_sign_position, "a2_sign.pdf"
    )

    add_svg_to_pdf(tuzhi1.path, "sign_svg.svg", "a2_sign.pdf", 0, 500, 300, 350, 230)
