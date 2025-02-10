import bpy
from .add_collider import MYADDON_OT_add_collider

#パネル コライダー
class OBJECT_PT_collider(bpy.types.Panel):
    bl_idname = "OBJECT_PT_collider"
    bl_label = "Collider"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    #サブメニューの描画
    def draw(self,context):

        #パネルに項目を追加
        if "collider" in context.object:
            self.layout.prop(context.object, '["collider"]',text = "Type")
            self.layout.prop(context.object, '["collider_attribute"]',text = "Attribute")
            #既にプロパティがあれば、プロパティを表示
            if context.object["collider"] == "AABB":
               self.layout.prop(context.object, '["collider_center"]',text = "Center")
               self.layout.prop(context.object, '["collider_size"]',text = "Size")
            elif context.object["collider"] == "OBB":
               self.layout.prop(context.object, '["collider_center"]',text = "Center")
               self.layout.prop(context.object, '["collider_size"]',text = "Size")
            elif context.object["collider"] == "SPHERE":
               self.layout.prop(context.object, '["collider_center"]',text = "Center")
               self.layout.prop(context.object, '["collider_radius"]',text = "Radius")
        else:
            #プロパティがなければ、プロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_collider.bl_idname)