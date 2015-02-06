#! /usr/bin/env python
#coding=utf-8
from Util import *
from Hillslope import *
from Subbasin import *
import os,sys,copy


def IdentifyRillShoulderPts(Aspect,Slope,ProfC,alpha,beta,ShoulderPts):
    aspect = ReadRaster(Aspect).data
    nrows,ncols = aspect.shape
    nodata = ReadRaster(Aspect).noDataValue
    geotrans = ReadRaster(Aspect).geotrans
    slope = ReadRaster(Slope).data
    profc = ReadRaster(ProfC).data
    ShoulderPtsMtx = numpy.ones((nrows,ncols))
    if nodata != -9999:
        ShoulderPtsMtx = ShoulderPtsMtx * -9999
    else:
        ShoulderPtsMtx = ShoulderPtsMtx * nodata

    for i in range(nrows):
        for j in range(ncols):
            # North
            if (aspect[i][j] >= 0 and aspect[i][j] < 22.5) or (aspect[i][j] >= 337.5 and aspect[i][j] < 360):
                if not(i-1 < 0 or i+1 >= nrows):
                    if (slope[i][j]<slope[i-1][j]) and (slope[i+1][j]<slope[i][j]) and slope[i][j]>alpha and (slope[i-1][j]-slope[i+1][j] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # Northeast
            if (aspect[i][j] >= 22.5 and aspect[i][j] < 67.5):
                if not(i-1 < 0 or i+1>nrows or j-1<0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i-1][j+1]) and (slope[i+1][j-1]<slope[i][j]) and slope[i][j]>alpha and (slope[i-1][j+1]-slope[i+1][j-1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # East
            if (aspect[i][j] >= 67.5 and aspect[i][j] < 112.5):
                if not(j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i][j+1]) and (slope[i][j-1]<slope[i][j]) and slope[i][j]>alpha and (slope[i][j+1]-slope[i][j-1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # Southeast
            if (aspect[i][j] >= 112.5 and aspect[i][j] < 157.5):
                if not(i-1 < 0 or i+1 >= nrows or j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i+1][j+1]) and (slope[i-1][j-1]<slope[i][j]) and slope[i][j]>alpha and (slope[i+1][j+1]-slope[i-1][j-1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # South
            if (aspect[i][j] >= 157.5 and aspect[i][j] < 202.5):
                if not(i-1 < 0 or i+1 >= nrows):
                    if (slope[i][j]<slope[i+1][j]) and (slope[i-1][j]<slope[i][j]) and slope[i][j]>alpha and (slope[i+1][j]-slope[i-1][j] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # Southwest
            if (aspect[i][j] >= 202.5 and aspect[i][j] < 247.5):
                if not(i-1 < 0 or i+1 >= nrows or j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i+1][j-1]) and (slope[i-1][j+1]<slope[i][j]) and slope[i][j]>alpha and (slope[i+1][j-1]-slope[i-1][j+1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # West
            if (aspect[i][j] >= 247.5 and aspect[i][j] < 292.5):
                if not(j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i][j-1]) and (slope[i][j+1]<slope[i][j]) and slope[i][j]>alpha and (slope[i][j-1]-slope[i][j+1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # Northwest
            if (aspect[i][j] >= 292.5 and aspect[i][j] < 337.5):
                if not(i-1 < 0 or i+1 >= nrows or j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i-1][j-1]) and (slope[i+1][j+1]<slope[i][j]) and slope[i][j]>alpha and (slope[i-1][j-1]-slope[i+1][j+1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
    WriteAscFile(ShoulderPts, ShoulderPtsMtx,ncols,nrows,geotrans,-9999)
            
def RillShoulderSegement(Boundary,FlowDir,ShoulderPts,ShoulderFile):
    flowdir = ReadRaster(FlowDir).data
    flownodata = ReadRaster(FlowDir).noDataValue
    geotrans = ReadRaster(FlowDir).geotrans
    boundary = ReadRaster(Boundary).data
    shoulderpts = ReadRaster(ShoulderPts).data
    nrows,ncols = flowdir.shape
    nodata = ReadRaster(Boundary).noDataValue
    bndIdx = []
    for i in range(nrows):
        for j in range(ncols):
            if boundary[i][j] != nodata:
                #print i,j
                bndIdx.append([i,j])
    
    iterate = 0
    changed = 0
    tempBnd = []
    tempBnd.extend(bndIdx)
    pairPts = []
    prev = []
    currcell = tempBnd[0]
    nextcell = []
    while len(tempBnd) > 0:
        nextcell = NearCells(boundary,nodata,currcell[0],currcell[1])
        if nextcell != [] and currcell in nextcell:
            nextcell.remove(currcell)
        if nextcell != [] and prev != [] and prev in nextcell:
            nextcell.remove(prev)
        if nextcell == [] or nextcell == None:
            prev = []
            currcell = tempBnd[0]
        elif len(nextcell) >= 1:
            pairPts.append([currcell,nextcell[0]])
            tempBnd.remove(nextcell[0])
            boundary[nextcell[0][0]][nextcell[0][1]] = nodata
            prev = currcell
            currcell = nextcell[0]
    #print pairPts
    #print len(pairPts)
    for pts in pairPts:
        for pt in pts:
            if shoulderpts[pt[0]][pt[1]] != nodata:
                tempBnd.append(pt)
            else:
                row,col = downstream_index(flowdir[pt[0]][pt[1]], pt[0],pt[1])
                if row < 0 or row >= nrows or col < 0 or col >= ncols:
                    tempBnd.append(pt)
                else:
                    tempBnd.append([row,col])
                    pairPts[pairPts.index(pts)][pts.index(pt)] = [row,col]
                    changed = changed + 1
    #print pairPts
    for pts in pairPts:
        #print InterpLine(pts[0],pts[1])
        tempBnd.extend(InterpLine(pts[0],pts[1]))
    uniqueIdxs = []
    for idx in tempBnd:
        if idx not in uniqueIdxs:
            uniqueIdxs.append(idx)
    tempBnd = []
    tempBnd.extend(uniqueIdxs)

    for pt in tempBnd:
        row,col = pt
        if row >= 0 and row < nrows and col >= 0 and col < ncols:
            boundary[row][col] = 1
        else:
            tempBnd.remove(pt)
    #print tempBnd
    #num,boundary = simplifyBoundary(boundary,nodata)
    #print num
#    while num != 0:
#        num,boundary = simplifyBoundary(boundary,nodata)
    iterate = iterate + 1
    WriteAscFile(ShoulderFile, tempBnd,ncols,nrows,geotrans,-9999)

        
        
        
#    while not(changed == 0 or iterate > 5):
#        print "iterate time:%s, changed num:%s, boundary num:%s" % (iterate,changed,len(bndIdx))
#        changed = 0
#        tempbndIdx = []
#        for bnd in bndIdx:
#            if shoulderpts[bnd[0]][bnd[1]] == 1:
#                tempbndIdx.append((bnd[0],bnd[1]))
#            else:
#                row,col = downstream_index(flowdir[bnd[0]][bnd[1]], bnd[0],bnd[1])
#                if row < 0 or row >= nrows or col < 0 or col >= ncols:
#                    tempbndIdx.append((bnd[0],bnd[1]))
#                else:
#                    tempbndIdx.append((row,col))
#                    changed = changed + 1
#        tempbndIdx = list(set(tempbndIdx))
#        bndIdx = tempbndIdx
#        iterate = iterate + 1
#        
#    shoulder = numpy.ones((nrows,ncols))
#    shoulder = shoulder * -9999
#    for sd in bndIdx:
#        shoulder[sd[0]][sd[1]] = 1
#    WriteAscFile(ShoulderFile, shoulder,ncols,nrows,geotrans,-9999)
def SnakeCreep(boundary,shoulderpts,flowdir,nodata,MaxIterate,geotrans,tempdir):
    iterate = 0
    changed = 9999
    nrows,ncols = boundary.shape
    while iterate < MaxIterate or changed == 0:
        bndIdx = []
        for i in range(nrows):
            for j in range(ncols):
                if boundary[i][j] != nodata:
                    #print i,j
                    bndIdx.append([i,j])
        changed = 0
        tempBnd = []
        tempBnd.extend(bndIdx)
        pairPts = []
        prev = []
        currcell = tempBnd[0]
        nextcell = []
        while len(tempBnd) > 0:
            nextcell = NearCells(boundary,nodata,currcell[0],currcell[1])
            if nextcell != [] and currcell in nextcell:
                nextcell.remove(currcell)
            if nextcell != [] and prev != [] and prev in nextcell:
                nextcell.remove(prev)
            if nextcell == [] or nextcell == None:
                if currcell in tempBnd:
                    tempBnd.remove(currcell)
                if prev in tempBnd:
                    tempBnd.remove(prev)
                prev = []
                if len(tempBnd) > 0:
                    currcell = tempBnd[0]
                else:
                    break
                
            elif len(nextcell) >= 1:
                pairPts.append([currcell,nextcell[0]])
                tempBnd.remove(nextcell[0])
                boundary[nextcell[0][0]][nextcell[0][1]] = nodata
                prev = currcell
                currcell = nextcell[0]
        #print pairPts
        #print len(pairPts)
        for pts in pairPts:
            for pt in pts:
                if shoulderpts[pt[0]][pt[1]] != nodata:
                    tempBnd.append(pt)
                else:
                    row,col = downstream_index(flowdir[pt[0]][pt[1]], pt[0],pt[1])
                    if row < 0 or row >= nrows or col < 0 or col >= ncols:
                        tempBnd.append(pt)
                    elif shoulderpts[row][col] != nodata:
                        tempBnd.append(pt)
                    else:
                        tempBnd.append([row,col])
                        pairPts[pairPts.index(pts)][pts.index(pt)] = [row,col]
                        changed = changed + 1
        #print pairPts
        for pts in pairPts:
            #print InterpLine(pts[0],pts[1])
            tempBnd.extend(InterpLine(pts[0],pts[1]))
        uniqueIdxs = []
        for idx in tempBnd:
            if idx not in uniqueIdxs:
                uniqueIdxs.append(idx)
        tempBnd = []
        tempBnd.extend(uniqueIdxs)

        for pt in tempBnd:
            row,col = pt
            if row >= 0 and row < nrows and col >= 0 and col < ncols:
                boundary[row][col] = 1
            else:
                tempBnd.remove(pt)
        #print tempBnd
        #WriteAscFile(r'E:\MasterBNU\RillMorphology\20150130\2Rill\SnakeICC0.asc', boundary,ncols,nrows,geotrans,-9999) 
        ## to avoid boundary grid break, first use thin tool of ArcGIS
        boundary = thin(boundary,geotrans,tempdir)
        ## end declaration
        #WriteAscFile(r'E:\MasterBNU\RillMorphology\20150130\2Rill\SnakeICC1.asc', boundary,ncols,nrows,geotrans,-9999) 
        num,boundary = simplifyBoundary(boundary,nodata,geotrans)
        #WriteAscFile(r'E:\MasterBNU\RillMorphology\20150130\2Rill\SnakeICC2.asc', boundary,ncols,nrows,geotrans,-9999)
        #print num
        count = 0
        while num != 0 and count < 3:
            num,boundary = simplifyBoundary(boundary,nodata,geotrans)
            count = count + 1
        iterate = iterate + 1
        ascName = "SnakeICC"+str(iterate)+".asc"
        print "iterate time: %s, Changed num: %s" % (str(iterate),str(changed))
        WriteAscFile(r'E:\MasterBNU\RillMorphology\20150130\2Rill' + os.sep + ascName , boundary,ncols,nrows,geotrans,-9999)
    return boundary
def MakePairs(fstpt,interpPt):
    tempseq = copy.copy(interpPt)
    #print tempseq
    pairPts = []
    prev = []
    currcell = fstpt
    while len(tempseq) > 0:
        nextcell = []
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                di = currcell[0] + i
                dj = currcell[1] + j
                if [di,dj] != currcell and [di,dj] in tempseq:
                    nextcell.append([di,dj])
        if nextcell != [] and prev != [] and prev in nextcell:
            nextcell.remove(prev)
        if nextcell == [] or nextcell == None:
            if currcell in tempseq:
                tempseq.remove(currcell)
            if prev in tempseq:
                tempseq.remove(prev)
            prev = []
            if len(tempseq) > 0:
                currcell = tempseq[0]
            else:
                break
        elif len(nextcell) >= 1:
            pairPts.append([currcell,nextcell[0]])
            prev = currcell
            currcell = nextcell[0]
    return pairPts
def isSurrounded(pt,shoulderpts,nodata):
    count = 0
    nrows,ncols = shoulderpts.shape
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            di = pt[0]+i
            dj = pt[1]+j
            if dj >=0 and di >= 0 and di < nrows and dj < ncols:
                if shoulderpts[di][dj] != nodata:
                    count = count + 1
    if count > 0:
        return True
    else:
        return False
    
def SnakeCreep2(boundary,shoulderpts,flowdir,nodata,MaxIterate,geotrans,tempdir):
    iterate = 0
    changed = 9999
    nrows,ncols = boundary.shape
    ## Initialize the point-pairs
    bndIdx = []
    for i in range(nrows):
        for j in range(ncols):
            if boundary[i][j] != nodata:
                #print i,j
                bndIdx.append([i,j])
    changed = 0
    tempBnd = []
    tempBnd.extend(bndIdx)
    pairPts = []
    prev = []
    currcell = tempBnd[0]
    nextcell = []
    while len(tempBnd) > 0:
        nextcell = NearCells(boundary,nodata,currcell[0],currcell[1])
        if nextcell != [] and currcell in nextcell:
            nextcell.remove(currcell)
        if nextcell != [] and prev != [] and prev in nextcell:
            nextcell.remove(prev)
        if nextcell == [] or nextcell == None:
            if currcell in tempBnd:
                tempBnd.remove(currcell)
            if prev in tempBnd:
                tempBnd.remove(prev)
            prev = []
            if len(tempBnd) > 0:
                currcell = tempBnd[0]
            else:
                break
            
        elif len(nextcell) >= 1:
            pairPts.append([currcell,nextcell[0]])
            tempBnd.remove(nextcell[0])
            boundary[nextcell[0][0]][nextcell[0][1]] = nodata
            prev = currcell
            currcell = nextcell[0]
        #print pairPts
        #print len(pairPts)
    ## boundary is all nodata
    while iterate < MaxIterate or changed == 0:
        changed = 0
        tempBoundary = numpy.ones((nrows,ncols))
        tempBoundary = tempBoundary * -9999
        for pts in pairPts:
            for pt in pts:
                if shoulderpts[pt[0]][pt[1]] == nodata and (not isSurrounded(pt,shoulderpts,nodata)):
                    row,col = downstream_index(flowdir[pt[0]][pt[1]], pt[0],pt[1])
                    if row >= 0 and row < nrows and col >= 0 and col < ncols:
                        if shoulderpts[row][col] == nodata:
                            pairPts[pairPts.index(pts)][pts.index(pt)] = [row,col]
                            changed = changed + 1
        temppairPts = []
        for pts in pairPts:
            if pts[0] != pts[1]:
                interpPt = InterpLine(pts[0],pts[1])
                interpPt.append(pts[1])
                temppair = MakePairs(pts[0],interpPt)
                temppairPts.extend(temppair)
        uniqueIdxs = []
        for idx in temppairPts:
            if idx not in uniqueIdxs:
                uniqueIdxs.append(idx)
        pairPts = copy.copy(uniqueIdxs)
        
        for pts in pairPts:
            for pt in pts:
                row,col = pt
                if row >= 0 and row < nrows and col >= 0 and col < ncols:
                    tempBoundary[row][col] = 1
        iterate = iterate + 1
        ascName = "SnakeICC"+str(iterate)+".asc"
        print "iterate time: %s, Changed num: %s, Points pairs num: %s" % (str(iterate),str(changed),str(len(pairPts)))
        WriteAscFile(r'E:\MasterBNU\RillMorphology\20150130\2Rill' + os.sep + ascName , tempBoundary,ncols,nrows,geotrans,-9999)
        boundary = numpy.copy(tempBoundary)
    return boundary

def RillShoulder(BasinFile,FlowDir,ShoulderPts,tempDir,ShoulderFile):
    UniqueBasinId = GetUniqueValues(BasinFile)
    print UniqueBasinId
    for BsnID in UniqueBasinId:
        tempBsnID = []
        tempBsnID.append(BsnID)
        BsnASC = tempDir + os.sep + "BsnID" + str(BsnID) + ".asc"
        ExtractBasinBoundary(BasinFile,tempBsnID,BsnASC)
        ShldASC = tempDir + os.sep + "Shld" + str(BsnID) + ".asc"
        RillShoulderSegement(BsnASC,FlowDir,ShoulderPts,ShldASC)
def Rectangle(row,col,side):
    GridIdxs = []
    if side/2 >= 1:
        for crow in range(row - side/2, row + side/2 + 1):
            for ccol in range(col - side/2, col + side/2 + 1):
                GridIdxs.append([crow,ccol])
    else:
        GridIdxs.append([row,col])
    return GridIdxs

def SnakeICC(RealrillFile1Final,side,BndPtsIdxFile,BndCellFile,SnakeICCFile):
    bndcells = ReadRaster(BndCellFile).data
    rillcells = ReadRaster(RealrillFile1Final).data
    nrows,ncols = bndcells.shape
    nodata = ReadRaster(BndCellFile).noDataValue
    geotrans = ReadRaster(BndCellFile).geotrans
    
    snakeicc = numpy.ones((nrows,ncols))
    snakeicc = snakeicc * -9999
#    for line in open(BndPtsIdxFile):
#        bnds = eval(line)
#        uniBnd = bnds[0]
#        for bnd in bnds:
#            if bnd[0] <= uniBnd[0] and bnd[1] <= uniBnd[1]:
#                uniBnd = bnd                
#        snakeicc[uniBnd[0]][uniBnd[1]] = 1
    for i in range(nrows):
        for j in range(ncols):
            if rillcells[i][j] != nodata:
                Idxs = Rectangle(i,j,side)
                for idx in Idxs:
                    crow,ccol = idx
                    if not(crow < 0 or crow >= nrows or ccol < 0 or ccol >= ncols ):
                        snakeicc[crow][ccol] = 1
    snakeicc = ExtractBoundary(snakeicc,nodata)
    WriteAscFile(SnakeICCFile, snakeicc,ncols,nrows,geotrans,-9999) 
