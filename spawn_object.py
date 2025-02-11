import bpy
from .create_spawn_object import MYADDON_OT_create_spawn_object

class MYADDON_OT_create_player_spawn_object(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_player_spawn_object"
    bl_label = "プレイヤー出現ポイントシンボルの作成"
    bl_description = "プレイヤー出現ポイントのシンボルを作成します"

    def execute(self, context):
        bpy.ops.myaddon.myaddon_ot_create_spawn_object('EXEC_DEFAULT', type = "Player")
        return {'FINISHED'}
    
class MYADDON_OT_create_enemy_spawn_object(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_enemy_spawn_object"
    bl_label = "敵出現ポイントシンボルの作成"
    bl_description = "敵出現ポイントのシンボルを作成します"

    def execute(self, context):
        bpy.ops.myaddon.myaddon_ot_create_spawn_object('EXEC_DEFAULT', type = "Enemy")
        return {'FINISHED'}