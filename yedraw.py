# Вспомогательный модуль для создания файлов yEd
# См. методы класса YedFile

from lxml import etree
from copy import deepcopy

# Шаблоны yEd
#
EMPTY_YED = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <!--Created by yEd 3.19-->
  <key attr.name="Description" attr.type="string" for="graph" id="d0"/>
  <key for="port" id="d1" yfiles.type="portgraphics"/>
  <key for="port" id="d2" yfiles.type="portgeometry"/>
  <key for="port" id="d3" yfiles.type="portuserdata"/>
  <key attr.name="url" attr.type="string" for="node" id="d4"/>
  <key attr.name="description" attr.type="string" for="node" id="d5"/>
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <key for="graphml" id="d7" yfiles.type="resources"/>
  <key attr.name="url" attr.type="string" for="edge" id="d8"/>
  <key attr.name="description" attr.type="string" for="edge" id="d9"/>
  <key for="edge" id="d10" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <data key="d0" xml:space="preserve"/>
  </graph>
  <data key="d7">
    <y:Resources/>
  </data>
</graphml>
'''  # пустой файл
SAMPLE_YED = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <!--Created by yEd 3.19-->
  <key attr.name="Description" attr.type="string" for="graph" id="d0"/>
  <key for="port" id="d1" yfiles.type="portgraphics"/>
  <key for="port" id="d2" yfiles.type="portgeometry"/>
  <key for="port" id="d3" yfiles.type="portuserdata"/>
  <key attr.name="url" attr.type="string" for="node" id="d4"/>
  <key attr.name="description" attr.type="string" for="node" id="d5"/>
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <key for="graphml" id="d7" yfiles.type="resources"/>
  <key attr.name="url" attr.type="string" for="edge" id="d8"/>
  <key attr.name="description" attr.type="string" for="edge" id="d9"/>
  <key for="edge" id="d10" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <data key="d0"/>
    <node id="n0">
      <data key="d6">
        <y:GenericNode configuration="com.yworks.entityRelationship.big_entity">
          <y:Geometry height="156.04999999999995" width="259.1499999999999" x="0.0" y="-176.04999999999998"/>
          <y:Fill color="#E8EEF7" color2="#B7C9E3" transparent="false"/>
          <y:BorderStyle color="#000000" type="line" width="1.0"/>
          <y:NodeLabel alignment="center" autoSizePolicy="content" backgroundColor="#99CCFF" configuration="com.yworks.entityRelationship.label.name" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasLineColor="false" height="18.1328125" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="28.837890625" x="115.15605468749996" xml:space="preserve" y="4.0">AAA</y:NodeLabel>
          <y:NodeLabel alignment="left" autoSizePolicy="content" configuration="com.yworks.entityRelationship.label.attributes" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="32.265625" horizontalTextPosition="center" iconTextGap="4" modelName="custom" textColor="#000000" verticalTextPosition="top" visible="true" width="55.05859375" x="2.0" xml:space="preserve" y="30.1328125">TEXT_A1
TEXT_A2
<y:LabelModel><y:ErdAttributesNodeLabelModel/></y:LabelModel><y:ModelParameter><y:ErdAttributesNodeLabelModelParameter/></y:ModelParameter></y:NodeLabel>
          <y:StyleProperties>
            <y:Property class="java.lang.Boolean" name="y.view.ShadowNodePainter.SHADOW_PAINTING" value="true"/>
          </y:StyleProperties>
        </y:GenericNode>
      </data>
    </node>
    <node id="n1">
      <data key="d6">
        <y:GenericNode configuration="com.yworks.entityRelationship.big_entity">
          <y:Geometry height="156.04999999999995" width="259.1499999999999" x="370.15" y="-172.04999999999998"/>
          <y:Fill color="#E8EEF7" color2="#B7C9E3" transparent="false"/>
          <y:BorderStyle color="#000000" type="line" width="1.0"/>
          <y:NodeLabel alignment="center" autoSizePolicy="content" backgroundColor="#99CCFF" configuration="com.yworks.entityRelationship.label.name" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasLineColor="false" height="18.1328125" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="24.70703125" x="117.22148437499993" xml:space="preserve" y="4.0">BBB</y:NodeLabel>
          <y:NodeLabel alignment="left" autoSizePolicy="content" configuration="com.yworks.entityRelationship.label.attributes" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="32.265625" horizontalTextPosition="center" iconTextGap="4" modelName="custom" textColor="#000000" verticalTextPosition="top" visible="true" width="53.681640625" x="2.0" xml:space="preserve" y="30.1328125">TEXT_B1
TEXT_B2
<y:LabelModel><y:ErdAttributesNodeLabelModel/></y:LabelModel><y:ModelParameter><y:ErdAttributesNodeLabelModelParameter/></y:ModelParameter></y:NodeLabel>
          <y:StyleProperties>
            <y:Property class="java.lang.Boolean" name="y.view.ShadowNodePainter.SHADOW_PAINTING" value="true"/>
          </y:StyleProperties>
        </y:GenericNode>
      </data>
    </node>
    <edge id="e0" source="n0" target="n1">
      <data key="d9"/>
      <data key="d10">
        <y:PolyLineEdge>
          <y:Path sx="0.0" sy="0.0" tx="0.0" ty="0.0"/>
          <y:LineStyle color="#000000" type="line" width="1.0"/>
          <y:Arrows source="none" target="standard"/>
          <y:BendStyle smoothed="false"/>
        </y:PolyLineEdge>
      </data>
    </edge>
  </graph>
  <data key="d7">
    <y:Resources/>
  </data>
</graphml>
'''  # сущность и связь
GROUP_YED = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <!--Created by yEd 3.20-->
  <key attr.name="Description" attr.type="string" for="graph" id="d0"/>
  <key for="port" id="d1" yfiles.type="portgraphics"/>
  <key for="port" id="d2" yfiles.type="portgeometry"/>
  <key for="port" id="d3" yfiles.type="portuserdata"/>
  <key attr.name="url" attr.type="string" for="node" id="d4"/>
  <key attr.name="description" attr.type="string" for="node" id="d5"/>
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <key for="graphml" id="d7" yfiles.type="resources"/>
  <key attr.name="url" attr.type="string" for="edge" id="d8"/>
  <key attr.name="description" attr.type="string" for="edge" id="d9"/>
  <key for="edge" id="d10" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <data key="d0"/>
    <node id="n0" yfiles.foldertype="group">
      <data key="d4" xml:space="preserve"/>
      <data key="d5"/>
      <data key="d6">
        <y:ProxyAutoBoundsNode>
          <y:Realizers active="0">
            <y:GroupNode>
              <y:Geometry height="50.0" width="50.0" x="248.0" y="168.0"/>
              <y:Fill color="#F5F5F5" transparent="false"/>
              <y:BorderStyle color="#000000" type="dashed" width="1.0"/>
              <y:NodeLabel alignment="right" autoSizePolicy="node_width" backgroundColor="#EBEBEB" borderDistance="0.0" fontFamily="Dialog" fontSize="15" fontStyle="plain" hasLineColor="false" height="22.37646484375" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="50.0" x="0.0" xml:space="preserve" y="0.0">1</y:NodeLabel>
              <y:Shape type="roundrectangle"/>
              <y:State closed="false" closedHeight="50.0" closedWidth="50.0" innerGraphDisplayEnabled="false"/>
              <y:Insets bottom="15" bottomF="15.0" left="15" leftF="15.0" right="15" rightF="15.0" top="15" topF="15.0"/>
              <y:BorderInsets bottom="0" bottomF="0.0" left="0" leftF="0.0" right="0" rightF="0.0" top="0" topF="0.0"/>
            </y:GroupNode>
            <y:GroupNode>
              <y:Geometry height="50.0" width="50.0" x="248.0" y="168.0"/>
              <y:Fill color="#F5F5F5" transparent="false"/>
              <y:BorderStyle color="#000000" type="dashed" width="1.0"/>
              <y:NodeLabel alignment="right" autoSizePolicy="node_width" backgroundColor="#EBEBEB" borderDistance="0.0" fontFamily="Dialog" fontSize="15" fontStyle="plain" hasLineColor="false" height="22.37646484375" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="50.0" x="0.0" xml:space="preserve" y="0.0">1</y:NodeLabel>
              <y:Shape type="roundrectangle"/>
              <y:State closed="true" closedHeight="50.0" closedWidth="50.0" innerGraphDisplayEnabled="false"/>
              <y:Insets bottom="15" bottomF="15.0" left="15" leftF="15.0" right="15" rightF="15.0" top="15" topF="15.0"/>
              <y:BorderInsets bottom="0" bottomF="0.0" left="0" leftF="0.0" right="0" rightF="0.0" top="0" topF="0.0"/>
            </y:GroupNode>
          </y:Realizers>
        </y:ProxyAutoBoundsNode>
      </data>
      <graph edgedefault="directed" id="n0:"/>
    </node>
  </graph>
  <data key="d7">
    <y:Resources/>
  </data>
</graphml>
'''  # узел-группа


def xpt(elem, path):
    return elem.xpath(path, namespaces={'y': 'http://www.yworks.com/xml/graphml',
                                        'r': "http://graphml.graphdrawing.org/xmlns"})


SAMPLE_NODE = xpt(etree.XML(bytes(bytearray(SAMPLE_YED, encoding='utf-8'))), '//r:node[1]')[0]
SAMPLE_EDGE = xpt(etree.XML(bytes(bytearray(SAMPLE_YED, encoding='utf-8'))), '//r:edge[1]')[0]
SAMPLE_GROUP = xpt(etree.XML(bytes(bytearray(GROUP_YED, encoding='utf-8'))), '//r:node[1]')[0]


class YedFile:
    def __init__(self):
        """ Заполняем пустым файлом yed при создании"""
        self.xml = etree.XML(bytes(bytearray(EMPTY_YED, encoding='utf-8')))

    def add_node(self, node_uid, label, text="", proto=SAMPLE_NODE, group='', style={}):
        """ Добавляет вершину в граф
        :param node_uid: уникальный id, используется при связи ребрами, строка
        :param label: подпись вершины
        :param text: описание, используется в вершинах типа сущность
        :param proto: прототип из которого делается вершина
        :param group: uid группы
        :param style: стиль
        :return: None
        """
        new_node = deepcopy(proto)
        new_node.attrib['id'] = str(node_uid)
        xpt(new_node, '//y:Geometry[1]')[0].attrib['height'] = str((text.count('\n') + label.count('\n')) * 15 + 50)
        xpt(new_node, '//y:NodeLabel[1]')[0].text = str(label)
        xpt(new_node, '//y:NodeLabel[2]')[0].text = str(
            text)  # TODO Не будет работать с вершинами других типов, сделать проверку
        if "BorderStyle" in style:
            if "color" in style['BorderStyle']:
                xpt(new_node, '//y:BorderStyle[1]')[0].attrib['color'] = style['BorderStyle']['color']
            if "type" in style['BorderStyle']:
                xpt(new_node, '//y:BorderStyle[1]')[0].attrib['type'] = style['BorderStyle']['type']
            if "width" in style['BorderStyle']:
                xpt(new_node, '//y:BorderStyle[1]')[0].attrib['width'] = style['BorderStyle']['width']
        if "Fill" in style:
            if "color" in style['Fill']:
                xpt(new_node, '//y:Fill[1]')[0].attrib['color'] = style['Fill']['color']
            if "color2" in style['Fill']:
                xpt(new_node, '//y:Fill[1]')[0].attrib['color2'] = style['Fill']['color2']
        if "NodeLabel" in style:
            if "backgroundColor" in style['NodeLabel']:
                xpt(new_node, '//y:NodeLabel[1]')[0].attrib['backgroundColor'] = style['NodeLabel']['backgroundColor']
        if group == '':
            xpt(self.xml, '//r:graph[1]')[0].append(new_node)
        else:
            xpt(self.xml, '//r:node[@id="' + group + '"]//r:graph[1]')[0].append(new_node)

    def add_group(self, node_uid, label, proto=SAMPLE_GROUP, group=''):
        """ Добавляет группу в граф
        :param node_uid: уникальный id, используется при связи ребрами, строка
        :param label: подпись вершины
        :param proto: прототип из которого делается вершина
         :param group: uid группы
        :return: None
        """
        new_node = deepcopy(proto)
        new_node.attrib['id'] = str(node_uid)
        xpt(new_node, '//y:NodeLabel[1]')[0].text = str(label)
        if group == '':
            xpt(self.xml, '//r:graph[1]')[0].append(new_node)
        else:
             xpt(self.xml, '//r:node[@id="' + group + '"]//r:graph[1]')[0].append(new_node)


    def add_edge(self, source, target, proto=SAMPLE_EDGE, line_type='line', width = '1.0'):  # TODO Сделать подпись ребер?
        """ Добавляет ребро
        :param source: uid начальной вершины
        :param target: uid конечной вершины
        :param proto: прототип из которого создается ребро
        :param line_type - тип линии, например line (сплошная), dashed (пунктирная)
        :param width - толщина линии
        :return: None
        """
        new_edge = deepcopy(proto)
        new_edge.attrib['id'] = str(source) + ":" + str(target)
        new_edge.attrib['source'] = str(source)
        new_edge.attrib['target'] = str(target)
        xpt(new_edge, '//y:LineStyle[1]')[0].attrib['type'] = line_type
        xpt(new_edge, '//y:LineStyle[1]')[0].attrib['width'] = width
        xpt(self.xml, '//r:graph[1]')[0].append(new_edge)

    def get_node(self, node):
        """
        """
        return xpt(self.xml, '//r:node[@id=' + str(node) + ']')[0]

    def change_node_style(self, node, style):
        """
        Изменить стиль существующей вершины
        :param node: id вершины
        :param style: стиль
        :return: None
        """
        if "Fill" in style:
            if "color" in style["Fill"]:
                xpt(self.xml, ".//r:node[@id='" + str(node) + "']//y:Fill[1]")[0].attrib["color"] = style["Fill"]["color"]
            if "color2" in style["Fill"]:
                xpt(self.xml, ".//r:node[@id='" + str(node) + "']//y:Fill[1]")[0].attrib["color2"] = style["Fill"]["color2"]
        if "NodeLabel" in style:
            if "backgroundColor" in style["NodeLabel"]:
                xpt(self.xml, ".//r:node[@id='" + str(node) + "']//y:NodeLabel[1]")[0].attrib["backgroundColor"] = \
                    style["NodeLabel"]["backgroundColor"]

    def save(self, path):
        """
        Сохраняет в файл
        :param path: путь к файлу
        :return:
        """
        f = open(path, 'w')
        f.write(etree.tostring(self.xml, pretty_print=True).decode("utf-8"))
        f.close()


if __name__ == "__main__":
    print("Самостоятельный запуск модуля")
    demo = YedFile()
    demo.add_group('g1', 'Группировка')
    demo.add_group('g2', 'Группа внутри группы',group='g1')
    demo.add_node(1, 'Это первая вершина', 'Текстовое описание для первой вершины')
    demo.add_node(2, 'Это вторая вершина', 'Текстовое описание может быть многострочным\nпри этом размер растягивается\
    \nтолько по вертикали')
    demo.add_node(3, 'Тест группы', 'Вершины можно группировать', group='g1')
    demo.add_node(4, 'При связывании ребрами', 'Группировка не важна', group='g2')
    demo.add_node('node_5', 'Индекс вершины может быть строковым', 'Стиль вершины можно менять после создания', group='g2')
    demo.add_edge(1, 2)
    demo.add_edge(1, 3, width = '4.0')
    demo.add_edge(3, 4, line_type='dashed')
    demo.add_edge('g2', 2)
    demo.change_node_style('node_5', {"Fill": {"color": "#ffcc99", "color2": "#ffcc99"}, "NodeLabel": {"backgroundColor": "#ffcc99"}})
    demo.save('demo.graphml')
