import cadquery as cq
from cadquery import exporters

# --- Part 1: Rectangular Prism ---
part_1_length = 0.1149 * 0.1149  # Scaled length
part_1_width = 0.0718 * 0.1149  # Scaled width
part_1_height = 0.0431

part_1 = (
    cq.Workplane("XY")
    .rect(part_1_length, part_1_width)
    .extrude(part_1_height)
)

# --- Coordinate System Transformation for Part 1 ---
part_1 = part_1.rotate((0, 0, 0), (1, 0, 0), -90)
part_1 = part_1.rotate((0, 0, 0), (0, 0, 1), -90)
part_1 = part_1.translate((0.0057, 0.0057, 0))

# --- Part 2: Cylinder ---
part_2_radius = 0.0086 * 0.2011  # Scaled radius
part_2_height = 0.0057

part_2 = (
    cq.Workplane("XY")
    .circle(part_2_radius)
    .extrude(part_2_height)
)

# --- Coordinate System Transformation for Part 2 ---
part_2 = part_2.rotate((0, 0, 0), (1, 0, 0), -90)
part_2 = part_2.rotate((0, 0, 0), (0, 0, 1), -90)
part_2 = part_2.translate((0.0057, 0.0057, 0))

# --- Part 3: Cylinder with Curved Top ---
part_3_radius = 0.0172 * 0.4841  # Scaled radius
part_3_height = 0.0345

part_3 = (
    cq.Workplane("XY")
    .circle(part_3_radius)
    .extrude(part_3_height)
)

# --- Coordinate System Transformation for Part 3 ---
part_3 = part_3.rotate((0, 0, 0), (1, 0, 0), -90)
part_3 = part_3.rotate((0, 0, 0), (0, 0, 1), -90)
part_3 = part_3.translate((0.0057, 0.0057, 0))

# --- Assembly ---
assembly = part_1.union(part_2).union(part_3)

# --- Export to STL ---
exporters.export(assembly, './stlcq/0028/00288878.stl')