from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


def plot_language_distribution(lang_stats: pd.DataFrame):
    """
    Create a bar chart with the number of repositories per language.
    Returns a matplotlib Figure.
    """
    fig, ax = plt.subplots()

    if lang_stats.empty:
        ax.text(0.5, 0.5, "No repositories found", ha="center", va="center")
        ax.axis("off")
        return fig

    ax.bar(lang_stats["language"], lang_stats["repo_count"])
    ax.set_xlabel("Language")
    ax.set_ylabel("Number of repositories")
    ax.set_title("Repositories per language")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    return fig


def plot_repos_by_year(activity_df: pd.DataFrame):
    """
    Create a simple line chart with repositories created per year.
    Returns a matplotlib Figure.
    """
    fig, ax = plt.subplots()

    if activity_df.empty:
        ax.text(0.5, 0.5, "No repositories found", ha="center", va="center")
        ax.axis("off")
        return fig

    ax.plot(activity_df["year"], activity_df["repo_count"], marker="o")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of repositories created")
    ax.set_title("Repositories created per year")
    fig.tight_layout()

    return fig


if __name__ == "__main__":
    # Quick manual test: generate and save charts for 'torvalds'
    from api_client import get_user_repos
    from data_processing import (
        build_repos_dataframe,
        get_language_stats,
        get_activity_by_year,
    )

    test_username = "torvalds"
    print(f"Generating plots for user '{test_username}'")

    repos_json = get_user_repos(test_username)
    df_repos = build_repos_dataframe(repos_json)

    lang_stats = get_language_stats(df_repos)
    activity = get_activity_by_year(df_repos)

    fig_lang = plot_language_distribution(lang_stats)
    fig_activity = plot_repos_by_year(activity)

    fig_lang.savefig("language_distribution.png")
    fig_activity.savefig("repos_by_year.png")
    print("Plots saved as 'language_distribution.png' and 'repos_by_year.png'")
