# Hardcoded URLs with data
import argparse

from sessions.aging_session import search_in_url, HIST_TOOL_PATH_MAP, IGV_BROWSER, HEADER, RESOURCE_TEMPLATE, \
    RESOURCE_FOOTER, print_tracks, format_track, FOOTER, TOOL_COLOR_MAP

ENCODE_BW_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                 "/cd14encode/bigwigs"
ENCODE_PEAK_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                   "/cd14encode/peaks/{}/{}/bigBed"
ENCODE_BB_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                 "/cd14encode/peaks/{}/encode/{}.bigBed"
LABELS_URL = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq/Y20O20" \
             "/labels/{}_labels.bed"
ENCODE_HIST_MAP = {
    'H3K27ac': {'GSM': 'GSM1102782', 'ENC': 'ENCFF439NLA'},
    'H3K27me3': {'GSM': 'GSM1102785', 'ENC': 'ENCFF575VMI'},
    'H3K36me3': {'GSM': 'GSM1102788', 'ENC': 'ENCFF003KSH'},
    'H3K4me1': {'GSM': 'GSM1102793', 'ENC': 'ENCFF158WJC'},
    'H3K4me3': {'GSM': 'GSM1102797', 'ENC': 'ENCFF317WLK'}
}


def _cli():
    parser = argparse.ArgumentParser(
        description="For given histone modification generates IGV aging session",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("hist", help="Histone modification")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("browser", help="Browser name (igv or ucsc)")

    args = parser.parse_args()
    hist = args.hist
    output = args.output
    browser = args.browser

    encode_bws = search_in_url(ENCODE_BW_PATH,
                               '<a href="([^"]*{}[^"]*bw)">'.format(ENCODE_HIST_MAP[hist]['GSM']))
    encode_default_peaks = []
    for tool_path in HIST_TOOL_PATH_MAP[hist]:
        encode_default_peaks += search_in_url(ENCODE_PEAK_PATH.format(hist, tool_path),
                                              '<a href="([^"]*{}[^"]*.bb)">'
                                              .format(ENCODE_HIST_MAP[hist]['GSM']))
    encode_tuned_peaks = search_in_url(ENCODE_PEAK_PATH.format(hist, "zinbra"),
                                       '<a href="([^"]*{}[^"]*.bb)">'
                                       .format(ENCODE_HIST_MAP[hist]['GSM']))

    with open(output, 'w') as f:
        big_bed_path = ENCODE_BB_PATH.format(hist, ENCODE_HIST_MAP[hist]['ENC'])

        if browser == IGV_BROWSER:
            print(HEADER, file=f)

            for path in encode_bws + encode_default_peaks + encode_tuned_peaks + \
                    [big_bed_path] + [LABELS_URL.format(hist)]:
                print(RESOURCE_TEMPLATE.format(path), file=f)
            print(RESOURCE_FOOTER, file=f)

        print_tracks(hist, browser, encode_bws, "type=bigWig", f, visibility="full")
        print_tracks(hist, browser, encode_default_peaks, "type=bigBed", f, visibility="dense",
                     name_processor=lambda x: ("MACS " if "broad" in x else "SICER ") + x)
        print(format_track(browser, ','.join(str(x) for x in TOOL_COLOR_MAP["narrow"]),
                           big_bed_path, "type=bigBed", visibility="dense",
                           name_processor=lambda _:
                           "Encode {} macs narrow".format(ENCODE_HIST_MAP[hist]['GSM'])), file=f)
        print_tracks(hist, browser, encode_tuned_peaks, "type=bigBed", f, visibility="dense",
                     name_processor=lambda x: "ZINBRA " + x)
        print(format_track(browser, "", LABELS_URL.format(hist), "", visibility="dense"), file=f)

        if browser == IGV_BROWSER:
            print(FOOTER, file=f)


if __name__ == "__main__":
    _cli()
