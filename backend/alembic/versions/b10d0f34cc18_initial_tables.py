"""initial_tables

Revision ID: b10d0f34cc18
Revises:
Create Date: 2025-12-30 23:12:07.525426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b10d0f34cc18'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # projects
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # modules
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['modules.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # environments
    op.create_table(
        'environments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('base_url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # env_variables
    op.create_table(
        'env_variables',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('environment_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # test_cases
    op.create_table(
        'test_cases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('path', sa.String(length=500), nullable=False),
        sa.Column('headers', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('params', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('body_type', sa.String(length=20), nullable=True, server_default='none'),
        sa.Column('body_content', sa.Text(), nullable=True),
        sa.Column('pre_script', sa.Text(), nullable=True),
        sa.Column('post_script', sa.Text(), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=True, server_default='30'),
        sa.Column('retry_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # assertions
    op.create_table(
        'assertions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('test_case_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('type', sa.String(length=30), nullable=False),
        sa.Column('expression', sa.String(length=500), nullable=False),
        sa.Column('operator', sa.String(length=20), nullable=False),
        sa.Column('expected_value', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # extractors
    op.create_table(
        'extractors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('test_case_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('expression', sa.String(length=500), nullable=False),
        sa.Column('variable_name', sa.String(length=100), nullable=False),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # test_suites
    op.create_table(
        'test_suites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('execution_mode', sa.String(length=20), nullable=True, server_default='sequential'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # suite_cases
    op.create_table(
        'suite_cases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('suite_id', sa.Integer(), nullable=False),
        sa.Column('test_case_id', sa.Integer(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['suite_id'], ['test_suites.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # schedules
    op.create_table(
        'schedules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('suite_id', sa.Integer(), nullable=False),
        sa.Column('environment_id', sa.Integer(), nullable=False),
        sa.Column('cron_expression', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notify_on_failure', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notify_emails', sa.Text(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['suite_id'], ['test_suites.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['environment_id'], ['environments.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # test_executions
    op.create_table(
        'test_executions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('suite_id', sa.Integer(), nullable=True),
        sa.Column('test_case_id', sa.Integer(), nullable=True),
        sa.Column('environment_id', sa.Integer(), nullable=False),
        sa.Column('trigger_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('total_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('passed_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('skipped_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['suite_id'], ['test_suites.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['environment_id'], ['environments.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # execution_details
    op.create_table(
        'execution_details',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('execution_id', sa.Integer(), nullable=False),
        sa.Column('test_case_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('request_url', sa.Text(), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('request_headers', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('request_body', sa.Text(), nullable=True),
        sa.Column('response_status_code', sa.Integer(), nullable=True),
        sa.Column('response_headers', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('assertion_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('extractor_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['execution_id'], ['test_executions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('execution_details')
    op.drop_table('test_executions')
    op.drop_table('schedules')
    op.drop_table('suite_cases')
    op.drop_table('test_suites')
    op.drop_table('extractors')
    op.drop_table('assertions')
    op.drop_table('test_cases')
    op.drop_table('env_variables')
    op.drop_table('environments')
    op.drop_table('modules')
    op.drop_table('projects')
