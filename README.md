# 3d-in-pygame-2

version 1:
A version where I have a small set of vertices and build polygons based on those vertices. A vertex can shared by many polygons.
Good: A lot less vertices to do math on.
Bad: Have to look up vertices when it is time to render polygons
This version is slow.

version 2:
Every vertices is unique to one polygon. The opposite of version 1. A lot easier to draw polygons and even though it is about 4 times the veritices it is still faster.

version 3:
Store some older version of version 2 here.
