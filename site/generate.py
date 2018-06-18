import datetime
import os
import re
import shutil

from collections import namedtuple

# Hardcoded URLs with data
from sessions.aging_session import GSM_HIST_MAP, LABELS_URL, Y20O20_BW_PATH, ENCODE_BW_PATH

DistrDescriptor = namedtuple('DistrDescriptor', ['title', 'suffix', 'folder'])

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

BASIC_UCSC_SESSION_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                          "/sessions/Y20O20/{}_aging_session.txt"
BASIC_IGV_SESSION_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                         "/sessions/Y20O20/{}_aging_session.xml"
EXTENDED_UCSC_SESSION_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                             "/sessions/Y20O20/{}_aging_session_extended.txt"
EXTENDED_IGV_SESSION_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                            "/sessions/Y20O20/{}_aging_session_extended.xml"

GSM_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={}"

FOLDER = os.path.dirname(__file__)
OUT_FOLDER = FOLDER + '/out'


def generate_explore_chipseq_page(page):
    explore_chipseq_template = FOLDER + '/_explore_chipseq.html'
    print('Creating explore data page {} by template {}'.format(page,
                                                                explore_chipseq_template))
    with open(explore_chipseq_template, 'r') as file:
        template_html = file.read()

    def create_tr_online(hist):
        return '<tr>' + \
               '<th>{}</th>'.format(hist) + \
               ('<th class="text-center"><a href="{}" title="Basic UCSC custom tracks session">'
                'Basic</a>&nbsp;&sol;&nbsp;'
                '<a href="{}" title="Extended UCSC custom tracks session">Extended</a></th>').format(
                   BASIC_UCSC_SESSION_PATH.format(hist), EXTENDED_UCSC_SESSION_PATH.format(hist)) + \
               '</tr>'

    def create_tr_session(hist):
        return '<tr>' + \
               '<th>{}</th>'.format(hist) + \
               ('<th class="text-center"><a href="{}" title="Basic IGV/JBR session file">Basic</a>&nbsp;&sol;&nbsp;'
                '<a href="{}" title="Extended IGV/JBR session file">Extended</a></th>').format(
                   BASIC_IGV_SESSION_PATH.format(hist), EXTENDED_IGV_SESSION_PATH.format(hist)) + \
               '</tr>'

    with open(OUT_FOLDER + '/' + page, 'w') as file:
        file.write(template_html
                   .replace('@TABLE@',
                            '\n'.join([create_tr_online(hist) for hist in sorted(GSM_HIST_MAP.keys())]))
                   .replace('@TABLE2@',
                            '\n'.join([create_tr_session(hist) for hist in sorted(GSM_HIST_MAP.keys())])))


def generate_download_data_page(page):
    download_data_template = FOLDER + '/_download_data.html'
    print('Creating download data page {} by template {}'.format(page, download_data_template))
    with open(download_data_template, 'r') as file:
        template_html = file.read()

    def create_tr_chipseq(hist):
        return '<tr>' + \
               '<th>{}</th>'.format(hist) + \
               '<th class="text-center"><a href="{}">Reads</a></th>'.format(BEDGZ_PATH.format(hist)) + \
               '<th class="text-center"><a href="{}">QC</a></th>'.format(FASTQC_PATH.format(hist)) + \
               ('<th class="text-center"><a href="{}">BigWigs</a>&nbsp;' +
                '<a href="explore_chipseq.html" title="Explore data">'
                '<img class="icon-url" src="glyphicons-52-eye-open.png"/></a></th>').format(
                   Y20O20_BW_PATH.format(hist)) + \
               '<th class="text-center"><a href="{}">Peaks</a></th>'.format(PEAKS_PATH.format(hist, 'zinbra')) + \
               '<th class="text-center"><a href="{}">Labels</a></th>'.format(LABELS_URL.format(hist)) + \
               ('<th class="text-center"><a href="{}">Models</a>&nbsp;' +
                '<a href="howto.html" title="Visual peak calling how to">' +
                '<img class="icon-url" src="glyphicons-195-question-sign.png"/></a></th>').format(ZINBRA_MODELS_PATH) + \
               '</tr>'
    table_chipseq = '\n'.join([create_tr_chipseq(hist) for hist in sorted(GSM_HIST_MAP.keys())])

    def create_tr_encode(hist):
        return '<tr>' + \
               '<th>{}</th>'.format(hist) + \
               ('<th><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}">' +
                '{0}</a></th>').format(GSM_HIST_MAP[hist]) + \
               '<th><a href="{}/{}_hg19.bw">BigWigs</a></th>'.format(ENCODE_BW_PATH, GSM_HIST_MAP[hist]) + \
               '<th><a href="{}">Peaks</a></th>'.format(ENCODE_PEAKS_PATH.format(hist)) + \
               '<th><a href="{}">Labels</a></th>'.format(ENCODE_LABELS_URL.format(hist)) + \
               '</tr>'

    table_encode = '\n'.join([create_tr_encode(hist) for hist in sorted(GSM_HIST_MAP.keys())])

    with open(OUT_FOLDER + '/' + page, 'w') as file:
        file.write(template_html.
                   replace('@TABLE_CHIPSEQ@', table_chipseq).
                   replace('@TABLE_ENCODE@', table_encode))


def generate_jbr_data(page):
    build = '1.0.beta.nnnn'
    date = 'Jun 13, 2018'

    # ---------------
    template = FOLDER + '/_jbr.html'

    print('Creating download data page {} by template {}'.format(page, template))
    with open(template, 'r') as f:
        template_html = f.read()

    def create_tr(dd, build):
        code_base = "https://download.jetbrains.com/biolabs/jbr_browser/"
        fname = "{}{}".format(build, dd.suffix)
        url = "{}/{}/{}".format(code_base, dd.folder, fname)
        return """
        <tr>
            <td> <a href="{}">{}</a></td>
            <td>{}</td>
        </tr>
        """.format(url, fname, dd.title)

    with open(OUT_FOLDER + '/' + page, 'w') as f:
        descrs = [
            DistrDescriptor("Windows 64-bit ZIP archive (includes bundled 64-bit Java Runtime)",
                            "_x64.zip", "win"),
            DistrDescriptor("Windows 32-bit ZIP archive (includes bundled 32-bit Java Runtime)",
                            "_x86.zip", "win"),
            DistrDescriptor("Mac installer (includes bundled 64-bit Java Runtime)",
                            ".dmg", "mac"),
            DistrDescriptor("Linux archive (includes bundled 64-bit Java Runtime)",
                            ".tar.gz", "linux"),
        ]

        content = template_html. \
            replace('@TABLE@', '\n'.join([create_tr(d, build) for d in descrs])) \
            .replace('@BUILD@', '1.0.beta.nnnn') \
            .replace('@DATE@', date)

        seen_file_names = set()
        for dd in descrs:
            fname = '@FILENAME-{}@'.format(dd.folder)
            if fname not in seen_file_names:
                seen_file_names.add(fname)
                content = content.replace(fname, "{}{}".format(build, dd.suffix))

        f.write(content)


def generate_span_data(page):
    template = FOLDER + '/_span.html'

    print('Creating download data page {} by template {}'.format(page, template))
    with open(template, 'r') as f:
        template_html = f.read()

    def create_tr(build):
        return """
        <tr>
            <th> <a href="url">todo {}</a></th>
            <th> Multi-platform JAR package </th>
        </tr>
        """.format(build)

    build = '1.0.beta.nnnn'
    with open(OUT_FOLDER + '/' + page, 'w') as f:
        f.write(template_html.
                replace('@TABLE@', create_tr(build)).
                replace('@BUILD@', build).
                replace('@DATE@', 'Jun 13, 2018')
                )


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
                   replace('@CONTENT@', content).
                   replace('@DATE@', datetime.datetime.now().strftime('%c')))


def _cli():
    if os.path.exists(OUT_FOLDER):
        shutil.rmtree(OUT_FOLDER)
    os.mkdir(OUT_FOLDER)
    print('Generating site structure in {}'.format(OUT_FOLDER))

    print('Copying resources')
    for file in os.listdir(FOLDER):
        if re.match('.*\.(html|css|png|svg)', file) and not re.match('template\\.html', file):
            shutil.copy(file, OUT_FOLDER)

    print('Generate static pages')
    generate_page('index.html', title='Multiomics dissection of healthy human aging',
                  scripts='', content='_index.html')
    generate_page('methods.html',
                  title='Methods', scripts='', content='_methods.html')
    generate_page('tools.html',
                  title='Peak Calling Solution', scripts='', content='_tools.html')
    generate_page('howto.html',
                  title='Visual peak calling how to', scripts='', content='_howto.html')
    generate_page('team.html',
                  title='Team', scripts='', content='_team.html')
    generate_page('study_cases.html',
                  title='Study cases', scripts='', content='_study_cases.html')

    print('Creating explore data pages')
    content_page = '_explore_chipseq.html'
    generate_explore_chipseq_page(content_page)
    generate_page('explore_chipseq.html',
                  title='Explore ChIP-Seq', scripts='', content=content_page)

    print('Creating download page')
    content_page = '_download_data.html'
    generate_download_data_page(content_page)
    generate_page('download_data.html',
                  title='Download Data', scripts='', content=content_page)

    print('Creating download tools page')
    content_page = '_jbr.html'
    generate_jbr_data(content_page)
    generate_page('jbr.html',
                  title='JBR Genome Browser', scripts='', content=content_page)

    print('Creating download tools page')
    content_page = '_span.html'
    generate_span_data(content_page)
    generate_page('span.html',
                  title='SPAN Peak Analyzer', scripts='', content=content_page)

    print('Done')


if __name__ == "__main__":
    _cli()
