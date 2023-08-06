import datetime
import os
import shutil
import fitz
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdfmetrics.registerFont(TTFont('simkai', 'simkai.ttf'))
replaceImagePath = "assets/318D98E1-079B-4B69-93A0-03D064160551/assets/EC4D645224CB4885BEF9235DE3BE670C.png"


def generate_pdf(output_path, text, max_width):
    doc = SimpleDocTemplate(output_path, pagesize=(330*mm, 190*mm))
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.alignment = 1

    para_style = ParagraphStyle(
        name="problem_pdf", style=style, wordWrap="CJK", fontName='simkai', fontSize=40, maxWidth=max_width, leading=40)
    content = Paragraph(text, para_style)

    doc.build([content])


def centerText(pdf, text, font_size=24):
    pdf.setFont("simkai", font_size)
    text_width = pdf.stringWidth(text, "simkai", font_size)
    canvas_width, canvas_height = pdf._pagesize
    x = (canvas_width - text_width) / 2
    y = canvas_height / 2
    pdf.drawString(x, y, text)


def exportImage(pdfPath, imagePath, idx):

    pdfDoc = fitz.open(pdfPath)
    # 只有一页时，直接转换即可
    page = pdfDoc[0]
    rotate = int(0)
    # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
    # 此处若是不做设置，默认图片大小为：792X612, dpi=96
    zoom_x = 1.33333333
    zoom_y = 1.33333333
    mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    if not os.path.exists(imagePath):  # 判断存放图片的文件夹是否存在
        os.makedirs(imagePath)  # 若图片文件夹不存在就创建

    pix.save(imagePath + '/' + 'images_%s.png' % idx)  # 将图片写入指定的文件夹内


if __name__ == "__main__":
    problemListPath = 'problemlist-single.txt'
    chapterName = "NOIP-3-单选"
    problemList = []
    templatePath = "./template"
    imageRoot = './temp/images'
    pdfRoot = "./temp/pdf"
    resultRoot = "./result"

    if not os.path.exists(os.path.join(pdfRoot, chapterName)):
        os.makedirs(os.path.join(pdfRoot, chapterName))

    if not os.path.exists(os.path.join(imageRoot, chapterName)):
        os.makedirs(os.path.join(imageRoot, chapterName))

    if not os.path.exists(os.path.join(resultRoot, chapterName)):
        os.makedirs(os.path.join(resultRoot, chapterName))

    with open(problemListPath, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            problemList.append(line.strip('\n'))

    for i in range(problemList.__len__()):
        print("正在处理第%d题" % (i+1))
        # 将文字转换为pdf
        pdfPath = os.path.join(pdfRoot, chapterName, f"pdf_output_{i}.pdf")
        text = problemList[i]
        generate_pdf(pdfPath, text, max_width=300)

        # 将pdf转换为图片
        imagePath = os.path.join(imageRoot, chapterName)
        exportImage(pdfPath, imagePath, i)

        # 将新的图片替换模板中的图片
        taskDir = os.path.join(resultRoot, chapterName, f"task-{i+1}")
        if os.path.exists(taskDir):
            shutil.rmtree(taskDir)
        shutil.copytree(templatePath, taskDir)
        shutil.copy(os.path.join(imagePath, f"images_{i}.png"),
                    os.path.join(taskDir, replaceImagePath))

        shutil.make_archive(os.path.join(
            resultRoot, chapterName, f"task-{i+1}"), 'zip', taskDir)
        shutil.rmtree(taskDir)

    shutil.rmtree(os.path.join(imageRoot, chapterName))
    shutil.rmtree(os.path.join(pdfRoot, chapterName))
