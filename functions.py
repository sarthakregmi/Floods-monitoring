# -*- coding: utf-8 -*-
#!/usr/bin/python

"""
Created on Thu Jun 28 14:46:41 2018

@author: gag

Document where the functions required for the opening of SAR images and the analysis of histograms are found.
The statistics calculated to histograms are used for the detection of flooded areas.

"""

import numpy as np
from osgeo import gdal, ogr, gdalconst
import peakutils
from matplotlib import pyplot as plt


#### --------------------------------------------------------------------------------------

def openFileHDF(file, nroBand):
    """ Function that opens an image with .HDF format and reads a specific band.

    Parameters:
    -----------
    file : complete path of the raster image 
    nroBand : number of the band to be read 

    Returns: 
    --------
    src_ds: source raster object
    band:
    GeoT: georeference
    Project: projection
    """

    #print "Open File"
    # file = path+nameFile
    #print file
    try:
        src_ds = gdal.Open(file)
    except (RuntimeError, e):
        print('Unable to open File')
        print(e)
        sys.exit(1)

#    cols = src_ds.RasterXSize
#    rows = src_ds.RasterYSize
#    print(cols)
#    print(rows)
    bands = src_ds.RasterCount
#    print(bands)

    # se obtienen las caracteristicas de las imagen HDR
    GeoT = src_ds.GetGeoTransform()
    #print GeoT
    Project = src_ds.GetProjection()

    try:
        srcband = src_ds.GetRasterBand(nroBand)
    except(RuntimeError, e):
        # for example, try GetRasterBand(10)
        print('Band ( %i ) not found' % band_num)
        print(e)
        sys.exit(1)
    band = srcband.ReadAsArray()
#    print(band.shape)
    return src_ds, band, GeoT, Project




#### --------------------------------------------------------------------------------------
### se define la función multimodal a partir de la composición de gausianas

def gauss(x,mu,sigma,A):
    return A*exp(-(x-mu)**2.0/(2*sigma**2.0))

def bimodal(x,mu1,sigma1,A1,mu2,sigma2,A2): 
    return gauss(x,mu1,sigma1,A1)+gauss(x,mu2,sigma2,A2)

### la multimodal para este caso la define con 3 gausianas
def multimodal(x,mu1,sigma1,A1,mu2,sigma2,A2, mu3,sigma3,A3): 
    return gauss(x,mu1,sigma1,A1)+gauss(x,mu2,sigma2,A2) + gauss(x, mu3,sigma3,A3)
    

#### --------------------------------------------------------------------------------------

def listofMax(y):
    """ Function that lists the maximums of the vector, uses the peakutils function

    Parameters:
    -----------
    y : array 

    Returns: 
    --------
    myList: list of vector maximums
    """

    l=[]
    indexes = peakutils.indexes(y, thres=0.005/max(y), min_dist=50) 
    print(indexes) 
    for i in range(0,len(indexes)):
        print(y[indexes[i]])
        l.append(y[indexes[i]])
    ### funcion set elimina los elementos repetidos
    myList = list(set(l))
    myList.sort()
    print("cantidad de maximos: " +str(len(myList)))
    return myList

#### --------------------------------------------------------------------------------------


def minLocal(max1, max2, y):
    indexMax2 = index(max2, y)
    indexMax1 = index(max1, y)
    minLocal = y[indexMax1]
    #print minLocal
    for i in range(indexMax1,indexMax2):
        if ((y[i] > minLocal) & (y[i] < max2)):
            minLocal= y[i]
    return minLocal



def isBigger(max,l):
    if(max >= np.min(l)):
        return True
    else: 
        return False


def index(max,y):
    for i in range(0,len(y)):
        if(y[i] == max):
            return i+1


def Max1MinLocalMax2(x,y):  
    l = listofMax(y)
    print("Los maximos: ")
    print(l)

    if (len(l) == 2):
        max2 = np.max(l)
        indexMax2 = index(max2,y)
        l.remove(max2)
    
        ### este pico pertenece al agua libre
        max1 = np.max(l)
        indexMax1 = index(max1,y)
        
        indexMax3 = indexMax2
        pico1 = x[indexMax1]
        pico2 = x[indexMax2]
        pico3 = x[indexMax3]

    else:
        max3 = np.max(l)
        l.remove(max3)    
        max2 = np.max(l)
        l.remove(max2)        
        ### este pico pertenece al agua libre
        max1 = np.max(l)
        indexMax1 = index(max1,y)
                
        print("####################################")
        print(max1)
        
        indexMax3 = index(max3,y)    
        indexMax2 = index(max2,y)
        ### el inconveniente aparece cuando el pico 2 es mayor o menor que el
        ### pico 3        

        if(indexMax3 < indexMax2):
            indexMax3 = index(max2,y)    
            indexMax2 = index(max3,y)
        if(indexMax2 < indexMax1):
            indexMax1 = index(max2,y)    
            indexMax2 = index(max1,y)



    
#    max3 = tercerPico(indexMax1, max1, max2, y)
#    print("maximo 3:" +str(max3))
#    indexMax1 = index(max1,y)    

        pico1 = x[indexMax1]
        pico2 = x[indexMax2]
        pico3 = x[indexMax3]
    

    
    
    print("Maximo 1: " + str(pico1))
    print("Maximo 2: " + str(pico2))
    print("Maximo 3: " + str(pico3))

    minL = minLocal(max1, max2,y)
    indexMinLocal = index(minL,y)
    minimoLocal = x[indexMinLocal]
    print("Minimo Local: " + str(minimoLocal))

    return pico1, minimoLocal, pico2, pico3
    

#### --------------------------------------------------------------------------------------   

def find_peaks(a):
    a= a*100
    x = np.array(a)
    max = np.max(x)
    print(max)
    lenght = len(a)
    ret = []
    for i in range(lenght):
        ispeak = True
        if i-1 > 0:
            ispeak &= (x[i] > 1.1 * x[i-1])
        if i+1 < lenght:
            ispeak &= (x[i] > 1.1 * x[i+1])

        ispeak &= (x[i] > 1 * max)
        if ispeak:
            ret.append(x[i]/100)
    return ret


    
 
