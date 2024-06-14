import glfw
from OpenGL.GL import *
import numpy as np
import glm
import math

from model import Model
from shader import Shader
from model_helper import ModelHelper
from camera import Camera

height = 1600
width = 1200

camera_speed = 0.2
mouse_sensitivity = 0.3
camera = Camera(mouse_sensitivity, camera_speed)

polygonal_mode = False

first_mouse = True
lastX =  width/2
lastY =  height/2
scale = 12.0


def resize_event(window, new_width, new_height):
    global width, height
    width = new_width
    height = new_height
    glViewport(0, 0, new_width, new_height)

def key_event(window, key, scancode, action, mods):
    global camera, polygonal_mode, camera_speed, scale
           
    if key == glfw.KEY_W and (action==glfw.PRESS or action==glfw.REPEAT):
        camera.set_position(camera.position + (camera.speed * camera.front))
    
    if key == glfw.KEY_S and (action==glfw.PRESS or action==glfw.REPEAT):
        camera.set_position(camera.position - (camera.speed * camera.front))
    
    if key == glfw.KEY_A and (action==glfw.PRESS or action==glfw.REPEAT):
        camera.set_position(camera.position - (glm.normalize(glm.cross(camera.front, camera.up)) * camera.speed))
        
    if key == glfw.KEY_D and (action==glfw.PRESS or action==glfw.REPEAT):
        camera.set_position(camera.position + (glm.normalize(glm.cross(camera.front, camera.up)) * camera.speed))
        
    if key == glfw.KEY_P and action==glfw.PRESS:
        polygonal_mode= not polygonal_mode

    if key == glfw.KEY_Q and action==glfw.PRESS:
        glfw.set_window_should_close(window, True)
    
    if key == glfw.KEY_LEFT_SHIFT and action==glfw.PRESS:
        camera.speed = 1.0
    if key == glfw.KEY_LEFT_SHIFT and action==glfw.RELEASE:
        camera.speed = 0.2

    if key == glfw.KEY_E and (action==glfw.PRESS or action==glfw.REPEAT):
        scale += 0.1

    if key == glfw.KEY_R and (action==glfw.PRESS or action==glfw.REPEAT):
        scale -= 0.1

def mouse_event(window, xpos, ypos):
    global first_mouse, camera_front, lastX, lastY, mouse_sensitivity
    if first_mouse:
        lastX = xpos
        lastY = ypos
        first_mouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos

    camera.update_front(xoffset, yoffset)

def view_matrix(camera):
    return camera.look_at()

def projection_matrix(height, width):
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(45.0), width/height, 0.1, 10000.0)
    return mat_projection

def main():
    global width, height, polygonal_mode, lastX, lastY, camera, scale

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
        uniform vec2 texture_size;
        
        void main(){
            gl_Position = projection * view * model * vec4(position,1.0);
            out_texture = vec2(texture_coord*texture_size);
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
    skybox = Model('skybox', 'skybox/skybox.obj',['skybox/left.jpg', 'skybox/front.jpg', 'skybox/right.jpg', 'skybox/back.jpg', 'skybox/bottom.jpg', 'skybox/top.jpg'], [0,1,2,3,4,5])
    skybox.position = glm.vec3(0.0, 0.0, 0.0)
    skybox.rotation = glm.vec3(0.0, 0.0, 1.0)
    skybox.scale = glm.vec3(1000.0, 1000.0, 1000.0)

    tree = Model('tree', 'references/arvore/arvore10.obj',['references/arvore/bark_0021.jpg', 'references/arvore/DB2X2_L01.png'], [6,7])
    tree.position = glm.vec3(7.0, -2.8, 3.2)
    tree.rotation = glm.vec3(0.0, 0.0, 1.0)
    tree.scale = glm.vec3(2.5, 2.5, 2.5)

    road = Model('road', 'road/road/road.obj', ['road/road/road-texture.jpg'], [8])
    road.position = glm.vec3(0.0, -2.5, 10.0)
    road.rotation = glm.vec3(0.0, 1.0, 0.0)
    road.scale = glm.vec3(1.0,1,100.0)
    road.angle = 90

    terrain = Model('terrain', 'ground/terrain.obj', ['ground/aerial_grass_rock_diff_1k.jpg'], [9])
    terrain.position = glm.vec3(0.0, -2.875, 0.0)
    terrain.rotation = glm.vec3(1.0, 0.0, 0.0)
    terrain.scale = glm.vec3(200.0,200.0,1.0)
    terrain.angle = -90.0

    storage = Model('storage', 'storage/Farm_free_obj.obj', ['storage/textures/Farm_Free_BaseColor.png'], [10])
    storage.position = glm.vec3(0.0, -2.5, 0.0)
    storage.rotation = glm.vec3(0.0, 0.0, 1.0)
    storage.scale = glm.vec3(1.0,1.0,1.0)

    human = Model('human', 'human/human.obj', ['human/human.jpg'], [11])
    human.position = glm.vec3(0.0, -2.5, 0.0)
    human.rotation = glm.vec3(0.0, 0.0, 1.0)
    human.scale = glm.vec3(0.015,0.015,0.015)

    hay_cart = Model('haycart', 'hay_cart/hay_cart.obj', ['hay_cart/hay_cart.png'], [12])
    hay_cart.position = glm.vec3(-9.0, -2.5, 3.2)
    hay_cart.rotation = glm.vec3(0.0, 0.0, 1.0)
    hay_cart.scale = glm.vec3(1.0, 1.0, 1.0)

    dog = Model('dog', 'dog/dog.obj', ['dog/dog.png'], [13])
    dog.position = glm.vec3(0.4, -2.5, 0.0)
    dog.rotation = glm.vec3(0.0, 1.0, 0.0)
    dog.scale = glm.vec3(1.0,1.0,1.0)

    crate = Model('crate', 'crate/Wooden_Crate.obj', ['crate/Wooden_Crate_Crate_BaseColor.png'], [14])
    crate.position = glm.vec3(0.0, -2.4, -0.40)
    crate.rotation = glm.vec3(0.0, 1.0, 0.0)
    crate.scale = glm.vec3(0.12, 0.12, 0.12)

    demoman = Model('demoman', 'demomantf2/scene.obj', ['demomantf2/demoman_red.jpg', 'demomantf2/demoman_head.jpg', 'demomantf2/Eye-Blue.jpg'], [15,16,17])
    demoman.position = glm.vec3(-3.0, -2.7, -10.0)
    demoman.rotation = glm.vec3(0.0, 1.0, 0.0)
    demoman.scale = glm.vec3(12.0, 12.0, 12.0)

    # Loading all models into a helper
    ModelHelper.attach_model(skybox)
    ModelHelper.attach_model(tree)
    ModelHelper.attach_model(storage)
    ModelHelper.attach_model(terrain)
    ModelHelper.attach_model(road)
    ModelHelper.attach_model(human)
    ModelHelper.attach_model(hay_cart)
    ModelHelper.attach_model(dog)
    ModelHelper.attach_model(crate)
    ModelHelper.attach_model(demoman)

    ModelHelper.upload_models(shader)

    # Setting GLFW callbacks
    glfw.set_key_callback(window,key_event)
    glfw.set_cursor_pos_callback(window, mouse_event)
    glfw.set_framebuffer_size_callback(window, resize_event)

    # Starting window
    glfw.show_window(window)
    glfw.set_cursor_pos(window, lastX, lastY)

    # 3D depth test
    glEnable(GL_DEPTH_TEST)
    
    theta = 0.0
    radius = 1.5
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

        mat_view = view_matrix(camera)
        loc_view = shader.getUniformLocation("view")
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(mat_view))

        mat_projection = projection_matrix(height, width)
        loc_projection = shader.getUniformLocation("projection")
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, glm.value_ptr(mat_projection))  

        mat_model = skybox.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('skybox', GL_QUADS)

        mat_model = storage.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('storage', GL_QUADS)

        loc = shader.getUniformLocation("texture_size")
        glUniform2fv(loc, 1, [200.0, 200.0])

        mat_model = terrain.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('terrain', GL_TRIANGLES)

        loc = shader.getUniformLocation("texture_size")
        glUniform2fv(loc, 1, [1.0, 100.0])

        mat_model = road.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('road', GL_QUADS)

        loc = shader.getUniformLocation("texture_size")
        glUniform2fv(loc, 1, [1.0,1.0])

        mat_model = tree.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('tree', GL_TRIANGLES)
        
        mat_model = human.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('human', GL_TRIANGLES)
        
        mat_model = hay_cart.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('haycart', GL_TRIANGLES)

        # Making the dog rotate aroung a circle with a radius
        dog.position.x = math.sin(theta)*radius
        dog.position.z = math.cos(theta)*radius
        dog.angle = 90+math.degrees(theta)

        theta += 0.05
        if theta > 2*np.pi:
            theta = 0.0

        mat_model = dog.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('dog', GL_TRIANGLES)

        mat_model = crate.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('crate', GL_QUADS)

        demoman.angle += 1
        demoman.scale = glm.vec3(scale, scale, scale)
        mat_model = demoman.model_matrix()
        loc_model = shader.getUniformLocation("model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(mat_model))
        ModelHelper.render_model('demoman', GL_TRIANGLES)

        glfw.swap_buffers(window)

    glfw.terminate()



if __name__ == "__main__":
    main()