from html.parser import HTMLParser
from collections import deque
import json


class CanvasToNotionHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__valid_tags = ("p", "h1", "h2", "h3", "a", "strong", "span", "hr", "em")
        self.stack = deque()
        self.__output = []
        self.__latest_block = None
        self.__latest_url = None
        self.__unknown_tag = False

    def handle_starttag(self, tag, attrs):
        if len(self.stack) > 0 and self.stack[-1] == "p" and self.__latest_block:
            self.__output.append(self.__latest_block)
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.__latest_url = value
                    break
        if tag in self.__valid_tags:
            self.stack.append(tag)
            self.__unknown_tag = False
        else:
            self.__unknown_tag = True
            self.__output.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": "There is content here that has/may not have been programmed to be parsed and "
                                       "rendered into Notion. Please check the Canvas assignment site to see if the "
                                       "missing content is important."
                        },
                    }],
                    "icon": {
                        "emoji": "⚠"
                    },
                    "color": "default"
                }
            })

    def handle_endtag(self, tag):
        if tag in self.__valid_tags:
            self.stack.pop()
        if len(self.stack) == 0 and self.__latest_block:
            self.__output.append(self.__latest_block)
            self.__latest_block = None

    def handle_data(self, data):
        # TODO Refactor the hard coded tag jsons
        if len(self.stack) == 0 or self.__unknown_tag:
            return
        latest_opening_tag = self.stack[-1]
        if latest_opening_tag in ("p", "span", "a", "strong", "em"):
            text_type = "paragraph"
        elif latest_opening_tag in ("h1", "h2", "h3"):
            text_type = f"heading_{latest_opening_tag[-1]}"
        elif latest_opening_tag == "hr":
            self.__latest_block = {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
            return

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

        if latest_opening_tag == "a":
            self.__latest_block[text_type]["rich_text"][0]["text"]["link"] = {"url": self.__latest_url}
        elif latest_opening_tag == "strong":
            self.__latest_block[text_type]["rich_text"][0]["annotations"] = {"bold": True}
        elif latest_opening_tag == "em":
            self.__latest_block[text_type]["rich_text"][0]["annotations"] = {"italic": True}

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
    '<p>Worksheet: <a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"assignment3.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71997/files/8823921?wrap=1\" target=\"_blank\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71997/files/8823921\" data-api-returntype=\"File\">assignment3.pdf</a></p>\n<p>Testcases for Question 3: Input: <a class=\"instructure_file_link inline_disabled\" title=\"testcases.in\" href=\"https://canvas.auckland.ac.nz/courses/71997/files/8804315?wrap=1\" target=\"_blank\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71997/files/8804315\" data-api-returntype=\"File\">testcases.in</a>; Output: <a class=\"instructure_file_link inline_disabled\" title=\"testcases.out\" href=\"https://canvas.auckland.ac.nz/courses/71997/files/8804316?wrap=1\" target=\"_blank\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71997/files/8804316\" data-api-returntype=\"File\">testcases.out</a></p>\n<p><span style=\"background-color: #fbeeb8;\">Sample solutions: <a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"assignment3-solutions.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71997/files/8993824?wrap=1\" target=\"_blank\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71997/files/8993824\" data-api-returntype=\"File\">assignment3-solutions.pdf</a></span></p>\n<p>&nbsp;</p>\n<p><em>By completing this assessment, I agree to the following declaration:</em></p>\n<p><em>I understand the University expects all students to complete coursework with integrity and honesty. I promise to complete all online assessment with the same academic integrity standards and values. Any identified form of poor academic practice or academic misconduct will be followed up and may result in disciplinary action.</em></p>\n<p><em>As a member of the University\u2019s student body, I will complete this assessment in a fair, honest, responsible and trustworthy manner. This means that:</em></p>\n<ul>\n<li><em>I declare that this assessment is my own work, except where acknowledged appropriately (e.g., use of referencing).</em></li>\n<li><em>I will not seek out any unauthorised help in completing this assessment. (NB. Unauthorised help <strong>includes</strong> a tutorial or answer service whether in person or online, friends or family, etc.)</em></li>\n<li><em>I declare that this work has not been submitted for academic credit in another University of Auckland course, or elsewhere.</em></li>\n<li><em>I am aware the University of Auckland may use Turnitin or any other plagiarism detecting methods to check my content.</em></li>\n<li><em>I will not discuss the content of the assessment with anyone else in any form, including, Canvas, Piazza, Chegg, Facebook, Twitter or any other social media within the assessment period.</em></li>\n<li><em>I will not reproduce the content of this assessment in any domain or in any form where it may be accessed by a third party.</em></li>\n</ul>')
parser.close()

parser = CanvasToNotionHTMLParser()
parser.feed(
    "<p>Worksheet: <a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"assignment3.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71997/files/8823921?wrap=1\" target=\"_blank\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71997/files/8823921\" data-api-returntype=\"File\">assignment3.pdf</a></p>\n<p>Testcases for Question 3: Input: <a class=\"instructure_file_link inline_disabled\" title=\"testcases.in\" href=\"https://canvas.auckland.ac.nz/courses/71997/files/8804315?wrap=1\" target=\"_blank\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71997/files/8804315\" data-api-returntype=\"File\">testcases.in</a>; Output: <a class=\"instructure_file_link inline_disabled\" title=\"testcases.out\" href=\"https://canvas.auckland.ac.nz/courses/71997/files/8804316?wrap=1\" target=\"_blank\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71997/files/8804316\" data-api-returntype=\"File\">testcases.out</a></p>\n<p><span style=\"background-color: #fbeeb8;\">Sample solutions: <a class=\"instructure_file_link instructure_scribd_file inline_disabled\" title=\"assignment3-solutions.pdf\" href=\"https://canvas.auckland.ac.nz/courses/71997/files/8993824?wrap=1\" target=\"_blank\" data-api-endpoint=\"https://canvas.auckland.ac.nz/api/v1/courses/71997/files/8993824\" data-api-returntype=\"File\">assignment3-solutions.pdf</a></span></p>\n<p>&nbsp;</p>\n<p><em>By completing this assessment, I agree to the following declaration:</em></p>\n<p><em>I understand the University expects all students to complete coursework with integrity and honesty. I promise to complete all online assessment with the same academic integrity standards and values. Any identified form of poor academic practice or academic misconduct will be followed up and may result in disciplinary action.</em></p>\n<p><em>As a member of the University\u2019s student body, I will complete this assessment in a fair, honest, responsible and trustworthy manner. This means that:</em></p>\n<ul>\n<li><em>I declare that this assessment is my own work, except where acknowledged appropriately (e.g., use of referencing).</em></li>\n<li><em>I will not seek out any unauthorised help in completing this assessment. (NB. Unauthorised help <strong>includes</strong> a tutorial or answer service whether in person or online, friends or family, etc.)</em></li>\n<li><em>I declare that this work has not been submitted for academic credit in another University of Auckland course, or elsewhere.</em></li>\n<li><em>I am aware the University of Auckland may use Turnitin or any other plagiarism detecting methods to check my content.</em></li>\n<li><em>I will not discuss the content of the assessment with anyone else in any form, including, Canvas, Piazza, Chegg, Facebook, Twitter or any other social media within the assessment period.</em></li>\n<li><em>I will not reproduce the content of this assessment in any domain or in any form where it may be accessed by a third party.</em></li>\n</ul>")
content = parser.parsed_content
parser.close()
print(json.dumps(content, indent=2))
