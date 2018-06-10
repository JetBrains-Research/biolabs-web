import argparse

from sessions.aging_session import search_in_url

PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq/Y20O20"
HIST_TOOL_PATH_MAP = {'H3K27ac': {}, 'H3K27me3': {}, 'H3K36me3': {}, 'H3K4me1': {}, 'H3K4me3': {}}
TYPES = {'bed': [], 'broadPeak': [], 'bed.gz': [], 'bw': []}


def _cli():
    parser = argparse.ArgumentParser(
        description="Creates index files for wget",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("output", help="Output file path")

    args = parser.parse_args()
    output = args.output

    for key in HIST_TOOL_PATH_MAP:
        HIST_TOOL_PATH_MAP[key] = {'bed': [], 'broadPeak': [], 'bed.gz': [], 'bw': []}
    paths = [PATH]
    while len(paths) > 0:
        path = paths.pop()
        urls = search_in_url(path, '<a href="([^"?]*)">')
        for url in urls:
            if "publications" not in url.replace(PATH, ""):
                if "." not in url.split("/")[-1]:
                    paths.append(url)
                else:
                    for key in HIST_TOOL_PATH_MAP:
                        if key in url:
                            for extension in HIST_TOOL_PATH_MAP[key]:
                                if url.endswith(extension) and "consensus" not in url and \
                                        "error" not in url and "labels" not in url:
                                    HIST_TOOL_PATH_MAP[key][extension].append(
                                        url.replace("//", "/").replace("https:/", "https://"))
    for key in HIST_TOOL_PATH_MAP:
        for extensions in [['bed', 'broadPeak'], ['bed.gz'], ['bw']]:
            with open(output + "/" + key + "_" + "_".join(extensions) + ".txt", 'w') as f:
                for extension in extensions:
                    for url in HIST_TOOL_PATH_MAP[key][extension]:
                        print(url, file=f)


if __name__ == "__main__":
    _cli()
