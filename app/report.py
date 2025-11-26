from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

import os
import pandas as pd


def generate_pdf_report(
    username: str,
    user_profile: dict,
    df_repos: pd.DataFrame,
    lang_stats_df: pd.DataFrame,
    activity_df: pd.DataFrame,
    fig_lang,
    fig_activity,
    output_path: str = "github_profile_report.pdf",
):
    # ------------------------------------------------------------------
    # 1. Save figures as temporary images
    # ------------------------------------------------------------------
    fig_lang_path = "temp_language_plot.png"
    fig_activity_path = "temp_activity_plot.png"

    fig_lang.savefig(fig_lang_path, dpi=120, bbox_inches="tight")
    fig_activity.savefig(fig_activity_path, dpi=120, bbox_inches="tight")

    # ------------------------------------------------------------------
    # 2. Create PDF document
    # ------------------------------------------------------------------
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # ------------------------------------------------------------------
    # 3. Title
    # ------------------------------------------------------------------
    title = f"GitHub Profile Report – {username}"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))

    # ------------------------------------------------------------------
    # 4. Profile summary
    # ------------------------------------------------------------------
    story.append(Paragraph("<b>User summary</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))

    profile_data = [
        ["Name", user_profile.get("name", "-")],
        ["Username", user_profile.get("login", "-")],
        ["Bio", user_profile.get("bio", "-")],
        ["Location", user_profile.get("location", "-")],
        ["Public repos", str(user_profile.get("public_repos", "-"))],
        ["Followers", str(user_profile.get("followers", "-"))],
        ["Following", str(user_profile.get("following", "-"))],
        ["GitHub URL", user_profile.get("html_url", "-")],
    ]

    profile_table = Table(profile_data, colWidths=[120, 380])
    profile_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(profile_table)
    story.append(Spacer(1, 12))

    # ------------------------------------------------------------------
    # 5. Language statistics
    # ------------------------------------------------------------------
    story.append(Paragraph("<b>Language distribution</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))

    if not lang_stats_df.empty:
        lang_table = Table(
            [lang_stats_df.columns.tolist()] + lang_stats_df.values.tolist()
        )
        lang_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ]
            )
        )
        story.append(lang_table)
    else:
        story.append(Paragraph("No languages found.", styles["Normal"]))

    story.append(Spacer(1, 12))

    # Insert language plot
    story.append(Image(fig_lang_path, width=400, height=300))
    story.append(Spacer(1, 18))

    # ------------------------------------------------------------------
    # 6. Activity metrics
    # ------------------------------------------------------------------
    story.append(Paragraph("<b>Repository activity by year</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))

    if not activity_df.empty:
        activity_table = Table(
            [activity_df.columns.tolist()] + activity_df.values.tolist()
        )
        activity_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ]
            )
        )
        story.append(activity_table)
    else:
        story.append(Paragraph("No activity data found.", styles["Normal"]))

    story.append(Spacer(1, 12))

    # Insert activity plot
    story.append(Image(fig_activity_path, width=400, height=300))
    story.append(Spacer(1, 18))

    # ------------------------------------------------------------------
    # 7. Build PDF
    # ------------------------------------------------------------------
    doc.build(story)

    # ------------------------------------------------------------------
    # 8. Delete temp images
    # ------------------------------------------------------------------
    if os.path.exists(fig_lang_path):
        os.remove(fig_lang_path)
    if os.path.exists(fig_activity_path):
        os.remove(fig_activity_path)

    return output_path
