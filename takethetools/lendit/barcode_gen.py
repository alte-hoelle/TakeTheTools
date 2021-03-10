from .models import Tool
from barcode import EAN13
from barcode.writer import ImageWriter
import os
import cv2
class Sheet:

    # One sheet contains a number of barcodes to print and their respecitve count

    ids = []
    def __init__(self):
        pass
    def __str__(self):
        pass
    # export the sheets barcode
    def export(self):
        os.system("mkdir barcodes")
        for tool in self.ids:

            with open("barcodes/" + str(tool[0]) + ".png", 'wb') as f:
                EAN13(str(tool[0]), writer=ImageWriter()).write(f)

            image = cv2.imread("barcodes/" + str(tool[0]) + ".png")


            cv2.putText(image, tool[1] + " " + tool[2] + " von " + tool[3], (90, 220), cv2.FONT_HERSHEY_SIMPLEX, .6, (0,0,0), 2)
            cv2.imwrite("barcodes/" + str(tool[0]) + ".png", image)

        #os.system("rm -r barcodes")
    def add_tool(self, id):
        tool = Tool.objects.get(id=id)
        self.ids.append([tool.id, tool.name, tool.model, tool.owner.username])

    def list(self):
        for id in self.ids:
            print(id)
