from datetime import datetime
from enum import Enum


class Language(Enum):
    """
    Enum class used to represent the programming languages that are supported.
    """

    Java = "Java"  # 0
    Python = "Python"  # 1
    Ruby = "Ruby"  # 2
    Go = "Go"  # 3
    C = "C"  # 4
    CPP = "C++"  # 5
    Scala = "Scala"  # 6
    JavaScript = "JavaScript"  # 7
    CSharp = "C#"  # 8
    Readme = "Readme"  # The most useful of programming languages
    Other = "Other"  # 10, always keep this one last

    def as_string(self):
        return self.value


def get_lan_id(incoming_language: Language) -> int:
    """
    Function to get the position of the language in the Language enum.
    :param incoming_language: The language to get the position of.
    :return: The position of the language in the Language enum.
    """

    pos = 0
    other_pos = 0
    for lan in list(Language):
        if lan == incoming_language:
            return pos

        if lan.value == "Other":
            other_pos = pos
        pos += 1

    return other_pos  # This will give the 'other' language by default


def find_file_type(file_path: str) -> (bool, int):
    """
    Function to find the type of file based on the file extension.
    :param file_path: The path of the file.
    :return: A tuple containing a boolean value indicating if the file type was found and the language of the file.
    """

    if file_path[-4:] == ".cpp" or file_path[-4:] == ".hpp":
        return True, Language.CPP
    elif file_path[-2:] == ".c" or file_path[-2:] == ".h":
        return True, Language.C
    elif file_path[-5:] == ".java":
        return True, Language.Java
    elif file_path[-3:] == ".py":
        return True, Language.Python
    elif file_path[-6:] == ".scala":
        return True, Language.Scala
    elif file_path[-3:] == ".go":
        return True, Language.Go
    elif file_path[-3:] == ".js":
        return True, Language.JavaScript
    elif file_path[-3:] == ".cs":
        return True, Language.CSharp
    elif file_path[-3:] == ".rb":
        return True, Language.Ruby

    return False, -1


class RepoFile:
    """
    Class used to represent a file from a GitHub repository.
    This is used to store the following information:

    Attributes:
    path -> str: The path of the file in the repository.
    branch -> str: The branch of the repository where the file was found.
    raw_content -> str: The raw content of the file.
    last_commit_date -> datetime: The date of the last commit that modified the file.
    language -> Language: The language of the file (i.e. Java, C++, Python, etc).
    """

    def __init__(
        self,
        path: str,
        branch: str,
        raw_content: str,
        last_commit_date: datetime,
        language: Language,
    ):
        self.path = path
        self.branch = branch
        self.raw_content = raw_content
        self.last_commit_date = last_commit_date
        self.language = language


class ScrapedRepo:
    """
    Class used to represent a GitHub repository that was scraped.
    This is used to capture the following information:
    repository name, last commit date, path, size and files within it.
    """

    def __init__(self, name: str, last_commit_date: datetime, path: str, size: int):
        """
        Constructor for the ScrapedRepo class.
        :param name: The name of the repository.
        :param last_commit_date:  The date of the last commit that modified the repository.
        :param path: The path of the repository.
        :param size: The size of the repository in bytes.
        """
        self.name = name
        self.lastCommitDate = last_commit_date
        self.path = path
        self.copies = 1
        self.size = size
        self.files = {}

    def add_file(self, file: RepoFile, path: str) -> None:
        """
        Adds a file to the repository, which is stored in a dictionary.
        :param file: The file to be added.
        :param path: The path of the file, which is used as the key in the dictionary.
        :return: None
        """
        self.files[path] = file

    def num_files(self) -> int:
        return len(self.files)
