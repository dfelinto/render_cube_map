#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

# <pep8 compliant>

# ########################################
# Render Cube Map
#
# Dalai Felinto
#
# dalaifelinto.com
# Rio de Janeiro, September 2015
#
# ########################################

bl_info = {
    "name": "Cube Map",
    "author": "Dalai Felinto",
    "version": (1, 0),
    "blender": (2, 7, 5),
    "location": "Render Panel",
    "description": "",
    "warning": "",
    "wiki_url": "https://github.com/dfelinto/render_cube_map",
    "tracker_url": "",
    "category": "Render"}


import bpy
from bpy.app.handlers import persistent


# ############################################################
# Callbacks
# ############################################################

class NodeTree:
    def __init__(self, scene):
        self._use_nodes = scene.use_nodes
        self._use_compositing = scene.render.use_compositing

        self._nodes_mute = {}
        self._scene = scene

        self._scene.render.use_compositing = True

        if not self._use_nodes:
            scene.use_nodes = True
            self._muteNodes()
        else:
            self._storeNodes()
            self._muteNodes()

    def _storeNodes(self):
        """
        store the existent nodes and if they are muted
        """
        nodes = self._scene.node_tree.nodes
        for node in nodes:
            self._nodes_mute[hash(node)] = node.mute

    def _muteNodes(self):
        """
        mute all the existent nodes
        """
        nodes = self._scene.node_tree.nodes
        for node in nodes:
            node.mute = True

    def cleanupScene(self):
        """
        remove all the new nodes, and unmute original ones
        """
        scene = self._scene
        scene.use_nodes = self._use_nodes
        scene.render.use_compositing = self._use_compositing

        self._cleanNodes()
        self._unMuteNodes()

    def _cleanNodes(self):
        """
        remote all the nodes created temporarily
        """
        nodes = self._scene.node_tree.nodes
        to_del = []
        keys = self._nodes_mute.keys()

        for node in nodes:
            if hash(node) not in keys:
                to_del.append(node)

        for node in to_del:
            nodes.remove(node)

    def _unMuteNodes(self):
        """
        unmute all the existent nodes
        """
        nodes = self._scene.node_tree.nodes
        for node in nodes:
            node.mute = self._nodes_mute[hash(node)]


class View:
    def __init__(self, name, euler_rotation):
        self._name = name
        self._scene = None
        self._scene_camera = None
        self._node = None
        self._camera = None
        self._euler_rotation = euler_rotation

    def setScene(self, scene):
        scene.name = self._name
        self._scene = scene

    def setNode(self, node, links, node_output):
        node.name = self._name
        node.label = self._name
        node.scene = self._scene
        self._node = node

        # TODO if there were nodetrees, duplicate them here

        # connect to output
        _input = node_output.layer_slots.new(self._name)
        links.new(node.outputs[0], _input)

    def setCamera(self, data, loc, zed):
        self._scene_camera = self._scene.camera

        self._camera = bpy.data.objects.new(self._name, data)
        self._scene.objects.link(self._camera)

        rotation = self._euler_rotation.copy()
        rotation.z += zed

        self._camera.rotation_euler = rotation
        self._camera.location = loc

        # change scene camera
        self._scene.camera = self._camera

    def resetCamera(self):
        self._scene.objects.unlink(self._camera)
        bpy.data.objects.remove(self._camera)
        self._camera = None

    @property
    def scene(self):
        return self._scene

    @property
    def name(self):
        return self._name


@persistent
def cube_map_render_init(scene):
    """
    setup the cube map settings for all the render frames
    """
    from mathutils import Euler
    from math import pi
    half_pi = pi * 0.5

    if not scene.cube_map.use_cube_map:
        return

    main_scene = scene
    hashes = [hash(scene) for scene in bpy.data.scenes]

    views = [
            View('NORTH',  Euler((half_pi, 0.0,  0.0))),
            View('SOUTH',  Euler((half_pi, 0.0, pi))),
            View('WEST',   Euler((half_pi, 0.0, half_pi))),
            View('EAST',   Euler((half_pi, 0.0, -half_pi))),
            View('ZENITH', Euler((pi, 0.0, 0.0))),
            View('NADIR',  Euler((0.0, 0.0, 0.0))),
            ]

    for view in views:
        # create a scene per view
        bpy.ops.scene.new(type='LINK_OBJECTS')
        scene = [scene for scene in bpy.data.scenes if hash(scene) not in hashes][0]

        # mark the scene to remove it afterwards
        scene.cube_map.is_temporary = True

        hashes.append(hash(scene))
        view.setScene(scene)

    # create a scene from scratch
    node_tree_data = NodeTree(main_scene)

    # created the necessary nodetrees there
    node_tree = main_scene.node_tree

    # output node
    node_output = node_tree.nodes.new('CompositorNodeOutputFile')
    node_output.inputs.clear()

    for view in views:
        node = node_tree.nodes.new('CompositorNodeRLayers')
        view.setNode(node, node_tree.links, node_output)

    # globals
    bpy.cube_map_node_tree_data = node_tree_data
    bpy.cube_map_views = views


# ############################################################
# Cameras Setup
# ############################################################

@persistent
def cube_map_render_pre(scene):
    if not scene.cube_map.use_cube_map:
        return

    from math import radians

    camera = scene.camera
    data = camera.data.copy()

    data.lens_unit = 'FOV'
    data.angle = radians(90)
    data.type='PERSP'

    mat = camera.matrix_world

    loc = mat.to_translation()
    rot = mat.to_euler()
    zed = rot.z

    views = bpy.cube_map_views

    for view in views:
        view.setCamera(data, loc, zed)


@persistent
def cube_map_render_post(scene):
    if not scene.cube_map.use_cube_map:
        return

    views = bpy.cube_map_views

    for view in views:
        view.resetCamera()


# ############################################################
# Clean-Up
# ############################################################

@persistent
def cube_map_render_cancel(scene):
    cube_map_cleanup(scene)


@persistent
def cube_map_render_complete(scene):
    cube_map_cleanup(scene)


def cube_map_cleanup(scene):
    """
    remove all the temporary data created for the cube map
    """
    if not scene.cube_map.use_cube_map:
        return

    bpy.cube_map_node_tree_data.cleanupScene()
    del bpy.cube_map_node_tree_data
    del bpy.cube_map_views

    bpy.app.handlers.scene_update_post.append(cube_map_post_update_cleanup)


def cube_map_post_update_cleanup(scene):
    """
    delay removal of scenes (otherwise we get a crash)
    """
    scenes_temp = [scene for scene in bpy.data.scenes if scene.cube_map.is_temporary]

    if not scenes_temp:
        bpy.app.handlers.scene_update_post.remove(cube_map_post_update_cleanup)

    else:
        bpy.data.scenes.remove(scenes_temp[0])

# ############################################################
# Setup Operator
# ############################################################

class CubeMapSetup(bpy.types.Operator):
    """"""
    bl_idname = "render.cube_map_setup"
    bl_label = "Cube Map Render Setup"
    bl_description = ""

    action = bpy.props.EnumProperty(
        description="",
        items=(("SETUP", "Setup", "Created linked scenes and setup cube map"),
               ("RESET", "Reset", "Delete added scenes"),
               ),
        default="SETUP",
        options={'SKIP_SAVE'},
        )

    @classmethod
    def poll(cls, context):
        return True

    def setup(self, window, scene):
        cube_map = scene.cube_map
        cube_map.is_enabled = True

        use_cube_map = cube_map.use_cube_map
        cube_map.use_cube_map = True

        cube_map_render_init(scene)
        cube_map_render_pre(scene)

        cube_map.use_cube_map = use_cube_map
        window.screen.scene = scene

    def reset(self, scene):
        cube_map = scene.cube_map
        cube_map.is_enabled = False

        use_cube_map = cube_map.use_cube_map
        cube_map.use_cube_map = True

        cube_map_render_post(scene)
        cube_map_cleanup(scene)

        cube_map.use_cube_map = use_cube_map

    def invoke(self, context, event):
        scene = context.scene
        cube_map = scene.cube_map

        is_enabled = cube_map.is_enabled

        if self.action == 'RESET':
            self.report({'ERROR'}, "Option temporarilly disabled")
            return {'CANCELLED'}

            if is_enabled:
                if cube_map.is_temporary:
                    self.report({'ERROR'}, "Cannot reset cube map from one of the created scenes")
                    return {'CANCELLED'}
                else:
                    self.reset(scene)
                    return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Cube Map render is not setup")
                return {'CANCELLED'}

        else: # SETUP
            if is_enabled:
                self.report({'ERROR'}, "Cube Map render is already setup")
                return {'CANCELLED'}
            else:
                self.setup(context.window, scene)
                return {'FINISHED'}


# ############################################################
# User Interface
# ############################################################

def RENDER_PT_cube_map(self, context):
    scene = context.scene
    cube_map = scene.cube_map

    col = self.layout.column()

    col.prop(scene.cube_map, "use_cube_map")
    col.separator()

    if not cube_map.is_enabled:
        col.operator("render.cube_map_setup", text="Cube Map Setup").action='SETUP'
    else:
        col.operator("render.cube_map_setup", text="Cube Map Reset", icon="X").action='RESET'


# ############################################################
# Scene Properties
# ############################################################

class CubeMapInfo(bpy.types.PropertyGroup):
    use_cube_map = bpy.props.BoolProperty(
            name="Cube Map",
            default=False,
            )

    is_temporary = bpy.props.BoolProperty(
            name="Temporary",
            default=False,
            )

    is_enabled = bpy.props.BoolProperty(
            name="Enabled",
            default=False,
            )


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(CubeMapInfo)
    bpy.utils.register_class(CubeMapSetup)

    bpy.types.Scene.cube_map = bpy.props.PointerProperty(
            name="cube_map",
            type=CubeMapInfo,
            options={'HIDDEN'},
            )

    bpy.app.handlers.render_init.append(cube_map_render_init)
    bpy.app.handlers.render_pre.append(cube_map_render_pre)
    bpy.app.handlers.render_post.append(cube_map_render_post)
    bpy.app.handlers.render_cancel.append(cube_map_render_cancel)
    bpy.app.handlers.render_complete.append(cube_map_render_complete)

    bpy.types.RENDER_PT_render.append(RENDER_PT_cube_map)


def unregister():
    bpy.types.RENDER_PT_render.remove(RENDER_PT_cube_map)

    del bpy.types.Scene.cube_map
    bpy.utils.unregister_class(CubeMapInfo)
    bpy.utils.unregister_class(HashInfo)
    bpy.utils.unregister_class(CubeMapSetup)

    bpy.app.handlers.render_init.remove(cube_map_render_init)
    bpy.app.handlers.render_pre.remove(cube_map_render_pre)
    bpy.app.handlers.render_post.remove(cube_map_render_post)
    bpy.app.handlers.render_cancel.remove(cube_map_render_cancel)
    bpy.app.handlers.render_complete.remove(cube_map_render_complete)


if __name__ == '__main__':
    register()
