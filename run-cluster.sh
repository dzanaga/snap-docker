export SPARK_MAJOR_VERSION=2
export SPARK_HOME=/usr/hdp/current/spark2-client
export PYSPARK_PYTHON="/usr/bin/python3.5"

GRAPH_FILE="graph_template_28N.xml"
OUTPUT_DIR="/data/sentinel_data/sentinel1/sigma0_1/"

spark-submit --master yarn --name S1_SIGMA0_LOCAL \
            --conf spark.yarn.executor.memoryOverhead=4048 \
            --conf spark.yarn.submit.waitAppCompletion=false \
            --deploy-mode cluster --executor-memory=32G \
            --conf spark.shuffle.service.enabled=true \
            --conf spark.memory.fraction=0.01 \
            --conf spark.dynamicAllocation.enabled=true \
            --jars hdfs:///workflows-dev/snap/snap-all-6.0.2.jar \
            --packages com.beust:jcommander:1.72 \
            --files $GRAPH_FILE \
            --archives hdfs:///workflows-dev/snap/etc.zip#etc,hdfs:///workflows-dev/snap/auxdata.zip#auxdata \
            --class be.vito.terrascope.snapgpt.ProcessFilesGPT \
            --conf spark.executor.extraJavaOptions="-XX:MaxHeapFreeRatio=60 -Dsnap.userdir=. -Dsnap.dataio.bigtiff.tiling.height=256 -Dsnap.dataio.bigtiff.tiling.width=256 -Dsnap.jai.defaultTileSize=256 -Dsnap.jai.tileCacheSize=2048 -Dsnap.dataio.bigtiff.compression.type=LZW -Dsnap.parallelism=10" \
            hdfs:///workflows-dev/snap/snap-gpt-spark-1.0-SNAPSHOT.jar \
            -format BEAM-DIMAP \
            -gpt $GRAPH_FILE \
            -output-dir $OUTPUT_DIR \
            /data/mep_uturn/S1/GRD/S1A_IW_GRDH_1SDV_20180329T190050_20180329T190115_021234_024845_5423.zip
