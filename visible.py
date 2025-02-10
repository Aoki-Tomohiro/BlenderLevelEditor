import bpy
from .add_visible import MYADDON_OT_add_visible

#パネル Visible
class OBJECT_PT_visible(bpy.types.Panel):
    bl_idname = "OBJECT_PT_visible"
    bl_label = "Visible"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    #カスタムプロパティの定義
    bpy.types.Object.visible = bpy.props.BoolProperty(
        name="Visible",
        description="Object visibility flag",
        default=True
    )

    #サブメニューの描画
    def draw(self,context):
        if "visible" in context.object:           
            #既にプロパティがあれば、プロパティを表示
            self.layout.prop(context.object,"visible", text = "Visible")
        else:
            #プロパティがなければ、プロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_visible.bl_idname)