import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import CategoryFlow from "./pages/CategoryFlow";
import BarcodeFlow from "./pages/BarcodeFlow";
import MySubstitutions from "./pages/MySubstitutions";
import SubstituteResult from "./pages/SubstituteResult";

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) {
    return (
      <div className="container" style={{ padding: "4rem 0", textAlign: "center" }}>
        Chargement…
      </div>
    );
  }
  return user ? children : <Navigate to="/login" state={{ from: location.pathname }} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="categories" element={<CategoryFlow />} />
        <Route path="barcode" element={<BarcodeFlow />} />
        <Route path="result" element={<SubstituteResult />} />
        <Route
          path="substitutions"
          element={
            <PrivateRoute>
              <MySubstitutions />
            </PrivateRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
