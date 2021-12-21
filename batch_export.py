import bpy
from bpy.types import AddonPreferences, Operator, Panel
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatVectorProperty
import os

bl_info = {
    "name": "Batch Export",
    "author": "MrTriPie",
    "version": (1, 1),
    "blender": (3, 00, 0),
    "category": "Import-Export",
    "location": "3D Viewport > Side Panel > Export",
    "description": "Batch export the objects in your scene into seperate files",
    "warning": "Relies on the export add-on for the format used being enabled",
    "doc_url": "",
    "tracker_url": "",
}


def get_operator_presets(operator):
    presets = [("NONE", "", "")]
    for d in bpy.utils.script_paths(subdir="presets\\operator\\" + operator):
        for f in os.listdir(d):
            if not f.endswith(".py"):
                continue

            presets.append((
                d + "\\" + f,
                os.path.splitext(f)[0],
                "",
            ))
    return presets


def load_operator_preset(preset):
    options = {}
    if preset == "NONE":
        return options
    file = open(preset, "r")
    for line in file.readlines():
        # This assumes formatting of these files remains exactly the same
        if line.startswith("op."):
            line = line.removeprefix("op.")
            split = line.split(" = ")
            key = split[0]
            value = split[1]

            options[key] = eval(value)
            print(options[key])
    file.close()
    return options


class BatchExportPreferences(AddonPreferences):
    bl_idname = __name__

    print(get_operator_presets("export_scene.x3d"))

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
    apply_mods: BoolProperty(
        name="Apply Modifiers",
        description="Should the modifiers by applied onto the exported mesh?\nCan't export Shape Keys with this on",
        default=True,
    )
    limit: EnumProperty(
        name="Limit to",
        description="How to limit which objects are exported",
        items=[
            ("VISIBLE", "Visible", "", 1),
            ("SELECTED", "Selected", "", 2),
        ],
        default="VISIBLE",
    )
    dae_preset: EnumProperty(
        name="Preset",
        description="Use export settings from a preset.\n(Create in the export settings from the File > Export > Collada (.dae))",
        items=lambda self, context : get_operator_presets('wm.collada_export'),
    )
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
    ply_ascii: BoolProperty(
        name="ASCII Format",
        default=False,
    )
    stl_ascii: BoolProperty(
        name="ASCII Format",
        default=False,
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
    # TODO: This should most likely be removed in favor of presets...
    gltf_format: EnumProperty(
        name="Format",
        items=[
            ("GLB", "Binary (default) (.glb)",
            "Binary format, textures packed in, fastest, hard to edit", 1),
            ("GLTF_EMBEDDED", "Embedded (.gltf)",
            "JSON text format, textures packed in, slowest but easier to edit", 2),
            ("GLTF_SEPARATE", "Seperate (.gltf + .bin + textures)",
            "Exported to multiple files, easiest to edit", 3),
        ],
        default="GLB",
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

    # Transform:
    set_location: BoolProperty(
        name="Set Location",
        default=True,
    )
    location: FloatVectorProperty(
        name="Location",
        default=(0.0, 0.0, 0.0),
        subtype="TRANSLATION",
    )
    set_rotation: BoolProperty(
        name="Set Rotation (XYZ Euler)",
        default=True,
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        default=(0.0, 0.0, 0.0),
        subtype="EULER",
    )
    set_scale: BoolProperty(
        name="Set Scale",
        default=False,
    )
    scale: FloatVectorProperty(
        name="Scale",
        default=(1.0, 1.0, 1.0),
        subtype="XYZ",
    )


class EXPORT_MESH_OT_batch(Operator):
    """Export many objects to seperate files all at once"""
    bl_idname = "export_mesh.batch"
    bl_label = "Batch Export"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences

        view_layer = context.view_layer
        obj_active = view_layer.objects.active
        selection = context.selected_objects

        objects = view_layer.objects
        if prefs.limit == "SELECTED":
            objects = selection

        if prefs.mode == "OBJECTS":
            for obj in objects:
                if obj.type != "MESH":
                    continue
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                self.export_selection(obj.name, context)

        elif prefs.mode == "OBJECT_PARENTS":
            for obj in objects:
                if obj.parent:  # if it has a parent, skip it for now, it'll be exported when we get to its parent
                    continue
                bpy.ops.object.select_all(action='DESELECT')
                if obj.type == "MESH":
                    obj.select_set(True)
                self.select_children_recursive(obj)
                if context.selected_objects:
                    self.export_selection(obj.name, context)

        elif prefs.mode == "COLLECTIONS":
            for col in bpy.data.collections.values():
                bpy.ops.object.select_all(action='DESELECT')
                for obj in col.objects:
                    if not objects.has(obj):
                        continue
                    obj.select_set(True)
                if context.selected_objects:
                    self.export_selection(col.name, context)

        bpy.ops.object.select_all(action='DESELECT')
        view_layer.objects.active = obj_active
        for obj in selection:
            obj.select_set(True)

        return {'FINISHED'}

    def select_children_recursive(self, obj):
        for c in obj.children:
            if c.type == "MESH":
                c.select_set(True)
            self.select_children_recursive(c)

    def export_selection(self, itemname, context):
        prefs = context.preferences.addons[__name__].preferences
        # save the transform to be reset later:
        old_locations = []
        old_rotations = []
        old_scales = []
        for obj in context.selected_objects:
            old_locations.append(obj.location.copy())
            old_rotations.append(obj.rotation_euler.copy())
            old_scales.append(obj.scale.copy())

            # If exporting by parent, don't set child (object that has a parent) transform
            if prefs.mode != "OBJECT_PARENTS" or not obj.parent:
                if prefs.set_location:
                    obj.location = prefs.location
                if prefs.set_rotation:
                    obj.rotation_euler = prefs.rotation
                if prefs.set_scale:
                    obj.scale = prefs.scale

        # Some exporters only use the active object: #I think this isn't true anymore
        # view_layer.objects.active = obj

        base_dir = bpy.path.abspath(context.scene.batch_export_directory)
        if not base_dir:
            raise Exception("Directory is not set")
        prefix = context.scene.batch_export_prefix
        suffix = context.scene.batch_export_suffix
        name = prefix + bpy.path.clean_name(itemname) + suffix
        fp = os.path.join(base_dir, name)

        # Export
        if prefs.file_format == "DAE":
            options = load_operator_preset(prefs.dae_preset)
            options["filepath"] = fp
            options["selected"] = True
            options["apply_modifiers"] = prefs.apply_mods
            bpy.ops.wm.collada_export(**options)

        elif prefs.file_format == "USD":
            bpy.ops.wm.usd_export(
                filepath=fp+prefs.usd_format, selected_objects_only=True)

        elif prefs.file_format == "PLY":
            bpy.ops.export_mesh.ply(
                filepath=fp+".ply", use_ascii=prefs.ply_ascii, use_selection=True, use_mesh_modifiers=prefs.apply_mods)

        elif prefs.file_format == "STL":
            bpy.ops.export_mesh.stl(
                filepath=fp+".stl", ascii=prefs.stl_ascii, use_selection=True, use_mesh_modifiers=prefs.apply_mods)

        elif prefs.file_format == "FBX":
            options = load_operator_preset(prefs.fbx_preset)
            options["filepath"] = fp+".fbx"
            options["use_selection"] = True
            options["use_mesh_modifiers"] = prefs.apply_mods
            bpy.ops.export_scene.fbx(**options)

        elif prefs.file_format == "glTF":
            options = load_operator_preset(prefs.gltf_preset)
            options["filepath"] = fp
            options["use_selection"] = True
            options["export_format"] = prefs.gltf_format
            options["export_apply"] = prefs.apply_mods
            bpy.ops.export_scene.gltf(**options)

        elif prefs.file_format == "OBJ":
            options = load_operator_preset(prefs.obj_preset)
            options["filepath"] = fp+".obj"
            options["use_selection"] = True
            options["use_mesh_modifiers"] = prefs.apply_mods
            bpy.ops.export_scene.obj(**options)

        elif prefs.file_format == "X3D":
            options = load_operator_preset(prefs.x3d_preset)
            options["filepath"] = fp+".x3d"
            options["use_selection"] = True
            options["use_mesh_modifiers"] = prefs.apply_mods
            bpy.ops.export_scene.x3d(**options)

        # Reset the transform to what it was before
        i = 0
        for obj in context.selected_objects:
            obj.location = old_locations[i]
            obj.rotation_euler = old_rotations[i]
            obj.scale = old_scales[i]
            i += 1

        print("exported: ", fp)


class VIEW3D_PT_batch_export(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Export"
    bl_label = "Batch Export"

    def draw(self, context):
        self.layout.operator('export_mesh.batch', icon='EXPORT')


class VIEW3D_PT_batch_export_files(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Export"
    bl_label = "Files"
    bl_parent_id = "VIEW3D_PT_batch_export"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene, "batch_export_directory")
        col.prop(context.scene, "batch_export_prefix")
        col.prop(context.scene, "batch_export_suffix")


class VIEW3D_PT_batch_export_export_settings(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Export"
    bl_label = "Export Settings"
    bl_parent_id = "VIEW3D_PT_batch_export"

    def draw(self, context):
        prefs = context.preferences.addons[__name__].preferences
        col = self.layout.column(align=True)
        col.prop(prefs, "file_format")
        col.prop(prefs, "mode")
        col.prop(prefs, "limit")
        if prefs.file_format == "DAE":
            col = self.layout.column(heading="DAE Settings:")
            col.prop(prefs, "dae_preset")
        elif prefs.file_format == "USD":
            col = self.layout.column(heading="USD Settings:")
            col.prop(prefs, "usd_format")
        elif prefs.file_format == "PLY":
            col = self.layout.column(heading="PLY Settings:")
            col.prop(prefs, "ply_ascii")
        elif prefs.file_format == "STL":
            col = self.layout.column(heading="STL Settings:")
            col.prop(prefs, "stl_ascii")
        elif prefs.file_format == "FBX":
            col = self.layout.column(heading="FBX Settings:")
            col.prop(prefs, "fbx_preset")
        elif prefs.file_format == "glTF":
            col = self.layout.column(heading="glTF Settings:", align=True)
            col.prop(prefs, "gltf_preset")
            # TODO: Prob remove?
            col.prop(prefs, "gltf_format")
        elif prefs.file_format == "OBJ":
            col = self.layout.column(heading="OBJ Settings:")
            col.prop(prefs, "obj_preset")
        elif prefs.file_format == "X3D":
            col = self.layout.column(heading="X3D Settings:")
            col.prop(prefs, "x3d_preset")
        if prefs.file_format != "USD":
            col = self.layout.column(align=True)
            col.prop(prefs, "apply_mods")


class VIEW3D_PT_batch_export_transform(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Export"
    bl_label = "Transform"
    bl_parent_id = "VIEW3D_PT_batch_export"

    def draw(self, context):
        prefs = context.preferences.addons[__name__].preferences
        col = self.layout.column(align=True)
        col.prop(prefs, "set_location")
        if prefs.set_location:
            col.prop(prefs, "location", text="")  # text is redundant
        col.prop(prefs, "set_rotation")
        if prefs.set_rotation:
            col.prop(prefs, "rotation", text="")
        col.prop(prefs, "set_scale")
        if prefs.set_scale:
            col.prop(prefs, "scale", text="")


classes = [
    BatchExportPreferences,
    EXPORT_MESH_OT_batch,
    VIEW3D_PT_batch_export,
    VIEW3D_PT_batch_export_files,
    VIEW3D_PT_batch_export_export_settings,
    VIEW3D_PT_batch_export_transform,
]


def register():
    bpy.types.Scene.batch_export_directory = StringProperty(
        name="Directory",
        description="Which folder to place the exported files",
        default="//",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.batch_export_prefix = StringProperty(
        name="Prefix",
        description="Text to put at the beginning of all the exported file names",
    )
    bpy.types.Scene.batch_export_suffix = StringProperty(
        name="Suffix",
        description="Text to put at the end of all the exported file names",
    )
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    del bpy.types.Scene.batch_export_directory
    del bpy.types.Scene.batch_export_prefix
    del bpy.types.Scene.batch_export_suffix
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
