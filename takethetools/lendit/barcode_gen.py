from .models import Tool
from barcode import EAN13
from barcode.writer import ImageWriter
from PIL import Image, ImageFont, ImageDraw
import os
import numpy as np


class Sheet:

    def __init__(self):
        self.barcodes = []

    def __str__(self):
        pass

    def export(self):
        os.system("rm -r pa*")
        os.system("mkdir barcodes")
        x_images = 0
        y_images = 0
        pages = 0
        stichted = None
        stichted_row = None

        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 20)
        spacer_vert_width = 80
        spacer_vert = Image.new('RGB', (spacer_vert_width, 250), (255, 255, 255))
        top_spacer = Image.new('RGB', (4*523 + 4*spacer_vert_width, 25), (255, 255, 255))
        for tool in self.barcodes:

            with open("barcodes/" + str(tool[0]) + ".png", 'wb') as f:
                EAN13(str(tool[0]), writer=ImageWriter()).write(f)

            image = Image.open("barcodes/" + str(tool[0]) + ".png")
            image = image.crop((0, 30, 523, 280))

            d_con = ImageDraw.Draw(image)
            d_con.multiline_text((80, 165), tool[1] + " " + tool[2], font=fnt, fill=(0, 0, 0))
            d_con.multiline_text((80, 190), tool[3] + " / " + tool[4] + " GV", font=fnt, fill=(0, 0, 0))
            for i in range(tool[-1]):
                if x_images == 0:
                    # if no images in x direction, start a new row
                    stichted_row = np.concatenate((spacer_vert, image), axis=1)

                    x_images += 1
                elif x_images % 4 != 0:
                    # if row has not reached the limit 4 continue adding pictures
                    stichted_row = np.concatenate((stichted_row, spacer_vert, image), axis=1)
                    x_images += 1
                elif x_images % 4 == 0 and x_images != 0:
                    # if line end has been reached decide what to do
                    if y_images == 0:
                        # if no rows are currently present, make the current row the first row
                        stichted = stichted_row
                        y_images += 1

                    elif y_images == 12:
                        # if there are enough rows for a page, save the pdf and start new
                        final = np.concatenate((top_spacer, stichted), axis=0)
                        im = Image.fromarray(final)
                        im.save("pa" + str(pages) + ".pdf", "PDF")
                        y_images = 0
                        pages += 1

                    else:
                        stichted = np.concatenate((stichted, stichted_row), axis=0)
                        y_images += 1
                    stichted_row = None
                    x_images = 0
                if i == tool[-1]-1 and tool == self.barcodes[-1]:
                    # if the last tool of a kind and the last tool in the sheet is reached, save the last pdf,
                    # even if its not complete

                    # add the current row to the page content and fill missing pieces with whitespace
                    whitespace_fill = Image.new('RGB', (stichted.shape[1] -
                                                        stichted_row.shape[1], 250), (255, 255, 255))

                    stichted_row = np.concatenate((stichted_row, whitespace_fill), axis=1)
                    stichted = np.concatenate((stichted, stichted_row), axis=0)
                    # add the current page content to the spacer
                    final = np.concatenate((top_spacer, stichted), axis=0)
                    im = Image.fromarray(final)
                    im.save("pa" + str(pages) + ".pdf", "PDF")
                    y_images = 0

        os.system("rm -r barcodes")

    def add_tool(self, barcode, number):
        try:
            tool = Tool.objects.get(barcode_ean13_no_check_bit=barcode)
        except Exception as e:
            print(e, barcode)
            return

        self.barcodes.append([
                              tool.barcode_ean13_no_check_bit,
                              tool.name,
                              tool.brand,
                              tool.model,
                              tool.owner.username,
                              number
                              ])

    def list(self):
        for barcode in self.barcodes:
            print(barcode)


def fix_ids_to_ean13():
    tools = Tool.objects.all()
    for tool in tools:
        if len(str(tool.id)) == 13:
            tool.delete()
