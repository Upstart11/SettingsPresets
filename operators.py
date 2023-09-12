import zipfile
import bpy
import os
import shutil
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

scriptDir = os.path.realpath(__file__)
CurVerUserPrefsDir =  bpy.utils.resource_path('USER')
VerPrefsDir = os.path.dirname(CurVerUserPrefsDir)
CustomDirForScripts = bpy.utils.script_path_pref()
DefaultPresetName = "New Preset"


class ImportPreset(Operator,  ImportHelper):
    bl_idname = "presets_list.import"
    bl_label = "Import"

    filter_glob: StringProperty(
        default='*.zip',
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        return len(context.scene.presets_list) >= 2
    
    def execute(self, context):
        PrFolder = bpy.context.preferences.addons['SettingsPresets'].preferences.SettingsPresetsFolder
        importFromZF =  os.path.abspath(self.filepath)
        if zipfile.is_zipfile(importFromZF):
            with zipfile.ZipFile(importFromZF, 'a') as importedzip:
                if ("PresetInfo.txt" in importedzip.namelist()):
                    importedzip.extractall(os.path.normpath(path=PrFolder + "/" + os.path.basename(importFromZF)[:-4]))
                    SPAF = os.path.normpath(PrFolder + "/" + os.path.basename(importFromZF)[:-4]  + "/scripts/addons/SettingsPresets")
                    ExtPath = os.path.normpath(PrFolder + "/" + os.path.basename(importFromZF)[:-4]  + "/External")
                    if os.path.isdir(SPAF):
                        shutil.rmtree(SPAF)
                    if os.path.exists(ExtPath):
                        if os.path.exists(CustomDirForScripts):
                            shutil.copytree(ExtPath, CustomDirForScripts, copy_function = shutil.copyfile, ignore_dangling_symlinks = True, dirs_exist_ok = True)
                        shutil.rmtree(ExtPath, ignore_errors=True)
                    bpy.ops.list.refresh()
                else:
                    self.report({'ERROR'},"This is not a preset file ")
        else:
            self.report({'ERROR'},"This is not a zip file")
        return{'FINISHED'}

class ListRefresh(Operator):
    bl_idname = "list.refresh"
    bl_label = "Refresh the list"

    def execute(self, context):
        PrFolder = bpy.context.preferences.addons['SettingsPresets'].preferences.SettingsPresetsFolder
        presetsList = context.scene.presets_list 
        presetsList.clear()
        
        if len(presetsList) < 2:
            presetsList.add()
            presetsList[0].name = "Default"
            presetsList[0].icon = "BLENDER"
            presetsList.add()
            presetsList[1].name = "Current"
            presetsList[1].icon = "PREFERENCES"
        else:
            presetsList[0].name = "Default"
            presetsList[0].icon = "BLENDER"
            presetsList[1].name = "Current"
            presetsList[1].icon = "PREFERENCES"
        if os.path.isdir(PrFolder):
            for PDfolder in os.listdir(PrFolder):
                PDfolder = os.path.normpath(PrFolder + "/" + PDfolder)
                PIFile = os.path.normpath(PDfolder + "/PresetInfo.txt")
                
                if os.path.isdir(PDfolder):
                    if os.path.isfile(PIFile):
                        with open(PIFile, mode = "r") as presetInfoFile:
                            presetAtrs = presetInfoFile.read().split("\n")
                            presetsList.add()
                            presetsList[len(presetsList) - 1].name = presetAtrs[0]
                            if eval(presetAtrs[1]):
                                presetsList[len(presetsList) - 1].icon = "SETTINGS"
                            presetsList[len(presetsList) - 1].prest_path = PDfolder
                            presetsList[len(presetsList) - 1].hasAddons = eval(presetAtrs[1])
        else:
            os.mkdir(PrFolder)


        return{'FINISHED'}


class DeletePreset(Operator):
    bl_idname = "presets_list.delete_item"
    bl_label = "Deletes a preset"
    custom_icon = 'CANCEL'


    @classmethod
    def poll(cls, context):
        return len(context.scene.presets_list) >= 2


    def execute(self, context):
        presetsList = context.scene.presets_list
        index = context.scene.list_index
        DirToDelete = os.path.normpath(presetsList[index].prest_path)
        shutil.rmtree(DirToDelete)
        bpy.ops.list.refresh()
        return{'FINISHED'}

class ExportSettings(Operator, ImportHelper):
    bl_idname = "preset.export"
    bl_label = "Export settings"


    def execute(self, context):
        presetsList = context.scene.presets_list
        index = context.scene.list_index
        props = context.scene.SP_props
        pathToExport = os.path.abspath(self.filepath)
        SFilesDir = CurVerUserPrefsDir

        if index == 1:
            bpy.ops.wm.save_userpref()
            bpy.ops.wm.save_homefile()

        if index >= 2:
            SFilesDir = os.path.normpath(presetsList[index].prest_path)            
        if os.path.isdir(pathToExport):
            pathToExport += "/" + DefaultPresetName
        if pathToExport[-4:] == ".zip":
            pathToExport = pathToExport[:-4]
        while pathToExport == " ":
            pathToExport = pathToExport[:-1]

        if props.includeAddons:
            if props.includeExternalAddons and os.path.exists(CustomDirForScripts):
                TempExternalDir = os.path.normpath(SFilesDir + "/External")
                shutil.copytree(CustomDirForScripts, TempExternalDir, ignore=shutil.ignore_patterns('.DS_Store') , copy_function = shutil.copyfile, ignore_dangling_symlinks = True, dirs_exist_ok = True)
                shutil.make_archive(os.path.normpath(pathToExport), "zip", SFilesDir)
                shutil.rmtree(TempExternalDir)
            else:
                shutil.make_archive(os.path.normpath(pathToExport), "zip", SFilesDir)

                
        else:
            lightDir = os.path.normpath(SFilesDir + "/scripts/presets/lights")
            operatorDir = os.path.normpath(SFilesDir + "/scripts/presets/operator")
            shutil.make_archive(os.path.normpath(pathToExport), "zip", root_dir=SFilesDir, base_dir="config")

            if os.path.isdir(lightDir):
                if len(os.listdir(lightDir)) > 0:
                    with zipfile.ZipFile(os.path.normpath(pathToExport) + ".zip", 'a') as eportetzip:
                        internalRootPath = "/scripts/presets/lights"
                        internalRootPathFull = os.path.normpath(SFilesDir + internalRootPath)
                        if os.path.isdir(internalRootPathFull):
                            for exportPresetFolrder in os.listdir(internalRootPathFull):
                                internalFolderPath = os.path.normpath(internalRootPath + "\\" + exportPresetFolrder) 
                                internalFolderPathFull = os.path.normpath(SFilesDir + internalFolderPath)
                                if os.path.isdir(internalFolderPathFull):
                                    for exportPresetFile in os.listdir(internalFolderPathFull):
                                        internalFilePath = os.path.normpath(internalFolderPath + "\\" + exportPresetFile)
                                        if(exportPresetFile != ".DS_Store"):
                                            eportetzip.write(os.path.normpath(SFilesDir + internalFilePath), arcname=internalFilePath)
                                        
            if os.path.isdir(operatorDir):
                if len(os.listdir(operatorDir)) > 0:
                    with zipfile.ZipFile(os.path.normpath(pathToExport + ".zip"), 'a') as eportetzip:
                        internalRootPath = "/scripts/presets/operator"
                        internalRootPathFull = os.path.normpath(SFilesDir + internalRootPath)
                        if os.path.isdir(internalRootPathFull):
                            for exportPresetFolrder in os.listdir(os.path.normpath(SFilesDir + internalRootPath)):
                                internalFolderPath = os.path.normpath(internalRootPath + "/" + exportPresetFolrder) 
                                internalFolderPathFull = os.path.normpath(SFilesDir + internalFolderPath)
                                if os.path.isdir(internalFolderPathFull):
                                    for exportPresetFile in os.listdir(os.path.normpath(SFilesDir + internalFolderPath)):
                                        internalFilePath = os.path.normpath(internalFolderPath + "/" + exportPresetFile)
                                        if(exportPresetFile != ".DS_Store"):
                                            eportetzip.write(os.path.normpath(SFilesDir + internalFilePath), arcname=internalFilePath)

        PITempFile = os.path.normpath(os.path.dirname(scriptDir) + "/PresetInfo.txt")

        with open(PITempFile, mode = "w") as presetInfoTemp:
            presetInfoTemp.write(os.path.basename(pathToExport) + "\n")
            if os.path.isdir(SFilesDir + "/scripts/addons"):
                presetInfoTemp.write(str(props.includeAddons))
            else:
                presetInfoTemp.write("False")


        with zipfile.ZipFile(pathToExport + ".zip", 'a') as finalzip:
            finalzip.write(PITempFile, arcname="PresetInfo.txt")
        os.remove(PITempFile)

                

        return{'FINISHED'}

class SaveSettings(Operator):
    bl_idname = "preset.save"
    bl_label = "Save as preset"


    def execute(self, context):
        PrFolder = bpy.context.preferences.addons['SettingsPresets'].preferences.SettingsPresetsFolder
        props = context.scene.SP_props
        bpy.ops.wm.save_userpref()
        bpy.ops.wm.save_homefile()
        presetName = props.saveName if props.saveName != " " else DefaultPresetName
        pathToSave = os.path.normpath(PrFolder + "/" + presetName)
        shutil.copytree(CurVerUserPrefsDir, pathToSave, ignore=shutil.ignore_patterns('.DS_Store'))
        pathToAF = os.path.normpath(pathToSave + "/scripts/addons")
        
        if not props.includeAddons:
            if os.path.isdir(pathToAF):
                shutil.rmtree(pathToAF)
        else:
            shutil.rmtree(os.path.normpath(pathToAF + "/SettingsPresets"))

        
        PITempFile = os.path.normpath(os.path.dirname(scriptDir) + "/PresetInfo.txt")

        with open(PITempFile, mode = "w") as presetInfoTemp:
            presetInfoTemp.write(presetName + "\n")
            if os.path.isdir(os.path.normpath(CurVerUserPrefsDir + "/scripts/addons")):
                presetInfoTemp.write(str(props.includeAddons))
            else:
                presetInfoTemp.write("False")
        shutil.move(PITempFile, pathToSave)

        bpy.ops.list.refresh()

        return{'FINISHED'}

class ApplySettings(Operator):
    bl_idname = "preset.apply"
    bl_label = "Apply this settings preset"

    def removeScripts(blp_folder, addons_folder):
        if os.path.isdir(blp_folder):
            shutil.rmtree(blp_folder)
        for AFolder in os.listdir(addons_folder):
            fullPath = os.path.normpath(addons_folder + "/" + AFolder)
            if os.path.isdir(fullPath):
                if AFolder != "SettingsPresets":
                    shutil.rmtree(fullPath)
            else:
                os.remove(fullPath)


    def execute(self, context):
        props = context.scene.SP_props
        presetsList = context.scene.presets_list
        index = context.scene.list_index
        configFolder = bpy.utils.user_resource('CONFIG')
        ScriptsFolder = bpy.utils.user_resource('SCRIPTS')
        blpFolder = os.path.normpath(ScriptsFolder + "/presets")
        addonsFolder = os.path.normpath(ScriptsFolder + "/addons")
        if index == 0:
            if os.path.isdir(configFolder):
                shutil.rmtree(configFolder)
            if props.replaceScripts:
                ApplySettings.removeScripts(blpFolder, addonsFolder)
            bpy.ops.wm.read_factory_settings(app_template='', use_empty=False)

        else:
            copyFrom = os.path.normpath(presetsList[index].prest_path)
            CFConfigF = os.path.normpath(copyFrom + "/config")
            CFBlpF = os.path.normpath(copyFrom + "/scripts/presets")
            CFAddonsF = os.path.normpath(copyFrom + "/scripts/addons")
            if os.path.isdir(configFolder):
                shutil.rmtree(configFolder)

            shutil.copytree(CFConfigF, configFolder, copy_function = shutil.copyfile, ignore=shutil.ignore_patterns('.DS_Store') , ignore_dangling_symlinks=True, dirs_exist_ok=True)

            if props.replaceScripts:
                ApplySettings.removeScripts(blpFolder, addonsFolder)
            
            if os.path.isdir(CFBlpF):
                shutil.copytree(CFBlpF, blpFolder, ignore=shutil.ignore_patterns('.DS_Store') , copy_function = shutil.copyfile, dirs_exist_ok=True)
            if presetsList[index].hasAddons:
                for AFolder in os.listdir(CFAddonsF):
                    CFfullPath = os.path.normpath(CFAddonsF + "/" + AFolder)
                    CTfullPath = os.path.normpath(addonsFolder + "/" + AFolder)
                    if os.path.isdir(CFfullPath):
                        if not os.path.isdir(CTfullPath):
                            shutil.copytree(CFfullPath, CTfullPath, ignore=shutil.ignore_patterns('.DS_Store') , copy_function = shutil.copyfile, ignore_dangling_symlinks=True)
                    elif os.path.isfile(CFfullPath):
                        shutil.copyfile(CFfullPath, CTfullPath)

            # bpy.ops.wm.read_history()
            bpy.ops.wm.lib_reload()
            bpy.utils.refresh_script_paths()
            bpy.app.use_userpref_skip_save_on_exit = False
            try:
                bpy.ops.wm.read_userpref()
            except:
                print("An exception occurred")
            # bpy.ops.wm.read_userpref()
            bpy.ops.wm.read_homefile(load_ui=True, use_splash=True, use_factory_startup=False, use_empty=False)
            print("asddfjjdfvjnkdfv")

        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)
 
    def draw(self, context):
        layout = self.layout
        layout.label(text="Are You Sure?(Current Settings will be replaced)")

class CancelOperator(bpy.types.Operator):
    bl_idname = "dialog.cancel"
    bl_label = "Are you sure?"


    def execute(self, context):
        self.report({'INFO'}, "It Works")
        return {'FINISHED'}