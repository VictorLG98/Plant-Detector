import tkinter
import requests
import json
from pprint import pprint
from dotenv import load_dotenv
import os
from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox

load_dotenv()


class PlantClassificatorUI:

    def __init__(self) -> None:
        self.API_KEY = os.environ["API_KEY"]
        self.window = tkinter.Tk()
        self.window.title("Plant Detector 1.0")
        self.window.resizable(False, False)
        self.window.config(padx=200, pady=200, background='green')

        self.select_imgs = Button(
            text="Select plant images", command=self.detect_plant)
        self.select_imgs.grid(row=0, column=0)

        self.window.mainloop()

    def select_plant_imgs(self):
        filetypes = (
            ('JPG', '*.jpg'),
            ('JPEG', '*.jpeg'),
            ('PNG', '*.png')
        )

        filenames = fd.askopenfilenames(
            title="Select images", filetypes=filetypes, initialdir="/")
        plant_images = list(filenames)
        if len(plant_images) > 2:
            messagebox.showinfo(
                title="Atención!", message="Debes seleccionar un máximo de dos imágenes!")
        else:
            return plant_images

    def detect_plant(self):
        plants_imgs = self.select_plant_imgs()
        if plants_imgs:
            api_endpoint = f"https://my-api.plantnet.org/v2/identify/all?api-key={self.API_KEY}"

            if len(plants_imgs) == 2:
                organs = ['flower', 'leaf']
            else:
                organs = ['leaf']

            images = []
            for img in plants_imgs:
                image_path_1 = img
                image_data_1 = open(image_path_1, 'rb')
                images.append(('images', (image_path_1, image_data_1)))

            data = {
                'organs': organs
            }

            files = images
            req = requests.Request('POST', url=api_endpoint,
                                   files=files, data=data)

            prepared = req.prepare()

            s = requests.Session()
            response = s.send(prepared)
            if response.status_code != 200:
                print(response.text)
                messagebox.showerror(
                    message="No se ha identificado ninguna planta... Prueba con otra imagen", title="Error!")
            else:
                json_result = json.loads(response.text)
                pprint(json_result)


if __name__ == "__main__":
    PC = PlantClassificatorUI()
