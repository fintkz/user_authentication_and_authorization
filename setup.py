import uuid
from sqlalchemy import create_engine, text, TypeDecorator, TEXT
from sqlalchemy.orm import sessionmaker

class UUID(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        elif dialect.name != 'postgresql':
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value

def create_tables():
    from app.models import Base
    from app.models.join_tables.all import metadata as join_tables_metadata
    from app.models import Role, Permission, EnumsPermissionName

    # Create a SQLite database
    engine = create_engine('sqlite:///test_data.db')
    
    # Replace UUID columns with the custom UUID type
    for table in Base.metadata.tables.values():
        for column in table.c:
            if isinstance(column.type, UUID):
                column.type = UUID()

    # Create all tables
    Base.metadata.create_all(engine)
    join_tables_metadata.create_all(engine)
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Enable foreign key support for SQLite
    session.execute(text("PRAGMA foreign_keys = ON"))

    # Create admin role if it doesn't exist
    admin_role = session.query(Role).filter_by(role_name="Admin").first()
    if not admin_role:
        admin_role = Role(
            id=uuid.uuid4(),
            role_name="Admin",
            description="Administrator role"
        )
        session.add(admin_role)

        # Create basic permissions
        permissions = [
            EnumsPermissionName(title="ShadowUser", description="Can Shadow a user as admin"),
            EnumsPermissionName(title="AdminSeeAllUsers", description="Can get all users as admin"),
        ]
        session.add_all(permissions)
        session.flush()  # This assigns IDs to the new objects

        # Create Permission objects and associate them with the admin role
        for perm in permissions:
            permission = Permission(
                id=uuid.uuid4(),
                permission_name=perm.title,
                description=perm.description
            )
            session.add(permission)
            admin_role.permissions.append(permission)

        session.commit()
        print("Admin role and permissions created successfully.")
    else:
        print("Admin role already exists.")

    session.close()

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully.")