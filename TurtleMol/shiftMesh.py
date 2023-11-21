'''Fills an arbitrary mesh with molecules'''

import numpy as np
from .isOverlap import isOverlapAtom, isOverlapMolecule
from .makeStruc import makeBase, reCenter, randReorient

def atomsFillMesh(mesh, og, tol, radii, numMol):
    '''Fills mesh with single atoms'''
    filled = []

    if str(numMol).lower() == 'fill':
        numMol = 10000000000000

    # Determine bounds of mesh
    bounds = mesh.bounds
    minBound, maxBound = bounds[0], bounds[1]

    # Determine spacing between molecules
    spacing = tol

    # Generate grid of points
    gridX, gridY, gridZ = np.mgrid[minBound[0]:maxBound[0]:spacing,
                                   minBound[1]:maxBound[1]:spacing,
                                   minBound[2]:maxBound[2]:spacing]
    
    # Check each point in the grid
    for x in np.nditer(gridX):
        for y in np.nditer(gridY):
            for z in np.nditer(gridZ):
                for atom in og:
                    # Construct atom data
                    atomData = [atom[0], x, y, z]
                    if len(atom) == 5:
                            atomData.append(atom[4])
                    point = [x, y, z]
                    if mesh.isInside(point) and \
                        not isOverlapAtom(atomData, filled, radii, tol):

                        filled.append(atomData)
    
    return filled

def moleculesFillMesh(mesh, og, tol, radii, numMol, baseStruc, randOrient):
    '''Fills mesh with molecules'''
    filled = []

    if str(numMol).lower() == 'fill':
        numMol = 10000000000000

    if baseStruc is not None:
        base = makeBase(baseStruc)
        #filled.append(reCenter(base, ))

    # Determine bounds of mesh
    bounds = mesh.bounds
    minBound, maxBound = bounds[0], bounds[1]
    print(minBound, maxBound)

    # Determine spacing between molecules
    spacing = tol

    # Generate grid of points
    gridX, gridY, gridZ = np.mgrid[minBound[0]:maxBound[0]:spacing,
                                   minBound[1]:maxBound[1]:spacing,
                                   minBound[2]:maxBound[2]:spacing]
    
    # Check each point in the grid
    for i in range(gridX.shape[0]):
        for j in range(gridY.shape[1]):
            for k in range(gridZ.shape[2]):
                x = gridX[i, j, k]
                y = gridY[i, j, k]
                z = gridZ[i, j, k]

                # Check if entire molecule can be placed
                molValid = True
                newMol = []
                for atom in og:
                    # Construct atom data
                    atomType, relX, relY, relZ = atom[:4]
                    atomPoint = [x + relX, y + relY, z + relZ]

                    if not mesh.isInside(atomPoint):
                        molValid = False
                        break
                
                if molValid:
                    for atom in og:
                        atomType, relX, relY, relZ = atom[:4]
                        if len(atom) == 4:
                            atomData = (atomType, float(x + relX), float(y + relY), float(z + relZ))
                        if len(atom) == 5:
                            atomData = (atomType, float(x + relX), float(y + relY), float(z + relZ), atom[4])

                        newMol.append(atomData)
                        
                        if randOrient and len(newMol) == len(og):
                            newMol = randReorient(newMol)

                        if not isOverlapMolecule(newMol, filled, radii, tol):
                            filled.append(newMol)
    return filled
