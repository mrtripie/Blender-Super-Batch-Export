# Maybe a triangulate option would be good?

import bpy
from bpy.types import AddonPreferences, Operator, Panel
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatVectorProperty
import os

bl_info = {
    "name": "Batch Export",
    "author": "MrTriPie",
    "version": (1, 0),
    "blender": (2, 91, 0),
    "category": "Import-Export",
    "location": "3D Viewport > Side Panel > Export",
    "description": "Batch export the objects in your scene into seperate files",
    "warning": "Relies on the export add-on for the format used being enabled",
    "doc_url": "",
    "tracker_url": "",
}


def export_selection(itemname, context):
    prefs = context.preferences.addons[__name__].preferences
    # save the transform to be reset later:
    old_locations = []
    old_rotations = []
    old_scales = []
    for obj in context.selected_objects:
        old_locations.append(obj.location.copy())
        old_rotations.append(obj.rotation_euler.copy())
        old_scales.append(obj.scale.copy())

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
    bpy.ops.export_scene.gltf(
        filepath=fp, use_selection=True)

    # Reset the transform to what it was before
    i = 0
    for obj in context.selected_objects:
        obj.location = old_locations[i]
        obj.rotation_euler = old_rotations[i]
        obj.scale = old_scales[i]
        i += 1

    print("written:", fp)


class BatchExportPreferences(AddonPreferences):
    bl_idname = __name__

    export_file_formats = [
        ("DAE", "Collada (.dae)", "", 1),
        ("USD", "Universal Scene Description (.usd/.usdc/.usda)", "", 2),
        ("PLY", "Stanford (.ply)", "", 3),
        ("STL", "STL (.stl)", "", 4),
        ("FBX", "FBX (.fbx)", "", 5),
        ("glTF", "glTF (.glb/.gltf)", "", 6),
        # ("glTF_B", "glTF Binary (Default) (.glb)", "", 6),
        # ("glTF_E", "glTF Embedded (.gltf)", "", 7),
        # ("glTF_S", "glTF Seperate (.gltf + .bin + textures)", "", 8),
        ("OBJ", "Wavefront (.obj)", "", 7),
    ]
    export_modes = [
        ("OBJECTS", "Objects", "Each object is exported to its own file", 1),
        ("OBJECT_PARENTS", "Objects by Parents",
         "Same as 'Objects', but objects that are parents have their\nchildren exported with them instead of by themselves", 2),
        ("COLLECTIONS", "Collections",
         "Each collection is exported into its own file", 3),
    ]
    export_limits = [
        ("NONE", "None", "", 1),
        ("VISIBLE", "Visible", "", 2),
        ("SELECTED", "Selected", "", 3),
    ]

    # Export Settings:
    file_format: EnumProperty(
        name="Format",
        items=export_file_formats,
        default="glTF",
    )
    mode: EnumProperty(
        name="Mode",
        items=export_modes,
        default="OBJECT_PARENTS",
    )
    # apply_mods: BoolProperty(
    #    name="Apply Modifiers",
    #    default=True,
    # )
    limit: EnumProperty(
        name="Limit",
        items=export_limits,
        default="VISIBLE",
    )

    # selection_only: BoolProperty(
    #     name="Selection Only",
    #     default=True,
    # )
    # visible_only: BoolProperty(
    #     name="Visible Only",
    #     default=True,
    # )

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
    bl_idname = "export_mesh.batch"  # ???????????????????????????
    bl_label = "Batch Export"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences

        view_layer = context.view_layer
        obj_active = view_layer.objects.active
        selection = context.selected_objects

        if prefs.mode == "OBJECTS":
            # for obj in selection:
            for obj in bpy.data.objects:
                # check if it is a mesh/selected/visible and continue to next
                # loop iteration if not
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                export_selection(obj.name, context)

        elif prefs.mode == "COLLECTIONS":
            for col in bpy.data.collections.values():
                bpy.ops.object.select_all(action='DESELECT')
                for obj in col.objects:
                    obj.select_set(True)
                if context.selected_objects:
                    export_selection(col.name, context)

        bpy.ops.object.select_all(action='DESELECT')
        view_layer.objects.active = obj_active
        for obj in selection:
            obj.select_set(True)

        return {'FINISHED'}


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
        prefs = context.preferences.addons[__name__].preferences
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
        # col.prop(prefs, "apply_mods")
        # col = self.layout.column(align=True, heading="Only")
        # col.use_property_split = True
        # col.prop(prefs, "selection_only", text="Selection")
        # col.prop(prefs, "visible_only", text="Visible")
        col.prop(prefs, "limit")


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
        default="//",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.batch_export_prefix = StringProperty(
        name="Prefix",
    )
    bpy.types.Scene.batch_export_suffix = StringProperty(
        name="Suffix",
    )
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    del bpy.types.Scene.batch_export_directory
    del bpy.types.Scene.batch_export_prefix
    del bpy.types.Scene.batch_export_suffix
    for cls in classes:
        bpy.utils.unregister_class(cls)


# not sure what this is used for? Was shown in the tutorial........................................................................
if __name__ == '__main__':
    register()
