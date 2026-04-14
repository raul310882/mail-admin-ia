import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from motor_reglas import MotorReglas, ProcesadorLotes

class InterfazClasificadorCorreos:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📧 Clasificador Inteligente de Correos")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Inicializar componentes
        self.motor_reglas = MotorReglas()
        self.procesador = ProcesadorLotes(self.motor_reglas)
        self.lote_actual = []
        self.indice_lote = 0
        self.carpetas_outlook = {}
        
        # Variables de estado
        self.seleccionados = {}
        self.carpetas_disponibles = []
        self.todos_seleccionados = False
        
        self.crear_interfaz()
        self.cargar_carpetas()
        self.actualizar_contador()
        
    def crear_interfaz(self):
        """Crea todos los componentes de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar pesos para que la interfaz se expanda
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        self.crear_header(main_frame)
        
        # Panel de control
        self.crear_panel_control(main_frame)
        
        # Lista de correos
        self.crear_lista_correos(main_frame)
        
        # Panel de detalles
        self.crear_panel_detalles(main_frame)
        
        # Barra de estado
        self.crear_barra_estado(main_frame)
    
    def crear_header(self, parent):
        """Crea el encabezado de la aplicación"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="📧 Clasificador Inteligente de Correos Outlook",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Contador de correos
        self.contador_label = ttk.Label(
            header_frame,
            text="📭 Correos no leídos: 0",
            font=('Arial', 12)
        )
        self.contador_label.pack(side=tk.RIGHT)
    
    def crear_panel_control(self, parent):
        """Crea el panel de control con botones"""
        control_frame = ttk.LabelFrame(parent, text="🎛️ Control", padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones principales
        ttk.Button(
            control_frame, 
            text="🔄 Cargar Correos", 
            command=self.cargar_lote_correos
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="✅ Mover Seleccionados", 
            command=self.mover_seleccionados
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="⏭️ Siguiente Lote", 
            command=self.siguiente_lote
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="📋 Lista Blanca", 
            command=self.mostrar_lista_blanca
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="🔧 Configurar Reglas", 
            command=self.configurar_reglas
        ).pack(side=tk.LEFT, padx=5)
        
        # Indicador de lote
        self.lote_label = ttk.Label(control_frame, text="Lote: 0/0")
        self.lote_label.pack(side=tk.RIGHT, padx=10)
    
    def crear_lista_correos(self, parent):
        """Crea la lista de correos con checkboxes"""
        lista_frame = ttk.LabelFrame(parent, text="📨 Correos para Clasificar", padding="10")
        lista_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Crear Treeview con checkboxes
        columns = ('Seleccionar', 'Remitente', 'Asunto', 'Clasificación', 'Fecha')
        self.tree = ttk.Treeview(lista_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('Seleccionar', text='☐', command=self.toggle_seleccionar_todos)
        self.tree.heading('Remitente', text='Remitente')
        self.tree.heading('Asunto', text='Asunto')
        self.tree.heading('Clasificación', text='Clasificación IA')
        self.tree.heading('Fecha', text='Fecha')
        
        # Anchos de columna
        self.tree.column('Seleccionar', width=60, anchor='center')
        self.tree.column('Remitente', width=200)
        self.tree.column('Asunto', width=300)
        self.tree.column('Clasificación', width=200)
        self.tree.column('Fecha', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Eventos
        self.tree.bind('<ButtonRelease-1>', self.on_item_click)
        self.tree.bind('<Double-1>', self.on_item_double_click)
    
    def crear_panel_detalles(self, parent):
        """Crea el panel de detalles del correo seleccionado"""
        detalles_frame = ttk.LabelFrame(parent, text="📄 Detalles del Correo", padding="10")
        detalles_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Información del correo
        info_frame = ttk.Frame(detalles_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text="Remitente:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.remitente_label = ttk.Label(info_frame, text="")
        self.remitente_label.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Email:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.email_label = ttk.Label(info_frame, text="")
        self.email_label.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Asunto:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.asunto_label = ttk.Label(info_frame, text="", wraplength=400)
        self.asunto_label.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        ttk.Label(info_frame, text="Para:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.destinatarios_label = ttk.Label(info_frame, text="", wraplength=400)
        self.destinatarios_label.grid(row=3, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        ttk.Label(info_frame, text="CC:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=2)
        self.cc_label = ttk.Label(info_frame, text="", wraplength=400)
        self.cc_label.grid(row=4, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Clasificación:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=2)
        self.clasificacion_label = ttk.Label(info_frame, text="")
        self.clasificacion_label.grid(row=5, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # ComboBox para cambiar clasificación
        ttk.Label(info_frame, text="Mover a:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=2)
        self.carpeta_combo = ttk.Combobox(info_frame, width=40, state='readonly')
        self.carpeta_combo.grid(row=6, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Cuerpo del correo
        ttk.Label(detalles_frame, text="Cuerpo del mensaje:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        self.cuerpo_text = scrolledtext.ScrolledText(detalles_frame, height=15, width=50, wrap=tk.WORD)
        self.cuerpo_text.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        accion_frame = ttk.Frame(detalles_frame)
        accion_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(accion_frame, text="📌 Agregar a Lista Blanca", command=self.agregar_lista_blanca).pack(side=tk.LEFT, padx=5)
        ttk.Button(accion_frame, text="💾 Guardar Regla", command=self.guardar_regla).pack(side=tk.LEFT, padx=5)
        ttk.Button(accion_frame, text="📤 Mover Ahora", command=self.mover_correo_actual).pack(side=tk.LEFT, padx=5)
    
    def crear_barra_estado(self, parent):
        """Crea la barra de estado"""
        estado_frame = ttk.Frame(parent)
        estado_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.estado_label = ttk.Label(estado_frame, text="Listo para procesar correos...", relief=tk.SUNKEN)
        self.estado_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def cargar_carpetas(self):
        """Carga las carpetas disponibles de Outlook"""
        try:
            self.carpetas_outlook = self.motor_reglas.obtener_carpetas_outlook()
            self.carpetas_disponibles = list(self.carpetas_outlook.keys())
            
            # Actualizar combobox
            self.carpeta_combo['values'] = self.carpetas_disponibles
            if self.carpetas_disponibles:
                self.carpeta_combo.set(self.carpetas_disponibles[0])
                
            self.actualizar_estado("Carpetas de Outlook cargadas correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las carpetas: {e}")
    
    def cargar_lote_correos(self):
        """Carga un lote de correos para procesar"""
        try:
            self.actualizar_estado("Cargando correos...")
            self.lote_actual = self.procesador.obtener_lote_correos(self.indice_lote)
            
            if not self.lote_actual:
                messagebox.showinfo("Información", "No hay correos no leídos para procesar")
                return
            
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Reiniciar estado del lote
            self.seleccionados = {}
            self.todos_seleccionados = False
            self.tree.heading('Seleccionar', text='☐', command=self.toggle_seleccionar_todos)
            
            # Agregar correos al treeview
            for i, correo in enumerate(self.lote_actual):
                # Formatear fecha
                fecha_str = correo['fecha'].strftime('%d/%m %H:%M') if correo['fecha'] else 'N/A'
                
                # Insertar en treeview (iid=str(i) para recuperar índice en clicks)
                item = self.tree.insert('', 'end', iid=str(i), values=(
                    '☐',  # Checkbox vacío
                    correo['remitente'][:30] + '...' if len(correo['remitente']) > 30 else correo['remitente'],
                    correo['asunto'][:40] + '...' if len(correo['asunto']) > 40 else correo['asunto'],
                    correo['clasificacion'],
                    fecha_str
                ))
                self.seleccionados[i] = False
            
            # Actualizar indicador de lote
            total_correos = self.procesador.contar_correos_no_leidos()
            tamano_lote = self.procesador.tamano_lote
            lote_actual_num = (self.indice_lote // tamano_lote) + 1
            total_lotes = max(1, ((total_correos - 1) // tamano_lote) + 1) if total_correos > 0 else 1
            self.lote_label.config(text=f"Lote: {lote_actual_num}/{total_lotes}")
            
            self.actualizar_estado(f"Se cargaron {len(self.lote_actual)} correos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar correos:\n{e}")
            self.actualizar_estado(f"Error al cargar correos: {e}")
    
    def on_item_click(self, event):
        """Maneja el clic en un item del treeview"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)

            if not item:
                return

            index = int(item)

            if column == '#1':  # Columna de checkbox: alternar selección
                self.seleccionados[index] = not self.seleccionados[index]
                checkbox = '☑' if self.seleccionados[index] else '☐'
                values = list(self.tree.item(item)['values'])
                values[0] = checkbox
                self.tree.item(item, values=values)
                self.actualizar_estado_seleccionar_todos()

            # Cargar detalles en el panel derecho para cualquier columna
            self.cargar_detalles_correo(index)
    
    def on_item_double_click(self, event):
        """Maneja doble clic para cargar detalles o cambiar clasificación"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if item:
            # Obtener índice del iid (que es str(i) como se definió en cargar_lote_correos)
            try:
                index = int(item)
                
                # Si el clic es en la columna de clasificación (columna #4)
                if column == '#4':
                    self.abrir_dialogo_clasificacion(index, item)
                else:
                    self.cargar_detalles_correo(index)
            except ValueError:
                pass  # Si no es un índice válido, ignorar
    
    def abrir_dialogo_clasificacion(self, index, tree_item):
        """Abre un diálogo para cambiar rápidamente la clasificación"""
        if 0 <= index < len(self.lote_actual):
            correo = self.lote_actual[index]
            clasificacion_actual = correo['clasificacion']
            
            # Detectar asuntos similares
            asuntos_similares = self.motor_reglas.detectar_asunto_similar(correo['asunto'])
            
            # Crear diálogo
            dialogo = tk.Toplevel(self.root)
            dialogo.title("Cambiar Clasificación")
            dialogo.geometry("450x450")
            dialogo.transient(self.root)
            dialogo.grab_set()
            
            # Centrar diálogo
            dialogo.update_idletasks()
            x = (dialogo.winfo_screenwidth() // 2) - (dialogo.winfo_width() // 2)
            y = (dialogo.winfo_screenheight() // 2) - (dialogo.winfo_height() // 2)
            dialogo.geometry(f"+{x}+{y}")
            
            # Frame principal con scroll
            canvas = tk.Canvas(dialogo)
            scrollbar = ttk.Scrollbar(dialogo, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            frame = ttk.Frame(scrollable_frame, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Información del correo
            ttk.Label(frame, text="📧 Información del Correo", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
            
            destinatarios = correo.get('destinatarios', '') or correo.get('cc', '') or 'No especificado'
            info_text = f"De: {correo['remitente']}\nPara: {destinatarios[:50]}...\nAsunto: {correo['asunto'][:60]}..."
            ttk.Label(frame, text=info_text, wraplength=350).pack(anchor=tk.W, pady=(0, 20))
            
            # Selección de clasificación
            ttk.Label(frame, text="🎯 Nueva Clasificación:", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
            
            clasificacion_combo = ttk.Combobox(
                frame, 
                values=self.carpetas_disponibles,
                width=40,
                state='readonly'
            )
            clasificacion_combo.set(clasificacion_actual)
            clasificacion_combo.pack(fill=tk.X, pady=(5, 20))
            
            # Mostrar sugerencias de asuntos similares si existen
            if asuntos_similares:
                ttk.Label(frame, text="💡 Asuntos similares encontrados:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
                for patron, carpeta_sugerida, similitud in asuntos_similares:
                    similitud_pct = int(similitud * 100)
                    sugerencia_text = f"• '{patron[:40]}...' → {carpeta_sugerida} ({similitud_pct}% similar)"
                    ttk.Label(frame, text=sugerencia_text, wraplength=350, foreground='#0066cc').pack(anchor=tk.W, padx=10)
                ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)
            
            # Opciones para guardar regla
            guardar_regla_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                frame, 
                text="💾 Guardar como regla", 
                variable=guardar_regla_var
            ).pack(anchor=tk.W, pady=(0, 5))
            
            incluir_destinatario_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                frame, 
                text="👥 Incluir destinatario (regla más específica)", 
                variable=incluir_destinatario_var
            ).pack(anchor=tk.W, pady=(0, 5))
            
            incluir_asunto_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                frame, 
                text="📝 Incluir asunto (aprende patrones similares)", 
                variable=incluir_asunto_var
            ).pack(anchor=tk.W, pady=(0, 20))
            
            # Botones
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill=tk.X)
            
            def confirmar_cambio():
                nueva_clasificacion = clasificacion_combo.get()
                if nueva_clasificacion:
                    # Actualizar en el Treeview
                    values = list(self.tree.item(tree_item)['values'])
                    values[3] = nueva_clasificacion
                    self.tree.item(tree_item, values=values)
                    
                    # Actualizar en el lote
                    self.lote_actual[index]['clasificacion'] = nueva_clasificacion
                    
                    # Guardar como regla si se seleccionó
                    if guardar_regla_var.get():
                        destinatario = correo.get('destinatarios', '') or correo.get('cc', '') or ''
                        self.motor_reglas.guardar_regla_aprendida(
                            correo['email_remitente'], 
                            nueva_clasificacion,
                            incluir_destinatario=incluir_destinatario_var.get(),
                            destinatario=destinatario,
                            incluir_asunto=incluir_asunto_var.get(),
                            asunto=correo['asunto']
                        )
                        
                        # Construir mensaje de confirmación
                        tipo_regla = []
                        if incluir_asunto_var.get():
                            tipo_regla.append("asunto")
                        if incluir_destinatario_var.get():
                            tipo_regla.append("destinatario")
                        tipo_regla.append("remitente")
                        
                        mensaje_tipo = " + ".join(tipo_regla)
                        messagebox.showinfo("Éxito", f"Clasificación cambiada y regla guardada ({mensaje_tipo})")
                    else:
                        messagebox.showinfo("Éxito", f"Clasificación cambiada temporalmente")
                    
                    dialogo.destroy()
            
            ttk.Button(btn_frame, text="✅ Confirmar", command=confirmar_cambio).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="❌ Cancelar", command=dialogo.destroy).pack(side=tk.RIGHT, padx=5)
    
    def cargar_detalles_correo(self, index):
        """Carga los detalles de un correo específico"""
        if 0 <= index < len(self.lote_actual):
            correo = self.lote_actual[index]
            
            self.remitente_label.config(text=correo['remitente'])
            self.email_label.config(text=correo['email_remitente'])
            self.asunto_label.config(text=correo['asunto'])
            self.destinatarios_label.config(text=correo.get('destinatarios', ''))
            self.cc_label.config(text=correo.get('cc', ''))
            self.clasificacion_label.config(text=correo['clasificacion'])
            
            # Establecer carpeta sugerida
            if correo['clasificacion'] in self.carpetas_disponibles:
                self.carpeta_combo.set(correo['clasificacion'])
            
            # Cargar cuerpo
            self.cuerpo_text.delete(1.0, tk.END)
            self.cuerpo_text.insert(1.0, correo['cuerpo'])
            
            # Guardar referencia al correo actual
            self.indice_correo_actual = index
    
    def mover_seleccionados(self):
        """Mueve los correos seleccionados a sus carpetas"""
        seleccionados_count = sum(1 for seleccionado in self.seleccionados.values() if seleccionado)
        
        if seleccionados_count == 0:
            messagebox.showwarning("Advertencia", "No hay correos seleccionados")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Mover {seleccionados_count} correos seleccionados?"):
            try:
                movidos = 0
                for i, seleccionado in enumerate(self.seleccionados.items()):
                    index, esta_seleccionado = seleccionado
                    if esta_seleccionado and index < len(self.lote_actual):
                        correo = self.lote_actual[index]
                        carpeta_destino = correo['clasificacion']
                        
                        if self.mover_correo(correo['mensaje'], carpeta_destino):
                            movidos += 1
                            # Aprender de esta acción
                            self.motor_reglas.guardar_regla_aprendida(
                                correo['email_remitente'], 
                                carpeta_destino
                            )
                
                messagebox.showinfo("Éxito", f"Se movieron {movidos} correos correctamente")
                self.cargar_lote_correos()  # Recargar lote
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al mover correos: {e}")
    
    def mover_correo(self, mensaje, carpeta_destino):
        """Mueve un correo a la carpeta especificada"""
        try:
            if carpeta_destino in self.carpetas_outlook:
                carpeta = self.carpetas_outlook[carpeta_destino]
                mensaje.Move(carpeta)
                return True
            else:
                print(f"Carpeta no encontrada: {carpeta_destino}")
                return False
        except Exception as e:
            print(f"Error al mover correo: {e}")
            return False
    
    def siguiente_lote(self):
        """Carga el siguiente lote de correos"""
        self.indice_lote += self.procesador.tamano_lote
        self.cargar_lote_correos()

    def actualizar_estado_seleccionar_todos(self):
        """Sincroniza el estado visual del encabezado de selección"""
        if not self.seleccionados:
            self.todos_seleccionados = False
        else:
            self.todos_seleccionados = all(self.seleccionados.values())

        texto = '☑' if self.todos_seleccionados else '☐'
        self.tree.heading('Seleccionar', text=texto, command=self.toggle_seleccionar_todos)

    def toggle_seleccionar_todos(self):
        """Marca o desmarca todos los correos del lote con un clic en el encabezado"""
        if not self.lote_actual:
            return

        nuevo_estado = not self.todos_seleccionados
        for i in range(len(self.lote_actual)):
            self.seleccionados[i] = nuevo_estado
            item_id = str(i)
            if self.tree.exists(item_id):
                values = list(self.tree.item(item_id)['values'])
                values[0] = '☑' if nuevo_estado else '☐'
                self.tree.item(item_id, values=values)

        self.todos_seleccionados = nuevo_estado
        self.actualizar_estado_seleccionar_todos()
        self.actualizar_estado(
            f"{'Todos seleccionados' if nuevo_estado else 'Selección limpiada'}: {len(self.lote_actual)} correos"
        )
    
    def actualizar_contador(self):
        """Actualiza el contador de correos no leídos"""
        try:
            count = self.procesador.contar_correos_no_leidos()
            self.contador_label.config(text=f"📭 Correos no leídos: {count}")
        except:
            self.contador_label.config(text="📭 Correos no leídos: ?")
    
    def actualizar_estado(self, mensaje):
        """Actualiza la barra de estado"""
        self.estado_label.config(text=mensaje)
        self.root.update_idletasks()
    
    def agregar_lista_blanca(self):
        """Agrega el remitente actual a la lista blanca"""
        if hasattr(self, 'indice_correo_actual') and self.indice_correo_actual < len(self.lote_actual):
            correo = self.lote_actual[self.indice_correo_actual]
            remitente = correo['email_remitente']
            
            motivo = simpledialog.askstring("Lista Blanca", "Motivo (opcional):")
            if self.motor_reglas.agregar_a_lista_blanca(remitente, motivo):
                messagebox.showinfo("Éxito", f"Se agregó {remitente} a la lista blanca")
            else:
                messagebox.showerror("Error", "No se pudo agregar a la lista blanca")
    
    def guardar_regla(self):
        """Guarda una regla personalizada"""
        if hasattr(self, 'indice_correo_actual') and self.indice_correo_actual < len(self.lote_actual):
            correo = self.lote_actual[self.indice_correo_actual]
            remitente = correo['email_remitente']
            carpeta = self.carpeta_combo.get()
            
            if self.motor_reglas.guardar_regla_aprendida(remitente, carpeta):
                messagebox.showinfo("Éxito", f"Regla guardada: {remitente} → {carpeta}")
            else:
                messagebox.showerror("Error", "No se pudo guardar la regla")
    
    def mover_correo_actual(self):
        """Mueve el correo actualmente seleccionado"""
        if hasattr(self, 'indice_correo_actual') and self.indice_correo_actual < len(self.lote_actual):
            correo = self.lote_actual[self.indice_correo_actual]
            carpeta = self.carpeta_combo.get()
            
            if messagebox.askyesno("Confirmar", f"Mover correo a '{carpeta}'?"):
                if self.mover_correo(correo['mensaje'], carpeta):
                    self.motor_reglas.guardar_regla_aprendida(correo['email_remitente'], carpeta)
                    messagebox.showinfo("Éxito", "Correo movido correctamente")
                    self.cargar_lote_correos()
    
    def mostrar_lista_blanca(self):
        """Muestra la ventana de lista blanca"""
        ListaBlancaWindow(self.root, self.motor_reglas)
    
    def configurar_reglas(self):
        """Muestra la ventana de configuración de reglas"""
        ConfiguracionReglasWindow(self.root, self.motor_reglas, self.carpetas_disponibles)
    
    def run(self):
        """Inicia la aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Desea cerrar la aplicación?"):
            self.motor_reglas.cerrar_conexion()
            self.root.destroy()

class ListaBlancaWindow:
    def __init__(self, parent, motor_reglas):
        self.motor = motor_reglas
        self.window = tk.Toplevel(parent)
        self.window.title("📋 Lista Blanca de Remitentes")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.crear_interfaz()
        self.cargar_lista_blanca()
    
    def crear_interfaz(self):
        frame = ttk.Frame(self.window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista
        columns = ('Remitente', 'Motivo', 'Fecha')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        self.tree.heading('Remitente', text='Remitente')
        self.tree.heading('Motivo', text='Motivo')
        self.tree.heading('Fecha', text='Fecha')
        
        self.tree.column('Remitente', width=200)
        self.tree.column('Motivo', width=200)
        self.tree.column('Fecha', width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_seleccionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def cargar_lista_blanca(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        lista = self.motor.obtener_lista_blanca()
        for remitente, motivo, fecha in lista:
            self.tree.insert('', 'end', values=(remitente, motivo or '', fecha))
    
    def eliminar_seleccionado(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']
            remitente = values[0]
            
            if messagebox.askyesno("Confirmar", f"Eliminar {remitente} de la lista blanca?"):
                self.motor.cursor.execute("DELETE FROM lista_blanca WHERE remitente = ?", (remitente,))
                self.motor.conn.commit()
                self.cargar_lista_blanca()

class ConfiguracionReglasWindow:
    def __init__(self, parent, motor_reglas, carpetas_disponibles):
        self.motor = motor_reglas
        self.carpetas_disponibles = carpetas_disponibles
        self.window = tk.Toplevel(parent)
        self.window.title("🔧 Configuración de Reglas")
        self.window.geometry("980x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.crear_interfaz()
        self.cargar_reglas()
    
    def crear_interfaz(self):
        frame = ttk.Frame(self.window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        formulario_simple = ttk.LabelFrame(frame, text="Nueva regla simple", padding="10")
        formulario_simple.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(formulario_simple, text="Criterio:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.tipo_combo = ttk.Combobox(formulario_simple, state='readonly', width=16)
        self.tipo_combo['values'] = ['asunto', 'remitente', 'destinatario']
        self.tipo_combo.set('asunto')
        self.tipo_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_simple, text="Patrón:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.patron_entry = ttk.Entry(formulario_simple, width=38)
        self.patron_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_simple, text="Coincidencia:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.modo_combo = ttk.Combobox(formulario_simple, state='readonly', width=12)
        self.modo_combo['values'] = ['contiene', 'exacto', 'parecido']
        self.modo_combo.set('contiene')
        self.modo_combo.grid(row=0, column=5, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_simple, text="Carpeta destino:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.carpeta_combo = ttk.Combobox(formulario_simple, state='readonly', width=45)
        self.carpeta_combo['values'] = self.carpetas_disponibles
        if self.carpetas_disponibles:
            self.carpeta_combo.set(self.carpetas_disponibles[0])
        self.carpeta_combo.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_simple, text="Prioridad:").grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)
        self.prioridad_spin = ttk.Spinbox(formulario_simple, from_=1, to=100, width=8)
        self.prioridad_spin.set(8)
        self.prioridad_spin.grid(row=1, column=5, sticky=tk.W, padx=5, pady=5)

        ttk.Button(formulario_simple, text="Agregar regla simple", command=self.agregar_regla).grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)

        formulario_compuesto = ttk.LabelFrame(frame, text="Nueva regla compuesta (criterio 1 AND criterio 2)", padding="10")
        formulario_compuesto.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(formulario_compuesto, text="Criterio 1:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.tipo1_combo = ttk.Combobox(formulario_compuesto, state='readonly', width=16)
        self.tipo1_combo['values'] = ['asunto', 'remitente', 'destinatario']
        self.tipo1_combo.set('remitente')
        self.tipo1_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_compuesto, text="Patrón 1:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.patron1_entry = ttk.Entry(formulario_compuesto, width=28)
        self.patron1_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_compuesto, text="Modo 1:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.modo1_combo = ttk.Combobox(formulario_compuesto, state='readonly', width=10)
        self.modo1_combo['values'] = ['contiene', 'exacto', 'parecido']
        self.modo1_combo.set('contiene')
        self.modo1_combo.grid(row=0, column=5, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_compuesto, text="Criterio 2:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.tipo2_combo = ttk.Combobox(formulario_compuesto, state='readonly', width=16)
        self.tipo2_combo['values'] = ['asunto', 'remitente', 'destinatario']
        self.tipo2_combo.set('asunto')
        self.tipo2_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_compuesto, text="Patrón 2:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.patron2_entry = ttk.Entry(formulario_compuesto, width=28)
        self.patron2_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_compuesto, text="Modo 2:").grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)
        self.modo2_combo = ttk.Combobox(formulario_compuesto, state='readonly', width=10)
        self.modo2_combo['values'] = ['contiene', 'exacto', 'parecido']
        self.modo2_combo.set('parecido')
        self.modo2_combo.grid(row=1, column=5, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_compuesto, text="Carpeta destino:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.carpeta_compuesta_combo = ttk.Combobox(formulario_compuesto, state='readonly', width=45)
        self.carpeta_compuesta_combo['values'] = self.carpetas_disponibles
        if self.carpetas_disponibles:
            self.carpeta_compuesta_combo.set(self.carpetas_disponibles[0])
        self.carpeta_compuesta_combo.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(formulario_compuesto, text="Prioridad:").grid(row=2, column=4, sticky=tk.W, padx=5, pady=5)
        self.prioridad_compuesta_spin = ttk.Spinbox(formulario_compuesto, from_=1, to=100, width=8)
        self.prioridad_compuesta_spin.set(12)
        self.prioridad_compuesta_spin.grid(row=2, column=5, sticky=tk.W, padx=5, pady=5)

        ttk.Button(formulario_compuesto, text="Agregar regla compuesta", command=self.agregar_regla_compuesta).grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        ttk.Label(formulario_compuesto, text="Ejemplo: remitente=facturas@... AND asunto parecido='Listado de facturas con soporte'").grid(row=3, column=1, columnspan=5, sticky=tk.W, padx=5)

        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        tab_simples = ttk.Frame(notebook)
        notebook.add(tab_simples, text="Reglas simples")
        tab_compuestas = ttk.Frame(notebook)
        notebook.add(tab_compuestas, text="Reglas compuestas")

        tabla_simple_frame = ttk.LabelFrame(tab_simples, text="Reglas simples configuradas", padding="10")
        tabla_simple_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        cols = ('ID', 'Criterio', 'Patrón', 'Coincidencia', 'Carpeta', 'Prioridad', 'Activa')
        self.tree_reglas = ttk.Treeview(tabla_simple_frame, columns=cols, show='headings', height=10)
        for col in cols:
            self.tree_reglas.heading(col, text=col)
        self.tree_reglas.column('ID', width=50, anchor='center')
        self.tree_reglas.column('Criterio', width=100, anchor='center')
        self.tree_reglas.column('Patrón', width=280)
        self.tree_reglas.column('Coincidencia', width=100, anchor='center')
        self.tree_reglas.column('Carpeta', width=280)
        self.tree_reglas.column('Prioridad', width=70, anchor='center')
        self.tree_reglas.column('Activa', width=70, anchor='center')
        scrollbar_simple = ttk.Scrollbar(tabla_simple_frame, orient=tk.VERTICAL, command=self.tree_reglas.yview)
        self.tree_reglas.configure(yscrollcommand=scrollbar_simple.set)
        self.tree_reglas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_simple.pack(side=tk.RIGHT, fill=tk.Y)

        tabla_compuesta_frame = ttk.LabelFrame(tab_compuestas, text="Reglas compuestas configuradas", padding="10")
        tabla_compuesta_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        cols_comp = ('ID', 'Criterio 1', 'Patrón 1', 'Modo 1', 'Criterio 2', 'Patrón 2', 'Modo 2', 'Carpeta', 'Prioridad', 'Activa')
        self.tree_compuestas = ttk.Treeview(tabla_compuesta_frame, columns=cols_comp, show='headings', height=10)
        for col in cols_comp:
            self.tree_compuestas.heading(col, text=col)
        self.tree_compuestas.column('ID', width=45, anchor='center')
        self.tree_compuestas.column('Criterio 1', width=85, anchor='center')
        self.tree_compuestas.column('Patrón 1', width=170)
        self.tree_compuestas.column('Modo 1', width=80, anchor='center')
        self.tree_compuestas.column('Criterio 2', width=85, anchor='center')
        self.tree_compuestas.column('Patrón 2', width=170)
        self.tree_compuestas.column('Modo 2', width=80, anchor='center')
        self.tree_compuestas.column('Carpeta', width=190)
        self.tree_compuestas.column('Prioridad', width=65, anchor='center')
        self.tree_compuestas.column('Activa', width=55, anchor='center')
        scrollbar_comp = ttk.Scrollbar(tabla_compuesta_frame, orient=tk.VERTICAL, command=self.tree_compuestas.yview)
        self.tree_compuestas.configure(yscrollcommand=scrollbar_comp.set)
        self.tree_compuestas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_comp.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Eliminar simple", command=self.eliminar_regla).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar compuesta", command=self.eliminar_regla_compuesta).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Recargar", command=self.cargar_reglas).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def cargar_reglas(self):
        for item in self.tree_reglas.get_children():
            self.tree_reglas.delete(item)
        for item in self.tree_compuestas.get_children():
            self.tree_compuestas.delete(item)

        for regla in self.motor.obtener_reglas_clasificacion():
            regla_id, tipo, patron, modo, carpeta, prioridad, activa = regla
            self.tree_reglas.insert('', 'end', values=(
                regla_id,
                tipo,
                patron,
                modo,
                carpeta,
                prioridad,
                'Sí' if activa else 'No'
            ))

        for regla in self.motor.obtener_reglas_compuestas():
            (regla_id, tipo1, patron1, modo1, tipo2, patron2, modo2, carpeta, prioridad, activa) = regla
            self.tree_compuestas.insert('', 'end', values=(
                regla_id,
                tipo1,
                patron1,
                modo1,
                tipo2,
                patron2,
                modo2,
                carpeta,
                prioridad,
                'Sí' if activa else 'No'
            ))

    def agregar_regla(self):
        tipo = self.tipo_combo.get().strip()
        patron = self.patron_entry.get().strip()
        modo = self.modo_combo.get().strip()
        carpeta = self.carpeta_combo.get().strip()

        try:
            prioridad = int(self.prioridad_spin.get())
        except ValueError:
            messagebox.showwarning("Validación", "La prioridad debe ser un número")
            return

        if not tipo or not patron or not modo or not carpeta:
            messagebox.showwarning("Validación", "Completa todos los campos de la regla")
            return

        ok = self.motor.agregar_regla_clasificacion(
            tipo_criterio=tipo,
            patron=patron,
            carpeta_destino=carpeta,
            modo_coincidencia=modo,
            prioridad=prioridad,
            activa=True
        )
        if ok:
            self.patron_entry.delete(0, tk.END)
            self.cargar_reglas()
            messagebox.showinfo("Éxito", "Regla agregada correctamente")
        else:
            messagebox.showerror("Error", "No se pudo agregar la regla")

    def agregar_regla_compuesta(self):
        tipo1 = self.tipo1_combo.get().strip()
        patron1 = self.patron1_entry.get().strip()
        modo1 = self.modo1_combo.get().strip()
        tipo2 = self.tipo2_combo.get().strip()
        patron2 = self.patron2_entry.get().strip()
        modo2 = self.modo2_combo.get().strip()
        carpeta = self.carpeta_compuesta_combo.get().strip()

        try:
            prioridad = int(self.prioridad_compuesta_spin.get())
        except ValueError:
            messagebox.showwarning("Validación", "La prioridad de la regla compuesta debe ser un número")
            return

        if not tipo1 or not patron1 or not modo1 or not tipo2 or not patron2 or not modo2 or not carpeta:
            messagebox.showwarning("Validación", "Completa todos los campos de la regla compuesta")
            return

        ok = self.motor.agregar_regla_compuesta(
            tipo_criterio_1=tipo1,
            patron_1=patron1,
            modo_coincidencia_1=modo1,
            tipo_criterio_2=tipo2,
            patron_2=patron2,
            modo_coincidencia_2=modo2,
            carpeta_destino=carpeta,
            prioridad=prioridad,
            activa=True
        )
        if ok:
            self.patron1_entry.delete(0, tk.END)
            self.patron2_entry.delete(0, tk.END)
            self.cargar_reglas()
            messagebox.showinfo("Éxito", "Regla compuesta agregada correctamente")
        else:
            messagebox.showerror("Error", "No se pudo agregar la regla compuesta")

    def eliminar_regla(self):
        seleccion = self.tree_reglas.selection()
        if not seleccion:
            messagebox.showwarning("Reglas", "Selecciona una regla para eliminar")
            return

        item = seleccion[0]
        valores = self.tree_reglas.item(item).get('values', [])
        if not valores:
            return

        regla_id = int(valores[0])
        if messagebox.askyesno("Confirmar", f"¿Eliminar la regla #{regla_id}?"):
            if self.motor.eliminar_regla_clasificacion(regla_id):
                self.cargar_reglas()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la regla")

    def eliminar_regla_compuesta(self):
        seleccion = self.tree_compuestas.selection()
        if not seleccion:
            messagebox.showwarning("Reglas", "Selecciona una regla compuesta para eliminar")
            return

        item = seleccion[0]
        valores = self.tree_compuestas.item(item).get('values', [])
        if not valores:
            return

        regla_id = int(valores[0])
        if messagebox.askyesno("Confirmar", f"¿Eliminar la regla compuesta #{regla_id}?"):
            if self.motor.eliminar_regla_compuesta(regla_id):
                self.cargar_reglas()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la regla compuesta")

if __name__ == "__main__":
    app = InterfazClasificadorCorreos()
    app.run()
