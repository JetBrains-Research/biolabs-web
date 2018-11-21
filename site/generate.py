import datetime
import os
import re
import shutil

from collections import namedtuple

# Hardcoded URLs with data
from sessions.aging_session import GSM_HIST_MAP, LABELS_URL, Y20O20_BW_PATH, ENCODE_BW_PATH

# Tools versions
SPAN_BUILD = '0.7.1.4518'
SPAN_DATE = 'Nov 21, 2018'

JBR_BUILD = '1.0.beta.4254'
JBR_DATE = 'Sep 11, 2018'

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
SPAN_MODELS_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                   "/Y20O20/span/{}"

BASIC_UCSC_SESSION_PATH = "https://genome.ucsc.edu/cgi-bin/hgTracks?" \
                          "hgS_doOtherUser=submit&hgS_otherUserName=Biolabs&" \
                          "hgS_otherUserSessionName={}%20Aging"
BASIC_UCSC_SESSION_TXT_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging" \
                              "/chipseq/sessions/Y20O20/{}_aging_session.txt"
BASIC_IGV_SESSION_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                         "/sessions/Y20O20/{}_aging_session.xml"
EXTENDED_UCSC_SESSION_PATH = "https://genome.ucsc.edu/cgi-bin/hgTracks?" \
                             "hgS_doOtherUser=submit&hgS_otherUserName=Biolabs&" \
                             "hgS_otherUserSessionName={}%20Aging%20Extended"
EXTENDED_UCSC_SESSION_TXT_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging" \
                                 "/chipseq/sessions/Y20O20/{}_aging_session_extended.txt"
EXTENDED_IGV_SESSION_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging" \
                            "/chipseq/sessions/Y20O20/{}_aging_session_extended.xml"
ENCODE_IGV_SESSION_PATH = "http://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                          "/sessions/cd14encode/{}_encode_session.xml"
ENCODE_UCSC_SESSION_PATH = "https://genome.ucsc.edu/cgi-bin/hgTracks?" \
                           "hgS_doOtherUser=submit&hgS_otherUserName=Biolabs&" \
                           "hgS_otherUserSessionName={}%20Encode"
ENCODE_UCSC_SESSION_TXT_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging" \
                               "/chipseq/sessions/cd14encode/{}_encode_session.txt"
ULI_IGV_SESSION_PATH = "http://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                       "/sessions/GSE63523/GSE63523_{}.xml"
ULI_UCSC_SESSION_PATH = "https://genome.ucsc.edu/cgi-bin/hgTracks?hgS_doOtherUser=submit&" \
                        "hgS_otherUserName=Biolabs&hgS_otherUserSessionName=GSE63523%20{}"
ULI_UCSC_SESSION_TXT_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging" \
                            "/chipseq/sessions/GSE63523/GSE63523_{}.txt"
MCGILL_IGV_SESSION_PATH = "http://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq" \
                          "/sessions/mcgill/mcgill_igv_session{}.xml"
MCGILL_UCSC_SESSION_PATH = "https://genome.ucsc.edu/cgi-bin/hgTracks?hgS_doOtherUser=submit" \
                           "&hgS_otherUserName=Biolabs&hgS_otherUserSessionName={}"
MCGILL_UCSC_SESSION_TXT_PATH = "https://artyomovlab.wustl.edu/publications/supp_materials/aging" \
                               "/chipseq/sessions/mcgill/mcgill_ucsc_session{}.txt"

GSM_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={}"

FOLDER = os.path.dirname(__file__)
OUT_FOLDER = FOLDER + '/out'


def generate_explore_page(page):
    explore_template = FOLDER + '/_explore_data.html'
    print('Creating explore data page {} by template {}'.format(page,
                                                                explore_template))
    with open(explore_template, 'r') as file:
        template_html = file.read()

    def create_tr_online(hist):
        return '<tr>' + \
               '<th>{}</th>'.format(hist) + \
               ('<td class="text-center"><a href="{}" title="Basic UCSC custom tracks session">'
                'Session</a>&nbsp;&sol;&nbsp;'
                '<a href="{}" title="Basic UCSC custom tracks session file">Txt</a></td>').format(
                   BASIC_UCSC_SESSION_PATH.format(hist),
                   BASIC_UCSC_SESSION_TXT_PATH.format(hist)) + \
               ('<td class="text-center"><a href="{}" title="Extended UCSC custom tracks session">'
                'Session</a>&nbsp;&sol;&nbsp;'
                '<a href="{}" title="Extended UCSC custom tracks session file">Txt</a></td>').format(
                   EXTENDED_UCSC_SESSION_PATH.format(hist),
                   EXTENDED_UCSC_SESSION_TXT_PATH.format(hist)) + \
               '</tr>'

    def create_tr_session(hist):
        return '<tr>' + \
               '<th>{}</th>'.format(hist) + \
               ('<td class="text-center"><a href="{}" title="Basic IGV/JBR session file">xml</a>'
                '</td>').format(BASIC_IGV_SESSION_PATH.format(hist)) + \
               ('<td class="text-center"><a href="{}" title="Extended IGV/JBR session file">'
                'xml</a></td>').format(EXTENDED_IGV_SESSION_PATH.format(hist)) + \
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
               '<td class="text-center"><a href="{}">Alignment</a></td>'.format(BEDGZ_PATH.format(hist)) + \
               '<td class="text-center"><a href="{}">QC</a></td>'.format(FASTQC_PATH.format(hist)) + \
               ('<td class="text-center"><a href="{}">BigWigs</a>&nbsp;' +
                '<a href="explore_chipseq.html" title="Explore data">'
                '<img class="icon-url" src="glyphicons-52-eye-open.png"/></a></td>').format(
                   Y20O20_BW_PATH.format(hist)) + \
               '<td class="text-center"><a href="{}">Peaks</a></td>'.format(PEAKS_PATH.format(hist, 'span')) + \
               '<td class="text-center"><a href="{}">Labels</a></td>'.format(LABELS_URL.format(hist)) + \
               ('<td class="text-center"><a href="{}">Models</a>&nbsp;' +
                '<a href="howto.html" title="Visual peak calling how to">' +
                '<img class="icon-url" src="glyphicons-195-question-sign.png"/></a></td>').format(
                   SPAN_MODELS_PATH.format(hist)) + '</tr>'

    table_chipseq = '\n'.join([create_tr_chipseq(hist) for hist in sorted(GSM_HIST_MAP.keys())])

    def create_tr_encode(hist):
        return '<tr>' + \
               '<th>{}</th>'.format(hist) + \
               ('<td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}">' +
                '{0}</a></td>').format(GSM_HIST_MAP[hist]) + \
               '<td><a href="{}/{}_hg19.bw">BigWigs</a></td>'.format(ENCODE_BW_PATH, GSM_HIST_MAP[hist]) + \
               '<td><a href="{}">Peaks</a></td>'.format(ENCODE_PEAKS_PATH.format(hist)) + \
               '<td><a href="{}">Labels</a></td>'.format(ENCODE_LABELS_URL.format(hist)) + \
               '</tr>'

    table_encode = '\n'.join([create_tr_encode(hist) for hist in sorted(GSM_HIST_MAP.keys())])

    with open(OUT_FOLDER + '/' + page, 'w') as file:
        file.write(template_html.
                   replace('@TABLE_CHIPSEQ@', table_chipseq).
                   replace('@TABLE_ENCODE@', table_encode))


DistrDescriptor = namedtuple('DistrDescriptor', ['title', 'suffix', 'folder'])


def generate_jbr_data(page):
    template = FOLDER + '/_jbr.html'

    print('Creating download data page {} by template {}'.format(page, template))
    with open(template, 'r') as f:
        template_html = f.read()

    def create_tr(dd, build):
        code_base = "https://download.jetbrains.com/biolabs/jbr_browser"
        fname = "jbr-{}{}".format(build, dd.suffix)
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
            replace('@TABLE@', '\n'.join([create_tr(d, JBR_BUILD) for d in descrs])) \
            .replace('@BUILD@', JBR_BUILD) \
            .replace('@DATE@', JBR_DATE)

        seen_file_names = set()
        for dd in descrs:
            fname = '@FILENAME-{}@'.format(dd.folder)
            if fname not in seen_file_names:
                seen_file_names.add(fname)
                content = content.replace(fname, "{}{}".format(JBR_BUILD, dd.suffix))

        f.write(content)


def generate_span_data(page):
    template = FOLDER + '/_span.html'

    print('Creating download data page {} by template {}'.format(page, template))
    with open(template, 'r') as f:
        template_html = f.read()

    def create_tr(build):
        return """
        <tr>
            <td> <a href="https://download.jetbrains.com/biolabs/span/{0}">{0}</a></td>
            <td> Multi-platform JAR package </td>
        </tr>
        """.format("span-{0}.jar".format(build))

    with open(OUT_FOLDER + '/' + page, 'w') as f:
        f.write(template_html.
                replace('@TABLE@', create_tr(SPAN_BUILD)).
                replace('@BUILD@', SPAN_BUILD).
                replace('@DATE@', SPAN_DATE)
                )


def generate_study_cases_page(page):
    study_cases_template = FOLDER + '/_study_cases.html'
    print('Creating study cases page {} by template {}'.format(page,
                                                               study_cases_template))
    with open(study_cases_template, 'r') as file:
        template_html = file.read()

    def create_tr_session(name, igv_session_path, ucsc_session_path, ucsc_session_txt_path,
                          gsm=False):
        return '<tr>' + \
               '<th>{}</th>'.format(name[0]) + \
               (('<td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}">' +
                 '{0}</a></td>').format(GSM_HIST_MAP[name[0]]) if gsm else '') + \
               ('<td class="text-center"><a href="{}" title="IGV/JBR session file">xml</a>'
                '</td>').format(igv_session_path.format(name[1])) + \
               ('<td class="text-center"><a href="{}" title="UCSC custom tracks session">'
                'Session</a>&nbsp;&sol;&nbsp;'
                '<a href="{}" title="UCSC custom tracks session file">txt</a></td>').format(
                   ucsc_session_path.format(name[0]), ucsc_session_txt_path.format(name[1])) + \
               '</tr>'

    with open(OUT_FOLDER + '/' + page, 'w') as file:
        file.write(template_html
                   .replace('@ENCODE_TABLE@', '\n'.join([create_tr_session(
            (hist, hist), ENCODE_IGV_SESSION_PATH, ENCODE_UCSC_SESSION_PATH,
            ENCODE_UCSC_SESSION_TXT_PATH, True)
            for hist in sorted(GSM_HIST_MAP.keys())]))
                   .replace('@ULI_TABLE@', '\n'.join([create_tr_session(
            hist, ULI_IGV_SESSION_PATH, ULI_UCSC_SESSION_PATH,
            ULI_UCSC_SESSION_TXT_PATH) for hist in [("H3K27me3", "k27me3"),
                                                    ("H3K4me3", "k4me3")]]))
                   .replace('@MCGILL_TABLE@', '\n'.join([create_tr_session(
            name, MCGILL_IGV_SESSION_PATH, MCGILL_UCSC_SESSION_PATH,
            MCGILL_UCSC_SESSION_TXT_PATH) for name in
            [("McGill", ""),
             ("McGill Input", "_input")]]))
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

    print('Creating explore data pages')
    content_page = '_explore_data.html'
    generate_explore_page(content_page)
    generate_page('explore_data.html',
                  title='Explore Data', scripts='', content=content_page)

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

    print('Creating study cases page')
    content_page = '_study_cases.html'
    generate_study_cases_page(content_page)
    generate_page('study_cases.html',
                  title='Study cases', scripts='', content=content_page)

    print('Done')


if __name__ == "__main__":
    _cli()
