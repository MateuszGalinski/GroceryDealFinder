import {
  Box,
  Button,
  CircularProgress,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import type { ShoppingItem, ShoppingListResponse } from "../utils/types";
import ProductCard from "../components/ProductCard";

export default function Shopping() {
  const [items, setItems] = useState<ShoppingItem[]>([{ id: 0, text: "" }]);
  const [nextId, setNextId] = useState(1);
  const [loading, setLoading] = useState(false);
  const [responseData, setResponseData] = useState<ShoppingListResponse | null>(
    null,
  );

  const handleChange = (id: number, value: string) => {
    const updatedItems = items.map((item) =>
      item.id === id ? { ...item, text: value } : item,
    );
    setItems(updatedItems);

    const lastItem = updatedItems[updatedItems.length - 1];
    if (lastItem.id === id && value.trim() !== "") {
      setItems([...updatedItems, { id: nextId, text: "" }]);
      setNextId(nextId + 1);
    }
  };

  const handleSubmit = async () => {
    const nonEmptyItems = items
      .filter((item) => item.text.trim() !== "")
      .map((item) => item.text.trim());

    if (nonEmptyItems.length === 0) {
      alert("Please add at least one item to your shopping list");
      return;
    }

    const formattedItems = nonEmptyItems.map((item) => `'${item}'`).join(", ");
    const payload = {
      products_names: `[${formattedItems}]`,
    };

    setLoading(true);
    setResponseData(null);

    try {
      // Dummy response for testing
      const dummyResponse: ShoppingListResponse = {
        shop: "Walmart",
        products: [
          {
            id: 1,
            url: "https://example.com/product/milk",
            name: "Organic Milk 1L",
            price: 4.99,
            is_discounted: true,
            discounted_price: 3.99,
          },
          {
            id: 2,
            url: "https://example.com/product/bread",
            name: "Whole Wheat Bread",
            price: 2.49,
            is_discounted: false,
          },
          {
            id: 3,
            url: "https://example.com/product/eggs",
            name: "Free Range Eggs (12 pack)",
            price: 5.99,
            is_discounted: true,
            discounted_price: 4.49,
          },
        ],
      };

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      console.log("Payload sent:", payload);
      console.log("Response received:", dummyResponse);
      setResponseData(dummyResponse);

      // When ready to use real API, uncomment this:
      // const response = await axiosClient.post("/list", payload);
      // setResponseData(response.data);
    } catch (error) {
      console.error("Error submitting shopping list:", error);
      alert("Failed to submit shopping list");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, pb: 10 }}>
      <Typography variant="h5" gutterBottom>
        Shopping List
      </Typography>
      <Box sx={{ mt: 2 }}>
        {items.map((item, index) => (
          <TextField
            key={item.id}
            fullWidth
            variant="outlined"
            placeholder={`Item ${index + 1}`}
            value={item.text}
            onChange={(e) => handleChange(item.id, e.target.value)}
            sx={{ mb: 2 }}
            disabled={loading}
          />
        ))}
      </Box>
      <Button
        variant="contained"
        color="primary"
        fullWidth
        onClick={handleSubmit}
        disabled={loading}
        sx={{ mt: 2 }}
      >
        {loading ? "Searching..." : "Submit Shopping List"}
      </Button>

      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {responseData && !loading && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Results from {responseData.shop}
          </Typography>
          <Box sx={{ mt: 2 }}>
            {responseData.products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
}
