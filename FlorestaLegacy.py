import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import math

# Constantes para largura da janela, altura, altura do jogador, velocidade e sensibilidade do mouse
LARGURA, ALTURA = 1280, 720
PLAYER_HEIGHT = 0.6
VELOCIDADE = 3.0
SENSIBILIDADE = 0.1
NUM_POSTES = 4
GRAVIDADE = 10 * 0.2 # Ajuste a gravidade para um efeito melhor no jogo
FORCA_PULO = 1.0
y_velocity = 0.0
is_jumping = False# Número de postes com luzes

# Variáveis globais
cam_pos = np.array([0.0, PLAYER_HEIGHT, 5.0], dtype=np.float32)
cam_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
cam_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
yaw, pitch = -90.0, 0.0
keys = {}
collision_objects = []  # Lista para objetos com colisão
mouse_first_move = True
last_x, last_y = LARGURA / 2, ALTURA / 2


def key_callback(window, key, scancode, action, mods):
    global keys, is_jumping, y_velocity # <<< MUDANÇA: Adiciona as variáveis do pulo
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key == glfw.KEY_SPACE and action == glfw.PRESS:
        if not is_jumping: # Só pode pular se não estiver no ar
            is_jumping = True
            y_velocity = FORCA_PULO

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

    move_dir[1] = 0
    if np.linalg.norm(move_dir) > 0:
        move_dir = move_dir / np.linalg.norm(move_dir)
        
    move_dir *= velocity
    
    new_pos = cam_pos + move_dir

    temp_pos_for_collision = np.array([new_pos[0], PLAYER_HEIGHT, new_pos[2]])

    if not check_collision(temp_pos_for_collision):
        cam_pos[0] = new_pos[0]
        cam_pos[2] = new_pos[2]
    else:
        # Lógica de deslizar (sliding)
        new_pos_x = np.array([new_pos[0], cam_pos[1], cam_pos[2]])
        if not check_collision(np.array([new_pos_x[0], PLAYER_HEIGHT, new_pos_x[2]])):
            cam_pos[0] = new_pos_x[0]

        new_pos_z = np.array([cam_pos[0], cam_pos[1], new_pos[2]])
        if not check_collision(np.array([new_pos_z[0], PLAYER_HEIGHT, new_pos_z[2]])):
            cam_pos[2] = new_pos_z[2]

def setup_collision_objects():
    global collision_objects
    collision_objects = [] # Limpa a lista para o frame atual

    # 1. Adicionar cercas à lista de colisão
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
        
    # 2. Adicionar árvores à lista de colisão
    random.seed(42) # Garante que as árvores estejam sempre no mesmo lugar
    for _ in range(100):
        x, z = random.uniform(-20, 20), random.uniform(-20, 20)
        if abs(x) > 2.5 or abs(z) > 20:
             # Adiciona o tronco da árvore como um objeto de colisão
            trunk_height = 1.0
            trunk_width = 0.2
            collision_objects.append({
                'pos': (x, trunk_height / 2, z),
                'size': (trunk_width, trunk_height, trunk_width)
            })

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

def draw_fences_along_road(road_width=3.0, road_length=50.0, spacing=1.0):
    z = -road_length/2
    while z < road_length/2:
        draw_small_fence(-road_width/2 - 0.3, z, spacing=spacing)
        draw_small_fence(road_width/2 + 0.3, z, spacing=spacing)
        z += spacing
        
def draw_ground():
    glColor3f(0.0, 0.2, 0.0)
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-25, 0, -25)
    glVertex3f(-25, 0, 25)
    glVertex3f(25, 0, 25)
    glVertex3f(25, 0, -25)
    glEnd()

def draw_small_rock(x=0, z=0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glScalef(0.2, 0.1, 0.2)
    glColor3f(0.41, 0.41, 0.41)
    draw_cube(0, 0, 0)
    glPopMatrix()

def generate_small_rocks(count=500, spread=20):
    return [(random.uniform(-spread, spread), random.uniform(-spread, spread)) for _ in range(count)]

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
               
def draw_asphalt(width=5.0, length=50.0): 
    glColor3f(0.05, 0.05, 0.05)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-width/2, 0.01, -length/2)
    glVertex3f(-width/2, 0.01, length/2)
    glVertex3f(width/2, 0.01, length/2)
    glVertex3f(width/2, 0.01, -length/2)
    glEnd()
    
    stripe_width = 0.2
    stripe_length = 2.0
    gap_length = 4.0
    glColor3f(1.0, 0.9, 0.0)
    
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
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glPushMatrix()
    glTranslatef(cam_pos[0], cam_pos[1], cam_pos[2])
    size = 10
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.1, 0.44)
    glVertex3f(-size, -size, -size); glVertex3f(size, -size, -size); glVertex3f(size, size, -size); glVertex3f(-size, size, -size)
    glVertex3f(-size, -size, size); glVertex3f(size, -size, size); glVertex3f(size, size, size); glVertex3f(-size, size, size)
    glVertex3f(-size, -size, -size); glVertex3f(-size, -size, size); glVertex3f(-size, size, size); glVertex3f(-size, size, -size)
    glVertex3f(size, -size, -size); glVertex3f(size, -size, size); glVertex3f(size, size, size); glVertex3f(size, size, -size)
    glVertex3f(-size, size, -size); glVertex3f(size, size, -size); glVertex3f(size, size, size); glVertex3f(-size, size, size)
    glEnd()
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

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

    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [2.0, 1.0, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, LARGURA / ALTURA, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    last_time = glfw.get_time()

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
            draw_asphalt(width=3.0, length=50.0)
            draw_fences_along_road(road_width=3.0, road_length=50.0, spacing=1.0)

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
        print(f"Erro: {str(e)}")
    finally:
        glfw.terminate()

if __name__ == "__main__":
    main()