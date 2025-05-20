import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import math

# Configurações da minha resolução
LARGURA, ALTURA = 2560, 1440
PLAYER_HEIGHT = 0.5
VELOCIDADE = 3.0
SENSIBILIDADE = 0.1

cam_pos = np.array([0.0, PLAYER_HEIGHT, 5.0], dtype=np.float32)
cam_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
cam_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
yaw, pitch,speed = -90.0, 0.0, 3.0
ultimo_x, ultimo_y = LARGURA//2, ALTURA//2
primeiro_mouse = True
keys = {}
#Precionar ESC para sair do jogo
def key_callback(window, key, scancode, action, mods):
    global keys
    
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    
    if key in [glfw.KEY_UP, glfw.KEY_DOWN, glfw.KEY_LEFT, glfw.KEY_RIGHT, 
               glfw.KEY_W, glfw.KEY_A, glfw.KEY_S, glfw.KEY_D]:
        if action == glfw.PRESS:
            keys[key] = True
        elif action == glfw.RELEASE:
            keys[key] = False
            
def process_input(window, delta_time): #Função para processar a entrada do teclado
    global cam_pos, yaw, pitch
#O yaw é a rotação em torno do eixo Y e o pitch é a rotação em torno do eixo X   
    velocity = speed * delta_time
    rot_speed = 50 * delta_time 
    
    if keys.get(glfw.KEY_LEFT, False):
        yaw -= rot_speed
    if keys.get(glfw.KEY_RIGHT, False):
        yaw += rot_speed
    if keys.get(glfw.KEY_UP, False):
        pitch += rot_speed
    if keys.get(glfw.KEY_DOWN, False):
        pitch -= rot_speed
    
    pitch = max(-89.0, min(89.0, pitch))
# Atualiza a posição da câmera com base no yaw e pitch
    front = [
        math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)),
        math.sin(math.radians(pitch)),
        math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    ]
    cam_front[:] = front / np.linalg.norm(front)
# Atualiza a posição da câmera com base na frente e no vetor up  
    right = np.cross(cam_front, cam_up)
    right = right / np.linalg.norm(right)

    move_dir = np.array([0.0, 0.0, 0.0])
    if keys.get(glfw.KEY_W, False):
        move_dir += cam_front * velocity
    if keys.get(glfw.KEY_S, False):
        move_dir -= cam_front * velocity
    if keys.get(glfw.KEY_A, False):
        move_dir -= right * velocity
    if keys.get(glfw.KEY_D, False):
        move_dir += right * velocity
# Atualiza a posição da câmera
# Limita a movimentação da câmera ao eixo Y 
    cam_pos[0] += move_dir[0]
    cam_pos[2] += move_dir[2]
    cam_pos[1] = PLAYER_HEIGHT

#Desenha o chão verde    
def draw_ground():
    glColor3f(0.0, 0.2, 0.0)  # verde
    glBegin(GL_QUADS)
    glVertex3f(-25, 0, -25)
    glVertex3f(-25, 0, 25)
    glVertex3f(25, 0, 25)
    glVertex3f(25, 0, -25)
    glEnd()

#Desenha as pedrinhas em cima do chão   
def draw_small_rock(x=0, z=0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glScalef(0.2, 0.1, 0.2)  
    glColor3f(0.41, 0.41, 0.41)  # cinza
    draw_cube(0, 0, 0)
    glPopMatrix()
#Gera as pedrinhas em posições aleatórias
#Count é o número de pedrinhas e spread é a distância máxima do centro
def generate_small_rocks(count=500, spread=10):
    rock_positions = []
    for _ in range(count):
        x = random.uniform(-spread, spread)
        z = random.uniform(-spread, spread)
        rock_positions.append((x, z))
    return rock_positions
#Desenha as árvores em cima do chão   
def draw_tree(x=0, z=0):
    trunk_height = 0.8
    trunk_width = 0.2
    crown_size = 1.2  # Tamanho da copa
    
    # Tronco (marrom)
    glColor3f(0.24, 0.17, 0.12)  # Marrom
    glPushMatrix()
    glTranslatef(x, trunk_height/2, z)
    glScalef(trunk_width, trunk_height, trunk_width)
    draw_cube(0, 0, 0)
    glPopMatrix()
    
    # Copa (verde)
    glColor3f(0.0, 0.39, 0.0)
    glPushMatrix()
    glTranslatef(x, trunk_height + 0.5, z) 
    glScalef(crown_size, crown_size, crown_size)
    draw_cube(0, 0, 0)
    glPopMatrix()
        
def draw_sky():
    glDisable(GL_DEPTH_TEST) 
    glPushMatrix()
    # Posiciona o céu ao redor da câmera
    glTranslatef(cam_pos[0], cam_pos[1], cam_pos[2])
    size = 10
    glBegin(GL_QUADS)
    
    # Face frontal 
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(-size, size, -size)
    
    # Face traseira
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(-size, -size, size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)
    
    # Face da esquerda 
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, -size, size)
    glVertex3f(-size, size, size)
    glVertex3f(-size, size, -size)
    
    # Face da direita 
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(size, size, -size)
    
    #Céu
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
       
def main():
    global LARGURA, ALTURA
    if not glfw.init():
        print("Erro ao inicializar GLFW")
        return
    
    glfw.window_hint(glfw.SAMPLES, 4)
    window = glfw.create_window(LARGURA,ALTURA, "NIGHTROOT", None, None)
    if not window:
        glfw.terminate()
        print("Erro janela GLFW")
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
    
    glEnable(GL_DEPTH_TEST)
 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 2560/1440, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time

        process_input(window, delta_time)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        center = cam_pos + cam_front
        gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],
                  center[0], center[1], center[2],
                  cam_up[0], cam_up[1], cam_up[2])
        
        draw_sky() # Céu azul
        
        draw_ground()  # Chão verde
        random.seed(100)  #Para garantir a mesma posição das árvores e pedrinhas
        for _ in range(150):
            x = random.uniform(-20, 20)
            z = random.uniform(-20, 20)
            height = random.uniform(1.5, 3.0)
            scale = random.uniform(1.0, 1.2)
            draw_tree(x, z)
            
        small_rocks = generate_small_rocks() #Chama a função para gerar as pedrinhas
        for pos in small_rocks:
            draw_small_rock(pos[0], pos[1]) # Desenha as pedrinhas em cima do chão
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()