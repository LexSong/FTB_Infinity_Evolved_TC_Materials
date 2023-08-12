import json
from pathlib import Path


def read_ocr_page_lines(file: Path) -> list[str]:
    page_num = int(file.stem)
    with file.open() as f:
        lines = [x.strip() for x in f]

    assert lines[0] == "Tool Materials"
    assert lines[-1] == f"Page {page_num}/134"
    return lines[1:-1]


def parse_field(field_name: str, line: str) -> str:
    field_name_with_colon = field_name + ": "
    assert line.startswith(field_name_with_colon)
    return line.removeprefix(field_name_with_colon).strip()


def parse_first_page(file: Path) -> dict[str, str]:
    lines = read_ocr_page_lines(file)

    material_name = lines[0]
    field_lines = lines[1:7]
    extra_lines = lines[7:]

    result = {"Name": material_name}

    field_names = [
        "Base Durability",
        "Handle Modifier",
        "Full Durability",
        "Mining Speed",
        "Mining Level",
        "Attack",
    ]

    for field_name, line in zip(field_names, field_lines):
        result[field_name] = parse_field(field_name, line)

    reinforced_traits = []
    other_traits = []

    for line in extra_lines:
        if line.startswith("Reinforced"):
            reinforced_traits.append(line)
        else:
            other_traits.append(line)

    if reinforced_traits:
        assert len(reinforced_traits) == 1
        result["Reinforced Level"] = reinforced_traits[0]

    if other_traits:
        assert len(other_traits) == 1
        result["Trait"] = other_traits[0]

    return result


def parse_second_page(file: Path) -> dict[str, str]:
    lines = read_ocr_page_lines(file)
    assert len(lines) == 5

    assert lines[0] == "Bow & Arrow"
    field_lines = lines[1:5]

    field_names = [
        "Draw Speed",
        "Arrow Speed",
        "Weight",
        "Break Chance",
    ]

    result = {}
    for field_name, line in zip(field_names, field_lines):
        result[field_name] = parse_field(field_name, line)

    return result


ocr_files = sorted(Path("ocr").glob("*.txt"))

for i, file in enumerate(ocr_files, start=1):
    assert file.name == f"{i:03d}.txt"

with open("tool_materials.jsonl", "w") as f:
    for i in range(0, len(ocr_files), 2):
        result = {
            **parse_first_page(ocr_files[i]),
            **parse_second_page(ocr_files[i + 1]),
        }
        f.write(json.dumps(result))
        f.write("\n")
