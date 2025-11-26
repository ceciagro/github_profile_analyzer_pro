import streamlit as st

from api_client import get_user_profile, get_user_repos
from data_processing import (
    build_repos_dataframe,
    get_language_stats,
    get_top_repos_by_stars,
    get_top_recent_repos,
    get_activity_by_year,
)
from plots import plot_language_distribution, plot_repos_by_year
from report import generate_pdf_report


st.set_page_config(
    page_title="GitHub Profile Analyzer – PRO",
    page_icon="📊",
    layout="wide",
)

st.title("GitHub Profile Analyzer – PRO")
st.write(
    "Analyze any public GitHub profile and generate a data-driven overview for "
    "recruiters, team leads, and developers."
)

with st.sidebar:
    st.header("Settings")
    username = st.text_input("GitHub username", value="torvalds")
    analyze_button = st.button("Analyze profile")

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
if analyze_button and not username.strip():
    st.error("Please enter a valid GitHub username.")

# -----------------------------------------------------------------------------
# Main analysis
# -----------------------------------------------------------------------------
if analyze_button and username.strip():
    username = username.strip()

    try:
        user_profile = get_user_profile(username)
        repos_json = get_user_repos(username)
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Unexpected error while calling GitHub API: {e}")
    else:
        df_repos = build_repos_dataframe(repos_json)

        # ---------------------------------------------------------------------
        # Section 1 – User overview
        # ---------------------------------------------------------------------
        st.subheader("User overview")

        col_avatar, col_info = st.columns([1, 3])

        with col_avatar:
            avatar_url = user_profile.get("avatar_url")
            if avatar_url:
                st.image(avatar_url, width=140)

        with col_info:
            st.markdown(f"**Name:** {user_profile.get('name') or '-'}")
            st.markdown(f"**Username:** {user_profile.get('login') or '-'}")
            st.markdown(f"**Bio:** {user_profile.get('bio') or '-'}")
            st.markdown(f"**Location:** {user_profile.get('location') or '-'}")

            st.markdown(
                f"**Public repos:** {user_profile.get('public_repos', 0)}  |  "
                f"**Followers:** {user_profile.get('followers', 0)}  |  "
                f"**Following:** {user_profile.get('following', 0)}"
            )

            created_at = user_profile.get("created_at")
            if created_at:
                created_str = created_at.split("T")[0]
                st.markdown(f"**Account created:** {created_str}")

            profile_url = user_profile.get("html_url")
            if profile_url:
                st.markdown(f"[Open profile on GitHub]({profile_url})")

        st.markdown("---")

        # ---------------------------------------------------------------------
        # Section 2 – Repositories overview
        # ---------------------------------------------------------------------
        st.subheader("Repositories overview")

        if df_repos.empty:
            st.info("This user has no public repositories.")
        else:
            st.markdown("**Repository table (sorted by stars)**")
            st.dataframe(
                df_repos[
                    ["name", "language", "stars", "forks", "created_at", "pushed_at"]
                ].sort_values("stars", ascending=False),
                use_container_width=True,
            )

            col_top_stars, col_recent = st.columns(2)

            with col_top_stars:
                st.markdown("**Top repositories by stars**")
                top_stars_df = get_top_repos_by_stars(df_repos, n=5)
                st.table(
                    top_stars_df[["name", "language", "stars", "forks", "html_url"]]
                )

            with col_recent:
                st.markdown("**Recently updated repositories**")
                top_recent_df = get_top_recent_repos(df_repos, n=5)
                st.table(
                    top_recent_df[["name", "language", "pushed_at", "html_url"]]
                )

        st.markdown("---")

        # ---------------------------------------------------------------------
        # Section 3 – Language analysis
        # ---------------------------------------------------------------------
        st.subheader("Language analysis")

        lang_stats_df = get_language_stats(df_repos)

        col_lang_table, col_lang_plot = st.columns([1, 2])

        with col_lang_table:
            st.markdown("**Repositories per language**")
            st.table(lang_stats_df)

        with col_lang_plot:
            fig_lang = plot_language_distribution(lang_stats_df)
            st.pyplot(fig_lang, use_container_width=True)

        st.markdown("---")

        # ---------------------------------------------------------------------
        # Section 4 – Activity metrics
        # ---------------------------------------------------------------------
        st.subheader("Activity metrics")

        activity_df = get_activity_by_year(df_repos)

        col_activity_table, col_activity_plot = st.columns([1, 2])

        with col_activity_table:
            st.markdown("**Repositories created per year**")
            st.table(activity_df)

        with col_activity_plot:
            fig_activity = plot_repos_by_year(activity_df)
            st.pyplot(fig_activity, use_container_width=True)

        st.markdown("---")

        # ---------------------------------------------------------------------
        # Section 5 – PDF report
        # ---------------------------------------------------------------------
        st.subheader("PDF report")

        if st.button("Generate PDF report"):
            with st.spinner("Generating PDF..."):
                pdf_path = generate_pdf_report(
                    username=username,
                    user_profile=user_profile,
                    df_repos=df_repos,
                    lang_stats_df=lang_stats_df,
                    activity_df=activity_df,
                    fig_lang=fig_lang,
                    fig_activity=fig_activity,
                    output_path=f"github_profile_report_{username}.pdf",
                )

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download PDF report",
                    data=f,
                    file_name=f"github_profile_report_{username}.pdf",
                    mime="application/pdf",
                )
