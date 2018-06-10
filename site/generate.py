import os
import re
import shutil
from pathlib import Path

# Hardcoded URLs with data
from sessions.aging_session import search_in_url, get_color

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

BEDGZ_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
             "/Y20O20/bedgz/{}"
PEAKS_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
             "/Y20O20/peaks/{}/{}"
ZINBRA_MODELS_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                     "/Y20O20/zinbra"

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

failed_tracks = []

FOLDER = os.path.dirname(__file__)
OUT_FOLDER = FOLDER + '/out'


def generate_explore_data_page(hist, page):
    explore_data_template = FOLDER + '/_explore_data.html'
    print('Creating explore data page {} by template {}'.format(page,
                                                                explore_data_template))
    with open(explore_data_template, 'r') as file:
        template_html = file.read()

    tracks = []

    y20o20_consensuses = search_in_url(Y20O20_CONSENSUS_PATH.format(hist),
                                       '<a href="([^"]*consensus[^"]*)">')
    y20o20_total_consensuses = [y20o20_cons for y20o20_cons in y20o20_consensuses
                                if "OD" not in y20o20_cons and "YD" not in y20o20_cons]
    y20o20_bws = search_in_url(Y20O20_BW_PATH.format(hist), HREF_MASK.format("bw"))
    y20o20_zinbra_peaks = search_in_url(Y20O20_BB_PATH.format(hist, 'zinbra'),
                                        HREF_MASK.format("bb"))
    encode_bws = search_in_url(ENCODE_BW_PATH,
                               '<a href="([^"]*{}[^"]*.bw)">'.format(GSM_HIST_MAP[hist]))
    encode_peaks = []
    for tool_path in HIST_TOOL_PATH_MAP[hist]:
        encode_peaks += search_in_url(ENCODE_BB_PATH.format(hist, tool_path),
                                      '<a href="([^"]*{}[^"]*.bb)">'.format(
                                          GSM_HIST_MAP[hist]))

        insensitive_hist = re.compile(re.escape(hist), re.IGNORECASE)

        tracks.extend(format_tracks(hist, y20o20_total_consensuses))
        for i in range(0, len(y20o20_bws)):
            tracks.extend(format_tracks(hist, [y20o20_bws[i]],
                                        name_processor=lambda x:
                                            insensitive_hist.sub(hist, x.upper())))
            tracks.extend(format_tracks(hist, [y20o20_zinbra_peaks[i]],
                                        name_processor=lambda x: "ZINBRA " + x))

        tracks.extend(format_tracks(hist, encode_bws))
        tracks.extend(format_tracks(hist, encode_peaks,
                                    name_processor=lambda x:
                                        ("MACS " if "broad" in x else "SICER ") + x))
        tracks.append(format_track(hist, LABELS_URL.format(hist)))

    with open(OUT_FOLDER + '/' + page, 'w') as file:
        file.write(template_html
                   .replace('@MODIFICATION@', hist)
                   .replace('//@TRACKS@', ',\n'.join(tracks)))


def format_tracks(hist, paths, name_processor=lambda x: x):
    return [format_track(hist, path, name_processor) for path in paths]


def format_track(hist, uri, name_processor=lambda x: x):
    return """{
    name: '@NAME@',
    bwgURI: '@URI@',
    style: [{
        type: 'default', 
        style: {glyph: 'HISTOGRAM', BGCOLOR: 'rgb(@RGB@)', HEIGHT: 30, id: 'style1'}
    }],
    noDownsample: false
}""".replace('@NAME@', name_processor(Path(uri).stem))\
        .replace('@URI@', uri).replace('@RGB@', get_color(hist, uri))


def generate_download_chipseq_page(page):
    download_chipseq_template = FOLDER + '/_download_chipseq.html'
    print('Creating download data page {} by template {}'.format(page, download_chipseq_template))
    with open(download_chipseq_template, 'r') as file:
        template_html = file.read()

    def create_tr(hist):
        return '<tr><th>{}</th>'.format(hist) + \
               '<th><a href="{}">Reads</a></th>'.format(BEDGZ_PATH.format(hist)) + \
               '<th><a href="{}">BigWigs</a></th>'.format(Y20O20_BW_PATH.format(hist)) + \
               '<th><a href="{}">Peaks</a></th>'.format(PEAKS_PATH.format(hist, 'zinbra')) + \
               '<th><a href="{}">Labels</a></th>'.format(LABELS_URL.format(hist)) + \
               '<th><a href="{}">Models</a></th>'.format(ZINBRA_MODELS_PATH) + '</tr>'

    table = """<table class="table table-striped">
                        <thead>
                        <tr>
                            <th>Modification</th>
                            <th>Reads</th>
                            <th>Bigwigs</th>
                            <th>Peaks</th>
                            <th>Peak caller labels</th>
                            <th>Peak caller models</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr>""" + '\n'.join([create_tr(hist) for hist in GSM_HIST_MAP.keys()]) + \
            """</tr>
            </tbody>
        </table>"""
    with open(OUT_FOLDER + '/' + page, 'w') as file:
        file.write(template_html.replace('@TABLE@', table))


def generate_page(page, title, scripts, content):
    template_path = FOLDER + '/template.html'
    print('Creating page {} by template {}\ntitle={}\nscripts={}\ncontent={}'.format(
        page, template_path, title, scripts, content
    ))
    with open(template_path, 'r') as file:
        template_html = file.read()
    with open(OUT_FOLDER + '/' + page, 'w') as file:
        file.write(template_html.
                   replace('@TITLE@', title).
                   replace('@SCRIPTS@', scripts).
                   replace('@CONTENT@', content))


def _cli():
    if os.path.exists(OUT_FOLDER):
        shutil.rmtree(OUT_FOLDER)
    os.mkdir(OUT_FOLDER)
    print('Generating site structure in {}'.format(OUT_FOLDER))

    print('Copying resources')
    for file in os.listdir(FOLDER):
        if re.match('.*\.(html|css|png)', file) and not re.match('template\\.html', file):
            shutil.copy(file, OUT_FOLDER)

    print('Generate static pages')
    generate_page('index.html', title='Multiomics dissection of healthy human aging',
                  scripts='', content='_index.html')
    generate_page('paper.html',
                  title='Paper', scripts='', content='_paper.html')
    generate_page('software.html',
                  title='Software', scripts='', content='_software.html')

    print('Creating explore data pages')
    for hist in GSM_HIST_MAP.keys():
        content_page = '_explore_data_{}.html'.format(hist).lower()
        generate_explore_data_page(hist, content_page)
        # biodallance should be included within main html page
        generate_page('{}.html'.format(hist).lower(),
                      title=hist,
                      scripts="""
<script type="text/javascript" 
    src="//www.biodalliance.org/release-0.13/dalliance-compiled.js"></script>""",
                      content=content_page)

    print('Creating download chipseq page')
    content_page = '_download_chipseq.html'
    generate_download_chipseq_page(content_page)
    generate_page('download_chipseq.html',
                  title='Download ChIP-Seq', scripts='', content=content_page)

    print('Done')


if __name__ == "__main__":
    _cli()
