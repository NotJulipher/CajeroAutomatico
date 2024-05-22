import sqlite3
import tkinter as tk
from tkinter import ttk
import datetime
import random
import time

class CajeroAutomatico(tk.Tk):
    intentos_tarjeta = 3
    intentos_cedula = 3
    intentos_celular = 3
    
    def __init__(self):
        super().__init__()


        self.title("Cajero Automático - Banco de Bogotá")
        self.geometry("1920x1080")
        self.config(bg="#14327D")

        # Cargar la imagen del logo
        self.logo_img = tk.PhotoImage(file="banco_de_bogota_logo.png")
        self.logo_img = self.logo_img.subsample(2)  # Redimensionar la imagen

        self.current_screen = None
        self.pantalla_inicio()
        
    def pantalla_inicio(self):
        frame_inicio = tk.Frame(self, bg="#14327D")
        frame_inicio.pack(expand=True, fill="both")

        self.attributes("-fullscreen", True) 
        self.bind("<F11>", lambda event: self.attributes("-fullscreen", not self.attributes("-fullscreen")))

        # Logo del Banco de Bogotá
        label_logo = tk.Label(frame_inicio, image=self.logo_img, bg="#14327D")
        label_logo.pack(pady=10)

        # Crear un marco para el resto de los widgets
        contenido_frame = tk.Frame(frame_inicio, bg="#14327D")
        contenido_frame.pack(fill="x", pady=50)

        # Crear una etiqueta para la selección del método de inicio de sesión
        etiqueta_metodo_inicio = tk.Label(contenido_frame, text="Inicio de Sesion", bg="#14327D", fg="white", font=("Segoe UI Semibold", 20))
        etiqueta_metodo_inicio.pack(pady=10)

        # Crear un marco para el checkbox
        opciones_frame = tk.Frame(contenido_frame, bg="#14327D")
        opciones_frame.pack()

        # Crear checkbox para la selección del método de inicio de sesión
        opciones = [("Tarjeta con chip", 1), ("Celular/Pin", 2), ("Cedula/Contraseña", 3)]
        self.metodo_inicio_var = tk.IntVar()

        
        def actualizar_campos():
            # Ocultar todos los campos inicialmente
            etiqueta_celular.pack_forget()
            entrada_celular.pack_forget()
            etiqueta_pin.pack_forget()
            entrada_pin.pack_forget()

            metodo = self.metodo_inicio_var.get()
            if metodo == 1:  # Tarjeta con chip
                etiqueta_pin.config(text="Pin: ")
                etiqueta_pin.pack(side='left', padx=10)
                entrada_pin.pack(side='left', padx=10)
                                
            elif metodo == 2:  # Celular/Pin
                etiqueta_celular.config(text="Celular:")
                etiqueta_pin.config(text="Pin")
                etiqueta_celular.pack(side='left', padx=10)
                entrada_celular.pack(side='left', padx=10)
                etiqueta_pin.pack(side='left', padx=10)
                entrada_pin.pack(side='left', padx=10)
            elif metodo == 3:  # Cedula/Contraseña
                etiqueta_celular.config(text="Cedula:")
                etiqueta_celular.pack(side='left', padx=10)
                entrada_celular.pack(side='left', padx=10)
                etiqueta_pin.config(text="Contraseña: ")
                etiqueta_pin.pack(side='left', padx=10)
                entrada_pin.pack(side='left', padx=10)

        for texto, valor in opciones:
            tk.Radiobutton(opciones_frame, text=texto, variable=self.metodo_inicio_var, value=valor, bg="#14327D", fg="white", font=("Segoe UI Semibold", 16), command=actualizar_campos).pack(side='left', padx=10)

        
        def confirmar(): #validacion del campo de pin
            pines_lista = []
            def buscar_pin_tarjeta(self):
                # Conectar a la base de datos
                conexion = sqlite3.connect("proyecto.db")
                cursor = conexion.cursor()

                # Buscar en la tabla tarjeta si existe un pin vinculado a una tarjeta
                cursor.execute("SELECT pin FROM tarjeta")
       
                pines = cursor.fetchall()

                # Print all the pins
                for pin in pines:
                    # print(pin)
                    pines_lista.append(pin[0])

                # Cerrar la conexión a la base de datos
                conexion.close()
                
            buscar_pin_tarjeta(self)
            
            pin = entrada_pin.get().strip()
            mensaje_error.config(text="")  # Limpiar mensaje de error
            if not pin:
                # Si el campo de texto está vacío
                mensaje_error.config(text="Por favor ingrese un pin.")
                return
            try:
                conexion = sqlite3.connect("proyecto.db")
                cursor = conexion.cursor()
                
                # Buscar que la tarjeta tenga estado 1
                cursor.execute("SELECT estado FROM tarjeta")
                estado = cursor.fetchall()
                # print(estado)
                if estado[0][0] == 0:
                    mensaje_error.config(text="Tarjeta bloqueada")
                    entrada_pin.delete(0, tk.END)
                    return
                
                valor_entero = int(pin)
                if valor_entero <= 9999 and valor_entero >= 0 and len(pin) == 4:
                    if valor_entero in pines_lista:
                        # Hacer algo con el pin encontrado
                        print("Pin correcto")
                        self.pantalla_retiro()
                        pass
                    else:
                    # No se encontró ningún pin vinculado a una tarjeta
                        print("Pin incorrecto")
                        mensaje_error.config(text="Pin incorrecto")
                        entrada_pin.delete(0, tk.END)
                        self.intentos_tarjeta -= 1
                        
                        if self.intentos_tarjeta == 0:
                            # Bloquear la tarjeta
                            entrada_pin.delete(0, tk.END)
                            print("Tarjeta bloqueada")
                            mensaje_error.config(text="Tarjeta bloqueada")
                            entrada_pin.config(state="disabled")

                            # Bloquear el boton de ingresar
                            boton_ingresar.config(state="disabled")
                            
                            # time.sleep(5)

                            entrada_pin.config(state="normal")
                            boton_ingresar.config(state="normal")

                            # Setear el estado de la tarjeta en la base de datos a 0

                            cursor.execute("UPDATE tarjeta SET estado = 0")
                            conexion.commit()
                            conexion.close()
                        else:
                            # Mostrar mensaje de intentos_tarjeta restantes
                            mensaje_error.config(text=f"Pin incorrecto. intentos_tarjeta restantes: {self.intentos_tarjeta}")
                            entrada_pin.delete(0, tk.END)
                        pass
                else:
                    # Si el valor ingresado no cumple con los requisitos
                    mensaje_error.config(text="El valor ingresado debe tener 4 digitos.")
                    entrada_pin.delete(0, tk.END)
                pines_lista = list(set(pines_lista))
                # print(pines_lista)
            except ValueError:
                # Si el valor ingresado no es un número válido, muestra un mensaje de error
                mensaje_error.config(text="Por favor ingrese un valor válido.")
                
        # Crear campos de texto
        campos_frame = tk.Frame(contenido_frame, bg="#14327D")
        campos_frame.pack(pady=20)

        etiqueta_celular = tk.Label(campos_frame, text="Celular:", bg="#14327D", fg="white", font=("Segoe UI Semibold", 16))
        entrada_celular = tk.Entry(campos_frame, font=("Segoe UI Semibold", 16))

        etiqueta_pin = tk.Label(campos_frame, text="Pin:", bg="#14327D", fg="white", font=("Segoe UI Semibold", 16))
        entrada_pin = tk.Entry(campos_frame, font=("Segoe UI Semibold", 16))

        # Crear botón para ingresar
        boton_ingresar = tk.Button(contenido_frame, text="Ingresar", bg="white", fg="#14327D", font=("Segoe UI Semibold", 20), command=confirmar)
        boton_ingresar.pack(pady=10)

        # Etiqueta para mostrar mensaje de error
        mensaje_error = tk.Label(frame_inicio, text="", bg="#14327D", fg="red", font=("Segoe UI Semibold", 14))
        mensaje_error.pack()

        self.cambiar_pantalla(frame_inicio)
        
        

    

    
    
    def pantalla_retiro(self):
        self.valor_btc = 270485639.70  # variable para poner lo que vale 1 BTC
        self.saldo_actual = 10000000  #saldo actual

        frame_retiro = tk.Frame(self, bg="#14327D")
        frame_retiro.pack(expand=True, fill="both")

        # Logo del Banco de Bogotá
        label_logo = tk.Label(frame_retiro, image=self.logo_img, bg="#14327D")
        label_logo.pack(pady=10)

        # Mostrar saldo actual y equivalencia en BTC
        saldo_frame = tk.Frame(frame_retiro, bg="#14327D")
        saldo_frame.pack(pady=20)

        etiqueta_saldo = tk.Label(saldo_frame, text=f"Saldo actual: ${self.saldo_actual}", bg="#14327D", fg="white", font=("Segoe UI Semibold", 20))
        etiqueta_saldo.pack()

        etiqueta_btc = tk.Label(saldo_frame, text=f"Equivalente en BTC: {self.saldo_actual / self.valor_btc:.6f} BTC", bg="#14327D", fg="white", font=("Segoe UI Semibold", 20))
        etiqueta_btc.pack()

        # Crear botones de valores predeterminados
        valores = [50000, 100000, 200000, 500000, 1000000, 2000000]
        botones_frame = tk.Frame(frame_retiro, bg="#14327D")
        botones_frame.pack(pady=20)

        def seleccionar_valor(valor):
            campo_valor.delete(0, tk.END)
            campo_valor.insert(0, str(valor))

        for valor in valores:
            boton_valor = tk.Button(botones_frame, text=f"${valor:,}", bg="white", fg="#14327D", font=("Segoe UI Semibold", 16), command=self.pantalla_confirmacion) #'''command=lambda v=valor: seleccionar_valor(v)''' 
            boton_valor.pack(side='left', padx=10, pady=10)

        # Campo de texto para valor exacto
        campo_valor = tk.Entry(frame_retiro, font=("Segoe UI Semibold", 16))
        campo_valor.pack(pady=10)

        # Botón para confirmar
        
        def confirmar(): #validacion del campo de texto
            valor_ingresado = campo_valor.get().strip()
            mensaje_error.config(text="")  # Limpiar mensaje de error
            if not valor_ingresado:
                # Si el campo de texto está vacío
                mensaje_error.config(text="Por favor ingrese un valor.")
                return
            try:
                valor_entero = int(valor_ingresado)
                if valor_entero % 10000 == 0 and valor_entero <= 2000000:
                    # Si el valor es múltiplo de 10,000 y menor o igual a 2,000,000, la función pantalla_confirmacion se llama
                    self.pantalla_confirmacion()
                else:
                    # Si el valor ingresado no cumple con los requisitos
                    mensaje_error.config(text="El valor ingresado es inválido.")
            except ValueError:
                # Si el valor ingresado no es un número válido, muestra un mensaje de error
                mensaje_error.config(text="Por favor ingrese un número válido.")

        boton_confirmar = tk.Button(frame_retiro, text="Confirmar", bg="white", fg="#14327D", font=("Segoe UI Semibold", 20), command=confirmar)
        boton_confirmar.pack(pady=10)
       
        # Etiqueta para mostrar mensaje de error
        mensaje_error = tk.Label(frame_retiro, text="", bg="#14327D", fg="red", font=("Segoe UI Semibold", 14))
        mensaje_error.pack()
    
        # Boton otras operaciones
        boton_otras_operaciones = tk.Button(frame_retiro, text="Otras Operaciones", bg="white", fg="#14327D", font=("Segoe UI Semibold", 20), command=self.pantalla_principal)
        boton_otras_operaciones.pack(pady=10)

        self.cambiar_pantalla(frame_retiro)

    def pantalla_principal(self):
        frame_principal = tk.Frame(self, bg="#14327D")
        frame_principal.pack(expand=True, fill="both")

        # Logo del Banco de Bogotá
        label_logo = tk.Label(frame_principal, image=self.logo_img, bg="#14327D")
        label_logo.pack(pady=10)

        # Mostrar el saldo actual y su equivalente en BTC
        saldo_actual = self.saldo_actual
        valor_btc = self.valor_btc
        equivalente_btc = saldo_actual / valor_btc

        etiqueta_saldo = tk.Label(frame_principal, text=f"El saldo de su cuenta es: ${saldo_actual:,.0f} lo que equivale en bitcoins a {equivalente_btc:.2f} BTC", bg="#14327D", fg="white", font=("Segoe UI Semibold", 20))
        etiqueta_saldo.pack(pady=20)

        # Crear los botones de funcionalidades
        frame_botones = tk.Frame(frame_principal, bg="#14327D")
        frame_botones.pack(pady=20)

        boton_extractos = tk.Button(frame_botones, text="Extractos", bg="white", fg="#14327D", font=("Segoe UI Semibold", 20), command=self.pantalla_confirmacion)
        boton_extractos.grid(row=0, column=0, padx=20, pady=10)

        boton_transferencias = tk.Button(frame_botones, text="Transferencias", bg="white", fg="#14327D", font=("Segoe UI Semibold", 20), command=self.pantalla_transferencias)
        boton_transferencias.grid(row=0, column=1, padx=20, pady=10)

        boton_cerrar_sesion = tk.Button(frame_principal, text="Cerrar sesión", bg="white", fg="#14327D", font=("Segoe UI Semibold", 20), command=self.pantalla_inicio)
        boton_cerrar_sesion.pack(pady=20)

        self.cambiar_pantalla(frame_principal)

    def pantalla_transferencias(self):
        cuenta_origen = "2347-8934-5678-9234" # self.cuenta_origen
        self.cuentas_destino = [
            {"titular": "Julian Grosso", "numero": "1234-5678-1011-1213"},
            {"titular": "Juan Montes", "numero": "1415-1617-1819-2021"},
            {"titular": "Samuel Perez", "numero": "2223-2425-2627-2829"},
            {"titular": "Laura Garcia", "numero": "3031-3233-3435-3637"},
            # Agregar más cuentas si es necesario, se hace desde las que ya se encuentran registradas en la BD
        ]


        frame_transferencias = tk.Frame(self, bg="#14327D")
        frame_transferencias.pack(expand=True, fill="both")

        # Logo del Banco de Bogotá
        label_logo = tk.Label(frame_transferencias, image=self.logo_img, bg="#14327D")
        label_logo.pack(pady=10)

        # Mostrar la información de la cuenta de origen
        etiqueta_cuenta_origen = tk.Label(frame_transferencias, text=f"Cuenta de origen: {cuenta_origen}", bg="#14327D", fg="white", font=("Segoe UI Semibold", 20))
        etiqueta_cuenta_origen.pack(pady=20)

        # Crear un marco para el menú desplegable
        frame_menu = tk.Frame(frame_transferencias, bg="#14327D")
        frame_menu.pack(pady=10)

        # Crear el menú desplegable con las opciones de cuenta de destino
        variable_cuenta_destino = tk.StringVar()
        scrollbar = tk.Scrollbar(frame_menu, orient="vertical")
        menu_cuenta_destino = tk.Listbox(frame_menu, listvariable=variable_cuenta_destino, yscrollcommand=scrollbar.set, height=5, width=40, font=("Segoe UI Semibold", 16))
        scrollbar.config(command=menu_cuenta_destino.yview)
        scrollbar.pack(side="right", fill="y")
        menu_cuenta_destino.pack(side="left", fill="both", expand=True)

        # Añadir las cuentas destino al menú desplegable
        for cuenta in self.cuentas_destino:
            menu_cuenta_destino.insert("end", f"{cuenta['titular']} - {cuenta['numero']}")

        # Crear campo de texto para el monto a transferir
        etiqueta_monto = tk.Label(frame_transferencias, text="Monto a transferir:", bg="#14327D", fg="white", font=("Segoe UI Semibold", 20))
        etiqueta_monto.pack(pady=10)
        entry_monto = tk.Entry(frame_transferencias, font=("Segoe UI Semibold", 16))
        entry_monto.pack(pady=10)

        def confirmar_transferencia(): #validacion del campo de texto
            valor_ingresado = entry_monto.get().strip()
            mensaje_error.config(text="")  # Limpiar mensaje de error
            if not valor_ingresado:
                # Si el campo de texto está vacío
                mensaje_error.config(text="Por favor ingrese un valor.")
                return
            try:
                valor_entero = int(valor_ingresado)
                if valor_entero < 30000000:
                    # Debe ser menor a 30 millones (limite diario de transferencias)
                    self.pantalla_confirmacion()
                else:
                    # Si el valor ingresado no cumple con los requisitos
                    mensaje_error.config(text="El valor ingresado es inválido, debe ser menor a 30'000.000.")
            except ValueError:
                # Si el valor ingresado no es un número válido, muestra un mensaje de error
                mensaje_error.config(text="Por favor ingrese un valor válido.")

                
        # Crear los botones de confirmar y regresar
        frame_botones = tk.Frame(frame_transferencias, bg="#14327D")
        frame_botones.pack(pady=20)

        boton_confirmar = tk.Button(frame_botones, text="Confirmar", bg="white", fg="#14327D", font=("Segoe UI Semibold", 20), command=confirmar_transferencia)
        boton_confirmar.grid(row=0, column=0, padx=20, pady=10)

        boton_regresar = tk.Button(frame_botones, text="Regresar", bg="white", fg="#14327D", font=("Segoe UI Semibold", 20), command= self.pantalla_principal)
        boton_regresar.grid(row=0, column=1, padx=20, pady=10)


        # Etiqueta para mostrar mensaje de error
        mensaje_error = tk.Label(frame_transferencias, text="", bg="#14327D", fg="red", font=("Segoe UI Semibold", 14))
        mensaje_error.pack()

        self.cambiar_pantalla(frame_transferencias)

    def pantalla_confirmacion(self):
        # Crear el frame principal
        frame_confirmacion = tk.Frame(self, bg="#14327D")
        frame_confirmacion.pack(expand=True, fill="both")
    
        # Logo del Banco de Bogotá
        label_logo = tk.Label(frame_confirmacion, image=self.logo_img, bg="#14327D")
        label_logo.pack(pady=10)
    
        # Mensaje de confirmación
        label_mensaje = tk.Label(frame_confirmacion, text="Operación Realizada!\nInformación:", bg="#14327D", fg="white", font=("Segoe UI Semibold", 24))
        label_mensaje.pack(pady=20)
    
        # Marco para la información de la operación
        info_frame = tk.Frame(frame_confirmacion, bg="white")
        info_frame.pack(pady=20, padx=20, fill="both", expand=True)
    
        #EJEMPLO LABEL PARA RETIRO
        '''# Información de la operación
        info_label = tk.Label(info_frame, text="""
        INFORMACION GENERAL DE LA OPERACION
        TIPO DE OPERACION: Retiro
        CUENTA: 1234-5678-9012
        MONTO RETIRADO: $500.000
        SALDO DISPONIBLE: $9.500.000
        SALDO DISPONIBLE (BTC): 0.24 BTC
        FECHA: 20/05/2024
        """, bg="white", fg="black", font=("Segoe UI Semibold", 16), justify="left")
        info_label.pack(pady=20, padx=20)'''

        # EJEMPLO LABEL PARA TRANSFERENCIA
        '''info_label = tk.Label(info_frame, text="""
        INFORMACION GENERAL DE LA OPERACION
        TIPO DE OPERACION: Transferencia
        CUENTA DE ORIGEN: 1234-5678-9012
        CUENTA DE DESTINO: 9876-5432-1098
        NOMBRE DEL DESTINATARIO: Juan Perez
        MONTO TRANSFERIDO: $200.000
        FECHA: 20/05/2024
        """, bg="white", fg="black", font=("Segoe UI Semibold", 16), justify="left")
        info_label.pack(pady=20, padx=20)'''
        
        # EJEMPLO LABEL EXTRACTOS
        '''# Información del extracto
        info_label = tk.Label(info_frame, text="""
        INFORMACION GENERAL DE LA OPERACION
        TIPO DE OPERACION: Extracto
        CUENTA: 1234-5678-9012
        FECHA: 20/05/2024

        MOVIMIENTOS:
        1. Fecha: 01/05/2024 - Descripción: Depósito - Monto: $1.000.000
        2. Fecha: 05/05/2024 - Descripción: Retiro - Monto: $200.000
        3. Fecha: 10/05/2024 - Descripción: Transferencia a 9876-5432-1098 - Monto: $300.000
        4. Fecha: 15/05/2024 - Descripción: Pago de servicios - Monto: $150.000
        5. Fecha: 18/05/2024 - Descripción: Depósito - Monto: $500.000

        SALDO FINAL: $1.850.000
        """, bg="white", fg="black", font=("Segoe UI Semibold", 16), justify="left")
        info_label.pack(pady=20, padx=20)'''
        
        # Botones de acción

        botones_frame = tk.Frame(frame_confirmacion, bg="#14327D")
        botones_frame.pack(pady=20)
    
        boton_otras_operaciones = tk.Button(botones_frame, text="Otra operación", bg="white", fg="#14327D", font=("Segoe UI Semibold", 16), command=self.pantalla_retiro)
        boton_otras_operaciones.pack(side="left", padx=20)
    
        boton_imprimir = tk.Button(botones_frame, text="Imprimir Recibo", bg="white", fg="#14327D", font=("Segoe UI Semibold", 16))
        boton_imprimir.pack(side="left", padx=20)
    
        boton_finalizar = tk.Button(botones_frame, text="Finalizar", bg="white", fg="#14327D", font=("Segoe UI Semibold", 16), command=self.pantalla_inicio)
        boton_finalizar.pack(side="left", padx=20)
    
        self.cambiar_pantalla(frame_confirmacion)
    
    def cambiar_pantalla(self, nueva_pantalla):
            if self.current_screen:
                self.current_screen.destroy()
            self.current_screen = nueva_pantalla
    



"""
************************************************************
FUNCIONES PARA LA BASE DE DATOS
************************************************************

"""

def crear_tablas():
    conexion = sqlite3.connect('proyecto.db')
    cursor = conexion.cursor()
    
    crear_cliente = ('''

        -- -----------------------------------------------------
        -- Table `Cliente`
        -- -----------------------------------------------------
        CREATE TABLE IF NOT EXISTS `Cliente` (
            `cedula` INT NOT NULL,
            `primer_nombre` VARCHAR(45) NULL,
            `primer_apellido` VARCHAR(45) NULL,
            `tipo_documento` VARCHAR(2) NULL,
            `celular` INT NULL,
            `pin_celular` INT NULL,
            `pin_cedula` INT NULL,
            PRIMARY KEY (`cedula`)
        );
        
        ''')
    crear_cuenta = ('''
        -- -----------------------------------------------------
        -- Table `Cuenta`
        -- -----------------------------------------------------
        CREATE TABLE IF NOT EXISTS `Cuenta` (
            `num_cuenta` INT NOT NULL,
            `estado` BOOLEAN NOT NULL,
            `tipo_cuenta` VARCHAR(45) NULL,
            `saldo` DOUBLE NULL,
            `cedula_cliente` INT NULL,
            `operable_transferible` BOOLEAN NULL,
            PRIMARY KEY (`num_cuenta`),
            FOREIGN KEY (`cedula_cliente`) REFERENCES `Cliente` (`cedula`)
        );
    ''')
    crear_transferencias = ('''
        -- -----------------------------------------------------
        -- Table `Transferencias`
        -- -----------------------------------------------------
        CREATE TABLE IF NOT EXISTS `Transferencias` (
            `codigo` INT NOT NULL,
            `num_cuenta_destino` INT NULL,
            `monto_transferir` DOUBLE NULL,
            `fecha` DATE NULL,
            PRIMARY KEY (`codigo`)
        )
    ''')
    
    crear_retiros = ('''
        -- -----------------------------------------------------
        -- Table `Retiros`
        -- -----------------------------------------------------
        CREATE TABLE IF NOT EXISTS `Retiros` (
            `codigo` INT NOT NULL,
            `cantidad_retirar` DOUBLE NULL,
            `fecha` DATE NULL,
            PRIMARY KEY (`codigo`)
        );
    ''')
    
    crear_operacion = ('''
        -- -----------------------------------------------------
        -- Table `Operacion`
        -- -----------------------------------------------------
        CREATE TABLE IF NOT EXISTS `Operacion` (
            `idOperacion` INT NOT NULL,
            `tipo_operacion` INT NULL,
            `num_cuenta` INT NULL,
            PRIMARY KEY (`idOperacion`),
            FOREIGN KEY (`num_cuenta`) REFERENCES `Cuenta` (`num_cuenta`),
            FOREIGN KEY (`tipo_operacion`) REFERENCES `Retiros` (`codigo`),
            FOREIGN KEY (`tipo_operacion`) REFERENCES `Transferencias` (`codigo`)
        );
    ''')
    crear_comprobante = ('''
        -- -----------------------------------------------------
        -- Table `Comprobante`
        -- -----------------------------------------------------
        CREATE TABLE IF NOT EXISTS `Comprobante` (
            `num_comprobante` INTEGER PRIMARY KEY AUTOINCREMENT,
            `codigo_operacion` INT NULL,
            FOREIGN KEY (`codigo_operacion`) REFERENCES `Operacion` (`idOperacion`)
        );
    ''')
    crear_tarjeta = ('''
        -- -----------------------------------------------------
        -- Table .`Tarjeta`
        -- -----------------------------------------------------
        CREATE TABLE IF NOT EXISTS `Tarjeta` (
            `idTarjeta` INTEGER PRIMARY KEY AUTOINCREMENT,
            `fecha_vencimiento` DATE NULL,
            `pin` INT NULL,
            `estado` BOOLEAN NULL,
            `num_cuenta` INT NOT NULL,
            FOREIGN KEY (`num_cuenta`) REFERENCES `Cuenta` (`num_cuenta`)
        );
    ''')
    
    cursor.execute(crear_cliente)
    cursor.execute(crear_cuenta)
    cursor.execute(crear_transferencias)
    cursor.execute(crear_retiros)
    cursor.execute(crear_operacion)
    cursor.execute(crear_comprobante)
    cursor.execute(crear_tarjeta)
    conexion.commit()
    
    print("Creacion de tablas exitosa")
    
    conexion.close()

def consultar_tablas():
    conexion = sqlite3.connect('proyecto.db')
    cursor = conexion.cursor()
    
    # Consultar tabla Cliente
    cursor.execute("SELECT * FROM Cliente")
    clientes = cursor.fetchall()
    print("Tabla Cliente:")
    for cliente in clientes:
        print(cliente)
    
    # Consultar tabla Cuenta
    cursor.execute("SELECT * FROM Cuenta")
    cuentas = cursor.fetchall()
    print("Tabla Cuenta:")
    for cuenta in cuentas:
        print(cuenta)
    
    # Consultar tabla Transferencias
    cursor.execute("SELECT * FROM Transferencias")
    transferencias = cursor.fetchall()
    print("Tabla Transferencias:")
    for transferencia in transferencias:
        print(transferencia)
    
    # Consultar tabla Retiros
    cursor.execute("SELECT * FROM Retiros")
    retiros = cursor.fetchall()
    print("Tabla Retiros:")
    for retiro in retiros:
        print(retiro)
    
    # Consultar tabla Operacion
    cursor.execute("SELECT * FROM Operacion")
    operaciones = cursor.fetchall()
    print("Tabla Operacion:")
    for operacion in operaciones:
        print(operacion)
    
    # Consultar tabla Comprobante
    cursor.execute("SELECT * FROM Comprobante")
    comprobantes = cursor.fetchall()
    print("Tabla Comprobante:")
    for comprobante in comprobantes:
        print(comprobante)
    
    # Consultar tabla Tarjeta
    cursor.execute("SELECT * FROM Tarjeta")
    tarjetas = cursor.fetchall()
    print("Tabla Tarjeta:")
    for tarjeta in tarjetas:
        print(tarjeta)
    
    conexion.close()

def insertar_datos():
    conexion = sqlite3.connect('proyecto.db')
    cursor = conexion.cursor()
    
    # Importar el módulo random

    # Generar una fecha aleatoria
    year = random.randint(2000, 2022)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    fecha_aleatoria = datetime.date(year, month, day)

    # Insertar datos en la tabla Cliente
    cursor.execute("INSERT INTO Cliente (cedula, primer_nombre, primer_apellido, tipo_documento, celular, pin_celular, pin_cedula) VALUES (?, ?, ?, ?, ?, ?, ?)", (1014738069, "Julian", "Roso", "CC", 3123819066, 1234, 9876))
    cursor.execute("INSERT INTO Cliente (cedula, primer_nombre, primer_apellido, tipo_documento, celular, pin_celular, pin_cedula) VALUES (?, ?, ?, ?, ?, ?, ?)", (1000252243, "Jane", "Smith", "CC", 3123768744, 4321, 4567))
    cursor.execute("INSERT INTO Cliente (cedula, primer_nombre, primer_apellido, tipo_documento, celular, pin_celular, pin_cedula) VALUES (?, ?, ?, ?, ?, ?, ?)", (1045738934, "Alice", "Johnson", "CC", 3153765490, 7654, 1234))
    cursor.execute("INSERT INTO Cliente (cedula, primer_nombre, primer_apellido, tipo_documento, celular, pin_celular, pin_cedula) VALUES (?, ?, ?, ?, ?, ?, ?)", (1043234765, "Bob", "Williams", "CC", 3114325476, 2222, 3333))
    cursor.execute("INSERT INTO Cliente (cedula, primer_nombre, primer_apellido, tipo_documento, celular, pin_celular, pin_cedula) VALUES (?, ?, ?, ?, ?, ?, ?)", (1087543562, "Eve", "Brown", "CC", 3123874823, 9999, 6666))

    # Insertar datos en la tabla Cuenta
    cursor.execute("INSERT INTO Cuenta (num_cuenta, estado, tipo_cuenta, saldo, cedula_cliente, operable_transferible) VALUES (?, ?, ?, ?, ?, ?)", (9876543210123456, 1, "Ahorros", 1000000, 1014738069, 1))
    cursor.execute("INSERT INTO Cuenta (num_cuenta, estado, tipo_cuenta, saldo, cedula_cliente, operable_transferible) VALUES (?, ?, ?, ?, ?, ?)", (1234567890123323, 1, "Corriente", 500000, 1000252243, 1))
    cursor.execute("INSERT INTO Cuenta (num_cuenta, estado, tipo_cuenta, saldo, cedula_cliente, operable_transferible) VALUES (?, ?, ?, ?, ?, ?)", (1111111111111111, 1, "Ahorros", 2000000, 1045738934, 1))
    cursor.execute("INSERT INTO Cuenta (num_cuenta, estado, tipo_cuenta, saldo, cedula_cliente, operable_transferible) VALUES (?, ?, ?, ?, ?, ?)", (2222222222222222, 1, "Corriente", 1500000, 1043234765, 1))
    cursor.execute("INSERT INTO Cuenta (num_cuenta, estado, tipo_cuenta, saldo, cedula_cliente, operable_transferible) VALUES (?, ?, ?, ?, ?, ?)", (3333333333333333, 1, "Ahorros", 3000000, 1087543562, 1))

    # Insertar datos en la tabla Transferencias
    cursor.execute("INSERT INTO Transferencias (codigo, num_cuenta_destino, monto_transferir, fecha) VALUES (?, ?, ?, ?)", (1, 3333333333333333, 500000, fecha_aleatoria))
    cursor.execute("INSERT INTO Transferencias (codigo, num_cuenta_destino, monto_transferir, fecha) VALUES (?, ?, ?, ?)", (2, 3333333333333333, 100000, fecha_aleatoria))
    cursor.execute("INSERT INTO Transferencias (codigo, num_cuenta_destino, monto_transferir, fecha) VALUES (?, ?, ?, ?)", (3, 3333333333333333, 200000, fecha_aleatoria))
    cursor.execute("INSERT INTO Transferencias (codigo, num_cuenta_destino, monto_transferir, fecha) VALUES (?, ?, ?, ?)", (4, 3333333333333333, 150000, fecha_aleatoria))
    cursor.execute("INSERT INTO Transferencias (codigo, num_cuenta_destino, monto_transferir, fecha) VALUES (?, ?, ?, ?)", (5, 3333333333333333, 300000, fecha_aleatoria))

    # Insertar datos en la tabla Operacion
    cursor.execute("INSERT INTO Operacion (idOperacion, tipo_operacion, num_cuenta) VALUES (?, ?, ?)", (1, 1, 3333333333333333))
    cursor.execute("INSERT INTO Operacion (idOperacion, tipo_operacion, num_cuenta) VALUES (?, ?, ?)", (2, 2, 3333333333333333))
    cursor.execute("INSERT INTO Operacion (idOperacion, tipo_operacion, num_cuenta) VALUES (?, ?, ?)", (3, 1, 3333333333333333))
    cursor.execute("INSERT INTO Operacion (idOperacion, tipo_operacion, num_cuenta) VALUES (?, ?, ?)", (4, 1, 3333333333333333))
    cursor.execute("INSERT INTO Operacion (idOperacion, tipo_operacion, num_cuenta) VALUES (?, ?, ?)", (5, 2, 3333333333333333))

    # Insertar datos en la tabla Comprobante
    cursor.execute("INSERT INTO Comprobante (num_comprobante, codigo_operacion) VALUES (?, ?)", (1, 1))
    cursor.execute("INSERT INTO Comprobante (num_comprobante, codigo_operacion) VALUES (?, ?)", (2, 2))
    cursor.execute("INSERT INTO Comprobante (num_comprobante, codigo_operacion) VALUES (?, ?)", (3, 3))
    cursor.execute("INSERT INTO Comprobante (num_comprobante, codigo_operacion) VALUES (?, ?)", (4, 4))
    cursor.execute("INSERT INTO Comprobante (num_comprobante, codigo_operacion) VALUES (?, ?)", (5, 5))

    # Insertar datos en la tabla Tarjeta
    cursor.execute("INSERT INTO Tarjeta (idTarjeta, fecha_vencimiento, pin, estado, num_cuenta) VALUES (?, ?, ?, ?, ?)", (1, fecha_aleatoria, 1234, 1, 9876543210123456))
    cursor.execute("INSERT INTO Tarjeta (idTarjeta, fecha_vencimiento, pin, estado, num_cuenta) VALUES (?, ?, ?, ?, ?)", (2, fecha_aleatoria, 4321, 1, 1234567890123323))
    cursor.execute("INSERT INTO Tarjeta (idTarjeta, fecha_vencimiento, pin, estado, num_cuenta) VALUES (?, ?, ?, ?, ?)", (3, fecha_aleatoria, 1111, 1, 1111111111111111))
    cursor.execute("INSERT INTO Tarjeta (idTarjeta, fecha_vencimiento, pin, estado, num_cuenta) VALUES (?, ?, ?, ?, ?)", (4, fecha_aleatoria, 2222, 1, 2222222222222222))
    cursor.execute("INSERT INTO Tarjeta (idTarjeta, fecha_vencimiento, pin, estado, num_cuenta) VALUES (?, ?, ?, ?, ?)", (5, fecha_aleatoria, 3333, 1, 3333333333333333))
    
    conexion.commit()
    print("Datos insertados correctamente")
    
    conexion.close()
    
def borrar_datos():
    conexion = sqlite3.connect('proyecto.db')
    cursor = conexion.cursor()
    
    # Borrar datos de la tabla Cliente
    cursor.execute("DELETE FROM Cliente")
    
    # Borrar datos de la tabla Cuenta
    cursor.execute("DELETE FROM Cuenta")
    
    # Borrar datos de la tabla Transferencias
    cursor.execute("DELETE FROM Transferencias")
    
    # Borrar datos de la tabla Retiros
    cursor.execute("DELETE FROM Retiros")
    
    # Borrar datos de la tabla Operacion
    cursor.execute("DELETE FROM Operacion")
    
    # Borrar datos de la tabla Comprobante
    cursor.execute("DELETE FROM Comprobante")
    
    # Borrar datos de la tabla Tarjeta
    cursor.execute("DELETE FROM Tarjeta")
    
    conexion.commit()
    print("Datos borrados correctamente")
    
    conexion.close()

if __name__ == "__main__":
    crear_tablas()
    borrar_datos()
    insertar_datos()
    # consultar_tablas()
    app = CajeroAutomatico()
    app.mainloop()
