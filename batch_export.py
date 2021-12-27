import bpy
from bpy.types import AddonPreferences, PropertyGroup, Operator, Panel
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty, FloatVectorProperty
import os

bl_info = {
    "name": "Batch Export",
    "author": "MrTriPie",
    "version": (2, 0, 2),
    "blender": (3, 00, 0),
    "category": "Import-Export",
    "location": "Set in preferences below. Default: Top Bar (After File, Edit, ...Help)",
    "description": "Batch export the objects in your scene into seperate files",
    "warning": "Relies on the export add-on for the format used being enabled",
    "doc_url": "github.com/mrtripie/Blender-Batch-Export/blob/main/README.md",
    "tracker_url": "github.com/mrtripie/Blender-Batch-Export/issues",
}

preset_enum_items_refs = {}

def get_operator_presets(operator):
    presets = [("NONE", "", "", 0)]
    for d in bpy.utils.script_paths(subdir="presets/operator/" + operator):
        for f in os.listdir(d):
            if not f.endswith(".py"):
                continue
            f = os.path.splitext(f)[0]
            i = hash(f) # use a hash of the filename to be most likely unique
            # use % to limit to C short int size. Include negative sign :
            # (not sure why it has to be short int, should be long, but the number becomes inaccurate in blender)
            i = (i % 32767) * (-1 if i < 0 else 1)
            presets.append((f, f, "", i))
    preset_enum_items_refs[operator] = presets # Blender's doc warns that not keeping reference to enum props array can cause crashs and weird issues
    return presets


def load_operator_preset(operator, preset):
    options = {}
    if preset == 'NONE':
        return options

    for d in bpy.utils.script_paths(subdir="presets/operator/" + operator):
        fp = "".join([d, "/", preset, ".py"])
        if os.path.isfile(fp): # Found the preset file
            print("Using preset " + fp)
            file = open(fp, 'r')
            for line in file.readlines():
                # This assumes formatting of these files remains exactly the same
                if line.startswith("op."):
                    line = line.removeprefix("op.")
                    split = line.split(" = ")
                    key = split[0]
                    value = split[1]
                    options[key] = eval(value)
            file.close()
            return options
    # If it didn't find the preset, use empty options
    # (the preset option should look blank if the file doesn't exist anyway)
    return options


def draw_settings(self, context):
    self.layout.use_property_split = True
    self.layout.use_property_decorate = False

    settings = context.scene.batch_export
    self.layout.operator('export_mesh.batch', icon='EXPORT')

    self.layout.separator()
    col = self.layout.column(align=True)
    col.prop(settings, 'directory')
    col.prop(settings, 'prefix')
    col.prop(settings, 'suffix')

    self.layout.separator()
    col = self.layout.column(align=True)
    col.label(text="Export Settings:")
    col.prop(settings, 'file_format')
    col.prop(settings, 'mode')
    col.prop(settings, 'limit')

    self.layout.separator()
    col = self.layout.column()

    col.label(text=settings.file_format + " Settings:")
    if settings.file_format == 'DAE':
        col.prop(settings, 'dae_preset')
    elif settings.file_format == 'USD':
        col.prop(settings, 'usd_format')
    elif settings.file_format == 'PLY':
        col.prop(settings, 'ply_ascii')
    elif settings.file_format == 'STL':
        col.prop(settings, 'stl_ascii')
    elif settings.file_format == 'FBX':
        col.prop(settings, 'fbx_preset')
    elif settings.file_format == 'glTF':
        col.prop(settings, 'gltf_preset')
    elif settings.file_format == 'OBJ':
        col.prop(settings, 'obj_preset')
    elif settings.file_format == 'X3D':
        col.prop(settings, 'x3d_preset')

    if settings.file_format != 'USD':
        self.layout.prop(settings, 'apply_mods')

    self.layout.use_property_split = False
    self.layout.separator()
    self.layout.label(text="Object Types:")
    grid = self.layout.grid_flow(columns=3, align=True)
    grid.prop(settings, 'object_types')

    self.layout.separator()
    col = self.layout.column(align=True, heading="Transform:")
    col.prop(settings, 'set_location')
    if settings.set_location:
        col.prop(settings, 'location', text="")  # text is redundant
    col.prop(settings, 'set_rotation')
    if settings.set_rotation:
        col.prop(settings, 'rotation', text="")
    col.prop(settings, 'set_scale')
    if settings.set_scale:
        col.prop(settings, 'scale', text="")


def popover(self, context):
    row = self.layout.row()
    row = row.row(align=True)
    row.operator('export_mesh.batch', text='', icon='EXPORT')
    row.popover(panel='POPOVER_PT_batch_export', text='')


# Side panel (used with Side Panel option)
class VIEW3D_PT_batch_export(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Export"
    bl_label = "Batch Export"

    def draw(self, context):
        draw_settings(self, context)


# Popover panel (used on 3D Viewport Header or Top Bar option)
class POPOVER_PT_batch_export(Panel):
    bl_space_type = 'TOPBAR'
    bl_region_type = 'HEADER'
    bl_label = "Batch Export"

    def draw(self, context):
        draw_settings(self, context)


class BatchExportPreferences(AddonPreferences):
    bl_idname = __name__

    def addon_location_updated(self, context):
        bpy.types.TOPBAR_MT_editor_menus.remove(popover)
        bpy.types.VIEW3D_MT_editor_menus.remove(popover)
        if hasattr(bpy.types, "VIEW3D_PT_batch_export"):
            bpy.utils.unregister_class(VIEW3D_PT_batch_export)
        if self.addon_location == 'TOPBAR':
            bpy.types.TOPBAR_MT_editor_menus.append(popover)
        elif self.addon_location == '3DHEADER':
            bpy.types.VIEW3D_MT_editor_menus.append(popover)
        elif self.addon_location == '3DSIDE':
            bpy.utils.register_class(VIEW3D_PT_batch_export)

    addon_location: EnumProperty(
        name="Addon Location",
        description="Where to put the Batch Export Addon UI",
        items=[
            ('TOPBAR', "Top Bar", "Place on Blender's Top Bar (Next to File, Edit, Render, Window, Help)"),
            ('3DHEADER', "3D Viewport Header", "Place in the 3D Viewport Header (Next to View, Select, Add, etc.)"),
            ('3DSIDE', "3D Viewport Side Panel (Export Tab)", "Place in the 3D Viewport's right side panel, in the Export Tab"),
        ],
        update=addon_location_updated,
    )

    def draw(self, context):
        self.layout.prop(self, "addon_location")


class EXPORT_MESH_OT_batch(Operator):
    """Export many objects to seperate files all at once"""
    bl_idname = "export_mesh.batch"
    bl_label = "Batch Export"
    file_count = 0

    def execute(self, context):
        settings = context.scene.batch_export

        base_dir = settings.directory
        if not bpy.path.abspath('//'): # Then the blend file hasn't been saved
            if base_dir != bpy.path.abspath(base_dir): # Then the path should be relative
                self.report({'ERROR'}, "Save .blend file somewhere before exporting to relative directory\n(or use an absolute directory)")
                return {'FINISHED'}
        base_dir = bpy.path.abspath(base_dir) # convert to absolute path
        if not os.path.isdir(base_dir):
            self.report({'ERROR'}, "Export directory doesn't exist")
            return {'FINISHED'}

        self.file_count = 0

        view_layer = context.view_layer
        obj_active = view_layer.objects.active
        selection = context.selected_objects
        objects = view_layer.objects.values()
        if settings.limit == 'SELECTED':
            objects = selection

        mode = ''
        if obj_active:
            mode = obj_active.mode
            bpy.ops.object.mode_set(mode='OBJECT') # Only works in Object mode

        if settings.mode == 'OBJECTS':
            for obj in objects:
                if not obj.type in settings.object_types:
                    continue
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                self.export_selection(obj.name, context, base_dir)

        elif settings.mode == 'OBJECT_PARENTS':
            for obj in objects:
                if obj.parent:  # if it has a parent, skip it for now, it'll be exported when we get to its parent
                    continue
                bpy.ops.object.select_all(action='DESELECT')
                if obj.type in settings.object_types:
                    obj.select_set(True)
                self.select_children_recursive(obj, context,)
                if context.selected_objects:
                    self.export_selection(obj.name, context, base_dir)

        elif settings.mode == 'COLLECTIONS':
            for col in bpy.data.collections.values():
                bpy.ops.object.select_all(action='DESELECT')
                for obj in col.objects:
                    if not obj.type in settings.object_types:
                        continue
                    if not obj in objects:
                        continue
                    obj.select_set(True)
                if context.selected_objects:
                    self.export_selection(col.name, context, base_dir)

        # Return selection to how it was
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select_set(True)
        view_layer.objects.active = obj_active

        # Return to whatever mode the user was in
        if obj_active:
            bpy.ops.object.mode_set(mode=mode)

        if self.file_count == 0:
            self.report({'ERROR'}, "NOTHING TO EXPORT")
        else:
            self.report({'INFO'}, "Exported " + str(self.file_count) + " file(s)")

        return {'FINISHED'}

    def select_children_recursive(self, obj, context):
        for c in obj.children:
            if obj.type in context.scene.batch_export.object_types:
                c.select_set(True)
            self.select_children_recursive(c, context)

    def export_selection(self, itemname, context, base_dir):
        settings = context.scene.batch_export
        # save the transform to be reset later:
        old_locations = []
        old_rotations = []
        old_scales = []
        for obj in context.selected_objects:
            old_locations.append(obj.location.copy())
            old_rotations.append(obj.rotation_euler.copy())
            old_scales.append(obj.scale.copy())

            # If exporting by parent, don't set child (object that has a parent) transform
            if settings.mode != "OBJECT_PARENTS" or not obj.parent:
                if settings.set_location:
                    obj.location = settings.location
                if settings.set_rotation:
                    obj.rotation_euler = settings.rotation
                if settings.set_scale:
                    obj.scale = settings.scale

        # Some exporters only use the active object: #I think this isn't true anymore
        # view_layer.objects.active = obj

        prefix = settings.prefix
        suffix = settings.suffix
        name = prefix + bpy.path.clean_name(itemname) + suffix
        fp = os.path.join(base_dir, name)

        # Export
        if settings.file_format == "DAE":
            options = load_operator_preset('wm.collada_export', settings.dae_preset)
            options["filepath"] = fp
            options["selected"] = True
            options["apply_modifiers"] = settings.apply_mods
            bpy.ops.wm.collada_export(**options)

        elif settings.file_format == "USD":
            bpy.ops.wm.usd_export(
                filepath=fp+settings.usd_format, selected_objects_only=True)

        elif settings.file_format == "PLY":
            bpy.ops.export_mesh.ply(
                filepath=fp+".ply", use_ascii=settings.ply_ascii, use_selection=True, use_mesh_modifiers=settings.apply_mods)

        elif settings.file_format == "STL":
            bpy.ops.export_mesh.stl(
                filepath=fp+".stl", ascii=settings.stl_ascii, use_selection=True, use_mesh_modifiers=settings.apply_mods)

        elif settings.file_format == "FBX":
            options = load_operator_preset('export_scene.fbx', settings.fbx_preset)
            options["filepath"] = fp+".fbx"
            options["use_selection"] = True
            options["use_mesh_modifiers"] = settings.apply_mods
            bpy.ops.export_scene.fbx(**options)

        elif settings.file_format == "glTF":
            options = load_operator_preset('export_scene.gltf', settings.gltf_preset)
            options["filepath"] = fp
            options["use_selection"] = True
            options["export_apply"] = settings.apply_mods
            bpy.ops.export_scene.gltf(**options)

        elif settings.file_format == "OBJ":
            options = load_operator_preset('export_scene.obj', settings.obj_preset)
            options["filepath"] = fp+".obj"
            options["use_selection"] = True
            options["use_mesh_modifiers"] = settings.apply_mods
            bpy.ops.export_scene.obj(**options)

        elif settings.file_format == "X3D":
            options = load_operator_preset('export_scene.x3d', settings.x3d_preset)
            options["filepath"] = fp+".x3d"
            options["use_selection"] = True
            options["use_mesh_modifiers"] = settings.apply_mods
            bpy.ops.export_scene.x3d(**options)

        # Reset the transform to what it was before
        i = 0
        for obj in context.selected_objects:
            obj.location = old_locations[i]
            obj.rotation_euler = old_rotations[i]
            obj.scale = old_scales[i]
            i += 1

        print("exported: ", fp)
        self.file_count += 1


class BatchExportSettings(PropertyGroup):
    # File Settings:
    directory: StringProperty(
        name="Directory",
        description="Which folder to place the exported files\nDefault of // will export to same directory as the blend file (only works if the blend file is saved)",
        default="//",
        subtype='DIR_PATH',
    )
    prefix: StringProperty(
        name="Prefix",
        description="Text to put at the beginning of all the exported file names",
    )
    suffix: StringProperty(
        name="Suffix",
        description="Text to put at the end of all the exported file names",
    )

    # Export Settings:
    file_format: EnumProperty(
        name="Format",
        description="Which file format to export to",
        items=[
            ("DAE", "Collada (.dae)", "", 1),
            ("USD", "Universal Scene Description (.usd/.usdc/.usda)", "", 2),
            ("PLY", "Stanford (.ply)", "", 3),
            ("STL", "STL (.stl)", "", 4),
            ("FBX", "FBX (.fbx)", "", 5),
            ("glTF", "glTF (.glb/.gltf)", "", 6),
            ("OBJ", "Wavefront (.obj)", "", 7),
            ("X3D", "X3D Extensible 3D (.x3d)", "", 8),
        ],
        default="glTF",
    )
    mode: EnumProperty(
        name="Mode",
        description="What to export",
        items=[
            ("OBJECTS", "Objects", "Each object is exported to its own file", 1),
            ("OBJECT_PARENTS", "Objects by Parents",
            "Same as 'Objects', but objects that are parents have their\nchildren exported with them instead of by themselves", 2),
            ("COLLECTIONS", "Collections",
            "Each collection is exported into its own file", 3),
        ],
        default="OBJECT_PARENTS",
    )
    limit: EnumProperty(
        name="Limit to",
        description="How to limit which objects are exported",
        items=[
            ("VISIBLE", "Visible", "", 1),
            ("SELECTED", "Selected", "", 2),
        ],
    )

    # Format specific options:
    usd_format: EnumProperty(
        name="Format",
        items=[
            (".usd", "Plain (.usd)",
            "Can be either binary or ASCII\nIn Blender this exports to binary", 1),
            (".usdc", "Binary Crate (default) (.usdc)", "Binary, fast, hard to edit", 2),
            (".usda", "ASCII (.usda)", "ASCII Text, slow, easy to edit", 3),
        ],
        default=".usdc",
    )
    ply_ascii: BoolProperty(name="ASCII Format", default=False)
    stl_ascii: BoolProperty(name="ASCII Format", default=False)
    dae_preset: EnumProperty(
        name="Preset",
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > Collada (.dae))",
        items=lambda self, context : get_operator_presets('wm.collada_export'),
    )
    fbx_preset: EnumProperty(
        name="Preset",
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > FBX (.fbx))",
        items=lambda self, context : get_operator_presets('export_scene.fbx'),
    )
    gltf_preset: EnumProperty(
        name="Preset",
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > glTF (.glb/.gltf))",
        items=lambda self, context : get_operator_presets('export_scene.gltf'),
    )
    obj_preset: EnumProperty(
        name="Preset",
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > Wavefront (.obj))",
        items=lambda self, context : get_operator_presets('export_scene.obj'),
    )
    x3d_preset: EnumProperty(
        name="Preset",
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > X3D Extensible 3D (.x3d))",
        items=lambda self, context : get_operator_presets('export_scene.x3d'),
    )

    apply_mods: BoolProperty(
        name="Apply Modifiers",
        description="Should the modifiers by applied onto the exported mesh?\nCan't export Shape Keys with this on",
        default=True,
    )
    object_types: EnumProperty(
        name="Object Types",
        options={'ENUM_FLAG'},
        items=[
            ('MESH', "Mesh", "", 1),
            ('CURVE', "Curve", "", 2),
            ('SURFACE', "Surface", "", 4),
            ('META', "Metaball", "", 8),
            ('FONT', "Text", "", 16),
            # ('GPENCIL', "Grease Pencil", "", 32), # I don't think its supported by anything but SVG currently.
            ('ARMATURE', "Armature", "", 64),
            ('EMPTY', "Empty", "", 128),
            ('LIGHT', "Lamp", "", 256),
            ('CAMERA', "Camera", "", 512),
        ],
        description="Which object types to export\n(NOT ALL FORMATS WILL SUPPORT THESE)",
        default={'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE'},
        )

    # Transform:
    set_location: BoolProperty(name="Set Location", default=True)
    location: FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), subtype="TRANSLATION")
    set_rotation: BoolProperty(name="Set Rotation (XYZ Euler)", default=True)
    rotation: FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), subtype="EULER")
    set_scale: BoolProperty(name="Set Scale", default=False)
    scale: FloatVectorProperty(name="Scale", default=(1.0, 1.0, 1.0), subtype="XYZ")


def register():
    # Register classes
    bpy.utils.register_class(BatchExportPreferences)
    bpy.utils.register_class(BatchExportSettings)
    bpy.utils.register_class(POPOVER_PT_batch_export)
    bpy.utils.register_class(EXPORT_MESH_OT_batch)

    # Add batch export settings to Scene type
    bpy.types.Scene.batch_export = PointerProperty(type=BatchExportSettings)

    # Show addon UI
    prefs = bpy.context.preferences.addons[__name__].preferences
    if prefs.addon_location == 'TOPBAR':
        bpy.types.TOPBAR_MT_editor_menus.append(popover)
    if prefs.addon_location == '3DHEADER':
        bpy.types.VIEW3D_MT_editor_menus.append(popover)
    elif prefs.addon_location == '3DSIDE':
        bpy.utils.register_class(VIEW3D_PT_batch_export)


def unregister():
    # Delete the settings from Scene type (Doesn't actually remove existing ones from scenes)
    del bpy.types.Scene.batch_export

    # Unregister Classes
    bpy.utils.unregister_class(BatchExportPreferences)
    bpy.utils.unregister_class(BatchExportSettings)
    bpy.utils.unregister_class(POPOVER_PT_batch_export)
    bpy.utils.unregister_class(EXPORT_MESH_OT_batch)

    # Remove UI
    bpy.types.TOPBAR_MT_editor_menus.remove(popover)
    bpy.types.VIEW3D_MT_editor_menus.remove(popover)
    if hasattr(bpy.types, "VIEW3D_PT_batch_export"):
        bpy.utils.unregister_class(VIEW3D_PT_batch_export)


if __name__ == '__main__':
    register()
