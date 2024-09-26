import re

class CodeExtractor:
    def extract_code_blocks(self, content):
        self.code_blocks = []
        self.lines = content.split('\n')
        self.current_line = 0
        
        while self.current_line < len(self.lines):
            self.extract_code_block_step()
        
        return self.code_blocks

    def extract_code_block_step(self):
        line = self.lines[self.current_line]
        file_path_pattern = r'^##\s+(.*?/.*?\.[a-zA-Z]{1,3})$'
        match = re.match(file_path_pattern, line)

        if match:
            potential_path = match.group(1).strip()
            self.current_line += 1
            self.find_code_block_start(potential_path)
        else:
            self.current_line += 1

    def find_code_block_start(self, potential_path):
        while self.current_line < len(self.lines) and not self.lines[self.current_line].startswith('```'):
            self.current_line += 1

        if self.current_line < len(self.lines):
            code_start = self.lines[self.current_line]
            lang = code_start.strip('`').strip()
            file_path = self.find_file_path()
            
            if file_path:
                self.current_line += 1
                self.extract_code_content(file_path, lang)
            else:
                self.current_line += 1
        else:
            pass

    def find_file_path(self):
        for i in range(1, 4):
            if self.current_line - i >= 0:
                line = self.lines[self.current_line - i]
                file_path_pattern = r'^##\s+(.*?/.*?\.[a-zA-Z]{1,3})$'
                match = re.match(file_path_pattern, line)
                if match:
                    return match.group(1).strip()
        return None

    def extract_code_content(self, file_path, lang):
        code_lines = []
        while self.current_line < len(self.lines) and not self.lines[self.current_line].startswith('```'):
            code_lines.append(self.lines[self.current_line])
            self.current_line += 1

        if self.current_line < len(self.lines) and self.lines[self.current_line] == '```':
            code = '\n'.join(code_lines)
            if file_path:
                self.code_blocks.append((file_path, lang, code))
        else:
            pass