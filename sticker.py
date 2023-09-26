import logging
import tempfile
import subprocess

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

dry_run = False

sticker_size = (70*mm, 54*mm)
margins = 2*mm

(page_width, page_height) = [x - margins*2 for x in sticker_size]

fonts = [
    ('regular', 'CiscoSansTTRegular.ttf'),
    ('bold', 'CiscoSansTTBold.ttf'),
    ('monospace', 'Hack-Regular.ttf'),
]
for (name, path) in fonts:
    pdfmetrics.registerFont(TTFont(name, path))

cisco_logo = ImageReader('cisco-logo.jpg')

class Sticker(object):
    def __init__(self, print_command):
        self.print_command = print_command
        print(f"Stickers will print with: {self.print_command}")

    def create_header(self, c, date, text="V I S I T O R"):
        style = ParagraphStyle('header', fontName='bold', fontSize=12, alignment=TA_CENTER)
        p = Paragraph(f"{text}<br />{date}", style)

        (_, height) = p.wrapOn(c, page_width - margins*2, page_height)
        p.drawOn(c, page_width * 0.23, page_height - height)

        image_oversize = 1.5*mm
        c.drawImage(cisco_logo,
                    0, page_height - height - image_oversize,
                    28*mm, height + image_oversize,
                    preserveAspectRatio=True)

    def create_visitor(self, c, name, company):
        style_name = ParagraphStyle('company', fontName='bold', fontSize=11, alignment=TA_CENTER)
        style_company = ParagraphStyle('name', fontName='regular', fontSize=10, alignment=TA_CENTER)

        placement = 31.0*mm

        p1 = Paragraph(f"{name}", style_name)
        p1.wrapOn(c, page_width, page_height)
        p1.drawOn(c, margins, placement)

        p2 = Paragraph(f"{company}", style_company)
        (_, height) = p2.wrapOn(c, page_width, page_height)
        p2.drawOn(c, margins, placement - height - 0.5*mm)

    def create_visitorinfo(self, c, location, host):
        style_location = ParagraphStyle('location', fontName='regular', fontSize=9, alignment=TA_CENTER)
        style_host = ParagraphStyle('host', fontName='bold', fontSize=9, alignment=TA_CENTER)

        placement = 9.5*mm

        p1 = Paragraph(f"{location}", style_location)
        (_, height) = p1.wrapOn(c, page_width, page_height)
        p1.drawOn(c, margins, placement + height + height)

        p2 = Paragraph(f"HOST: {host}", style_host)
        p2.wrapOn(c, page_width, page_height)
        p2.drawOn(c, margins, placement + height)

    def print_file(self, file):
        try:
            subprocess.check_output(
                [f"{self.print_command} \"{file}\""],
                stderr=subprocess.STDOUT,
                shell=True,
            )
        except Exception as exception:
            raise Exception(exception.output.decode().strip()) from exception # pylint: disable=no-member

    def create(self, data):
        name = data['name'].upper()
        company = data['company'].upper()
        location = data['location'].upper()
        host = data['host'].upper()
        date = data['date']

        with tempfile.NamedTemporaryFile(delete=True) as temp:
            file_name = temp.name
            c = canvas.Canvas(file_name, pagesize=sticker_size)

            self.create_header(c, date)
            self.create_visitor(c, name, company)
            self.create_visitorinfo(c, location, host)

            c.save()
            if not dry_run:
                self.print_file(file_name)
            else:
                import shutil
                logging.warning("dry run: sticker not printed, saved to file")
                shutil.copy(file_name, "sticker.pdf")


if __name__ == "__main__":
    dry_run = True

    sticker = Sticker("lp -d DYMO_LabelWriter_550_Turbo -o landscape")
    sticker.create({
        'name': "Foobar",
        'company': "Binbaz Company Inc",
        'location': "LOCATION 1",
        'host': "Test Host With Long Name",
        'date': "January 19, 2038",
        'email': 'foo@example.com'
    })
