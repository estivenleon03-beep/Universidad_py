class persona:
    def __init__(self, nombre, apellido, edad, genero, fecha_naciemiento, direccion, telefono, correo):
        self.nombre = nombre
        self.apellido= apellido
        self.edad = edad
        self.genero = genero
        self.fecha_naciemiento = fecha_naciemiento
        self.direccion = direccion
        self.telefono = telefono
        self.correo = correo

def __str__(self):
    return f"Nombre: {self.nombre} {self.apellido}"
    
@property
def nombre_completo(self):
    return f"{self.nombre} {self.apellido}"

@property
def edad(self):
    return self._edad

@property
def correo(self):   
    return self.correo

@property
def telefono(self):
    return self.telefono

@property
def genero(self):
    return self.genero

@property
def fechaNaci(self):
    return self.fechaNaci

@property
def direccion(self):
    return self.direccion

@nombre_completo.setter
def nombre_completo(self, nombre_completo):
    if nombre_completo == None:
        raise ValueError("El nombre y apellido no puede ser nulo")
    elif nombre_completo.isalpha():
        raise ValueError("El nombre y apellido no puede contener números")
    else:
    self.nombre, self.apellido = nombre_completo

@edad.setter
def edad(self, edad):
    try:
        int(edad)
        return True
        if edad == None:
        raise ValueError("La edad no puede estar vacía")
        
    except ValueError:
        print("La edad no puede estar vacía y debe ser un número entero")
        return False
    
@correo.setter
def correo(self, correo):
    if correo == None or correo.strip() == "":
        raise ValueError("El correo no puede estar vacío")
    else:
        self.correo = correo
        print("Correo guardado correctamente")
    
@telefono.setter
def telefono(self, telefono):
    if telefono == None or telefono.strip() == "":
        raise ValueError("El teléfono no puede estar vacío")
    elif not telefono.isdigit():
        raise ValueError("El teléfono debe contener solo números")
    else:
        self.telefono = telefono
        print("Teléfono guardado correctamente")

@genero.setter
def genero(self, genero):
    if genero == None or genero.strip() == "":
        raise ValueError("El género no puede estar vacío")
    elif genero.lower() not in ["masculino", "femenino", "otro"]:
        raise ValueError("El género debe ser 'masculino', 'femenino' u 'otro'")
    elif genero.isdigit():
        raise ValueError("El género no puede contener números")
    else:
        self.genero = genero
        print("genero guardado correctamente")

@fecha_naciemiento.setter
def fecha_naciemiento(self, fecha_naciemiento):
    if fecha_naciemiento == None or fecha_naciemiento.strip() == "":
        raise ValueError("La fecha de nacimiento no puede estar vacía")
    else:
        self.fecha_naciemiento = fecha_naciemiento
        print("Fecha de nacimiento guardada correctamente")

@direccion.setter
def direccion(self, direccion):
    if direccion == None or direccion.strip() == "":
        raise ValueError("La dirección no puede estar vacía")
    else:
        self.direccion = direccion
        print("Dirección guardada correctamente")