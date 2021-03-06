Quickstart
----------

The general steps for mesh generation in `PyAero <index.html>`_ can be explained as follows:

.. important::
   It is important for the each of the following steps, that the airfoil is *selected*. I.e., after loading, click once onto the airfoil contour. You see that the contour is selected if a dashed black frame is drawn around the airfoil contour. If you click anywhere else in the graphics view, the contour will be deselected again, and none of the splining or meshing tasks will work.

1. Load an airfoil contour file

   - Loading can be done in several ways (see also :ref:`tutorial_load`).
   - For the quick start, just use the :menuselection:`File --> Open` menu and browse to your airfoil contour and load it

2. Spline and refine the airfoil contour

   - This is an important task, since the mesh around the airfoil is based on the point distribution which is generated right here
   - For first tests you can go with the default settings and just click the :guilabel:`Spline and Refine` Button
   - The contour will first be splined (constant distance between points) with the given number of points.
   - In the same step the contour will be refined mainly around the leading edge. The refinment criterion is a minimum angle between two consecutive line segments made of three adjacent points

3. Make a trailing edge with finite thickness

   - Since in real life the airfoil trailing edge has a finit thickness, this needs to be taken into account before meshing
   - The defaults make a trailing edge with a thickness of 0.4% relative to the unity chord length

4. Mesh the refined airfoil contour

   - Click on :guilabel:`Create Mesh` to create your first mesh

5. Export the mesh in the required format

   - Click on :guilabel:`Export Mesh` to export the mesh in a specific format. Use the appropriate check box(es)

This is it.