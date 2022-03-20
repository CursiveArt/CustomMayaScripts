# Custom Maya Scripts For Destruna
## Referencing script
A referencing script that handles deletion and creation of references. Reason we needed a custom tool for this was to create maya references with an enviroment variable in the file path so we could get around the issue with having different drive letters from overseas staff to our in-house structure. An example of this is that MacOS referes to drives as volumes where as windows refereces to them as a letter. By having employees set up an enviroment variable as $DESTRUNA that pointed to the location of the productions assets we could ensure the scene file would work on both in-house and overseas computers.

## Exporting script
This script handles the exporting of 3D models to .mcx and then converts it to .pc2 files. While initally the production on Destruna was exported with Alembic from Maya to Blender to mostly great success we wanted to try .pc2 files instead because all we needed was the vertex deformations and none of the uv data or other attributes on the vertexs and we also had some strange issues with creasing not being applied correctly on render in Blender with a alembic cache. This export script was the first script written as a proof of concept of this exporting method. 

The script features a fully functional UI that replicated the Alebmic exporter from Maya (to make the tool feel familiar), options inside of the tool to determine what rig was being exported or to just bulk export all rigs in the scene, auto file path making that was determined by the animation scenes location ensuring the export followed correct folder structure.

The process of the script when the export script is executed is as follows
1. Check what export options selected
2. Export .mcx files to "_forTransport folder" then convert to .pc2 and delete .mcx files
3. Move .pc2 files into folders that correspond to the rig that animation was exported from eg "_forTransport/Don0" or if it was a duplicate rig of the same name "_forTransport/Don1"  
