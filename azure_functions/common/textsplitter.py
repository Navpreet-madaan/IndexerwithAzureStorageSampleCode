"This file contains the class that splits pages into smaller chunks."
from typing import List, Tuple

from common.splitpage import SplitPage
from helpers.configmapper import ConfigMapper


class TextSplitter:
    """
    Class that splits pages into smaller chunks.
    This is required because embedding models may not be able to analyze
    an entire page at once
    """

    def __init__(self, config_mapper: ConfigMapper):
        self.max_section_length = int(config_mapper.max_section_length)
        self.sentence_limit = int(config_mapper.sentence_search_limit)
        self.sec_overlap = int(config_mapper.section_overlap)
        self.verbose = config_mapper.verbose
        self.has_image_embeddings = config_mapper.has_image_embeddings
        self.end_chars = (
            list(config_mapper.sentence_endings)
            if config_mapper.sentence_endings
            else [".", "!", "?"]
        )
        self.word_breaks = (
            list(config_mapper.word_breaks) if config_mapper.word_breaks else []
        )

    def split_pages(self, rows: List[Tuple[int, str]]):
        "Chunking is disabled when using GPT4V. To be updated in the future."
        if self.has_image_embeddings:
            for _, (page_num, text) in enumerate(rows):
                # Yield a SplitPage object for each row
                yield SplitPage(page_num=page_num, text=text)

        def find_page(offset, rows):
            # finding pages within the SQL stored database related to file
            num_rows = len(rows)
            for i in range(num_rows - 1):
                if offset >= rows[i][0] and offset < rows[i + 1][0]:
                    return rows[i][0]
            return rows[num_rows - 1][0]

        def process_pages(rows):
            "collecting text out of each page"
            all_text = "".join(text for _, text in rows)
            if len(all_text.strip()) == 0:
                return
            length = len(all_text)
            if length <= self.max_section_length:
                yield SplitPage(page_num=find_page(0, rows), text=all_text)
                return
            start = 0
            end = length
            while start + self.sec_overlap < length:
                last_word = -1
                end = start + self.max_section_length
                if end > length:
                    end = length
                else:
                    # Try to find the end of the sentence
                    while (
                        end < length
                        and (end - start - self.max_section_length)
                        < self.sentence_limit
                        and all_text[end] not in self.end_chars
                    ):
                        if all_text[end] in self.word_breaks:
                            last_word = end
                        end += 1
                    if (
                        end < length
                        and all_text[end] not in self.end_chars
                        and last_word > 0
                    ):
                        end = last_word
                if end < length:
                    end += 1
                # Try to find the start of the sentence or
                # at least a whole word boundary
                last_word = -1
                while (
                    start > 0
                    and start > end - self.max_section_length - 2 * self.sentence_limit
                    and all_text[start] not in self.end_chars
                ):
                    if all_text[start] in self.word_breaks:
                        last_word = start
                    start -= 1
                if all_text[start] not in self.end_chars and last_word > 0:
                    start = last_word
                if start > 0:
                    start += 1
                section_text = all_text[start:end]
                yield SplitPage(page_num=find_page(start, rows), text=section_text)
                table_start = section_text.rfind("<table")
                if (
                    table_start > 2 * self.sentence_limit
                    and table_start > section_text.rfind("</table")
                ):
                    # If the section ends with an unclosed table,
                    # we need to start the next section with the table.
                    # If table starts inside sentence_search_limit,
                    # we ignore it,as that will cause an infinite loop
                    # for tables longer than MAX_SECTION_LENGTH
                    # If last table starts inside section_overlap,
                    # keep overlapping
                    start = min(end - self.sec_overlap, start + table_start)
                else:
                    start = end - self.sec_overlap
            if start + self.sec_overlap < end:
                yield SplitPage(
                    page_num=find_page(start, rows), text=all_text[start:end]
                )
                process_pages(rows)
