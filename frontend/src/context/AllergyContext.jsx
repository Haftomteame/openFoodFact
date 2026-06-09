import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { authApi } from "../services/api";
import { useAuth } from "./AuthContext";

const STORAGE_KEY = "pur_beurre_allergens";
const FILTER_KEY = "pur_beurre_allergy_filter";

const AllergyContext = createContext(null);

export function AllergyProvider({ children }) {
  const { user } = useAuth();
  const [allergens, setAllergensState] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    } catch {
      return [];
    }
  });
  const [filterEnabled, setFilterEnabled] = useState(() => {
    return localStorage.getItem(FILTER_KEY) === "1";
  });

  useEffect(() => {
    if (user?.allergens) {
      setAllergensState(user.allergens);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user.allergens));
    }
  }, [user?.id, user?.allergens]);

  const setAllergens = useCallback(
    async (nextAllergens) => {
      setAllergensState(nextAllergens);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(nextAllergens));

      if (user) {
        try {
          const res = await authApi.updateAllergens(nextAllergens);
          setAllergensState(res.data.allergens || nextAllergens);
        } catch {
          /* conserve la sélection locale */
        }
      }
    },
    [user],
  );

  const toggleAllergen = useCallback(
    (key) => {
      const next = allergens.includes(key)
        ? allergens.filter((item) => item !== key)
        : [...allergens, key];
      setAllergens(next);
    },
    [allergens, setAllergens],
  );

  const setAllergyFilter = useCallback((enabled) => {
    setFilterEnabled(enabled);
    localStorage.setItem(FILTER_KEY, enabled ? "1" : "0");
  }, []);

  return (
    <AllergyContext.Provider
      value={{
        allergens,
        filterEnabled,
        setAllergens,
        toggleAllergen,
        setAllergyFilter,
        hasAllergens: allergens.length > 0,
      }}
    >
      {children}
    </AllergyContext.Provider>
  );
}

export function useAllergy() {
  return useContext(AllergyContext);
}
