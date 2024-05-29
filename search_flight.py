#Instalación de librerías necesarias
#pip install lxml
#pip install selenium
#pip install openai

#Librerías para Web Scrapping
from selenium import webdriver
from bs4 import BeautifulSoup
#Librería para IA
from openai import OpenAI
#Librería para sqllite
import sqlite3
#Otras
import re
import time
import datetime
from datetime import datetime



#Elementos de entrada
from_city = input("Flying from: ")
to_city = input("Flying to: ")
day = input("What date (dd/mm/yyyy): ")
web = input("expedia or kayak: ")


#Función de IA que devuelve el código interncacional de un aeropuerto pasando
#por parámetro de entrada el nombre de una ciudad
def get_code_airport(name_city):
   
    client = OpenAI(api_key = "API-KEY",)
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Give me only the airport code of the city"+name_city}
    ]
    )
    return completion.choices[0].message

#Función para insertar en Base de datos
def insert_sqllite3(data):    

    try:
        #Conexión con la Base de Datos creada
        conn = sqlite3.connect("C:/Users/Eva/Documents/sqlite-tools-win-x64-3450300/vuelos.db")
        c = conn.cursor()
        #Insercción de datos
        query = f"INSERT INTO vuelos VALUES (?,?,?,?,?)"
        #Ejecución de la insercción
        c.execute(query, data)
        conn.commit()
        conn.close()

    except Exception:
            print(Exception)
    
    

#Función para buscar vuelos con los elementos de entrada definidos previamente
def search_flight(web,from_loc, to_loc, date):
    from_loc = get_code_airport(from_loc).content
    to_loc = get_code_airport(to_loc).content
    if not web in ['expedia','kayak']:
        return print("No web ok")
    if web =='expedia':
        #URL a la que haremos Web scrapping
        #A la URL se le pasará los elementos de entrada ya que así lo permite
        #url = f"https://www.expedia.ie/Flights-Search?flight-type=on&mode=search&trip=oneway&leg1=from:{from_loc},to:{to_loc},departure:{date},TANYT&passengers=adults:1"
        url = f"https://www.expedia.ie/Flights-Search?flight-type=on&mode=search&trip=oneway&leg1=from%3A{from_loc}%2Cto%3A{to_loc}%2Cdeparture%3A{date}%2CTANYT&passengers=adults%3A01"
        #Pintamos en pantalla información de url
        print(f"URL: {url}")    
        #Llamamos al emulador de Firefox
        driver = webdriver.Firefox()
        driver.get(url)
        #Añadimos tiempo de espera para evitar ser baneados en la medida de lo posible
        time.sleep(15)
        #Se parsea la WEB a texto legible
        soup = BeautifulSoup(driver.page_source, 'lxml')        
        # Obtener todos los datos del sitio web utilizando elementos html y etiquetas.
        airline_name = soup.find_all('h3', attrs={'class': 'uitk-layout-flex-item'})    
        price = soup.find_all('span', attrs={'class': 'uitk-lockup-price'})
        #Dejamos de emular en firefox
        driver.quit()
    if web =='kayak':
         #URL a la que haremos Web scrapping
        #A la URL se le pasará los elementos de entrada ya que así lo permite
        date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
        url = f"https://www.kayak.es/flights/" + from_loc + "-" + to_loc + "/" + date + "/" + date + "?sort=bestflight_a"
        #Pintamos en pantalla información de url
        print(f"URL: {url}")    
        #Llamamos al emulador de Firefox
        driver = webdriver.Firefox()
        driver.get(url)
        #Añadimos tiempo de espera para evitar ser baneados en la medida de lo posible
        time.sleep(10)
        #Se parsea la WEB a texto legible
        soup = BeautifulSoup(driver.page_source,'lxml')       
        # Obtener todos los datos del sitio web utilizando elementos html y etiquetas.
        airline_name = soup.find_all('div', attrs={'class': 'J0g6-operator-text'})    
        price = soup.find_all('div', attrs={'class': 'f8F1-price-text'})
        #Dejamos de emular en firefox
        driver.quit()        

    if airline_name and price:
        # Limpiamos los datos, obtenemos solo texto y eliminamos espacios en blanco. Todo esto se almacena en una lista utilizando la comprensión de listas.
        airlines_name_list = [a.getText().strip() for a in airline_name]    
        price_list = [f.getText().strip() for f in price]
        # Eliminamos el símbolo del euro y las comas para que los datos se puedan convertir a entero desde una cadena
        num_price_list = [int(re.sub('[€,]', '', x)) for x in price_list]
        #Creamos N elementos según el número de precios que hemos obtenido para los datos de entrada
        from_loc_list = [from_loc] * len(num_price_list)
        to_loc_list = [to_loc] * len(num_price_list)
        date_list = [date] * len(num_price_list)

        # Comprimimos toda la lista y vinculamos los datos en una tupla
        zipped_list = zip(date_list, from_loc_list, to_loc_list, airlines_name_list,num_price_list)
        
        print("The cheapest flights: \n")
        # Recorremos la tupla
        for data in zipped_list:
        #Nos quedamos con el menor de los precios
            if data[4] == min(num_price_list):
                #Mostramos los datos
                print(data)
                #guardamos en base de datos
                insert_sqllite3(data)
        print("Flights saved in the database \n")
    else:
        print("Something went wrong \n")    


#Llamamos a la función de búsqueda de vuelos para su ejecución
search_flight(web,from_city, to_city, day)
