import { Box, Button, IconButton, TextField, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
// import axiosClient from "../utils/axiosClient";

export default function UserProfile() {
  const navigate = useNavigate();
  const [glossary, setGlossary] = useState<Record<string, string>>({});

  useEffect(() => {
    // Fetch glossary from API
    const fetchGlossary = async () => {
      // const response = await axiosClient.get('/glossary');
      // setGlossary(response.data.glossary);

      // Dummy API call - mock data
      const mockData = {
        glossary: {
          milk: "Organic Whole Milk",
          bread: "Whole Wheat Bread",
          eggs: "Free Range Eggs",
        },
      };
      setGlossary(mockData.glossary);
    };

    fetchGlossary();
  }, []);

  // Debounced PUT request when glossary changes
  useEffect(() => {
    // Skip on initial mount (empty glossary)
    if (Object.keys(glossary).length === 0) return;

    const timeoutId = setTimeout(async () => {
      // await axiosClient.put('/glossary', glossary);

      // Dummy PUT request
      console.log('PUT /glossary', glossary);
    }, 2000); // 2 seconds delay

    return () => clearTimeout(timeoutId);
  }, [glossary]);

  const handleLogout = () => {
    // await axiosClient.post('/logout');
    // localStorage.removeItem("accessToken");

    // Dummy logout - remove credentials from localStorage
    localStorage.removeItem("username");
    localStorage.removeItem("password");

    // Redirect to home
    navigate("/sign-in");
  };

  const handleGlossaryChange = (
    oldKey: string,
    newKey: string,
    value: string,
  ) => {
    const newGlossary = { ...glossary };
    if (oldKey !== newKey) {
      delete newGlossary[oldKey];
    }
    newGlossary[newKey] = value;
    setGlossary(newGlossary);
  };

  const handleAddEntry = () => {
    setGlossary({ ...glossary, "": "" });
  };

  const handleRemoveEntry = (key: string) => {
    const newGlossary = { ...glossary };
    delete newGlossary[key];
    setGlossary(newGlossary);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        User Profile
      </Typography>

      <Button variant="contained" color="error" onClick={handleLogout}>
        Logout
      </Button>

      <Box sx={{ mb: 4, mt: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Product Glossary
        </Typography>

        {Object.entries(glossary).map(([key, value], index) => (
          <Box
            key={index}
            sx={{ display: "flex", gap: 2, mb: 2, alignItems: "center" }}
          >
            <TextField
              label="Alias"
              value={key}
              onChange={(e) => handleGlossaryChange(key, e.target.value, value)}
              size="small"
              sx={{ flex: 1 }}
            />
            <TextField
              label="Product Name"
              value={value}
              onChange={(e) => handleGlossaryChange(key, key, e.target.value)}
              size="small"
              sx={{ flex: 2 }}
            />
            <IconButton
              color="error"
              onClick={() => handleRemoveEntry(key)}
              size="small"
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        ))}

        <Button
          startIcon={<AddIcon />}
          onClick={handleAddEntry}
          variant="outlined"
          sx={{ mt: 1 }}
        >
          Add Entry
        </Button>
      </Box>
    </Box>
  );
}
