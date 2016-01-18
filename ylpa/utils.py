'''
Created on 2. 6. 2015

@author: Kapsak
'''
import numpy as np
from numpy.linalg import inv

def get_point_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

def cutoff_by_vector(p1, p2, points):
    '''p1 is the origin of the coordinate system, vector |p1,p2| is the x axis.
    The points that have a positive y coordinate are returned.
    '''
    vector_length = get_point_distance(p1, p2)
    s = (p2[1] - p1[1]) / vector_length
    c = (p2[0] - p1[0]) / vector_length
    points = np.array(points)
    inner_points = []
    for i in range(len(points)):
        yi = -s * (points[i, 0] - p1[0]) + c * (points[i, 1] - p1[1])
        if yi >= 0:
            inner_points.append(i)
    return points[inner_points, :]

def gauss(matrix1, matrix2):
    '''A gauss elimination algorithm is applied on matrix2 until a unit matrix is obtained.
    The row operations are performed simultaneously on matrix1.
    Matrix2 should be of shape MxN. When M>N, the output matrix has zeros in the last M-N rows.
    Matrix1 is of shape MxM.

    @todo: Input control should be written
    '''
    m1 = matrix1.copy()
    m2 = matrix2.copy()
    nrows, ncols = m2.shape[0], m2.shape[1]
    for i in range(ncols):
        # print 'down', i
        # If the diagonal element is zero, we try to add some of the next rows.
        # If there are none with nonzero value in the column, raise an error.
        if m2[i, i] == 0.:
            nonzero = np.where(m2[:, i])[0][-1]
            if nonzero > i:
                m2[i, :] += m2[nonzero, :]
                m1[i, :] += m1[nonzero, :]
            else:
                print 'Error: matrix2...'  # improve error message
                return
        # print m1, m2

        # Unit value on the diagonal
        dia = m2[i, i]
        m2[i, :] *= (1 / dia)
        m1[i, :] *= (1 / dia)

        # Subtract from succeeding rows
        for j in range(i + 1, nrows):
            if m2[j, i] != 0.:
                c = m2[j, i]
                m2[j, :] -= m2[i, :] * c
                m1[j, :] -= m1[i, :] * c
        # print m1, m2

    # Start from the N-th row and make a unit matrix
    for i in range(ncols)[:0:-1]:
        # print 'up', i
        # Subtract from succeeding rows
        for j in range(ncols)[i - 1::-1]:
            if m2[j, i] != 0.:
                c = m2[j, i] / m2[i, i]
                m2[j, :] -= m2[i, :] * c
                m1[j, :] -= m1[i, :] * c
    # print m1, m2
    return [m1, m2]
