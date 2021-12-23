# Blender Batch Export
Allows you to export multiple meshes in a blend file to separate files in one click. Supports: **DAE, USD, PLY, STL, FBX, glTF, OBJ, X3D**

It can be found in a few differnet places such as the **Top Bar** (by File, Edit, Render, Window, Help), the **3D Viewport Header** (next to View, Select, Add...), or the **3D Viewport Side Bar Export Tab**. You can set where to show it in the **Addon Location setting under Edit > Preferences > Add-ons > Batch Export > Preferences**.

<img src="https://user-images.githubusercontent.com/65431647/147272597-7ed290c6-51b4-4afa-a8ee-ee4661330825.png" height="400"/> <img src="https://user-images.githubusercontent.com/65431647/147272883-0c8c10d7-062f-4737-8522-55a3c51c5c50.png" height="400"/>



## Instructions:
Batch Export button: Press after everything is set up to export your meshes to seperate files.

### Files:
**Directory:** Which folder to export all the files to, the default of // means to export to the same folder this blend file is in.

**Prefix:** Allows you add some text before the rest of the exported file name (which is the name of the object). For example putting "OldHouse_" here could get you names like "OldHouse_FrontDoor" and "OldHouse_Roof". Another example is for naming conventions, such as putting "sm_" before all static meshes in Unreal Engine.

**Suffix:** The same as prefix, but after the rest of the file name.

### Export Settings:
Export settings are stored in each scene. You can create your own default settings by opening a new file, choosing the settings you want as default, and pressing File > Defaults > Save Startup File.

**Format:** Which file format to export to, supports: **DAE, USD, PLY, STL, FBX, glTF, OBJ, X3D**

**Mode:** Three different modes for deciding what goes in which file:
* **Objects:** Export each object to a seperate file.
* **Objects by Parents:** Export each object to a seperate file, except for child objects which will be put in the same file as their parents.
* **Collections:** Export each collection to a seperate file.

**Limit to:** Limit either to all visible objects, or all selected objects.

**Apply Modifiers:** Should modifiers be applied to the exported meshes? Warning: Having this on prevents shape keys from exporting.

Formats also have format-specific options. DAE, FBX, glTF, OBJ, and X3D can choose a preset (created in export options from the normal File > Export > File Format menus), which can be used to set more specific settings.

### Object Types:
Choose which object types to export. WARNING: Blender doesn't support exporting all types to all formats, so if Blender's exporter for that format doesn't support an object type selected here, you may end up with empty files.

### Transform:
**Set Location:** If on it will move the location each object to these coordinates, for example if all your objects are placed side by side, you can export them all centered out by using the coordinates (0, 0, 0).

**Set Rotation:** Set the rotation of each object on export. This can be used to reset their rotations, or if the exported models are rotated wrong when imported to another software such as a game engine, you can use this to cancel that out.

**Set Scale:** Set the scale of each object on export. Use this to reset everything's scale, or to export everything scaled up or down.
