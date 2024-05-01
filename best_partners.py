import requests
from collections import defaultdict


# Function to get the files changed in a specific commit
def get_commit_files(owner, repo, commit_sha):
    # Construct the URL for the GitHub API request
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
    response = requests.get(url)
    commit_data = response.json()
    # Return the 'files' field of the response, or an empty list if 'files' is not present
    return commit_data.get('files', [])


# Function to get the commit history of a repository
def get_commit_history(repo):
    owner, repo_name = repo.split('/')
    url = f"https://api.github.com/repos/{repo}/commits?per_page=50"
    # Loop until there are no more pages of commits
    while url:
        response = requests.get(url)
        commits = response.json()
        for commit in commits:
            # Get the SHA of the commit
            commit_sha = commit['sha']
            files = get_commit_files(owner, repo_name, commit_sha)
            yield commit, files
        # Get the URL for the next page of commits
        url = response.links.get("next", {}).get("url")


# Function to get pairs of contributors who have edited the same files
def get_contributor_pairs(commit_history):
    file_to_authors = defaultdict(set)
    for commit, files in commit_history:
        author = commit["commit"]["author"]["name"]
        for file in files:
            file_to_authors[file["filename"]].add(author)

    # Dictionary to count the number of files each pair of authors have in common
    contributor_pairs = defaultdict(int)
    for authors in file_to_authors.values():
        for author1 in authors:
            for author2 in authors:
                # Ensure author1 comes before author2 lexicographically
                if author1 < author2:
                    contributor_pairs[(author1, author2)] += 1

    return contributor_pairs


def main(repo):
    try:
        # Remove starting slashes from the repo string
        repo = repo.lstrip('/')

        # Get the commit history of the repository
        commit_history = list(get_commit_history(repo))
        # Get the pairs of contributors who have edited the same files
        contributor_pairs = get_contributor_pairs(commit_history)

        # Sort the pairs by count in descending order and take the top 5
        top_pairs = sorted(contributor_pairs.items(), key=lambda x: x[1], reverse=True)[:5]
        # Print the top 5 (or less) pairs
        print(f"The top {len(top_pairs)} pairs of developers who most frequently contribute to the same "
              f"files/modules in a GitHub repository are:")
        for pair, count in top_pairs:
            print(f"\033[94m{pair[0]}\033[0m and \033[94m{pair[1]}\033[0m have \033[94m{count}\033[0m files in common.")

    except Exception as e:
        print(f"An error occurred: {e}")


# If this script is run directly (not imported as a module), call the main function
if __name__ == "__main__":
    import sys

    # Call the main function with the first command-line argument as the repository identifier
    main(sys.argv[1])
