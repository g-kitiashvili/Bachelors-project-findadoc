# 3D asset credits

Assets used by the interactive body map.

## Mannequin

`mannequin.glb` is the "Male Base Mesh" from Free3D, used as a neutral, unbranded body shell.

- Source: https://free3d.com/3d-model/male-base-mesh-6682.html (credit to its Free3D author)
- License: Free3D Personal Use License (the free-download tier) - personal, non-commercial use only,
  no resale or redistribution, and the mesh's authorship may not be claimed as one's own. This does
  not grant commercial or public production use; a different license would be needed before any
  public deployment.

## Organs

`organs/*.glb` are derived from **BodyParts3D**, © The Database Center for Life Science, licensed
under Creative Commons Attribution-ShareAlike 2.1 Japan (CC BY-SA 2.1 JP). The original STL parts
were converted to glTF, merged where an organ spans several sub-parts, and Draco-compressed.

- Source: https://github.com/Kevin-Mattheus-Moerman/BodyParts3D (original: http://lifesciencedb.jp/bp3d/)
- Parts used (Foundational Model of Anatomy IDs): heart wall (FMA7274), lungs (FMA7309, FMA7310),
  large intestine (FMA7201), liver (FMA7197), stomach (FMA7148), bladder (FMA15900),
  kidneys (FMA7204, FMA7205), pancreas (FMA7198), spleen (FMA7196)

## Decoder

The Draco mesh decoder under `../draco/` is from three.js, licensed under Apache-2.0.
