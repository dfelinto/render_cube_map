# Render Cube Map
Addon to automatically render cube maps from Blender

How to Use
==========
* Install and enable the [Addon](render_cube_map.py)
* Turn the Cube Map option in the ``Render`` tab in the ``Render`` panel.
* Render your frame or animation, as you would normally

![Cube Map Addon](http://dalaifelinto.com/images/cube_map.png)

Each face of the cube map is saved separately in your output folder.

Design Considerations
=====================
Since this was originally designed to generated VR Cube Maps (with my [Spherical Stereo](http://www.dalaifelinto.com/?p=1009) Blender branch), the cube map is always upward. In other words, the Z rotation of the camera is taken into consideration, but the ``NORTH``, ``WEST``, ``EAST``, ``SOUTH`` faces are all upward oriented.

Also, the composite nodes are not taken into consideration at the moment.
