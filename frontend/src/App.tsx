import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";

import { BrowserRouter, Routes, Route } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import SignIn from "./pages/SignIn";
import Register from "./pages/Register";
import MainPage from "./pages/MainPage";
import NotFound from "./pages/NotFound";
import UserProfile from "./pages/UserProfile";
import Shopping from "./pages/Shopping";

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/sign-in" element={<SignIn />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainPage />
              </ProtectedRoute>
            }
          >
            <Route
              index
              element={
                <ProtectedRoute>
                  <Shopping />
                </ProtectedRoute>
              }
            />
            <Route
              path="profile"
              element={
                <ProtectedRoute>
                  <UserProfile />
                </ProtectedRoute>
              }
            />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
