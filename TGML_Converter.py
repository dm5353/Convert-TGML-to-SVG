import math
from lxml import etree
import os
import re

count = 0

def add_element(tag, attribs, element_type, parent_svg, element=None):

    common_attribs = {
        "fill": attribs.get("fill", "none").lower(),
        "stroke": attribs.get("stroke", "none").lower(),
        "stroke-width": attribs.get("strokewidth", "1.0"),
        "stroke-dasharray": attribs.get("strokedasharray", "none").lower(),
        "opacity": attribs.get("opacity", "1.0")
    }


    if 'name' in attribs:
        common_attribs["id"] = attribs["name"]
    if 'visibility' in attribs:
        common_attribs["visibility"] = attribs["visibility"].lower()


    if element_type == 'ellipse':
        cx = float(attribs.get("left", 0)) + float(attribs.get("width", 0)) / 2
        cy = float(attribs.get("top", 0)) + float(attribs.get("height", 0)) / 2
        rx = float(attribs.get("width", 0)) / 2
        ry = float(attribs.get("height", 0)) / 2

        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "ellipse", {
            **common_attribs, "cx": str(cx), "cy": str(cy), "rx": str(rx), "ry": str(ry), "transform" : transform
        })


    if element_type == 'rectangle':
        x, y = float(attribs.get("left", 0)), float(attribs.get("top", 0))
        width, height = float(attribs.get("width", 0)), float(attribs.get("height", 0))
        rx, ry = float(attribs.get("radiusx", 0)), float(attribs.get("radiusy", 0))
        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "rect", {
            **common_attribs, "x": str(x), "y": str(y), "width": str(width), "height": str(height), "rx": str(rx), "ry": str(ry), "transform" : transform
        })


    if element_type == 'path':
        path_data = attribs.get("pathdata", "").replace(",", " ").replace("M", " M ").replace("L", " L ").strip()
        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "path", {**common_attribs, "d": path_data, "transform":transform})


    if element_type == 'pie':
        cx, cy = map(float, attribs.get("center", "0,0").split(","))
        rx = float(attribs.get("radiusx", 0))
        ry = float(attribs.get("radiusy", 0))
        start_angle = float(attribs.get("startangle", 0))
        sweep_angle = float(attribs.get("sweepangle", 90))
        end_angle = start_angle + sweep_angle
        large_arc_flag = "1" if abs(sweep_angle) > 180 else "0"
        sweep_flag = "1" if sweep_angle > 0 else "0"

        d = f"M{cx + rx * math.cos(math.radians(start_angle))},{cy + ry * math.sin(math.radians(start_angle))} "
        d += f"A{rx},{ry} 0 {large_arc_flag},{sweep_flag} {cx + rx * math.cos(math.radians(end_angle))},{cy + ry * math.sin(math.radians(end_angle))} "
        d += f"L{cx},{cy} Z"

        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "path", {**common_attribs, "d": d, "transform":transform})


    if element_type == 'polygon':
        points = attribs.get("points", "").strip()
        transform = process_element_child(element, parent_svg, common_attribs)

        etree.SubElement(parent_svg, "polygon", {
            **common_attribs, "points": points, "transform":transform
        })


    if element_type == 'curve':
        points = attribs.get("points", "").strip()
        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "polyline", {**common_attribs, "points": points, "transform":transform})


    if element_type == 'line':
        x1 = float(attribs.get("x1", 0))
        y1 = float(attribs.get("y1", 0))
        x2 = float(attribs.get("x2", 0))
        y2 = float(attribs.get("y2", 0))
        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "line", {**common_attribs, "x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2), "transform":transform})


    if element_type == 'arc':
        cx, cy = map(float, attribs.get("center", "0,0").split(","))
        rx = float(attribs.get("radiusx", 0))
        ry = float(attribs.get("radiusy", 0))
        start_angle = float(attribs.get("startangle", 0))
        sweep_angle = float(attribs.get("sweepangle", 0))
        end_angle = start_angle + sweep_angle
        large_arc_flag = "1" if abs(sweep_angle) > 180 else "0"
        sweep_flag = "1" if sweep_angle > 0 else "0"

        d = f"M{cx + rx * math.cos(math.radians(start_angle))},{cy + ry * math.sin(math.radians(start_angle))} "
        d += f"A{rx},{ry} 0 {large_arc_flag},{sweep_flag} {cx + rx * math.cos(math.radians(end_angle))},{cy + ry * math.sin(math.radians(end_angle))}"

        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "path", {**common_attribs, "d": d, "transform":transform})

    if element_type == 'polyline':
        points = attribs.get("points", "").strip()
        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "polyline", {**common_attribs, "points": points, "transform":transform})

    if element_type in ['image', 'animatedimage']:
        x = float(attribs.get("left", 0))
        y = float(attribs.get("top", 0))
        width = float(attribs.get("width", 0))
        height = float(attribs.get("height", 0))
        image_data = element.text.strip() if element.text else ""
        if image_data:
            href_data = f"data:image/png;base64,{image_data}"

        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "image", {**common_attribs, "x": str(x), "y": str(y), "width": str(width), "height": str(height), "href": href_data, "transform":transform})

    if element_type in ['text', 'textbox']:
        id = attribs.get("name", "text")
        x = float(attribs.get("left", 0))
        y = float(attribs.get("top", 0))
        font_size = attribs.get("fontsize", "10")
        font_weight = attribs.get("fontweight", "regular")
        text_content = element.text if element.text else attribs.get("content", "")
        text_attribs = {
            "id" : id,
            "x": str(x),
            "y": str(y),
            "font-weight":font_weight,
            "font-size": font_size,
            "font-family": attribs.get("fontfamily", "Arial"),  # Default 'Arial' font family
            "stroke": attribs.get("stroke", "none"),  # Default 'black' stroke color
            "fill": attribs.get("fill", "none"),  # Default 'none' for text fill
        }
        transform = process_element_child(element, parent_svg, common_attribs)
        etree.SubElement(parent_svg, "text", {**text_attribs,"transform":transform}).text = text_content

    if element_type in ['group', 'component']:
        if len(element):
            left = float(attribs.get('left', '0'))
            top = float(attribs.get('top', '0'))
            content_width = float(attribs.get("contentwidth", 1))
            content_height = float(attribs.get("contentheight", 1))
            if content_width == 0:
                content_width = 1
            if content_height == 0:
                content_height = 1
            scale_x = float(attribs.get("width", 1)) / content_width
            scale_y = float(attribs.get("height", 1)) / content_height
            cx, cy = 0,0
            rotation = 0
            transform = f"translate({left},{top}) scale({scale_x},{scale_y})"
            if element is not None:
                for child in element:
                    if child.tag.lower() == "rotate":
                        rotation = float(child.attrib.get("Angle", 0))
                        cx, cy = map(float, child.attrib.get("Center", "0,0").split(','))
                        transform += f" rotate({rotation})"
                    if child.tag.lower() == "scale":
                        scale_x = float(child.attrib.get("ScaleX", 1.0))
                        scale_y = float(child.attrib.get("ScaleY", 1.0))
                        cx, cy = map(float, child.attrib.get("Center", "0,0").split(','))
                        transform += f" scale({scale_x} {scale_y})"
                    if child.tag.lower() == "skewx":
                        skew_x = float(child.attrib.get("Angle", 0))
                        cx, cy = map(float, child.attrib.get("Center", "0,0").split(','))
                        transform += f" skewX({skew_x})"
                    if child.tag.lower() == "skewy":
                        skew_y = float(child.attrib.get("Angle", 0))
                        cx, cy = map(float, child.attrib.get("Center", "0,0").split(','))
                        transform += f" skewY({skew_y})"
                    if child.tag.lower() == "translate":
                        tx = float(child.attrib.get("X", 0))
                        ty = float(child.attrib.get("Y", 0))
                        transform += f" translate({tx} {ty})"

            group_element = etree.SubElement(parent_svg, "g", {**common_attribs, "transform": transform})

            for child in element:
                process_element(child, group_element)

def create_lineargradient(gradient_element):
    global count
    # Extract gradient attributes
    startpoint = gradient_element.attrib.get("StartPoint", "0.0,0.0").split(',')
    endpoint = gradient_element.attrib.get("EndPoint", "0.0,0.0").split(',')
    spread_method = gradient_element.attrib.get("SpreadMethod", "none")
    gradient_id = gradient_element.attrib.get("name", f"gradient_{id(gradient_element)}_{count}")
    attribute = gradient_element.attrib.get("Attribute", "fill").lower()
    
    # Create the linear gradient element
    gradient = etree.Element("linearGradient", {
        "x1": startpoint[0], "y1": startpoint[1], "x2": endpoint[0], "y2": endpoint[1],
        "spreadMethod": spread_method, "id": gradient_id, "attribute": attribute
    })
    
    # Iterate through child GradientStops and add them
    for stop in gradient_element:
        if stop.tag.lower() == "gradientstop":
            color = stop.attrib.get("Color", "#00000000")  # Default color with transparency
            if color == "None":
                color = "#00000000"
                offset = "0"
            offset = stop.attrib.get("Offset", "0")
            if color.startswith("#") and len(color) == 9:  # Format #AARRGGBB
                opacity = int(color[1:3], 16) / 255  # Convert alpha to float between 0 and 1
                rgba_color = f"#{color[3:]}"  # Remove alpha for CSS color
                style = f"stop-color:{rgba_color};stop-opacity:{opacity};"
            else:  # Handle case without alpha
                style = f"stop-color:{color};"
            etree.SubElement(gradient, "stop", {
                "offset": offset, "style": style
            })
    
    count += 1

    return gradient

def create_radialgradient(gradient_element):
    global count
    # Extract gradient attributes
    center = gradient_element.attrib.get("Center", "0.5,0.5").split(',')
    focus = gradient_element.attrib.get("Focus", "0.5,0.5").split(',')
    radius_x = gradient_element.attrib.get("RadiusX", "0.5")
    radius_y = gradient_element.attrib.get("RadiusY", "0.5")
    attribute = gradient_element.attrib.get("Attribute", "fill").lower()
    spread_method = gradient_element.attrib.get("SpreadMethod", "none")
    gradient_id = gradient_element.attrib.get("name", f"gradient_{id(gradient_element)}_{count}")
    
    # Create the radial gradient element
    gradient = etree.Element("radialGradient", {
        "cx": center[0], "cy": center[1], "fx": focus[0], "fy": focus[1],
        "rx": radius_x, "ry": radius_y, "spreadMethod": spread_method, "id": gradient_id,
        "attribute": attribute
    })
    
    # Iterate through child GradientStops and add them
    for stop in gradient_element:
        if stop.tag.lower() == "gradientstop":
            color = stop.attrib.get("Color", "#00000000")  # Default color with transparency
            if color == "None":
                color = "#00000000"
                offset = "0"
            offset = stop.attrib.get("Offset", "0")
            if color.startswith("#") and len(color) == 9:  # Format #AARRGGBB
                opacity = int(color[1:3], 16) / 255  # Convert alpha to float between 0 and 1
                rgba_color = f"#{color[3:]}"  # Remove alpha for CSS color
                style = f"stop-color:{rgba_color};stop-opacity:{opacity};"
            else:  # Handle case without alpha
                style = f"stop-color:{color};"
            etree.SubElement(gradient, "stop", {
                "offset": offset, "style": style
            })
    
    count += 1

    return gradient

def process_element_child(element, parent_svg, common_attribs):
    transform = ""

    if element is not None:
        for child in element:
            if child.tag.lower() == "lineargradient":
                gradient_element = create_lineargradient(child)
                parent_svg.append(gradient_element)
                common_attribs[gradient_element.get('attribute')] = f"url(#{gradient_element.get('id')})"
            if child.tag.lower() == "radialgradient":
                gradient_element = create_radialgradient(child)
                parent_svg.append(gradient_element)
                common_attribs[gradient_element.get('attribute')] = f"url(#{gradient_element.get('id')})"
            if child.tag.lower() == "rotate":
                rotation = float(child.attrib.get("Angle", 0))
                cx, cy = map(float, child.attrib.get("Center", "0,0").split(","))
                transform += f" rotate({rotation})"
            if child.tag.lower() == "scale":
                scale_x = float(child.attrib.get("ScaleX", 1.0))
                scale_y = float(child.attrib.get("ScaleY", 1.0))
                cx, cy = map(float, child.attrib.get("Center", "0,0").split(','))
                transform += f" scale({scale_x} {scale_y})"
            if child.tag.lower() == "skewx":
                skew_x = float(child.attrib.get("Angle", 0))
                cx, cy = map(float, child.attrib.get("Center", "0,0").split(','))
                transform += f" skewX({skew_x})"
            if child.tag.lower() == "skewy":
                skew_y = float(child.attrib.get("Angle", 0))
                cx, cy = map(float, child.attrib.get("Center", "0,0").split(','))
                transform += f" skewY({skew_y})"
            if child.tag.lower() == "translate":
                tx = float(child.attrib.get("X", 0))
                ty = float(child.attrib.get("Y", 0))
                transform += f" translate({tx} {ty})"

        return transform.strip()

def process_element(element, parent_svg):

    tag = element.tag.lower()
    attribs = {k.lower(): v for k, v in element.attrib.items()}

    if tag == 'tgml':
        # Обработка дочерних элементов для корневого тега
        for child in element:
            process_element(child, parent_svg)
    else:
        # Добавление элемента в SVG
        add_element(tag, attribs, tag, parent_svg, element)

def convert_tgml_to_svg(tgml_content):
    try:
        root = etree.fromstring(tgml_content)

        canvas_width = float(root.attrib.get("Width", "1920"))
        canvas_height = float(root.attrib.get("Height", "1080"))

        svg = etree.Element(
            'svg',
            xmlns="http://www.w3.org/2000/svg",
            xlink="http://www.w3.org/1999/xlink",
            version="1.1",
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