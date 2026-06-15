# HCE · Project Notes

Running list of design/build notes captured during HCE district
work but not yet acted on. Each note has a date and a clear
deliverable so the next session can pick them up.

## Locations needing interiors on the exterior map

**Convenience Store (Kwik Stop / NexCorp Gas & Go)** ·
captured 2026-06-14

> "The convenience store is one of the few locations on the map
> that needs an interior on the large exterior map. It has large
> plate-glass windows and being able to see nearby environs
> features into it."

Why it matters: most exterior-map shops can be closed boxes, but
the convenience stores have giant plate-glass storefronts that
look INTO the interior from the public sidewalk. The interior is
a chapter-one focal point (Sam's register / wire basket / back-
cooler recursion at Kwik Stop, Skip's shift / locker #4 at Gas &
Go).

Build implications:
- The exterior model needs transparent (or no) front-wall
  geometry where the plate glass sits, with the interior visible
  through it.
- Interior at the same scale as the exterior — a few aisles,
  counter, back cooler, walk-in cooler door, ceiling, floor.
- Lights inside the store should leak out the windows at night
  (fluorescent practicals).
- The interior is at the SAME world position as the exterior;
  player can walk in via the door.

Other locations likely needing the same treatment when they land:
- D'Ambrosio's holdover · already has a vol5 interior pattern
- Cosmic Comics · the photocopier is canonically visible inside
- Halsey Studios · recording booth window probably visible

For now: marked as TODO. Build script for the commercial cluster
will need to either model the interior as part of the exterior
build (one GLB) or split into exterior + interior GLBs joined in
the scene.
