from .models import Tool
from barcode import EAN13
from barcode.writer import ImageWriter
from PIL import Image, ImageFont, ImageDraw
import os
import numpy as np
import wget


class Sheet:

    ids = []

    def __str__(self):
        pass

    def export(self):
        os.system("mkdir barcodes")
        x_images = 0
        y_images = 0
        pages = 0
        stiched = None
        stiched_row = None

        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 20)

        for tool in self.ids:

            with open("barcodes/" + str(tool[0]) + ".png", 'wb') as f:
                EAN13(str(tool[0]), writer=ImageWriter()).write(f)

            image = Image.open("barcodes/" + str(tool[0]) + ".png")

            d_con = ImageDraw.Draw(image)
            d_con.multiline_text((80,200), tool[1] + " " + tool[2], font=fnt,fill=(0, 0, 0))
            d_con.multiline_text((80,225), tool[3] + " / " + tool[4], font=fnt, fill=(0, 0, 0))

            if x_images == 0:
                stiched_row = image
                x_images += 1
            elif x_images%4 != 0:
                stiched_row = np.concatenate((stiched_row, image), axis=1)
                x_images += 1
            elif x_images%4 == 0 and x_images != 0:
                if y_images == 0:
                    stiched = stiched_row
                    y_images += 1

                elif y_images == 11:
                    im = Image.fromarray(stiched)
                    im.save("page" + str(pages) + ".png","PNG")
                    y_images = 0
                else:
                    stiched = np.concatenate((stiched, stiched_row), axis=0)
                    y_images += 1
                stiched_row = None
                x_images = 0

        os.system("rm -r barcodes")

    def add_tool(self, id):
        tool = Tool.objects.get(id=id)
        for n in range(tool.available_amount):
            self.ids.append([tool.id, tool.name, tool.brand, tool.model, tool.owner.username])

    def list(self):
        for id in self.ids:
            print(id)


def fix_ids_to_EAN13():
    tools = Tool.objects.all()
    for tool in tools:
        if len(str(tool.id)) == 13:
            tool.delete()

            #prev = tool.id
            #tool.id = int(str(tool.id)[1:])
            #print(str(tool), prev, "-->", tool.id)
            #tool.save()
            #print(tool.id)

def download_scale_toolicon(toolid, link):

    path = os.path.abspath(os.path.dirname(__file__))
    path = path.split("/")

    path.pop(-1)
    path_new = '/'.join([str(item) for item in path])

    try:
        image_filename = wget.download(link)
    except Exception as e:

        return False, str(e)

    name = str(toolid) + ".jpg"
    im = Image.open(image_filename)
    im.thumbnail((60, 60), Image.ANTIALIAS)

    os.system("rm " + image_filename)
    impath = os.path.join(path_new, "static", "img", "tool_icons", name)

    im.save(impath, "JPEG")

    return True, name