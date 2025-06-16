from OpenGL.GL import *
import glm
import ctypes

class Shader:
    def __init__(self, vertex_path, fragment_path):
        vertex_code = self._load_shader_file(vertex_path)
        fragment_code = self._load_shader_file(fragment_path)
        
        vertex_shader = self._compile_shader(GL_VERTEX_SHADER, vertex_code)
        fragment_shader = self._compile_shader(GL_FRAGMENT_SHADER, fragment_code)
        
        self.ID = glCreateProgram()
        glAttachShader(self.ID, vertex_shader)
        glAttachShader(self.ID, fragment_shader)
        glLinkProgram(self.ID)
        
        if not glGetProgramiv(self.ID, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.ID).decode()
            raise RuntimeError(f"Shader linking error: {error}")
        
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
    
    def _load_shader_file(self, path):
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            raise RuntimeError(f"Error loading shader {path}: {str(e)}")
    
    def _compile_shader(self, shader_type, source):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            glDeleteShader(shader)
            raise RuntimeError(f"Shader compilation error: {error}")
        return shader
    
    def use(self):
        glUseProgram(self.ID)
    
    def set_mat4(self, name, value):
        loc = glGetUniformLocation(self.ID, name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(value))
    
    def set_vec3(self, name, value):
        loc = glGetUniformLocation(self.ID, name)
        glUniform3fv(loc, 1, glm.value_ptr(value))