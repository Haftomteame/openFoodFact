import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_URL || "/api";

if (import.meta.env.PROD && !import.meta.env.VITE_API_URL) {
  console.error(
    "VITE_API_URL manquant : le frontend appelle /api sur Vercel au lieu du backend Render.",
  );
}

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (response) => {
    const contentType = response.headers["content-type"] || "";
    if (!contentType.includes("application/json")) {
      return Promise.reject(
        new Error("Réponse non-JSON (backend non configuré ou URL API incorrecte)."),
      );
    }
    return response;
  },
  (error) => Promise.reject(error),
);

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  register: (data) => api.post("/auth/register/", data),
  login: (data) => api.post("/auth/login/", data),
  me: () => api.get("/auth/me/"),
};

export const foodApi = {
  getCategories: () => api.get("/categories/"),
  getCategoryProducts: (categoryTag, page = 1) =>
    api.get("/categories/products/", {
      params: { category_tag: categoryTag, page },
    }),
  searchProducts: (q, pageSize = 24) =>
    api.get("/search/", { params: { q, page_size: pageSize } }),
  getProductByBarcode: (barcode) => api.get(`/products/${barcode}/`),
  findSubstitute: (barcode, avoidAllergens = true) =>
    api.post("/substitute/", { barcode, avoid_allergens: avoidAllergens }),
  saveSubstitution: (originalBarcode, substituteBarcode, reason = "") =>
    api.post("/substitutions/save/", {
      original_barcode: originalBarcode,
      substitute_barcode: substituteBarcode,
      reason,
    }),
  getMySubstitutions: () => api.get("/substitutions/"),
  deleteSubstitution: (id) => api.delete(`/substitutions/${id}/`),
};

export default api;
