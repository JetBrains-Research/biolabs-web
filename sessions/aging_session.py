import re
import argparse
from pathlib import Path
from urllib.request import urlopen, HTTPError

# Hardcoded URLs with data
Y20O20_CONSENSUS_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                        "/Y20O20/peaks/{}/zinbra/consensus"
Y20O20_BW_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq/Y20O20" \
                 "/bigwigs/{}"
Y20O20_BB_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                   "/Y20O20/peaks/{}/{}/bigBed"
ENCODE_BW_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                 "/cd14encode/bigwigs"
ENCODE_BB_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                   "/cd14encode/peaks/{}/{}/bigBed"
LABELS_URL = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq/Y20O20" \
             "/labels/{}_labels.bed"
GSM_HIST_MAP = {
    'H3K27ac': 'GSM1102782',
    'H3K27me3': 'GSM1102785',
    'H3K36me3': 'GSM1102788',
    'H3K4me1': 'GSM1102793',
    'H3K4me3': 'GSM1102797'
}
HIST_TOOL_PATH_MAP = {
    'H3K27ac': {'macs_broad'},
    'H3K27me3': {'macs_broad', 'sicer'},
    'H3K36me3': {'macs_broad', 'sicer'},
    'H3K4me1': {'macs_broad'},
    'H3K4me3': {'macs_broad'}
}
HIST_COLOR_MAP = {
    "H3K27ac": (255, 0, 0),
    "H3K27me3": (153, 0, 255),
    "H3K4me1": (255, 153, 0),
    "H3K4me3": (51, 204, 51),
    "H3K36me3": (0, 0, 204)
}
TOOL_COLOR_MAP = {
    "broad": (55, 126, 184),
    "island": (228, 26, 28),
    "peaks": (152, 78, 163),
    "zinbra": (152, 78, 163)
}
HREF_MASK = '<a href="([^"]*.{})">'

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<Session genome="hg19" hasGeneTrack="true" hasSequenceTrack="true" locus="All" \
path="/home/user/aging/${HIST}_igv_session.xml" version="8">
    <Resources>"""
RESOURCE_TEMPLATE = "        <Resource path=\"{}\"/>"
RESOURCE_FOOTER = """    </Resources>
    <Panel height="591" name="DataPanel" width="1836">"""
IGV_TRACK_TEMPLATE = """        <Track altColor="{}" autoScale="true" \
clazz="org.broad.igv.track.FeatureTrack" color="{}" \
colorScale="ContinuousColorScale;0.0;100.0;255,255,255;{}" displayMode="COLLAPSED" \
featureVisibilityWindow="-1" fontSize="10" id="{}" name="{}" renderer="BASIC_FEATURE" \
sortable="false" visible="true" windowFunction="count">
            <DataRange baseline="0.0" drawBaseline="true" flipAxis="false" maximum="100.0" \
minimum="0.0" type="LINEAR"/>
        </Track>"""
UCSC_TRACK_TEMPLATE = """track {} name="{}" visibility={} maxHeightPixels=50:100:11 \
windowingFunction=maximum smoothingWIndow=off {} {}"""
FOOTER = """    </Panel>
    <Panel height="367" name="FeaturePanel" width="1836">
        <Track altColor="0,0,178" autoScale="false" color="0,0,178" displayMode="COLLAPSED" \
featureVisibilityWindow="-1" fontSize="10" id="Reference sequence" name="Reference sequence" \
sortable="false" visible="true"/>
        <Track altColor="0,0,178" autoScale="false" clazz="org.broad.igv.track.FeatureTrack" \
color="0,0,178" colorScale="ContinuousColorScale;0.0;423.0;255,255,255;0,0,178" \
displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" height="35" id="hg19_genes" \
name="RefSeq Genes" renderer="BASIC_FEATURE" sortable="false" visible="true" windowFunction="count">
            <DataRange baseline="0.0" drawBaseline="true" flipAxis="false" maximum="423.0" \
minimum="0.0" type="LINEAR"/>
        </Track>
    </Panel>
    <PanelLayout dividerFractions="0.6145077720207254"/>
    <HiddenAttributes>
        <Attribute name="DATA FILE"/>
        <Attribute name="DATA TYPE"/>
        <Attribute name="NAME"/>
    </HiddenAttributes>
</Session>"""
IGV_BROWSER = "igv"
UCSC_BROWSER = "ucsc"
failed_tracks = []


def _cli():
    parser = argparse.ArgumentParser(
        description="For given histone modification generates IGV aging session",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("hist", help="Histone modification")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("browser", help="Browser name (igv or ucsc)")
    parser.add_argument('--extended',
                        help="Include macs broad and sicer default peaks into session",
                        type=bool, default=False, required=False)

    args = parser.parse_args()
    hist = args.hist
    output = args.output
    browser = args.browser
    extended = args.extended

    y20o20_consensuses = search_in_url(Y20O20_CONSENSUS_PATH.format(hist),
                                       '<a href="([^"]*consensus[^"]*)">')
    y20o20_total_consensuses = [y20o20_cons for y20o20_cons in y20o20_consensuses
                                if "OD" not in y20o20_cons and "YD" not in y20o20_cons]
    y20o20_bws = search_in_url(Y20O20_BW_PATH.format(hist), HREF_MASK.format("bw"))
    y20o20_zinbra_peaks = search_in_url(Y20O20_BB_PATH.format(hist, 'zinbra'),
                                        HREF_MASK.format("bb"))
    y20o20_macs_broad_peaks = []
    y20o20_sicer_peaks = []
    if extended:
        y20o20_macs_broad_peaks = search_in_url(Y20O20_BB_PATH.format(hist, 'macs_broad'),
                                                HREF_MASK.format("bb"))
        try:
            y20o20_sicer_peaks = search_in_url(Y20O20_BB_PATH.format(hist, 'sicer'),
                                               HREF_MASK.format("bb"))
        except HTTPError:
            print("Fail to find sicer peaks, skipping them.")

    encode_bws = search_in_url(ENCODE_BW_PATH,
                               '<a href="([^"]*{}[^"]*.bw)">'.format(GSM_HIST_MAP[hist]))
    encode_peaks = []
    for tool_path in HIST_TOOL_PATH_MAP[hist]:
        encode_peaks += search_in_url(ENCODE_BB_PATH.format(hist, tool_path),
                                      '<a href="([^"]*{}[^"]*.bb)">'.format(GSM_HIST_MAP[hist]))

    with open(output, 'w') as f:
        if browser == IGV_BROWSER:
            print(HEADER, file=f)

            for path in y20o20_total_consensuses + y20o20_bws + y20o20_zinbra_peaks + \
                    y20o20_macs_broad_peaks + y20o20_sicer_peaks + encode_bws + \
                    encode_peaks + [LABELS_URL.format(hist)]:
                print(RESOURCE_TEMPLATE.format(path), file=f)
            print(RESOURCE_FOOTER, file=f)

        insensitive_hist = re.compile(re.escape(hist), re.IGNORECASE)

        print_tracks(hist, browser, y20o20_total_consensuses, "", f, visibility="dense")
        for i in range(0, len(y20o20_bws)):
            print_tracks(hist, browser, [y20o20_bws[i]], "type=bigWig", f, visibility="full",
                         name_processor=lambda x: insensitive_hist.sub(hist, x.upper()))
            print_tracks(hist, browser, [y20o20_zinbra_peaks[i]], "type=bigBed", f,
                         visibility="dense", name_processor=lambda x: "ZINBRA " + x)
            if extended:
                if i < len(y20o20_macs_broad_peaks):
                    print_tracks(hist, browser, [y20o20_macs_broad_peaks[i]], "type=bigBed", f,
                                 visibility="dense", name_processor=lambda x: "MACS " + x)
                if i < len(y20o20_sicer_peaks):
                    print_tracks(hist, browser, [y20o20_sicer_peaks[i]], "type=bigBed", f,
                                 visibility="dense", name_processor=lambda x: "SICER " + x)

        print_tracks(hist, browser, encode_bws, "type=bigWig", f, visibility="full")
        print_tracks(hist, browser, encode_peaks, "type=bigBed", f, visibility="dense",
                     name_processor=lambda x: ("MACS " if "broad" in x else "SICER ") + x)
        print(format_track(browser, "", LABELS_URL.format(hist), "", visibility="dense"), file=f)

        if browser == IGV_BROWSER:
            print(FOOTER, file=f)


def print_tracks(hist, browser, paths, track_type, file, visibility="", name_processor=lambda x: x):
    for path in paths:
        print(format_track(browser, get_color(hist, path), path, track_type, visibility=visibility,
                           name_processor=name_processor), file=file)


def format_track(browser, color, path, track_type, visibility="", name_processor=lambda x: x):
    if browser == IGV_BROWSER:
        return IGV_TRACK_TEMPLATE.format(color, color, color, path, name_processor(Path(path).stem))
    if browser == UCSC_BROWSER:
        return UCSC_TRACK_TEMPLATE.format("" if urlopen(path).getheader("Content-Length") == '0'
                                          else track_type, name_processor(Path(path).stem),
                                          visibility,
                                          "itemRgb=On" if "labels" in path else "color=" + color,
                                          ("bigDataUrl=" if "big" in track_type else "\n") + path)


def get_color(hist, filename):
    if "failed" in filename.lower() or re.match('.*[YO]D\\d+.*', filename, flags=re.IGNORECASE) \
            and re.findall('[YO]D\\d+', filename, flags=re.IGNORECASE)[0].lower() in failed_tracks:
        failed_tracks.append(re.findall('[YO]D\\d+', filename, flags=re.IGNORECASE)[0].lower())
        return "192,192,192"
    color = HIST_COLOR_MAP[hist]
    for tool in TOOL_COLOR_MAP.keys():
        if tool in filename:
            color = TOOL_COLOR_MAP[tool]
            break
    if "od" in filename.split("/")[-1].lower():
        return ','.join(str(int(x * 0.7)) for x in color)
    else:
        return ','.join(str(x) for x in color)


def search_in_url(url, regexp):
    print('Crawling urls at {} by regexp {}'.format(url, regexp))
    html = str(urlopen(url).read())
    file_names = re.findall(regexp, html)
    file_urls = [url + "/" + file_name for file_name in file_names]
    return file_urls


if __name__ == "__main__":
    _cli()
