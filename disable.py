import bpy
from .add_disable import MYADDON_OT_add_disable

#パネル Disable
class OBJECT_PT_disable(bpy.types.Panel):
    bl_idname = "OBJECT_PT_disable"
    bl_label = "Disable"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    #カスタムプロパティの定義
    bpy.types.Object.disable = bpy.props.BoolProperty(
        name="Disable",
        description="Object disabled flag",
        default=True
    )

    #サブメニューの描画
    def draw(self,context):
        if "disable" in context.object:           
            #既にプロパティがあれば、プロパティを表示
            self.layout.prop(context.object,"disable", text = "Disable")
        else:
            #プロパティがなければ、プロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_disable.bl_idname)