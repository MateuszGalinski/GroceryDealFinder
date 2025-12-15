import { type PropsWithChildren } from "react";
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children }: PropsWithChildren) {
  const accessToken = localStorage.getItem("accessToken");

  if (!accessToken) {
    return <Navigate to={"/sign-in"} />;
  }

  return children;
}
