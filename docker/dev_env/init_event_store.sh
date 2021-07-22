source event_store_set_up.sh

docker exec -it kafka kafka-topics.sh --create --zookeeper $ZOOKEPER_HOST_NAME:$ZOOKEPER_PORT --replication-factor $DATA_REPLICATION_FACTOR --partitions $N_PARTITIONS --config delete.retention.ms=$DATA_RETENTATION_TIME_IN_MS --config retention.ms=$LOG_RETENTATION_TIME_IN_MS --config retention.bytes=$LOG_MAX_MEM_IN_BYTES --config segment.ms=$SEGMENT_RETENTATION_TIME_IN_MS --config segment.bytes=$SEGMENT_MAX_MEM_IN_BYTES --topic catalog


docker exec -it kafka kafka-topics.sh --create --zookeeper $ZOOKEPER_HOST_NAME:$ZOOKEPER_PORT --replication-factor $DATA_REPLICATION_FACTOR --partitions $N_PARTITIONS --config delete.retention.ms=$DATA_RETENTATION_TIME_IN_MS --config retention.ms=$LOG_RETENTATION_TIME_IN_MS --config retention.bytes=$LOG_MAX_MEM_IN_BYTES --config segment.ms=$SEGMENT_RETENTATION_TIME_IN_MS --config segment.bytes=$SEGMENT_MAX_MEM_IN_BYTES --topic training


docker exec -it kafka kafka-topics.sh --create --zookeeper $ZOOKEPER_HOST_NAME:$ZOOKEPER_PORT --replication-factor $DATA_REPLICATION_FACTOR --partitions $N_PARTITIONS --config delete.retention.ms=$DATA_RETENTATION_TIME_IN_MS --config retention.ms=$LOG_RETENTATION_TIME_IN_MS --config retention.bytes=$LOG_MAX_MEM_IN_BYTES --config segment.ms=$SEGMENT_RETENTATION_TIME_IN_MS --config segment.bytes=$SEGMENT_MAX_MEM_IN_BYTES --topic evaluation


docker exec -it kafka kafka-topics.sh --create --zookeeper $ZOOKEPER_HOST_NAME:$ZOOKEPER_PORT --replication-factor $DATA_REPLICATION_FACTOR --partitions $N_PARTITIONS --config delete.retention.ms=$DATA_RETENTATION_TIME_IN_MS --config retention.ms=$LOG_RETENTATION_TIME_IN_MS --config retention.bytes=$LOG_MAX_MEM_IN_BYTES --config segment.ms=$SEGMENT_RETENTATION_TIME_IN_MS --config segment.bytes=$SEGMENT_MAX_MEM_IN_BYTES --topic storage


docker exec -it kafka kafka-topics.sh --create --zookeeper $ZOOKEPER_HOST_NAME:$ZOOKEPER_PORT --replication-factor $DATA_REPLICATION_FACTOR --partitions $N_PARTITIONS --config delete.retention.ms=$DATA_RETENTATION_TIME_IN_MS --config retention.ms=$LOG_RETENTATION_TIME_IN_MS --config retention.bytes=$LOG_MAX_MEM_IN_BYTES --config segment.ms=$SEGMENT_RETENTATION_TIME_IN_MS --config segment.bytes=$SEGMENT_MAX_MEM_IN_BYTES --topic session


docker exec -it kafka kafka-topics.sh --zookeeper $ZOOKEPER_HOST_NAME:$ZOOKEPER_PORT --describe