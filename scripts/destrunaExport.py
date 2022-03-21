#Destruna Export Script 1.0
from maya import cmds as mc
import shutil 
import os
import re
import importlib
from re import search
from os import listdir, path
from os.path import isfile, join



#main export function
def export(*args):
    print("Beginning export")
    cacheDir = mc.textFieldGrp('cacheDir', q=1, tx = 1)
    passCnt = int(mc.textField('cachePass', q=1, text=1))
    #checks if cache directory has been defined by user if not displays error
    if cacheDir != "":
        #modifies path to follow Destruna structure
        cachePass = os.path.join(cacheDir, "_forTransport", "sceneCache", "pass" + str(passCnt))
        print("Caching to " + cacheDir + ", pass count is " + str(passCnt))
    else:
        mc.error("Cache directory not defined please choose a location")
    #checks rig mode export, by default its always "All Rigs" or 1
    rigMode = mc.radioButtonGrp(cachingUI.rigList, q=True, select = 1)
    if rigMode == 1:
        exportList = refreshRigList.rigGeoGrps
    if rigMode == 2:
        exportList = getSelected.exportList
        if exportList is None:
            mc.error("No rigs selected for export")
    #list relatives twice to get geoShapes.
    geoNames = mc.listRelatives(exportList)
    #check if export list is empty, if something continue else error
    if not geoNames:
        mc.error("No rigs detected. Please add a rig and refresh the list")
    geoNames = mc.listRelatives(geoNames, typ = "mesh")
    #getting the relatives of geo includes the origShape which on our rigs has no animation so best to filter it out
    geoNames = list(filter(lambda k: "geoShapeOrig" not in k, geoNames))
    #remove anything thats not the geoShape eg polysurfaces or objects that dont follow the naming convention by having "_geo" at the end
    geoNames = list(filter(lambda k: "geoShape" in k, geoNames))
    #prompt user if cache pass is present if they want to overwrite it
    if path.exists(cachePass) == 1:
        confirmOverwrite = mc.confirmDialog( title='Confirm', message= "Pass " + str(passCnt) + " exists. Overwrite it?", button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if confirmOverwrite != "No":
            exportPC2(cachePass, passCnt, geoNames, exportList)
            organiseExportPC2(cachePass, exportList, geoNames)
            print("Rigs cached")
        else:
            print("Export canceled")
    else:
        #if cache pass isnt present execute export anyway
        exportPC2(cachePass, passCnt, geoNames, exportList)
        organiseExportPC2(cachePass, exportList, geoNames) 
        print("Rigs cached")
    print("Export complete")

#exports a .pc2 file of the rigs
def exportPC2(cachePass, passCnt, geoNames, exportList):
    objectsToProcess = len(exportList)
    print("Starting rig caching...")
    print("rigs to cache " + str(objectsToProcess))
    print("Caching scene...")
    #runs frameRange() to get frame range info from UI
    frameRange()
    frameMin = frameRange.start
    frameMax = frameRange.end
    if frameRange.frameMode ==1:
        print("Caching current frame: " + str(int(frameMin)))
    else:
        print("Caching frames " + str(int(frameMin)) + " to " + str(int(frameMax)))
    #Uses Mayas inbuilt cache command to export a mcx file for each geo in the Geometry grp of a rig
    mc.cacheFile(st=frameMin, et=frameMax, points= geoNames, dir = cachePass, fm = "OneFile", cacheFormat = "mcx")
    #list cached files, filter for .mcx. pc2 files can only be made from .mcx or .mcc
    cachedFiles = [f for f in listdir(cachePass) if isfile(join(cachePass, f))]
    cacheFilesFiltered = list(filter(lambda k: ".mcx" in k, cachedFiles))
    for file in cacheFilesFiltered:
        pc2File = os.path.join(cachePass,os.path.dirname('.')) + file.replace("mcx", "pc2") 
        print(pc2File)
        mc.cacheFile(pc2=0, f = file , pcf = pc2File, dir = os.path.join(cachePass,os.path.dirname('.')))
    #remove files that aren't .pc2. Maybe infuture keep these and use them in maya for previews.
    cacheFilesDel = filter(lambda k: ".pc2" not in k, cachedFiles)
    for rem in cacheFilesDel:
        os.remove(os.path.join(cachePass,os.path.dirname('.')) + rem)

#from the exported pc2 files organise into folders and clean up names
def organiseExportPC2(cachePass,exportList,geoNames):
    #Determine what file belongs to what cache, move file to associated cache folder and clean up file name
    for export in exportList:
        #make list of geo filter for anything not a mesh and for geoShapeOrig
        list = mc.listRelatives(export)
        list = mc.listRelatives(list, typ = "mesh")
        list = filter(lambda k: "geoShapeOrig" not in k, list)
        print("Organising " + export)
        #add .pc2 to everything in list
        list = [s + ".pc2" for s in list]
        itemsExport = []
        #replace : with _ in list
        for s in list:
            replace = s.replace(":", "_")
            itemsExport.append(replace)
        #determine if cache file from a duplicate rig or first rig, create folder for rig    
        namespace = export.rpartition(':')[0]
        namespaceNum = re.search('[0-9]+$', namespace) or ""
        rigName = export.rpartition(':')[2]
        if namespaceNum != "":
            namespaceNum = namespaceNum.group()
            print("Duplicate geometry, assigning cache number " + namespaceNum)
        else: 
            namespaceNum = "0"
            print("Original geometry, assigning cache number " + namespaceNum)
        #creates folders based off the rig name and its namespace number. For ease of reading in the rig structure the name should always be in the Geometry grp eg koGeometry instead of just Geometry.
        rigFolder = os.path.join(os.path.join(cachePass,os.path.dirname('.')), rigName.replace("Geometry", "Cache") + namespaceNum)
        if (path.exists(rigFolder)) != 1:
            print("Creating " + rigName.replace("Geometry", "Cache") + namespaceNum + " folder")
            os.makedirs(rigFolder) 
        #move files to correct folders. Clean up file names
        for move in itemsExport:
            fileRenamed = move.replace(namespace + "_", "")
            fileRenamed = fileRenamed.replace("geoShape", "geo")
            src = os.path.join(cachePass,os.path.dirname('.')) + move
            dst = os.path.join(rigFolder,os.path.dirname('.')) + fileRenamed
            shutil.move(src,dst)
        print("Rig done")
        

        
#Creates the default path for caches to be placed in. Follows animScene/_forTransport/cache/
def defaultCacheDir(*args):
    cacheDir = mc.file(q=True, sn=True)
    fileName = os.path.basename(cacheDir)
    cacheDir = cacheDir.replace(fileName, '')
    defaultCacheDir.dir =  cacheDir.replace(fileName, '')
    mc.textFieldGrp('cacheDir', e=1, tx = defaultCacheDir.dir)
    export.path = defaultCacheDir.dir

#Opens file dialog for cache browsing. Replaces path. Adds
def browseCacheDir(*args):
    #seems to be a bug with only listing directories mode includes maya files?
    directory = mc.fileDialog2(fm = 3, dir = defaultCacheDir.dir, ff = "") or defaultCacheDir.dir
    browseCacheDir.dir = ''.join(directory) + "/"
    mc.textFieldGrp('cacheDir', e=1, tx = browseCacheDir.dir)
    export.path = defaultCacheDir.dir

#determines what frame range to use from cachingUI and controls UI logic
def frameRange(*args):
    frameRange.frameMode  = mc.radioButtonGrp( 'frameRangeMode',q=1, select=1)
    if frameRange.frameMode ==1:
        frameRange.start = mc.currentTime( query=True )
        frameRange.end = mc.currentTime( query=True ) 
        frameRange.end += 1 #need 1 so the delta between frames is >1 if delta <1 cache wont start. Delta here is 1 hence 1 frame is cached
        mc.intFieldGrp(cachingUI.startEnd, e=True, en = 0)  
    if frameRange.frameMode ==2:
        frameRange.start = mc.playbackOptions(q=1, minTime=1 )
        frameRange.end = mc.playbackOptions(q=1, maxTime=1 )
        mc.intFieldGrp(cachingUI.startEnd, e=True, en = 0)  
    if frameRange.frameMode ==3:
        frameRange.start = mc.intFieldGrp('startEnd',  q=1,value1=1)
        frameRange.end = mc.intFieldGrp('startEnd',  q=1,value2=1)
        mc.intFieldGrp(cachingUI.startEnd, e=True, en = 1)
        
#increments the cache pass up        
def cachePassUp(*args):
    cachePass = int(mc.textField('cachePass', q=1, text=1))
    cachePass += 1
    mc.textField('cachePass', e=1, text=str(cachePass))
    
#increments the cache pass down    
def cachePassDown(*args):
    cachePass = int(mc.textField('cachePass', q=1, text=1))
    cachePass -= 1
    if cachePass > 0:
        mc.textField('cachePass', e=1, text=str(cachePass))
    else:
        mc.warning( "Can't have a cache pass less then 0" )

def getSelected(*args):
    getSelected.exportList = mc.textScrollList(cachingUI.rigSelect, q=1, si=1)

#determine rig selection logic
def rigSelMode(*args): 
    rigMode = mc.radioButtonGrp(cachingUI.rigList, q=True, select = 1)
    if rigMode == 1:
        mc.textScrollList(cachingUI.rigSelect, edit=True, en = 0)
        
    if rigMode == 2:
        mc.textScrollList(cachingUI.rigSelect, edit=True, en = 1)
        getSelected()
        
#update list of items to choose from 
def refreshRigList(*args):  
    listRefs = mc.ls(rn=1)
    refTransGrps = mc.listRelatives(listRefs, type='transform') or "" #find grps in transforms
    rigGeoGrps = list(filter(lambda k: "Geometry" in k, refTransGrps))  #find 'Geometry' in grps
    rigsToProcess = len(rigGeoGrps)
    mc.textScrollList(cachingUI.rigSelect, edit=1, ra=1) #need to clear list before adding items in list again
    if rigsToProcess == 0:
        mc.textScrollList(cachingUI.rigSelect, edit=1, numberOfRows=1, append=["No rigs found please add a rig and refresh list"])
        refreshRigList.rigGeoGrps = []

    else:
        mc.textScrollList(cachingUI.rigSelect, edit=1, numberOfRows=rigsToProcess, append=rigGeoGrps)
        refreshRigList.rigGeoGrps = rigGeoGrps

#ui window    
def cachingUI():
    cachingUI.cacheUIWindow = 'cacheUIWindow'
    if mc.window(cachingUI.cacheUIWindow, exists=1):
        mc.deleteUI( cachingUI.cacheUIWindow , window=True )
    if mc.windowPref(cachingUI.cacheUIWindow, exists=1):
        mc.windowPref( cachingUI.cacheUIWindow, remove=True )
    cacheUIWindow = mc.window(cachingUI.cacheUIWindow,menuBar=True, title="Export To Blender", w=600)
    #expanding buttons in bottom of UI to mimic alembic UI
    form = mc.formLayout(numberOfDivisions=100)
    #bottom Three Buttons. Alignment handled by formLayout
    exportButton = mc.button(label='Export', command = export)
    cancelButton = mc.button(label='Cancel', command = closeUI)
    masterCol = mc.columnLayout(adj = 1) #master column for layout, adj allows it to expand to fit formLayout
    
    #---Cache Options---
    cacheOpts = mc.frameLayout( label='Cache Options', labelAlign='left', collapsable=True, cll=True, p = masterCol)
    #cache directory row
    mc.rowLayout( numberOfColumns=3, adj=1, cw3=[300,20,50], ct3=['both','both','left'])
    mc.textFieldGrp('cacheDir', label='Cache Directory:', w=300, tx = "", adj = 2, fi = 1)
    defaultCacheDir()
    mc.symbolButton(image='navButtonBrowse.png', command = browseCacheDir)
    mc.separator(st='none', w=5)
    #cache pass row
    mc.setParent( '..' )
    mc.rowLayout( numberOfColumns=4, cw4=[140,50,20,20], ct4=['right','both','both','both'])
    mc.text(label = 'Cache pass:')
    mc.textField('cachePass', text = "1", ed = 0)
    #mc.intFieldGrp('cachePass', numberOfFields=1, label='Cache pass:', value1=1, en=0)
    mc.symbolButton('cachePassUp', image='moveUVUp.png', command = cachePassUp)
    mc.symbolButton('cachePassDown', image='moveUVDown.png', command = cachePassDown)
    mc.setParent( '..' )
    
    #---Frame Range Options---
    frameOpts = mc.frameLayout( label='Frame Range', labelAlign='left', collapsable=True, cll=True, p = masterCol)
    frameRangeMode = mc.radioButtonGrp('frameRangeMode', label='Cache time range: ', labelArray3=['Current Frame', 'Time Slider', 'Start/End'], numberOfRadioButtons=3, vr=1, select=2, changeCommand = frameRange)
    cachingUI.startEnd = mc.intFieldGrp('startEnd', numberOfFields=2, label='Start/End', value1=1, value2=120, en=0) #values set to 1 and 120 as they are default in Maya
    mc.setParent( '..' )

    #---Rig Options---
    refOpts = mc.frameLayout( label='Rigs', labelAlign='left', collapsable=True, cll=True, p = masterCol)
    cachingUI.rigList = mc.radioButtonGrp(label='Rig Choice: ', labelArray2=['All Rigs', 'Selected rigs'], numberOfRadioButtons=2, vr=1, select=1, en = 1, changeCommand = rigSelMode)
    mc.rowLayout(adj=1, numberOfColumns=3, cw3=[100,100,25], ct3=['left','right','right'])
    mc.text( label='Rig List:', align='left' )
    mc.text( label='Refresh List', align='left' )
    mc.symbolButton('refreshReferences', image='refresh.png', command = refreshRigList)
    mc.setParent( '..' )
    cachingUI.rigSelect = mc.textScrollList(en=0, numberOfRows=1, allowMultiSelection=True, sc = getSelected, p=refOpts) #on selection calls selection function and stores the selected rigs
    refreshRigList()#executed once to populate rig list on load
    
    #---Bottom Buttons--
    mc.formLayout(form, edit=True, 
                    attachForm=[(exportButton, "bottom", 5),
                                (exportButton, "left", 5), 
                                (cancelButton, "bottom", 5),
                                (cancelButton, "right", 5),                               
                                (masterCol, "right", 5)],
                    attachPosition=[(exportButton, "right", 5, 50), 
                                (cancelButton, "left", 5, 50),
                                (masterCol, "left", 5, 0)], 
                    attachNone=[(exportButton, "top"),
                                (cancelButton, "top")])

    mc.showWindow(cacheUIWindow)

def closeUI(*args):
    mc.deleteUI(cachingUI.cacheUIWindow, window=1)

#excute UI on script load with security check
if __name__=='__main__':
    cachingUI()

  


