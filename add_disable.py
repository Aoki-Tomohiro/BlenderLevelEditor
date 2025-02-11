import bpy

#オペレータ カスタムプロパティ['Disable']追加
class MYADDON_OT_add_disable(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_disable"
    bl_label = "Disable フラグ 追加"
    bl_description = "['disable']カスタムプロパティを追加します"
    bl_options = {"REGISTER","UNDO"}

    def execute(self,context):
        #['disable']カスタムプロパティを追加
        context.object["disable"] = True

        return {"FINISHED"}