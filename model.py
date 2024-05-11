from OpenGL.GL import *
from PIL import Image

def load_model_from_file(filename):
    """Loads a Wavefront OBJ file. """
    objects = {}
    vertices = []
    texture_coords = []
    faces = []

    material = None

    # abre o arquivo obj para leitura
    for line in open(filename, "r"): ## para cada linha do arquivo .obj
        if line.startswith('#'): continue ## ignora comentarios
        values = line.split() # quebra a linha por espaço
        if not values: continue


        ### recuperando vertices
        if values[0] == 'v':
            vertices.append(values[1:4])


        ### recuperando coordenadas de textura
        elif values[0] == 'vt':
            texture_coords.append(values[1:3])

        ### recuperando faces 
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
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

def load_texture_from_file(texture_id, img_textura):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    img = Image.open(img_textura)
    print(img_textura,img.mode)
    img_width = img.size[0]
    img_height = img.size[1]
    #image_data = img.tobytes("raw", "RGB", 0, -1)
    image_data = img.convert("RGBA").tobytes("raw", "RGBA",0,-1)

    #image_data = np.array(list(img.getdata()), np.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

def add_to_vertices_list(modelo, vertices_list):
    init = len(vertices_list)
    for face in modelo['faces']:
        for vertice_id in face[0]:
            vertices_list.append(modelo['vertices'][vertice_id-1])
    print(f"Foram adicionados {len(vertices_list) - init} vértices ({init}, {len(vertices_list)})")
    return (init, len(vertices_list))

def add_to_texture_list(modelo, textures_coord_list):
    for face in modelo['faces']:
        for texture_id in face[1]:
            textures_coord_list.append(modelo['texture'][texture_id-1])

def load_model_helper(model_path, texture_path, uploaded_objects, vertices_list, textures_coord_list, texture_id):
    modelo = load_model_from_file(model_path)
    vertice_range = add_to_vertices_list(modelo, vertices_list)
    add_to_texture_list(modelo, textures_coord_list)
    load_texture_from_file(texture_id, texture_path)
    obj = {'model': model_path, 'vertice_range': vertice_range, 'texture_id': texture_id}
    uploaded_objects.append(obj)
    
    return texture_id+1