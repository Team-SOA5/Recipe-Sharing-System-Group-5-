from extensions import db, bcrypt
from models.models import Role, UserEntity
from repositories.repositories import RoleRepository, UserRepository
from constants.constants import PredefinedRole
from exceptions.exceptions import AppException, ErrorCode
import logging

logger = logging.getLogger(__name__)


def init_application_data():
    """
    Initialize application data - equivalent to Java ApplicationInitConfig
    Creates default roles and admin user
    """
    logger.info("Initializing application.....")
    
    # Initialize roles if not exists
    if RoleRepository.count() == 0:
        user_role = Role(name=PredefinedRole.USER_ROLE, description="role user")
        admin_role = Role(name=PredefinedRole.ADMIN_ROLE, description="role admin")
        RoleRepository.save_all([user_role, admin_role])
        logger.info("Initiate role data")
    
    # Create admin user if not exists
    admin_email = "admin@gmail.com"
    if not UserRepository.find_by_email(admin_email):
        admin_role = RoleRepository.find_by_id(PredefinedRole.ADMIN_ROLE)
        if not admin_role:
            raise AppException(ErrorCode.ROLE_NOT_EXISTED)
        
        admin_user = UserEntity()
        admin_user.email = admin_email
        admin_user.password = bcrypt.generate_password_hash("admin12345").decode('utf-8')
        admin_user.role = [admin_role]
        
        UserRepository.save(admin_user)
        logger.warning(
            "admin user has been created with default email: admin@gmail.com, "
            "password: admin12345, please change it"
        )
