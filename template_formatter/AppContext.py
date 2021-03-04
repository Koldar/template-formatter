from typing import Optional

from template_formatter.Jinja2Model import Jinja2Model


class AppContext:

    def __init__(self):
        self.model = Jinja2Model()
        self.input_file: Optional[str] = None
        self.input_directory: Optional[str] = None
        self.output_directory: Optional[str] = None
        self.trailing_string_template_file: Optional[str] = None
        self.output_file_format: Optional[str] = None
        self.log_level: Optional[str] = None
        self.block_start_string: Optional[str] = None
        self.block_end_string: Optional[str] = None
        self.comment_start_string: Optional[str] = None
        self.comment_end_string: Optional[str] = None
        self.expression_start_string: Optional[str] = None
        self.expression_end_string: Optional[str] = None
        self.line_statement_prefix: Optional[str] = None
        self.input_file_encoding: Optional[str] = None
        self.output_file_encoding: Optional[str] = None
        self.write_on_stdout: bool = False
        self.template_string: Optional[str] = None
        self.format: Optional[str] = None
