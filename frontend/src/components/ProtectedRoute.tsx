import { type PropsWithChildren } from "react";
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children }: PropsWithChildren) {
  // const accessToken = localStorage.getItem("accessToken");

  // if (!accessToken) {
  //   return <Navigate to={"/sign-in"} />;
  // }
  const username = localStorage.getItem("username");
  const password = localStorage.getItem("password");

  if (!username || !password) {
    return <Navigate to={"sign-in"} />;
  }

  return children;
}
