import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import numpy as np

LOG = logging.getLogger("CG-NET")


@dataclass
class Interaction:
    serial: int = field(repr=False)
    id: int
    mol_type: str
    molecule_info: str = field(repr=False)
    r: float
    energy: float | str = field(default=None)

    def add_energy(self, energy: float | str):
        if self.energy is None:
            self.energy = energy
            LOG.debug("Added energy %s to: %s", energy, self)
        else:
            LOG.warning(
                "Can't add energy [%s]! %s was already assinged to %s",
                energy,
                self.energy,
                self,
            )
            raise ValueError("Use 'modify_energy to modify energy value.'")

    def modify_id(self, idx: int):
        LOG.debug("Modifying ID of %s to: %s", self, idx)
        self.id = idx

    def modify_energy(self, energy: float):
        LOG.debug("Modifying energy of %s to: %s", self, energy)
        self.energy = energy

    def __eq__(self, other):
        if not isinstance(other, Interaction):
            return NotImplemented

        # Compare all fields except 'serial'
        return (
            self.id == other.id
            and self.mol_type == other.mol_type
            and self.r == other.r
        )


@dataclass
class Molecule:
    serial: int
    label: str
    interactions: List[Interaction] = field(default_factory=list)

    @property
    def energies(self) -> np.ndarray:
        added = []
        energies = []
        for interaction in self.interactions:
            if interaction.serial in added:
                continue
            energies.append(interaction.energy)
            added.append(interaction.serial)
        return np.array(energies)

    @property
    def unique_energies(self) -> np.ndarray:
        added = []
        energies = []
        for interaction in self.interactions:
            if interaction in added:
                continue
            energies.append(interaction.energy)
            added.append(interaction)
        return np.array(energies)

    @energies.setter
    def energies(self, energies: list | np.ndarray):
        LOG.info(
            "Setting energies to Molecule (%s | %s) with:\n %s",
            self.serial,
            self.label,
            energies,
        )
        if len(energies) != self.unique_energies.size:
            raise ValueError(
                f"{self.n_energies} interactions found, only {len(energies)} energies were given."
            )
        for interaction in self.interactions:

            if isinstance(interaction.energy, str):
                LOG.debug(
                    "Current energy potentially a placeholder [%s]",
                    interaction.energy,
                )
                if "_" in interaction.energy:
                    energy = energies[int(interaction.energy.split("_")[-1]) - 1]
                    interaction.modify_energy(energy)
                    LOG.debug("Replacing [%s] with [%s]", interaction.energy, energy)
                else:
                    interaction.modify_energy(energy[interaction.id])
                    LOG.debug(
                        "Placeholder index not found: Replacing [%s] with [%s]",
                        interaction.energy,
                        energy,
                    )
            else:
                LOG.debug("Replacing [%s] with [%s]", interaction.energy, energy)
                interaction.modify_energy(energy)

    @property
    def n_energies(self, kind="all") -> int:
        if kind == "all":
            return self.energies.size
        if kind == "unique":
            return self.unique_energies.size

    @property
    def n_interactions(self) -> int:
        return len(self.interactions)

    def add_interaction(self, interaction: Interaction):

        self.interactions.append(interaction)

    def add_energy(self, energy: float | str):
        if isinstance(energy, str):
            try:
                energy = float(energy)
            except ValueError:
                LOG.warning("Energy string was not a float: %s", energy)
                if "_" in energy:
                    try:
                        _ = int(energy.split("_")[-1])
                    except ValueError:
                        LOG.error(
                            "Cant convert energy to float or placeholder! "
                            "For a placeholder, ensure format of 'Int_#' #=int. Error at: %s",
                            energy,
                        )
                        raise
                else:
                    LOG.error(
                        "Cant convert energy to float or placeholder! "
                        "For a placeholder, ensure format of 'Int_#' #=int. Error at: %s",
                        energy,
                    )
                    raise

        assigned = False

        for interaction in self.interactions:
            if interaction.energy is None:
                lowest_unoccipied_id = interaction.id
                break
        for interaction in self.interactions:
            if interaction.id == lowest_unoccipied_id:
                interaction.add_energy(energy)

        if not assigned:
            LOG.warning("No interaction required energy assignment")

    def group_interactions(self, using="r"):
        grouping_dict = {}
        # Group interactions by radius and collect energies
        for interaction in self.interactions:
            group_val = getattr(interaction, using)
            if group_val not in grouping_dict:
                grouping_dict[group_val] = {
                    "count": 0,
                    "total_energy": 0,
                }
            grouping_dict[group_val]["count"] += 1
            grouping_dict[group_val]["total_energy"] += interaction.energy

        # Average energies and assign the same ID to interactions with the same desired attribute
        group_dict_keys = list(grouping_dict.keys())
        for r, data in grouping_dict.items():
            average_energy = data["total_energy"] / data["count"]
            idx = group_dict_keys.index(r) + 1

            for interaction in self.interactions:
                if getattr(interaction, using) == r:
                    interaction.modify_energy(average_energy)
                    interaction.modify_id(idx)


class CGNet:
    def __init__(self, filename: str | Path):
        self.filename: str | Path = Path(filename)
        self.molecules: List[Molecule] = []
        self.interaction_order_counter: int = 1

    @property
    def energies(self) -> dict:
        energies = {}
        for molecule in self.molecules:
            energies[molecule.label] = molecule.energies
        return energies

    @property
    def unique_energies(self) -> dict:
        energies = {}
        for molecule in self.molecules:
            energies[molecule.label] = molecule.unique_energies

        return energies

    @property
    def unique_energies_arr(self) -> np.ndarray:
        return np.concatenate(list(self.energies.values()))

    @property
    def n_energies(self) -> int:
        return sum([len(v) for _, v in self.energies.items()])

    @property
    def n_unique_energies(self) -> int:
        return self.unique_energies_arr.size

    def parse(self):
        with open(self.filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        mol_serial = 0
        reading_interactions = False
        reading_energies = False
        initial = True
        for line in lines:
            if re.match(r"^\d+:", line):
                reading_interactions = True
                match = re.match(r"^(\d+):\[(\d[A-Za-z])\](.*?)R=([\d\.]+)", line)
                if match:
                    reading_interactions = True
                    idx, label, molecule_info, r = match.groups()
                    idx = int(idx)
                    r = float(r)

                    if reading_interactions and (reading_energies or initial):
                        molecule = Molecule(mol_serial, label)
                        self.molecules.append(molecule)
                        mol_serial += 1
                        reading_energies = False
                        initial = False

                    interaction = Interaction(
                        serial=self.interaction_order_counter,
                        id=idx,
                        mol_type=label,
                        molecule_info=molecule_info,
                        r=r,
                    )
                    self.interaction_order_counter += 1
                    molecule.add_interaction(interaction)

            else:
                reading_energies = True
                reading_interactions = False
                # Parse energy values
                try:
                    energy = line.strip()
                    molecule.add_energy(energy)
                except ValueError:
                    continue

        LOG.info(
            "%s unique energies were found: %s",
            self.n_unique_energies,
            self.unique_energies,
        )

    def group_net(self, using="r"):
        for molecule in self.molecules:
            molecule.group_interactions(using)

    def write(self, output_filename):
        with open(output_filename, "w", encoding="utf-8") as file:
            for molecule in self.molecules:
                for interaction in molecule.interactions:
                    file.write(
                        f"{interaction.id}:[{interaction.mol_type}]{interaction.molecule_info}R={interaction.r}\n"
                    )
                written = []
                for interaction in molecule.interactions:
                    if interaction.id in written:
                        continue
                    if isinstance(interaction.energy, float):
                        file.write(f"{interaction.energy:.4f}\n")
                        written.append(interaction.id)
                    if isinstance(interaction.energy, str):
                        file.write(f"{interaction.energy}\n")
                        written.append(interaction.id)
        LOG.info("Written to: %s", output_filename)

    def replace_energies_from_net(self, other: List[Molecule]):
        for mol1, mol2 in zip(self.molecules, other.molecules):
            if len(mol1.interactions) != len(mol2.interactions):
                raise ValueError(
                    f"Number of interactions do not match. [{len(mol1.interactions)} vs {len(mol2.interactions)}]"
                )

            for inter1, inter2 in zip(mol1.interactions, mol2.interactions):
                if inter1 != inter2:
                    raise ValueError("Interactions do not match.")

            mol1.energies = mol2.unique_energies

        LOG.info("Successfully replaced energies in %s with those in %s", self, other)

    def replace_energies_from_array(self, energies: list | np.ndarray):
        energies = np.asarray(energies)

        if self.n_unique_energies != energies.size:
            raise ValueError(
                f"Needed {self.n_unique_energies}, while provided array has {energies.size}"
            )

        for mol in self.molecules:
            mol.energies(energies)

        LOG.info(
            "Successfully replaced energies in %s with those in %s", self, energies
        )

    def __repr__(self) -> str:
        return f"CG Net File : {self.filename.name}"


if __name__ == "__main__":
    tests = Path(__file__).parents[1] / "tests"
    cg_net = CGNet(tests / "inputs" / "xemium_acn_net.txt")
    # cg_net = CGNet(tests / "inputs" / "adipic_new_c_bonds.txt")
    # temp_net = CGNet(tests / "inputs" / "template_net.txt")
    cg_net.parse()
    cg_net.group_net()
    # temp_net.parse()
    # cg_net.group_net("r")
    # cg_net.parse()
    # temp_net.replace_energies_from_net(cg_net)
    cg_net.write(tests / "inputs" / "xemium_acn_grouped_net.txt")
    # temp_net.write(tests / "inputs" / "parsed_output.txt")
    # cg_net.write(tests / "inputs" / "parsed_output.txt")
