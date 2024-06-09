import pydot
import plyplus 
from plyplus import STransformer 

class CPPCodeGenerator(STransformer):
    def __init__(self):
        self.output = [] # Lista para almacenar el código C++ generado
        self.banderaArithmetic = False # Bandera para indicar si se está procesando una expresión aritmética
        self.banderaConditional = False # Bandera para indicar si se está procesando una estructura condicional
        self.banderaFuncionDef = False # Bandera para indicar si se está procesando una definición de función
        self.banderaFunctioncall = False # Bandera para indicar si se está procesando una llamada a función

    # Esta función procesa las expresiones aritméticas
    def arithmetic_exp(self, tree):
        self.banderaArithmetic = True
        # Se obtienen los valores de los nodos del árbol
        left = self.evaluate(tree.tail[0])  # Primer parte de la expresión
        op = tree.tail[1].tail[0] # Operador, '+', '-', etc.
        right = self.evaluate(tree.tail[2]) # Segunda parte de la expresión

        # Se genera código C++ para la operación aritmética
        cpp_code = f"{left} {op} {right}"
        #cpp_code = f"std::cout << ({expresion}) << std::endl;"
        return cpp_code

    # Esta función procesa las expresiones de asignación que contienen paréntesis
    def parexpression(self, tree):
        # Se evalúa la expresión dentro de los paréntesis y se devuelve el resultado.
        exp_interna = tree.tail[0]
        return f"({exp_interna})"
    
    def number(self, tree):
        return tree.tail[0].tail[0]

    def variable(self, tree):
        nombre_variable = tree.tail[0].tail[0]
        return nombre_variable
    

    # Esta función procesa las definiciones de funciones
    def functiondef(self, tree):
        func_name = tree.tail[0].tail[0]  # Nombre de la función
        # Ya que no hay que no hay tipos explícitos en Kaleidoscope
        # Se asumen los parámetros enteros por simplicidad
        # Se recolentan parámetros, asumiendo que están en nodos sucesivos tras el nombre
        params = []
        for parametro in tree.tail:
            if hasattr(parametro, 'head') and parametro.head == 'parameter':
                params.append(f"int {parametro.tail[0].tail[0]}")  # Asume que los parámetros son de tipo entero
        
        # Se procesa el cuerpo de la función
        body = self.ensure_semicolon(tree.tail[-1])  # Se asegura que el cuerpo termine en ';'

        # Se genera el código C++ para la definición de la función
        cpp_code = f"int {func_name}({', '.join(params)}) {{\n{body}\n}}\n"
        self.output.append(cpp_code)
    
    # Esta función procesa las llamadas a funciones
    def functioncall(self, tree):
        self.banderaFunctioncall = True
        nombre_funcion = tree.tail[0].tail[0]  # Nombre de la función
        # Recolectar argumentos, que están entre paréntesis después del nombre de la función
        args = []
        i = 1
        while i < len(tree.tail):
            args.append(tree.tail[i])  # Asume que los argumentos son numéricos
            i += 1
        
        # Se genera el código C++ para la llamada a la función
        cpp_code = f"{nombre_funcion}({', '.join(args)})"
        return cpp_code
    
    # Esta función procesa las expresiones de asignación
    def conditional(self, tree):
        self.banderaConditional = True
        condition = tree.tail[0]  # Procesa la condición directamente
        if_body = tree.tail[1]  # Procesa el cuerpo del if
        else_body = tree.tail[2] # Procesa el cuerpo del else
        if_body = if_body.replace("\n", "\n    ")  # Se añade indentación
        else_body = else_body.replace("\n", "\n    ") # Se añade indentación
        if_body = self.ensure_semicolon(if_body)  # Se asegura que el cuerpo del if termine en ';'
        else_body = self.ensure_semicolon(else_body)  # Se asegura que el cuerpo del else termine en ';'

        # Se genera el código C++ para la estructura condicional
        cpp_code = f"if ({condition}) {{\n{if_body}\n}} else {{\n{else_body}\n}}"
        return cpp_code

    # Esta función procesa las expresiones lógicas
    def logicalexpression(self, tree):
        left = tree.tail[0]
        op = tree.tail[1].tail[0]
        right = tree.tail[2]
        return f"{left} {op} {right}"
    
    # Esta función procesa los números y los devuelve
    def number(self, tree):
        return tree.tail[0]

    # Esta función procesa las variables y las devuelve
    def variable(self, tree):
        return tree.tail[0].tail[0]
    
    # Esta función procesa el cuerpo del programa
    def program(self, cpp_code):
        body_code = []
        headers = '#include <iostream>\n'
        for item in cpp_code.tail:
            if self.banderaArithmetic and item != None and not self.banderaConditional:
                self.output.append(headers)
                body_code.append(f"std::cout << {item} << std::endl;")
                self.banderaArithmetic = False
            elif self.banderaConditional and item != None and not self.banderaFunctioncall:
                body_code.append(item)
                self.banderaConditional = False
            elif self.banderaFunctioncall and item != None:
                self.output.append(headers)
                body_code.append(f"std::cout << {item} << std::endl;")
                self.banderaFunctioncall = False
        #print(f'body_code: {body_code}')

        # Se genera el código C++ para el cuerpo del programa
        main_body = "\n    ".join(body_code)
        main_function = f"int main() {{\n    {main_body}\n    return 0;\n}}"
        self.output.append(main_function)


    # Esta función obtiene el código C++ generado
    def obtenerCpp(self):
        return "\n".join(self.output)
    
    # Esta función procesa las expresiones del árbol de parseo 
    def evaluate(self, tree):
        if hasattr(tree, 'head'):
            method = getattr(self, tree.head, None)
            if method:
                return method(tree)
        return tree
    
    # Esta función asegura que las líneas de código terminen en ';'
    def ensure_semicolon(self, code):
        lines = code.split("\n")
        result = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line and not stripped_line.endswith(';') and not stripped_line.endswith('}') and not stripped_line.endswith('{'):
                line += ";"
            result.append(line)
        return "\n".join(result)


# Función principal
def main():

    # Se carga la gramática y parsea el archivo
    with open('Kaleidoscope.g', 'r') as archivoGramatica:
        with open('sumafuncion.kl', 'r') as archivoKL:
            gramatica = plyplus.Grammar(archivoGramatica)
            codigoFuente = archivoKL.read()
            print("Código de entrada Kaleidoscope:")
            print(codigoFuente)

            # Se parsea el código fuente
            arbolParse = gramatica.parse(codigoFuente)

            print("\nÁrbol de parseo:")
            print(arbolParse)
            input("Presione Enter para continuar...")

            # Se genera y se guarda el árbol en formato PNG
            arbolParse.to_png_with_pydot(r'arbolParser.png')

            # Se instancia el generador de código C++
            generador = CPPCodeGenerator()
            generador.transform(arbolParse)
            codigo_cpp = generador.obtenerCpp()

            # Se guarda en un archivo el código C++ generado
            with open('output.cpp', 'w') as archivoSalida:
                archivoSalida.write(codigo_cpp)

            print("\nCÓDIGO C++ GENERADO:\n         |\n         V\n")
            print(codigo_cpp)
            
if __name__ == '__main__':
    main()