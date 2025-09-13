"""
Database initialization commands.
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from app import db
from app.models.seeds import seed_rbac_data, assign_user_role
from app.models.user import User

@click.command()
@with_appcontext
def init_db():
    """Initialize the database with tables."""
    db.create_all()
    click.echo('Database tables created.')

@click.command()
@with_appcontext
def seed_db():
    """Seed the database with initial data."""
    try:
        result = seed_rbac_data()
        click.echo(f'Database seeded successfully!')
        click.echo(f'Created {result["permissions"]} permissions and {result["roles"]} roles.')
    except Exception as e:
        click.echo(f'Error seeding database: {str(e)}', err=True)

@click.command()
@with_appcontext
def create_admin():
    """Create an admin user."""
    username = click.prompt('Username')
    email = click.prompt('Email')
    password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
    first_name = click.prompt('First Name')
    last_name = click.prompt('Last Name')
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        click.echo(f'User {username} already exists!', err=True)
        return
    
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        click.echo(f'Email {email} already in use!', err=True)
        return
    
    try:
        # Create user
        user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='admin'
        )
        user.is_verified = True
        
        db.session.add(user)
        db.session.commit()
        
        # Assign admin role
        assign_user_role(user, 'admin')
        
        click.echo(f'Admin user {username} created successfully!')
        
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error creating admin user: {str(e)}', err=True)

@click.command()
@click.argument('username')
@click.argument('role')
@with_appcontext
def assign_role(username, role):
    """Assign a role to a user."""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f'User {username} not found!', err=True)
        return
    
    if assign_user_role(user, role):
        click.echo(f'Role {role} assigned to user {username}.')
    else:
        click.echo(f'Role {role} not found!', err=True)

@click.command()
@with_appcontext
def list_users():
    """List all users with their roles."""
    users = User.query.all()
    if not users:
        click.echo('No users found.')
        return
    
    click.echo('Users:')
    click.echo('-' * 60)
    for user in users:
        role_name = user.role_obj.name if user.role_obj else user.role
        role_display = user.display_role
        status = 'Active' if user.is_active else 'Inactive'
        if user.is_locked:
            status = 'Locked'
        
        click.echo(f'{user.username:<20} {user.email:<30} {role_display:<15} {status}')

@click.command()
@with_appcontext
def reset_db():
    """Reset the database (drop and recreate all tables)."""
    if click.confirm('This will delete all data. Are you sure?'):
        db.drop_all()
        db.create_all()
        click.echo('Database reset completed.')
    else:
        click.echo('Operation cancelled.')

def init_app(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(init_db)
    app.cli.add_command(seed_db)
    app.cli.add_command(create_admin)
    app.cli.add_command(assign_role)
    app.cli.add_command(list_users)
    app.cli.add_command(reset_db)
