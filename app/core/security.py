import bcrypt


def hash_password(password: str) -> str:
    # 1. Превращаем строку пароля в байты (bcrypt работает только с байтами)
    password_bytes = password.encode("utf-8")

    # 2. Генерируем «соль» — случайную строку, которая добавляется к паролю
    salt = bcrypt.gensalt()

    # 3. Хешируем пароль + соль
    hashed = bcrypt.hashpw(password_bytes, salt)

    # 4. Превращаем байты обратно в строку (чтобы сохранить в БД)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 1. Пароль → байты
    password_bytes = plain_password.encode("utf-8")

    # 2. Хеш из БД → байты
    hashed_bytes = hashed_password.encode("utf-8")

    # 3. Сравниваем (bcrypt сам извлечёт соль из хеша и проверит)
    return bcrypt.checkpw(password_bytes, hashed_bytes)