# Blender Batch Export
Allows you to export multiple meshes in a blend file to separate files in one click.

Found in right side panel of the 3d viewport under the Export tab.

## Instructions:
Batch Export button: Press after everything is set up to export your meshes to seperate files.

### Files:
**Directory:** Which folder to export all the files to, the default of // means to export to the same folder this blend file is in.

**Prefix:** Allows you add some text before the rest of the exported file name (which is the name of the object). For example putting "OldHouse_" here could get you names like "OldHouse_FrontDoor" and "OldHouse_Roof". Another example is for naming conventions, such as putting "sm_" before all static meshes in Unreal Engine.

**Suffix:** The same as prefix, but after the rest of the file name.

### Export Settings:
**Format:** Which file format to export to, supports: **DAE, USD, PLY, STL, FBX, glTF, OBJ, X3D**

**Mode:** Three different modes for deciding what goes in which file:
* **Objects:** Export each object to a seperate file.
* **Objects by Parents:** Export each object to a seperate file, except for child objects which will be put in the same file as their parents.
* **Collections:** Export each collection to a seperate file.

**Limit to:** Limit either to all visible objects, or all selected objects.

**Apply Modifiers:** Should modifiers be applied to the exported meshes? Warning: Having this on prevents shape keys from exporting.

There may also be some format specific settings shown at the end of the Export Settings category.

### Transform:
**Set Location:** If on it will move the location each object to these coordinates, for example if all your objects are placed side by side, you can export them all centered out by using the coordinates (0, 0, 0).

**Set Rotation:** Set the rotation of each object on export. This can be used to reset their rotations, or if the exported models are rotated wrong when imported to another software such as a game engine, you can use this to cancel that out.

**Set Scale:** Set the scale of each object on export. Use this to reset everything's scale, or to export everything scaled up or down.
