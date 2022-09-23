import tkinter
import requests
import json
from dotenv import load_dotenv
import os
from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox
from serpapi import GoogleSearch

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

            params = {
                'lang': 'es'
            }

            files = images
            req = requests.Request('POST', url=api_endpoint,
                                   files=files, data=data, params=params)

            prepared = req.prepare()

            s = requests.Session()
            response = s.send(prepared)
            if response.status_code != 200:
                print(response.text)
                messagebox.showerror(
                    message="No se ha identificado ninguna planta... Prueba con otra imagen", title="Error!")
            else:
                json_result = json.loads(response.text)

                bestMatch = json_result.get('bestMatch')
                images = self.serpapi_get_google_images(bestMatch.split(" ")[0])
                remainingRequests = json_result.get(
                    'remainingIdentificationRequests')

                print(
                    f"Best Match: {bestMatch}\nPuedes identificar {remainingRequests} plantas más!")
                print(f"Similar images: {images}")
                print("Showing first 5 results:")

                for n, res in enumerate(json_result.get('results')[0:5], start=1):
                    gbifCode = res.get('gbif').get('id')
                    response2 = requests.get(
                        f"https://api.gbif.org/v1/species/{gbifCode}")
                    json_result_2 = json.loads(response2.text)
                    response3 = requests.get("https://api.gbif.org/v1/species/{gbifCode}/media")
                    if response3.status_code == 200:
                        json_result_3 = json.loads(response3.text)
                        if json_result_3.get('results'):
                            similar_image = json_result_3.get('results')[0].get('identifier')
                    else:
                        similar_image = None
                            
                    kingdom = json_result_2.get('kingdom')
                    family = json_result_2.get('family')
                    species = json_result_2.get('species')
                    cannonicalName = json_result_2.get('canonicalName')
                    accuracyScore = round(res.get('score') * 100, 2)
                    commonNames = res.get('species').get('commonNames')
                    scientificName = res.get('species').get('scientificName')
                    scientificAuthor = res.get('species').get(
                        'scientificNameAuthorship')
                    print(f"\nResult {n}:")
                    print(f"	- Gbif code: {gbifCode}")
                    print(f"	- Precission score: {res.get('score')} ({accuracyScore}%)")
                    print(f"	- Common names: {commonNames}")
                    print(f"	- Cannonical name: {cannonicalName}")
                    print(f"	- Scientific name: {scientificName}")
                    print(f"	- Species: {species}")
                    print(f"	- Family: {family}")
                    print(f"	- Kingdom: {kingdom}")
                    print(f"	- Author: {scientificAuthor}")
                    print(f"	- Similar images: {similar_image}")

    def serpapi_get_google_images(self, query):
        image_results = []

        # search query parameters
        params = {
            # search engine. Google, Bing, Yahoo, Naver, Baidu...
            "engine": "google",
            "q": query,                       # search query
            "tbm": "isch",                    # image results
            "num": "20",                     # number of images per page
            # page number: 0 -> first page, 1 -> second...
            "ijn": 0,
            # your serpapi api key
            "api_key": os.environ["API_KEY2"]
            # other query parameters: hl (lang), gl (country), etc
        }

        # where data extraction happens
        search = GoogleSearch(params)

        image_results = []
        results = search.get_dict()
        # checks for "Google hasn't returned any results for this query."
        try:
            if "error" not in results:
                for image in results["images_results"]:
                    if image["original"] not in image_results:
                        image_results.append(image["original"])
        except KeyError:
            print("No se han encontrado imágenes similares...")
        else:
            return image_results[0:5]


if __name__ == "__main__":
    PC = PlantClassificatorUI()