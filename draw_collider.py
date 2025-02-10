import bpy
import math
import mathutils
import gpu
import gpu_extras.batch

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