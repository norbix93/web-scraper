import os
import string
from http import HTTPStatus
import requests
from bs4 import BeautifulSoup


def fetch_nature_content(path):
    """
    Fetches content from the Nature website for a given path.
    """
    url = f"https://www.nature.com/nature{path}"
    headers = {'Accept-Language': 'en-US,en;q=0.5'}
    response = requests.get(url, headers=headers)

    if response.status_code == HTTPStatus.OK:
        return response
    else:
        print(f"Error: The URL returned status code {response.status_code}!")
        return None


def save_to_file(file_name, content, directory):
    """
    Saves the given content to a file in the specified directory.
    """
    file_path = os.path.join(directory, f"{file_name}.txt")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def find_articles_by_tag(soup, tag):
    """
    Finds articles in the given soup object that match the specified tag.
    """
    articles = soup.find_all("article")
    return [
        article for article in articles
        if any(span.text == tag for span in article.find_all("span", {"data-test": "article.type"}))
    ]


def fetch_article_content(path):
    """
    Fetches the title and teaser content of an article from the given path.
    """
    response = fetch_nature_content(path)
    if not response:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    title_tag = soup.find("title")
    teaser_tag = soup.find("p", {"class": "article__teaser"})

    if title_tag and teaser_tag:
        return {
            title_tag.text.strip(): teaser_tag.text.strip()
        }
    else:
        print(f"Warning: Missing content for article at {path}")
        return None


def format_title(title):
    """
    Formats the title to create a safe filename.
    """
    return (title.translate(str.maketrans('', '', string.punctuation))
            .rstrip()
            .replace(" ", "_"))


def read_user_input():
    """
    Reads the number of pages and article type from user input.
    """
    try:
        number_of_pages = int(input("Enter the number of pages to scrape: "))
        search_param = input("Enter the article type to filter (e.g., 'News'): ").strip()
        return search_param, number_of_pages
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None, 0


def create_directory(index):
    """
    Creates a directory for the specified page index.
    """
    directory_name = f"Page_{index}"
    os.makedirs(directory_name, exist_ok=True)
    return directory_name


def process_article(article, directory, search_param):
    """
    Processes an article by fetching its content and saving it to a file.
    """
    path = article.find("a", {"data-track-action": "view article"}).get("href")
    content = fetch_article_content(path)

    if content:
        title = list(content.keys())[0]
        body = list(content.values())[0]
        formatted_title = format_title(title)
        save_to_file(formatted_title, body, directory)


def main():
    """
    Main function to orchestrate the web scraping.
    """
    search_param, number_of_pages = read_user_input()
    if not search_param or number_of_pages <= 0:
        print("No valid input provided. Exiting.")
        return

    for page_index in range(1, number_of_pages + 1):
        response = fetch_nature_content(f"/articles?sort=PubDate&year=2020&page={page_index}")
        if not response:
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        articles = find_articles_by_tag(soup, search_param)

        directory = create_directory(page_index)
        for article in articles:
            process_article(article, directory, search_param)

    print("Saved all articles.")


if __name__ == "__main__":
    main()
