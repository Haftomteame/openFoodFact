import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: { "Content-Type": "application/json" },
});

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
