from html.parser import HTMLParser
from collections import deque

class CanvasToNotionHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.stack = deque()
        self.__output = []
        self.__latest_block = None

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # <br>
        pass

    def handle_endtag(self, tag):
        if self.stack[-1] == tag:
            self.stack.remove()
        if len(self.stack) == 0:
            self.__output.append(self.__latest_block)

    def handle_data(self, data):
        match self.stack[-1].lower():
            case "p":
                pass
            case "h1" | "h2" | "h3":
                pass
            case "code":
                pass
            case "ul":
                pass
            case "li":
                pass
            case "h":
                pass
            case "em":
                pass
            case "strong":
                pass




        data = {
            "object": "block",
        }


parser = CanvasToNotionHTMLParser()
parser.feed('<p>Here is the tutorial sheet: &nbsp;<a class=\"instructure_file_link instructure_scribd_file inline_disabled\" href=\"https://canvas.auckland.ac.nz/courses/71970/files/8123667?wrap=1\" target=\"_blank\" data-canvas-previewable=\"true\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71970/files/8123667\" data-api-returntype=\"File\">Tutorial 1</a></p>')