import random
import numpy as np
from OpenGL.GL import *

class Geometry:
    """Basic class to hold geometric data attributes."""
    def __init__(self):
        self._attributes = {}
        self._vertex_count = 0

    def add_attribute(self, attribute_type, attribute_name, data):
        """Adds a list of data (e.g., vertices, colors) as an attribute."""
        # Basic type checking and storage
        if not isinstance(data, list):
            print(f"Warning: Data for attribute '{attribute_name}' is not a list.")
            return
        
        # Convert list of lists to numpy array for easier handling later
        self._attributes[attribute_name] = np.array(data, dtype='float32')

    def get_attribute(self, attribute_name):
        """Retrieves data for a given attribute name."""
        return self._attributes.get(attribute_name)
        
    def count_vertices(self):
        """Sets the vertex count based on the size of the first attribute added."""
        if self._attributes:
            # Assumes all attributes have the same number of elements
            first_attr_name = list(self._attributes.keys())[0]
            self._vertex_count = len(self._attributes[first_attr_name])
        else:
            self._vertex_count = 0

    def vertex_count(self):
        """Returns the number of vertices in the geometry."""
        return self._vertex_count


class ObjReader(Geometry):
    """Subclass of Geometry for loading OBJ files and applying colors per face."""
    
    def __init__(self, filename):
        super().__init__()  # Initialize the Geometry base class
        self.load_from_obj(filename)  # Load data from the OBJ file upon instantiation

    def load_from_obj(self, filename):
        """Reads vertices and UVs from an OBJ file, duplicates vertices per face for unique coloring."""
        original_vertices = []
        original_normals = []
        original_uvs = []  # Coordenadas de textura originais
        face_vertices = []  # Para armazenar vértices duplicados por face
        face_normals = []   # Normais duplicadas por face
        face_uvs = []       # UVs duplicados por face
        
        try:
            print(f"Carregando modelo OBJ: {filename}")
            with open(filename, 'r') as obj_file:
                for line in obj_file:
                    if line.startswith('v '):  # Posição do vértice
                        original_vertices.append([float(value) for value in line.strip().split()[1:]])
                    elif line.startswith('vt '):  # Coordenada de textura
                        # Extrai as coordenadas de textura (pode ter 2 ou 3 componentes)
                        values = [float(value) for value in line.strip().split()[1:]]
                        if len(values) >= 2:
                            original_uvs.append(values[:2])  # Pega apenas as duas primeiras componentes (U, V)
                    elif line.startswith('vn '):  # Normal do vértice
                        original_normals.append([float(value) for value in line.strip().split()[1:]])
                    elif line.startswith('f '):  # Face
                        # OBJ indices are 1-based, adjust to 0-based
                        parts = line.strip().split()[1:]
                        v_indices = []
                        vt_indices = []
                        vn_indices = []
                        
                        for part in parts:
                            # Handle different face formats (v, v/vt, v/vt/vn, v//vn)
                            elements = part.split('/')
                            
                            # Vertex index (sempre presente)
                            v_idx = int(elements[0]) - 1
                            v_indices.append(v_idx)
                            
                            # Texture coordinate index (pode estar ausente)
                            if len(elements) > 1 and elements[1]:
                                vt_idx = int(elements[1]) - 1
                                vt_indices.append(vt_idx)
                            else:
                                vt_indices.append(-1)  # Marca como ausente
                                
                            # Normal index (pode estar ausente)
                            if len(elements) > 2 and elements[2]:
                                vn_idx = int(elements[2]) - 1
                                vn_indices.append(vn_idx)
                            else:
                                vn_indices.append(-1)  # Marca como ausente
                            
                        # Assume faces are triangles or quads
                        if len(v_indices) == 3: # Triangle
                            for i in range(3):
                                face_vertices.append(original_vertices[v_indices[i]])
                                
                                # Adiciona UV se disponível
                                if vt_indices[i] != -1 and vt_indices[i] < len(original_uvs):
                                    face_uvs.append(original_uvs[vt_indices[i]])
                                else:
                                    face_uvs.append([0.0, 0.0])  # UV padrão
                                    
                                # Adiciona normal se disponível
                                if vn_indices[i] != -1 and vn_indices[i] < len(original_normals):
                                    face_normals.append(original_normals[vn_indices[i]])
                                    
                        elif len(v_indices) == 4: # Quad, convert to two triangles
                            # Triangle 1: v_indices[0], v_indices[1], v_indices[2]
                            for i in [0, 1, 2]:
                                face_vertices.append(original_vertices[v_indices[i]])
                                
                                # Adiciona UV se disponível
                                if vt_indices[i] != -1 and vt_indices[i] < len(original_uvs):
                                    face_uvs.append(original_uvs[vt_indices[i]])
                                else:
                                    face_uvs.append([0.0, 0.0])  # UV padrão
                                    
                                # Adiciona normal se disponível
                                if vn_indices[i] != -1 and vn_indices[i] < len(original_normals):
                                    face_normals.append(original_normals[vn_indices[i]])
                                    
                            # Triangle 2: v_indices[0], v_indices[2], v_indices[3]
                            for i in [0, 2, 3]:
                                face_vertices.append(original_vertices[v_indices[i]])
                                
                                # Adiciona UV se disponível
                                if vt_indices[i] != -1 and vt_indices[i] < len(original_uvs):
                                    face_uvs.append(original_uvs[vt_indices[i]])
                                else:
                                    face_uvs.append([0.0, 0.0])  # UV padrão
                                    
                                # Adiciona normal se disponível
                                if vn_indices[i] != -1 and vn_indices[i] < len(original_normals):
                                    face_normals.append(original_normals[vn_indices[i]])

            print(f"Modelo carregado: {len(original_vertices)} vértices, {len(original_uvs)} UVs, {len(original_normals)} normais")
            print(f"Faces processadas: {len(face_vertices)} vértices, {len(face_uvs)} UVs, {len(face_normals)} normais")

        except FileNotFoundError:
            print(f"Erro: Arquivo OBJ não encontrado em {filename}")
            return
        except Exception as e:
            print(f"Erro ao carregar arquivo OBJ {filename}: {e}")
            import traceback
            traceback.print_exc()
            return

        # Now we have duplicated vertices per face, with each set of face vertices having a unique color
        if face_vertices:
            self.add_attribute("vec3", "vertexPosition", face_vertices)
            
            if face_uvs and len(face_uvs) == len(face_vertices): # Only add UVs if we have a valid amount
                self.add_attribute("vec2", "vertexUV", face_uvs)
                print(f"Coordenadas de textura adicionadas ao modelo ({len(face_uvs)} UVs)")
            else:
                print(f"Aviso: Coordenadas de textura não adicionadas. UVs: {len(face_uvs)}, Vértices: {len(face_vertices)}")
                
            if face_normals and len(face_normals) == len(face_vertices): # Only add normals if we have a valid amount
                self.add_attribute("vec3", "vertexNormal", face_normals)

            self.count_vertices()  # Update the vertex count based on duplicated vertices
            print(f"Modelo processado com {self.vertex_count()} vértices")
        else:
            print(f"Aviso: Nenhum vértice ou face válida encontrada em {filename}")

def draw_obj_model(obj_geometry):
    """Draws a loaded OBJ model using vertex attributes."""
    vertices = obj_geometry.get_attribute("vertexPosition")
    uv_coords = obj_geometry.get_attribute("vertexUV") # Coordenadas de textura
    
    if vertices is None:
        print("Erro: Dados de vértice ausentes para desenhar o modelo OBJ.")
        return
        
    glEnableClientState(GL_VERTEX_ARRAY)
    
    # Habilita array de coordenadas de textura se disponível
    if uv_coords is not None and len(uv_coords) > 0:
        # Garantir que as coordenadas UV estejam corretamente configuradas
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, 0, uv_coords)
    else:
        # Se não houver coordenadas de textura, desabilita
        glDisable(GL_TEXTURE_2D)
        print("Aviso: Modelo não possui coordenadas de textura!")

    glVertexPointer(3, GL_FLOAT, 0, vertices)

    # Desenha os triângulos
    glDrawArrays(GL_TRIANGLES, 0, obj_geometry.vertex_count())

    # Desabilita arrays
    if uv_coords is not None and len(uv_coords) > 0:
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    
    glDisableClientState(GL_VERTEX_ARRAY)
