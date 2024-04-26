import argparse
import logging
import re

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions


class WordExtractingDoFn(beam.DoFn):
    """Parse each line of input text into words."""
    def process(self, element):
        """Returns an iterator over the words of this element.

        The element is a line of text.  If the line is blank, note that, too.

        Args:
          element: the element being processed

        Returns:
          The processed element.
        """
        return re.findall(r'[\w\']+', element, re.UNICODE)


def run(argv=None, save_main_session=True):
    """Main entry point; defines and runs the wordcount pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        default='gs://dataflow-samples/shakespeare/kinglear.txt',
        help='Input file to process.',
        required=True)
    parser.add_argument(
        '--output-file',
        dest='output',
        help='Output file to write results to.',
        required=True)
    parser.add_argument(
        '--job_name',
        dest='job_name',
        help='Name of the job in Dataflow.',
        required=True)
    parser.add_argument(
        '--project',
        dest='project',
        help='The name of your GCP project.',
        required=True)
    parser.add_argument(
        '--region',
        dest='region',
        help='The region the job should run in.',
        required=True)
    parser.add_argument(
        '--temp_location',
        dest='temp_location',
        help='A location in GCS to store temporary files.',
        required=True)
    parser.add_argument(
        '--staging_location.',
        dest='staging_location',
        help='A location in GCS to store temporary files.',
        required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(
        pipeline_args,
        streaming=False,
        save_main_session=save_main_session,
        job_name=known_args.job_name,
        project=known_args.project,
        region=known_args.region,
        temp_location=known_args.temp_location,
        staging_location=known_args.staging_location)

    with beam.Pipeline(options=pipeline_options) as p:

        lines = p | 'Read' >> ReadFromText(known_args.input)

        counts = (
            lines
            | 'Split' >> (beam.ParDo(WordExtractingDoFn()).with_output_types(str))
            | 'PairWithOne' >> beam.Map(lambda x: (x, 1))
            | 'GroupAndSum' >> beam.CombinePerKey(sum))

        def format_result(word, count):
            return '%s: %d' % (word, count)

        output = counts | 'Format' >> beam.MapTuple(format_result)
        output | 'Write' >> WriteToText(known_args.output)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
