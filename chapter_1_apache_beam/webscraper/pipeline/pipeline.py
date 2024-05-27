import argparse
import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp import gcsio
import requests
from bs4 import BeautifulSoup
from structlog import get_logger
from io import BytesIO
import matplotlib.pyplot as plt
from google.cloud import storage
from io import StringIO


logger = get_logger()


class ScrapeNews(beam.DoFn):
    def __init__(self, current_element):
        """ Constructor to receive the current element to process"""
        self.current_element = current_element

    def process(self, element):
        """ Transform to perform scraping"""
        def remove_duplicates_and_corresponding_elements(list1, list2):
            """ Remove duplicates from list1 and corresponding elements from list2"""
            # Find duplicates and their first occurrences
            seen = {}
            duplicates_indexes = set()
            for index, item in enumerate(list1):
                if item in seen:
                    duplicates_indexes.add(seen[item])
                    duplicates_indexes.add(index)
                else:
                    seen[item] = index  # Store the first occurrence of this item
            # If no duplicates, return lists as they are
            if not duplicates_indexes:
                return list1, list2
            # Remove duplicates from list1 using indexes to keep
            new_list1 = [item for idx, item in enumerate(list1) if idx not in duplicates_indexes]
            new_list2 = [item for idx, item in enumerate(list2) if idx not in duplicates_indexes]
            return new_list1, new_list2

        base_url = "https://news.google.com/search"
        query = f"{self.current_element}"
        params = {'q': query, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'}
        response = requests.get(base_url, params=params)

        newspaper_names = []
        newspaper_titles = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # newspaper titles
            newspaper_titles_div = soup.find_all('div', class_='vr1PYe')
            for news_title in newspaper_titles_div:
                newspaper_names.append(news_title.text)

            # title
            buttons = soup.find_all('button', {'aria-label': True})
            for button in buttons:
                if 'aria-label' in button.attrs:
                    # remove "More -" from the title
                    title = button.attrs['aria-label'].replace("More - ", "")
                    newspaper_titles.append(title)

        # remove the first 6 elements from titles
        newspaper_titles = newspaper_titles[6:]
        # as well as the last 2 elements
        newspaper_titles = newspaper_titles[:-2]

        news_titles, news_names = remove_duplicates_and_corresponding_elements(newspaper_titles, newspaper_names)
        # NB how we're returning the elemnts
        yield news_titles, news_names


class WordCloud(beam.DoFn):
    def __init__(self, output_path, filename):
        """ We need a constructor to set the output path"""
        self.output_path = output_path
        self.filename = filename

    def process(self, element):
        """ Generate a word cloud from the titles"""
        text = ' '.join(element)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        # Prepare to save the image to GCS
        output = BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig(output, format='png')
        plt.close()
        # Reset stream position
        output.seek(0)
        # Write to Google Cloud Storage
        gcs_path = f"{self.output_path}/{self.filename}.png"
        gcs = gcsio.GcsIO()
        gcs.write(gcs_path, output.getvalue())

        yield f"Word cloud saved to {gcs_path}"


def run_pipeline(argv=None):
    parser = argparse.ArgumentParser()
    # this must be changed with an input file
    parser.add_argument('--input-file', dest='input_file',
                        help="File with a list of words to look for",
                        required=True)
    parser.add_argument('--output-bucket', dest='output_bucket',
                        help="Output bucket to save wordcloud", required=True)
    parser.add_argument('--job_name', dest='job_name', required=True)
    parser.add_argument('--project', dest='project', required=True)
    parser.add_argument('--region', dest='region', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(
        pipeline_args,
        streaming=False,
        save_main_session=True,
        job_name=known_args.job_name,
        project=known_args.project,
        region=known_args.region
    )


    # create a pipeline object
    pipeline = beam.Pipeline(options=pipeline_options)
    # read the input file
    storage_client = storage.Client()
    bucket = known_args.input_file.split("/")[2]
    file_name = known_args.input_file.split("/")[-1]
    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(file_name)
    blob = blob.download_as_string()
    blob = blob.decode('utf-8')
    blob = StringIO(blob)
    input_elements = blob.readlines()

    for input_element in input_elements:
        current_line = input_element.strip()
        (pipeline | f'Scrape {current_line}' >> beam.ParDo(ScrapeNews(current_element=current_line))
         | f'Save {current_line} on GCS' >> beam.ParDo(WordCloud(output_path=known_args.output_bucket, filename=current_line)))


if __name__ == '__main__':
    run_pipeline()
