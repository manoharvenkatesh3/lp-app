"""Initial schema for Super Agent core entities

Revision ID: 202402050001
Revises:
Create Date: 2024-02-05 00:01:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "202402050001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), unique=True),
        sa.Column("phone", sa.String(length=32)),
        sa.Column("headline", sa.String(length=255)),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="new"),
        sa.Column("source", sa.String(length=50)),
        sa.Column("ats_identifier", sa.String(length=128), unique=True),
        sa.Column("notes", sa.Text()),
        sa.Column("tags", postgresql.ARRAY(sa.String(length=64))),
    )

    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_url", sa.String(length=512)),
        sa.Column("parsed_text", sa.Text()),
        sa.Column("structured_data", sa.Text()),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "interviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scheduled_time", sa.DateTime(timezone=True)),
        sa.Column("platform", sa.String(length=50)),
        sa.Column("meeting_url", sa.String(length=512)),
        sa.Column("status", sa.String(length=50), server_default="pending", nullable=False),
        sa.Column("facilitator", sa.String(length=255)),
        sa.Column("agenda", sa.Text()),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "transcripts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("interview_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("speaker", sa.String(length=255)),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("start_time", sa.Float()),
        sa.Column("end_time", sa.Float()),
        sa.Column("confidence", sa.Float()),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "scorecards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("interview_id", postgresql.UUID(as_uuid=True)),
        sa.Column("reviewer", sa.String(length=255)),
        sa.Column("overall_score", sa.Numeric(5, 2)),
        sa.Column("decision", sa.String(length=50)),
        sa.Column("feedback", sa.Text()),
        sa.Column("rubric", sa.Text()),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True)),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor", sa.String(length=255)),
        sa.Column("details", sa.Text()),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("scorecards")
    op.drop_table("transcripts")
    op.drop_table("interviews")
    op.drop_table("resumes")
    op.drop_table("candidates")
