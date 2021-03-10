from .models import Tool
from barcode import EAN13
from barcode.writer import ImageWriter
import os
import cv2
import numpy as np
class Sheet:

    # One sheet contains a number of barcodes to print and their respecitve count

    ids = []

    def __str__(self):
        pass
    # export the sheets barcode
    def export(self):
        os.system("mkdir barcodes")
        x_images = 0
        y_images = 0
        pages = 0
        stiched = None
        stiched_row = None
        print(len(self.ids))
        for tool in self.ids:
            with open("barcodes/" + str(tool[0]) + ".png", 'wb') as f:
                print(str(tool[0]))
                print(EAN13())
                EAN13(str(tool[0]), writer=ImageWriter()).write(f)

            image = cv2.imread("barcodes/" + str(tool[0]) + ".png")
            cv2.putText(image, tool[1] + " " + tool[2] + " von " + tool[3], (90, 220),
                        cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 0), 2)
            if x_images == 0:
                print(x_images, y_images, "start")
                stiched_row = image
                x_images += 1
            elif x_images%4 != 0:
                print(x_images, y_images,"add row")
                stiched_row = np.concatenate((stiched_row, image), axis=1)
                x_images += 1
            elif x_images%4 == 0 and x_images != 0:
                print(x_images, y_images,"end row")
                if y_images == 0:
                    print("first row")
                    stiched = stiched_row
                    y_images += 1


                elif y_images == 11:
                    print(x_images, y_images,"page finished")
                    cv2.imwrite("barcodes/page" + str(pages) + ".png", stiched)
                    y_images = 0
                else:
                    print(x_images, y_images,"next row")
                    stiched = np.concatenate((stiched, stiched_row), axis=0)
                    y_images += 1
                stiched_row = None
                x_images = 0

            #cv2.imwrite("barcodes/" + str(tool[0]) + ".png", image)




        #os.system("rm -r barcodes")
    def add_tool(self, id):
        tool = Tool.objects.get(id=id)
        for n in range(tool.available_amount):
            self.ids.append([tool.id, tool.name, tool.model, tool.owner.username])

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

