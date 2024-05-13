from model import Model
from OpenGL.GL import *
import numpy as np

class ModelHelper():
    vertices_list = []    
    textures_coord_list = []
    uploaded_objects = {}

    @classmethod
    def render_model(cls, model_name, primitive):
        model = cls.uploaded_objects[model_name]
        for index, vertex_range in enumerate(model['vertex_range']):
            glBindTexture(GL_TEXTURE_2D, model['texture_id'][index])
            glDrawArrays(primitive, vertex_range[0], vertex_range[1] - vertex_range[0])

    @classmethod
    def attach_model(cls, model: Model):
        vertex_range = cls.__add_to_vertices_list(model.model, cls.vertices_list)
        cls.__add_to_texture_list(model.model, cls.textures_coord_list)
        obj = {'vertex_range': vertex_range, 'texture_id': model.texture_id}
        cls.uploaded_objects[model.name] = obj

    @classmethod
    def __add_to_vertices_list(cls, modelo, vertices_list):
        vertex_range = []
        material = modelo['faces'][0][2]

        init = len(vertices_list)
        for face in modelo['faces']:
            if material != face[2]:
                print("novo material")
                material = face[2]
                vertex_range.append((init, len(vertices_list)))
                init = len(vertices_list)

            for vertice_id in face[0]:
                vertices_list.append(modelo['vertices'][vertice_id-1])

        vertex_range.append((init, len(vertices_list)))
        print(f"Foram adicionados {len(vertices_list) - init} vértices, range: {vertex_range}")
        return vertex_range

    @classmethod
    def __add_to_texture_list(cls, modelo, textures_coord_list):
        for face in modelo['faces']:
            for texture_id in face[1]:
                textures_coord_list.append(modelo['texture'][texture_id-1])

    @classmethod
    def upload_models(cls, shader):
        # Request a buffer slot from GPU
        buffer = glGenBuffers(2)

        # Uploading vertices data
        vertices = np.zeros(len(cls.vertices_list), [("position", np.float32, 3)])
        vertices['position'] = cls.vertices_list
        glBindBuffer(GL_ARRAY_BUFFER, buffer[0])
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        stride = vertices.strides[0]
        offset = ctypes.c_void_p(0)
        loc_vertices = shader.getAttributeLocation("position")
        glEnableVertexAttribArray(loc_vertices)
        glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

        # Uploading texture data
        textures = np.zeros(len(cls.textures_coord_list), [("position", np.float32, 2)]) # duas coordenadas
        textures['position'] = cls.textures_coord_list
        glBindBuffer(GL_ARRAY_BUFFER, buffer[1])
        glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
        stride = textures.strides[0]
        offset = ctypes.c_void_p(0)
        loc_texture_coord = shader.getAttributeLocation("texture_coord")
        glEnableVertexAttribArray(loc_texture_coord)
        glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)