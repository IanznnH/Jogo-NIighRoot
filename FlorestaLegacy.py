import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import math

#Largura da janela, altura, altura do jogador, velocidade e sensibilidade do mouse
LARGURA, ALTURA = 1280, 720
PLAYER_HEIGHT = 0.6
VELOCIDADE = 3.0
SENSIBILIDADE = 0.1
GRAVIDADE = 10 * 0.2 # Gravidade 
FORCA_PULO = 1.0
y_velocity = 0.0
is_jumping = False

# Variáveis globais
cam_pos = np.array([0.0, PLAYER_HEIGHT, 5.0], dtype=np.float32)
cam_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
cam_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
yaw, pitch = -90.0, 0.0
keys = {}
collision_objects = []  # Lista para objetos com colisão
tree_positions = []
rock_positions = []# Lista para posições de árvores
mouse_first_move = True
last_x, last_y = LARGURA / 2, ALTURA / 2


def key_callback(window, key, scancode, action, mods):
    global keys, is_jumping, y_velocity
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key == glfw.KEY_SPACE and action == glfw.PRESS:
        if not is_jumping: # Para evitar o pulo duas vezes
            is_jumping = True
            y_velocity = FORCA_PULO

    if action == glfw.PRESS or action == glfw.RELEASE:# Atualiza o estado da tecla
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
    pitch = max(-89.0, min(89.0, pitch))
    front = np.array([
        math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)),
        math.sin(math.radians(pitch)),
        math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    ])
    cam_front = front / np.linalg.norm(front)
    
def check_collision(new_pos):
    # A caixa de colisão do jogador é aproximada por um raio
    player_radius = 0.3 
    
    # Verifica colisão com cada objeto na lista
    for obj in collision_objects:
        obj_pos = obj['pos']
        obj_size = obj['size']
        dx = abs(new_pos[0] - obj_pos[0]) - (player_radius + obj_size[0] / 2)
        dy = abs(new_pos[1] - obj_pos[1]) - (player_radius + obj_size[1] / 2)
        dz = abs(new_pos[2] - obj_pos[2]) - (player_radius + obj_size[2] / 2)

        # Se as distâncias em todos os eixos forem negativas, há uma colisão
        if dx < 0 and dy < 0 and dz < 0:
            return True # Colisão detectada


def process_input(window, delta_time):
    global cam_pos, y_velocity, is_jumping 

    if is_jumping:
        # Aplica a velocidade vertical à posição do jogador
        cam_pos[1] += y_velocity * delta_time
        # Aplica a gravidade à velocidade vertical
        y_velocity -= GRAVIDADE * delta_time
        
        if cam_pos[1] <= PLAYER_HEIGHT:
            cam_pos[1] = PLAYER_HEIGHT
            is_jumping = False
            y_velocity = 0

    velocity = VELOCIDADE * delta_time
    right = np.cross(cam_front, cam_up)
    right /= np.linalg.norm(right)
    
    move_dir = np.zeros(3)
    if keys.get(glfw.KEY_W, False):
        move_dir += cam_front
    if keys.get(glfw.KEY_S, False):
        move_dir -= cam_front
    if keys.get(glfw.KEY_A, False):
        move_dir -= right
    if keys.get(glfw.KEY_D, False):
        move_dir += right
        
    move_dir *= velocity
    
    new_pos = cam_pos + move_dir

    temp_pos_for_collision = np.array([new_pos[0], PLAYER_HEIGHT, new_pos[2]])
# Verifica colisão com a nova posição
    if not check_collision(temp_pos_for_collision):
        cam_pos[0] = new_pos[0]
        cam_pos[2] = new_pos[2]
    else:# Se houver colisão, tenta ajustar a posição
        new_pos_x = np.array([new_pos[0], cam_pos[1], cam_pos[2]])
        if not check_collision(np.array([new_pos_x[0], PLAYER_HEIGHT, new_pos_x[2]])):
            cam_pos[0] = new_pos_x[0]

        new_pos_z = np.array([cam_pos[0], cam_pos[1], new_pos[2]])
        if not check_collision(np.array([new_pos_z[0], PLAYER_HEIGHT, new_pos_z[2]])):
            cam_pos[2] = new_pos_z[2]
# Função para configurar os objetos de colisão
def setup_collision_objects():
    global collision_objects
    collision_objects = []

    #Adicionacercas à lista de colisão
    road_width=3.0
    road_length=50.0
    spacing=1.0
    z = -road_length/2
    while z < road_length/2:
        # Cerca da esquerda
        x_left = -road_width/2 - 0.2
        collision_objects.append({'pos': (x_left, 0.5/2, z), 'size': (0.05, 0.5, 0.0)})
        # Cerca da direita
        x_right = road_width/2 + 0.2
        collision_objects.append({'pos': (x_right, 0.5/2, z), 'size': (0.05, 0.5, 0.0)})
        z += spacing
        
    #Adiciona árvores à lista de colisão
    trunk_height = 1.0
    trunk_width = 0.2
    for x, z in tree_positions:
        collision_objects.append({
            'pos': (x, trunk_height / 2, z),
            'size': (trunk_width, trunk_height, trunk_width)
        })
#Adiciona as pedras à lista de colisão
def draw_small_fence(x, z, height=0.5, width=0.05, spacing=1.0):
    glDisable(GL_LIGHTING)
    # Desenha o poste vertical
    glPushMatrix()
    glTranslatef(x, height/2, z)
    glScalef(width, height, width)
    glColor3f(0.24, 0.17, 0.12)
    draw_cube(0, 0, 0)
    glPopMatrix()
    
    # Desenha as barras horizontais
    bar_length = spacing * 1.0
    for y_pos in [0.2, 0.5, 0.8]:
        glPushMatrix()
        glTranslatef(x, height*y_pos, z)
        glScalef(width, width, bar_length)
        glColor3f(0.24, 0.17, 0.12)
        draw_cube(0, 0, 0)
        glPopMatrix()
    
    glEnable(GL_LIGHTING)
# Função para desenhar cercas ao longo da estrada
def draw_fences_along_road(road_width=3.0, road_length=50.0, spacing=1.0):
    z = -road_length/2
    while z < road_length/2:
        draw_small_fence(-road_width/2 - 0.3, z, spacing=spacing)
        draw_small_fence(road_width/2 + 0.3, z, spacing=spacing)
        z += spacing
# Função para desenhar o chão        
def draw_ground():
    glColor3f(0.0, 0.2, 0.0)
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-25, 0, -25)
    glVertex3f(-25, 0, 25)
    glVertex3f(25, 0, 25)
    glVertex3f(25, 0, -25)
    glEnd()
# Função para desenhar uma pequena pedra    
def draw_small_rock(x=0, z=0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glScalef(0.2, 0.1, 0.2)
    glColor3f(0.41, 0.41, 0.41)
    draw_cube(0, 0, 0)
    glPopMatrix()
# Função para gerar posições de pedras estáticas   
def generate_static_rock_positions(count=400, spread=22):
    global rock_positions
    rock_positions = []  # Limpa a lista para garantir
    random.seed(43) # Usamos uma "seed" para que a aleatoriedade seja sempre a mesma
    
    for _ in range(count):
        # Gera uma posição aleatória
        x = random.uniform(-spread, spread)
        z = random.uniform(-spread, spread)
        
        # Adiciona a pedra na lista apenas se ela NÃO estiver no caminho principal
        if abs(x) > 2.5:
            rock_positions.append((x, z))
# Função para gerar posições de árvores ao longo da estrada
def generate_tree_positions(road_width=3.0, road_length=50.0, spacing=5.0):
    global tree_positions
    tree_positions = []
    random.seed(42) 

    z = -road_length / 2
    while z < road_length / 2:
        random_z_offset = random.uniform(-spacing / 3, spacing / 3)
        current_z = z + random_z_offset
        # Lado direito
        x_right = road_width / 5 + 2.0 + random.uniform(0.0, 1.5)
        tree_positions.append((x_right, current_z))
        # Lado esquerdo
        x_left = -road_width / 5 - 2.0 - random.uniform(0.0, 1.5)
        tree_positions.append((x_left, current_z))
        
        z += spacing
        
def draw_tree(x=0, z=0):
    trunk_height = 1.0
    trunk_width = 0.2
    glColor3f(0.24, 0.17, 0.12)
    glPushMatrix()
    glTranslatef(x, trunk_height / 2, z)
    glScalef(trunk_width, trunk_height, trunk_width)
    draw_cube(0, 0, 0)
    glPopMatrix()
    glColor3f(0.0, 0.39, 0.0)
    for i in range(3):
        layer_size = 1.2 - i * 0.3
        layer_height = trunk_height + i * 0.5
        glPushMatrix()
        glTranslatef(x, layer_height, z)
        glScalef(layer_size, 0.5, layer_size)
        draw_cube(0, 0, 0)
        glPopMatrix()
# Função o chão verde                       
def draw_chao(width=5.0, length=50.0): 
    glColor3f(0.22, 0.36, 0.28)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-width/2, 0.01, -length/2)
    glVertex3f(-width/2, 0.01, length/2)
    glVertex3f(width/2, 0.01, length/2)
    glVertex3f(width/2, 0.01, -length/2)
    glEnd()
# Função para desenhar o céu        
def draw_sky():
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glPushMatrix()
    glTranslatef(cam_pos[0], cam_pos[1], cam_pos[2])
    size = 10
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(-size, -size, -size); glVertex3f(size, -size, -size); glVertex3f(size, size, -size); glVertex3f(-size, size, -size) # Fundo
    glVertex3f(-size, -size, size); glVertex3f(size, -size, size); glVertex3f(size, size, size); glVertex3f(-size, size, size) # Frente
    glVertex3f(-size, -size, -size); glVertex3f(-size, -size, size); glVertex3f(-size, size, size); glVertex3f(-size, size, -size) # Esquerda 
    glVertex3f(size, -size, -size); glVertex3f(size, -size, size); glVertex3f(size, size, size); glVertex3f(size, size, -size) # Direita
    glVertex3f(-size, size, -size); glVertex3f(size, size, -size); glVertex3f(size, size, size); glVertex3f(-size, size, size) # Cima
    glEnd()
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
# Função para desenhar um cubo
def draw_cube(x, y, z, size=1):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(size, size, size)
    glBegin(GL_QUADS)   
    glNormal3f(0.0, 0.0, 1.0); glVertex3f(-0.5, -0.5, 0.5); glVertex3f(0.5, -0.5, 0.5); glVertex3f(0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)
    glNormal3f(0.0, 0.0, -1.0); glVertex3f(-0.5, -0.5, -0.5); glVertex3f(0.5, -0.5, -0.5); glVertex3f(0.5, 0.5, -0.5); glVertex3f(-0.5, 0.5, -0.5)
    glNormal3f(-1.0, 0.0, 0.0); glVertex3f(-0.5, -0.5, -0.5); glVertex3f(-0.5, -0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, -0.5)
    glNormal3f(1.0, 0.0, 0.0); glVertex3f(0.5, -0.5, -0.5); glVertex3f(0.5, -0.5, 0.5); glVertex3f(0.5, 0.5, 0.5); glVertex3f(0.5, 0.5, -0.5)
    glNormal3f(0.0, 1.0, 0.0); glVertex3f(-0.5, 0.5, -0.5); glVertex3f(0.5, 0.5, -0.5); glVertex3f(0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)
    glNormal3f(0.0, -1.0, 0.0); glVertex3f(-0.5, -0.5, -0.5); glVertex3f(0.5, -0.5, -0.5); glVertex3f(0.5, -0.5, 0.5); glVertex3f(-0.5, -0.5, 0.5)
    glEnd()
    glPopMatrix()
# Função para desenhar o sol
def draw_sun():
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glColor3f(1.0, 0.9, 0.6)
    glTranslatef(45.0, 15.0, -10.0)
    glScalef(2.0, 2.0, 2.0)
    draw_cube(0, 0, 0)
    glPopMatrix()
    glEnable(GL_LIGHTING)

def main():
    if not glfw.init():
        print("Erro ao inicializar GLFW")
        return
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_ANY_PROFILE)
    
    window = glfw.create_window(LARGURA, ALTURA, "Floresta com Pedras", None, None)
    if not window:
        glfw.terminate()
        print("Erro ao criar janela GLFW")
        return
    
    glfw.make_context_current(window)
    
    if not glGetString(GL_VERSION):
        print("Erro: OpenGL não está disponível")
        glfw.terminate()
        return
    
    print(f"OpenGL versão: {glGetString(GL_VERSION).decode('utf-8')}")
    
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.8, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [2.0, 1.0, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, LARGURA / ALTURA, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    last_time = glfw.get_time()
    
    generate_tree_positions(spacing=2.5)
    generate_static_rock_positions()

    try:
        while not glfw.window_should_close(window):
            current_time = glfw.get_time()
            delta_time = current_time - last_time
            last_time = current_time

            setup_collision_objects()
            process_input(window, delta_time)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            center = cam_pos + cam_front
            gluLookAt(*cam_pos, *center, *cam_up)
            
            sun_pos = [5.0, 8.0, 1.0, 0.0]
            glLightfv(GL_LIGHT0, GL_POSITION, sun_pos)

            draw_sky()
            draw_sun()
            draw_ground()
            draw_chao(width=3.0, length=50.0)
            draw_fences_along_road(road_width=3.0, road_length=50.0, spacing=1.0)

            for x, z in tree_positions:
                draw_tree(x, z)
            
            for x, z in rock_positions:
                draw_small_rock(x, z)
            
            glfw.swap_buffers(window)
            glfw.poll_events()
            
    except Exception as e:
        print(f"Erro: {str(e)}")
    finally:
        glfw.terminate()

if __name__ == "__main__":
    main()