import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import math

# Configurações
LARGURA, ALTURA = 1280, 720  # Reduzi para uma resolução mais comum
PLAYER_HEIGHT = 0.5
VELOCIDADE = 3.0
SENSIBILIDADE = 0.1

# Estado da câmera
cam_pos = np.array([0.0, PLAYER_HEIGHT, 5.0], dtype=np.float32)
cam_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
cam_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
yaw, pitch = -90.0, 0.0  # Removi variáveis não utilizadas

# Controles
keys = {}
mouse_first_move = True
last_x, last_y = LARGURA / 2, ALTURA / 2

def key_callback(window, key, scancode, action, mods):
    global keys
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    
    if action == glfw.PRESS or action == glfw.RELEASE:
        keys[key] = action == glfw.PRESS

def mouse_callback(window, xpos, ypos):
    global yaw, pitch, mouse_first_move, last_x, last_y, cam_front
    
    if mouse_first_move:
        last_x, last_y = xpos, ypos
        mouse_first_move = False
    
    xoffset = xpos - last_x
    yoffset = last_y - ypos  # Invertido pois as coordenadas Y vão de baixo para cima
    last_x, last_y = xpos, ypos
    
    xoffset *= SENSIBILIDADE
    yoffset *= SENSIBILIDADE
    
    yaw += xoffset
    pitch += yoffset
    
    # Limita o pitch para evitar flip
    pitch = max(-89.0, min(89.0, pitch))
    
    # Atualiza a direção da câmera
    front = np.array([
        math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)),
        math.sin(math.radians(pitch)),
        math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    ])
    cam_front = front / np.linalg.norm(front)

def process_input(window, delta_time):
    global cam_pos
    
    velocity = VELOCIDADE * delta_time
    right = np.cross(cam_front, cam_up)
    right /= np.linalg.norm(right)
    
    move_dir = np.zeros(3)
    if keys.get(glfw.KEY_W, False):
        move_dir += cam_front * velocity
    if keys.get(glfw.KEY_S, False):
        move_dir -= cam_front * velocity
    if keys.get(glfw.KEY_A, False):
        move_dir -= right * velocity
    if keys.get(glfw.KEY_D, False):
        move_dir += right * velocity
    
    cam_pos += move_dir
    cam_pos[1] = PLAYER_HEIGHT  # Mantém altura fixa
    
def draw_ground():
    glColor3f(0.0, 0.2, 0.0)  # verde
    glBegin(GL_QUADS)
    glVertex3f(-25, 0, -25)
    glVertex3f(-25, 0, 25)
    glVertex3f(25, 0, 25)
    glVertex3f(25, 0, -25)
    glEnd()
    
rock_positions = []

def draw_small_rock(x=0, z=0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glScalef(0.2, 0.1, 0.2)  
    glColor3f(0.41, 0.41, 0.41)  # cinza
    draw_cube(0, 0, 0)
    glPopMatrix()

def generate_small_rocks(count=500, spread=20):
    rock_positions = []
    for _ in range(count):
        x = random.uniform(-spread, spread)
        z = random.uniform(-spread, spread)
        rock_positions.append((x, z))
    return rock_positions
    
def draw_tree(x=0, z=0):
    # Dimensões fixas
    trunk_height = 0.8
    trunk_width = 0.2
    
    # Tronco (marrom)
    glColor3f(0.24, 0.17, 0.12)
    glPushMatrix()
    glTranslatef(x, trunk_height/2, z)
    glScalef(trunk_width, trunk_height, trunk_width)
    draw_cube(0, 0, 0)
    glPopMatrix()
    
    # Copa em 3 camadas decrescentes (verde)
    glColor3f(0.0, 0.39, 0.0)
    for i in range(3):
        layer_size = 1.2 - i*0.3  # Tamanho decrescente
        layer_height = trunk_height + i*0.5
        glPushMatrix()
        glTranslatef(x, layer_height, z)
        glScalef(layer_size, 0.5, layer_size)  # Achatado verticalmente
        draw_cube(0, 0, 0)
        glPopMatrix()
       

def draw_sky():
    glDisable(GL_DEPTH_TEST)  # Desativa o depth test para o céu ser desenhado por trás de tudo
    glPushMatrix()
    # Posiciona o céu ao redor da câmera
    glTranslatef(cam_pos[0], cam_pos[1], cam_pos[2])
    size = 10  # Tamanho do skybox
    glBegin(GL_QUADS)
    
    # Face frontal (Z negativo)
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(-size, size, -size)
    
    # Face traseira (Z positivo)
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(-size, -size, size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)
    
    # Face esquerda (X negativo)
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, -size, size)
    glVertex3f(-size, size, size)
    glVertex3f(-size, size, -size)
    
    # Face direita (X positivo)
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(size, size, -size)
    
    # Face superior (Y positivo - céu)
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)
    
    glEnd()
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)  # Reativa o depth test
    
def draw_cube(x, y, z, size=1):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(size, size, size)
    glBegin(GL_QUADS)
    
    # Frente
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    # Trás
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    
    # Esquerda
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    
    # Direita
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)
    
    #Superior
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    

    glEnd()
    glPopMatrix()
    
def desenhar_mira():
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glDisable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, LARGURA, ALTURA, 0)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Mira mais visível
    tamanho = 10
    glColor3f(1, 1, 1)  # Amarelo
    glLineWidth(2)
    
    glBegin(GL_LINES)
    centro_x, centro_y = LARGURA//2, ALTURA//2
    # Horizontal
    glVertex2f(centro_x - tamanho, centro_y)
    glVertex2f(centro_x + tamanho, centro_y)
    # Vertical
    glVertex2f(centro_x, centro_y - tamanho)
    glVertex2f(centro_x, centro_y + tamanho)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW) 
    glPopAttrib()
    
def main():
    if not glfw.init():
        print("Erro ao inicializar GLFW")
        return

    window = glfw.create_window(LARGURA, ALTURA, "Floresta 3D", None, None)
    if not window:
        glfw.terminate()
        print("Erro ao criar janela GLFW")
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)  # Mouse preso e invisível

    glEnable(GL_DEPTH_TEST)
    
    # Configuração da projeção
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, LARGURA/ALTURA, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    last_time = glfw.get_time()
    
    while not glfw.window_should_close(window):
        # Delta time
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Input
        process_input(window, delta_time)
        
        # Render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Câmera
        center = cam_pos + cam_front
        gluLookAt(*cam_pos, *center, *cam_up)
        
        # Cena
        draw_sky()
        draw_ground()
        
        # Árvores
        random.seed(42)  # Seed fixa para sempre gerar no mesmo lugar
        for _ in range(50):  # Reduzi o número para melhor performance
            x, z = random.uniform(-20, 20), random.uniform(-20, 20)
            draw_tree(x, z)
        
        # Rochas
        for x, z in generate_small_rocks(200):  # Menos rochas
            draw_small_rock(x, z)
        
        # Mira
        desenhar_mira()
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()