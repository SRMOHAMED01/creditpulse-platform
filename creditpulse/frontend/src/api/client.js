/*
client.js — Instance Axios centralisée (Palier A.3)
À IMPLÉMENTER :
1. axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL })
2. Interceptor de requête : ajoute "Authorization: Bearer <token>"
   (token lu depuis localStorage) sur chaque appel
3. Interceptor de réponse : si 401, redirige vers /login
*/
