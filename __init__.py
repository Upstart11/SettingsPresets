bl_info = {
    "name" : "SettingsPresets",
    "description": "An addon which allow you to import, export, save and switch between settings presets",
    "author" : "Vladislav Ciocoi",
    "blender" : (2, 90, 0),
    "version" : (1, 1, 2),
    "location": "File > Import Export",
    "category": "Import Export"
}
from bpy.app.handlers import persistent

if 'bpy' not in locals():
    import bpy
    from bpy.props import PointerProperty, IntProperty, StringProperty, CollectionProperty, BoolProperty
    from bpy.types import PropertyGroup
    from . import operators
    from . import properties
    from . import preferences
    from . import sidepanel

else:
    import imp
    imp.reload(operators)
    imp.reload(properties)
    imp.reload(preferences)
    imp.reload(sidepanel)

class ListItem(PropertyGroup):
    name: StringProperty(
    name="Name",
    description="Presets Name",
    default="NewPreset")

    prest_path: StringProperty(
    name="Path",
    description="Path to preset files",
    default="")

    icon: StringProperty(
    name="Icon",
    description="",
    default="OPTIONS")

    hasAddons: BoolProperty(
    name = 'includAddons',
    default=True,
    description="If this flag is checked the addons will be exported as well")

classes = (
    ListItem,
    properties.SP_Properties,
    preferences.SettingsPresetsPreferences,
    sidepanel.PresetsUIList,
    sidepanel.PresetsListPanel,
    operators.ListRefresh,
    operators.ExportSettings,
    operators.SaveSettings,
    operators.ApplySettings,
    operators.ImportPreset,
    operators.DeletePreset,
    operators.CancelOperator
)

@persistent
def load_handler(dummy):
    bpy.ops.list.refresh()




def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.SP_props = PointerProperty(type=properties.SP_Properties)
    bpy.types.Scene.presets_list = CollectionProperty(type = ListItem)
    bpy.types.Scene.list_index = IntProperty(name = "Index for my_list",default = 0)
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.load_factory_startup_post.append(load_handler)
    


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.SP_props
    del bpy.types.Scene.presets_list
    del bpy.types.Scene.list_index
