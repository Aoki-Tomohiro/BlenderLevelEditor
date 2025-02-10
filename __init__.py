import bpy
import bpy_extras
import math
import gpu
import gpu_extras.batch
import copy
import mathutils
import json

#ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Tomohiro Aoki",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description": "レベルエディタ",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}

#オペレータ 頂点を伸ばす
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "頂点座標を引っ張って伸ばします"
    #リドゥ、アンドゥ可能オプション
    bl_options = {'REGISTER','UNDO'}

    #メニューを実行したときに呼ばれるコールバック関数
    def execute(self,context):
        bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
        print("頂点を伸ばしました。")

        #オペレータの命令終了を通知
        return {'FINISHED'}
    
#オペレータ ICO球生成
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_object"
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    bl_options = {'REGISTER','UNDO'}

    #メニューを実行したときに呼ばれる関数
    def execute(self,context):
        bpy.ops.mesh.primitive_ico_sphere_add()
        print("ICO球を生成しました。")

        return {'FINISHED'}
    
#オペレータ シーン出力
class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーン情報をExportします"
    #出力するファイルの拡張子
    filename_ext = ".json"

    def write_and_print(self,file,str):
        print(str)

        file.write(str)
        file.write('\n')

    def parse_scene_recursive(self,file,object,level):
        """シーン解析用再起関数"""

        #深さ文インデントする(タブを挿入)
        indent = ''
        for i in range(level):
            indent += "\t"

        #オブジェクト名書き込み
        self.write_and_print(file, indent + object.type)
        #ローカルトランスフォーム行列から平行移動、回転、スケーリングを抽出
        #型はVector, Quaternion, Vector
        trans,rot,scale = object.matrix_local.decompose()
        #回転をQuaternionからEuler(3軸での回転角)に変換
        rot = rot.to_euler()
        #ラジアンから度数法に変換
        rot.x = math.degrees(rot.x)
        rot.y = math.degrees(rot.y)
        rot.z = math.degrees(rot.z)
        #トランスフォーム情報を表示
        self.write_and_print(file, indent + "T %f,%f,%f"%(trans.x,trans.y,trans.z))
        self.write_and_print(file, indent + "R %f,%f,%f"%(rot.x,rot.y,rot.z))
        self.write_and_print(file, indent + "S %f,%f,%f"%(scale.x,scale.y,scale.z))
        #カスタムプロパティ'file_name'
        if "file_name" in object:
            self.write_and_print(file,indent + "N %s" % object["file_name"])
        #カスタムプロパティ'collision'
        if "collider" in object:
            self.write_and_print(file, indent + "C %s" % object["collider"])
            if object["collider"] == "AABB":
                temp_str = indent + "CC %f %f %f"
                temp_str %= (object["collider_center"][0], object["collider_center"][1], object["collider_center"][2])
                self.write_and_print(file, temp_str)
                temp_str = indent + "CS %f %f %f"
                temp_str %= (object["collider_size"][0], object["collider_size"][1], object["collider_size"][2])
                self.write_and_print(file, temp_str)
            elif object["collider"] == "OBB":
                temp_str = indent + "CC %f %f %f"
                temp_str %= (object["collider_center"][0], object["collider_center"][1], object["collider_center"][2])
                self.write_and_print(file, temp_str)
                temp_str = indent + "CS %f %f %f"
                temp_str %= (object["collider_size"][0], object["collider_size"][1], object["collider_size"][2])
                self.write_and_print(file, temp_str)            
            elif object["collider"] == "SPHERE":
                temp_str = indent + "CC %f %f %f" 
                temp_str %= (object["collider_center"][0], object["collider_center"][1], object["collider_center"][2])
                self.write_and_print(file, temp_str)
                temp_str = indent + "CR %f"
                temp_str %= (object["collider_radius"])
                self.write_and_print(file, temp_str)                               
        self.write_and_print(file,indent + 'END')
        self.write_and_print(file,'')

        #子ノードへ進む(深さが1上がる)
        for child in object.children:
            self.parse_scene_recursive(file,child,level + 1)

    def export(self):
        """ファイルに出力""" 

        print("シーン情報出力開始...%r"%self.filepath)

        #ファイルをテキスト形式で書き出し用にオープン
        #スコープを抜けると自動的にクローズされる
        with open(self.filepath,"wt") as file:

            #ファイルに文字列を書き込む
            file.write("SCENE\n")

            #シーン内の全オブジェクトについて
            for object in bpy.context.scene.objects:

                #親オブジェクトがあるものはスキップ(代わりに親から呼び出すから)
                if(object.parent):
                    continue
                
                #シーン直下のオブジェクトをルートノード(深さ0)都とし、再起関数で走査
                self.parse_scene_recursive(file,object,0)

    def export_json(self):
        """JSON形式でファイルに出力"""

        #保存する情報をまとめるdict
        json_object_root = dict()

        #ノード名
        json_object_root["name"] = "scene"
        #オブジェクトリストを作成
        json_object_root["objects"] = list()

        #シーン内の全オブジェクトについて
        for object in bpy.context.scene.objects:

            #親オブジェクトがあるものはスキップ(代わりに親から呼び出すから)
            if(object.parent):
                continue

            #シーン直下のオブジェクトをルートノード(深さ0)とし、再起関数で走査
            self.parse_scene_recursive_json(json_object_root["objects"], object, 0)

        #オブジェクトをJSON文字列にエンコード
        json_text = json.dumps(json_object_root,ensure_ascii = False, cls = json.JSONEncoder, indent = 4)
        #コンソールに表示してみる
        print(json_text)

        #ファイルをテキスト形式で書き出し用にオープン
        #スコープを抜けると自動的にクローズされる
        with open(self.filepath,"wt",encoding = "utf-8") as file:

            #ファイルに文字列を書き込む
            file.write(json_text)

    def parse_scene_recursive_json(self,data_parent,object,level):

        #シーンのオブジェクト1個分のjsonオブジェクト生成
        json_object = dict()
        #オブジェクト種類
        json_object["type"] = object.type
        #オブジェクト名
        json_object["name"] = object.name

        #オブジェクトのローカルトランスフォームから
        #平行移動、回転、スケールを抽出
        trans, rot, scale = object.matrix_local.decompose()
        #回転を Quaternion から Euler (3軸での回転角) に変換
        rot = rot.to_euler()
        #トランスフォーム情報をディクショナリに登録
        transform = dict()
        transform["translation"] = (trans.x, trans.y, trans.z)
        transform["rotation"] = (rot.x, rot.y, rot.z)
        transform["scaling"] = (scale.x, scale.y, scale.z)
        #まとめて1個分のjsonオブジェクトに登録
        json_object["transform"] = transform

        #カスタムプロパティ'file_name'
        if "file_name" in object:
            json_object["file_name"] = object["file_name"]

        #カスタムプロパティ'collider'
        if "collider" in object:
            collider = dict()
            collider["type"] = object["collider"]
            collider["attribute"] = object["collider_attribute"]
            if collider["type"] == "AABB":
                collider["center"] = object["collider_center"].to_list()
                collider["size"] = object["collider_size"].to_list()
                json_object["collider"] = collider
            elif collider["type"] == "OBB":
                collider["center"] = object["collider_center"].to_list()
                collider["size"] = object["collider_size"].to_list()
                json_object["collider"] = collider                
            elif collider["type"] == "SPHERE":
                collider["center"] = object["collider_center"].to_list()
                collider["radius"] = object["collider_radius"]
                json_object["collider"] = collider       

        # カスタムプロパティ 'visible'
        if "visible" in object:
            json_object["visible"] = object.visible

        #1個分のjsonオブジェクトを親オブジェクトに登録
        data_parent.append(json_object)

        #子ノードがあれば
        if len(object.children) > 0:
            #子ノードリストを作成
            json_object["children"] = list()

            #子ノードへ進む(深さが1上がる)
            for child in object.children:
                self.parse_scene_recursive_json(json_object["children"], child, level + 1)

    def execute(self,context):
        print("シーン情報をExportします")

        #ファイルに出力
        self.export_json()

        print("シーン情報をExportしました")
        self.report({'INFO'},"シーン情報をExportしました")
        
        return {'FINISHED'}   

#トップバーの拡張メニュー
class TOPBAR_MT_my_menu(bpy.types.Menu):
    #Blenderがクラスを識別する為の固有の文字列
    bl_idname = "TOPBAR_MT_my_menu"
    #メニューのラベルとして表示される文字列
    bl_label = "MyMenu"
    #著者表示用の文字列
    bl_description = "拡張メニュー by" + bl_info["author"]

    #サブメニューの描画
    def draw(self,context):

        #トップバーの「エディターメニュー」に項目(オペレータ)を追加
        self.layout.operator("wm.url_open_preset",text = "Manual",icon = 'HELP')

        #トップバーの「エディターメニュー」に項目(オペレータ)を追加
        self.layout.operator(MYADDON_OT_stretch_vertex.bl_idname,text = MYADDON_OT_stretch_vertex.bl_label)

        #トップバーの「エディターメニュー」に項目(オペレータ)を追加
        self.layout.operator(MYADDON_OT_create_ico_sphere.bl_idname,text = MYADDON_OT_create_ico_sphere.bl_label)

        #トップバーの「エディターメニュー」に項目(オペレータ)を追加
        self.layout.operator(MYADDON_OT_export_scene.bl_idname,text = MYADDON_OT_export_scene.bl_label)

    #既存のメニューにサブメニューを追加
    def submenu(self,context):

        #ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

#オペレータ カスタムプロパティ['file_name']追加
class MYADDON_OT_add_filename(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_filename"
    bl_label = "FileName 追加"
    bl_description = "['file_name']カスタムプロパティを追加します"
    bl_options = {"REGISTER","UNDO"}

    def execute(self,context):
        
        #['file_name']カスタムプロパティを追加
        context.object["file_name"] = ""

        return {'FINISHED'}

#オペレータ カスタムプロパティ['collider']追加
class MYADDON_OT_add_collider(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_collider"
    bl_label = "コライダー 追加"
    bl_description = "['collider']カスタムプロパティを追加します"
    bl_options = {"REGISTER","UNDO"}

    def execute(self,context):
        
        #['collider']カスタムプロパティを追加
        context.object["collider"] = "AABB"
        context.object["collider_attribute"] = ""
        context.object["collider_center"] = mathutils.Vector((0,0,0))
        context.object["collider_size"] = mathutils.Vector((2,2,2))
        context.object["collider_radius"] = 1.0

        return {"FINISHED"}

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

#パネル ファイル名
class OBJECT_PT_file_name(bpy.types.Panel):
    """オブジェクトのファイルネームパネル"""
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "FileName"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    #サブメニューの描画
    def draw(self,context):

        #パネルに項目を追加
        if "file_name" in context.object:
            #既にプロパティがあれば、プロパティを表示
            self.layout.prop(context.object,'["file_name"]',text = self.bl_label)
        else:
            #プロパティがなければ、プロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_filename.bl_idname)

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

#コライダー描画
class DrawCollider:

    #描画ハンドル
    handle = None

    # 3Dビューに登録する描画関数
    def draw_collider():
        # 頂点データ
        vertices = {"pos": []}
        # インデックスデータ
        indices = []

        # 立方体の各頂点のオフセット
        box_offsets = [
            [-0.5, -0.5, -0.5],  # 左下前
            [+0.5, -0.5, -0.5],  # 右下前
            [-0.5, +0.5, -0.5],  # 左上前
            [+0.5, +0.5, -0.5],  # 右上前
            [-0.5, -0.5, +0.5],  # 左下奥
            [+0.5, -0.5, +0.5],  # 右下奥
            [-0.5, +0.5, +0.5],  # 左上奥
            [+0.5, +0.5, +0.5],  # 右上奥
        ]

        # 球の頂点数（分割数を調整して精度を変える）
        num_segments = 16
        num_rings = 8

        # 現在のシーンのオブジェクトリストを走査
        for object in bpy.context.scene.objects:
            # コライダープロパティがなければ、描画をスキップ
            if not "collider" in object:
                continue

            # 中心点、サイズの変数を宣言
            center = mathutils.Vector((0, 0, 0))
            size = mathutils.Vector((2, 2, 2))
            radius = 1.0

            # プロパティから値を取得
            center[0] = object["collider_center"][0]
            center[1] = object["collider_center"][1]
            center[2] = object["collider_center"][2]
            size[0] = object["collider_size"][0]
            size[1] = object["collider_size"][1]
            size[2] = object["collider_size"][2]
            radius = object["collider_radius"]

            # 追加前の頂点数
            start = len(vertices["pos"])

            if object.get("collider") in ["AABB", "OBB"]:
                # BOXの頂点生成
                for offset in box_offsets:
                    pos = center + mathutils.Vector(offset) * size
                    pos = object.matrix_world @ pos
                    vertices["pos"].append(pos)

                # BOXのインデックス生成
                indices.extend([
                    [start + 0, start + 1], [start + 1, start + 3], [start + 3, start + 2], [start + 2, start + 0],
                    [start + 4, start + 5], [start + 5, start + 7], [start + 7, start + 6], [start + 6, start + 4],
                    [start + 0, start + 4], [start + 1, start + 5], [start + 2, start + 6], [start + 3, start + 7],
                ])
            elif object["collider"] == "SPHERE":
                # 球の頂点生成
                for ring in range(num_rings + 1):
                    phi = ring * math.pi / num_rings
                    for segment in range(num_segments):
                        theta = segment * 2 * math.pi / num_segments

                        x = math.sin(phi) * math.cos(theta)
                        y = math.sin(phi) * math.sin(theta)
                        z = math.cos(phi)

                        pos = center + mathutils.Vector((x, y, z)) * radius
                        pos = object.matrix_world @ pos
                        vertices["pos"].append(pos)

                # 球のインデックス生成
                for ring in range(num_rings):
                    for segment in range(num_segments):
                        next_segment = (segment + 1) % num_segments

                        index1 = start + ring * num_segments + segment
                        index2 = start + ring * num_segments + next_segment
                        index3 = start + (ring + 1) * num_segments + segment
                        index4 = start + (ring + 1) * num_segments + next_segment

                        indices.extend([[index1, index2], [index2, index4], [index4, index3], [index3, index1]])

        # ビルトインのシェーダを取得
        shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        # バッチを作成(引数:シェーダ、トポロジー、頂点データ、インデックスデータ)
        batch = gpu_extras.batch.batch_for_shader(shader, "LINES", vertices, indices=indices)

        # シェーダのパラメータ設定
        color = [0.5, 1.0, 1.0, 1.0]
        shader.bind()
        shader.uniform_float("color", color)
        # 描画
        batch.draw(shader)

#Blenderに登録するクラスリスト
classes = (
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    TOPBAR_MT_my_menu,
    MYADDON_OT_add_filename,
    MYADDON_OT_add_collider,
    MYADDON_OT_add_visible,
    OBJECT_PT_file_name,
    OBJECT_PT_collider,
    OBJECT_PT_visible,
)

#アドオン有効化時コールバック
def register():
    #Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    #メニューに項目を追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    #3Dビューに描画関数を追加
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(DrawCollider.draw_collider,(),"WINDOW","POST_VIEW")
    print("レベルエディタが有効化されました。")
    
#アドオン無効化時コールバック
def unregister():
    #メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
     #3Dビューから描画関数を削除
    bpy.types.SpaceView3D.draw_handler_remove(DrawCollider.handle,"WINDOW")

    #Blenderからクラスを削除
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました。")
    
#テスト実行用コード
if __name__ == "__main__":
    register()