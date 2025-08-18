"""Add enhanced models for comprehensive ticketing system

Revision ID: add_enhanced_models
Revises: 
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'add_enhanced_models'
down_revision = 'add_is_admin_to_user'  # Link to the is_admin migration instead
depends_on = None

def upgrade():
    # Create ticket_category table
    op.create_table('ticket_category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(7), nullable=False, default='#3B82F6'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('sla_response_hours', sa.Integer(), nullable=True, default=24),
        sa.Column('sla_resolution_hours', sa.Integer(), nullable=True, default=72),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Add new fields to existing ticket table
    with op.batch_alter_table('ticket', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ticket_number', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False))
        batch_op.add_column(sa.Column('resolution_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('resolved_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('closed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('estimated_hours', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('actual_hours', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('sla_response_due', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('sla_resolution_due', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('sla_response_breached', sa.Boolean(), nullable=False, default=False))
        batch_op.add_column(sa.Column('sla_resolution_breached', sa.Boolean(), nullable=False, default=False))
        batch_op.add_column(sa.Column('first_response_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        
        # Add foreign key constraint
        batch_op.create_foreign_key('fk_ticket_category', 'ticket_category', ['category_id'], ['id'])
        
        # Add indexes
        batch_op.create_index('ix_ticket_ticket_number', ['ticket_number'], unique=True)
        batch_op.create_index('ix_ticket_is_deleted', ['is_deleted'])
        batch_op.create_index('ix_ticket_sla_response_due', ['sla_response_due'])
        batch_op.create_index('ix_ticket_sla_resolution_due', ['sla_resolution_due'])
        batch_op.create_index('ix_ticket_category_id', ['category_id'])
    
    # Add new fields to existing user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, default=True))
        batch_op.add_column(sa.Column('phone', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('department', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('job_title', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('timezone', sa.String(50), nullable=False, default='UTC'))
        batch_op.add_column(sa.Column('email_notifications', sa.Boolean(), nullable=False, default=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow))
        
        # Add indexes
        batch_op.create_index('ix_user_last_seen', ['last_seen'])
        batch_op.create_index('ix_user_created_at', ['created_at'])
    
    # Add new fields to existing client_ticket table
    with op.batch_alter_table('client_ticket', schema=None) as batch_op:
        batch_op.add_column(sa.Column('company', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('reference_number', sa.String(20), nullable=True))
        
        # Add indexes
        batch_op.create_index('ix_client_ticket_reference_number', ['reference_number'], unique=True)
        batch_op.create_index('ix_client_ticket_email', ['email'])
        batch_op.create_index('ix_client_ticket_created_at', ['created_at'])
    
    # Create ticket_comment table
    op.create_table('ticket_comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_internal', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id']),
        sa.ForeignKeyConstraint(['author_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for ticket_comment
    op.create_index('ix_ticket_comment_created_at', 'ticket_comment', ['created_at'])
    op.create_index('ix_ticket_comment_ticket_id', 'ticket_comment', ['ticket_id'])
    op.create_index('ix_ticket_comment_author_id', 'ticket_comment', ['author_id'])
    
    # Create ticket_attachment table
    op.create_table('ticket_attachment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id']),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for ticket_attachment
    op.create_index('ix_ticket_attachment_ticket_id', 'ticket_attachment', ['ticket_id'])
    
    # Create ticket_watcher table
    op.create_table('ticket_watcher',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticket_id', 'user_id')
    )
    
    # Create indexes for ticket_watcher
    op.create_index('ix_ticket_watcher_ticket_id', 'ticket_watcher', ['ticket_id'])
    op.create_index('ix_ticket_watcher_user_id', 'ticket_watcher', ['user_id'])
    
    # Create audit_log table
    op.create_table('audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ticket_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for audit_log
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])
    op.create_index('ix_audit_log_created_at', 'audit_log', ['created_at'])
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('ix_audit_log_ticket_id', 'audit_log', ['ticket_id'])
    
    # Update existing token_blacklist table indexes
    with op.batch_alter_table('token_blacklist', schema=None) as batch_op:
        batch_op.create_index('ix_token_blacklist_jti', ['jti'], unique=True)
        batch_op.create_index('ix_token_blacklist_created_at', ['created_at'])
    
    # Create default categories
    op.execute("""
        INSERT INTO ticket_category (name, description, color, sla_response_hours, sla_resolution_hours)
        VALUES 
        ('General Support', 'General support requests and questions', '#3B82F6', 4, 24),
        ('Technical Issue', 'Technical problems and bug reports', '#EF4444', 2, 8),
        ('Feature Request', 'New feature requests and enhancements', '#10B981', 24, 168),
        ('Account Issue', 'Account-related problems and access issues', '#F59E0B', 1, 4),
        ('Billing', 'Billing and payment related questions', '#8B5CF6', 8, 48)
    """)
    
    # Generate ticket numbers for existing tickets
    op.execute("""
        UPDATE ticket 
        SET ticket_number = 'TKT-' || strftime('%Y%m%d', created_at) || '-' || 
                           substr('000000' || id, -6, 6)
        WHERE ticket_number IS NULL
    """)
    
    # Generate reference numbers for existing client tickets
    op.execute("""
        UPDATE client_ticket 
        SET reference_number = 'CT' || substr('000000' || id, -6, 6)
        WHERE reference_number IS NULL
    """)

def downgrade():
    # Drop new tables
    op.drop_table('audit_log')
    op.drop_table('ticket_watcher')
    op.drop_table('ticket_attachment')
    op.drop_table('ticket_comment')
    op.drop_table('ticket_category')
    
    # Remove new columns from existing tables
    with op.batch_alter_table('ticket', schema=None) as batch_op:
        batch_op.drop_constraint('fk_ticket_category', type_='foreignkey')
        batch_op.drop_index('ix_ticket_ticket_number')
        batch_op.drop_index('ix_ticket_is_deleted')
        batch_op.drop_index('ix_ticket_sla_response_due')
        batch_op.drop_index('ix_ticket_sla_resolution_due')
        batch_op.drop_index('ix_ticket_category_id')
        batch_op.drop_column('category_id')
        batch_op.drop_column('first_response_at')
        batch_op.drop_column('sla_resolution_breached')
        batch_op.drop_column('sla_response_breached')
        batch_op.drop_column('sla_resolution_due')
        batch_op.drop_column('sla_response_due')
        batch_op.drop_column('actual_hours')
        batch_op.drop_column('estimated_hours')
        batch_op.drop_column('closed_at')
        batch_op.drop_column('resolved_at')
        batch_op.drop_column('resolution_notes')
        batch_op.drop_column('is_deleted')
        batch_op.drop_column('ticket_number')
    
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('ix_user_last_seen')
        batch_op.drop_index('ix_user_created_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('email_notifications')
        batch_op.drop_column('timezone')
        batch_op.drop_column('job_title')
        batch_op.drop_column('department')
        batch_op.drop_column('phone')
        batch_op.drop_column('is_active')
    
    with op.batch_alter_table('client_ticket', schema=None) as batch_op:
        batch_op.drop_index('ix_client_ticket_reference_number')
        batch_op.drop_index('ix_client_ticket_email')
        batch_op.drop_index('ix_client_ticket_created_at')
        batch_op.drop_column('reference_number')
        batch_op.drop_column('company')
    
    with op.batch_alter_table('token_blacklist', schema=None) as batch_op:
        batch_op.drop_index('ix_token_blacklist_jti')
        batch_op.drop_index('ix_token_blacklist_created_at')
