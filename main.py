import glfw
from OpenGL.GL import *
import numpy as np
import glm
import math

from model import *
from shader import Shader

height = 1600
width = 1200

camera_pos   = glm.vec3(0.0,  0.0,  1.0);
camera_front = glm.vec3(0.0,  0.0, -1.0);
camera_up    = glm.vec3(0.0,  1.0,  0.0);

polygonal_mode = False

first_mouse = True
yaw = -90.0 
pitch = 0.0
lastX =  width/2
lastY =  height/2

camera_speed = 0.2
mouse_sensitivity = 0.3

def key_event(window, key, scancode, action, mods):
    global camera_pos, camera_front, camera_up, polygonal_mode, camera_speed
           
    if key == glfw.KEY_W and (action==1 or action==2):
        camera_pos += camera_speed * camera_front
    
    if key == glfw.KEY_S and (action==1 or action==2):
        camera_pos -= camera_speed * camera_front
    
    if key == glfw.KEY_A and (action==1 or action==2):
        camera_pos -= glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed
        
    if key == glfw.KEY_D and (action==1 or action==2):
        camera_pos += glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed
        
    if key == glfw.KEY_P and action==1:
        polygonal_mode= not polygonal_mode

def mouse_event(window, xpos, ypos):
    global first_mouse, camera_front, yaw, pitch, lastX, lastY, mouse_sensitivity
    if first_mouse:
        lastX = xpos
        lastY = ypos
        first_mouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos

    xoffset *= mouse_sensitivity
    yoffset *= mouse_sensitivity

    yaw += xoffset;
    pitch += yoffset;
    
    if pitch >= 90.0: pitch = 90.0
    if pitch <= -90.0: pitch = -90.0

    front = glm.vec3()
    front.x = math.cos(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    front.y = math.sin(glm.radians(pitch))
    front.z = math.sin(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    camera_front = glm.normalize(front)

def model_matrix(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):
    angle = math.radians(angle)
    
    # Identity matrix
    matrix_transform = glm.mat4(1.0)

    matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))    
    
    matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(r_x, r_y, r_z))
    
    matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))
    
    return matrix_transform

def view_matrix(camera_position, camera_front, camera_up):
    mat_view = glm.lookAt(camera_position, camera_position + camera_front, camera_up);
    return mat_view

def projection_matrix():
    global height, width, inc_fov, inc_near, inc_far
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(45.0), width/height, 0.1, 1000.0)
    return mat_projection

def main():
    global width, height, camera_pos, camera_front, camera_up, polygonal_mode, lastX, lastY

    # Initializing GLFW window
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
    window = glfw.create_window(width, height, "TrabalhoCG", None, None)
    glfw.make_context_current(window)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)

    # Initialing OpenGL program
    vertex_code = """
        attribute vec3 position;
        attribute vec2 texture_coord;
        varying vec2 out_texture;
                
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;        
        
        void main(){
            gl_Position = projection * view * model * vec4(position,1.0);
            out_texture = vec2(texture_coord);
        }
        """

    fragment_code = """
            uniform vec4 color;
            varying vec2 out_texture;
            uniform sampler2D samplerTexture;
            
            void main(){
                vec4 texture = texture2D(samplerTexture, out_texture);
                gl_FragColor = texture;
            }
            """

    shader = Shader(vertex_code, fragment_code)
    shader.useProgram()

    # Textures
    glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
    glEnable(GL_BLEND)
    glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_TEXTURE_2D)
    texture_amount = 10
    textures = glGenTextures(texture_amount)

    vertices_list = []    
    textures_coord_list = []
    texture_id = 0
    uploaded_objects = []
    texture_id = load_model_helper('references/caixa/caixa.obj','references/caixa/caixa2.jpg', uploaded_objects, vertices_list, textures_coord_list, texture_id)

    # Request a buffer slot from GPU
    buffer = glGenBuffers(2)

    # Uploading vertices data
    vertices = np.zeros(len(vertices_list), [("position", np.float32, 3)])
    vertices['position'] = vertices_list
    glBindBuffer(GL_ARRAY_BUFFER, buffer[0])
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)
    loc_vertices = shader.getAttributeLocation("position")
    glEnableVertexAttribArray(loc_vertices)
    glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

    # Uploading texture data
    textures = np.zeros(len(textures_coord_list), [("position", np.float32, 2)]) # duas coordenadas
    textures['position'] = textures_coord_list
    glBindBuffer(GL_ARRAY_BUFFER, buffer[1])
    glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
    stride = textures.strides[0]
    offset = ctypes.c_void_p(0)
    loc_texture_coord = shader.getAttributeLocation("texture_coord")
    glEnableVertexAttribArray(loc_texture_coord)
    glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)

    # Setting GLFW callbacks
    glfw.set_key_callback(window,key_event)
    glfw.set_cursor_pos_callback(window, mouse_event)

    # Starting window
    glfw.show_window(window)
    glfw.set_cursor_pos(window, lastX, lastY)

    # 3D depth test
    glEnable(GL_DEPTH_TEST)
    
    while not glfw.window_should_close(window):
        glfw.poll_events() 
        
        # Clearing buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        
        # Changing polygon mode
        if polygonal_mode==True:
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
        if polygonal_mode==False:
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)

        # Applying transformations
        # Rotation
        angle = 0.0;
        r_x = 0.0; r_y = 0.0; r_z = 1.0;
        # Translation
        t_x = 0.0; t_y = -1.0; t_z = 0.0;
        # Scale
        s_x = 1.0; s_y = 1.0; s_z = 1.0;
        
        mat_model = model_matrix(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        
        #define id da textura do modelo
        glBindTexture(GL_TEXTURE_2D, 0)
        
        # desenha o modelo
        glDrawArrays(GL_TRIANGLES, 0, 36) ## renderizando
        
        mat_view = view_matrix(camera_pos, camera_front, camera_up)
        loc_view = shader.getUniformLocation("view")
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(mat_view))

        mat_projection = projection_matrix()
        loc_projection = shader.getUniformLocation("projection")
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(mat_projection))  
        
        glfw.swap_buffers(window)

    glfw.terminate()



if __name__ == "__main__":
    main()