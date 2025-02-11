import bpy
from .load_spawn_object import MYADDON_OT_load_spawn_object

# オペレータ 出現ポイントのシンボルを作成・配置する
class MYADDON_OT_create_spawn_object(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_spawn_object"
    bl_label = "出現ポイントシンボルの作成"
    bl_description = "出現ポイントのシンボルを作成します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # 読み込み済みのコピー元オブジェクトを検索
        spawn_object = bpy.data.objects.get(MYADDON_OT_load_spawn_object.prototype_object_name)

        # まだ読み込んでいない場合
        if spawn_object is None:
            # 読み込みオペレータを実行する
            bpy.ops.myaddon.myaddon_ot_load_spawn_object('EXEC_DEFAULT')

            # 再検索。今度は見つかるはず
            spawn_object = bpy.data.objects.get(MYADDON_OT_load_spawn_object.prototype_object_name)

            # 出現ポイント作成開始
            print("出現ポイントのシンボルを作成します")

            # Blenderでの選択を解除する
            object = spawn_object.copy()

            # 複製したオブジェクトを現在のシーンにリンク（出現させる）
            bpy.context.collection.objects.link(object)

            # オブジェクト名を変更
            object.name = MYADDON_OT_create_spawn_object.object_name

            return {'FINISHED'}