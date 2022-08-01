from html.parser import HTMLParser
from collections import deque
import json


class CanvasToNotionHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__block_tags = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li"}
        self.__inline_tags = {"a", "strong", "em"}
        self.__ignore_tags = ("div", "span", "br")
        self.__tag_stack = deque()
        self.__output = []
        self.__latest_block = None
        self.__latest_text_type = None
        self.__latest_url = None
        self.__latest_list_type = None
        self.__unknown_tag = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.__latest_url = value
                    break

        if tag in self.__ignore_tags:
            return

        if tag in ("ul", "ol"):
            self.__latest_list_type = (
                "bulleted_list_item"
                if self.__latest_list_type == "ul"
                else "numbered_list_item"
            )
            self.__unknown_tag = False

        if tag not in self.__block_tags | self.__inline_tags:
            self.__unknown_tag = True
            self.__output.append(
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "There is content here that has/may not have been programmed to be parsed"
                                    " and rendered into Notion. Please check the Canvas assignment site to "
                                    "see if the missing content is important."
                                },
                            }
                        ],
                        "icon": {"emoji": "⚠"},
                        "color": "default",
                    },
                }
            )
            return
        if tag in self.__block_tags:
            match tag:
                case "h1" | "h2" | "h3":
                    self.__latest_text_type = f"heading_{tag[-1]}"
                case "p":
                    self.__latest_text_type = "paragraph"
            self.__new_block_data(self.__latest_text_type)
        self.__unknown_tag = False

    def handle_endtag(self, tag):
        match tag:
            case "strong":
                self.__convert_latest_rich_text_to_bold()
            case "em":
                self.__convert_latest_rich_text_to_italics()
            case "a":
                self.__convert_latest_rich_text_to_url()
            case "ul" | "ol":
                self.__latest_list_type = None
        if self.__latest_block and tag in self.__block_tags:
            self.__output.append(self.__latest_block)
            self.__latest_block = None
            self.__latest_text_type = None

    def handle_data(self, data):
        if not self.__latest_text_type or self.__unknown_tag:
            return
        self.__append_data_to_block(data)

    def __new_block_data(self, text_type):
        match text_type:
            case "paragraph":
                self.__new_paragraph_block()
            case "heading_1" | "heading_2" | "heading_3" as heading_type:
                self.__new_heading_block(heading_type)
            case "h4" | "h5" | "h6":
                self.__new_small_heading_block()
            case "bulleted_list_item" | "numbered_list_item":
                self.__new_list_block()

    def __new_paragraph_block(self):
        self.__latest_block = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": []},
        }

    def __new_heading_block(self, heading_type: str):
        self.__latest_block = {
            "object": "block",
            "type": heading_type,
            heading_type: {"rich_text": []},
        }

    def __new_small_heading_block(self):
        self.__new_paragraph_block()
        self.__convert_latest_rich_text_to_bold()

    def __new_list_block(self):
        self.__latest_block = {
            "object": "block",
            "type": self.__latest_list_type,
            self.__latest_list_type: {"rich_text": []},
        }

    def __append_data_to_block(self, data):
        latest_block_type = self.__latest_block.get("type")
        rich_text_list = self.__latest_block[latest_block_type]["rich_text"]
        rich_text_list.append({"type": "text", "text": {"content": data}})

    def __convert_latest_rich_text_to_bold(self):
        latest_block_type = self.__latest_block.get("type")
        latest_rich_text = self.__latest_block[latest_block_type]["rich_text"][-1]
        latest_rich_text["annotations"] = latest_rich_text.get(
            "annotations", dict()
        ) | {"bold": True}

    def __convert_latest_rich_text_to_italics(self):
        latest_block_type = self.__latest_block.get("type")
        latest_rich_text = self.__latest_block[latest_block_type]["rich_text"][-1]
        latest_rich_text["annotations"] = latest_rich_text.get(
            "annotations", dict()
        ) | {"italic": True}

    def __convert_latest_rich_text_to_url(self):
        latest_block_type = self.__latest_block.get("type")
        latest_rich_text = self.__latest_block[latest_block_type]["rich_text"][-1]
        latest_rich_text["text"]["link"] = {"url": self.__latest_url}

    def __inline_data(self, data):
        latest_block_type = self.__latest_block.get("type")
        latest_rich_text = self.__latest_block[latest_block_type]["rich_text"]
        latest_rich_text.append({"type": "text", "text": {"content": data}})

    @property
    def parsed_content(self):
        return self.__output


if __name__ == "__main__":

    class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            print("Encountered a start tag:", tag)

        def handle_endtag(self, tag):
            print("Encountered an end tag :", tag)

        def handle_data(self, data):
            print("Encountered some data  :", data)

    parser = MyHTMLParser()
    parser.feed(
        """<p><span style="font-size: 18pt; color: #000000; background-color: #fbeeb8;"><a class="instructure_file_link instructure_scribd_file inline_disabled" title="COMPSCI120-2022-S1-test-soln.pdf" href="https://canvas.auckland.ac.nz/courses/71970/files/9022875?wrap=1" target="_blank" data-canvas-previewable="false" data-api-endpoint="https://canvas.auckland.ac.nz/api/v1/courses/71970/files/9022875" data-api-returntype="File">SOLUTIONS</a>:&nbsp;</span></p>
<p>The mid-semester test is being run as a Canvas quiz.</p>
<p>This quiz is open for <strong>75 minutes</strong> on <strong>May 2nd</strong> from 6.30 pm<strong> to 7.45 pm</strong>&nbsp;(New Zealand Time).</p>
<p>There are 8 multiple-choice questions (Q1-8), and one free-response question (Q9).</p>
<p>The quiz is designed to take <strong>60 minutes</strong>. The <strong>extra 15 minutes are for you to upload your answer to Q9</strong>. If you encounter technical issues uploading your answer to Q9, email <a class="inline_disabled" href="mailto:sudeep.stephen@auckland.ac.nz" target="_blank">sudeep.stephen@auckland.ac.nz</a> (using your university email address) and attach your work, <strong>before 7:45 pm on May 2nd.&nbsp;</strong></p>
<p>You only have <strong>one attempt</strong> at this quiz. Only click ‘Submit quiz’ when you are sure you are finished and no longer want to make any changes. <strong>You will not be able to re-open the quiz after you click 'Submit quiz'. <br></strong></p>
<div class="page" title="Page 1">
<div class="layoutArea">
<div class="column">
<p><span>This is an 'open book' test. You can refer to any material you like (including any lecture material), and you can use any calculator you like. However, you must work on your own and <strong>not help or seek help from anybody</strong>. If you are found to have broken this rule, you may face disciplinary action.<br></span></p>
<p><span style="background-color: #f1c40f;">If you post on online tutoring websites (e.g. Chegg) we are able to obtain your personal information from those websites. Take this as a warning and if you are found to have used these services, you may face disciplinary action.&nbsp;</span></p>
<p><span>Good luck!</span></p>
</div>
</div>
</div>"""
    )
    parser.close()

    parser = CanvasToNotionHTMLParser()
    parser.feed(
        """<p><span style="font-size: 18pt; color: #000000; background-color: #fbeeb8;"><a class="instructure_file_link instructure_scribd_file inline_disabled" title="COMPSCI120-2022-S1-test-soln.pdf" href="https://canvas.auckland.ac.nz/courses/71970/files/9022875?wrap=1" target="_blank" data-canvas-previewable="false" data-api-endpoint="https://canvas.auckland.ac.nz/api/v1/courses/71970/files/9022875" data-api-returntype="File">SOLUTIONS</a>:&nbsp;</span></p>
<p>The mid-semester test is being run as a Canvas quiz.</p>
<p>This quiz is open for <strong>75 minutes</strong> on <strong>May 2nd</strong> from 6.30 pm<strong> to 7.45 pm</strong>&nbsp;(New Zealand Time).</p>
<p>There are 8 multiple-choice questions (Q1-8), and one free-response question (Q9).</p>
<p>The quiz is designed to take <strong>60 minutes</strong>. The <strong>extra 15 minutes are for you to upload your answer to Q9</strong>. If you encounter technical issues uploading your answer to Q9, email <a class="inline_disabled" href="mailto:sudeep.stephen@auckland.ac.nz" target="_blank">sudeep.stephen@auckland.ac.nz</a> (using your university email address) and attach your work, <strong>before 7:45 pm on May 2nd.&nbsp;</strong></p>
<p>You only have <strong>one attempt</strong> at this quiz. Only click ‘Submit quiz’ when you are sure you are finished and no longer want to make any changes. <strong>You will not be able to re-open the quiz after you click 'Submit quiz'. <br></strong></p>
<div class="page" title="Page 1">
<div class="layoutArea">
<div class="column">
<p><span>This is an 'open book' test. You can refer to any material you like (including any lecture material), and you can use any calculator you like. However, you must work on your own and <strong>not help or seek help from anybody</strong>. If you are found to have broken this rule, you may face disciplinary action.<br></span></p>
<p><span style="background-color: #f1c40f;">If you post on online tutoring websites (e.g. Chegg) we are able to obtain your personal information from those websites. Take this as a warning and if you are found to have used these services, you may face disciplinary action.&nbsp;</span></p>
<p><span>Good luck!</span></p>
</div>
</div>
</div>"""
    )
    content = parser.parsed_content
    parser.close()
    print(json.dumps(content, indent=2))
