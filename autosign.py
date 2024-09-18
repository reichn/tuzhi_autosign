import fitz
from pathlib import Path


class Tuzhi(object):
    def __init__(self, h=0, w=0, path=""):
        self._h = h
        self._w = w
        self._path = path
        self._category = ""
        self.set_category()

    @property
    def size(self):
        return self._h, self._w

    @property
    def path(self):
        return self._path

    @property
    def category(self):
        return self._category

    @path.setter
    def path(self, path):
        self._path = path

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
    try:
        # 打开PDF文件
        pdf_document = fitz.open(pdf_path)

        # 获取指定页面
        page = pdf_document[page_number - 1]  # 页面索引从0开始，所以要减1

        # 获取页面大小
        page_size = round(page.rect.height), round(page.rect.width)

        return page_size

    except Exception as e:
        print(f"Error: {e}")
        return None


def extract_text_with_coordinates(pdf_path, word):
    # 打开 PDF 文件
    document = fitz.open(pdf_path)

    all_text_data = []

    # 遍历每一页
    for page_num in range(len(document)):
        # 获取页面对象
        page = document.load_page(page_num)

        # 获取页面上的所有文本块及其坐标信息
        text_dict = page.get_text("dict")

        # 提取文本块及其坐标
        for block in text_dict["blocks"]:
            if block["type"] == 0:  # 0 表示文本块
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        bbox = span["bbox"]  # (x0, y0, x1, y1) 表示文本块的边界框
                        all_text_data.append(
                            {
                                "page": page_num + 1,  # 页码从 1 开始
                                "text": text,
                                "bbox": bbox,
                            }
                        )

    # 关闭文档
    document.close()

    out = [item for item in all_text_data if item["text"] == word]
    return out


def get_word_positions(pdf_path):

    text_data = extract_text_with_coordinates(pdf_path, "设计")

    for item in text_data:
        print(f"Page {item['page']}: Text: '{item['text']}', BBox: {item['bbox']}")


def add_image_to_pdf_page(pdf_path, image_path, page_number, output_path):
    # 打开现有的 PDF 文件
    pdf_document = fitz.open(pdf_path)

    # 打开指定的页面（page_number 从 0 开始）
    page = pdf_document.load_page(page_number)

    # 定义图片的位置和尺寸 (x0, y0, x1, y1)
    x0 = 100  # 图片的左上角 x 坐标
    y0 = 500  # 图片的左上角 y 坐标
    x1 = x0 + 400  # 图片的右下角 x 坐标 (宽度为 400)
    y1 = y0 + 300  # 图片的右下角 y 坐标 (高度为 300)

    # 在页面上添加图片
    page.insert_image(fitz.Rect(x0, y0, x1, y1), filename=image_path)

    # 保存修改后的 PDF 文件
    pdf_document.save(output_path)
    pdf_document.close()


if __name__ == "__main__":
    file1_path = "a2.pdf"
    file1_h, file1_w = get_pdf_page_size(file1_path)
    tuzhi1 = Tuzhi(file1_h, file1_w, file1_path)

    print(tuzhi1)
    print(tuzhi1.path)
    print(tuzhi1.size)
