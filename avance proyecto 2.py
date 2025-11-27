import tkinter as tk
from tkinter import messagebox
import random
import time
from collections import deque
import heapq 

# CONFIGURACIÓN Y CONSTANTES
CELDA_TAMANO = 40
COLOR_FONDO = "#F0F0F0"
FPS = 100 
SEGUNDOS_COOLDOWN = 5 
SEGUNDOS_RESPAWN = 10 
ENERGIA_COSTO_CORRER = 8 
DISTANCIA_MINIMA_SALIDA = 8 

# COLORES PARA LA INTERFAZ 
BG_PRIMARIO = "#2C3E50"      
FG_PRIMARIO = "white"      
ACCENT_BOTON_START = "#2ECC71"
ACCENT_BOTON_INFO = "#3498DB"  
COLOR_TEXTO = "#ECF0F1"      

# colores para los terrenos
COLORES_TERRENO = {
    0: "white",  # Camino
    1: "black",  # Muro
    2: "blue",   # Túnel 
    3: "green"   # Liana 
}

# CLASES DE LÓGICA DE TERRENO Y ENTIDADES 

class Terreno:
    def __init__(self, simbolo, transitable_jugador, transitable_enemigo):
        self.simbolo = simbolo
        self.transitable_jugador = transitable_jugador
        self.transitable_enemigo = transitable_enemigo

class Camino(Terreno):
    def __init__(self):
        super().__init__(0, True, True)

class Muro(Terreno):
    def __init__(self):
        super().__init__(1, False, False)

class Tunel(Terreno):
    def __init__(self):
        super().__init__(2, True, False)

class Liana(Terreno):
    def __init__(self):
        super().__init__(3, False, True)

class Jugador:
    def __init__(self, nombre, x, y):
        self.nombre = nombre
        self.x = x
        self.y = y
        self.energia = 100
        self.trampas_disponibles = 3
        self.trampa_cooldown_fin = 0
    
    def mover(self, dx, dy, mapa_logico, es_correr=False):
        nueva_x = self.x + dx
        nueva_y = self.y + dy
        
        filas = len(mapa_logico)
        columnas = len(mapa_logico[0])
        
        if 0 <= nueva_x < filas and 0 <= nueva_y < columnas:
            celda = mapa_logico[nueva_x][nueva_y]
            if celda.transitable_jugador:
                if es_correr:
                    if self.energia >= ENERGIA_COSTO_CORRER:
                        self.energia -= ENERGIA_COSTO_CORRER
                    else:
                        return False 
                
                self.x = nueva_x
                self.y = nueva_y
                return True
        return False
    
    def regenerar_energia(self, esta_corriendo):
        if not esta_corriendo and self.energia < 100:
            self.energia = min(100, self.energia + 0.5) 

    def colocar_trampa(self):
        ahora = time.time()
        if len(self.juego.trampas_activas) < 3 and ahora >= self.trampa_cooldown_fin:
            self.trampa_cooldown_fin = ahora + SEGUNDOS_COOLDOWN
            return (self.x, self.y, ahora)
        return None
        
class Enemigo:
    def __init__(self, x, y, modo_juego, velocidad_base): 
        self.x = x
        self.y = y
        self.modo_juego = modo_juego 
        self.velocidad = velocidad_base 
        self.contador_movimiento = 0 

    def heuristica(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def _a_star(self, inicio, objetivo, mapa_logico):
        filas, columnas = len(mapa_logico), len(mapa_logico[0])
        frontera = [(0, 0, inicio[0], inicio[1])]
        g_score = {inicio: 0} 
        padre = {inicio: None} 

        while frontera:
            f, g, x, y = heapq.heappop(frontera)
            actual = (x, y)

            if actual == objetivo:
                camino = []
                while actual != inicio:
                    camino.append(actual)
                    actual = padre[actual]
                return camino[-1] if camino else None 

            posibles_movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for dx, dy in posibles_movimientos:
                nx, ny = x + dx, y + dy
                vecino = (nx, ny)

                if 0 <= nx < filas and 0 <= ny < columnas:
                    terreno = mapa_logico[nx][ny]
                    if terreno.transitable_enemigo:
                        nuevo_g = g + 1 
                        
                        if nuevo_g < g_score.get(vecino, float('inf')):
                            g_score[vecino] = nuevo_g
                            h = self.heuristica(nx, ny, objetivo[0], objetivo[1])
                            f_score = nuevo_g + h
                            padre[vecino] = actual
                            heapq.heappush(frontera, (f_score, nuevo_g, nx, ny))
        return None 


    def mover_ia(self, jugador_pos, mapa_logico, salida_pos):
        self.contador_movimiento += 1
        if self.contador_movimiento < self.velocidad:
            return False
        
        self.contador_movimiento = 0
        
        inicio = (self.x, self.y)
        
        if self.modo_juego == 'escapa':
            objetivo = jugador_pos
        else:
            objetivo = salida_pos
            
        siguiente_paso = self._a_star(inicio, objetivo, mapa_logico) 
        
        if siguiente_paso:
            self.x, self.y = siguiente_paso
            return True
        return False 


# CLASE DE PUNTUACIÓN Y REGISTRO 

class PuntajeManager:
    PUNTOS_BASE = 50 
    BONO_TRAMPA = 10 
    
    def __init__(self):
        self.top_escapa = [] 
        self.top_cazador = [] 
        self.puntos_actuales = 0
        self.historial_completo = [] 

    def calcular_y_registrar_puntaje(self, nombre, modo, tiempo_final=0, multiplicador_dificultad=1.0, dificultad="Normal"):
        
        if modo == 'escapa':
            puntaje = max(0, 5000 - int(tiempo_final * 10)) 
            puntaje += int(self.puntos_actuales) 
            puntaje = int(puntaje * multiplicador_dificultad) 
            self.registrar_top(self.top_escapa, nombre, puntaje)
            
        elif modo == 'cazador':
            puntaje = self.puntos_actuales
            self.registrar_top(self.top_cazador, nombre, puntaje)
        
        registro = {
            'nombre': nombre,
            'modo': modo,
            'dificultad': dificultad,
            'puntaje': puntaje,
            'fecha': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.historial_completo.append(registro)
        self.historial_completo.sort(key=lambda x: x['fecha'], reverse=True) 
            
        self.puntos_actuales = 0 
        return puntaje
    
    def log_cazador_final(self, nombre, dificultad):
        puntaje = int(self.puntos_actuales)
        if puntaje > 0:
            self.registrar_top(self.top_cazador, nombre, puntaje)
            
            registro = {
                'nombre': nombre,
                'modo': 'cazador',
                'dificultad': dificultad,
                'puntaje': puntaje,
                'fecha': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self.historial_completo.append(registro)
            self.historial_completo.sort(key=lambda x: x['fecha'], reverse=True)
            
        self.puntos_actuales = 0 
        

    def registrar_top(self, lista_top, nombre, puntaje):
        lista_top.append({'nombre': nombre, 'puntaje': puntaje})
        lista_top.sort(key=lambda x: x['puntaje'], reverse=True) 
        lista_top[:] = lista_top[:5] 
    
    def enemigo_escapo(self):
        self.puntos_actuales -= self.PUNTOS_BASE 
        
    def enemigo_atrapado(self):
        self.puntos_actuales += (self.PUNTOS_BASE * 2)
    
    def cazador_eliminado_trampa(self):
        self.puntos_actuales += self.BONO_TRAMPA
        
    def mostrar_top(self, modo):
        if modo == 'escapa':
            lista = self.top_escapa
            titulo = "TOP 5 - Modo Escapa (Tiempo)"
        else:
            lista = self.top_cazador
            titulo = "TOP 5 - Modo Cazador (Puntos)"
            
        texto = titulo + "\n" + "="*len(titulo) + "\n"
        if not lista:
            texto += "Aún no hay puntajes registrados."
        else:
            for i, item in enumerate(lista):
                texto += f"{i+1}. {item['nombre']}: {item['puntaje']} puntos\n"
        return texto
    
    def mostrar_historial_completo(self):
        texto = "HISTORIAL COMPLETO DE PARTIDAS\n" + "="*35 + "\n"
        if not self.historial_completo:
            texto += "Aún no hay partidas registradas en esta sesión."
        else:
            for item in self.historial_completo:
                texto += f"[{item['fecha'].split(' ')[1]}] {item['nombre']} - {item['modo'].capitalize()} ({item['dificultad']}): {item['puntaje']} pts\n"
        return texto

# CLASE PRINCIPAL DEL JUEGO

class Juego:
    def __init__(self, filas, columnas, modo_inicial, dificultad):
        self.filas = filas
        self.columnas = columnas
        self.mapa_logico = []
        self.modo_actual = modo_inicial
        self.dificultad = dificultad
        self.salida_pos = (self.filas-1, self.columnas-1)
        
        self._ajustar_parametros_dificultad() 
        self.generar_mapa() 
        self.jugador = Jugador("", 0, 0)
        self.enemigos = []
        self.puntaje_manager = PuntajeManager()
        self.trampas_activas = [] 
        self.enemigos_muertos = []
        self.tiempo_inicio = time.time()
        
        self.jugador.juego = self 

        self._inicializar_entidades()

    def _ajustar_parametros_dificultad(self):
        self.config = {
            'Facil': {
                'velocidad_escapa': 30,  
                'enemigos_escapa': 1,
                'velocidad_cazador': 40, 
                'multiplicador_puntaje': 1.0
            },
            'Normal': {
                'velocidad_escapa': 20, 
                'enemigos_escapa': 2,
                'velocidad_cazador': 30, 
                'multiplicador_puntaje': 1.5
            },
            'Dificil': {
                'velocidad_escapa': 10, 
                'enemigos_escapa': 3,
                'velocidad_cazador': 20, 
                'multiplicador_puntaje': 2.0
            }
        }[self.dificultad]


    def _obtener_posicion_segura(self, modo):
        distancia_minima = DISTANCIA_MINIMA_SALIDA
        salida_pos = self.salida_pos

        while True:
            e_x = random.randint(0, self.filas - 1)
            e_y = random.randint(0, self.columnas - 1)
            e_pos = (e_x, e_y)

            es_transitable = self.mapa_logico[e_x][e_y].transitable_enemigo
            es_posicion_jugador = (e_x, e_y) == (self.jugador.x, self.jugador.y)
            
            if not es_transitable:
                continue

            if modo == 'escapa':
                return e_x, e_y
            
            elif modo == 'cazador':
                
                distancia_a_salida = abs(e_x - salida_pos[0]) + abs(e_y - salida_pos[1])
                es_lejos_de_salida = distancia_a_salida >= distancia_minima
                
                tiene_camino_a_salida = self._validar_camino_enemigo_bfs(e_pos, self.salida_pos)
                
                if not es_posicion_jugador and tiene_camino_a_salida and es_lejos_de_salida:
                    return e_x, e_y


    def _validar_camino_bfs(self, inicio, fin):
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
        cola = deque([inicio])
        visitados = {inicio}
        
        while cola:
            x, y = cola.popleft()
            if (x, y) == fin: return True
            
            for dx, dy in movimientos:
                nx, ny = x + dx, y + dy
                nueva_pos = (nx, ny)
                
                if 0 <= nx < self.filas and 0 <= ny < self.columnas and nueva_pos not in visitados:
                    terreno = self.mapa_logico[nx][ny]
                    if terreno.transitable_jugador:
                        visitados.add(nueva_pos)
                        cola.append(nueva_pos)
        return False 

    def _validar_camino_enemigo_bfs(self, inicio, fin):
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
        cola = deque([inicio])
        visitados = {inicio}
        
        while cola:
            x, y = cola.popleft()
            if (x, y) == fin: return True
            
            for dx, dy in movimientos:
                nx, ny = x + dx, y + dy
                nueva_pos = (nx, ny)
                
                if 0 <= nx < self.filas and 0 <= ny < self.columnas and nueva_pos not in visitados:
                    terreno = self.mapa_logico[nx][ny]
                    if terreno.transitable_enemigo: 
                        visitados.add(nueva_pos)
                        cola.append(nueva_pos)
        return False 

    def generar_mapa(self):
        mapa_valido = False
        while not mapa_valido:
            opciones = [Camino(), Muro(), Tunel(), Liana()]
            self.mapa_logico = []
            
            for i in range(self.filas):
                fila = []
                for j in range(self.columnas):
                    terreno_elegido = random.choices(opciones, weights=[60, 20, 10, 10], k=1)[0]
                    fila.append(terreno_elegido)
                self.mapa_logico.append(fila)
            
            inicio_pos = (0, 0)
            self.mapa_logico[inicio_pos[0]][inicio_pos[1]] = Camino()
            self.mapa_logico[self.salida_pos[0]][self.salida_pos[1]] = Camino()
            
            if self._validar_camino_bfs(inicio_pos, self.salida_pos):
                mapa_valido = True
    
    def _inicializar_entidades(self):
        if self.modo_actual == 'escapa':
            num_enemigos = self.config['enemigos_escapa']
            velocidad = self.config['velocidad_escapa']
            
            initial_positions = [(self.filas-1, 0), (0, self.columnas-1), (self.filas-1, self.columnas-1)] 
            self.enemigos = [
                Enemigo(x, y, 'escapa', velocidad)
                for (x, y) in initial_positions[:num_enemigos]
            ]
        
        elif self.modo_actual == 'cazador':
             velocidad = self.config['velocidad_cazador']
             e_x, e_y = self._obtener_posicion_segura('cazador')
             self.enemigos = [Enemigo(e_x, e_y, 'cazador', velocidad)] 

    def _manejar_respawn(self):
        ahora = time.time()
        enemigos_revividos = []
        
        for item in self.enemigos_muertos:
            tiempo_muerte = item['tiempo_muerte']
            
            if ahora >= tiempo_muerte + SEGUNDOS_RESPAWN: 
                e_x, e_y = self._obtener_posicion_segura('escapa')

                self.enemigos.append(Enemigo(e_x, e_y, 'escapa', self.config['velocidad_escapa'])) 
                enemigos_revividos.append(item)

        for item in enemigos_revividos:
            self.enemigos_muertos.remove(item)

    def _comprobar_trampas(self, enemigo):
        if enemigo.modo_juego == 'escapa':
            pos_enemigo = (enemigo.x, enemigo.y)
            trampas_a_remover = []
            
            for trampa in self.trampas_activas:
                trampa_x, trampa_y, _ = trampa
                if (trampa_x, trampa_y) == pos_enemigo:
                    trampas_a_remover.append(trampa)
                    self.enemigos_muertos.append({'enemigo': enemigo, 'tiempo_muerte': time.time()})
                    self.puntaje_manager.cazador_eliminado_trampa()
                    break 

            for trampa in trampas_a_remover:
                self.trampas_activas.remove(trampa)
                
            return len(trampas_a_remover) > 0
        return False

    def actualizar_enemigos(self):
        self._manejar_respawn()
        
        enemigos_a_remover = []
        
        for enemigo in self.enemigos:
            if self._comprobar_trampas(enemigo):
                enemigos_a_remover.append(enemigo)
                continue
                
            jugador_pos = (self.jugador.x, self.jugador.y)
            enemigo.mover_ia(jugador_pos, self.mapa_logico, self.salida_pos)
            
            resultado_colision = self._comprobar_colisiones(enemigo)
            
            if resultado_colision == "ENEMIGO_ATRAPADO" or resultado_colision == "ENEMIGO_ESCAPA":
                enemigos_a_remover.append(enemigo)
            elif resultado_colision == "VICTORIA" or resultado_colision == "DERROTA_ATRAPADO":
                return resultado_colision

        for enemigo in enemigos_a_remover:
            if enemigo in self.enemigos:
                self.enemigos.remove(enemigo)
                
                if enemigo.modo_juego == 'cazador':
                    velocidad = self.config['velocidad_cazador']
                    e_x, e_y = self._obtener_posicion_segura('cazador')
                    self.enemigos.append(Enemigo(e_x, e_y, 'cazador', velocidad)) 
        

        return None

    def _comprobar_colisiones(self, enemigo):
        if (enemigo.x, enemigo.y) == (self.jugador.x, self.jugador.y):
            if self.modo_actual == 'escapa':
                return "DERROTA_ATRAPADO" 
            
            elif self.modo_actual == 'cazador':
                self.puntaje_manager.enemigo_atrapado()
                return "ENEMIGO_ATRAPADO" 

        if self.modo_actual == 'cazador' and (enemigo.x, enemigo.y) == self.salida_pos:
            self.puntaje_manager.enemigo_escapo()
            return "ENEMIGO_ESCAPA" 

        if self.modo_actual == 'escapa' and (self.jugador.x, self.jugador.y) == self.salida_pos:
            tiempo_final = time.time() - self.tiempo_inicio
            multiplicador = self.config['multiplicador_puntaje'] 
            dificultad = self.dificultad 
            self.puntaje_manager.calcular_y_registrar_puntaje(self.jugador.nombre, 'escapa', tiempo_final, multiplicador, dificultad)
            return "VICTORIA"
        
        return None

# CLASE DE INTERFAZ Y REGISTRO 

class RegistroVentana(tk.Toplevel):
    def __init__(self, master, callback, puntaje_manager):
        super().__init__(master)
        self.title("Proyecto 2: Menú Principal")
        self.geometry("400x380") 
        self.configure(bg=BG_PRIMARIO) 
        self.transient(master)
        self.callback = callback
        self.puntaje_manager = puntaje_manager
        
        tk.Label(self, text="ESCAPA DEL LABERINTO", bg=BG_PRIMARIO, fg=FG_PRIMARIO, 
                 font=('Arial', 14, 'bold')).pack(pady=(15, 10))
        
        tk.Label(self, text="Ingrese su nombre:", bg=BG_PRIMARIO, fg=COLOR_TEXTO, 
                 font=('Arial', 10)).pack()
        self.entry_nombre = tk.Entry(self, font=('Arial', 12), justify='center')
        self.entry_nombre.pack(pady=(5, 15), padx=40, fill='x')
        
        tk.Label(self, text="Seleccione Dificultad:", bg=BG_PRIMARIO, fg=COLOR_TEXTO, 
                 font=('Arial', 10)).pack()
                 
        self.opciones_dificultad = ['Facil', 'Normal', 'Dificil']
        self.dificultad_var = tk.StringVar(self)
        self.dificultad_var.set('Normal') 
        
        self.menu_dificultad = tk.OptionMenu(self, self.dificultad_var, *self.opciones_dificultad)
        self.menu_dificultad.config(bg=BG_PRIMARIO, fg=FG_PRIMARIO, font=('Arial', 10), width=10)
        self.menu_dificultad['menu'].config(bg=BG_PRIMARIO, fg='black', font=('Arial', 10))
        self.menu_dificultad.pack(pady=(5, 15))

        boton_kwargs = {'bg': ACCENT_BOTON_START, 'fg': FG_PRIMARIO, 'font': ('Arial', 10, 'bold'), 'relief': 'flat', 'width': 30}

        tk.Button(self, text="Comenzar Modo Escapa", 
                  command=lambda: self.iniciar_juego('escapa'), **boton_kwargs).pack(pady=3)
        
        tk.Button(self, text="Comenzar Modo Cazador", 
                  command=lambda: self.iniciar_juego('cazador'), **boton_kwargs).pack(pady=3)
        
        info_frame = tk.Frame(self, bg=BG_PRIMARIO)
        info_frame.pack(pady=(15, 5))
        
        tk.Button(info_frame, text="Instrucciones", command=self.mostrar_instrucciones, 
                  bg=ACCENT_BOTON_INFO, fg=FG_PRIMARIO, font=('Arial', 10), relief='flat').pack(side=tk.LEFT, padx=3)
        
        tk.Button(info_frame, text="Ver Top Escapa", command=lambda: self.mostrar_top('escapa'),
                  bg=ACCENT_BOTON_INFO, fg=FG_PRIMARIO, font=('Arial', 10), relief='flat').pack(side=tk.LEFT, padx=3)
        
        tk.Button(info_frame, text="Ver Top Cazador", command=lambda: self.mostrar_top('cazador'),
                  bg=ACCENT_BOTON_INFO, fg=FG_PRIMARIO, font=('Arial', 10), relief='flat').pack(side=tk.LEFT, padx=3)
        
        tk.Button(info_frame, text="Ver Historial", command=self.mostrar_historial,
                  bg=ACCENT_BOTON_INFO, fg=FG_PRIMARIO, font=('Arial', 10), relief='flat').pack(side=tk.LEFT, padx=3)


    def iniciar_juego(self, modo):
        nombre = self.entry_nombre.get()
        dificultad = self.dificultad_var.get()
        if nombre:
            self.callback(nombre, modo, dificultad) 
            self.destroy()
        else:
            messagebox.showerror("Error", "El registro es obligatorio antes de comenzar.")

    def mostrar_top(self, modo):
        texto = self.puntaje_manager.mostrar_top(modo)
        messagebox.showinfo("Top 5 Puntajes", texto)
        
    def mostrar_historial(self):
        texto = self.puntaje_manager.mostrar_historial_completo()
        messagebox.showinfo("Historial de Partidas", texto)


    def mostrar_instrucciones(self):
        instrucciones = (
            "Instrucciones del Juego\n\n"
            "Dificultades (Afecta Velocidad, #Enemigos y Puntos):\n"
            "  • Fácil: Velocidad Lenta / 1 Cazador (Escapa) / Multiplicador x1.0\n"
            "  • Normal: Velocidad Media / 2 Cazadores (Escapa) / Multiplicador x1.5\n"
            "  • Difícil: Velocidad Rápida / 3 Cazadores (Escapa) / Multiplicador x2.0\n\n"
            "Modo 1: Escapa\n"
            "  • Objetivo: Llegar a la salida (bandera FIN).\n"
            "  • Trampas (T): Máx. 3 activas (cooldown de 5s). Matan al cazador.\n\n"
            "Modo 2: Cazador\n"
            f"  • Restricción de Aparición: El cazador reaparece a una distancia mínima de {DISTANCIA_MINIMA_SALIDA} de la salida.\n"
            "  • IA Mejorada: Los enemigos usan A* para huir a la salida.\n"
            "  • Objetivo: Atrapar al cazador antes de que escape.\n"
            "  • Atrapado: El enemigo desaparece y reaparece en una zona segura (lejos de la salida)."
        )
        messagebox.showinfo("Instrucciones", instrucciones)


class Interfaz(tk.Frame):
    def __init__(self, master):
        super().__init__(master) 
        
        self.master = master
        self.juego = None 
        self.pack()
        self.master.title("Proyecto 2: Escapa del Laberinto")
        self.puntaje_manager_global = PuntajeManager()
        self.canvas_mapa = None
        
        self.corriendo = False
        
        self.master.bind('<Shift_L>', self.iniciar_correr)
        self.master.bind('<KeyRelease-Shift_L>', self.detener_correr)
        self.master.bind('<Key>', self.manejar_tecla)
        
        RegistroVentana(master, self.iniciar_juego, self.puntaje_manager_global)

    def iniciar_correr(self, event):
        self.corriendo = True

    def detener_correr(self, event):
        self.corriendo = False
    
    def iniciar_juego(self, nombre, modo, dificultad): 
        self.juego = Juego(15, 15, modo, dificultad) 
        self.juego.jugador.nombre = nombre
        self.juego.puntaje_manager = self.puntaje_manager_global
        self.crear_widgets()
        self.actualizar_juego()

    def crear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.canvas_mapa = tk.Canvas(self, width=self.juego.columnas * CELDA_TAMANO, 
                                     height=self.juego.filas * CELDA_TAMANO, bg=COLOR_FONDO)
        self.canvas_mapa.pack(pady=10)
        
        info_frame = tk.Frame(self)
        info_frame.pack(pady=5)
        
        tk.Label(info_frame, text=f"Modo: {self.juego.modo_actual.capitalize()} | Dificultad: {self.juego.dificultad}", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.label_energia = tk.Label(info_frame, text=f"Energía: {self.juego.jugador.energia:.1f}%") 
        self.label_energia.pack(side=tk.LEFT, padx=10)
        
        self.label_puntaje = tk.Label(info_frame, text="Puntos: 0")
        self.label_puntaje.pack(side=tk.LEFT, padx=10)
        
        self.label_trampas = tk.Label(info_frame, text=f"Trampas: {len(self.juego.trampas_activas)}/3")
        self.label_trampas.pack(side=tk.LEFT, padx=10)
        
        if self.juego.modo_actual == 'cazador':
             button_text = "Guardar Puntaje y Salir"
             button_bg = "#E74C3C" 
        else:
             button_text = "Reiniciar (Menú Principal)"
             button_bg = None 
             
        tk.Button(info_frame, text=button_text, command=self.reiniciar_juego, bg=button_bg).pack(side=tk.RIGHT, padx=10)
    
    def reiniciar_juego(self):
        if self.juego and self.juego.modo_actual == 'cazador':
            self.juego.puntaje_manager.log_cazador_final(self.juego.jugador.nombre, self.juego.dificultad)

        self.juego = None
        self.corriendo = False
        RegistroVentana(self.master, self.iniciar_juego, self.puntaje_manager_global)

    def dibujar_mapa(self):
        if not self.juego or not self.canvas_mapa: return
        self.canvas_mapa.delete("all")
        
        for r in range(self.juego.filas):
            for c in range(self.juego.columnas):
                terreno = self.juego.mapa_logico[r][c]
                x1, y1 = c * CELDA_TAMANO, r * CELDA_TAMANO
                x2, y2 = x1 + CELDA_TAMANO, y1 + CELDA_TAMANO
                color = COLORES_TERRENO.get(terreno.simbolo, "gray")
                self.canvas_mapa.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ccc")
                
                if (r, c) == self.juego.salida_pos:
                    self.canvas_mapa.create_text(x1 + CELDA_TAMANO/2, y1 + CELDA_TAMANO/2, text="FIN", font=('Arial', 10, 'bold'))
        
        for trampa in self.juego.trampas_activas:
            tx, ty, _ = trampa
            cx = ty * CELDA_TAMANO + CELDA_TAMANO // 2
            cy = tx * CELDA_TAMANO + CELDA_TAMANO // 2
            self.canvas_mapa.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="orange", tags="trampa")
            
        self._dibujar_entidad(self.juego.jugador.x, self.juego.jugador.y, "red", "jugador")
        for enemigo in self.juego.enemigos:
            self._dibujar_entidad(enemigo.x, enemigo.y, "yellow", "enemigo", is_rect=True)

    def _dibujar_entidad(self, r, c, color, tag, is_rect=False):
        cx = c * CELDA_TAMANO + CELDA_TAMANO // 2
        cy = r * CELDA_TAMANO + CELDA_TAMANO // 2
        
        border_color = "red"
        if tag == "jugador" and self.corriendo:
            border_color = "darkorange" 
        
        if is_rect:
            self.canvas_mapa.create_rectangle(cx - 8, cy - 8, cx + 8, cy + 8, fill=color, tags=tag, outline="black")
        else:
            self.canvas_mapa.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill=color, tags=tag, outline=border_color, width=2)


    def manejar_tecla(self, event):
        if not self.juego: return
        
        dx, dy = 0, 0
        es_correr = self.corriendo 
        
        if event.keysym in ['w', 'Up']: dx = -1; dy = 0 
        elif event.keysym in ['s', 'Down']: dx = 1; dy = 0
        elif event.keysym in ['a', 'Left']: dx = 0; dy = -1
        elif event.keysym in ['d', 'Right']: dx = 0; dy = 1
        
        if event.keysym == 't' and self.juego.modo_actual == 'escapa':
            self.colocar_trampa_handler()

        if dx != 0 or dy != 0:
            self.juego.jugador.mover(dx, dy, self.juego.mapa_logico, es_correr)

    def colocar_trampa_handler(self):
        if len(self.juego.trampas_activas) < 3:
            resultado_trampa = self.juego.jugador.colocar_trampa()
            if resultado_trampa:
                self.juego.trampas_activas.append(resultado_trampa)
                self.juego.jugador.trampas_disponibles = 3 - len(self.juego.trampas_activas)
            else:
                tiempo_restante = max(0, self.juego.jugador.trampa_cooldown_fin - time.time())
                if tiempo_restante > 0:
                    print(f"Trampa en cooldown. Espera {tiempo_restante:.1f}s")
                else:
                     print("Límite de 3 trampas activas alcanzado.")

        else:
            print("Límite de 3 trampas activas alcanzado.")

    def actualizar_info(self):
        if not self.juego: return
        
        cooldown_restante = max(0, self.juego.jugador.trampa_cooldown_fin - time.time())
        cooldown_str = f" ({cooldown_restante:.1f}s)" if cooldown_restante > 0 else ""
        
        self.label_energia.config(text=f"Energía: {self.juego.jugador.energia:.1f}%")
        self.label_puntaje.config(text=f"Puntos: {self.juego.puntaje_manager.puntos_actuales}")
        self.label_trampas.config(text=f"Trampas: {len(self.juego.trampas_activas)}/3{cooldown_str}")

    def mostrar_final(self, resultado):
        if resultado == "VICTORIA":
            puntaje = self.juego.puntaje_manager.top_escapa[0]['puntaje'] if self.juego.puntaje_manager.top_escapa else 'N/A'
            mensaje = f"¡VICTORIA! Has escapado en dificultad {self.juego.dificultad}.\nTu puntaje final es: {puntaje}"
        elif resultado == "DERROTA_ATRAPADO":
              mensaje = "¡DERROTA! Has sido atrapado por un cazador."
        else:
            return

        messagebox.showinfo(resultado, mensaje)
        self.reiniciar_juego()

    def actualizar_juego(self):
        if not self.juego:
            self.master.after(int(1000/FPS), self.actualizar_juego)
            return

        self.juego.jugador.regenerar_energia(self.corriendo)
        
        resultado = self.juego.actualizar_enemigos()
        
        if resultado:
            self.mostrar_final(resultado)
            return

        self.actualizar_info()
        self.dibujar_mapa()
        
        self.master.after(int(1000/FPS), self.actualizar_juego)


if __name__ == "__main__":
    root = tk.Tk()
    app = Interfaz(root)
    root.mainloop()

