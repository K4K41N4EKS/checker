import os
import shutil
import zipfile
from datetime import datetime, timezone
from tempfile import mkdtemp

from lxml import etree
from docx.oxml.ns import qn

NAMESPACES = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
REL = f"{{{REL_NS}}}Relationship"


def _next_comment_id(comments_root) -> str:
    """Return next unique w:id for comments.xml.
    Uses max existing w:id + 1 to avoid collisions with preexisting comments.
    """
    max_id = -1
    for node in comments_root.xpath("//w:comment", namespaces=NAMESPACES):
        try:
            cid = int(node.get(qn("w:id")))
            if cid > max_id:
                max_id = cid
        except Exception:
            continue
    return str(max_id + 1 if max_id >= 0 else 0)


def _content_children(p):
    """Return content child nodes of a paragraph (exclude w:pPr)."""
    return [c for c in p if c.tag != qn("w:pPr")]


def add_comments_to_docx_batch(docx_path: str, comments: list[dict], inplace: bool = True) -> str:
    """Batch-insert Word comments for given paragraph indices.

    comments: list of {"paragraph_index": int, "error": str}
    Returns target .docx path with comments added.
    """
    temp_dir = mkdtemp()
    try:
        # Unpack the DOCX
        with zipfile.ZipFile(docx_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        document_xml = os.path.join(temp_dir, "word", "document.xml")
        comments_xml = os.path.join(temp_dir, "word", "comments.xml")
        rels_xml = os.path.join(temp_dir, "word", "_rels", "document.xml.rels")
        content_types_xml = os.path.join(temp_dir, "[Content_Types].xml")

        # Ensure comments.xml exists
        if not os.path.exists(comments_xml):
            root = etree.Element(qn("w:comments"), nsmap={"w": NAMESPACES["w"]})
            etree.ElementTree(root).write(
                comments_xml, xml_declaration=True, encoding="UTF-8", standalone="yes"
            )

        # Load trees
        doc_tree = etree.parse(document_xml)
        doc_root = doc_tree.getroot()
        # include paragraphs inside tables as well
        paragraphs = doc_root.xpath("//w:body//w:p", namespaces=NAMESPACES)

        comments_tree = etree.parse(comments_xml)
        comments_root = comments_tree.getroot()

        # Pre-compute next comment id once (performance)
        try:
            next_id_int = int(_next_comment_id(comments_root))
        except Exception:
            next_id_int = 0

        # Insert comments
        for item in comments:
            idx = item.get("paragraph_index")
            text = item.get("error")
            if idx is None or text is None:
                continue
            if not isinstance(idx, int) or idx < 0 or idx >= len(paragraphs):
                continue

            target_p = paragraphs[idx]
            # Prefer any paragraph child (excluding w:pPr) as anchor; covers fldSimple/sdt/etc.
            text_nodes = _content_children(target_p)

            # If paragraph has no content children, create a run to anchor the comment
            if not text_nodes:
                r = etree.SubElement(target_p, qn("w:r"))
                etree.SubElement(r, qn("w:t")).text = ""
                text_nodes = [r]

            comment_id = str(next_id_int)
            next_id_int += 1

            comment = etree.Element(
                qn("w:comment"),
                {
                    qn("w:author"): "Checker",
                    qn("w:initials"): "CHK",
                    qn("w:date"): datetime.now(timezone.utc)
                    .replace(microsecond=0)
                    .isoformat(),
                    qn("w:id"): comment_id,
                },
            )
            p = etree.SubElement(comment, qn("w:p"))
            r = etree.SubElement(p, qn("w:r"))
            t = etree.SubElement(r, qn("w:t"))
            t.text = str(text)
            comments_root.append(comment)

            comment_start = etree.Element(qn("w:commentRangeStart"), {qn("w:id"): comment_id})
            comment_end = etree.Element(qn("w:commentRangeEnd"), {qn("w:id"): comment_id})
            comment_ref = etree.Element(qn("w:r"))
            etree.SubElement(comment_ref, qn("w:commentReference"), {qn("w:id"): comment_id})

            # Insert so that start/end are siblings of top-level text nodes of the paragraph,
            # not inside wrappers like w:hyperlink (Word expects them directly under w:p)
            first_text_node = text_nodes[0]
            last_text_node = text_nodes[-1]
            first_text_node.addprevious(comment_start)
            last_text_node.addnext(comment_end)
            comment_end.addnext(comment_ref)

        # Persist XML updates
        doc_tree.write(document_xml, xml_declaration=True, encoding="UTF-8", standalone="yes")
        comments_tree.write(comments_xml, xml_declaration=True, encoding="UTF-8", standalone="yes")

        # Ensure relationship to comments exists
        if os.path.exists(rels_xml):
            rels_tree = etree.parse(rels_xml)
            rels_root = rels_tree.getroot()
            rel_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
            # Check existing relationships with correct namespace
            has_rel = any(
                (el.tag == REL and el.get("Type") == rel_type and el.get("Target") == "comments.xml")
                for el in rels_root
            )
            if not has_rel:
                # Compute next rId as max existing numeric suffix + 1
                import re

                ids = [el.get("Id", "") for el in rels_root if el.tag == REL]
                nums = []
                for i in ids:
                    m = re.match(r"rId(\d+)$", i)
                    if m:
                        try:
                            nums.append(int(m.group(1)))
                        except Exception:
                            pass
                next_num = (max(nums) + 1) if nums else 1
                rel_id = f"rId{next_num}"
                etree.SubElement(
                    rels_root,
                    REL,
                    {"Id": rel_id, "Type": rel_type, "Target": "comments.xml"},
                )
                rels_tree.write(rels_xml, xml_declaration=True, encoding="UTF-8", standalone="yes")

        # Ensure content type mapping exists
        ct_tree = etree.parse(content_types_xml)
        ct_root = ct_tree.getroot()
        override_tag = "{http://schemas.openxmlformats.org/package/2006/content-types}Override"
        has_override = any(
            el.tag == override_tag and el.attrib.get("PartName") == "/word/comments.xml" for el in ct_root
        )
        if not has_override:
            etree.SubElement(
                ct_root,
                "{http://schemas.openxmlformats.org/package/2006/content-types}Override",
                {
                    "PartName": "/word/comments.xml",
                    "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
                },
            )
            ct_tree.write(content_types_xml, xml_declaration=True, encoding="UTF-8", standalone="yes")

        # Repack DOCX
        base, ext = os.path.splitext(docx_path)
        target_path = docx_path if inplace else f"{base}_with_comment{ext}"
        with zipfile.ZipFile(target_path, "w", compression=zipfile.ZIP_DEFLATED) as new_zip:
            for foldername, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    arcname = os.path.relpath(filepath, temp_dir)
                    new_zip.write(filepath, arcname)

        return target_path

    finally:
        shutil.rmtree(temp_dir)
