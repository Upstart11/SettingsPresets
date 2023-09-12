import bpy
import os
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty


class SettingsPresetsPreferences(AddonPreferences):
    bl_idname = __package__.split('.')[0]

    SettingsPresetsFolder: StringProperty(
        name = "Settings Presets folder",
        subtype = 'DIR_PATH',
        description = "Folder where the imported and saved presets will be stored",
        default = os.path.normpath(os.path.dirname(bpy.utils.resource_path('USER')) + "/SettingsPresets")
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'SettingsPresetsFolder')

        