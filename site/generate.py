import os
import re
import shutil
from pathlib import Path

# Hardcoded URLs with data
from sessions.aging_session import search_in_url, get_color, HREF_MASK, HIST_TOOL_PATH_MAP, GSM_HIST_MAP, \
    Y20O20_CONSENSUS_PATH, LABELS_URL, Y20O20_BW_PATH, Y20O20_BB_PATH, ENCODE_BW_PATH, ENCODE_BB_PATH

ENCODE_PEAKS_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                    "/cd14encode/peaks/{}"
ENCODE_LABELS_URL = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq/cd14encode" \
                    "/labels/{}_labels.bed"

BEDGZ_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
             "/Y20O20/bedgz/{}"
FASTQC_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
              "/Y20O20/qc/fastq/{}/fastqc/"
PEAKS_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
             "/Y20O20/peaks/{}/{}"
ZINBRA_MODELS_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                     "/Y20O20/zinbra"

GSM_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={}"

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
}""".replace('@NAME@', name_processor(Path(uri).stem)) \
        .replace('@URI@', uri).replace('@RGB@', get_color(hist, uri))


def generate_download_chipseq_page(page):
    download_chipseq_template = FOLDER + '/_download_chipseq.html'
    print('Creating download data page {} by template {}'.format(page, download_chipseq_template))
    with open(download_chipseq_template, 'r') as file:
        template_html = file.read()

    def create_tr(hist):
        return '<tr>' + \
               '<th>{}</th>'.format(hist) + \
               '<th><a href="{}">Reads</a></th>'.format(BEDGZ_PATH.format(hist)) + \
               '<th><a href="{}">QC</a></th>'.format(FASTQC_PATH.format(hist)) + \
               ('<th><a href="{}">BigWigs</a>&nbsp;' +
                '<a href="{}.html" title="Explore data"><span class="glyphicon glyphicon-eye-open" '
                'aria-hidden="true"></span></a></th>').format(Y20O20_BW_PATH.format(hist), hist) + \
               '<th><a href="{}">Peaks</a></th>'.format(PEAKS_PATH.format(hist, 'zinbra')) + \
               '<th><a href="{}">Labels</a></th>'.format(LABELS_URL.format(hist)) + \
               ('<th><a href="{}">Models</a>&nbsp;' +
                '<a href="howto.html" title="Visual peak calling how to">' +
                '<span class="glyphicon glyphicon-question-sign" ' +
                'aria-hidden="true"></span></a></th>').format(ZINBRA_MODELS_PATH) + \
               '</tr>'

    with open(OUT_FOLDER + '/' + page, 'w') as file:
        file.write(template_html.replace('@TABLE@',
                                         '\n'.join([create_tr(hist) for hist in GSM_HIST_MAP.keys()])))


def generate_download_public_data(page):
    download_chipseq_template = FOLDER + '/_public_data.html'
    print('Creating download data page {} by template {}'.format(page, download_chipseq_template))
    with open(download_chipseq_template, 'r') as file:
        template_html = file.read()

    def create_tr(hist):
        return '<tr>' + \
               '<th>{}</th>'.format(hist) + \
               ('<th><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}">' +
                '{0}</a></th>').format(GSM_HIST_MAP[hist]) + \
               '<th><a href="{}/{}_hg19.bw">BigWigs</a></th>'.format(ENCODE_BW_PATH, GSM_HIST_MAP[hist]) + \
               '<th><a href="{}">Peaks</a></th>'.format(ENCODE_PEAKS_PATH.format(hist)) + \
               '<th><a href="{}">Labels</a></th>'.format(ENCODE_LABELS_URL.format(hist)) + \
               '</tr>'

    with open(OUT_FOLDER + '/' + page, 'w') as file:
        file.write(template_html.replace('@TABLE@',
                                         '\n'.join([create_tr(hist) for hist in GSM_HIST_MAP.keys()])))


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
    generate_page('methods.html',
                  title='Methods', scripts='', content='_methods.html')
    generate_page('tools.html',
                  title='Tools', scripts='', content='_tools.html')
    generate_page('howto.html',
                  title='Visual peak calling how to', scripts='', content='_howto.html')

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

    print('Creating download public data page')
    content_page = '_public_data.html'
    generate_download_public_data(content_page)
    generate_page('public_data.html',
                  title='Download Public Data', scripts='', content=content_page)

    print('Done')


if __name__ == "__main__":
    _cli()
