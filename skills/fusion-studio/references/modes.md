# Project modes

Ask once at the start of a project. The mode changes what "good" means, so it changes how you model.

## Print

The model must survive a printer.

- Material and printer first. Default printer: Bambu Lab H2C. See [print-rules.md](print-rules.md).
- One component per part that prints separately, named `<Part> - PRINT`. Parts that print together in one piece are one body.
- Decide orientation before modelling: the face on the bed, where overhangs fall, where layer lines run against load.
- Clearances, wall and radii are parameters so a test print can be corrected by editing one number.
- Add fillets and chamfers late. A first-layer chamfer on bed-contact edges stops elephant foot.
- Outputs: one 3MF per printed part (positioned flat is the slicer's job, but state the orientation), plus a STEP of the whole design.

Print-mode brief questions: material, nozzle (0.4 default), colour count, what it must hold or fit, load, outdoors or indoors, how it is used (hung, dropped, heated), any hardware (magnets, screws, inserts) and its real size.

## Showcase

The model is a picture or a video clip, not a part. Think crowdfunding page, product render, acrylic merch.

- Model real material thickness anyway (acrylic 3 mm, 5 mm, backing board 1.5 mm) so the render reads as a real object.
- Layered products (acrylic keychains: print layer, clear layer, ring, hole) are separate bodies so they can be exploded.
- **Exploded view:** keep parts as separate components, give them an `explode_gap` parameter, offset each occurrence along one axis in order of assembly. Screenshot at gap 0 (assembled) and at the exploded gap. The parts keep their exact positions, so a video editor can interpolate between the two stills or animate the exported meshes.
- Use `fusion_mcp.py shot` with a transparent background for cut-outs, `--dir` for the angle.
- Outputs: PNG per angle (assembled, exploded), OBJ for video software (FBX is not available through the API in Fusion 2705.1), STEP. Export the OBJ in the position the editor needs: assembled, exploded, or both.
- Printing checks are not needed. Say so. Do not spend effort on bridges and clearances.

Showcase brief questions: what the product is, the materials it would be made from and their thickness, the angles wanted, whether a transparent PNG or a mesh is the deliverable, brand colours (the brand-studio skill produces tokens for these).

## Apparel

A clothing brand mockup. Fusion models rigid things, so this mode covers what is rigid.

- Hang tags, label plates (woven or rubber), buttons, zip pulls, snap fasteners and hat badges. Also packaging boxes and display pieces such as hangers.
- Flat artwork goes on a thin body (a label is 0.8 to 2 mm), then the logo is shown through appearance, a decal or an engraved cut.
- It does not do fabric drape. If the user wants a garment picture, say it needs a cloth tool or a photographic mockup and offer the trims and packaging instead.
- Outputs: PNG views, STEP, and a note listing every artwork file placed and at what size.

Apparel brief questions: the item, the brand kit (logo files, colours, fonts), sizes of the real trim, how it attaches, quantity and finish.
