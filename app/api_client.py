import requests


BASE_URL = "https://api.github.com"


def get_user_profile(username: str) -> dict:
    """
    Fetch basic user profile data from the GitHub REST API.

    Raises:
        ValueError: If the user is not found (404).
        RuntimeError: For other non-success HTTP responses.
    """
    url = f"{BASE_URL}/users/{username}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-profile-analyzer"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        raise ValueError(f"GitHub user '{username}' not found.")
    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API error for user '{username}': "
            f"status {response.status_code} - {response.text}"
        )

    return response.json()


def get_user_repos(username: str) -> list[dict]:
    """
    Fetch public repositories for a given GitHub user.

    Raises:
        ValueError: If the user is not found (404).
        RuntimeError: For other non-success HTTP responses.
    """
    url = f"{BASE_URL}/users/{username}/repos"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-profile-analyzer"
    }

    # You can adjust per_page if needed; 100 is the max
    params = {
        "per_page": 100,
        "sort": "updated"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 404:
        raise ValueError(f"GitHub user '{username}' not found when fetching repos.")
    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API error for repos of '{username}': "
            f"status {response.status_code} - {response.text}"
        )

    return response.json()


if __name__ == "__main__":
    # Simple manual test when running:
    # python app/api_client.py
    test_username = "torvalds"

    print(f"Testing GitHub API client with user '{test_username}'")

    profile = get_user_profile(test_username)
    print("User name:", profile.get("name"))
    print("Public repos:", profile.get("public_repos"))

    repos = get_user_repos(test_username)
    print("Number of repos fetched:", len(repos))
    if repos:
        print("First repo:", repos[0].get("name"))
