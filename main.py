import glfw
from OpenGL.GL import *
import numpy as np
import glm
import math

from model import Model
from shader import Shader
from model_helper import ModelHelper

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
           
    if key == glfw.KEY_W and (action==glfw.PRESS or action==glfw.REPEAT):
        camera_pos += camera_speed * camera_front
    
    if key == glfw.KEY_S and (action==glfw.PRESS or action==glfw.REPEAT):
        camera_pos -= camera_speed * camera_front
    
    if key == glfw.KEY_A and (action==glfw.PRESS or action==glfw.REPEAT):
        camera_pos -= glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed
        
    if key == glfw.KEY_D and (action==glfw.PRESS or action==glfw.REPEAT):
        camera_pos += glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed
        
    if key == glfw.KEY_P and action==glfw.PRESS:
        polygonal_mode= not polygonal_mode

    if key == glfw.KEY_Q and action==glfw.PRESS:
        glfw.set_window_should_close(window, True)
    
    if key == glfw.KEY_LEFT_SHIFT and action==glfw.PRESS:
        camera_speed = 1.0
    if key == glfw.KEY_LEFT_SHIFT and action==glfw.RELEASE:
        camera_speed = 0.2

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

def view_matrix(camera_position, camera_front, camera_up):
    mat_view = glm.lookAt(camera_position, camera_position + camera_front, camera_up);
    return mat_view

def projection_matrix(height, width):
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
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

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

    # Loading Models
    box = Model('box', 'crate/Crate1.obj',['crate/crate_1.jpg'], [0])
    box.position = glm.vec3(0.0, -1.0, 0.0)
    box.rotation = glm.vec3(0.0, 0.0, 1.0)
    box.scale = glm.vec3(1.0, 1.0, 1.0)

    tree = Model('tree', 'references/arvore/arvore10.obj',['references/arvore/bark_0021.jpg', 'references/arvore/DB2X2_L01.png'], [1,2])
    tree.position = glm.vec3(0.0, -1.0, 3.0)
    tree.rotation = glm.vec3(0.0, 0.0, 1.0)
    tree.scale = glm.vec3(1.0, 1.0, 1.0)

    # Loading all models into a helper
    ModelHelper.attach_model(box)
    ModelHelper.attach_model(tree)
    ModelHelper.upload_models(shader)

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

        mat_model = box.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('box', GL_QUADS)

        mat_model = tree.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('tree', GL_TRIANGLES)
        
        mat_view = view_matrix(camera_pos, camera_front, camera_up)
        loc_view = shader.getUniformLocation("view")
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(mat_view))

        mat_projection = projection_matrix(height, width)
        loc_projection = shader.getUniformLocation("projection")
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(mat_projection))  
        
        glfw.swap_buffers(window)

    glfw.terminate()



if __name__ == "__main__":
    main()