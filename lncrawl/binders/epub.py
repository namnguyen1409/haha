import logging
import os
from typing import Dict, List

from ..assets.epub import epub_chapter_xhtml, epub_cover_xhtml, epub_style_css
from ..models.chapter import Chapter

try:
    from ebooklib import epub
except ImportError:
    logging.fatal("Failed to import ebooklib")


logger = logging.getLogger(__name__)

COVER_IMAGE_NAME = "cover.jpg"
STYLE_FILE_NAME = "style.css"
PROJECT_URL = "https://github.com/dipu-bd/lightnovel-crawler"


def bind_epub_book(
    chapter_groups: List[List[Chapter]],  # chapters grouped by volumes
    images: List[str],  # full path of images to add
    book_title: str,
    novel_author: str,
    output_path: str,
    book_cover: str,
    novel_title: str,
    novel_url: str,
    novel_synopsis: str,
    novel_tags: list,
    good_file_name: str,
    suffix: str,  # suffix to the file name
    no_suffix_after_filename: bool = False,
    is_rtl: bool = False,
    language: str = "en",
):
    logger.info("Binding epub for %s", book_title)

    logger.debug("Creating EpubBook instance")
    book = epub.EpubBook()
    book.set_language(language)
    book.set_title(book_title)
    book.add_author(novel_author)
    book.add_metadata('DC', 'description', novel_synopsis)
    book.set_identifier(output_path + suffix)
    if is_rtl:
        book.set_direction("rtl")

    for tag in novel_tags:
        book.add_metadata("DC", "subject", tag)

    logger.debug("Adding %s", STYLE_FILE_NAME)
    style_item = epub.EpubItem(
        file_name=STYLE_FILE_NAME,
        content=epub_style_css(),
        media_type="text/css",
    )
    book.add_item(style_item)

    logger.debug("Adding templates")
    book.set_template("cover", epub_cover_xhtml())
    book.set_template("chapter", epub_chapter_xhtml())

    logger.debug("Adding cover image")
    assert book_cover and os.path.isfile(book_cover), "No book cover"
    with open(book_cover, "rb") as fp:
        book.set_cover(COVER_IMAGE_NAME, fp.read(), create_page=False)
    cover_item = epub.EpubCoverHtml(image_name=COVER_IMAGE_NAME)
    cover_item.add_link(
        href=style_item.file_name,
        rel="stylesheet",
        type="text/css",
    )
    book.add_item(cover_item)

    logger.debug("Creating intro page")
    intro_html = f"""
    <div id="intro">
        <div class="header">
            <h1>{novel_title or "N/A"}</h1>
            <h3>{novel_author}</h3>
        </div>
        <img class="cover" src="{COVER_IMAGE_NAME}">
        <div class="footer">
            <b>Nguồn:</b> <a href="{novel_url}">{novel_url}</a>
            <br>
            <i>Được tạo bởi <b>
            <a href="https://t.me/crawl_ebook_bot">crawl ebook bot</a></b></i>
        </div>
    </div>
    """
    intro_item = epub.EpubHtml(
        title="Intro Page",
        file_name="intro.xhtml",
        content=intro_html,
    )
    intro_item.add_link(
        href=STYLE_FILE_NAME,
        rel="stylesheet",
        type="text/css",
    )
    book.add_item(intro_item)

    if novel_synopsis:
        synopsis_html = f"""
        <div class="synopsis">
            <h1>Synopsis</h1>
            <p>{novel_synopsis}</p>
        </div>
        """
        synopsis_item = epub.EpubHtml(
            title="Synopsis",
            file_name="synopsis.xhtml",
            content=synopsis_html,
        )
        synopsis_item.add_link(
            href=STYLE_FILE_NAME,
            rel="stylesheet",
            type="text/css",
        )
        book.add_item(synopsis_item)

    logger.debug("Creating chapter contents")
    toc = []
    spine = ["cover", intro_item]
    if novel_synopsis:
        spine.append(synopsis_item)
    spine.append("nav")

    for chapters in chapter_groups:
        first_chapter = chapters[0]
        volume_id = first_chapter.volume
        volume_title = first_chapter.volume_title or f"Book ${volume_id}"
        volume_html = f"""
        <div id="volume">
            <h1>{volume_title}</h1>
        </div>
        """
        volume_item = epub.EpubHtml(
            file_name=f"volume_{volume_id}.xhtml",
            content=volume_html,
            title=volume_title,
        )
        volume_item.add_link(
            href=style_item.file_name,
            rel="stylesheet",
            type="text/css",
        )
        book.add_item(volume_item)
        spine.append(volume_item)

        volume_contents = []
        for chapter in chapters:
            # ebooklib does pretty-print for xhtml. minify is useless :(
            chapter_item = epub.EpubHtml(
                file_name=f"chapter_{chapter.id}.xhtml",
                content=str(chapter["body"]),
                title=chapter["title"],
            )
            chapter_item.add_link(
                href=style_item.file_name,
                rel="stylesheet",
                type="text/css",
            )
            book.add_item(chapter_item)
            spine.append(chapter_item)
            volume_contents.append(chapter_item)

        volume_section = epub.Section(volume_title, href=volume_item.file_name)
        toc.append([volume_section, volume_contents])

    book.toc = toc
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    logger.debug("Adding images")
    for image_path in images:
        filename = os.path.basename(image_path)
        with open(image_path, "rb") as fp:
            image_item = epub.EpubImage()
            image_item.file_name = f"images/{filename}"
            image_item.media_type = "image/jpeg"
            image_item.content = fp.read()
        book.add_item(image_item)

    logger.debug("Saving epub file")
    file_name = good_file_name
    if not no_suffix_after_filename:
        file_name += " " + suffix

    epub_path = os.path.join(output_path, "epub")
    file_path = os.path.join(epub_path, file_name + ".epub")

    logger.info("Writing %s", file_path)
    os.makedirs(epub_path, exist_ok=True)
    epub.write_epub(file_path, book, {})

    print("Created: %s.epub" % file_name)
    return file_path


def make_epubs(app, data: Dict[str, List[Chapter]]) -> List[str]:
    from ..core.app import App

    assert isinstance(app, App)

    epub_files = []
    for volume, chapters in data.items():
        if not chapters:
            continue

        book_title = (app.crawler.novel_title + " " + volume).strip()
        volumes: Dict[int, List[Chapter]] = {}
        for chapter in chapters:
            suffix = chapter.volume or 1
            volumes.setdefault(suffix, []).append(chapter)

        images = []
        image_path = os.path.join(app.output_path, "images")
        if os.path.isdir(image_path):
            images = {
                os.path.join(image_path, filename)
                for filename in os.listdir(image_path)
                if filename.endswith(".jpg")
            }

        output = bind_epub_book(
            chapter_groups=list(volumes.values()),
            images=images,
            suffix=volume,
            book_title=book_title,
            novel_title=app.crawler.novel_title,
            novel_author=app.crawler.novel_author or app.crawler.home_url,
            novel_url=app.crawler.novel_url,
            novel_synopsis=app.crawler.novel_synopsis,
            language=app.crawler.language,
            novel_tags=app.crawler.novel_tags,
            output_path=app.output_path,
            book_cover=app.book_cover,
            good_file_name=app.good_file_name,
            no_suffix_after_filename=app.no_suffix_after_filename,
        )
        epub_files.append(output)
    return epub_files
