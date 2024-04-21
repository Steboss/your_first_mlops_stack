import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from structlog import get_logger


logger = get_logger()


class ParseLogEntry(beam.DoFn):
    def process(self, element):
        """ Parse the input logs
        This is a csv file in the format:
        timestamp,event_type,duration"""
        timestamp, event_type, duration = element.split(',')
        return [{'event_type': event_type, 'duration': float(duration)}]


class CalculateAverageDuration(beam.CombineFn):
    def create_accumulator(self):
        """ This function creates an accumulator
        that stores the total duration and the count of elements.
        In a nutshell, we'll have (sum of durations, count of elements)
        """
        return (0.0, 0)

    def add_input(self, accumulator, input):
        """ Called once per input element.
        E.g. if we have A, B, C keys, we'll process firstly A, then B, then C
        along with all their elements.
        Then, it updates the accumulator with the duration
        of the input elements."""
        total_duration, count = accumulator
        for duration in input:
            total_duration += duration
            count += 1
        return total_duration, count

    def merge_accumulators(self, accumulators):
        """ This function merges several accumulators into a single one.
        This is useful, as we have multiple accumulators, and they can be
        processed in parallel."""
        total_duration, count = zip(*accumulators)
        return sum(total_duration), sum(count)

    def extract_output(self, accumulator):
        """ This function adds an additional layer before returning the output.
        For example, we may want to treat NaN differently, so we can
        add a step here."""
        total_duration, count = accumulator
        return total_duration / count if count != 0 else 0


def run_pipeline(argv=None, save_main_session=True):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', dest='input', required=True)
    parser.add_argument('--output-file', dest='output', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    options = PipelineOptions(['--runner=DirectRunner'])

    with beam.Pipeline(options=options) as pipeline:
        results = (
            pipeline
            | 'ReadFromText' >> beam.io.ReadFromText(known_args.input)
            | 'ParseLogEntry' >> beam.ParDo(ParseLogEntry())
            # Create a dictionary: element_type, its duration, e.g. {A, 11.61}, {B, 29.02} {A, 5.0} {C, 30.0}
            | 'WithKeys' >> beam.Map(lambda element: (element['event_type'], element['duration']))
            # Group by keys, e.g.{A, [11.61, 5.0]}, {B, [29.02]}, {C, [30.0]}
            | 'GroupByKey' >> beam.GroupByKey()
            # Calculate the average duration for each key
            | 'CalculateAverageDuration' >> beam.CombinePerKey(CalculateAverageDuration())
            # The output from the above step is ('event_type', average_duration)
            | 'FormatOutput' >> beam.Map(lambda kv: f'Event Type: {kv[0]}, Average Duration: {kv[1]:.2f}')
            | 'WriteToText' >> beam.io.WriteToText(known_args.output)
        )


if __name__ == '__main__':
    run_pipeline()