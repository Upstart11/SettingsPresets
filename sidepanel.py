from bpy.types import UIList, Panel

class PresetsUIList(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):


        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = item.icon)
            layout.use_property_decorate = True

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = item.icon)



class PresetsListPanel(Panel):
    bl_label = "Presets List"
    bl_idname = "SCENE_PT_LIST_DEMO"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SPresets"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        index = scene.list_index
        props = scene.SP_props
        presetsList = context.scene.presets_list

        row = layout.row()
        row.operator("list.refresh", text="Refresh")
        row = layout.row()
        row.template_list("PresetsUIList", "The_List", scene,"presets_list", scene, "list_index")
        row = layout.row()

        if len(presetsList) >= 2:
            row.operator('presets_list.import', text='Import')
                
            if index >= 2:
                row = layout.row()
                row.operator('presets_list.delete_item', text='Delete')

            if index != 1:
                row = layout.row()
                row.operator('preset.apply', text='Apply')
                row.prop(props, 'replaceScripts')
            else:
                row = layout.row()
                row.separator
                row.operator('preset.save', text='Save as preset')
                row.prop(props, "saveName", text="")
            

            if index >=1:
                row = layout.row()
                row.operator('preset.export', text='Export')
                row.prop(props, 'includeAddons')
            if index == 1 and props.includeAddons:
                row = layout.row()
                row.prop(props, 'includeExternalAddons')

