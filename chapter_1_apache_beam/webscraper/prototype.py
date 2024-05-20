import requests
from bs4 import BeautifulSoup

from wordcloud import WordCloud
import matplotlib.pyplot as plt


def create_word_cloud(titles_list):
    # Combine the list into a single string
    text = ' '.join(titles_list)

    # Generate the word cloud image
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Display the generated image using matplotlib:
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")  # Turn off axis numbers and ticks
    plt.show()


def remove_duplicates_and_corresponding_elements(list1, list2):
    # Find duplicates and their first occurrences
    seen = {}
    duplicates_indexes = set()
    for index, item in enumerate(list1):
        if item in seen:
            duplicates_indexes.add(seen[item])  # Add the first occurrence of the duplicate
            duplicates_indexes.add(index)       # Add the current index
        else:
            seen[item] = index  # Store the first occurrence of this item

    # If no duplicates, return lists as they are
    if not duplicates_indexes:
        return list1, list2

    # Remove duplicates from list1 using indexes to keep
    new_list1 = [item for idx, item in enumerate(list1) if idx not in duplicates_indexes]

    # Remove corresponding elements from list2 using the same indexes
    new_list2 = [item for idx, item in enumerate(list2) if idx not in duplicates_indexes]

    return new_list1, new_list2


element = "openai"
base_url = "https://news.google.com/search"
query = f"{element}"
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

print(len(newspaper_titles))
print(len(newspaper_names))

news_titles, news_names = remove_duplicates_and_corresponding_elements(newspaper_titles, newspaper_names)
print(len(news_titles))
print(len(news_names))
print(news_titles)

create_word_cloud(news_titles)
