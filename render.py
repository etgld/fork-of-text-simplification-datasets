from typing import Any
import re

import yaml
from yaml.loader import SafeLoader
from tabulate import tabulate

DOMAIN_ORDER = [
    "Wikipedia",
    "News",
    "Web",
    "Mixed",
    "Books",
    "Education",
    "Medical",
    "Clinical",
    "Talks",
]

HEADER = [
    "Dataset",
    "Lang",
    "Domain",
    "Kind",
    "Level",
    "Instances",
    "Refs.",
    "Link",
]

# More compact
LEVEL_MAP = {
    "Sentence": "Sent",
    "Paragraph": "Par",
    "Document": "Doc",
    "Lexical": "Lex",
}


def record_to_row(d: dict):
    if d["link"]:
        link = f"[Link]({d['link']})"
    else:
        link = "n/a"
    if d["linkNote"]:
        link += f" ({d['linkNote']})"

    author_year = f"({d['author']}, {d['year']})"
    author_year_link = f"[{author_year}]({d['paper']})"
    name = f"**{d['name']}** {author_year_link}"
    return [
        name,
        d["language"],
        d["domain"],
        d["kind"],
        LEVEL_MAP.get(d["level"]),
        d["instances"],
        d["references"],
        link,
    ]


def reference_ordering(reference_count: Any) -> int:
    if reference_count is None:
        return -1
    elif isinstance(reference_count, str):
        match reference_count:
            case "multiple":
                return 2
            case "n/a":
                return -1
            case _:
                # raise ValueError(f"Bad value for reference count: {reference_count}")
                return 100
    elif isinstance(reference_count, int):
        return reference_count
    else:
        raise ValueError(f"Bad value for reference count: {reference_count}")


with open("data.yml") as f:
    datasets = yaml.load(f, Loader=SafeLoader)

datasets = datasets["datasets"].values()
# datasets = sorted(datasets, key=lambda d: (DOMAIN_ORDER.index(d["domain"]), d["year"]))
datasets = sorted(datasets, key=lambda d: int(d["year"]), reverse=True)
rows = sorted(map(record_to_row, datasets), key=lambda s: reference_ordering(s[-2]), reverse=True)

table = tabulate(rows, headers=HEADER, tablefmt="github")
table = re.sub(" +", " ", table)  # more compact
table = re.sub("-+", "-", table)  # more compact

with open("README.template.md") as fin:
    text = fin.read()

text = text.replace("{{datasets}}", table)

with open("README.md", "w") as fout:
    fout.write(text)
