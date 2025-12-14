#draw_vertices()

# Pyxel Studio

import pyxel
import time
import math

angulo_x = 0
angulo_y = 0
angulo_z = 0
width = 256
height = 256
distancia_camara = 2

wx, wy, wz = 0.020, 0.015, 0.010
paused = False

colors = [(int(255*(i/14)), int(215*(i/14)), 0) for i in range(15)] 

def convert_hex(l):
    r, g, b = l
    return int((f"0x{r:02X}{g:02X}{b:02X}"),16)
    
colors_hex = [convert_hex(col) for col in colors] + [0x000000]
print(colors_hex)



vertices_cubo = [
    [-0.5, -0.5, -0.5],  # vértice 0
    [ 0.5, -0.5, -0.5],  # vértice 1
    [ 0.5,  0.5, -0.5],  # vértice 2
    [-0.5,  0.5, -0.5],  # vértice 3
    [-0.5, -0.5,  0.5],  # vértice 4
    [ 0.5, -0.5,  0.5],  # vértice 5
    [ 0.5,  0.5,  0.5],  # vértice 6
    [-0.5,  0.5,  0.5]   # vértice 7
]

faces = [

    (0,3,2,1),  # z = -0.5  <-- ahora la normal es -Z (hacia afuera)
    (4,5,6,7),
    (0,1,5,4),
    (1,2,6,5),
    (2,3,7,6),
    (3,0,4,7),

]

shade_ramp = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]    

faces_colors = [2,4,7,10,3,6]

pares_aristas = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (3,7),(2,6),(1,5),(0,4)
    ]
    
def triangulate_face(f):
    orig = f[0]
    return (orig, f[1], f[2]) , (orig, f[2], f[3])#(dos triangulos)

def proyectar_perspectiva(vertices):
    global distancia_camara
    proyectados = []
    for vertice in vertices:
        x, y, z = vertice
        z += distancia_camara  # para evitar la división por cero
        x_p = distancia_camara * x / z
        y_p = distancia_camara * y / z
        proyectados.append((x_p, y_p))
    
    return proyectados

pyxel.init(width, height)

vertices_cubo_proyec = proyectar_perspectiva(vertices_cubo)


def mat3_vec(m, v):
    x, y, z = v
    return [
        m[0][0]*x + m[0][1]*y + m[0][2]*z,
        m[1][0]*x + m[1][1]*y + m[1][2]*z,
        m[2][0]*x + m[2][1]*y + m[2][2]*z,
    ]

def mat3_mul(a, b):
    return [
        [
            a[i][0]*b[0][j] + a[i][1]*b[1][j] + a[i][2]*b[2][j]
            for j in range(3)
        ] for i in range(3)
    ]

def rotmx(ax):
    c, s = math.cos(ax), math.sin(ax)
    return [
        [1, 0, 0],
        [0, c, -s],
        [0, s,  c],
    ]

def rotmy(ay):
    c, s = math.cos(ay), math.sin(ay)
    return [
        [ c, 0, s],
        [ 0, 1, 0],
        [-s, 0, c],
    ]

def rotmz(az):
    c, s = math.cos(az), math.sin(az)
    return [
        [ c, -s, 0],
        [ s,  c, 0],
        [ 0,  0, 1],
    ]

def rotation_matrix_xyz(ax, ay, az):
    Rx = rotmx(ax)
    Ry = rotmy(ay)
    Rz = rotmz(az)
    return mat3_mul(Rz, mat3_mul(Ry, Rx))

def avg_z(face):
    return sum(vertices_rotados[i][2] for i in face) / 4.0

def draw_aristas():
    global pares_aristas
    
    for par in pares_aristas:
        x,y= par
        pyxel.line(vertices_cubo_proyec[x][0] * (width/2) + (width/2), vertices_cubo_proyec[x][1] * (width/2) + (width/2),vertices_cubo_proyec[y][0] * (width/2) + (width/2),vertices_cubo_proyec[y][1] * (width/2) + (width/2),14)
    
def draw_vertices():
    global width
    for verts in vertices_cubo_proyec:
        x,y = verts
        pyxel.rect(x * (width/2) + (width/2) , y * (width/2)  + (width/2) , 2, 2, 7)
        
def normalize(v):
    x, y, z = v
    l = (x*x + y*y + z*z) ** 0.5
    return (x/l, y/l, z/l) if l > 0 else (0.0, 0.0, 0.0)

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def face_normal_unit(face):
    i0, i1, i2, _ = face
    v0 = vertices_rotados[i0]
    v1 = vertices_rotados[i1]
    v2 = vertices_rotados[i2]
    e1 = (v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2])
    e2 = (v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2])
    # e1 × e2
    nx = e1[1]*e2[2] - e1[2]*e2[1]
    ny = e1[2]*e2[0] - e1[0]*e2[2]
    nz = e1[0]*e2[1] - e1[1]*e2[0]
    return normalize((nx, ny, nz))        
    
def draw_faces():
    order = sorted(range(len(faces)), key=lambda i: avg_z(faces[i]), reverse=True)
    for idx in order:
        tri1, tri2 = triangulate_face(faces[idx])
        n = face_normal_unit(faces[idx])          # normal unitaria de la cara (en 3D rotado)
        lambert = max(0.0, (dot(n, light_dir) + 1)/2)     # [0,1]
        lvl = min(len(shade_ramp)-1,
                  int(lambert * (len(shade_ramp)-1) + 0.5))  # cuantiza a niveles
        c = shade_ramp[lvl]  
        
    
        pyxel.tri(vertices_cubo_proyec[tri1[0]][0] * (width/2) + (width/2),vertices_cubo_proyec[tri1[0]][1] * (width/2) + (width/2),vertices_cubo_proyec[tri1[1]][0] * (width/2) + (width/2),vertices_cubo_proyec[tri1[1]][1] * (width/2) + (width/2),vertices_cubo_proyec[tri1[2]][0] * (width/2) + (width/2),vertices_cubo_proyec[tri1[2]][1] * (width/2) + (width/2),c)
        pyxel.tri(vertices_cubo_proyec[tri2[0]][0] * (width/2) + (width/2),vertices_cubo_proyec[tri2[0]][1] * (width/2) + (width/2),vertices_cubo_proyec[tri2[1]][0] * (width/2) + (width/2),vertices_cubo_proyec[tri2[1]][1] * (width/2) + (width/2),vertices_cubo_proyec[tri2[2]][0] * (width/2) + (width/2),vertices_cubo_proyec[tri2[2]][1] * (width/2) + (width/2),c)



light_dir = normalize((0.5, -1.0, -0.75))

R = rotation_matrix_xyz(angulo_x, angulo_y, angulo_z)
vertices_rotados = [mat3_vec(R, v) for v in vertices_cubo]

def update():
    """
    lensvert = 0.5    
    t = time.time()
    
    for vert in vertices_cubo:
        vert[0], vert[2] =  
    
    
    """
    global angulo_x, angulo_y, angulo_z, vertices_cubo_proyec, distancia_camara, wx, wy, wz, paused,vertices_rotados
    
    
        
    if pyxel.btnp(pyxel.KEY_R):
        angulo_x = angulo_y = angulo_z = 0.0
        wx, wy, wz = 0, 0, 0
        distancia_camara = 2.0
        
    if pyxel.btn(pyxel.KEY_Q): wx += 0.001
    if pyxel.btn(pyxel.KEY_A): wx -= 0.001

    if pyxel.btn(pyxel.KEY_W): wy += 0.001           
    if pyxel.btn(pyxel.KEY_S): wy -= 0.001

    if pyxel.btn(pyxel.KEY_E): wz += 0.001
    if pyxel.btn(pyxel.KEY_D): wz -= 0.001
    
    if pyxel.btn(pyxel.KEY_Z): distancia_camara = max(1.0, distancia_camara - 0.02)  #esto es acercar
    if pyxel.btn(pyxel.KEY_X): distancia_camara = min(10.0, distancia_camara + 0.02)  #esto es alejar
    
    angulo_x = (angulo_x + wx) % (2 * math.pi)
    angulo_y = (angulo_y + wy) % (2 * math.pi)
    angulo_z = (angulo_z + wz) % (2 * math.pi)
    
    R = rotation_matrix_xyz(angulo_x, angulo_y, angulo_z)
    vertices_rotados = [mat3_vec(R, v) for v in vertices_cubo]
    vertices_cubo_proyec = proyectar_perspectiva(vertices_rotados)
    


def draw():
    pyxel.cls(15)
    draw_faces()
    if pyxel.btn(pyxel.KEY_SPACE):
        draw_aristas()
    #draw_vertices()
    
for i in range(len(colors_hex)):
    pyxel.colors[i] = colors_hex[i]    
pyxel.run(update, draw)