import os.path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import re


def get_mesh_size():
    #What: Lee los tamanos de la malla gruesa y fina en X, Y y Z
    #Why: El tamano de malla es util en el conteo de lineas
    #How: Utiliza REgex para encontrar cadenas en el texto
    
    with open("output.txt", "r") as output:
        lines = output.readlines()
        for line in lines:
            if line.find("Coarse_mesh_X_size:") != -1:
                coarse_x = np.array([int(s) for s in re.findall(r'\d+', line)])
            if line.find("Fine_mesh_X_size:") != -1:
                fine_x = np.array([int(s) for s in re.findall(r'\d+', line)])
            if line.find("Coarse_mesh_Y_size:") != -1:
                coarse_y = np.array([int(s) for s in re.findall(r'\d+', line)])
            if line.find("Fine_mesh_Y_size:") != -1:
                fine_y = np.array([int(s) for s in re.findall(r'\d+', line)])
            if line.find("Coarse_mesh_Z_size:") != -1:
                coarse_z = np.array([int(s) for s in re.findall(r'\d+', line)])
            if line.find("Fine_mesh_Z_size:") != -1:
                fine_z = np.array([int(s) for s in re.findall(r'\d+', line)])
    
    coarse = np.concatenate((coarse_x, coarse_y, coarse_z)).astype(int)
    fine = np.concatenate((fine_x, fine_y, fine_z)).astype(int)
    
    return coarse, fine

def get_number_of_segments():
    # What: Regresa el numero de segmentos en las mallas X, Y y Z
    # Why: Aumenta la legibilidad de algunas funciones
    # How: segmentos = puntos - 1. 
    
    coarse_size, fine_size = get_mesh_size()
    
    number_in_coarse = [coarse_size[0]-1, coarse_size[1]-1, coarse_size[2]]
    number_in_fine = [fine_size[0]-1, fine_size[1]-1, fine_size[2]-1]
    
    return number_in_coarse, number_in_fine

def get_number_of_axial_levels():
    return get_number_of_segments()[1][2]   

def print_clean_file():
    #What: Genera un documento que contiene unicamente los flujos.
    #Why: Leer los flujos es mas sencillo que leer todo.
    #How: Usando el tamano de la malla se eliminan lineas innecesarias.
    
    coarse_size, fine_size = get_mesh_size()
    lines_to_skip = np.sum([coarse_size, fine_size])+2*7+2
    lines_to_read = fine_size[0]*fine_size[2]-188
    
    begin = lines_to_skip
    end = lines_to_skip + lines_to_read -1

    with open("output.txt") as output:
        clean = output.readlines()[begin:end]
    
    with open("clean_file.txt", "w") as f:
        for line in clean:
            f.write(line)

def generate_matrix_of_axial_fluxes():
    # What: Genera una matriz usando los flujos del clean file
    # Why:  Primer paso para generar un arreglo de varillas 
    # How:  Elimina los saltos de linea (\n) con strip()
            # genera arreglos unidimensionales usando split()
            # adjunta los arreglos a la matriz usando append()
    
    matrix = []

    with open("clean_file.txt", "r") as file:
        for lines in file:
            lines = lines.strip().split()
            matrix.append(lines)

    return matrix

def get_pin_fluxes(pos_x, pos_y):
    number_of_levels = get_number_of_axial_levels()
    
    matrix_py = generate_matrix_of_axial_fluxes()
    pin_data = np.zeros(number_of_levels)

    x = pos_x
    y = pos_y

    pin = []
    for i in range(0, number_of_levels):
        pin.append(matrix_py[190*i-(i) + x][y-1])

    pin_data = np.array(pin).astype(float)
    return pin_data

def get_coarse_mesh():
    coarse_x = []
    coarse_y = []
    coarse_z = []

    with open("output.txt", "r") as output:
        contents = output.read()
        
        coarse_x = contents[contents.index("Coarse_mesh_X:"):contents.index("Fine_mesh_X_size:")]
        coarse_y = contents[contents.index("Coarse_mesh_Y:"):contents.index("Fine_mesh_Y_size:")]
        coarse_z = contents[contents.index("Coarse_mesh_Z:"):contents.index("Fine_mesh_Z_size:")]

    coarse_x = coarse_x.split()
    coarse_y = coarse_y.split()
    coarse_z = coarse_z.split()

    del coarse_x[0]
    del coarse_y[0]
    del coarse_z[0]

    coarse_x = np.array(coarse_x).astype(float)
    coarse_y = np.array(coarse_y).astype(float)
    coarse_z = np.array(coarse_z).astype(float)

    return coarse_x, coarse_y, coarse_z

def get_fine_mesh():
    fine_x = []
    fine_y = []
    fine_z = []

    with open("output.txt", "r") as output:
        contents = output.read()
        
        fine_x = contents[contents.index("Fine_mesh_X:"):contents.index("Coarse_mesh_Y_size:")]
        fine_y = contents[contents.index("Fine_mesh_Y:"):contents.index("Coarse_mesh_Z_size:")]
        fine_z = contents[contents.index("Fine_mesh_Z:"):contents.index("Fine_Scalar_Flux:")]

    fine_x = fine_x.split()
    fine_y = fine_y.split()
    fine_z = fine_z.split()

    del fine_x[0]
    del fine_y[0]
    del fine_z[0]

    fine_x = np.array(fine_x).astype(float)
    fine_y = np.array(fine_y).astype(float)
    fine_z = np.array(fine_z).astype(float)

    return fine_x, fine_y, fine_z

class pin:
    def __init__(self, pos_x, pos_y):
        self.x = int(pos_x)
        self.y = int(pos_y)
        self.coarse_mesh = get_coarse_mesh()[2]
        self.fine_mesh = get_fine_mesh()[2]
        self.fluxes = get_pin_fluxes(pos_x, pos_y)
        self.levels = get_number_of_axial_levels()
    
def plot_pin(pos_x, pos_y):
    bar = pin(pos_x, pos_y)
       
    title = "Bar: (" + str(bar.x) + ", " + str(bar.y) + ")"
    title += "  Assembly: (" + str(int(bar.x/11)) + ", " + str(int(bar.y/11))  + ")"
    plt.title(title)

    x = bar.fine_mesh[1:]
    y = bar.fluxes 
    plt.plot(x, y)

    plt.xlabel("Z (cm)")
    plt.ylabel("Normalized axial Flux (neutrons/$cm^2$*s)")

    y_top = np.amax(y) + np.amax(y)*0.15
    plt.axis([0, 288, 0, y_top])

    plt.xticks(np.arange(0, 300, 20))

    plt.grid(True)    
    plt.show()

def get_level_flux(level):
    k = level
    flux = []
    with open("clean_file.txt", "r") as file:
        for lines in file.readlines()[189*k-188:189*k-1]:
                lines = lines.split()
                flux.append(lines)
    flux = np.array(flux).astype(float)
    return flux

def plot_level(level):
    #TO DO : Reescribir usando plotly 
    fig = plt.figure(figsize=(8,8), dpi=80)
    ax = plt.axes(projection='3d')

    # Make data.
    x = np.linspace(0, 188, 188)
    y = np.linspace(0, 187, 187)
    x, y = np.meshgrid(x, y)
    z = get_level_flux(level)


    surf = ax.plot_surface(x, y, z, linewidth=0, cmap=cm.gnuplot, antialiased=False, rcount=300, ccount=300)

    # # # # Customize the z axis.
    ax.set_zlim(0,1.5e-5)
    # ax.zaxis.set_major_locator(LinearLocator(10))
    # # # # A StrMethodFormatter is used automatically
    # # ax.zaxis.set_major_formatter('{x:.0002f}')

    # # # # Add a color bar which maps values to colors.
    title = "Normalized axial flux (neutrons/$cm^2$*s) at level: " + str(level)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.xlabel("X (cm)")
    plt.ylabel("Y (cm)")
    # plt.set_zlabel("Normalized axial flux neutrons/$cm^2$*s")
    plt.title(title)
    plt.show()


def hottest_pin():
    bigger = np.sum(get_pin_fluxes(1,1))
    pos = [1, 1]
    for i in range(1, 95):
        for j in range(1, 95):
            flux = np.sum(get_pin_fluxes(i,j))
            print(i, j)
            if (flux > bigger):
                bigger = flux
                pos = [i, j]
    print(pos)


def main():
    if os.path.isfile("clean_file.txt") == False:
        print_clean_file()

if __name__ == "__main__":
    main()
