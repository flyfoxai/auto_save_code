import os

class ProjectStructureExtractor:
    def extract_project_structure(self, directory):
        structure_lines = self.find_structure_lines(directory)
        return structure_lines

    def find_structure_lines(self, directory, prefix=""):
        lines = []
        try:
            items = os.listdir(directory)
            items.sort()
            for item in items:
                path = os.path.join(directory, item)
                if os.path.isdir(path):
                    lines.append(f"{prefix}- {item}/")
                    lines.extend(self.find_structure_lines(path, prefix + "  "))
                else:
                    lines.append(f"{prefix}- {item}")
        except Exception as e:
            print(f"读取目录 {directory} 时出错: {str(e)}")
        return lines