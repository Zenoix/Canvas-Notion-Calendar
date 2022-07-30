from html.parser import HTMLParser
from collections import deque


class CanvasToNotionHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__valid_tags = ("p", "h1", "h2", "h3", "a", "strong")
        self.stack = deque()
        self.__output = []
        self.__latest_block = None
        self.__latest_url = None

    def handle_starttag(self, tag, attrs):
        if len(self.stack) > 0 and self.stack[-1] == "p":
            self.__output.append(self.__latest_block)
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.__latest_url = value
                    break
        if tag in self.__valid_tags:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.__valid_tags:
            self.stack.pop()
        if len(self.stack) == 0 and self.__latest_block:
            self.__output.append(self.__latest_block)
            self.__latest_block = None

    def handle_data(self, data):
        # TODO Fix duplicate
        if len(self.stack) == 0:
            return
        latest_opening_tag = self.stack[-1]
        if latest_opening_tag == "p":
            text_type = "paragraph"
        elif latest_opening_tag in ("h1", "h2", "h3"):
            text_type = f"heading_{latest_opening_tag[-1]}"
        elif latest_opening_tag == "a":
            self.__latest_block = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": data,
                            "link": {
                                "url": self.__latest_url
                            }
                        }
                    }]
                }
            }
            return
        elif latest_opening_tag == "strong":
            self.__latest_block = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": data
                        },
                        "annotations": {
                            "bold": True
                        }
                    }]
                }
            }
            return
        elif latest_opening_tag == "em":
            self.__latest_block = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": data
                        },
                        "annotations": {
                            "italic": True
                        }
                    }]
                }
            }
            return
        else:
            text_type = "paragraph"
        self.__latest_block = {
            "object": "block",
            "type": text_type,
            text_type: {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": data
                    }
                }]
            }
        }

    @property
    def parsed_content(self):
        return self.__output


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)


parser = MyHTMLParser()
parser.feed(
    '<p>Here are the tutorial sheets:&nbsp;<strong> (Please take a print or BYO device to class to view the tutorial sheets)</strong></p>\n<p><a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"compsci120_tutorial9_version1.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71970/files/8675212?wrap=1\" target=\"_blank\" data-canvas-previewable=\"false\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71970/files/8675212\" data-api-returntype=\"File\">Tutorial 9-Sheet 1</a></p>\n<p><a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"compsci120_tutorial9_version2.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71970/files/8675213?wrap=1\" target=\"_blank\" data-canvas-previewable=\"false\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71970/files/8675213\" data-api-returntype=\"File\">Tutorial 9-Sheet 2</a></p>\n<p><a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"compsci120_tutorial9_version3.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71970/files/8675214?wrap=1\" target=\"_blank\" data-canvas-previewable=\"false\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71970/files/8675214\" data-api-returntype=\"File\">Tutorial 9-Sheet 3</a></p>\n<p><span style=\"background-color: #f1c40f;\">If you are submitting the tutorial on Canvas, you can pick any sheet from the above and submit your work.</span></p>')
parser.close()

parser = CanvasToNotionHTMLParser()
parser.feed(
    "<p>Here are the tutorial sheets:&nbsp;"
    "<strong> (Please take a print or BYO device to class to view the tutorial sheets)"
    "</strong>"
    "</p>\n"
    "<p>"
    "<a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"compsci120_tutorial9_version1.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71970/files/8675212?wrap=1\" target=\"_blank\" data-canvas-previewable=\"false\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71970/files/8675212\" data-api-returntype=\"File\">"
    "Tutorial 9-Sheet 1"
    "</a>"
    "</p>\n"
    "<p>"
    "<a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"compsci120_tutorial9_version2.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71970/files/8675213?wrap=1\" target=\"_blank\" data-canvas-previewable=\"false\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71970/files/8675213\" data-api-returntype=\"File\">"
    "Tutorial 9-Sheet 2</a>"
    "</p>\n"
    "<p>"
    "<a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"compsci120_tutorial9_version3.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71970/files/8675214?wrap=1\" target=\"_blank\" data-canvas-previewable=\"false\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71970/files/8675214\" data-api-returntype=\"File\">Tutorial 9-Sheet 3</a></p>\n<p><span style=\"background-color: #f1c40f;\">"
    "If you are submitting the tutorial on Canvas, you can pick any sheet from the above and submit your work."
    "</span>"
    "</p>")
content = parser.parsed_content
parser.close()
print(content)
