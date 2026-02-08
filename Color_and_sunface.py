# -*- coding: utf-8 -*-
import NXOpen
import NXOpen.Assemblies
import random
import NXOpen.UF

AREA_TOLERANCE = 0.01


def get_all_components(root_component):
    components = []
    stack = [root_component]
    while stack:
        comp = stack.pop()
        components.append(comp)
        children = comp.GetChildren()
        for child in children:
            stack.append(child)
    return components


def face_area(face, uf_session=None):
    if uf_session is None:
        uf_session = NXOpen.UF.UFSession.GetUFSession()
    try:
        return uf_session.Modl.AskFaceArea(face.Tag)
    except Exception:
        if hasattr(face, "Area"):
            return face.Area
        if hasattr(face, "GetArea"):
            return face.GetArea()
        return 0.0


def body_surface_area(body, uf_session=None):
    if uf_session is None:
        uf_session = NXOpen.UF.UFSession.GetUFSession()
    faces = body.GetFaces()
    return sum(face_area(face, uf_session) for face in faces)


def total_body_area(part, uf_session=None):
    if uf_session is None:
        uf_session = NXOpen.UF.UFSession.GetUFSession()
    bodies = [b for b in part.Bodies]
    if not bodies:
        return None, []
    area = sum(body_surface_area(body, uf_session) for body in bodies)
    return area, bodies


def find_existing_color(area, area_color_pairs):
    for existing_area, color in area_color_pairs:
        if abs(existing_area - area) <= AREA_TOLERANCE:
            return color
    return None

def main():
    session = NXOpen.Session.GetSession()
    ui = NXOpen.UI.GetUI()
    lw = session.ListingWindow
    uf_session = NXOpen.UF.UFSession.GetUFSession()
    lw.Open()

    work_part = session.Parts.Work
    root_component = work_part.ComponentAssembly.RootComponent
    if root_component is None:
        ui.NXMessageBox.Show(
            "Random Color",
            NXOpen.NXMessageBox.DialogType.Warning,
            "No assembly loaded"
        )
        return

    # Lưu các part đã xử lý để tránh đổi màu trùng
    processed_parts = set()
    area_color_pairs = []

    disp_mod = session.DisplayManager.NewDisplayModification()
    disp_mod.ApplyToAllFaces = True
    disp_mod.ApplyToOwningParts = False   # ⚠️ QUAN TRỌNG: PART-LEVEL
    disp_mod.NewTranslucency = 0

    all_components = get_all_components(root_component)
    for comp in all_components:
        part = comp.Prototype.OwningPart

        if part is None:
            continue

        # Tránh xử lý lại cùng 1 part
        if part.Tag in processed_parts:
            continue

        processed_parts.add(part.Tag)

        area, bodies = total_body_area(part, uf_session)
        if area is None:
            continue

        existing_color = find_existing_color(area, area_color_pairs)
        if existing_color is None:
            existing_color = random.randint(1, 216)
            area_color_pairs.append((area, existing_color))

        disp_mod.NewColor = existing_color

        # APPLY MÀU CHO BODY CỦA PART
        disp_mod.Apply(bodies)

        lw.WriteLine(
            "Part: {} → Area {:.4f} → Color {}".format(part.Leaf, area, existing_color)
        )

    disp_mod.Dispose()
    lw.WriteLine("DONE")

if __name__ == "__main__":
    main()
