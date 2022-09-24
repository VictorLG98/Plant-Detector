import tkinter
import requests
import json
from dotenv import load_dotenv
import os
from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox
# from serpapi import GoogleSearch
from PIL import ImageTk, Image
from threading import Thread
from fpdf import FPDF
from datetime import datetime
import wikipedia

load_dotenv()
wikipedia.set_lang('es')

class PlantClassificatorUI:

    def __init__(self) -> None:
        self.API_KEY = os.environ["API_KEY"]
        self.window = tkinter.Tk()
        self.window.title("Plant Detector 1.0")
        self.window.resizable(False, False)
        self.window.config(padx=100, pady=100, background='#17ED4F')

        self.select_imgs = Button(
            text="Choose plant", command=self.threading, font=('Arial', 20, 'bold'), highlightthickness=0, 
            background='#17ED4F', borderwidth=0, activebackground='#00FA4C', justify=CENTER)
        self.select_imgs.grid(row=1, column=0, columnspan=2)
        
        self.result_label = Label(text="", font=("Helvetica", 12, "bold"), background='#17ED4F')
        self.result_label.grid(row=2, column=0, columnspan=2)
        
        self.cannonical_Name = None
        
        self.label1 = Label()

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
        
        if plant_images:
            if len(plant_images) > 2:
                messagebox.showinfo(
                    title="Atención!", message="Debes seleccionar un máximo de dos imágenes!")
            else:
                return plant_images
        else:
            self.select_imgs.config(state=ACTIVE, text="Choose plant")
            

    def detect_plant(self):
        plants_imgs = self.select_plant_imgs()
            
        if plants_imgs:
            api_endpoint = f"https://my-api.plantnet.org/v2/identify/all?api-key={self.API_KEY}"
            
            image1 = Image.open(plants_imgs[0])
            image1 = image1.resize((300, 300), Image.ANTIALIAS)
            test = ImageTk.PhotoImage(image1)
            self.label1 = tkinter.Label(image=test, borderwidth=0, highlightthickness=0)
            self.label1.image = test
            self.label1.grid(row=0, column=0, padx=10)

            if len(plants_imgs) == 2:
                organs = ['flower', 'leaf']
            else:
                organs = ['leaf']

            images2 = []
            for img in plants_imgs:
                image_path_1 = img
                image_data_1 = open(image_path_1, 'rb')
                images2.append(('images', (image_path_1, image_data_1)))

            data = {
                'organs': organs
            }

            params = {
                'lang': 'es'
            }

            files = images2
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
                result1_accuracy = json_result.get('results')[0].get('score')
                
                self.result_label.config(text=f"Best match is '{bestMatch}' with {result1_accuracy * 100}% score.")
                # images = self.serpapi_get_google_images(bestMatch.split(" ")[0])
                remainingRequests = json_result.get(
                    'remainingIdentificationRequests')

                print(
                    f"Best Match: {bestMatch}\nPuedes identificar {remainingRequests} plantas más!")
                # print(f"Similar images: {images}")
                
                pdf = FPDF('P', 'mm', 'Letter')
                
                num = 120
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
                    self.cannonical_Name = json_result_2.get('canonicalName')
                    accuracyScore = round(res.get('score') * 100, 2)
                    commonNames = res.get('species').get('commonNames')
                    scientificName = res.get('species').get('scientificName')
                    scientificAuthor = res.get('species').get(
                        'scientificNameAuthorship')
                    
                    if n == 1:
                        similar_images = self.get_wiki_images(self.cannonical_Name)
                        print(f"Similar images: {similar_images}")
                        self.get_wiki_info(self.cannonical_Name)
                    
                    pdf.add_page()

                    pdf.set_font('helvetica', '', 14)

                    pdf.cell(num, 10, f'Result {n}:', ln=True)
                    pdf.cell(num, 10, f'- Gbif code: {gbifCode}', ln=True)
                    pdf.cell(num, 10, f'- Precission score: {res.get("score")} ({accuracyScore}%)', ln=True)
                    pdf.cell(num, 10, f'- Common names: {commonNames}', ln=True)
                    pdf.cell(num, 10, f'- Cannonical name: {self.cannonical_Name}', ln=True)
                    pdf.cell(num, 10, f'- Scientific name: {scientificName}', ln=True)
                    pdf.cell(num, 10, f'- Species: {species}', ln=True)
                    pdf.cell(num, 10, f'- Family: {family}', ln=True)
                    pdf.cell(num, 10, f'- Kingdom: {kingdom}', ln=True)
                    pdf.cell(num, 10, f'- Author: {scientificAuthor}', ln=True)
                    
                    num -= 20

                yn = messagebox.askyesno(title="Download PDF?", message="Do you want to download a PDF with more results?")
                if yn:
                    pdf.output(f'Plant_{gbifCode}_{bestMatch}_{datetime.now().strftime("%Y-%m-%d")}.pdf')
                    messagebox.showinfo(title="Info", message="Pdf report created succesfully!")
                else:
                    pass
                self.select_imgs.config(state=ACTIVE, text="Choose plant")
                
    def get_wiki_images(self, plant_name):
        
        images = wikipedia.page(plant_name).images
        
        final_images = []
        for img in images:
            if img.endswith('.jpg') or img.endswith('.jpeg'):
                final_images.append(img)  
            else:
                pass
        
        return final_images
    
    def get_wiki_info(self, plant_name):
        summary = wikipedia.summary(plant_name)
        title = wikipedia.page(plant_name).title
        
        messagebox.showinfo(title=f"Wiki '{title}' info", message=summary)
        
                  
    # def serpapi_get_google_images(self, query):
    #     image_results = []

    #     # search query parameters
    #     params = {
    #         # search engine. Google, Bing, Yahoo, Naver, Baidu...
    #         "engine": "google",
    #         "q": query,                       # search query
    #         "tbm": "isch",                    # image results
    #         "num": "20",                     # number of images per page
    #         # page number: 0 -> first page, 1 -> second...
    #         "ijn": 0,
    #         # your serpapi api key
    #         "api_key": os.environ["API_KEY2"]
    #         # other query parameters: hl (lang), gl (country), etc
    #     }

    #     # where data extraction happens
    #     search = GoogleSearch(params)

    #     image_results = []
    #     results = search.get_dict()
    #     # checks for "Google hasn't returned any results for this query."
    #     try:
    #         if "error" not in results:
    #             for image in results["images_results"]:
    #                 if image["original"] not in image_results:
    #                     image_results.append(image["original"])
    #     except KeyError:
    #         print("No se han encontrado imágenes similares...")
    #     else:
    #         return image_results[0:5]
        
    # def threading(self): 
    #     self.disable_button()
    
    #     t1=Thread(target=self.detect_plant) 
    #     t1.start()        
        
    # def disable_button(self):
    #     self.select_imgs.config(state=DISABLED, text="Loading...")


if __name__ == "__main__":
    PC = PlantClassificatorUI()
