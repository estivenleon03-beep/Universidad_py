import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tokenize  # Módulo para tokenizar código Python
import io        # Para convertir strings en flujos de entrada
import keyword   # Para identificar palabras reservadas de Python
import ast       # Para construir y recorrer el Árbol de Sintaxis Abstracta (AST)
from graphviz import Digraph  # Para generar gráficos de árbol
import os        # Para abrir archivos generados automáticamente

# ─────────────────────────────────────────────
# CONFIGURACIÓN VISUAL DE LA INTERFAZ
# Modo oscuro con tema de color azul (customtkinter)
# ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CompiladorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Mini Compilador Python PRO")
        self.root.geometry("1100x650")  # Tamaño inicial de la ventana

        self.crear_interfaz()  # Construye todos los widgets de la UI

    # ─────────────────────────────────────────────
    # INTERFAZ GRÁFICA
    # Divide la ventana en dos paneles:
    #   - Izquierda: editor de código
    #   - Derecha: botones, tabla de tokens y área de salida
    # ─────────────────────────────────────────────
    def crear_interfaz(self):

        # Editor de texto donde el usuario escribe el código fuente
        self.editor = ctk.CTkTextbox(self.root, width=500)
        self.editor.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Panel derecho que contiene controles y resultados
        frame_derecho = ctk.CTkFrame(self.root)
        frame_derecho.pack(side="right", fill="both", expand=True)

        # Fila de botones de acción
        frame_botones = ctk.CTkFrame(frame_derecho)
        frame_botones.pack(fill="x", pady=5)

        # Cada botón dispara una funcionalidad del compilador
        ctk.CTkButton(frame_botones, text="Analizar",  command=self.analizar).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Árbol",     command=self.mostrar_arbol_inteligente).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Función",   command=self.explicar_codigo).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Guardar",   command=self.guardar).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Cargar",    command=self.cargar).pack(side="left", padx=5)

        # Tabla que muestra los tokens clasificados por categoría
        self.tabla = ttk.Treeview(frame_derecho, columns=("Categoría", "Valores"), show="headings")
        self.tabla.heading("Categoría", text="Categoría")
        self.tabla.heading("Valores",   text="Valores")
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)

        # Área de texto para mensajes de estado, errores y descripciones
        self.salida = ctk.CTkTextbox(frame_derecho, height=120)
        self.salida.pack(fill="x", padx=10, pady=5)

    # ─────────────────────────────────────────────
    # ANÁLISIS LÉXICO
    # Recorre el código fuente token por token y lo clasifica en:
    #   • Keywords    → palabras reservadas (if, for, return…)
    #   • Identificadores → nombres de variables y funciones
    #   • Literales   → números y cadenas de texto
    #   • Operadores  → +, -, *, =, ==, etc.
    #   • Delimitadores → (), {}, [], ;, :, ,
    # Devuelve un diccionario {categoría: conjunto de valores únicos}
    # ─────────────────────────────────────────────
    def analisis_lexico(self, codigo):

        categorias = {
            "Identificadores": set(),
            "Keywords":        set(),
            "Operadores":      set(),
            "Delimitadores":   set(),
            "Literales":       set()
        }

        try:
            # tokenize.generate_tokens recibe una función readline;
            # io.StringIO convierte el string del código en un objeto de archivo en memoria
            tokens = tokenize.generate_tokens(io.StringIO(codigo).readline)

            for tok in tokens:
                tipo  = tokenize.tok_name[tok.type]  # Nombre del tipo de token (NAME, OP, NUMBER…)
                valor = tok.string                    # Texto exacto del token

                # Prioridad 1: si el valor es palabra reservada de Python, va a Keywords
                if valor in keyword.kwlist:
                    categorias["Keywords"].add(valor)

                # Prioridad 2: NAME que no es keyword → identificador (variable, función, clase)
                elif tipo == "NAME":
                    categorias["Identificadores"].add(valor)

                # Prioridad 3: números y cadenas literales
                elif tipo in ["NUMBER", "STRING"]:
                    categorias["Literales"].add(valor)

                # Prioridad 4: operadores vs delimitadores
                # Los caracteres de puntuación estructural se separan de los operadores aritméticos/lógicos
                elif tipo == "OP":
                    if valor in "(){}[];:,":
                        categorias["Delimitadores"].add(valor)
                    else:
                        categorias["Operadores"].add(valor)

        except Exception as e:
            self.mostrar_error(f"Error léxico: {e}")

        return categorias

    # ─────────────────────────────────────────────
    # MOSTRAR TABLA DE TOKENS
    # Limpia la tabla y vuelca cada categoría como una fila
    # ─────────────────────────────────────────────
    def mostrar_tabla(self, categorias):
        self.tabla.delete(*self.tabla.get_children())  # Borra filas anteriores

        for categoria, valores in categorias.items():
            texto = ", ".join(valores)  # Une los valores del set en una cadena legible
            self.tabla.insert("", "end", values=(categoria, texto))

    # ─────────────────────────────────────────────
    # ANALIZAR (botón principal)
    # Ejecuta el análisis léxico y sintáctico:
    #   1. Tokeniza el código y muestra la tabla de categorías
    #   2. Valida la sintaxis con ast.parse; informa éxito o error
    # ─────────────────────────────────────────────
    def analizar(self):
        codigo = self.editor.get("1.0", "end")  # Lee todo el contenido del editor
        self.salida.delete("1.0", "end")         # Limpia el área de salida

        categorias = self.analisis_lexico(codigo)
        self.mostrar_tabla(categorias)

        try:
            ast.parse(codigo)  # Si no lanza excepción, el código es sintácticamente válido
            self.salida.insert("end", "✔ Código sintácticamente correcto\n")
        except Exception as e:
            self.salida.insert("end", f"❌ Error sintáctico: {e}\n")

    # ─────────────────────────────────────────────
    # ÁRBOL INTELIGENTE
    # Decide qué tipo de árbol generar según la complejidad del código:
    #   • Código simple (una sola asignación) → árbol simplificado estilo diagrama
    #   • Cualquier otra estructura           → AST completo de Python
    # ─────────────────────────────────────────────
    def mostrar_arbol_inteligente(self):
        codigo = self.editor.get("1.0", "end")
        self.salida.delete("1.0", "end")

        try:
            arbol = ast.parse(codigo)

            # Condición de simplicidad: exactamente un nodo raíz y ese nodo es una asignación
            es_simple = (
                len(arbol.body) == 1 and
                isinstance(arbol.body[0], ast.Assign)
            )

            if es_simple:
                self.salida.insert("end", "🌳 Árbol simplificado (tipo PDF)\n")
                self.arbol_simple(arbol.body[0])
            else:
                self.salida.insert("end", "🌳 Árbol completo (AST de Python)\n")
                self.arbol_completo(arbol)

        except Exception as e:
            self.mostrar_error(f"Error: {e}")

    # ─────────────────────────────────────────────
    # ÁRBOL SIMPLE
    # Genera un árbol de expresión limpio para asignaciones sencillas.
    # Usa recursión para descomponer:
    #   ast.Assign  → nodo "=" con hijo izquierdo (target) y derecho (value)
    #   ast.BinOp   → nodo con el símbolo del operador (+, -, *, /)
    #   ast.Name    → hoja con el nombre de la variable
    #   ast.Constant→ hoja con el valor literal
    # El resultado se exporta como PNG y se abre automáticamente.
    # ─────────────────────────────────────────────
    def arbol_simple(self, nodo_principal):
        dot = Digraph()
        contador = 0  # Contador global para IDs únicos de nodos en el grafo

        def nuevo_id():
            nonlocal contador
            contador += 1
            return str(contador)  # Cada nodo recibe un ID numérico único como string

        def simplificar(nodo):
            # Nodo de asignación: conecta el operador "=" con target y value
            if isinstance(nodo, ast.Assign):
                raiz = nuevo_id()
                dot.node(raiz, "=")
                izq = simplificar(nodo.targets[0])  # Lado izquierdo de la asignación
                der = simplificar(nodo.value)        # Lado derecho (expresión)
                dot.edge(raiz, izq)
                dot.edge(raiz, der)
                return raiz

            # Operación binaria: conecta el operador con sus dos operandos
            elif isinstance(nodo, ast.BinOp):
                simbolos = {
                    ast.Add:  "+",
                    ast.Sub:  "-",
                    ast.Mult: "*",
                    ast.Div:  "/"
                }
                raiz = nuevo_id()
                dot.node(raiz, simbolos.get(type(nodo.op), "?"))  # "?" si el operador no está mapeado
                izq = simplificar(nodo.left)
                der = simplificar(nodo.right)
                dot.edge(raiz, izq)
                dot.edge(raiz, der)
                return raiz

            # Hoja: nombre de variable
            elif isinstance(nodo, ast.Name):
                nodo_id = nuevo_id()
                dot.node(nodo_id, nodo.id)
                return nodo_id

            # Hoja: valor constante (número, string, booleano…)
            elif isinstance(nodo, ast.Constant):
                nodo_id = nuevo_id()
                dot.node(nodo_id, str(nodo.value))
                return nodo_id

        simplificar(nodo_principal)
        ruta = dot.render("arbol_simple", format="png")  # Genera arbol_simple.png
        os.startfile(ruta)  # Abre la imagen con el visor predeterminado del sistema

    # ─────────────────────────────────────────────
    # ÁRBOL COMPLETO
    # Recorre recursivamente el AST completo de Python con ast.iter_child_nodes.
    # Cada nodo del AST se convierte en un nodo del grafo etiquetado con su tipo;
    # los nodos Name y Constant también muestran su valor para mayor legibilidad.
    # ─────────────────────────────────────────────
    def arbol_completo(self, arbol):
        dot = Digraph()

        def recorrer(nodo, padre=None):
            nombre  = str(id(nodo))          # id() de Python es único por objeto en memoria
            etiqueta = type(nodo).__name__   # Nombre de la clase AST (Module, Assign, BinOp…)

            # Enriquece la etiqueta con el valor concreto si el nodo lo tiene
            if isinstance(nodo, ast.Name):
                etiqueta += f"\n{nodo.id}"
            elif isinstance(nodo, ast.Constant):
                etiqueta += f"\n{nodo.value}"

            dot.node(nombre, etiqueta)

            if padre:
                dot.edge(padre, nombre)  # Conecta el nodo con su padre

            # Desciende a todos los hijos directos del nodo actual
            for hijo in ast.iter_child_nodes(nodo):
                recorrer(hijo, nombre)

        recorrer(arbol)
        ruta = dot.render("arbol_completo", format="png")  # Genera arbol_completo.png
        os.startfile(ruta)

    # ─────────────────────────────────────────────
    # EXPLICAR CÓDIGO
    # Recorre el AST con ast.walk (visita todos los nodos en orden BFS/DFS)
    # y genera una descripción en lenguaje natural de las construcciones encontradas:
    #   FunctionDef → informa el nombre de la función definida
    #   Assign      → indica que hay asignaciones
    #   Return      → indica que hay retorno de valor
    #   Call        → indica que se invoca una función
    # ─────────────────────────────────────────────
    def explicar_codigo(self):
        codigo = self.editor.get("1.0", "end")
        self.salida.delete("1.0", "end")

        try:
            arbol = ast.parse(codigo)
            descripcion = ""

            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.FunctionDef):
                    descripcion += f"Define una función '{nodo.name}'.\n"
                elif isinstance(nodo, ast.Assign):
                    descripcion += "Realiza asignaciones.\n"
                elif isinstance(nodo, ast.Return):
                    descripcion += "Retorna un valor.\n"
                elif isinstance(nodo, ast.Call):
                    descripcion += "Llama a una función.\n"

            if descripcion == "":
                descripcion = "Código simple."  # Ninguna construcción relevante detectada

            self.salida.insert("end", descripcion)

        except Exception as e:
            self.mostrar_error(f"Error: {e}")

    # ─────────────────────────────────────────────
    # MOSTRAR ERROR
    # Método centralizado para imprimir mensajes de error en el área de salida
    # ─────────────────────────────────────────────
    def mostrar_error(self, mensaje):
        self.salida.insert("end", mensaje + "\n")

    # ─────────────────────────────────────────────
    # GUARDAR
    # Abre un diálogo para elegir ruta y nombre de archivo (.txt por defecto).
    # Escribe el código fuente y la tabla de tokens en el archivo resultante.
    # ─────────────────────────────────────────────
    def guardar(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".txt")

        if archivo:
            codigo = self.editor.get("1.0", "end")
            categorias = self.analisis_lexico(codigo)  # Re-tokeniza para obtener datos frescos

            with open(archivo, "w") as f:
                f.write("CÓDIGO:\n")
                f.write(codigo + "\n\n")

                f.write("TOKENS:\n")
                for cat, vals in categorias.items():
                    f.write(f"{cat}: {', '.join(vals)}\n")

            messagebox.showinfo("Guardado", "Archivo guardado correctamente")

    # ─────────────────────────────────────────────
    # CARGAR
    # Abre un diálogo filtrado a archivos .py, lee su contenido
    # y lo vuelca en el editor, reemplazando cualquier texto previo.
    # ─────────────────────────────────────────────
    def cargar(self):
        archivo = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])

        if archivo:
            with open(archivo, "r") as f:
                contenido = f.read()

            self.editor.delete("1.0", "end")   # Borra el contenido actual del editor
            self.editor.insert("1.0", contenido)


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# Crea la ventana raíz de customtkinter, instancia la aplicación y arranca el loop de eventos
# ─────────────────────────────────────────────
root = ctk.CTk()
app = CompiladorApp(root)
root.mainloop()
