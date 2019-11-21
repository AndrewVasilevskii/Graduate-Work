from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class Canvas(FigureCanvas):
    def __init__(self, panel, par, figure):
        super().__init__(panel, par, figure)
        self.figure = figure
        self.axis = Axes3D(self.figure)
        self.axis.set_xlabel('x')
        self.axis.set_ylabel('y')
        self.axis.set_zlabel('z')
        self.axis.set_facecolor(color='#d2d2d2')

    def Remove_canvas(self):
        self.axis.clear()
        self.draw()

    def Draw_canvas(self, x, y, vector, n_dimension, m_dimension, color, quarterCount):
        vector1 = np.reshape(vector, (n_dimension, m_dimension)).transpose()
        vector1 = abs(vector1)
        if quarterCount == 4:
            arr1 = np.append(vector1, vector1)
            arr2 = np.append(vector1, vector1)
            arrr = np.append(arr1, arr2)
            arrr = np.reshape(arrr,(4 * n_dimension, m_dimension))
            # x_quarter = x[:][i*m_dimension:(i+1)*m_dimension]
            # y_quarter = y[:][i*m_dimension:(i+1)*m_dimension]
            self.axis.plot_wireframe(x, y, arrr, color=color,)
            self.draw()
        else:
            x_quarter = x[:][0:m_dimension]
            y_quarter = y[:][0:m_dimension]
            self.axis.plot_wireframe(x_quarter, y_quarter, vector1, color=color, )
            self.draw()
        self.axis.set_xlabel('x')
        self.axis.set_ylabel('y')
        self.axis.set_zlabel('\u03C8')

class ResultCanvas(FigureCanvas):
    def __init__(self, panel, par, figure):
        super().__init__(panel, par, figure)
        self.enableLegend = True
        self.figure = figure
        self.axis = figure.add_axes([0.1,0.1,0.8,0.8])

        # self.axis = figure.add_subplot(111)
        self.axis.set_facecolor(color='#e1e1e1')

    def Draw_Result(self, List, graph, eigenvalue='First order', dimensionCoeff=None):
        if eigenvalue == 'First order':
            eigenvalue = 'Energy_0 (Ry*)'
        elif eigenvalue == 'Second order':
            eigenvalue = 'Energy_1 (Ry*)'
        else:
            eigenvalue = 'Energy_2 (Ry*)'
        if graph == 'radius':
            # self.axis.set_ylabel('Energy (Ry*)')
            # self.axis.set_xlabel('Dot Radius(a*)')
            # for energy in List:
                # print(energy)
                # if energy == 'First order' :
                #     label = 'Energy_0'
                # elif energy == 'Second order':
                #     label = 'Energy_1'
                # else:
                #     label = 'Energy_2'
                # values = np.zeros(7)
                # for item in range(1, 8):
                #     values[item-1] = List[energy][item]
                # self.axis.plot(range(1,8), values, label = label )
                # self.figure.legends.clear()
                # self.figure.legend(loc='center right')
                # self.draw()

            self.axis.set_ylabel(eigenvalue)
            self.axis.set_xlabel('Dot Radius(a*)')
            for gamma in List:
                values = np.zeros(10)
                for item in range(1, 11):
                    values[item-1] = List[gamma][item]
                # self.axis.set_ylim(0,12)
                self.axis.plot(range(1,11), values, label = 'Gamma = %s' % gamma)
                self.figure.legends.clear()
                self.figure.legend(loc='center right')
                self.draw()
        if graph == 'gamma':
            print(List)
            self.axis.set_ylabel('Energy (Ry*)')
            self.axis.set_xlabel('Gamma')
            for m in List:
                for energy in List[m]:
                    if energy == 'First order' :
                        label = 'Energy_0, m = %s' % m
                    elif energy == 'Second order':
                        label = 'Energy_1, m = %s' % m
                    else:
                        label = 'Energy_2, m = %s' % m
                    values = np.zeros(6)
                    for item in range(6):
                        values[item] = List[m][energy][item]
                    self.axis.plot(range(6), values, label=label)
                    self.figure.legends.clear()
                    self.figure.legend()
                    self.draw()
            # self.axis.set_ylabel(eigenvalue)
            # self.axis.set_xlabel('Gamma')
            # for radius in List:
            #     values = np.zeros(11)
            #     for item in range(0, 11):
            #         values[item] = List[radius][item]
            #     self.axis.plot(range(0, 11), values, label='Radius = %s' % radius)
            #     self.figure.legends.clear()
            #     self.figure.legend(loc='center right')
            #     self.draw()
        if graph == 'method':
            print(List)
            self.axis.set_ylabel(eigenvalue)
            self.axis.set_xlabel(dimensionCoeff)
            for method in List:
                if method == 1 :
                    label = 'Main Method'
                else:
                    label = 'Alternative Method'
                values = np.zeros(13)
                for item in range(2, 15):
                    values[item - 2] = List[method][item]
                import numpy
                dimens = numpy.array(range(10,75,5))
                if dimensionCoeff == '1/N':
                    dimens = 1/dimens
                elif dimensionCoeff == 'N':
                    pass
                else:
                    dimens = 1/dimens**2

                # print(numpy.arange(5,75,5))
                # print(values)
                # with open('111.txt', 'w') as file:
                #     file.write(str(numpy.arange(5,75,5)))
                #     file.write(str(values))
                print(dimens)
                print(values)
                self.axis.plot(dimens, values, label=label)
                self.figure.legends.clear()
                self.figure.legend(loc='center right')
                self.draw()

    def Remove_Result(self):
        self.axis.clear()
        self.figure.legends.clear()
        self.draw()
