import random
import sys
from datetime import datetime, timedelta


def generate_log_entry():
    """ Function to generate a fake log entry

    canwe make an example where these info can be re-sorted?
    The function returns a string in the format: timestamp,event_type,duration
    """
    timestamp = datetime(2022, 1, 1, 12, 0, 0) + timedelta(minutes=random.randint(0, 1440))
    event_type = f"event_type_{random.choice(['A', 'B', 'C'])}"
    duration = round(random.uniform(5.0, 30.0), 2)
    return f"{timestamp.isoformat()},{event_type},{duration}"


if __name__ == '__main__':
    n_rows = int(sys.argv[1])
    output_file = 'log_entries_large.txt'

    with open(output_file, 'w') as file:
        for _ in range(n_rows):
            file.write(generate_log_entry() + '\n')

    print(f"Generated log entries file: {output_file}")
