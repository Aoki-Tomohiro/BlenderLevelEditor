import bpy

#オペレータ カスタムプロパティ['Visible']追加
class MYADDON_OT_add_visible(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_visible"
    bl_label = "Visible フラグ 追加"
    bl_description = "['visible']カスタムプロパティを追加します"
    bl_options = {"REGISTER","UNDO"}

    def execute(self,context):
        #['visible']カスタムプロパティを追加
        context.object["visible"] = True

        return {"FINISHED"}