import { useState } from "react";

export default function PreferencesBar({ productCount = 0, onSortByPreferences }) {
  const [enabled, setEnabled] = useState(false);

  const toggle = () => {
    const next = !enabled;
    setEnabled(next);
    onSortByPreferences?.(next);
  };

  return (
    <div className="preferences-bar">
      <div className="preferences-inner">
        <button
          type="button"
          className={`toggle-switch${enabled ? " on" : ""}`}
          onClick={toggle}
          aria-pressed={enabled}
        />
        <span>
          Classer les {productCount || "…"} produits ci-dessous suivant vos préférences
        </span>
      </div>
    </div>
  );
}
