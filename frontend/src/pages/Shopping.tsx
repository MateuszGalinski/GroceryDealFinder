import {
  Box,
  Button,
  Divider,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import type { ShoppingItem, ShoppingListResponse } from "../utils/types";
import ProductCard from "../components/ProductCard";
import axiosClient from "../utils/axiosClient";
import Loading from "../components/Loading";

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

    const payload = {
      products: nonEmptyItems,
    };

    setLoading(true);
    setResponseData(null);

    try {
      const response = await axiosClient.post("/generate-list/", payload);
      console.log(response.data);
      setResponseData(response.data);
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
        <Box sx={{ mt: 4, minHeight: "200px" }}>
          <Loading />
        </Box>
      )}

      {responseData && !loading && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Comparison Results
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Compared {responseData.shops_compared} shop
            {responseData.shops_compared !== 1 ? "s" : ""}
          </Typography>

          {responseData.cheapest ? (
            <>
              <Box
                sx={{
                  p: 3,
                  bgcolor: "success.light",
                  borderRadius: 2,
                  mb: 4,
                }}
              >
                <Typography variant="h6" gutterBottom>
                  Best Deal: {responseData.cheapest.shop}
                </Typography>
                <Typography variant="h4" color="success.dark">
                  Total: {responseData.cheapest.total.toFixed(2)} zł
                </Typography>
              </Box>

              <Typography variant="h6" sx={{ mb: 2 }}>
                Products from {responseData.cheapest.shop}
              </Typography>
              <Box sx={{ mb: 4 }}>
                {responseData.cheapest.products.map((product, index) => (
                  <ProductCard key={index} product={product} />
                ))}
              </Box>

              {Object.keys(responseData.complete_shops).length > 1 && (
                <>
                  <Divider sx={{ my: 4 }} />
                  <Typography variant="h6" sx={{ mb: 3 }}>
                    All Shop Comparisons
                  </Typography>
                  {Object.entries(responseData.complete_shops).map(
                    ([shopName, shopData]) => (
                      <Box key={shopName} sx={{ mb: 4 }}>
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            mb: 2,
                          }}
                        >
                          <Typography variant="h6">{shopName}</Typography>
                          <Typography variant="h6" color="primary">
                            Total: {shopData.total.toFixed(2)} zł
                          </Typography>
                        </Box>
                        {shopData.products.map((product, index) => (
                          <ProductCard key={index} product={product} />
                        ))}
                      </Box>
                    ),
                  )}
                </>
              )}
            </>
          ) : (
            <Box sx={{ textAlign: "center", py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No products found for your shopping list.
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Try adjusting your search terms or check your glossary settings.
              </Typography>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
}
