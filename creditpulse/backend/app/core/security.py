"""
security.py — JWT + hashing (Palier A.2)

À IMPLÉMENTER :
1. hash_password(password: str) -> str          (passlib CryptContext, bcrypt)
2. verify_password(plain, hashed) -> bool
3. create_access_token(data: dict) -> str         (jose.jwt.encode)
4. decode_access_token(token: str) -> dict
5. get_current_user(token: str = Depends(oauth2_scheme)) -> User
   -> Dependency FastAPI utilisée pour protéger les routes
"""
