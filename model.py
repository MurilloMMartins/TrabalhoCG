from OpenGL.GL import *
from PIL import Image
import glm
import math

class Model:
    def __init__(self, name, model_path, texture_paths, texture_ids) -> None:
        self.name = name
        self.texture_id = texture_ids
        self.model = self.__load_model_from_file(model_path)
        
        for index, texture in enumerate(texture_paths):
            self.__load_texture_from_file(texture_ids[index], texture)
        
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.scale    = glm.vec3(1.0, 1.0, 1.0)
        self.angle    = 0

    def __load_model_from_file(self, filename):
        vertices = []
        texture_coords = []
        faces = []

        material = None

        # Opens .obj file
        for line in open(filename, "r"):
            # Ignore comments
            if line.startswith('#'): 
                continue

            values = line.split()
            if not values: 
                continue

            # Vertices
            if values[0] == 'v':
                vertices.append(values[1:4])

            # Texture Coordinates
            elif values[0] == 'vt':
                texture_coords.append(values[1:3])

            # Material 
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]

            # Faces
            elif values[0] == 'f':
                face = []
                face_texture = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        face_texture.append(int(w[1]))
                    else:
                        face_texture.append(0)

                faces.append((face, face_texture, material))

        model = {}
        model['vertices'] = vertices
        model['texture'] = texture_coords
        model['faces'] = faces

        return model
    
    def __load_texture_from_file(self, texture_id, texture_filename):
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        img = Image.open(texture_filename)
        print(texture_filename,img.mode)
        img_width = img.size[0]
        img_height = img.size[1]
        image_data = img.convert("RGBA").tobytes("raw", "RGBA",0,-1)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    def model_matrix(self):
        # Identity matrix
        matrix_transform = glm.mat4(1.0)

        matrix_transform = glm.translate(matrix_transform, self.position)    
        
        matrix_transform = glm.rotate(matrix_transform, math.radians(self.angle), self.rotation)
        
        matrix_transform = glm.scale(matrix_transform, self.scale)
        
        return matrix_transform
    