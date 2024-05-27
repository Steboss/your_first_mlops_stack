import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from structlog import get_logger
from datetime import datetime
import json

logger = get_logger()


# Anomaly Detection Process (for 30s window)
class DetectAnomalies(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        user_id, events = element
        # Collect unique IP addresses from the events
        unique_ips = set(event['source_ip'] for event in events)

        # Count the number of unique IP addresses
        unique_ip_count = len(unique_ips)

        # Convert window start and end to timestamps or strings for serialization
        window_start = window.start.to_utc_datetime().isoformat()
        window_end = window.end.to_utc_datetime().isoformat()

        # You can still include your anomaly detection logic here if needed
        failure_count = sum(1 for event in events if event['event_type'] == 'fail')
        if failure_count > 5:  # Example threshold for anomaly
            anomaly_detected = True
        else:
            anomaly_detected = False

        # Yield a dictionary with the counts and window information
        yield user_id, {
            'window_start': window_start,
            'window_end': window_end,
            'unique_ip_count': unique_ip_count,
            'anomaly_detected': anomaly_detected,
            'failures': failure_count
        }


# Moving Average Calculation (for 60s sliding window)
class CalculateMovingAverage(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        user_id, events = element
        total_successes = sum(1 for event in events if event['event_type'] == 'success')
        average = total_successes / len(events) if events else 0
        # Convert window start and end to timestamps or strings for serialization
        window_start = window.start.to_utc_datetime().isoformat()
        window_end = window.end.to_utc_datetime().isoformat()
        yield user_id, {'window_start': window_start, 'window_end': window_end, 'moving_average': average}


# Total Sum Aggregation (for 180s sliding window)
class CalculateTotalSum(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        user_id, events = element
        success_count = sum(1 for event in events if event['event_type'] == 'success')
        failure_count = sum(1 for event in events if event['event_type'] == 'fail')
        # Convert window start and end to timestamps or strings for serialization
        window_start = window.start.to_utc_datetime().isoformat()
        window_end = window.end.to_utc_datetime().isoformat()
        yield user_id, {'window_start': window_start, 'window_end': window_end, 'success': success_count, 'fail': failure_count}


def run_pipeline(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-subscription', dest='input_subscription', required=True)
    parser.add_argument('--output-topic', dest='output_topic', required=True)
    parser.add_argument('--job_name', dest='job_name', required=True)
    parser.add_argument('--project', dest='project', required=True)
    parser.add_argument('--region', dest='region', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(
        pipeline_args,
        streaming=True,
        save_main_session=True,
        job_name=known_args.job_name,
        project=known_args.project,
        region=known_args.region
    )

    with beam.Pipeline(options=pipeline_options) as p:
        parsed_events = (
            p
            | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(subscription=known_args.input_subscription)
            | 'Parse JSON' >> beam.Map(lambda x: json.loads(x))
            | 'Extract Timestamp' >> beam.Map(lambda x: beam.window.TimestampedValue(x, datetime.strptime(x['timestamp'], "%Y%m%d%H%M%S").timestamp()))
        )

        # Short-term window (e.g., 30s fixed)
        short_term_window = (
            parsed_events
            | '30s Fixed Window' >> beam.WindowInto(beam.window.FixedWindows(30))
            | 'Key By User ID for Anomalies' >> beam.Map(lambda x: (x['user_id'], x))
            | 'Group By User ID for Sum' >> beam.GroupByKey()
            | 'Calculate Total Sum' >> beam.ParDo(CalculateTotalSum())
        )

        # Medium-term sliding window overlapping with short-term (e.g., 60s sliding, every 30s)
        medium_term_window = (
            parsed_events
            | '60s Sliding Window Every 30s' >> beam.WindowInto(beam.window.SlidingWindows(60, 30))
            | 'Key By User ID for Moving Averages' >> beam.Map(lambda x: (x['user_id'], x))
            | 'Group By User ID for Moving Averages' >> beam.GroupByKey()
            | 'Calculate Moving Average' >> beam.ParDo(CalculateMovingAverage())
        )

        # Long-term sliding window overlapping with both (e.g., 180s sliding, every 60s)
        long_term_window = (
            parsed_events
            | '180s Sliding Window Every 60s' >> beam.WindowInto(beam.window.SlidingWindows(180, 60))
            | 'Key By User ID for Total Sums' >> beam.Map(lambda x: (x['user_id'], x))
            | 'Group By User ID for Anomalies' >> beam.GroupByKey()
            | 'Detect Anomalies' >> beam.ParDo(DetectAnomalies())
        )

        ((short_term_window, medium_term_window, long_term_window)
            | 'Flatten Results' >> beam.Flatten()
            | 'Format for Output' >> beam.Map(lambda x: json.dumps(x).encode('utf-8'))
            | 'Write to PubSub' >> beam.io.WriteToPubSub(topic=known_args.output_topic)
        )

        result = p.run()
        result.wait_until_finish()


if __name__ == '__main__':
    run_pipeline()
