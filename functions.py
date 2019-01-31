# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 14:46:41 2018

@author: stanza
"""

import numpy as np
from osgeo import gdal, ogr, gdalconst
import peakutils
from matplotlib import pyplot as plt

def listofMax(y):
    l=[]
#    x = np.arange(y.size)
#    dy = np.gradient(y, x)
#    
#    ddy = np.gradient(dy)
#    fig, ax = plt.subplots()
#    ax.plot(ddy)
#    plt.show()
#    for i in range(0, len(ddy)):
#        if((ddy[i] < 0)):
#            l.append(y[i])
#    myList = list(set(l))
#    myList.sort()
#    return myList
###########------------------------------------------------------------------
    indexes = peakutils.indexes(y, thres=0.005/max(y), min_dist=50)  #error line
    print(indexes) 
    for i in range(0,len(indexes)):
        print(y[indexes[i]])
        l.append(y[indexes[i]])
###########------------------------------------------------------------------    
#    max = y[1]
#    l = []
#    l.append(max)
#    for i in range(1,len(y)-1, 15):
##        print(y[i])
#        if (y[i] > y[i-1]): # tendencia ascendente
#            if (y[i] > max): # mas grande
#                max = y[i]
#        elif (y[i] > y[i+1]): # tendencia descendente
#            if (isBigger(max,l)):
#                l.append(max)
#                max=np.min(l)
#    l.remove(0.0)
    myList = list(set(l))
    myList.sort()
    return myList

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
    
def openFileHDF(file, nroBand):
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
    
    
    

def matchData(data_src, data_match, type, nRow, nCol):
    # funcion que retorna la informacion presente en el raster data_scr
    # modificada con los datos de proyeccion y transformacion del raster data_match
    # se crea un raster en memoria que va a ser el resultado
    #data_result = gdal.GetDriverByName('MEM').Create('', data_match.RasterXSize, data_match.RasterYSize, 1, gdalconst.GDT_Float64)

    data_result = gdal.GetDriverByName('MEM').Create('', nCol, nRow, 1)

    # Se establece el tipo de proyección y transfomcion en resultado  qye va ser coincidente con data_match
    data_result.SetGeoTransform(data_match.GetGeoTransform())
    data_result.SetProjection(data_match.GetProjection())

    # se cambia la proyeccion de data_src, con los datos de data_match y se guarda en data_result
    if (type == "Nearest"):
        gdal.ReprojectImage(data_src,data_result,data_src.GetProjection(),data_match.GetProjection(), gdalconst.GRA_NearestNeighbour)
    if (type == "Bilinear"):
        gdal.ReprojectImage(data_src, data_result, data_src.GetProjection(), data_match.GetProjection(), gdalconst.GRA_Bilinear)
    if (type == "Cubic"):
        gdal.ReprojectImage(data_src, data_result, data_src.GetProjection(), data_match.GetProjection(), gdalconst.GRA_Cubic)
    if (type == "Average"):
        gdal.ReprojectImage(data_src, data_result, data_src.GetProjection(), data_match.GetProjection(), gdal.GRA_Average)
    return data_result
