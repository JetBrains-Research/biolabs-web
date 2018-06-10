#!/bin/bash

# A track list file is supplied as a parameter, cf. e.g. /mnt/stripe/dievsky/annotations/H3K36me3_AM_immune.txt

TRACK_LIST=$(cat $1)

# The file name is converted to the dataset name

DATASET=$(echo $1 | sed 's#^.*/##g; s#\.txt$##g;')
TARGET=$(echo $DATASET | sed 's#_.*$##g;')
OUTPUT="${DATASET}_session.xml"

# Hardcoded URLs with data

BW_DIR="https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq/mcgill/bigwigs"
LABEL_DIR="https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq/mcgill/labels/${DATASET}"
PEAK_PATH="https://artyomovlab.wustl.edu/publications/supp_materials/aging/chipseq/mcgill/$DATASET/benchmark/$TARGET/zinbra"

# Shameless exploit of server's redirect (trying to GET a directory returns an HTML file list) to get peak files.

wget $PEAK_PATH -O ./index.html

PEAK_LIST=$(cat ./index.html | sed 's#.*<a href=\"\([^"]*\)\">.*#\1#g; t; d;' | grep '_peaks\.bed$')

# Generate the session file.

(echo '<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<Session genome="hg19" hasGeneTrack="true" hasSequenceTrack="true" locus="All" path="/home/user/mcgill/igv_session.xml" version="8">
    <Resources>'

for TRACK in $TRACK_LIST;
do ID=${TRACK##McGill};
LABEL_URL=$LABEL_DIR/$TRACK.bed;
BW_URL=${BW_DIR}/${TARGET}_$ID.bw;
echo "        <Resource path=\"$LABEL_URL\"/>"
echo "        <Resource path=\"$BW_URL\"/>"
PEAK_FILE=$(echo "$PEAK_LIST" | grep $ID | head -n 1)
if [ -n $PEAK_FILE ];
then
PEAK_URL="$PEAK_PATH/$PEAK_FILE";
echo "        <Resource path=\"$PEAK_URL\"/>";
fi;
done;

echo '    </Resources>
    <Panel height="591" name="DataPanel" width="1836">'

for TRACK in $TRACK_LIST;
do ID=${TRACK##McGill};
LABEL_URL=$LABEL_DIR/$TRACK.bed;
BW_URL=${BW_DIR}/${TARGET}_$ID.bw;
echo '        <Track altColor="0,0,178" autoScale="true" clazz="org.broad.igv.track.DataSourceTrack" color="0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10"' "id=\"$BW_URL\" name=\"$TARGET $ID signal\"" 'normalize="false" renderer="BAR_CHART" sortable="true" visible="true" windowFunction="mean">
            <DataRange baseline="0.0" drawBaseline="true" flipAxis="false" maximum="100.0" minimum="0.0" type="LINEAR"/>
        </Track>
        <Track altColor="0,0,178" autoScale="false" clazz="org.broad.igv.track.FeatureTrack" color="0,0,178" colorScale="ContinuousColorScale;0.0;12.0;255,255,255;0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10"' "id=\"$LABEL_URL\" name=\"$DATASET $ID labels\"" 'renderer="BASIC_FEATURE" sortable="false" visible="true" windowFunction="count">
            <DataRange baseline="0.0" drawBaseline="true" flipAxis="false" maximum="12.0" minimum="0.0" type="LINEAR"/>
        </Track>'
PEAK_FILE=$(echo "$PEAK_LIST" | grep $ID | head -n 1)
if [ -n $PEAK_FILE ];
then
echo '        <Track altColor="0,0,178" autoScale="false" clazz="org.broad.igv.track.FeatureTrack" color="0,0,178" colorScale="ContinuousColorScale;0.0;100.0;255,255,255;0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10"' "id=\"$PEAK_PATH/$PEAK_FILE\" name=\"ZINBRA $DATASET $ID peaks\"" 'renderer="BASIC_FEATURE" sortable="false" visible="true" windowFunction="count">
            <DataRange baseline="0.0" drawBaseline="true" flipAxis="false" maximum="100.0" minimum="0.0" type="LINEAR"/>
        </Track>'
fi;
done;

echo '    </Panel>
    <Panel height="367" name="FeaturePanel" width="1836">
        <Track altColor="0,0,178" autoScale="false" color="0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" id="Reference sequence" name="Reference sequence" sortable="false" visible="true"/>
        <Track altColor="0,0,178" autoScale="false" clazz="org.broad.igv.track.FeatureTrack" color="0,0,178" colorScale="ContinuousColorScale;0.0;423.0;255,255,255;0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" height="35" id="hg19_genes" name="RefSeq Genes" renderer="BASIC_FEATURE" sortable="false" visible="true" windowFunction="count">
            <DataRange baseline="0.0" drawBaseline="true" flipAxis="false" maximum="423.0" minimum="0.0" type="LINEAR"/>
        </Track>
    </Panel>
    <PanelLayout dividerFractions="0.6145077720207254"/>
    <HiddenAttributes>
        <Attribute name="DATA FILE"/>
        <Attribute name="DATA TYPE"/>
        <Attribute name="NAME"/>
    </HiddenAttributes>
</Session>') > $OUTPUT
