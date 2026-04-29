# LimbusDB ER Diagram

This folder contains a Graphviz DOT file that models the ER diagram for the `limbus_db` schema.

Files
- `limbus_db_er.gv`: Graphviz DOT file showing tables, primary keys, and foreign-key relationships.

Render commands (PowerShell / Windows):

```powershell
# render PNG
dot -Tpng .\limbus_db_er.gv -o .\limbus_db_er.png

# render SVG
dot -Tsvg .\limbus_db_er.gv -o .\limbus_db_er.svg
```

Notes & mapping
- Tables: `sinner`, `ego`, `identity`, `affinity`, `statuseffect`.
- Join tables: `egoaffinity`, `egostatuseffect`, `identityaffinity`, `identitystatuseffect` (all composite PKs of their FKs).
- PKs/FKs are annotated in the DOT file; `ego` and `identity` reference `sinner(sinner_id)`.

If you'd like, I can:
- Render the diagram and add `limbus_db_er.png`/`limbus_db_er.svg` into this folder (requires Graphviz installed on this machine), or
- Produce a PNG and embed it into one of your repo pages.
