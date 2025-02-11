import bpy
import bpy.ops
import os

# オペレータ 出現ポイントのシンボルを読み込む
class MYADDON_OT_load_spawn_object(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_load_spawn_object"
    bl_label = "出現ポイントシンボルImport"
    bl_description = "出現ポイントのシンボルをImportします"
    bl_options = {"REGISTER", "UNDO"}
    prototype_object_name = "ProttypePlayerSpawn"
    object_name = "PlayerSpawn"

    def execute(self, context):
        # 読み込み開始
        print("出現ポイントのシンボルをImportします")

        # 重複ロード防止
        spawn_object = bpy.data.objects.get(MYADDON_OT_load_spawn_object.prototype_object_name)
        if spawn_object is not None:
            return {'CANSELLED'}

        # スクリプトが配置されているディレクトリの名前を取得する
        addon_directory = os.path.dirname(__file__)

        # ディレクトリからのモデルファイルの相対パスを記述
        relative_path = "Models/Player/Player.obj"
        
        # 合成してモデルファイルのフルパスを得る
        full_path = os.path.join(addon_directory, relative_path)

        #オブジェクトをインポート
        bpy.ops.wm.obj_import('EXEC_DEFAULT', filepath = full_path, display_type = 'THUMBNAIL', forward_axis = 'Z', up_axis = 'Y')

        # 回転を適用
        bpy.ops.object.transform_apply(location = False, rotation = True, scale = False, properties = False, isolate_users = False)

        # アクティブなオブジェクトを取得
        object = bpy.context.active_object

        # オブジェクト名を変更
        object.name = MYADDON_OT_load_spawn_object.prototype_object_name

        # オブジェクトの種類を設定
        object["type"] = MYADDON_OT_load_spawn_object.object_name

        # メモリ上にはおいておくがシーンから外す
        bpy.context.collection.objects.unlink(object)

        return {'FINISHED'}