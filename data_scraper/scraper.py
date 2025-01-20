import argparse
import logging
import sqlite3
import time
from datetime import date
from math import floor

import requests
from bs4 import BeautifulSoup

from scraped_repo import *
from upload_db import save_to_hf

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]:  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

GITHUB_BASE_URL = "https://github.com/"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/"
GITHUB_RAW_CONNECTOR = "/refs/heads/"

"""
    Layout for github's navigation url's: 
    'https://github.com/{user}/{repository}/'     -> Optionally, it can have /tree/{branch} after it, but we can leave that out.
    
    For the navigation window if you click a folder:
    'https://github.com/{user}/{repository}/tree/{branch}/{route/to/folder}'
    
    For the 'view code' type page (but not raws):
    'https://github.com/{user}/{repository}/blob/{branch}/{route/to/file}'   (includes the .py / .cpp or whatever afterwards)
    
    For the raw content page - most useful for us to scrape just the content
    'https://raw.githubusercontent.com/{user}/{repository}/refs/heads/{branch}/{route/to/file}'
"""


def scrape_repository(repo_path: str):
    """
    This function scrapes the repository and all of its files and folders.
    If successful, it will save the scraped data to the database.
    Basic scraping logic, which was taken from the following source:
    https://brightdata.com/blog/how-tos/how-to-scrape-github-repositories-in-python
    Default test repo: 'https://github.com/luminati-io/luminati-proxy'
    :param repo_path: the path to the repository
    """
    full_url = GITHUB_BASE_URL + repo_path
    try:
        failed_searches = []

        page_data = requests.get(full_url)

        if not page_data.ok:
            add_failed_search(full_url)
            return page_data.status_code, failed_searches

        soup = BeautifulSoup(page_data.text, "html.parser")

        # This is used to get the name of the main branch
        git_branch_icon_html_element = soup.select(".octicon-git-branch")

        count = 0
        main_branch = None
        for branch_elem in git_branch_icon_html_element:
            count += 1
            parent = branch_elem.parent.find_next_sibling("div")
            if parent:
                main_branch_html_element2 = parent.find("span")
                if main_branch_html_element2:
                    main_branch = main_branch_html_element2.get_text().strip()
                    # print(main_branch, count)
                    break

        # relative_time_html_element = soup.select_one('relative-time')
        # print("soop", soup.find('div', attrs={'data-testid': 'latest-commit-details'}), soup.find('relative-time'))
        # tree_element = soup.select('script')
        # print("tree", type(tree_element[-2]), tree_element[-2].text)

        # folder_directories = soup.findAll('svg', attrs={'class': 'icon-directory'})
        file_directories = soup.findAll(
            "div", attrs={"class": "react-directory-truncate"}
        )

        for i in range(0, floor(len(file_directories) / 2)):
            # If the icon is icon-directory that means it is a folder system and we deal with it like a tree.
            if (
                file_directories[i * 2].parent.parent.previous_sibling["class"][0]
                == "icon-directory"
            ):
                repo_folder_name = file_directories[2 * i].text
                # We can just ignore the builds, git and all those standard files
                if (
                    repo_folder_name != ".builds"
                    and repo_folder_name != ".git"
                    and repo_folder_name != ".github"
                    and repo_folder_name != ".vscode"
                ):
                    scrape_repository_tree_navigation(
                        repo_path, main_branch, repo_folder_name
                    )
            else:
                # If the icon is not icon-directory, it is an individual file
                repo_file_name = file_directories[2 * i].text
                scrape_repository_file_handling(repo_path, main_branch, repo_file_name)

        # We probably don't want to save a readme do we, if not we just get rid of this following section entirey

        # readme_url = f'{raw_url}/{repo_path}/{main_branch}/README.md'
        # readme_page = requests.get(readme_url)
        # readme_soup = BeautifulSoup(readme_page.text, 'html.parser')
        #
        # readme = None
        # readme_date = None
        # # if there is a README.md file
        # if readme_page.status_code != 404:
        #     readme = readme_page.text
        #     scrape_repository_file_handling(repo_path, main_branch, "/README.md")
        #     # print("readme soup relative time:", readme_soup)
        #     # readme_date = datetime.strptime(readme_soup.select_one('relative-time')['datetime'], '%Y-%m-%dT%H:%M:%SZ')
        #
        # # repo_file = RepoFile("README", main_branch, readme, readme_date, Language.Readme)
        # # final_repo = ScrapedRepo(name, latest_commit, repo_path, 0)
        # # final_repo.add_file(repo_file, "README")

        logger.info(f"{repo_path} complete")
        return
        # return repo
    except Exception:
        add_failed_search(full_url)
        logger.warning(f"{repo_path} failed search")
        return


def add_failed_search(full_url: str) -> None:
    """
    This function adds the URL to the list of failed searches in the failed_scrape_attempts.txt file
    :param full_url: the URL that failed to be scraped
    :return: None
    """
    f = open("failed_scrape_attempts.txt", "w", encoding="utf8")
    f.write(f"{full_url}\n")
    f.close()
    return


"https://github.com/{user}/{repository}/tree/{branch}/{route/to/folder}"


def scrape_repository_tree_navigation(repo_path: str, branch_name: str, tree_path: str):
    """
    This function scrapes the repository's tree navigation and all of its files and folders.
    :param repo_path: the path to the repository
    :param branch_name: the name of its branch
    :param tree_path: the tree path
    """
    full_url = GITHUB_BASE_URL + repo_path + "/tree/" + branch_name + "/" + tree_path
    try:
        page_data = requests.get(full_url)

        if not page_data.ok:
            add_failed_search(full_url)
            return page_data.status_code

        # Scraper stuff
        soup = BeautifulSoup(page_data.text, "html.parser")
        file_directories = soup.findAll(
            "div", attrs={"class", "react-directory-filename-column"}
        )
        # print(len(file_directories))
        for i in range(0, floor(len(file_directories) / 2)):
            # print(file_directories[2 * i].text)
            # If the icon is icon-directory that means it is a folder system and we deal with it like a tree.
            if file_directories[i * 2].svg["class"][0] == "icon-directory":
                repo_folder_name = file_directories[2 * i].text
                scrape_repository_tree_navigation(
                    repo_path, branch_name, tree_path + "/" + repo_folder_name
                )
            else:
                # If the icon is not icon-directory, it is an individual file
                repo_file_name = file_directories[2 * i].text
                scrape_repository_file_handling(
                    repo_path, branch_name, tree_path + "/" + repo_file_name
                )

        return

    except Exception as e:
        print(f"exception caught: {e}")
        add_failed_search(full_url)
        return


def scrape_repository_file_handling(repo_path: str, branch_name: str, file_path: str):
    """
    This function scrapes the repository's file and saves it to the database (i.e. repository file handling)
    :param repo_path: the path to the repository
    :param branch_name: the name of its branch
    :param file_path: the file path
    """
    valid_file_type, file_type = find_file_type(file_path)

    if not valid_file_type:
        return

    full_url = (
        GITHUB_RAW_URL
        + repo_path
        + GITHUB_RAW_CONNECTOR
        + branch_name
        + "/"
        + file_path
    )
    page_data = requests.get(full_url)

    if not page_data.ok:
        add_failed_search(full_url)
        return page_data.status_code

    write_to_db(repo_path, branch_name, file_path, file_type, page_data.text)

    return


def save_page(path: str):
    """
    This function saves the page data to a text file.
    :param path: the path to the page
    """
    page_data = requests.get(path)

    print(page_data.status_code)
    if not page_data.ok:
        logger.error(f"Failed to get page data from {path}")
        return page_data.status_code

    soup = BeautifulSoup(page_data.text, "html.parser")

    f = open(
        "env/raw_page_data/page_data_konfig_generator_tree.txt", "w", encoding="utf8"
    )
    f.write(page_data.text)
    f.close()
    return


def write_to_db(
    repo_path: str, branch_name: str, file_path: str, language: Language, data: str
):
    sqlite_connection = sqlite3.connect(".\scraped_repos.db")

    cursor = sqlite_connection.cursor()

    lan_id = get_lan_id(language)
    today = date.today()

    # This is essentially what we are inputting
    # insert_into = (f"""INSERT INTO SCRAPED_PAGE (Repo_Name, Branch, Path, Date_Scraped, Language_ID, Data)
    #                VALUES ({repo_path}, '{branch_name}', '{file_path}', {today}, {lan_id}, "{data}");""")

    insert_into = (
        "INSERT INTO SCRAPED_PAGE (Repo_Name, Branch, Path, Date_Scraped, Language_ID, Data) "
        "VALUES (?, ?, ?, ?, ?, ?);"
    )

    inputs = (repo_path, branch_name, file_path, today, lan_id, data)

    cursor.execute(insert_into, inputs)
    sqlite_connection.commit()

    # Close the cursor
    cursor.close()


def setup_database(db_path: str) -> None:
    """
    This function sets up the database for the scraped repositories.
    :param db_path: the path to the database that will be set up
    :return: None
    """
    logger.info(f"Setting up database at {db_path}...")
    db_connection_path = ".\\" + db_path
    sqlite_connection = sqlite3.connect(db_connection_path)

    cursor = sqlite_connection.cursor()

    # check_if_page_exists = ("SELECT table_type FROM ")
    check_if_page_exists = (
        "SELECT * " "FROM sqlite_master " "WHERE tbl_name='PAGE_LANGUAGE';"
    )

    cursor.execute(check_if_page_exists)
    language_table = cursor.fetchall()

    if len(language_table) == 0:
        logger.info("Setting up db requirements")
        language_table = (
            "CREATE TABLE IF NOT EXISTS PAGE_LANGUAGE("
            "ID INTEGER PRIMARY KEY NOT NULL,"
            "Language       TEXT    NOT NULL"
            ");"
        )
        cursor.execute(language_table)

        for lang in list(Language):
            # Might be unnecessary, but it's useful for consistency, and it only happens once anyway
            lan_id = get_lan_id(lang)
            insert_into = (
                "INSERT INTO PAGE_LANGUAGE (ID, Language) "
                f"VALUES ({lan_id}, '{lang.value}')"
            )
            cursor.execute(insert_into)

        # Create the main table after setting up the languages table
        create_table = (
            "CREATE TABLE IF NOT EXISTS SCRAPED_PAGE("
            "ID INTEGER PRIMARY KEY     AUTOINCREMENT,"
            "Repo_Name      TEXT    NOT NULL,"
            "Branch         TEXT    NOT NULL,"
            "Path           TEXT    NOT NULL,"
            "Date_Scraped   DATE    NOT NULL,"
            "Language_ID    Integer NOT NULL,"
            "Data         LONGTEXT,"
            "FOREIGN KEY (Language_ID)  REFERENCES PAGE_LANGUAGE(ID)"  # I'm not really sure about this one, its just like an enum with python/c++ or whatever but will just store it like this for now
            ");"
        )

        cursor.execute(create_table)
        sqlite_connection.commit()
        logger.info("db setup complete")

    # Close the cursor
    cursor.close()


def scrape_top_repos(num_to_scrape: int, pos_to_begin=0):
    path = "https://anthonygarvan.github.io/thousandstars/"

    page_data = requests.get(path)

    if not page_data.ok:
        logger.error(f"Failed to get page data from {path}")
        return page_data.status_code

    soup = BeautifulSoup(page_data.text, "html.parser")

    file_directories = soup.find("table")
    fb2 = file_directories.find("tbody")
    child_list = list(fb2.children)
    # print(fb2.children)
    count = 1
    for child in child_list[pos_to_begin : pos_to_begin + num_to_scrape]:
        try:
            link = child.find("a")

            repo_split = link["href"].split("/")[-2:]
            repo_name = repo_split[0] + "/" + repo_split[1]
            scrape_repository(repo_name)
            print(f"finished {count} out of {num_to_scrape}")
            count += 1
        except Exception as e:
            print(e)
            count += 1
            continue


def start_scraping(
    hf_repository: str, dataset_path: str, hf_token: str, upload_flag: bool
) -> None:
    """
    This function starts the scraping process.
    :param hf_repository: the HuggingFace repo to upload the dataset to
    :param dataset_path: the path for the dataset to upload to HuggingFace
    :param hf_token: the HuggingFace API token
    :param upload_flag: toggle whether to upload the scraped data to HuggingFace
    :return: None
    """
    start_time = time.time()
    logger.info(f"Starting scrapping process with upload flag: {upload_flag}")

    # We always set up the database as a sanity-check.
    # There is a check where if the db is already up we just skip it anyway
    setup_database(db_path)

    # Just scraping the 10 top repositories on the 'trending' page of GitHub as of 22:57 30/10/2024 CEST
    # scrape_repository('EbookFoundation/free-programming-books')
    # The one above is apparently just html so let's ignore this one

    # Scrape the following repositories
    scrape_repository("WerWolv/ImHex")
    scrape_repository("DrewThomasson/ebook2audiobook")
    scrape_repository("kovidgoyal/kitty")
    scrape_repository("Stirling-Tools/Stirling-PDF")
    scrape_repository("imputnet/cobalt")
    scrape_repository("fish-shell/fish-shell")
    scrape_repository("pathwaycom/pathway")
    scrape_repository("public-apis/public-apis")
    scrape_repository("MervinPraison/PraisonAI")
    scrape_repository("ManimCommunity/manim")

    # scrape_top_repos(500, 4270)

    # Save the scraped data to the huggingface repo if enabled
    if upload_flag:
        save_to_hf(hf_repository, dataset_path, hf_token)

    end_time = time.time()
    logging.info(f"Scraping took: {end_time - start_time} seconds")
    logger.info("Scraping complete!)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape the top repositories on GitHub and save them to a database."
    )

    parser.add_argument(
        "--upload",
        "-u",
        action="store_true",
        required=False,
        help="Toggle whether to upload the scraped data to HuggingFace.",
    )

    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        required=False,
        default="bwmfvanveen/ml4se-team14-bigger-scraped-dataset",
        help="The HuggingFace repo to upload the dataset to.",
    )

    parser.add_argument(
        "--dataset",
        "-d",
        type=str,
        required=False,
        default="scraped_repos.db",
        help="The path for the dataset to upload to HuggingFace.",
    )

    parser.add_argument(
        "--token", "-t", type=str, required=False, help="The HuggingFace API token."
    )

    # Parse the arguments
    args = parser.parse_args()
    upload_flag = args.upload
    hf_repo = args.repo
    hf_api_token = args.token
    db_path = args.dataset

    # Input Validation
    if upload_flag and not hf_api_token:
        raise ValueError(
            "Please specify the HuggingFace API token to upload the dataset."
        )

    # Start scraping
    start_scraping(
        hf_repository=hf_repo,
        dataset_path=db_path,
        hf_token=hf_api_token,
        upload_flag=upload_flag,
    )
