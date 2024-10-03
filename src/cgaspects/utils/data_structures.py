from collections import namedtuple

results_tuple = namedtuple("Result", ["csv", "selected", "folder"])

xyz_tuple = namedtuple("CrystalXYZ", ("xyz", "xyz_movie"))

ar_selection_tuple = namedtuple(
    "Options",
    [
        "selected_ar",
        "selected_cda",
        "selected_solvent_screen",
        "checked_directions",
        "selected_directions",
        "plotting",
    ],
)

shape_info_tuple = namedtuple(
    "shape_info",
    "x, y, z, pc1, pc2, pc3, aspect1, aspect2, sa, vol, sa_vol, shape",
)

file_info_tuple = namedtuple(
    "file_info",
    "supersats, size_files, directions, growth_mod, folders, summary_file",
)

plot_obj_tuple = namedtuple(
    "Plot",
    ["scatter", "line", "trendline"],
)
