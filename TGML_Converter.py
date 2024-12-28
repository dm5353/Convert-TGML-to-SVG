import math
from lxml import etree
import os

def convert_tgml_to_svg(tgml_content):
    """
    Преобразует TGML содержимое в SVG формат с поддержкой всех тегов
    и точным использованием атрибутов TGML.
    """
    try:
        # Парсим TGML
        root = etree.fromstring(tgml_content)

        # Определяем размеры холста TGML
        canvas_width = root.attrib.get("Width", "500")
        canvas_height = root.attrib.get("Height", "500")

        # Создаем SVG корневой элемент с сохранением размеров
        svg = etree.Element(
            'svg',
            xmlns="http://www.w3.org/2000/svg",
            version="1.1",
            width=canvas_width,
            height=canvas_height,
            viewBox=f"-10 -10 {canvas_width} {canvas_height}"
        )

        # Функция для добавления элементов в SVG
        def add_element(tag, attribs, element_type, parent_svg):
            """
            Добавляет элементы в SVG на основе типа элемента (path, rect, etc.)
            """
            common_attribs = {
                "fill": attribs.get("fill", "none"),
                "stroke": attribs.get("stroke", "none"),
                "stroke-width": attribs.get("strokewidth", "1.0"),
                "opacity": attribs.get("opacity", "1.0")
            }

            # Добавляем имя элемента как атрибут id, если оно есть
            if 'name' in attribs:
                common_attribs["id"] = attribs["name"]

            if element_type == 'component':
                # Создаем группу для компонента
                group_attribs = {
                    "transform": attribs.get("transform", ""),
                    "id": attribs.get("name", "")
                }
                group = etree.SubElement(parent_svg, "g", group_attribs)

                # Обработка вложенных элементов
                for child in attribs.get("children", []):
                    child_attribs = {k.lower(): v for k, v in child.attrib.items()}
                    add_element(child.tag.lower(), child_attribs, child.tag.lower(), group)

            elif element_type == 'rect':
                x = float(attribs.get("left", 0))
                y = float(attribs.get("top", 0))
                rx = float(attribs.get("cornerRadiusX", 0))
                ry = float(attribs.get("cornerRadiusY", 0))
                width = float(attribs.get("width", 0))
                height = float(attribs.get("height", 0))
                
                # Если есть LinearGradient
                if 'gradient' in attribs:
                    gradient = etree.SubElement(parent_svg, "linearGradient", {"id": "grad1", "x1": "0%", "y1": "0%", "x2": "100%", "y2": "100%"})
                    gradient_stop1 = etree.SubElement(gradient, "stop", {"offset": "0%", "style": "stop-color:" + attribs.get("gradientstart", "#50000000") + ";stop-opacity:1"})
                    gradient_stop2 = etree.SubElement(gradient, "stop", {"offset": "100%", "style": "stop-color:" + attribs.get("gradientend", "#50FFFFFF") + ";stop-opacity:1"})
                    common_attribs["fill"] = "url(#grad1)"

                etree.SubElement(parent_svg, "rect", {**common_attribs, "x": str(x), "y": str(y), "width": str(width), "height": str(height)})

            elif element_type == 'polyline':
                points = attribs.get("points", "")
                x = float(attribs.get("left", 0))
                y = float(attribs.get("top", 0))
                width = float(attribs.get("width", 0))
                height = float(attribs.get("height", 0))
                etree.SubElement(parent_svg, "polyline", {**common_attribs, "points": points, "x": str(x), "y": str(y), "width": str(width), "height": str(height)})

            elif element_type == 'path':
                path_data = attribs.get("pathdata", "")
                etree.SubElement(parent_svg, "path", {**common_attribs, "d": path_data})

            elif element_type == 'curve':
                points = attribs.get("points", "")
                x = float(attribs.get("left", 0))
                y = float(attribs.get("top", 0))
                width = float(attribs.get("width", 0))
                height = float(attribs.get("height", 0))
                etree.SubElement(parent_svg, "path", {**common_attribs, "d": f"M{points}", "x": str(x), "y": str(y), "width": str(width), "height": str(height)})

            elif element_type == 'line':
                x1 = float(attribs.get("x1", 0))
                y1 = float(attribs.get("y1", 0))
                x2 = float(attribs.get("x2", 100))
                y2 = float(attribs.get("y2", 100))
                width = float(attribs.get("width", 0))
                height = float(attribs.get("height", 0))
                etree.SubElement(parent_svg, "line", {**common_attribs, "x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2), "width": str(width), "height": str(height)})

            elif element_type == 'circle':
                cx = float(attribs.get("cx", 0))
                cy = float(attribs.get("cy", 0))
                r = float(attribs.get("r", 50))
                width = float(attribs.get("width", 0))
                height = float(attribs.get("height", 0))
                etree.SubElement(parent_svg, "circle", {**common_attribs, "cx": str(cx), "cy": str(cy), "r": str(r), "width": str(width), "height": str(height)})

            elif element_type == 'text':
                x = float(attribs.get("x", 0))
                y = float(attribs.get("y", 0))
                font_size = attribs.get("fontsize", "12")
                text_content = attribs.get("content", "")
                etree.SubElement(parent_svg, "text", {**common_attribs, "x": str(x), "y": str(y), "font-size": font_size}).text = text_content

            elif element_type == 'g':  # Группировка элементов
                group = etree.SubElement(parent_svg, "g")
                return group  # Возвращаем ссылку на группу для добавления вложенных элементов
            

            elif element_type == 'ellipse':
                cx = float(attribs.get("left", 0)) + float(attribs.get("width", 100)) / 2
                cy = float(attribs.get("top", 0)) + float(attribs.get("height", 100)) / 2
                rx = float(attribs.get("width", 100)) / 2
                ry = float(attribs.get("height", 100)) / 2
                width = float(attribs.get("width", 0))
                height = float(attribs.get("height", 0))
                fill = attribs.get("fill", "none")
                stroke = attribs.get("stroke", "none")
                stroke_width = attribs.get("strokewidth", "1.0")
                strokedasharray = attribs.get("strokedasharray", "none")

                etree.SubElement(parent_svg, "ellipse", {
                    "cx": str(cx),
                    "cy": str(cy),
                    "rx": str(rx),
                    "ry": str(ry),
                    "fill": fill,
                    "stroke": stroke,
                    "stroke-width": stroke_width,
                    "stroke-dasharray": strokedasharray,
                    "width": str(width),
                    "height": str(height)
                })

            elif element_type == 'polygon':
                points = attribs.get("points", "")
                x = float(attribs.get("left", 0))
                y = float(attribs.get("top", 0))
                width = float(attribs.get("width", 0))
                height = float(attribs.get("height", 0))
                etree.SubElement(parent_svg, "polygon", {**common_attribs, "points": points, "x": str(x), "y": str(y), "width": str(width), "height": str(height)})

            elif element_type == 'image':
                x = float(attribs.get("x", 0))
                y = float(attribs.get("y", 0))
                width = float(attribs.get("width", 100))
                height = float(attribs.get("height", 100))
                href = attribs.get("href", "")
                etree.SubElement(parent_svg, "image", {**common_attribs, "x": str(x), "y": str(y), "width": str(width), "height": str(height), "href": href})

            elif element_type == 'bind':
                attribute = attribs.get("attribute", "")
                name = attribs.get("name", "")
                prevent_default = attribs.get("preventdefault", "False")
                etree.SubElement(parent_svg, "bind", {**common_attribs, "attribute": str(attribute), "name": str(name), "prevent_default": str(prevent_default)})

            elif element_type == 'arc':
                # Получаем параметры дуги
                center = attribs.get("center", "0,0")
                radius_x = float(attribs.get("radiusx", 0))
                radius_y = float(attribs.get("radiusy", 0))
                start_angle = float(attribs.get("startangle", 0))
                sweep_angle = float(attribs.get("sweepangle", 0))
                fill = attribs.get("fill", "none")
                stroke = attribs.get("stroke", "none")
                stroke_width = attribs.get("strokewidth", "1.0")
    
                # Разделяем координаты центра
                cx, cy = map(float, center.split(","))

                # Вычисляем начальную и конечную точки дуги
                start_x = cx + radius_x * math.cos(math.radians(start_angle))
                start_y = cy + radius_y * math.sin(math.radians(start_angle))
                end_x = cx + radius_x * math.cos(math.radians(start_angle + sweep_angle))
                end_y = cy + radius_y * math.sin(math.radians(start_angle + sweep_angle))

                # Определяем флаги
                large_arc_flag = "1" if abs(sweep_angle) > 180 else "0"
                sweep_flag = "1" if sweep_angle > 0 else "0"

                # Создаем path
                path_data = f"M {start_x},{start_y} A {radius_x},{radius_y} 0 {large_arc_flag},{sweep_flag} {end_x},{end_y}"

                etree.SubElement(parent_svg, "path", {
                    "d": path_data,
                    "fill": fill,
                    "stroke": stroke,
                    "stroke-width": stroke_width,
                })

        # Обработка элементов TGML
        for element in root.iter():
            tag = element.tag.lower()
            attribs = {k.lower(): v for k, v in element.attrib.items()}

            # Обработка каждого тега
            if tag == "rectangle":
                add_element(tag, attribs, "rect", svg)

            elif tag == "component":
                add_element(tag, attribs, "component", svg)

            elif tag == "arc":
                add_element(tag, attribs, "arc", svg)

            elif tag == "bind":
                add_element(tag, attribs, "bind", svg)

            elif tag == "polyline":
                add_element(tag, attribs, "polyline", svg)

            elif tag == "path":
                add_element(tag, attribs, "path", svg)

            elif tag == "curve":
                add_element(tag, attribs, "curve", svg)

            elif tag == "line":
                add_element(tag, attribs, "line", svg)

            elif tag == "circle":
                add_element(tag, attribs, "circle", svg)

            elif tag == "text":
                add_element(tag, attribs, "text", svg)

            elif tag == "group":
                group = add_element(tag, attribs, "g", svg)
                # Добавление вложенных элементов в группу
                for child in element:
                    child_attribs = {k.lower(): v for k, v in child.attrib.items()}
                    add_element(child.tag.lower(), child_attribs, child.tag.lower(), group)

            elif tag == "ellipse":
                add_element(tag, attribs, "ellipse", svg)

            elif tag == "polygon":
                add_element(tag, attribs, "polygon", svg)

            elif tag == "image":
                add_element(tag, attribs, "image", svg)
            

        # Возвращаем строку SVG
        return etree.tostring(svg, pretty_print=True, encoding='unicode')

    except Exception as e:
        print(f"Ошибка при преобразовании: {e}")
        return None

def process_files(input_folder, output_folder):
    """
    Преобразует все файлы TGML в папке в SVG и сохраняет в другой папке.
    """
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
    input_folder = "C:/Users/Shitfrombitch/Desktop/1"  # Укажите путь к папке с TGML файлами
    output_folder = "C:/Users/Shitfrombitch/Desktop/2"  # Укажите путь для сохранения SVG файлов

    process_files(input_folder, output_folder)
