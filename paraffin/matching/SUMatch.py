# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 17:03:14 2015

@author: piotrt
"""
# Import necessary libraries
import tables
import numpy as np
import sys
from ..SU import readSUF  # SU Format
from ..SU import writeSUF  # SU Format
import getTwiss
import matchTwiss
import getBeamTwiss
from ..puffin import puffData
from ..puffin import undulator

def SU2Matched(fnamein, puffVars, undmod, qf, DL, twx1=False, twy1=False, twx2=False, twy2=False):

#  twx1, twy1 are numpy arrays in form [emittance, beta, alpha] describing x
#  and y, respectively
#  emittance is geometric emittance
#  beta and alpha are usual Twiss parameters
#  If these are entered, then the beam will be assumed to have these Twiss parameters,
#  if not present, then they will be calculated from the beam file.


#    Store basename of file

    file_name_base  = (fnamein.split('.')[0]).strip()

#    Get beam distribution from file

    MPs = readSUF(fnamein)

    calcdtwy = False

    qFODO = True
    if (qf == 0.):
        qFODO = False

#  Twiss parameters of beam before matching:

    if (not twx1):
        # Calculate twiss parameters for beam
        #SU_data = np.vstack((x, px, y, py, z, pz, wghts)).T
        twxt, twyt = getBeamTwiss.getTwiss(MPs)
        calcdtwy = True
        twxr1 = twxt
    else:
        # Using Twiss parameters given as initial condition
        twxr1 = twx1 # [131.98, 69.22] # [300., 157.]  (betax, alphax) of beam to be transformed

    if (not twy1):
        # Calculate twiss parameters for beam
        if (calcdtwy):
            twyr1 = twyt
        else:
            SU_data = np.vstack((x, px, y, py, z, pz, wghts)).T
            twxt, twyt = getBeamTwiss.getTwiss(SU_data)
            twyr1 = twyt            
    else:
        # Using Twiss parameters given as initial condition
        twyr1 = twy1 # [131.98, 69.22] # [300., 157.]  (betax, alphax) of beam to be transformed



    calcdtwy = False
    if (not twx2):
        if qFODO:
            twx2, twy2 = getTwiss.getFODOTwiss(puffVars, undmod, qf, DL, twxr1[0], twyr1[0])
        else:
            twx2, twy2 = getTwiss.getUndTwiss(puffVars, undmod, twxr1[0], twyr1[0])
        calcdtwy = True
        twxr2 = twx2
    else:
        twxr2 = twx2


    if (not twy2):
        if (calcdtwy):
            twyr2 = twy2
        else:
            if qFODO:
                twx2, twy2 = getTwiss.getFODOTwiss(puffVars, undmod, qf, DL, twxr1[0], twyr1[0])
            else:
                twx2, twy2 = getTwiss.getUndTwiss(puffVars, undmod, twxr1[0], twyr1[0])
            twyr2 = twy2
    else:
        twyr2 = twy2

#    twxr2[1:] = [3.76, -0.189]
#    twyr2[1:] = [1.44, 0.]

    print twxr2
    print twyr2

#   Match beam to given parameters

    x = MPs[:,0]
    px = MPs[:,1]
    y = MPs[:,2]
    py = MPs[:,3]
    z = MPs[:,4]
    pz = MPs[:,5]
    wghts = MPs[:,6]

    x2, px2, y2, py2 = matchTwiss.matchTwiss(x, px/pz, y, py/pz, twxr1[1:], twxr2[1:], twyr1[1:], twyr2[1:])

    px2 = px2 * pz
    py2 = py2 * pz

    MPs=np.vstack((x2, px2, y2, py2, z, pz, wghts)).T

    outname = file_name_base + '_matched.h5'
    writeSUF(outname, MPs)
    return outname



#if __name__ == '__main__':
#
#    if len(sys.argv)==2:
#        fname = sys.argv[1]
#        print 'Processing file:', fname
#        SU2Matched(fname)
#    else:
#        print 'Usage: SU2Puffin <FileName> \n'
#        sys.exit(1)
        
        

