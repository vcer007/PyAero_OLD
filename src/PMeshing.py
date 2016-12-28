
import os
import copy
import numpy as np

from PUtils import Utils as Utils
from PSettings import OUTPUTDATA, LOGCOLOR
import PLogger as logger


class Windtunnel(object):
    """docstring for Windtunnel"""
    def __init__(self):
        super(Windtunnel, self).__init__()

    def AirfoilMesh(self, name='', contour=None, divisions=15, ratio=3.0,
                    thickness=0.04):

        # get airfoil contour coordinates
        x, y = contour

        # make a list point tuples
        # [(x1, y1), (x2, y2), (x3, y3), ... , (xn, yn)]
        line = zip(x, y)

        # block mesh around airfoil contour
        block_airfoil = BlockMesh(name=name)
        block_airfoil.addLine(line)
        block_airfoil.extrudeLine(line, length=thickness, direction=3,
                                  divisions=divisions, ratio=ratio)

        return block_airfoil

    def TrailingEdgeMesh(self, block_airfoil, name='', te_divisions=3,
                         length=0.04, divisions=6, ratio=3.0):

        # compile first line of trailing edge block
        first = block_airfoil.getLine(number=0, direction='v')
        last = block_airfoil.getLine(number=-1, direction='v')
        last_reversed = copy.deepcopy(last)
        last_reversed.reverse()

        vec = np.array(first[0]) - np.array(last[0])
        line = copy.deepcopy(last_reversed)
        for i in range(1, te_divisions):
            p = last_reversed[-1] + float(i) / te_divisions * vec
            # p is type numpy.float, so convert it to float
            line.append((float(p[0]), float(p[1])))
        line += first

        # trailing edge block mesh
        block_te = BlockMesh(name=name)
        block_te.addLine(line)
        block_te.extrudeLine(line, length=length, direction=3,
                             divisions=divisions, ratio=ratio)

        # equidistant point distribution
        block_te.distribute(direction='u', number=divisions+1)

        # smooth trailing edge block
        smooth = Smooth(block_te)
        nodes = smooth.selectNodes(domain='interior')
        block_te_smooth = smooth.smooth(nodes, iterations=1,
                                        algorithm='parallelogram')

        return block_te_smooth


class BlockMesh(object):

    def __init__(self, name='block'):
        self.name = name
        self.ULines = list()

    def addLine(self, line):
        # line is a list of (x, y) tuples
        self.ULines.append(line)

    def getULines(self):
        return self.ULines

    def getVLines(self):
        vlines = list()
        U, V = self.getDivUV()

        # loop over all u-lines
        for i in range(U + 1):
            # prepare new v-line
            vline = list()
            # collect i-th point on each u-line
            for uline in self.getULines():
                vline.append(uline[i])
            vlines.append(vline)

        return vlines

    def getLine(self, number=0, direction='u'):
        if direction.lower() == 'u':
            lines = self.getULines()
        if direction.lower() == 'v':
            lines = self.getVLines()
        return lines[number]

    def getDivUV(self):
        u = len(self.ULines[0]) - 1
        v = len(self.ULines) - 1
        return u, v

    def getNodeCoo(self, node):
        I, J = node[0], node[1]
        uline = self.getULines()[J]
        point = uline[I]
        return np.array(point)

    def setNodeCoo(self, node, new_pos):
        I, J = node[0], node[1]
        uline = self.getULines()[J]
        uline[I] = new_pos
        return

    def extrudeLine(self, line, direction=0, length=0.1, divisions=1,
                    ratio=1.00001, constant=False):
        x, y = zip(*line)
        x = np.array(x)
        y = np.array(y)
        if constant and direction == 0:
            x.fill(length)
            line = zip(x.tolist(), y.tolist())
            self.addLine(line)
        elif constant and direction == 1:
            y.fill(length)
            line = zip(x.tolist(), y.tolist())
            self.addLine(line)
        elif direction == 3:
            spacing = self.spacing(divisions=divisions,
                                   ratio=ratio,
                                   thickness=length)
            normals = self.curveNormals(x, y)
            for i in range(1, len(spacing)):
                xo = x + spacing[i] * normals[:, 0]
                yo = y + spacing[i] * normals[:, 1]
                line = zip(xo.tolist(), yo.tolist())
                self.addLine(line)

    def distribute(self, direction='u', number=1):

        U, V = self.getDivUV()

        divisions = {'u': U, 'v': V}

        if direction == 'u':
            line = self.ULines[number - 1]
        elif direction == 'v':
            line = self.getVLines()[number - 1]

        p1 = np.array((line[0], line[0]))
        p2 = np.array((line[-1], line[-1]))
        vec = p2 - p1

        for i in range(1, divisions[direction]):
            delta = p1 + i * vec / divisions[direction]
            line[i] = delta[0]
            line[i] = delta[1]

    def spacing(self, divisions=10, ratio=1.0, thickness=1.0):
        """Calculate point distribution on a line

        Args:
            divisions (int, optional): Number of subdivisions
            ratio (float, optional): Ratio of last to first subdivision size
            thickness (float, optional): length of line

        Returns:
            TYPE: Description
        """

        if divisions == 1:
            sp = [0.0, 1.0]
            return np.array(sp)

        growth = ratio**(1.0 / (float(divisions) - 1.0))

        if growth == 1.0:
            growth = 1.0 + 1.0e-10

        s0 = 1.0
        s = [s0]
        for i in range(1, divisions + 1):
            app = s0 * growth**i
            s.append(app)
        sp = np.array(s)
        sp -= sp[0]
        sp /= sp[-1]
        sp *= thickness
        return sp

    def curveNormals(self, x, y, closed=False):
        istart = 0
        iend = 0
        n = list()

        for i, dummy in enumerate(x):

            if closed:
                if i == len(x) - 1:
                    iend = -i - 1
            else:
                if i == 0:
                    istart = 1
                if i == len(x) - 1:
                    iend = -1

            a = np.array([x[i + 1 + iend] - x[i - 1 + istart],
                          y[i + 1 + iend] - y[i - 1 + istart]])
            e = Utils.unit_vector(a)
            n.append([e[1], -e[0]])
            istart = 0
            iend = 0
        return np.array(n)

    def writeFLMA(self, airfoil='', depth=0.1):

        folder = OUTPUTDATA + '/'
        nameroot, extension = os.path.splitext(str(airfoil))
        filename = nameroot + '_' + self.name + '.flma'
        fullname = folder + filename

        logger.log.info('Mesh <b><font color=%s> %s</b> saved to output folder'
                        % ('#099a53', filename))

        U, V = self.getDivUV()
        points = (U + 1) * (V + 1)

        with open(fullname, 'w') as f:

            numvertex = '8'

            # write number of points to FLMA file (*2 for z-direction)
            f.write(str(2 * points) + '\n')

            signum = -1.

            # write x-, y- and z-coordinates to FLMA file
            # loop 1D direction (symmetry)
            for j in range(2):
                for uline in self.getULines():
                    for i in range(len(uline)):
                        f.write(str(uline[i][0]) + ' ' + str(uline[i][1]) +
                                ' ' + str(signum * depth / 2.0) + ' ')
                signum = 1.

            # write number of cells to FLMA file
            cells = U * V
            f.write('\n' + str(cells) + '\n')

            # write cell connectivity to FLMA file
            up = U + 1
            vp = V + 1
            for i in range(U):
                for j in range(V):

                    p1 = j * up + i + 1
                    p2 = (vp + j) * up + i + 1
                    p3 = p2 - 1
                    p4 = p1 - 1
                    p5 = (j + 1) * up + i + 1
                    p6 = (vp + j + 1) * up + i + 1
                    p7 = p6 - 1
                    p8 = p5 - 1

                    connectivity = str(p1) + ' ' + str(p2) + ' ' + str(p3) + \
                        ' ' + str(p4) + ' ' + str(p5) + ' ' + str(p6) + \
                        ' ' + str(p7) + ' ' + str(p8) + '\n'

                    f.write(numvertex + '\n')
                    f.write(connectivity)

            # write FIRE element type (FET) to FLMA file
            fetHEX = '5'
            f.write('\n' + str(cells) + '\n')
            for i in range(cells):
                f.write(fetHEX + ' ')
            f.write('\n\n')

            # write FIRE selections to FLMA file
            f.write('0')


class Smooth(object):

    def __init__(self, block):
        self.block = block

    def transfinite(xi_count, eta_count, xi_curve_bottom, xi_curve_top,
                    eta_curve_left, eta_curve_right):
        pass

    def getRotationAngle(self, node, n, degree=True):

        before = n - 1
        if before == 0:
            before = 8
        after = n + 1
        if after == 9:
            after = 1

        b = np.array([graph.node[neighbours[before]]['pos'][0],
                      graph.node[neighbours[before]]['pos'][1]])
        a = np.array([graph.node[neighbours[after]]['pos'][0],
                      graph.node[neighbours[after]]['pos'][1]])
        c = np.array([graph.node[node]['pos'][0], graph.node[node]['pos'][1]])
        s = np.array([graph.node[neighbours[n]]['pos'][0],
                      graph.node[neighbours[n]]['pos'][1]])
        u = b - s
        v = a - s
        w = c - s
        alpha2 = Utils.angle_between(u, w, degree=degree) * (-1.0) * \
            np.sign(np.cross(u, w))
        alpha1 = Utils.angle_between(w, v, degree=degree) * (-1.0) * \
            np.sign(np.cross(w, v))
        beta = (alpha2 - alpha1) / 2.0

        return beta

    def getNeighbours(self, node):
        """Get a list of neighbours around a node """

        i, j = node[0], node[1]
        neighbours = {1: (i - 1, j - 1), 2: (i, j - 1), 3: (i + 1, j - 1),
                      4: (i + 1, j), 5: (i + 1, j + 1), 6: (i, j + 1),
                      7: (i - 1, j + 1), 8: (i - 1, j)}
        return neighbours

    def smooth(self, nodes, iterations=1, algorithm='angle_based'):
        """Smoothing of a square lattice mesh

        Algorithms:
           - Angle based
             Tian Zhou:
             AN ANGLE-BASED APPROACH TO TWO-DIMENSIONAL MESH SMOOTHING
           - Laplace
             Mean of surrounding node coordinates
           - Parallelogram smoothing
             Sanjay Kumar Khattri:
             A NEW SMOOTHING ALGORITHM FOR QUADRILATERAL AND HEXAHEDRAL MESHES

        Args:
            nodes (TYPE): List of (i, j) tuples for the nodes to be smoothed
            iterations (int, optional): Number of smoothing iterations
            algorithm (str, optional): Smoothing algorithm
        """

        # loop number of smoothing iterations
        for i in range(iterations):

            new_pos = list()

            # smooth a node (i, j)
            for node in nodes:
                nb = self.getNeighbours(node)

                if algorithm == 'laplace':
                    new_pos = (self.block.getNodeCoo(nb[2]) +
                               self.block.getNodeCoo(nb[4]) +
                               self.block.getNodeCoo(nb[6]) +
                               self.block.getNodeCoo(nb[8])) / 4.0

                if algorithm == 'parallelogram':

                    new_pos = (self.block.getNodeCoo(nb[1]) +
                               self.block.getNodeCoo(nb[3]) +
                               self.block.getNodeCoo(nb[5]) +
                               self.block.getNodeCoo(nb[7])) / 4.0 - \
                              (self.block.getNodeCoo(nb[2]) +
                               self.block.getNodeCoo(nb[4]) +
                               self.block.getNodeCoo(nb[6]) +
                               self.block.getNodeCoo(nb[8])) / 20.0

                self.block.setNodeCoo(node, new_pos.tolist())

        return self.block

    def selectNodes(self, domain='interior'):
        """Generate a node index list

        Args:
            domain (str, optional): Defines the part of the domain where
                                    nodes shall be selected

        Returns:
            List: Indices as (i, j) tuples
        """
        U, V = self.block.getDivUV()
        nodes = list()

        # select all nodes except boundary nodes
        if domain == 'interior':
            for i in range(1, U):
                for j in range(1, V):
                    nodes.append((i, j))

        return nodes
