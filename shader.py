from OpenGL.GL import *

class Shader:
    __program = None

    def __init__(self, vertex_code:str, fragment_code:str) -> None:
        # Request a program and shader slots from GPU
        program  = glCreateProgram()
        vertex   = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)

        # Set shaders source
        glShaderSource(vertex, vertex_code)
        glShaderSource(fragment, fragment_code)

        # Compile shaders
        glCompileShader(vertex)
        if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vertex).decode()
            print(error)
            raise RuntimeError("Vertex Shader compiling error")

        glCompileShader(fragment)
        if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(fragment).decode()
            print(error)
            raise RuntimeError("Frament Shader compiling error")

        # Attach shader objects to the program
        glAttachShader(program, vertex)
        glAttachShader(program, fragment)

        # Build program
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            print(glGetProgramInfoLog(program))
            raise RuntimeError('Linking error')
        
        self.__program = program

    def useProgram(self) -> None:
        glUseProgram(self.__program)

    def getAttributeLocation(self, attribute:str) -> int:
        return glGetAttribLocation(self.__program, attribute)
    
    def getUniformLocation(self, uniform:str) -> int:
        return glGetUniformLocation(self.__program, uniform)