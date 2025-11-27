Se ha avanzado en la implementación del juego "Escapa del Laberinto"
Avance del proyecto
Fecha: 26 de Noviembre de 2025 Proyecto: Escapa del Laberinto

1. Implementación de Inteligencia a los enemigos
Algoritmo A*: Se implementó completamente el algoritmo de búsqueda A* dentro de la clase Enemigo (_a_star). Esto permite a los enemigos calcular la ruta óptima (más corta) a un objetivo.

Modo Escapa: Perseguir la posición actual del jugador.

Modo Cazador: Huir hacia la posición de la salida.

2. Lógica de Juego y Entidades
Clases de Terreno: Se definieron clases de terreno (Camino, Muro, Tunel, Liana) con propiedades explícitas de transitabilidad para el jugador y para el enemigo, lo que es clave para el movimiento.

Clase Jugador:

Incluye lógica de Energía para el movimiento normal y el modo "correr".

Implementa un sistema de Trampas con límite de 3 activas y un cooldown de 5 segundos.

Gestión de Dificultad: La clase Juego configura la velocidad de los enemigos, el número de enemigos (en modo Escapa) y el multiplicador de puntaje basado en la dificultad seleccionada (Facil, Normal, Dificil).

3. Sistema de Puntuación 
Se creó una clase dedicada a la gestión de puntajes.

Implementa el cálculo y registro de puntajes diferenciado para el Modo Escapa (basado en tiempo y multiplicador de dificultad) y Modo Cazador (basado en puntos acumulados por atrapar enemigos y usar trampas).

Manejo de Top 5 y un Historial Completo de partidas.

4. Interfaz Gráfica 
Menú Principal (RegistroVentana): Permite al usuario ingresar nombre, seleccionar modo y dificultad, y acceder a las instrucciones y los tops de puntaje.

Dibujado Dinámico: La clase Interfaz dibuja el mapa, el jugador, los enemigos, la salida y las trampas activas en un Canvas.

Actualización de Estado: Muestra información en tiempo real del jugador (Energía, Trampas disponibles/cooldown) y el puntaje actual.

Manejo de Eventos: Implementación de la captura de teclas (movimiento WASD/Flechas, Correr con Shift, Trampa con 'T') y lógica de final de partida (Victoria/Derrota).

En resumen, el código está en una etapa funcional avanzada, sistema de juego principal (movimiento, colisiones, puntuación, modos) completamente integrados en una interfaz de tkinter.
