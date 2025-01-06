import math
from lxml import etree
import os

def add_element(tag, attribs, element_type, parent_svg, element=None):
    common_attribs = {
        "fill": attribs.get("fill", "none"),
        "stroke": attribs.get("stroke", "none"),
        "stroke-width": attribs.get("strokewidth", "1.0"),
        "stroke-dasharray": attribs.get("strokedasharray", "none"),
        "opacity": attribs.get("opacity", "1.0")
    }
    if 'name' in attribs:
        common_attribs["id"] = attribs["name"]

    if element_type == 'rectangle':
        x, y = float(attribs.get("left", 0)), float(attribs.get("top", 0))
        width, height = float(attribs.get("width", 0)), float(attribs.get("height", 0))
        rx, ry = float(attribs.get("radiusx", 0)), float(attribs.get("radiusy", 0))
        etree.SubElement(parent_svg, "rect", {
            **common_attribs, "x": str(x), "y": str(y), "width": str(width), "height": str(height), "rx" : str(rx), "ry":str(ry)
        })

    elif element_type == 'path':
        path_data = attribs.get("pathdata", "").replace(",", " ").replace("M", " M ").replace("L", " L ").strip()
        etree.SubElement(parent_svg, "path", {**common_attribs, "d": path_data})


    elif element_type == 'text':
        x = float(attribs.get("left", 0)) - float(attribs.get("centerx", 0))
        y = float(attribs.get("top", 0)) - float(attribs.get("centery", 0))
        font_size = attribs.get("fontsize", "12")
        text_content = element.text if element.text else attribs.get("content", "")
        text_attribs = {
            **common_attribs,
            "x": str(x),
            "y": str(y),
            "font-size": font_size,
            "text-anchor": attribs.get("text-anchor", "start"),
            "font-family": attribs.get("fontfamily", "Arial"),
        }
        etree.SubElement(parent_svg, "text", text_attribs).text = text_content

    elif element_type == 'image':
        x = float(attribs.get("left", 0))
        y = float(attribs.get("top", 0))
        width = float(attribs.get("width", 100))
        height = float(attribs.get("height", 100))
        href = attribs.get("src", "")
        etree.SubElement(parent_svg, "image", {
            **common_attribs, "x": str(x), "y": str(y), "width": str(width), "height": str(height), "href": href
        })

    elif element_type == 'polygon':
        points = attribs.get("points", "").strip()
        scale_x = scale_y = 1.0

        # Поиск возможного масштаба внутри элемента
        if element is not None:
            for child in element:
                if child.tag.lower() == "scale":
                    scale_x = float(child.attrib.get("scalex", 1.0))
                    scale_y = float(child.attrib.get("scaley", 1.0))
    
        # Применение трансформации к координатам точек
        scaled_points = []
        for point in points.split():
            x, y = map(float, point.split(","))
            scaled_x = x * scale_x
            scaled_y = y * scale_y
            scaled_points.append(f"{scaled_x},{scaled_y}")
    
        etree.SubElement(parent_svg, "polygon", {
            **common_attribs, "points": " ".join(scaled_points)
        })

    elif element_type == 'curve':
        points = attribs.get("points", "").strip()
        etree.SubElement(parent_svg, "polygon", {**common_attribs, "points": points})

    elif element_type == 'line':
        x1 = float(attribs.get("x1", 0))
        y1 = float(attribs.get("y1", 0))
        x2 = float(attribs.get("x2", 0))
        y2 = float(attribs.get("y2", 0))
        etree.SubElement(parent_svg, "line", {
            **common_attribs, "x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2)
        })

    elif element_type == 'ellipse':
        cx = float(attribs.get("cx", 0))
        cy = float(attribs.get("cy", 0))
        rx = float(attribs.get("rx", 50))
        ry = float(attribs.get("ry", 50))
        etree.SubElement(parent_svg, "ellipse", {
            **common_attribs, "cx": str(cx), "cy": str(cy), "rx": str(rx), "ry": str(ry)
        })

    elif element_type == 'arc':
        cx = float(attribs.get("cx", 0))
        cy = float(attribs.get("cy", 0))
        r = float(attribs.get("radius", 50))
        start_angle = float(attribs.get("startangle", 0))
        end_angle = float(attribs.get("endangle", 90))
        large_arc_flag = "1" if end_angle - start_angle > 180 else "0"
        sweep_flag = "1"
        d = f"M{cx + r * math.cos(math.radians(start_angle))},{cy + r * math.sin(math.radians(start_angle))} "
        d += f"A{r},{r} 0 {large_arc_flag},{sweep_flag} {cx + r * math.cos(math.radians(end_angle))},{cy + r * math.sin(math.radians(end_angle))} "
        etree.SubElement(parent_svg, "path", {**common_attribs, "d": d})

    elif element_type == 'polyline':
        points = attribs.get("points", "").strip()
        etree.SubElement(parent_svg, "polyline", {**common_attribs, "points": points})
    
    elif element_type == 'pie':
        cx = float(attribs.get("centerx", 0))
        cy = float(attribs.get("centery", 0))
        rx = float(attribs.get("radiusx", 50))
        ry = float(attribs.get("radiusy", 50))
        start_angle = float(attribs.get("startangle", 0))
        sweep_angle = float(attribs.get("sweepangle", 90))

        end_angle = start_angle + sweep_angle
        large_arc_flag = "1" if sweep_angle > 180 else "0"
        sweep_flag = "1"

        # Построение пути сектора (pie)
        d = f"M{cx + rx * math.cos(math.radians(start_angle))},{cy + ry * math.sin(math.radians(start_angle))} "
        d += f"A{rx},{ry} 0 {large_arc_flag},{sweep_flag} {cx + rx * math.cos(math.radians(end_angle))},{cy + ry * math.sin(math.radians(end_angle))} "
        d += f"L{cx},{cy} Z"  # Замкнуть путь в центре
        etree.SubElement(parent_svg, "path", {**common_attribs, "d": d})

    elif element_type == 'group' or 'component':
        left = float(attribs.get('left', '0'))
        top = float(attribs.get('top', '0'))
        scale_y = float(attribs.get("scaley", 1))
        scale_x = float(attribs.get("scalex", 1))
        rotation = float(attribs.get("rotation", 0))
        anchor_x = float(attribs.get("centerx", 0))
        anchor_y = float(attribs.get("centery", 0))
        transform = f"translate({left},{top}) rotate({rotation},{anchor_x},{anchor_y}) scale({scale_x},{scale_y})"
        group_element = etree.SubElement(parent_svg, "g", {**common_attribs, "transform": transform})
    
        # Рекурсивная обработка дочерних элементов
        for child in element:
            child_tag = child.tag.lower()
            child_attribs = {k.lower(): v for k, v in child.attrib.items()}
            add_element(child_tag, child_attribs, child_tag, group_element, child)

def process_element(element, parent_svg):
    tag = element.tag.lower()
    attribs = {k.lower(): v for k, v in element.attrib.items()}
    add_element(tag, attribs, tag, parent_svg, element)

def convert_tgml_to_svg(tgml_content):
    try:
        root = etree.fromstring(tgml_content)

        canvas_width = float(root.attrib.get("Width", "1920"))
        canvas_height = float(root.attrib.get("Height", "1080"))

        svg = etree.Element(
            'svg',
            xmlns="http://www.w3.org/2000/svg",
            version="1.0",
            width=str(canvas_width),
            height=str(canvas_height),
            viewBox=f"0 0 {canvas_width} {canvas_height}"
        )

        process_element(root, svg)  # Начинаем обработку с корневого элемента

        return etree.tostring(svg, pretty_print=True, encoding='unicode')

    except Exception as e:
        print(f"Ошибка при преобразовании: {e}")
        return None

def process_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.tgml'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace('.tgml', '.svg'))
            try:
                with open(input_path, 'r', encoding='utf-8') as tgml_file:
                    tgml_content = tgml_file.read()

                svg_content = convert_tgml_to_svg(tgml_content)
                if svg_content:
                    with open(output_path, 'w', encoding='utf-8') as svg_file:
                        svg_file.write(svg_content)
                    print(f"Преобразован: {filename} -> {output_path}")
                else:
                    print(f"Не удалось преобразовать: {filename}")
            except Exception as e:
                print(f"Ошибка с файлом {filename}: {e}")

if __name__ == "__main__":
    input_folder = "C:/Users/Shitfrombitch/Desktop/1"
    output_folder = "C:/Users/Shitfrombitch/Desktop/3"

    process_files(input_folder, output_folder)