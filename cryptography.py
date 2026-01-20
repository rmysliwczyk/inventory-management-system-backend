from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_hashed_password(plain_password: str, hashed_password: str | None) -> bool:
    if hashed_password == None:
        return False
    return password_hasher.verify(plain_password, hashed_password)
