import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
import math
import random
import glm
from shader import Shader
import ctypes

# Configurações
LARGURA, ALTURA = 1280, 720
PLAYER_HEIGHT = 0.5
VELOCIDADE = 3.0
SENSIBILIDADE = 0.1

class camera:
    def __init__(self):
        self.pos = glm.vec3(0.0, PLAYER_HEIGHT, 5.0)
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw, self.pitch = -90.0, 0.0

def create_cube_vertices():
    vertices = [
        # Positions          # Colors
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,
         0.5, -0.5, -0.5,  1.0, 0.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 0.0, 0.0,
        -0.5,  0.5, -0.5,  1.0, 0.0, 0.0,
        
        -0.5, -0.5,  0.5,  0.0, 1.0, 0.0,
         0.5, -0.5,  0.5,  0.0, 1.0, 0.0,
         0.5,  0.5,  0.5,  0.0, 1.0, 0.0,
        -0.5,  0.5,  0.5,  0.0, 1.0, 0.0,
    ]
    return np.array(vertices, dtype=np.float32)

def create_cube_indices():
    indices = [
        0, 1, 2, 2, 3, 0, 4, 5, 6, 6, 7, 4,
        3, 2, 6, 6, 7, 3, 0, 1, 5, 5, 4, 0,
        0, 3, 7, 7, 4, 0, 1, 2, 6, 6, 5, 1
    ]
    return np.array(indices, dtype=np.uint32)

class Mesh:
    def __init__(self, vertices, indices):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)
        
        glBindVertexArray(self.VAO)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        
        # Position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Color attribute
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        
        glBindVertexArray(0)

def key_callback(window, key, scancode, action, mods):
    global keys
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    keys[key] = action == glfw.PRESS or action == glfw.REPEAT

def mouse_callback(window, xpos, ypos):
    global mouse_first_move, last_x, last_y
    
    if mouse_first_move:
        last_x, last_y = xpos, ypos
        mouse_first_move = False
    
    xoffset = xpos - last_x
    yoffset = last_y - ypos
    last_x, last_y = xpos, ypos
    
    camera.yaw += xoffset * SENSIBILIDADE
    camera.pitch += yoffset * SENSIBILIDADE
    camera.pitch = max(-89.0, min(89.0, camera.pitch))
    
    front = glm.vec3()
    front.x = math.cos(glm.radians(camera.yaw)) * math.cos(glm.radians(camera.pitch))
    front.y = math.sin(glm.radians(camera.pitch))
    front.z = math.sin(glm.radians(camera.yaw)) * math.cos(glm.radians(camera.pitch))
    camera.front = glm.normalize(front)

def process_input(window, delta_time):
    velocity = VELOCIDADE * delta_time
    
    if keys.get(glfw.KEY_W, False):
        camera.pos += camera.front * velocity
    if keys.get(glfw.KEY_S, False):
        camera.pos -= camera.front * velocity
    
    right = glm.normalize(glm.cross(camera.front, camera.up))
    if keys.get(glfw.KEY_A, False):
        camera.pos -= right * velocity
    if keys.get(glfw.KEY_D, False):
        camera.pos += right * velocity
    
    camera.pos.y = PLAYER_HEIGHT

def main():
    if not glfw.init():
        print("Failed to initialize GLFW")
        return
    
    # Configuração da janela para OpenGL 3.3 Core
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.RESIZABLE, False)

    window = glfw.create_window(LARGURA, ALTURA, "OpenGL Moderno", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")
    
    glfw.make_context_current(window)
    
    # Verificação opcional de versão do OpenGL
    print(f"OpenGL version: {glGetString(GL_VERSION).decode('utf-8')}")
    
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    
    glEnable(GL_DEPTH_TEST)
    
    # Carrega shaders
    shader = Shader("shaders/vertex.shader", "shaders/fragment.shader")
    cube_mesh = Mesh(create_cube_vertices(), create_cube_indices())
    
    projection = glm.perspective(glm.radians(45.0), LARGURA/ALTURA, 0.1, 100.0)
    
    # Posições dos cubos na cena
    cube_positions = [
        glm.vec3(0.0, 0.5, 0.0),
        glm.vec3(2.0, 1.0, -1.0),
        glm.vec3(-1.5, 0.2, -2.5)
    ]
    
    last_time = glfw.get_time()
    
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time
        
        process_input(window, delta_time)
        
        glClearColor(0.1, 0.1, 0.44, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        shader.use()
        shader.set_mat4("projection", projection)
        
        view = glm.lookAt(
            camera.pos,
            camera.pos + camera.front,
            camera.up
        )
        shader.set_mat4("view", view)
        
        # Renderiza cubos
        glBindVertexArray(cube_mesh.VAO)
        for i, pos in enumerate(cube_positions):
            model = glm.mat4(1.0)
            model = glm.translate(model, pos)
            angle = 20.0 * i
            model = glm.rotate(model, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))
            shader.set_mat4("model", model)
            glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glfw.terminate()

if __name__ == "__main__":
    main()