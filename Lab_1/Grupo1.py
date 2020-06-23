####### BLOQUE DE DEFINICION #######

#### IMPORTACIÓN DE FUNCIONES Y LIBRERÍAS.

import tkinter as tk
import os.path as path
from tkinter import messagebox
from pyswip import Prolog, Query
from collections import Counter

#### DEFINICIÓN DE CONSTANTES Y VARIABLES GLOBALES.
global user_symptoms, btn_top_symptoms_list, lbl_init_symptoms, lbl_current_symptoms, text_name, main_window, lbl_possible_disease, user_frame_disease, user_top_symptoms, btn_no_symptoms
p = Prolog()

#### DEFINICIÓN DE FUNCIONES Y CLASES.


# Función auxiliar para la librería tkinter, que permite mostrar un scroll no nativo por pantalla.
# (Tkinter no posee nativamente un scroll para una lista de botones)
# Obtenido de https://stackoverflow.com/questions/31762698/dynamic-button-with-scrollbar-in-tkinter-python
class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, bg="white")
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set, height = 550, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas, bg="white")
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

# Función que permite leer el archivo de texto pathology_file y cargar su contenido en una base de conocimiento.
# Entrada: String con el nombre del archivo de texto a cargar.
# Salida: Boolean. True o False, dependiendo si el archivo de texto se pudo cargar correctamente.
def read_pathology_file(pathology_file):
    if is_valid_file(pathology_file):
        file = open(pathology_file, 'r')
        for line in file:
            filtered_line = filter_line(line)
            add_pathology(filtered_line[0], filtered_line[1])
        file.close()
        return True
    else:
        return False

# Función que permite verificar si el archivo de texto de entrada existe en la carpeta contenedora del programa.
# Entrada: String con el nombre del archivo de texto a verificar.
# Salida: Boolean. True o False, dependiendo si existe el archivo de texto en el directorio.
def is_valid_file(filename):
    if not path.exists(filename):
        return False
    elif filename[-4:] != ".txt":
        return False
    else:
        return True

# Función que permite formatear la línea leída desde el archivo de entrada, quitanto salto de linea y tabulación.
# Entrada: String que contiene la línea leída.
# Salida: String que contiene la línea formateada.
def filter_line(line):
    return line.replace("\t", "").replace("\n", "").split(' _ ')

# Predicado que permite añadir las patologias del archivo de texto en la base de conocimientos, con la forma del siguiente hecho: "pathology(disease,symptom)"
# Entrada: String que contiene la enfermedad y String que contiene el sintoma respectivo de la enfermedad.
# Salida: Hecho construido y agregado a la base de conocimientos.
def add_pathology(disease, symptom):
    pathology = "pathology('"+disease+"','"+symptom+"')"
    p.assertz(pathology)

# Predicado que permite mostrar todos los hechos presentes en la base de conocimiento.
# Entrada: Vacía.
# Salida: Vacía. Se imprime por pantalla todos las patologías representadas como hechos.
def show_all_pathology():
    for soln in p.query("pathology(Disease, Symptom)"):
        print("[Pathology] "+soln["Disease"]+": "+soln["Symptom"])

# Predicado que permite listar todas las enfermedades presentes en la base de conocimiento.
# Entrada: Vacía.
# Salida: Una lista que contiene todas las enfermedades de la base de conocimiento.
def get_all_disease():
    disease = []
    for soln in p.query("pathology(Disease, Symptom)"):
        disease.append(soln["Disease"])
    return disease

# Predicado que dada una consulta sobre una patología en la base de conocimiento, verifica si la consulta es válida.
# Entrada: String que contiene la enfermedad y String que contiene le síntoma.
# Salida: Boolean. True o False, dependiendo si es la consulta en la base de conocimiento es válida o no.
def is_pathology(disease, symptom):
    query = "pathology('"+disease+"','"+symptom+"')"
    response = list(p.query(query))
    return is_valid_query(response)

# Predicado que dado un sintoma, obtiene una lista de todas las enfermedades que lo contienen.
# Entrada: String que representa al sintoma.
# Salida: Lista que contiene las enfermedades.
def diseases_by_symptom(symptom):
    query = "pathology(Disease,'"+symptom+"')"
    response = prolog_query(query)
    return response

# Predicado que dado una enfermedad, obtiene una lista de los sintomas presentes en dicha enfermedad.
# Entrada: String que representa la enfermedad.
# Salida_ Lista que contiene los sintomas.
def symptoms_by_disease(disease):
    query = "pathology('"+disease+"', Symptom)"
    response = prolog_query(query)
    return response

# Predicado que dada una consulta, verifica si es valida y la transforma en formato lista.
# Entrada: Consulta en la base de conocimiento.
# Salida: Respuesta de la consulta.
def prolog_query(query):
    p_query = list(p.query(query))
    if is_valid_query(p_query):
        response = query_results(p_query)
    else:
        response = []
    return response

# Predicado que dada una consulta, verifica si está entrega un respuesta vacía o no.
# Entrada: Consulta en la base de conocimiento.
# Salida: Boolean. True o False, dependiendo si la consulta obtuvo una respuesta o no.
def is_valid_query(query):
    if query == []:
        return False
    else:
        return True

# Predicado que dada una respuesta a una consulta en la base de conocimientos, lista dicha respuesta.
# Entrada: Respuesta de consulta en la base de conocimiento.
# Salida: Lista que contiene el resultado de la consulta.
def query_results(query_response):
    name = get_query_name(query_response)
    response = []
    for res in query_response:
        response.append(res[name])
    return response

# Predicado que dada una respuesta a una consulta en la base de conocimientos, obtiene el nombre de dicha consulta.
# Entrada: Respuesta de consulta en la base de conocimiento.
# Salida: String que contiene el nombre de dicha consulta.
def get_query_name(query_response):
    return [*query_response[0]][0]

# Predicado que dada una lista de síntomas, obtiene las enfermedades en donde estan presentes los sintomas ingresados.
# Entrada: Lista de String que contiene cada sintoma a consultar.
# Salida: Lista de enfermedades.
def diseases_by_symptoms(symptoms):
    diseases = []
    for symptom in symptoms:
        res = diseases_by_symptom(symptom)
        for disease in res:
            diseases.append(disease)
    diseases = disease_filter(diseases, symptoms)
    return diseases

# Predicado que permite filtrar las enfermedades. 
# Entrada: Lista de String que contiene enfermedades y Lista de String que contiene síntomas.
# Salida: Lista con de String con las enfermedades filtradas.
def disease_filter(diseases, symptoms):
    common_diseases = Counter(diseases).items()
    diseases_filter = filter_common_diseases(symptoms, common_diseases)
    diseases = get_counter_names(diseases_filter)
    return diseases

# Predicado que permite contar y filtrar las enfermedades ingresadas.
# Entrada: Lista de String que contiene las enfermedades repetidas y una Lista con los respectivos síntomas.
# Salida: Lista de String con las enfermedades filtradas.
def filter_common_diseases(symptoms, common_diseases):
    return list(filter(lambda disease: match(disease, symptoms), common_diseases))

# Función que tiene la condición de filtrado para los sintomas de una enfermedad.
# Entrada: Lista de String que contiene enfermedades y Lista de String que contiene los síntomas.
# Salida: Boolean. True o False, dependiendo si se cumplió o no la condición del filtrado.
def match(disease, symptoms):
    count_disease = disease[1]
    len_symtoms = len(symptoms)
    if count_disease == len_symtoms:
        return True
    else:
        return False

# Condición para verificar si es necesario parar la lógica del programa.
# Entrada: Lista de String que contiene las posibles enfermedades del usuario e Integer top que permite saber en que momento hacer el corte del programa.
# Salida: Bool. True o False, dependiendo si el usuario ha cumplido la condición necesaria par terminar el programa.
def result_disease(query_response, top):
    if (len(query_response) > top):
        #print("Aun existen muchas enfermedades, por favor siga seleccionando sintomas para tener un resultado mas exacto")
        return False
    else:
        #print("Los sintomas encontrados son:")
        #print(query_response)
        return True
 
# Predicado que dado una lista de enfermedades y una cantidad N, permite obtener los N sintomas más comunes entre las enfermedades de entrada.
# Entrada: Integer que indica cuantos sintomas mostrará el top y Lista con las enfermedades de donde se obtendran los sintomas.
# Salida: Lista de String que contiene los sintomas más comunes entre las enfermedades ingresadas.
def top_symptoms_2(number_symptoms, diseases):
    all_symptoms = []
    for disease in diseases:
        for symptom in symptoms_by_disease(disease):
            if not symptom in user_symptoms:
                all_symptoms.append(symptom)
    symptoms = symptom_filter(number_symptoms, all_symptoms)
    return symptoms

# Predicado que permite filtrar los sintomas. 
# Entrada: Lista de String que contiene enfermedades y Lista de String que contiene síntomas.
# Salida: Lista con de String con los sintomas filtrados.
def symptom_filter(number_symptoms, symptoms):
    common_symptoms = Counter(symptoms).most_common(number_symptoms)
    return get_counter_names(common_symptoms)

# Predicado que permite obtener los nombres de un resultado de una consulta a la base de conocimiento.
# Entrada: Lista de String con la respuesta a una consulta, esta respuesta debe estar filtrada.
# Salida: Lista de String con los nombres.
def get_counter_names(counter_common):
    return list(map(lambda name: name[0], counter_common))

# Predicado que permite obtener una lista de sintomas, donde su condición de filtrado es que se encuentren en al menos 10 enfemerdades.
# Entrada: Lista de String con las enfermedades a analizar.
# Salida: Lista de String con los sintomas filtrados.
def top_symptoms_3(diseases):
    all_symptoms = []
    for disease in diseases:
        for symptom in symptoms_by_disease(disease):
            if not symptom in user_symptoms:
                all_symptoms.append(symptom)
    symptoms = symptom_filter_3(all_symptoms)
    return symptoms

# Función que permite filtrar resultados a partir de una lista de sintomas repetidos. Cuenta cada sintoma y selecciona los que presenten al menos
# 10 cooincidencias por cada enfermedad en la base de conocimientos.
# Entrada: Lista de String con los sintomas repetidos.
# Salida: Lista de String con los nombres de los sintomas sin repetir mas comunes que cumplen la condición.
def symptom_filter_3(symptoms):
    common_symptoms = list(filter( lambda symptom: symptom[1] >= 10, Counter(symptoms).most_common()))
    return get_counter_names(common_symptoms)

# Función que permite actualizar, en la vista principal, los sintomas actuales que presenta el usuario.
# Entrada: Lista que contiene los sintomas actuales.
# Salida: Vacía. Actualiza los labels dentro de la vista principal. 
def update_lbl_current_symptoms(symptom):
    global lbl_current_symptoms
    lbl_current_symptoms["text"] = lbl_current_symptoms["text"]+ "\n" + symptom.capitalize() + "\n"


# Función que permite actualizar, en la vista principal, los botones actuales que puede seleccionar el usuario con los distintos sintomas que puede tener.
# Entrada: Lista de botones con los sintomas
# Salida: Lista actualizada de botones
def update_btn_symptoms():
    i = 0
    remaining_symptoms = top_symptoms_2(top, diseases_by_symptoms(user_symptoms))
    for nombre in remaining_symptoms:
        btn_top_symptoms_list[i]["text"] = nombre.capitalize()
        i += 1
    while i < top:
        btn_top_symptoms_list[i].destroy()
        i += 1

# Esta función se encarga de mostrar por medio de una etiqueta, la o las enfermedades asociadas a una serie de sintomas que ingresó el usuario.
# Entrada: No posee. Las variables requeridas por la interfaz gráfica, se encuentran de manera global.
# Salida: No posee.
def lbl_end_disease():
    diseases = diseases_by_symptoms(user_symptoms)
    if len(diseases) > 1:
        i = 0
        while i < top:
            btn_top_symptoms_list[i]["state"] = tk.DISABLED
            i += 1
        msg_diseases = ""
        for disease in diseases:
            lbl_possible_disease["text"] = lbl_possible_disease["text"] + "\n" + disease.capitalize() + "\n"
            msg_diseases = msg_diseases + disease +"\n"
        messagebox.showwarning(title="DIAGNOSTICO", message= "Con la cantidad de síntomas ingresados, nuestro diagnostico no puede ser certero. \nA continuación te mostraremos las posibles patologías que puedes tener, según nuestros registros." , parent=user_frame_disease)

    else:
        i = 0
        while i < top:
            btn_top_symptoms_list[i]["state"] = tk.DISABLED
            i += 1
        lbl_possible_disease["text"] = lbl_possible_disease["text"] + "\n" + diseases[0].capitalize() + "\n"
        messagebox.showinfo(title="DIAGNOSTICO", message= "Los sintomas ingresados pueden ser de "+ diseases[0], parent=user_frame_disease)
    btn_no_symptoms["state"] = tk.DISABLED

# Función que se ejecuta cada vez que el usuario hace clic en algún sintoma. Se encarga de checkear los sintomas ingresados y de mostrar nuevos sintomas.
# Entrada: Boton seleccionado, donde viene el sintoma del usuario.
# Salida: No posee.
def btn_symptom_action(btn):
    global user_symptoms, top
    symptom = btn['text'].lower()
    if not symptom in user_symptoms:
        user_symptoms.append(symptom)
        update_lbl_current_symptoms(symptom)
    update_btn_symptoms()
    top = len(top_symptoms_2(top, diseases_by_symptoms(user_symptoms)))
    if btn_no_symptoms["state"] == tk.DISABLED and user_symptoms != []:
        btn_no_symptoms["state"] = tk.NORMAL

    if result_disease(diseases_by_symptoms(user_symptoms), 1) or len(user_symptoms) == 0:
        lbl_init_symptoms["text"] = "Usted además puede presentar\n algunos de estos síntomas."
        lbl_end_disease()
    else:
        lbl_init_symptoms["text"] = "Necesito más síntomas para \nhacer el diagnóstico.\n ¿Presenta alguno de estos síntomas?"

# Ventana principal del programa, en esta ventana se seleccionan los sintomas y se realiza la lógica para detectar si una serie de sintomas pertenece a una enfermedad.
# Entrada: Una lista con los sintomas iniciales, se consideran acá los sintomas que estén presentes en al menos 10 enfermedades. top: la cantidad de sintomas a mostrar.
# Salida: No posee.
def start_program(init_top_symptoms, top):
    if(text_name.get() != ""):
        global btn_top_symptoms_list, lbl_init_symptoms, lbl_current_symptoms, lbl_possible_disease, window, main_window, user_frame_disease, user_top_symptoms, btn_no_symptoms
        name_user = text_name.get()
        window = tk.Tk(className='Logic Doctor App por Grupo 1')

        main_window.destroy()
        window.configure(bg="white")
        window.resizable(False, False)
        user_frame = tk.Frame(master=window, width=1200, height=100, bg="#7ac5cd")
        exit_program = tk.Frame(master=window, width=1200, height=50, bg="#7ac5cd")
        user_top_symptoms = tk.Frame(master=window, width=400, height=620, bg="white")
        user_current_symptoms = tk.Frame(master=window, width=400, bg="white")
        aux_frame = tk.Frame(master=window, width=1, bg="black")
        user_top_symptoms = tk.Frame(master=window, width=400, bg="white")
        aux_frame_2 = tk.Frame(master=window, width=1, bg="black")
        user_frame_disease = tk.Frame(master=window, width=400, bg="white")

        scframe = VerticalScrolledFrame(user_top_symptoms)
        scframe.pack()

        lbl_user_name = tk.Label(
            master=user_frame,
            text="Paciente: "+name_user,
            bd=2,
            fg="white",
            bg="#7ac5cd", 
            font=("Arial", 14)
            )
        lbl_user_name.grid(row=0, column=0, padx=20, pady=10)

        lbl_init_symptoms = tk.Label(
            master=scframe.interior,
            text="¿Presenta alguno de estos síntomas?",
            bg="white",
            font=("Arial", 14)
        )
        lbl_init_symptoms.grid(row=0, column=0, padx=20, pady=10)

        btn_top_symptoms_list = []
        i = 1
        for symptom in init_top_symptoms:

            btn_top_symptom = tk.Button(
                master=scframe.interior,
                text=symptom.capitalize(),
                font=("Arial", 14),
                bd=2,
                fg="white",
                bg="#7ac5cd",
                state=tk.NORMAL,
                width=30
            )
            btn_top_symptom["command"] = lambda btn=btn_top_symptom: btn_symptom_action(btn)
            btn_top_symptom.grid(row=i, column=0, pady=5)
            btn_top_symptoms_list.append(btn_top_symptom)
            i += 1
        
        lbl_current_symptoms = tk.Label(
            master=user_current_symptoms,
            text="Sintomas ingresados:\n",
            bg="white",
            font=("Arial", 14)
        )
        lbl_current_symptoms.grid(row=0, column=0, padx=100, pady=10)

        lbl_possible_disease = tk.Label(
            master=user_frame_disease,
            text="Posible patología:\n",
            bg="white",
            font=("Arial", 14)
        )
        lbl_possible_disease.grid(row=0, column=0, padx=20, pady=10)

        btn_exit = tk.Button(master=exit_program, text="Salir", bg="white", font=("Arial", 14), width=10, command= lambda x=window :window.destroy())
        btn_exit.place(x=1075, y=5)
        btn_no_symptoms = tk.Button(master=exit_program, state=tk.DISABLED, text="No, no presento más sintomas", bg="white", font=("Arial", 14), width=30, command= lambda x=1 :lbl_end_disease())
        btn_no_symptoms.place(x=20, y=5)

        user_frame.pack(fill=tk.X, side=tk.TOP)
        exit_program.pack(fill=tk.X, side=tk.BOTTOM)
        user_top_symptoms.pack(fill=tk.BOTH, side=tk.LEFT, pady=10, padx=10)
        aux_frame.pack(fill=tk.Y, side=tk.LEFT, pady=15 ,padx=10)
        user_current_symptoms.pack(fill=tk.BOTH, side=tk.LEFT,  pady=10)
        aux_frame_2.pack(fill=tk.Y, side=tk.LEFT, pady=15 ,padx=10)
        user_frame_disease.pack(fill=tk.BOTH, side=tk.LEFT, pady=10)


        window.mainloop()
        
    else:
        messagebox.showerror(title="Error", message= "Debes ingresar el nombre del paciente antes de continuar")

# Función que permite realizar toda la lógica del programa.
# Realiza la construcción de la vista principal y se encarga de realizar las consultas a la base de conociemiento.
# Muestra, mediante la vista, la respuesta al usuario en caso de encontrar una enfermedad que contemple los sintomas ingresados.
# Entrada: Vacía.
# Salida: Vacía.
def main():
    read_file = read_pathology_file("pathology.txt")
    if read_file is True:
        global user_symptoms, text_name, main_window, top
        
        user_symptoms = []
        all_diseases = get_all_disease()

        # Top symptoms
        top = len(top_symptoms_3(all_diseases))
        init_top_symptoms = top_symptoms_2(top, all_diseases)

        # Creación de la vista principal.
        main_window=tk.Tk()

        name_user = ""

        main_window.title("Logic Doctor App por Grupo 1")
        main_window.geometry("800x600")
        main_window.resizable(width=False, height=False)
        photo= tk.PhotoImage(file="fondo.png")
        label_photo = tk.Label(main_window, image=photo).place(x=0,y=0)
                
        label_title = tk.Label(main_window,text="Logic Doctor App", bg="white", font=("Arial", 28))
        label_title.place(x=400, y=20)

        label_description = tk.Label(text="Hola, soy un sistema de asesoramiento que simula un\n diagnostico medico, para esto\n necesito que selecciones\n los sintomas que presenta el paciente \npara determinar la posible afección médica.", font=("Arial", 14), bg="#fcfbfb")
        label_description.place(x=320, y=80)

        label_information = tk.Label(text="INFORMACIÓN IMPORTANTE: \nLogic Doctor App NO RECOMIENDA SU USO PARA \nFINES PROFESIONALES, esta App se creó\n con fines estudiantiles y en ningún caso deben\n tomarse en cuenta los resultados obtenidos aquí.", font=("Arial", 14), bg="#fcfbfb")
        label_information.place(x=320, y=220)

        label_collaborators = tk.Label(text="Grupo 1.\nDesarrollado por: \n - Jorge Ayala\n - Felipe Gonzalez\n - Cristobal Medrano\n - Javier Perez", font=("Arial", 14), bg="#fefefe")
        label_collaborators.place(x=30, y=450)

        label_collaborators = tk.Label(text="Para continuar, ingrese el nombre del paciente.", font=("Arial", 14), bg="#fcfcfc")
        label_collaborators.place(x=350, y=500)

        text_name = tk.Entry(main_window, width=40)
        text_name.place(x=400, y=540)

        button_begin = tk.Button(text="Comenzar",font=("Arial", 14), width=10, command = lambda init=init_top_symptoms:  start_program(init_top_symptoms, top))
        button_begin.place(x=650, y=540)

        main_window.mainloop()
    else:
        print("Error al abrir el archivo de patologías.")

####### BLOQUE PRINCIPAL #######

#### LLAMADO FUNCIÓN MAIN PARA ARRANCAR EL PROGRAMA.
main()