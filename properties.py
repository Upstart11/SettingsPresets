from bpy.props import (BoolProperty,
                       StringProperty,
                       )

from bpy.types import PropertyGroup
    
class SP_Properties(PropertyGroup):

    includeAddons : BoolProperty(
    name = 'Include Addons',
    default=False,
    description="If this flag is checked the addons will be exported as well(If there are any)")

    includeExternalAddons : BoolProperty(
    name = 'Include Custom folder Addons',
    default=False,
    description="Include also the addons which are stored in different location rather than default")

    replaceScripts : BoolProperty(
    name = 'Replace Scripts',
    default=False,
    description="If this flag is checked the addons, light presets and export presets will be replaced or deleted(if htere are no one) othewise them will be added to existing ones")

    saveName : StringProperty(
    name = 'Name',
    default="Untitled",
    description="Which name the saved preset will have")
