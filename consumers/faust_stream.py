"""Defines trends calculations for stations"""
import logging

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


# DONE: Define a Faust Stream that ingests data from the Kafka Connect stations topic and
#   places it into a new topic with only the necessary information.
input_topic_name = "org.chicago.stations"
output_topic_name = "org.chicago.cta.stations.table.v1"
app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")
topic = app.topic(input_topic_name, value_type=Station)
# DONE: Define the output Kafka Topic
out_topic = app.topic(output_topic_name, partitions=1)
# DONE: Define a Faust Table
table = app.Table(
   output_topic_name,
   default=TransformedStation,
   partitions=1,
   changelog_topic=out_topic,
)


#
#
# DONE: Using Faust, transform input `Station` records into `TransformedStation` records. Note that
# "line" is the color of the station. So if the `Station` record has the field `red` set to true,
# then you would set the `line` of the `TransformedStation` record to the string `"red"`
#
#
@app.agent(topic)
async def process(stream):
    async for event in stream:
        line = None
        
        if event.red is True:
            line = "red"
        elif event.blue is True:
            line = "blue"
        elif event.green is True:
            line = "green"


        table[event.station_id] = TransformedStation(
            station_id=event.station_id,
            station_name=event.station_name,
            order=event.order,
            line=line,
        )

if __name__ == "__main__":
    app.main()
