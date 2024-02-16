import numpy as np
from typing import Tuple, List
from pathlib import Path
import trimesh
import logging

LOG = logging.getLogger("CGA:xyz_file")


def parse_xyz_file(
    filepath: Path, progress_callback=None
) -> List[Tuple[str, np.ndarray]]:
    """Convert provided CG xyz file into list of arrays by reading line by line.

    Parameters
    ----------
    filepath : str
        Path to the .XYZ file to read.
    progress_callback : function, optional
        Callback function taking (position, total) for e.g. progress tracking

    Returns
    -------
    list of tuple of :obj:`np.ndarray`
        List of (N) comment lines, along with :obj:`np.ndarray` arrays of contents
    """
    frames = []
    current_position = 0

    # make a callback function for progress
    def callback(pos, tot):
        if progress_callback is not None:
            progress_callback(pos, tot)

    num_frames = 1

    with filepath.open() as file:
        while True:
            header = file.readline()
            # Break at the end of file
            if not header:
                break

            section_line_count = int(header.strip())

            comment = file.readline().strip()
            if progress_callback is not None:
                num_frames = int(comment.split("//")[1])

            values = np.loadtxt(file, max_rows=section_line_count)
            frames.append((comment, np.array(values)))

            callback(len(frames), num_frames)

    return frames


def read_XYZ(filepath, progress_callback=None):
    """Read in shape data and generates a np arrary.
    Supported formats:
        .XYZ
        .txt (.xyz format)
        .stl
    """
    filepath = Path(filepath)
    LOG.debug(filepath)
    xyz = None
    xyz_movie = {}

    LOG.debug("reading file from %s", filepath.name)
    suffix = filepath.suffix

    if suffix == ".XYZ":
        LOG.debug("XYZ: File read!")
        xyzs = parse_xyz_file(filepath, progress_callback=progress_callback)
        if len(xyzs) > 0:
            xyz = xyzs[0][1]
        if len(xyzs) > 1:
            xyz_movie = {i: x[1] for i, x in enumerate(xyzs)}

    elif suffix == ".txt":
        LOG.debug("xyz: File read!")
        xyz = np.loadtxt(filepath, skiprows=2)
    elif suffix == ".stl":
        LOG.debug("stl: File read!")
        xyz = trimesh.load(filepath)
    else:
        LOG.warning("Invalid suffix when reading XYZ file %s", suffix)

    return xyz, xyz_movie
