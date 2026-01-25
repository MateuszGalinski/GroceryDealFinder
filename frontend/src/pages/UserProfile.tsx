import { Box, Button, CircularProgress, IconButton, TextField, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import axiosClient from "../utils/axiosClient";
import { useQuery, useMutation } from "@tanstack/react-query";
import queryClient from "../utils/queryClient";
import Loading from "../components/Loading";

export default function UserProfile() {
  const navigate = useNavigate();
  const [glossary, setGlossary] = useState<Record<string, string>>({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const debounceTimerRef = useRef<number | null>(null);
  const accessToken = localStorage.getItem("accessToken");

  const { data, isLoading } = useQuery({
    queryKey: ["glossary", accessToken],
    queryFn: async () => {
      const response = await axiosClient.get("/glossary/");
      return response.data.translations || {};
    },
  });

  useEffect(() => {
    if (data) {
      setGlossary(data);
    }
  }, [data]);

  const updateMutation = useMutation({
    mutationFn: async (translations: Record<string, string>) => {
      const response = await axiosClient.put("/glossary/", { translations });
      return response.data;
    },
    onSuccess: () => {
      console.log("Glossary updated successfully");
      setHasUnsavedChanges(false);
      queryClient.invalidateQueries({ queryKey: ["glossary"] });
    },
    onError: (error) => {
      console.error("Failed to update glossary:", error);
    },
  });

  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  const debouncedUpdate = (updatedGlossary: Record<string, string>) => {
    setHasUnsavedChanges(true);

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      updateMutation.mutate(updatedGlossary);
    }, 2000);
  };

  const handleLogout = async () => {
    localStorage.clear();
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
    debouncedUpdate(newGlossary);
  };

  const handleAddEntry = () => {
    const newGlossary = { ...glossary, "": "" };
    setGlossary(newGlossary);
    debouncedUpdate(newGlossary);
  };

  const handleRemoveEntry = (key: string) => {
    const newGlossary = { ...glossary };
    delete newGlossary[key];
    setGlossary(newGlossary);
    debouncedUpdate(newGlossary);
  };

  if (isLoading) {
    return (
      <Box sx={{ p: 3, minHeight: "200px" }}>
        <Loading />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        User Profile
      </Typography>

      <Button variant="contained" color="error" onClick={handleLogout}>
        Logout
      </Button>

      <Box sx={{ mb: 4, mt: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
          <Typography variant="h6">
            Product Glossary
          </Typography>
          {updateMutation.isPending ? (
            <Box sx={{ display: "flex", alignItems: "center", ml: 2 }}>
              <CircularProgress size={16} sx={{ mr: 1 }} />
              <Typography
                component="span"
                sx={{ fontSize: "0.875rem", color: "text.secondary" }}
              >
                Saving...
              </Typography>
            </Box>
          ) : hasUnsavedChanges ? (
            <Typography
              component="span"
              sx={{ ml: 2, fontSize: "0.875rem", color: "warning.main" }}
            >
              Unsaved changes
            </Typography>
          ) : null}
        </Box>

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
