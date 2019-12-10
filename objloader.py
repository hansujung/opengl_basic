import numpy as np
from PIL import Image

import OpenGL.GL as gl

def MTL(filename):
    contents = {}
    mtl = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
            # print(values[1])
        elif mtl is None:
            raise ValueError("mtl file doesn't start with newmtl stmt")
        elif values[0] == 'map_Kd' or values[0] == 'map_Ka':
            mtl[values[0]] = values[1]
            image = Image.open(mtl[values[0]])
            img_data = np.array(list(image.getdata()), np.int8)
            texid = mtl['texture_Kd'] = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texid)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, 3, image.size[0], image.size[1], 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
            # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
            # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL)
        else:
            mtl[values[0]] = list(map(float, values[1:]))
    return contents

class OBJ:

    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        material = None
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = MTL(values[1])
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))

        # zero to means
        # print(np.mean(self.vertices, axis=0, keepdims=True))
        self.vertices -= np.mean(self.vertices, axis=0, keepdims=True)

        self.gl_list = gl.glGenLists(1)
        gl.glNewList(self.gl_list, gl.GL_COMPILE)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glFrontFace(gl.GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face
            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                gl.glEnable(gl.GL_TEXTURE_2D)
                gl.glEnable(gl.GL_LIGHT0)
                gl.glEnable(gl.GL_LIGHTING)
                gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, *mtl['Ks'])
                gl.glBindTexture(gl.GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                # 재질 불러오기
                gl.glDisable(gl.GL_TEXTURE_2D)
                gl.glLightModelfv(gl.GL_LIGHT_MODEL_LOCAL_VIEWER, 0.0)
                gl.glFrontFace(gl.GL_CW)
                gl.glEnable(gl.GL_BLEND)
                gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
                gl.glColor(*mtl['Kd'], *mtl['d'])
                gl.glEnable(gl.GL_LIGHT0)
                gl.glEnable(gl.GL_LIGHTING)
                gl.glEnable(gl.GL_COLOR_MATERIAL)
                gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, *mtl['Ks'])
            gl.glBegin(gl.GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    gl.glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    gl.glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                gl.glVertex3fv(self.vertices[vertices[i] - 1])
            gl.glEnd()
        gl.glDisable(gl.GL_TEXTURE_2D)

        gl.glEndList()
