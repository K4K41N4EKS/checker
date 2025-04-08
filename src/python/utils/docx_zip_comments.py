import zipfile
import shutil
import os
from lxml import etree
from tempfile import mkdtemp
from docx.oxml.ns import qn
from datetime import datetime, timezone

NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

def add_comments_to_docx_batch(docx_path: str, comments: list[dict], inplace: bool = True) -> str:
    """
    Добавляет список комментариев в .docx одним проходом.
    comments: список словарей {"paragraph_index": int, "error": str}
    """
    temp_dir = mkdtemp()
    try:
        # Распаковка
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        document_xml = os.path.join(temp_dir, 'word', 'document.xml')
        comments_xml = os.path.join(temp_dir, 'word', 'comments.xml')
        rels_xml = os.path.join(temp_dir, 'word', '_rels', 'document.xml.rels')
        content_types_xml = os.path.join(temp_dir, '[Content_Types].xml')

        if not os.path.exists(comments_xml):
            root = etree.Element(qn('w:comments'), nsmap={'w': NAMESPACES['w']})
            etree.ElementTree(root).write(comments_xml, xml_declaration=True, encoding='UTF-8', standalone='yes')

        # Парсинг
        doc_tree = etree.parse(document_xml)
        doc_root = doc_tree.getroot()
        paragraphs = doc_root.xpath('//w:body/w:p', namespaces=NAMESPACES)

        comments_tree = etree.parse(comments_xml)
        comments_root = comments_tree.getroot()

        # Вставка комментариев
        for i, item in enumerate(comments):
            idx = item.get("paragraph_index")
            text = item.get("error")
            if idx is None or text is None:
                continue
            if idx >= len(paragraphs):
                continue

            target_p = paragraphs[idx]
            runs = target_p.xpath('./w:r', namespaces=NAMESPACES)
            if not runs:
                continue

            comment_id = str(len(comments_root))

            comment = etree.Element(qn('w:comment'), {
                qn('w:author'): 'Checker',
                qn('w:initials'): 'CHK',
                qn('w:date'): datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                qn('w:id'): comment_id
            })
            p = etree.SubElement(comment, qn('w:p'))
            r = etree.SubElement(p, qn('w:r'))
            t = etree.SubElement(r, qn('w:t'))
            t.text = text
            comments_root.append(comment)

            comment_start = etree.Element(qn('w:commentRangeStart'), {qn('w:id'): comment_id})
            comment_end = etree.Element(qn('w:commentRangeEnd'), {qn('w:id'): comment_id})
            comment_ref = etree.Element(qn('w:r'))
            etree.SubElement(comment_ref, qn('w:commentReference'), {qn('w:id'): comment_id})

            runs[0].addprevious(comment_start)
            runs[-1].addnext(comment_end)
            comment_end.addnext(comment_ref)

        # Сохранение изменений
        doc_tree.write(document_xml, xml_declaration=True, encoding='UTF-8', standalone='yes')
        comments_tree.write(comments_xml, xml_declaration=True, encoding='UTF-8', standalone='yes')

        # Обновление rels
        if os.path.exists(rels_xml):
            rels_tree = etree.parse(rels_xml)
            rels_root = rels_tree.getroot()
            if not any(rel.get('Type') == 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments' for rel in rels_root):
                rel_id = f"rId{len(rels_root) + 1}"
                etree.SubElement(rels_root, 'Relationship', {
                    'Id': rel_id,
                    'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments',
                    'Target': 'comments.xml'
                })
                rels_tree.write(rels_xml, xml_declaration=True, encoding='UTF-8', standalone='yes')

        # Обновление content types
        ct_tree = etree.parse(content_types_xml)
        ct_root = ct_tree.getroot()
        if not any(el.tag.endswith('Override') and el.attrib.get('PartName') == '/word/comments.xml' for el in ct_root):
            etree.SubElement(ct_root, 'Override', {
                'PartName': '/word/comments.xml',
                'ContentType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml'
            })
            ct_tree.write(content_types_xml, xml_declaration=True, encoding='UTF-8', standalone='yes')

        # Перезапись .docx
        target_path = docx_path if inplace else docx_path.replace('.docx', '_with_comment.docx')
        with zipfile.ZipFile(target_path, 'w') as new_zip:
            for foldername, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    arcname = os.path.relpath(filepath, temp_dir)
                    new_zip.write(filepath, arcname)

        return target_path

    finally:
        shutil.rmtree(temp_dir)
