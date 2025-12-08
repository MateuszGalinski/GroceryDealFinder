import {
  Box,
  BottomNavigation,
  BottomNavigationAction,
  Paper,
} from "@mui/material";
import { ShoppingCart, Person } from "@mui/icons-material";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

export default function MainPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (location.pathname === "/") {
      setValue(0);
    } else if (location.pathname.includes("/profile")) {
      setValue(1);
    }
  }, [location]);

  const handleNavigation = (_event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
    if (newValue === 0) {
      navigate("/");
    } else if (newValue === 1) {
      navigate("/profile");
    }
  };

  return (
    <Box sx={{ pb: 7, mx: { sm: "16px", md: "32px", lg: "200px" } }}>
      <Outlet />
      <Paper
        sx={{ position: "fixed", bottom: 0, left: 0, right: 0 }}
        elevation={3}
      >
        <BottomNavigation value={value} onChange={handleNavigation}>
          <BottomNavigationAction label="Shopping" icon={<ShoppingCart />} />
          <BottomNavigationAction label="Profile" icon={<Person />} />
        </BottomNavigation>
      </Paper>
    </Box>
  );
}
