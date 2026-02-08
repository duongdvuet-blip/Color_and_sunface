# -*- coding: utf-8 -*-
import NXOpen
import NXOpen.Assemblies
import random

def main():
    session = NXOpen.Session.GetSession()
    ui = NXOpen.UI.GetUI()
    lw = session.ListingWindow
    lw.Open()

    sel = ui.SelectionManager
    count = sel.GetNumSelectedObjects()

    if count == 0:
        ui.NXMessageBox.Show(
            "Random Color",
            NXOpen.NXMessageBox.DialogType.Warning,
            "No component selected"
        )
        return

    # Lưu các part đã xử lý để tránh đổi màu trùng
    processed_parts = set()

    disp_mod = session.DisplayManager.NewDisplayModification()
    disp_mod.ApplyToAllFaces = True
    disp_mod.ApplyToOwningParts = False   # ⚠️ QUAN TRỌNG: PART-LEVEL
    disp_mod.NewTranslucency = 0

    for i in range(count):
        obj = sel.GetSelectedObject(i)

        if not isinstance(obj, NXOpen.Assemblies.Component):
            continue

        comp = obj
        part = comp.Prototype.OwningPart

        if part is None:
            continue

        # Tránh xử lý lại cùng 1 part
        if part.Tag in processed_parts:
            continue

        processed_parts.add(part.Tag)

        bodies = [b for b in part.Bodies]
        if len(bodies) == 0:
            continue

        random_color = random.randint(1, 216)
        disp_mod.NewColor = random_color

        # APPLY MÀU CHO BODY CỦA PART
        disp_mod.Apply(bodies)

        lw.WriteLine(
            "Part: {} → Color {}".format(part.Leaf, random_color)
        )

    disp_mod.Dispose()
    lw.WriteLine("DONE")

if __name__ == "__main__":
    main()
