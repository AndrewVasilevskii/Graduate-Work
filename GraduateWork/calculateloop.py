import os
import time
import logging
import numpy as np
from numpy import cos, tan, sin
from scipy.sparse import csr_matrix, linalg
import warnings

from wx.lib.pubsub import pub

def bubble_sort(val, vector):
    index = val.size - 1
    while index >= 0:
        for j in range(index):
            if val[j] > val[j+1]:
                val[j], val[j+1] = val[j+1], val[j]
                for i in range(int(vector.size/val.size)):
                    vector[i, j], vector[i, j+1] = vector[i, j+1], vector[i, j]
        index -= 1
    return val, vector


def index_transform(i, j, m_dimension):
    return (i - 2)*m_dimension + j - 2


def V_ij(i, j, mass, gamma, h, k, potential):
    if 'True' in str(potential):
        return mass*gamma + mass**2/((r_i(i, h))**2*(sin(o_j(j, k)))**2) + gamma**2*(r_i(i,h))**2*(sin(o_j(j,k)))**2/4 - 2/r_i(i,h)
    else:
        return 0


def r_i(i,h):
    return (i-1)*h


def o_j(j, k):
    return (j-1)*k


def cotang(item):
    return 1/tan(item)
#return 0

def cart2pol(x, y):
    rho, theta = np.meshgrid(x, y)
    x = rho*cos(theta)
    y = rho*sin(theta)
    return x, y

# in %(module)s module  in %(funcName)s function'', on %(lineno)d line
def Calculate_loop(method, mass, radius, n_dimension, m_dimension, gamma, potential, sigma, start_time):
    # computer_name = os.environ['COMPUTERNAME']
    # start_time = time.time()
    # logging.basicConfig(filename='log_%s.log' % computer_name, format='%(asctime)s.%(msecs)03d : %(message)s', datefmt="%H:%M:%S", level=logging.INFO)
    # logging.info('Dimension: ' + '(' + str(n_dimension) + ', ' + str(m_dimension) + ')' + '\nMass : ' + str(mass) +
    #              '||Radius : ' + str(radius) + '||Gamma : ' + str(gamma) + '\nPotential : ' + str(potential))
    # logging.info('Start')
    mass = float(mass)
    R = float(radius)
    gamma = float(gamma)
    N = n_dimension
    M = m_dimension

    print('method = %s, mass = %s, radius = %s, N = %s, M = %s, gamma = %s, potential = %s, sigma = %s' % (method, mass, R, N, M, gamma, potential, sigma))
    h = R / (N + 1.)
    k = np.pi / (2 *(M + 1.))
    # logging.info('Creating matrix')
    b = csr_matrix((N*M, N*M))
    # logging.info('Created csr matrix')
    # logging.info('Matrix filling in ')
    if method == 'Main method':
        if not int(mass) == 0:
            print('main not 0')
            if sigma == 'Positive':
                main_method_nonzero_MQN_PosSigma(b, mass, N, M, h, k, gamma, potential)
            else:
                main_method_nonzero_MQN_NegSigma(b, mass, N, M, h, k, gamma, potential)
        else:
            print('main 0')
            main_method_zero_MQN_PosSigma(b, mass, N, M, h, k, gamma, potential)
    else:
        if not int(mass) == 0:
            print ('alternative not 0')
            if sigma == 'Positive':
                alternative_method_nonzero_MQN_PosSigma(b, mass, N, M, h, k, gamma, potential)
            else:
                alternative_method_nonzero_MQN_NegSigma(b, mass, N, M, h, k, gamma, potential)
        else:
            print('alternative 0')
            alternative_method_zero_MQN_PosSigma(b, mass, N, M, h, k, gamma, potential)

    # logging.info('Finding eigen values\\vectors')
    val, vector = linalg.eigs(b, k=3, which='SR')
    # logging.info('Sorting')
    val, vector = bubble_sort(val.real, vector.real)
    sendingMessage(val=np.ndarray.tolist(val), vector=np.ndarray.tolist(vector.transpose()),  time=start_time)
    # logging.info('END in %.3f.\n' % (time.time() - start_time))

def sendingMessage(val, vector, time):
    pub.sendMessage('calculatedTransfer', val=val, vector=vector, time=time)

def main_method_nonzero_MQN_NegSigma(b, mass, N, M, h, k, gamma, potential):
    for i in range(2, N + 2):
        for j in range(2, M + 2):
            index = index_transform(i, j, M)
            if i != 2 and i != N + 1 and j != 2 and j != M + 1:
            # 2 < i < N + 1, 2 < j < M+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif j == 2 and i != 2 and i != N + 1:
            # j = 2, 2 < i < N+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif j == M + 1 and i != 2 and i != N + 1:
            # j = M+1, 2 < i < N+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == 2 and j != 2 and j != M + 1:
            # i = 2, 2 < j < M+1
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == N + 1 and j != 2 and j != M + 1:
            # i = N+1, 2 < j < M+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
            elif i == 2 and j == 2:
            # i = 2, j = 2
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == 2 and j == M + 1:
            # i = 2, j = M+1
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == N + 1 and j == 2:
            # i = N + 1, j = 2
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
            elif i == N + 1 and j == M + 1:
            # i = N + 1, j = M + 1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)

def main_method_zero_MQN_PosSigma(b, mass, N, M, h, k, gamma, potential):
    for i in range(2, N + 2):
        for j in range(2, M + 2):
            index = index_transform(i, j, N)
            if i != 2 and i != N + 1 and j != 2 and j != M + 1:
            # 2 < i < N + 1, 2 < j < M+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif j == 2 and i != 2 and i != N + 1:
            # j = 2, 2 < i < N+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) - 4 / (3*k ** 2 * (r_i(i, h)) ** 2) + (4*cotang(o_j(j, k))) / (3*2 * k * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2) + 1 / (3*k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (3*2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif j == M + 1 and i != 2 and i != N + 1:
            # j = M+1, 2 < i < N+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2) + 1 / (3*k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (3*2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) - 4 / (3*k ** 2 * (r_i(i, h)) ** 2) - (4*cotang(o_j(j, k))) / (2*3 * k * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == 2 and j != 2 and j != M + 1:
            # i = 2, 2 < j < M+1
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == N + 1 and j != 2 and j != M + 1:
            # i = N+1, 2 < j < M+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
            elif i == 2 and j == 2:
            # i = 2, j = 2
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) - 4 / (3*k ** 2 * (r_i(i, h)) ** 2) + (4*cotang(o_j(j, k))) / (3*2 * k * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2) + 1 / (3*k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (3*2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == 2 and j == M + 1:
            # i = 2, j = M+1
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2) + 1 / (3*k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (3*2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) - 4 / (3*k ** 2 * (r_i(i, h)) ** 2) - (4*cotang(o_j(j, k))) / (3*2 * k * (r_i(i, h)) ** 2)+ V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == N + 1 and j == 2:
            # i = N + 1, j = 2
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) - 4 / (3*k ** 2 * (r_i(i, h)) ** 2) + (4*cotang(o_j(j, k))) / (3*2 * k * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h))) ** 2 + 1 / (3*k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (3*2 * k * (r_i(i, h)) ** 2)
            elif i == N + 1 and j == M + 1:
            # i = N + 1, j = M + 1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2) + 1 / (3*k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (3*2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) - 4 / (3*k ** 2 * (r_i(i, h)) ** 2) - (4*cotang(o_j(j, k))) / (3*2 * k * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)

def main_method_nonzero_MQN_PosSigma(b, mass, N, M, h, k, gamma, potential):
    for i in range(2, N + 2):
        for j in range(2, M + 2):
            index = index_transform(i, j, N)
            if i != 2 and i != N + 1 and j != 2 and j != M + 1:
            # 2 < i < N + 1, 2 < j < M+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif j == 2 and i != 2 and i != N + 1:
            # j = 2, 2 < i < N+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif j == M + 1 and i != 2 and i != N + 1:
            # j = M+1, 2 < i < N+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2) + 1 / (3*k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (3*2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) - 4 / (3*k ** 2 * (r_i(i, h)) ** 2) - (4*cotang(o_j(j, k))) / (3*2 * k * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == 2 and j != 2 and j != M + 1:
            # i = 2, 2 < j < M+1
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == N + 1 and j != 2 and j != M + 1:
            # i = N+1, 2 < j < M+1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
            elif i == 2 and j == 2:
            # i = 2, j = 2
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == 2 and j == M + 1:
            # i = 2, j = M+1
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2) + 1 / (3*k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (3*2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) - 4 / (3*k ** 2 * (r_i(i, h)) ** 2) - (4*cotang(o_j(j, k))) / (3*2 * k * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = -1 / h ** 2 - 1 / (h * r_i(i, h))
            elif i == N + 1 and j == 2:
            # i = N + 1, j = 2
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) - cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2)
            elif i == N + 1 and j == M + 1:
            # i = N + 1, j = M + 1
                b[index, index - M] = -1 / h ** 2 + 1 / (h * r_i(i, h))
                b[index, index - 1] = - 1 / (k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (2 * k * (r_i(i, h)) ** 2) + 1 / (3*k ** 2 * (r_i(i, h)) ** 2) + cotang(o_j(j, k)) / (3*2 * k * (r_i(i, h)) ** 2)
                b[index, index] = 2 / h ** 2 + 2 / (k ** 2 * (r_i(i, h)) ** 2) - 4 / (3*k ** 2 * (r_i(i, h)) ** 2) - (4*cotang(o_j(j, k))) / (3*2 * k * (r_i(i, h)) ** 2) + V_ij(i, j, mass, gamma, h, k, potential)

def alternative_method_nonzero_MQN_NegSigma(b, mass, N, M, h, k, gamma, potential):
    for i in range(2, N + 2):
        for j in range(2, M + 2):
            index = index_transform(i, j, N)
            if i != 2 and i != N + 1 and j != 2 and j != M + 1:
            # 2 < i < N + 1, 2 < j < M+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif j == 2 and i != 2 and i != N + 1:
            # j = 2, 2 < i < N+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif j == M + 1 and i != 2 and i != N + 1:
            # j = M+1, 2 < i < N+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == 2 and j != 2 and j != M + 1:
            # i = 2, 2 < j < M+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) - (4*r_i(i + 0.5, h) ** 2) / (3*r_i(i, h) ** 2 * h ** 2)+ V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2) + r_i(i + 0.5, h) ** 2 / (3*r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == N + 1 and j != 2 and j != M + 1:
            # i = N+1, 2 < j < M+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == 2 and j == 2:
            # i = 2, j = 2
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) - (4*r_i(i - 0.5, h) ** 2) / (3*r_i(i, h) ** 2 * h ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2) + r_i(i - 0.5, h) ** 2 / (3*r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == 2 and j == M + 1:
            # i = 2, j = M+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) - (4*r_i(i + 0.5, h) ** 2) / (3*r_i(i, h) ** 2 * h ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2) + r_i(i + 0.5, h) ** 2 / (3*r_i(i, h) ** 2 * h ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == N + 1 and j == 2:
            # i = N + 1, j = 2
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == N + 1 and j == M + 1:
            # i = N + 1, j = M + 1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)

def alternative_method_zero_MQN_PosSigma(b, mass, N, M, h, k, gamma, potential):
    for i in range(2, N + 2):
        for j in range(2, M + 2):
            index = index_transform(i, j, N)
            if i != 2 and i != N + 1 and j != 2 and j != M + 1:
            # 2 < i < N + 1, 2 < j < M+1
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) + V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index + M] = - r_i(i+0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index - M] = - r_i(i-0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index + 1] = - sin(o_j(j+0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2)
                b[index, index - 1] = - sin(o_j(j-0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2)
            elif j == 2 and i != 2 and i != N + 1:
            # j = 2, 2 < i < N+1
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) - (4*sin(o_j(j-0.5,k)))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2)+ V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index + M] = - r_i(i+0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index - M] = - r_i(i-0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index + 1] = - sin(o_j(j+0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) + sin(o_j(j-0.5,k))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2)
            elif j == M + 1 and i != 2 and i != N + 1:
            # j = M+1, 2 < i < N+1
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) - (4*sin(o_j(j+0.5,k)))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2)+ V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index + M] = - r_i(i+0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index - M] = - r_i(i-0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index - 1] = - sin(o_j(j-0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) + sin(o_j(j+0.5,k))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2)
            elif i == 2 and j != 2 and j != M + 1:
            # i = 2, 2 < j < M+1
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) - (4*r_i(i-0.5,h)**2)/(3*r_i(i,h)**2*h**2) + V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index + M] = - r_i(i+0.5,h)**2/(r_i(i,h)**2*h**2) + r_i(i-0.5,h)**2/(3*r_i(i,h)**2*h**2)
                b[index, index + 1] = - sin(o_j(j+0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2)
                b[index, index - 1] = - sin(o_j(j-0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2)
            elif i == N + 1 and j != 2 and j != M + 1:
            # i = N+1, 2 < j < M+1
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) + V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index - M] = - r_i(i-0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index + 1] = - sin(o_j(j+0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2)
                b[index, index - 1] = - sin(o_j(j-0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2)
            elif i == 2 and j == 2:
            # i = 2, j = 2
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) - (4*r_i(i-0.5,h)**2)/(3*r_i(i,h)**2*h**2) - (4*sin(o_j(j-0.5,k)))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2) + V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index + M] = - r_i(i+0.5,h)**2/(r_i(i,h)**2*h**2) + (r_i(i-0.5,h)**2)/(3*r_i(i,h)**2*h**2)
                b[index, index + 1] = - sin(o_j(j+0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) + (sin(o_j(j-0.5,k)))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2)
            elif i == 2 and j == M + 1:
            # i = 2, j = M+1
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) - (4*r_i(i-0.5,h)**2)/(3*r_i(i,h)**2*h**2) - (4*sin(o_j(j+0.5,k)))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2) + V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index + M] = - r_i(i+0.5,h)**2/(r_i(i,h)**2*h**2) + (r_i(i-0.5,h)**2)/(3*r_i(i,h)**2*h**2)
                b[index, index - 1] = - sin(o_j(j-0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) + (sin(o_j(j+0.5,k)))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2)
            elif i == N + 1 and j == 2:
            # i = N + 1, j = 2
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) - (4*sin(o_j(j-0.5,k)))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2) + V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index - M] = - r_i(i-0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index + 1] = - sin(o_j(j+0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) + sin(o_j(j-0.5,k))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2)
            elif i == N + 1 and j == M + 1:
            # i = N + 1, j = M + 1
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) - (4*sin(o_j(j+0.5,k)))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2) + V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index - M] = - r_i(i-0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index - 1] = - sin(o_j(j-0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) + (sin(o_j(j+0.5,k)))/(3*r_i(i,h)*sin(o_j(j,k))*k**2)

def alternative_method_nonzero_MQN_PosSigma(b, mass, N, M, h, k, gamma, potential):
    for i in range(2, N + 2):
        for j in range(2, M + 2):
            index = index_transform(i, j, N)
            if i != 2 and i != N + 1 and j != 2 and j != M + 1:
            # 2 < i < N + 1, 2 < j < M+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif j == 2 and i != 2 and i != N + 1:
            # j = 2, 2 < i < N+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif j == M + 1 and i != 2 and i != N + 1:
            # j = M+1, 2 < i < N+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) - (4 * sin(o_j(j + 0.5, k))) / (3 * r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + sin(o_j(j + 0.5, k)) / (3 * r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == 2 and j != 2 and j != M + 1:
            # i = 2, 2 < j < M+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) - (4 * r_i(i - 0.5, h) ** 2) / (3 * r_i(i, h) ** 2 * h ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2) + r_i(i - 0.5, h) ** 2 / (3 * r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == N + 1 and j != 2 and j != M + 1:
            # i = N+1, 2 < j < M+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == 2 and j == 2:
            # i = 2, j = 2
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) - (4*r_i(i - 0.5, h) ** 2) / (3*r_i(i, h) ** 2 * h ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2) + r_i(i - 0.5, h) ** 2 / (3*r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == 2 and j == M + 1:
            # i = 2, j = M+1
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) - (4 * r_i(i - 0.5, h) ** 2) / (3 * r_i(i, h) ** 2 * h ** 2) - (4 * sin(o_j(j + 0.5, k))) / (3 * r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass, gamma, h, k, potential)
                b[index, index + M] = - r_i(i + 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2) + (r_i(i - 0.5, h) ** 2) / (3 * r_i(i, h) ** 2 * h ** 2)
                b[index, index - 1] = - sin(o_j(j - 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + (sin(o_j(j + 0.5, k))) / (3 * r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == N + 1 and j == 2:
            # i = N + 1, j = 2
                b[index, index] = (r_i(i + 0.5, h) ** 2 + r_i(i - 0.5, h) ** 2) / (r_i(i, h) ** 2 * h ** 2) + (sin(o_j(j + 0.5, k)) + sin(o_j(j - 0.5, k))) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2) + V_ij(i, j, mass,gamma, h, k,potential)
                b[index, index - M] = - r_i(i - 0.5, h) ** 2 / (r_i(i, h) ** 2 * h ** 2)
                b[index, index + 1] = - sin(o_j(j + 0.5, k)) / (r_i(i, h) ** 2 * sin(o_j(j, k)) * k ** 2)
            elif i == N + 1 and j == M + 1:
            # i = N + 1, j = M + 1
                b[index, index] = (r_i(i+0.5,h)**2+r_i(i-0.5,h)**2)/(r_i(i,h)**2*h**2) + (sin(o_j(j+0.5,k))+sin(o_j(j-0.5,k)))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) - (4*sin(o_j(j+0.5,k)))/(3*r_i(i,h)**2*sin(o_j(j,k))*k**2) + V_ij(i, j, mass, gamma, h, k,potential)
                b[index, index - M] = - r_i(i-0.5,h)**2/(r_i(i,h)**2*h**2)
                b[index, index - 1] = - sin(o_j(j-0.5,k))/(r_i(i,h)**2*sin(o_j(j,k))*k**2) + (sin(o_j(j+0.5,k)))/(3*r_i(i,h)*sin(o_j(j,k))*k**2)

def x_y_arrays_creating(radius, n_dimension, m_dimension, quarterNumber=1):
    R = float(radius)
    N = n_dimension
    M = m_dimension

    h = R / (N + 1.)
    k = np.pi / (2 * M + 2.)

    x = np.zeros(N)
    for i in range(N):
        x[i] = (i) * h
    M = m_dimension*quarterNumber
    y = np.zeros(M)
    for i in range(M):
        y[i] = (i)* k

    x, y = cart2pol(x, y)
    return x, y,

