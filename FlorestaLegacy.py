import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import math

# Constantes para largura da janela, altura, altura do jogador, velocidade e sensibilidade do mouse
LARGURA, ALTURA = 1280, 720
PLAYER_HEIGHT = 0.5
VELOCIDADE = 3.0
SENSIBILIDADE = 0.1
NUM_POSTES = 4 # Número de postes com luzes

# Posição inicial da câmera, vetores de frente e para cima, e ângulos de rotação (yaw e pitch)
cam_pos = np.array([0.0, PLAYER_HEIGHT, 5.0], dtype=np.float32)
cam_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
cam_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
yaw, pitch = -90.0, 0.0

# Dicionário para armazenar estado das teclas e variáveis de controle do mouse
keys = {}
pole_positions = []
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
    yoffset = last_y - ypos
    last_x, last_y = xpos, ypos
    xoffset *= SENSIBILIDADE
    yoffset *= SENSIBILIDADE
    yaw += xoffset
    pitch += yoffset
    pitch = max(-89.0, min(89.0, pitch))  # Limitar o ângulo de pitch para evitar inversões
    front = np.array([
        math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)),
        math.sin(math.radians(pitch)),
        math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    ])
    cam_front = front / np.linalg.norm(front)  # Normalizar o vetor de direção

def process_input(window, delta_time):
    global cam_pos
    velocity = VELOCIDADE * delta_time  # Velocidade baseada no tempo entre frames
    right = np.cross(cam_front, cam_up)  # Vetor para a direita
    right /= np.linalg.norm(right)  # Normalizar o vetor
    move_dir = np.zeros(3)
    if keys.get(glfw.KEY_W, False):
        move_dir += cam_front * velocity  # Mover para frente
    if keys.get(glfw.KEY_S, False):
        move_dir -= cam_front * velocity  # Mover para trás
    if keys.get(glfw.KEY_A, False):
        move_dir -= right * velocity  # Mover para a esquerda
    if keys.get(glfw.KEY_D, False):
        move_dir += right * velocity  # Mover para a direita
    cam_pos += move_dir
    cam_pos[1] = PLAYER_HEIGHT  # Manter altura constante

def draw_ground():
    glColor3f(0.0, 0.2, 0.0)  # Cor verde escuro para o chão
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)  # Normal apontando para cima (importante para iluminação)
    glVertex3f(-25, 0, -25)
    glVertex3f(-25, 0, 25)
    glVertex3f(25, 0, 25)
    glVertex3f(25, 0, -25)
    glEnd()

def draw_small_rock(x=0, z=0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glScalef(0.2, 0.1, 0.2)  # Escala para uma pedra pequena e achatada
    glColor3f(0.41, 0.41, 0.41)  # Cor cinza para a pedra
    draw_cube(0, 0, 0)  # draw_cube deve ter normais para iluminação
    glPopMatrix()

def generate_small_rocks(count=500, spread=20):
    # Gerar posições aleatórias para pedras pequenas
    return [(random.uniform(-spread, spread), random.uniform(-spread, spread)) for _ in range(count)]

def draw_tree(x=0, z=0):
    trunk_height = 1.0  # Altura do tronco
    trunk_width = 0.2   # Largura do tronco
    glColor3f(0.24, 0.17, 0.12)  # Cor marrom para o tronco
    glPushMatrix()
    glTranslatef(x, trunk_height / 2, z)
    glScalef(trunk_width, trunk_height, trunk_width)
    draw_cube(0, 0, 0)  # draw_cube deve ter normais para iluminação
    glPopMatrix()
    glColor3f(0.0, 0.39, 0.0)  # Cor verde para as folhas
    for i in range(3):  # Três camadas de folhas
        layer_size = 1.2 - i * 0.3  # Tamanho decrescente para cada camada
        layer_height = trunk_height + i * 0.5  # Altura crescente para cada camada
        glPushMatrix()
        glTranslatef(x, layer_height, z)
        glScalef(layer_size, 0.5, layer_size)
        draw_cube(0, 0, 0)  # draw_cube deve ter normais para iluminação
        glPopMatrix()
        
def draw_asphalt(width=5.0, length=50.0):  # Removi stone_density pois não é mais necessário
    # Desenha o asfalto (base preta)
    glColor3f(0.1, 0.1, 0.1)  # Cor preta para o asfalto
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-width/2, 0.01, -length/2)
    glVertex3f(-width/2, 0.01, length/2)
    glVertex3f(width/2, 0.01, length/2)
    glVertex3f(width/2, 0.01, -length/2)
    glEnd()
    
    # Desenha as listras amarelas no meio
    stripe_width = 0.2
    stripe_length = 2.0
    gap_length = 4.0
    glColor3f(1.0, 0.9, 0.0)  # Amarelo vibrante
    
    z = -length/2
    while z < length/2:
        glBegin(GL_QUADS)
        glVertex3f(-stripe_width/2, 0.02, z)
        glVertex3f(-stripe_width/2, 0.02, z + stripe_length)
        glVertex3f(stripe_width/2, 0.02, z + stripe_length)
        glVertex3f(stripe_width/2, 0.02, z)
        glEnd()
        z += stripe_length + gap_length
        
def draw_sky():
    glDisable(GL_LIGHTING)  # Skybox geralmente não tem iluminação
    glDisable(GL_DEPTH_TEST)  # Desativar teste de profundidade para desenhar atrás de tudo
    glPushMatrix()
    glTranslatef(cam_pos[0], cam_pos[1], cam_pos[2])  # Manter skybox centrado na câmera
    size = 10
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.1, 0.44)  # Azul escuro para o céu
    
    # Frente 
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(-size, size, -size)
    
    # Trás 
    glVertex3f(-size, -size, size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)
    
    # Esquerda 
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, -size, size)
    glVertex3f(-size, size, size)
    glVertex3f(-size, size, -size)
    # Direita 
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(size, size, -size)
    # Topo (
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)
    
    glEnd()
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)  # Reativar iluminação para o resto da cena

def draw_cube(x, y, z, size=1):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(size, size, size)
    glBegin(GL_QUADS)
    
    # Face frontal
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    # Face traseira
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    
    # Face esquerdA
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    
    # Face direita 
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)
    
    # Face superior
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    # Face inferior
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    
    glEnd()
    glPopMatrix()

def draw_sun():
    glDisable(GL_LIGHTING)  # Desativar iluminação para o sol
    glPushMatrix()
    glColor3f(1.0, 0.9, 0.6)  # Cor amarela para o sol
    glTranslatef(45.0, 15.0, -10.0)  # Posição do sol no céu
    glScalef(2.0, 2.0, 2.0)  # Achatado para parecer um disco
    draw_cube(0, 0, 0)
    glPopMatrix()
    glEnable(GL_LIGHTING)  # Reativar iluminação

def main():
    if not glfw.init():
        print("Erro ao inicializar GLFW")
        return
    
    # Configuração da janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_ANY_PROFILE)
    
    window = glfw.create_window(LARGURA, ALTURA, "Floresta com Pedras", None, None)
    if not window:
        glfw.terminate()
        print("Erro ao criar janela GLFW")
        return
    
    glfw.make_context_current(window)
    
    # Verifica se o contexto OpenGL foi criado
    if not glGetString(GL_VERSION):
        print("Erro: OpenGL não está disponível")
        glfw.terminate()
        return
    
    print(f"OpenGL versão: {glGetString(GL_VERSION).decode('utf-8')}")
    
    # Configura callbacks
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Configurações básicas de OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)  # Luz principal (sol)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Configuração da luz do sol
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [2.0, 1.0, 0.8, 1.0]) # Luz difusa amarela 
    glLightfv(GL_LIGHT0, GL_SPECULAR, [2.0, 1.0, 0.9, 1.0]) # Luz especular amarela
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0) # Atenuação constante
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0) # Atenuação linear
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0) # Atenuação quadrática

    #Matriz de projeção
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, LARGURA / ALTURA, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    last_time = glfw.get_time()

    try:
        while not glfw.window_should_close(window):
            current_time = glfw.get_time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # Processa input
            process_input(window, delta_time)
            
            # Limpa buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            # Configura câmera
            center = cam_pos + cam_front
            gluLookAt(*cam_pos, *center, *cam_up)
            
            sun_pos = [5.0, 8.0, 1.0, 0.0]  
            glLightfv(GL_LIGHT0, GL_POSITION, sun_pos)

            draw_sky()
            draw_sun()

            draw_ground()
            draw_asphalt(width=3.0, length=50.0)  

            random.seed(42)
            for _ in range(100):  
                x, z = random.uniform(-20, 20), random.uniform(-20, 20)
                if abs(x) > 2.5 or abs(z) > 20:
                    draw_tree(x, z)
            
            for x, z in generate_small_rocks(400, spread=22):
                if abs(x) > 2.5:  
                    draw_small_rock(x, z)
            
            glfw.swap_buffers(window)
            glfw.poll_events()
            
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")
    finally:
        glfw.terminate()

if __name__ == "__main__":
    main()