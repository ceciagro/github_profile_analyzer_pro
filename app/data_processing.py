from datetime import datetime
from typing import List, Dict

import pandas as pd


def build_repos_dataframe(repos_json: List[Dict]) -> pd.DataFrame:
    """
    Build a clean pandas DataFrame from the list of repositories
    returned by the GitHub API.
    """
    if not repos_json:
        return pd.DataFrame(
            columns=[
                "name",
                "full_name",
                "description",
                "language",
                "stargazers_count",
                "forks_count",
                "created_at",
                "pushed_at",
                "html_url",
            ]
        )

    df = pd.json_normalize(repos_json)

    # Keep only relevant columns and rename them to cleaner names
    columns_mapping = {
        "name": "name",
        "full_name": "full_name",
        "description": "description",
        "language": "language",
        "stargazers_count": "stars",
        "forks_count": "forks",
        "created_at": "created_at",
        "pushed_at": "pushed_at",
        "html_url": "html_url",
    }

    df = df[list(columns_mapping.keys())].rename(columns=columns_mapping)

    # Convert datetime columns
    for col in ["created_at", "pushed_at"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def get_language_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with the number of repos per main language.
    """
    if df.empty:
        return pd.DataFrame(columns=["language", "repo_count"])

    lang_counts = (
        df["language"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )
    lang_counts.columns = ["language", "repo_count"]
    return lang_counts


def get_top_repos_by_stars(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Return the top N repositories sorted by star count.
    """
    if df.empty:
        return df

    return df.sort_values(by="stars", ascending=False).head(n)


def get_top_recent_repos(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Return the top N most recently updated repositories (by pushed_at).
    """
    if df.empty:
        return df

    return df.sort_values(by="pushed_at", ascending=False).head(n)


def get_activity_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with repository count by creation year.
    """
    if df.empty:
        return pd.DataFrame(columns=["year", "repo_count"])

    df = df.copy()
    df["year"] = df["created_at"].dt.year

    activity = (
        df.groupby("year")
        .size()
        .reset_index(name="repo_count")
        .sort_values("year")
    )
    return activity


if __name__ == "__main__":
    # Small manual test, will be used together with api_client
    from api_client import get_user_repos

    test_username = "torvalds"
    print(f"Testing data processing for user '{test_username}'")

    repos_json = get_user_repos(test_username)
    df_repos = build_repos_dataframe(repos_json)

    print("DataFrame shape:", df_repos.shape)
    print("Columns:", df_repos.columns.tolist())

    lang_stats = get_language_stats(df_repos)
    print("\nLanguage stats:")
    print(lang_stats.head())

    top_stars = get_top_repos_by_stars(df_repos, n=3)
    print("\nTop 3 repos by stars:")
    print(top_stars[["name", "stars"]])

    activity = get_activity_by_year(df_repos)
    print("\nActivity by year:")
    print(activity.tail())
