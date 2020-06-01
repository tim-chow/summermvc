# coding: utf8

__all__ = ["MultipartParser"]
__authors__ = ["Tim Chow"]


class MultipartParser(object):
    def __init__(self, body, boundary):
        self._files = self.parse(body, boundary)

    @staticmethod
    def parse(body, boundary):
        parts = {}
        original_parts = body.split("--%s" % boundary)[1:-1]
        for one_original_part in original_parts:
            part = {}
            phrases = one_original_part.split("\r\n")[1:-1]
            line_no = 0
            for line_no, line in enumerate(phrases, start=1):
                if line == "":
                    break
                pair = line.split(":", 1)
                if len(pair) != 2:
                    continue
                part[pair[0].strip()] = pair[1].strip()

            cd = part.pop("Content-Disposition", "")
            for item in cd.split(";")[1:]:
                pair = item.split("=", 1)
                if len(pair) != 2:
                    continue
                part[pair[0].strip()] = pair[1].strip(" \"")

            if "name" in part:
                part["content"] = "\r\n".join(phrases[line_no:])
                parts[part["name"]] = part
        return parts

    @property
    def files(self):
        return self._files


if __name__ == "__main__":
    boundary_string = "form_boundary"
    post_body = '--{0}\r\nContent-Disposition: form-data; name="file1"; filename="file1.txt"\r\n' \
                'Content-Type: text/plain\r\n\r\nthis is file1.txt\r\n--{0}\r\n' \
                'Content-Disposition: form-data; name="file2"; filename="file2.txt"\r\n' \
                'Content-Type: text/plain\r\n\r\n\r\nthis\r\nis\r\nfile2.txt\r\n\r\n' \
                '--{0}--'.format(boundary_string)
    multipart_entity = MultipartParser(post_body, boundary_string)
    print(multipart_entity.files)
