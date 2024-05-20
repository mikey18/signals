import uuid
from passlib.context import CryptContext

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_id():
    return str(uuid.uuid4()).replace("-", "")

def hash_password(password):
    return PWD_CONTEXT.hash(password)