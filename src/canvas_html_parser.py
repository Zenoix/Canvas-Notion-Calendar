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
        self.__unknown_tag = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.__latest_url = value
                    break

        if tag in self.__ignore_tags:
            return

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

        if tag in ("ul", "ol"):
            self.__latest_text_type = (
                "bulleted_list_item"
                if self.__latest_text_type == "ul"
                else "numbered_list_item"
            )

        if tag in self.__block_tags:
            match tag:
                case "h1" | "h2" | "h3":
                    self.__latest_text_type = f"heading_{tag[-1]}"
                case "p":
                    self.__latest_text_type = "paragraph"
                case _:
                    self.__latest_text_type = tag
            self.__new_block_data(self.__latest_text_type)
        self.__unknown_tag = False

    def handle_endtag(self, tag):
        match tag:
            case "strong" | "h4" | "h5" | "h6":
                self.__convert_latest_rich_text_to_bold()
            case "em":
                self.__convert_latest_rich_text_to_italics()
            case "a":
                self.__convert_latest_rich_text_to_url()
            case "ul" | "ol":
                self.__latest_text_type = None
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

    def __new_list_block(self):
        self.__latest_block = {
            "object": "block",
            "type": self.__latest_text_type,
            self.__latest_text_type: {"rich_text": []},
        }

    def __append_data_to_block(self, data):
        print(data)
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
        output = self.__output
        self.__output = []
        return output


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
        """<h1><span>Student Instructions</span></h1>\n<h4><strong>Accessing your exam</strong></h4>\n<p>When your exam is open, you will be able to start it from the Inspera Dashboard at:&nbsp;<br><a class=\"external\" href=\"http://auckland.inspera.com/\" target=\"_blank\"><span>http://auckland.inspera.com/</span></a></p>\n<p><strong>Important:</strong> This assignment shows the <strong>timetabled exam start time</strong> as the <strong>Due date/time</strong>.</p>\n<p>You can view your exam timetable in&nbsp;<a class=\"external\" href=\"https://www.auckland.ac.nz/en/students/my-tools/sso/timetables-grades-and-course-history/exam-timetable.html\" target=\"_blank\"><span>Student Services Online.</span></a></p>\n<p><strong>Submitting your exam</strong></p>\n<p>Online exams have an additional 30 minutes added to the exam duration to allow time to submit all components of the exam.</p>\n<table border=\"1\">\n<tbody>\n<tr>\n<td>\n<p><strong>File upload guidance</strong></p>\n<p>An exam may require answering a question with handwritten work (such as proofs or diagrams). Answer this type of question by uploading a scanned copy of your work as a PDF through apps such as Adobe Scan.</p>\n<p>See the steps for&nbsp;<strong>Uploading a file for your Inspera exam&nbsp;</strong>on the&nbsp;<a class=\"external\" href=\"https://www.auckland.ac.nz/en/students/academic-information/exams-and-final-results/online-exams/sitting-your-exam.html\" target=\"_blank\"><span>Sitting Your Exam</span></a>&nbsp;page.</p>\n<p>IMPORTANT</p>\n<p>Start uploading any documents<strong>&nbsp;at least&nbsp;15 minutes before the deadline</strong>&nbsp;as it can take several minutes for a submission to upload. After uploading a document always check the correct file has been submitted. You can only submit a document in Inspera if the upload process has started&nbsp;<em>before</em>&nbsp;the end of the exam.&nbsp;<strong>It is your responsibility to ensure your assessment is successfully submitted on time.</strong></p>\n<p>If your file did not upload in time, contact<span>&nbsp;</span><strong>Student Support</strong><span>&nbsp;</span>immediately and do not open or edit the exam documents on your computer.</p>\n</td>\n</tr>\n</tbody>\n</table>\n<p><strong>Useful Guides</strong></p>\n<p>Review&nbsp;<a class=\"external\" href=\"https://www.auckland.ac.nz/en/students/academic-information/exams-and-final-results/online-exams/computer-based-exams.html\" target=\"_blank\"><span>Inspera online exams</span></a>&nbsp;page for key information including the&nbsp;<strong>Getting started with Inspera online exams</strong>&nbsp;guide.</p>\n<p>The&nbsp;<a class=\"external\" href=\"https://cdn.auckland.ac.nz/assets/auckland/students/academic-information/exams-and-final-results/online-exams/student-support-for-inspera-exams.pdf\" target=\"_blank\"><span>Support during your Inspera exam guide</span></a><span>&nbsp;</span>document outlines what to do in case of technical issues (recommend saving this PDF to your device for quick reference).</p>\n<p><a class=\"external\" href=\"https://www.auckland.ac.nz/en/students/academic-information/exams-and-final-results/online-exams/computer-based-exams/inspera-exams-faqs.html\" target=\"_blank\"><span>Click here</span></a>&nbsp;for Inspera exam FAQ\u2019s.</p>\n<table style=\"border-collapse: collapse; border-style: dashed;\">\n<tbody>\n<tr>\n<td>\n<p>FROM THE UNIVERSITY:</p>\n<p>Please note, as per the usual requirements for exams, with online exams you cannot directly contact your instructor during the assessment.</p>\n<p><strong>Student Support</strong></p>\n<p>If you need help during your online exam, please call the Student Contact Centre for advice. The Contact Centre will be open 8:30am \u2013 9:30pm Monday to Friday and 12:00pm \u2013 9:30pm Saturday (NZ Time) throughout the exam period.</p>\n<p>Phone: (Auckland) 09 373 7513, (New Zealand) 0800 61 62 63, or (International)&nbsp;+64 9 373 7513. If you are unable to call, please email&nbsp;<a href=\"mailto:studentinfo@auckland.ac.nz\">studentinfo@auckland.ac.nz</a>&nbsp;and provide exam details, contact information and a description of the issue. Please note that email responses may not be provided before your exam submission deadline so please call in the first instance.</p>\n<p>An Inspera announcement will be made if there are any corrections or clarifications regarding your exam.</p>\n</td>\n</tr>\n</tbody>\n</table>\n<p><strong>Academic Integrity Statement&nbsp;for online exams</strong></p>\n<p>The following academic integrity statement is part of each online exam. Please familiarise yourself with the content below before exam day. More information is available on the <a class=\"inline_disabled external\" href=\"https://www.auckland.ac.nz/en/students/academic-information/exams-and-final-results/online-exams/preparing-for-your-exam/academic-integrity-online-assessment.html\" target=\"_blank\"><span>Academic integrity in online assessments</span></a><span>&nbsp;</span>page.<span>&nbsp;</span><strong>It is your responsibility to ensure you know and understand this information.</strong></p>\n<p>By submitting this assessment, I agree to the following declaration:&nbsp;</p>\n<p><em>As a member of the University\u2019s student body, I will complete this assessment with academic integrity and in a fair, honest, responsible, and trustworthy manner. This means that:&nbsp;</em></p>\n<ul>\n<li><em>I will not seek out any unauthorised help in completing this assessment. Unauthorised help includes, but is not limited to, asking another person, friend, family member, third party, tutorial, search function or answer service, whether in person or online.</em></li>\n<li><em>I will not discuss or share the content of the assessment with anyone else in any form during the assessment period, including but not limited to, using a messaging service, communication channel or discussion forum, Canvas, Piazza, Chegg, third party website, Facebook, Twitter, Discord, social media or any other channel within the assessment period.&nbsp;</em></li>\n<li><em>I will not reproduce and/or share the content of this assessment in any domain or in any form where it may be accessed by a third party.&nbsp;</em></li>\n<li><em>I will not share my answers or thoughts regarding this assessment in any domain or in any form within the assessment period.</em></li>\n<li><em>I am aware the University of Auckland may use Turnitin or any other plagiarism detecting methods to check my content.</em></li>\n<li><em>I declare that this assessment is my own work, except where acknowledged appropriately (e.g., use of referencing).&nbsp;</em></li>\n<li><em>I declare that this work has not been submitted for academic credit in this or another University of Auckland course, or elsewhere.</em></li>\n</ul>\n<p><em>I understand the University expects all students to complete coursework with integrity and honesty. I promise to complete all online assessments with the same academic integrity standards and values.&nbsp;</em></p>\n<p><em>Any identified form of poor academic practice or academic misconduct will be followed up and may result in disciplinary action.&nbsp;</em></p>\n<p><em>I confirm that by completing this exam I agree to the above statements in full.</em></p>",
 """
    )
    parser.close()

    parser = CanvasToNotionHTMLParser()
    parser.feed(
        """<h1><span>Student Instructions</span></h1>\n<h4><strong>Accessing your exam</strong></h4>\n<p>When your exam is open, you will be able to start it from the Inspera Dashboard at:&nbsp;<br><a class=\"external\" href=\"http://auckland.inspera.com/\" target=\"_blank\"><span>http://auckland.inspera.com/</span></a></p>\n<p><strong>Important:</strong> This assignment shows the <strong>timetabled exam start time</strong> as the <strong>Due date/time</strong>.</p>\n<p>You can view your exam timetable in&nbsp;<a class=\"external\" href=\"https://www.auckland.ac.nz/en/students/my-tools/sso/timetables-grades-and-course-history/exam-timetable.html\" target=\"_blank\"><span>Student Services Online.</span></a></p>\n<p><strong>Submitting your exam</strong></p>\n<p>Online exams have an additional 30 minutes added to the exam duration to allow time to submit all components of the exam.</p>\n<table border=\"1\">\n<tbody>\n<tr>\n<td>\n<p><strong>File upload guidance</strong></p>\n<p>An exam may require answering a question with handwritten work (such as proofs or diagrams). Answer this type of question by uploading a scanned copy of your work as a PDF through apps such as Adobe Scan.</p>\n<p>See the steps for&nbsp;<strong>Uploading a file for your Inspera exam&nbsp;</strong>on the&nbsp;<a class=\"external\" href=\"https://www.auckland.ac.nz/en/students/academic-information/exams-and-final-results/online-exams/sitting-your-exam.html\" target=\"_blank\"><span>Sitting Your Exam</span></a>&nbsp;page.</p>\n<p>IMPORTANT</p>\n<p>Start uploading any documents<strong>&nbsp;at least&nbsp;15 minutes before the deadline</strong>&nbsp;as it can take several minutes for a submission to upload. After uploading a document always check the correct file has been submitted. You can only submit a document in Inspera if the upload process has started&nbsp;<em>before</em>&nbsp;the end of the exam.&nbsp;<strong>It is your responsibility to ensure your assessment is successfully submitted on time.</strong></p>\n<p>If your file did not upload in time, contact<span>&nbsp;</span><strong>Student Support</strong><span>&nbsp;</span>immediately and do not open or edit the exam documents on your computer.</p>\n</td>\n</tr>\n</tbody>\n</table>\n<p><strong>Useful Guides</strong></p>\n<p>Review&nbsp;<a class=\"external\" href=\"https://www.auckland.ac.nz/en/students/academic-information/exams-and-final-results/online-exams/computer-based-exams.html\" target=\"_blank\"><span>Inspera online exams</span></a>&nbsp;page for key information including the&nbsp;<strong>Getting started with Inspera online exams</strong>&nbsp;guide.</p>\n<p>The&nbsp;<a class=\"external\" href=\"https://cdn.auckland.ac.nz/assets/auckland/students/academic-information/exams-and-final-results/online-exams/student-support-for-inspera-exams.pdf\" target=\"_blank\"><span>Support during your Inspera exam guide</span></a><span>&nbsp;</span>document outlines what to do in case of technical issues (recommend saving this PDF to your device for quick reference).</p>\n<p><a class=\"external\" href=\"https://www.auckland.ac.nz/en/students/academic-information/exams-and-final-results/online-exams/computer-based-exams/inspera-exams-faqs.html\" target=\"_blank\"><span>Click here</span></a>&nbsp;for Inspera exam FAQ\u2019s.</p>\n<table style=\"border-collapse: collapse; border-style: dashed;\">\n<tbody>\n<tr>\n<td>\n<p>FROM THE UNIVERSITY:</p>\n<p>Please note, as per the usual requirements for exams, with online exams you cannot directly contact your instructor during the assessment.</p>\n<p><strong>Student Support</strong></p>\n<p>If you need help during your online exam, please call the Student Contact Centre for advice. The Contact Centre will be open 8:30am \u2013 9:30pm Monday to Friday and 12:00pm \u2013 9:30pm Saturday (NZ Time) throughout the exam period.</p>\n<p>Phone: (Auckland) 09 373 7513, (New Zealand) 0800 61 62 63, or (International)&nbsp;+64 9 373 7513. If you are unable to call, please email&nbsp;<a href=\"mailto:studentinfo@auckland.ac.nz\">studentinfo@auckland.ac.nz</a>&nbsp;and provide exam details, contact information and a description of the issue. Please note that email responses may not be provided before your exam submission deadline so please call in the first instance.</p>\n<p>An Inspera announcement will be made if there are any corrections or clarifications regarding your exam.</p>\n</td>\n</tr>\n</tbody>\n</table>\n<p><strong>Academic Integrity Statement&nbsp;for online exams</strong></p>\n<p>The following academic integrity statement is part of each online exam. Please familiarise yourself with the content below before exam day. More information is available on the <a class=\"inline_disabled external\" href=\"https://www.auckland.ac.nz/en/students/academic-information/exams-and-final-results/online-exams/preparing-for-your-exam/academic-integrity-online-assessment.html\" target=\"_blank\"><span>Academic integrity in online assessments</span></a><span>&nbsp;</span>page.<span>&nbsp;</span><strong>It is your responsibility to ensure you know and understand this information.</strong></p>\n<p>By submitting this assessment, I agree to the following declaration:&nbsp;</p>\n<p><em>As a member of the University\u2019s student body, I will complete this assessment with academic integrity and in a fair, honest, responsible, and trustworthy manner. This means that:&nbsp;</em></p>\n<ul>\n<li><em>I will not seek out any unauthorised help in completing this assessment. Unauthorised help includes, but is not limited to, asking another person, friend, family member, third party, tutorial, search function or answer service, whether in person or online.</em></li>\n<li><em>I will not discuss or share the content of the assessment with anyone else in any form during the assessment period, including but not limited to, using a messaging service, communication channel or discussion forum, Canvas, Piazza, Chegg, third party website, Facebook, Twitter, Discord, social media or any other channel within the assessment period.&nbsp;</em></li>\n<li><em>I will not reproduce and/or share the content of this assessment in any domain or in any form where it may be accessed by a third party.&nbsp;</em></li>\n<li><em>I will not share my answers or thoughts regarding this assessment in any domain or in any form within the assessment period.</em></li>\n<li><em>I am aware the University of Auckland may use Turnitin or any other plagiarism detecting methods to check my content.</em></li>\n<li><em>I declare that this assessment is my own work, except where acknowledged appropriately (e.g., use of referencing).&nbsp;</em></li>\n<li><em>I declare that this work has not been submitted for academic credit in this or another University of Auckland course, or elsewhere.</em></li>\n</ul>\n<p><em>I understand the University expects all students to complete coursework with integrity and honesty. I promise to complete all online assessments with the same academic integrity standards and values.&nbsp;</em></p>\n<p><em>Any identified form of poor academic practice or academic misconduct will be followed up and may result in disciplinary action.&nbsp;</em></p>\n<p><em>I confirm that by completing this exam I agree to the above statements in full.</em></p>
 """
    )
    content = parser.parsed_content
    parser.close()
    print(json.dumps(content, indent=2))
