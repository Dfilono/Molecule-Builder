'''Sets up the structure files'''

import numpy as np
from scipy.spatial.transform import Rotation
from setAtomProp import setAtomicMass

def makeBase(baseStruc):
    '''Convert dataframe to list of points'''
    atomBase = baseStruc['Atom'].values.tolist()
    xBase = baseStruc['X'].values.tolist()
    yBase = baseStruc['Y'].values.tolist()
    zBase = baseStruc['Z'].values.tolist()

    if 'Residue' not in baseStruc.columns:
        return [(atomBase[i], xBase[i], yBase[i], zBase[i]) for i in range(len(atomBase))]

    residue = baseStruc['Residue'].values.tolist()
    return [(atomBase[i], xBase[i], yBase[i], zBase[i], residue[i]) for i in range(len(atomBase))]

def calcCenter(coords):
    '''Calculate geometric center'''
    if not coords:
        return None

    numCoords = len(coords)
    centerX = sum(coord[1] for coord in coords) / numCoords
    centerY = sum(coord[2] for coord in coords) / numCoords
    centerZ = sum(coord[3] for coord in coords) / numCoords

    return (centerX, centerY, centerZ)

def reCenter(struc, shape):
    '''Set center structure coordiantes to center of shape'''
    currentCenter = calcCenter(struc)
    shapeCenter = shape.findCenter()
    displacement = (
        shapeCenter[0] - currentCenter[0],
        shapeCenter[1] - currentCenter[1],
        shapeCenter[2] - currentCenter[2]
    )
    newCoords = [(coord[0], coord[1] + displacement[0], coord[2] + displacement[1],
                coord[3] + displacement[2]) for coord in struc]

    return newCoords

def shiftPoints(points, shape):
    '''Sifts points to the bottom-left front corner of a 3D shape'''
    pointNames = [point[0] for point in points]
    coords = np.array([point[1:4] for point in points], dtype=float)

    if len(points[0]) == 5:
        pointRes = [point[4] for point in points]
    else:
        pointRes = None

    # Determine the bounds of the points
    min_x_points = np.min(coords[:, 0])
    min_y_points = np.min(coords[:, 1])
    min_z_points = np.min(coords[:, 2])

    # Calculate the translation required
    translation = np.array([
        shape.leftCorner()[0] - min_x_points,
        shape.leftCorner()[1] - min_y_points,
        shape.leftCorner()[2] - min_z_points,
    ])

    # Shift the points
    shiftedCoords = coords + translation
    if pointRes:
        shiftedPoints = [[name] + coord.tolist() + [residue] 
                         for name, coord, residue in 
                         zip(pointNames, shiftedCoords, pointRes)]
    else:
        shiftedPoints = [[name] + coord.tolist() 
                         for name, coord in zip(pointNames, shiftedCoords)]

    return shiftedPoints

def randReorient(mol): # NOTE Currently does not work and is disabled
    '''Randomly reorients a molecule around geometric center'''
    if not mol:
        return mol

    center = np.asarray(calcCenter(mol))
    pointsToRotate = []
    for i in mol:
        pointsToRotate.append(i[1:])
    print(pointsToRotate)
    randomRotation = Rotation.random()

    rotatedPoints = []
    for i in pointsToRotate:
        rotatedPoints.append(randomRotation.apply(i - center) + center)
    print(rotatedPoints)
    rotatedMol = []
    for i in mol:
        rotatedMol.append((i[0], rotatedPoints[0], rotatedPoints[1], rotatedPoints[2]))
    print(f"Center: {center}, Mol: {mol}, Rotated Mol: {rotatedMol}\n")

    return rotatedMol

def calcDensity(shape, mol):
    '''Calculates the density of a given structure'''
    vol = shape.volume() * 1.0e-24 # mL
    mass = 0
    atomicMass = setAtomicMass() # g/mol

    for atom in mol:
        mass += atomicMass[atom[0]]

    return mass/vol # g/mol/mL

def calcNumMol(shape, mol, denisty):
    '''
    Calulates the number of molecules needed in a box to match
    the defined density based off of the defined volume
    '''
    vol = shape.volume() # mL
    massGoal = vol * float(denisty)
    print(massGoal)
    mass = 0
    atomicMass = setAtomicMass() # g/mol

    for atom in mol:
        mass += atomicMass[atom[0]]

    numMol = 1
    while mass < massGoal:
        mass += mass
        numMol += 1

    return int(numMol)
