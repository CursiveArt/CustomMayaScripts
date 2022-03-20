
#Destruna tools version 1.3


from maya import cmds
import webbrowser
import os

# Get location of Maya environment variable
env = os.getenv("DESTRUNA")
# Store correct file structure for checking later
crtStru = "masterAssets_forRef"

def loadRef():

    # Filters file according to format or shows all the files
    multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    filepath = cmds.fileDialog2(fileFilter=multipleFilters, dialogStyle=2, fileMode=1, caption="Reference")

    # If statement to query if filepath variable returns a string, and loads the file selected if it does
    if filepath:
    # convert filedialog2 from list to string, strip path and extension from filename
        filename = ' '.join(filepath)
        filenameExt = os.path.basename(filename)
        filename=os.path.splitext(filenameExt)[0]
        # Changes reference file path to use env variable and adds namespace to reference
        for f in filepath:
            pathname = f.replace(env, '$DESTRUNA')
            cmds.file(pathname, reference=True, namespace=filename)
            print(pathname)
            if crtStru not in pathname:
                cmds.confirmDialog(t= 'Reference Warning',m= filenameExt + ' is not in the masterAssets_forRef folder and should be moved there as soon as possible')
            print(filenameExt + ' referenced successfully')
    # If filepath variable returns a None or empty the message is displayed
    else:
        print('No file selected.')
        
def delRef():
    # Gets selected objects
     selected = cmds.ls(sl=True,long=True) or []
    # Checks for any selection. if not cancled operation
     if not selected:
        print('Nothing selected. Operation Canceled')
     else:
        delList =[]
        # Creates a list of references to delete for our dialog window. list is converted to string with \n added a line break between each reference
        for refExt in selected:
            refList = cmds.referenceQuery(refExt, f=True, shn=True)
            print(refList + ' marked for delection')
            delList.append(refList)
        delList = '\n'.join(delList)
        
    # Warning window asking user to confirm deletion and that it's not a undoable operation
        refDelConfirm = cmds.confirmDialog(t= 'WARNING', m= 'References selected for deletion:' + '\n' + delList + '\n' + "Deleting a reference can't be undone please confirm", button=['Confirm','Cancel'], defaultButton='Confirm', cancelButton='Cancel', dismissString='Cancel')
    # Iterates over list removing each reference
    # ReferenceQuery file commands can only handle one Query at a time hence the for loop
        if refDelConfirm == 'Confirm':
            for refDel in selected:
                ref_name = cmds.referenceQuery(refDel, f=True, shn=True)
                file = cmds.referenceQuery(refDel, f=True)
                cmds.file(file, rr=True)
                print(ref_name + ' removed successfully')
        else:
            print('Reference delection canceled')
       

def checkFile():
    # Selects the reference in the scene
    ref_node = cmds.ls('*RN*', type="reference", r=True)
    if not ref_node:
        cmds.warning('No references in scene. Operation canceled')
    else:
        refList = []
        # This will change the reference filepath if reference is in the scene
        for ref in ref_node:
            if cmds.referenceQuery(ref, isLoaded=True):
                ref_path = cmds.referenceQuery(ref, f=True, un=True)
                ref_name = cmds.referenceQuery(ref, f=True, shn=True)
                # Breaks the loop if the correct env variable is detected in the filename (ref_path) and reports its correct
                if '$DESTRUNA' in ref_path:
                    print('File path contains $Destruna and is correct for ' + ref_name)
                elif crtStru not in ref_path:
                # Dialog warning for assets not being in correct structure
                    cmds.warning(ref_name + ' has incorrect folder structure missing ' + '"' + crtStru + '". Path not updated.')
                    refList.append(ref_name)
                else:
                    # Replaces the contents of the env variable with $Destruna and reports the old path the new path and a reminder
                    new_path = ref_path.replace(env, '$DESTRUNA')
                    cmds.file(new_path, loadReference=ref)
                    print('File path for ' + ref_name + ' has been updated')
                    print('New path is - ' + new_path)
                    print('Old path was - ' + ref_path)
                    print('In future please use the provided self tool to create your reference :)')
        # Makes a pop up window if assets not in the folder structure are found
        if not refList:
            print("All files are in the masterAssets_forRef folder!")
        else:
            refList = '\n'.join(refList)
            cmds.confirmDialog(t= 'Reference Warning',m= 'The following references have errors:' + '\n' + refList + '\n\n' + "These references aren't in the " + '"' + crtStru + '" folder and should be moved there or deleted as soon as possible. Paths have remained unchanged.')
                
                
def theButton():
    # Don't spoil it you must find the button in maya :)
    url = 'https://imgur.com/a/xaXYxjO'
    webbrowser.open_new_tab(url)
    